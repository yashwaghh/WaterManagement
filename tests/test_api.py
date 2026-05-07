"""
Test suite for Flask API endpoints.
Uses Flask's built-in test client (no extra dependencies beyond pytest).
"""

import os
import datetime as dt
import pytest
from unittest.mock import patch

# Set required env vars before importing the app so load_dotenv() doesn't
# overwrite them with missing values.
os.environ.setdefault("ADMIN_SECRET", "test-secret")
os.environ.setdefault("SQLITE_DB_PATH", ":memory:")

import src.storage as storage  # noqa: E402
import api  # noqa: E402  (must come after env setup)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def reset_storage():
    """Reset the SQLite connection before every test for isolation."""
    storage._reset_connection()
    yield
    storage._reset_connection()


@pytest.fixture()
def client(reset_storage):
    """Return a Flask test client with an isolated in-memory database."""
    api.app.config["TESTING"] = True
    api.ADMIN_SECRET = "test-secret"
    # Re-initialise session state so tests start from a known baseline.
    api.session_state.update(
        {
            "current_cycle_readings_by_flat": {},
            "cycle_start_time": dt.datetime.now(),
            "simulated_day_number": 1,
            "weekly_points": {},
            "completed_daily_leaderboards": [],
        }
    )
    with api.app.test_client() as c:
        yield c


ADMIN_HEADERS = {"Authorization": "Bearer test-secret"}


# ---------------------------------------------------------------------------
# /api/health
# ---------------------------------------------------------------------------

class TestHealth:
    def test_health_returns_200(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200

    def test_health_body(self, client):
        resp = client.get("/api/health")
        data = resp.get_json()
        assert data["status"] == "healthy"
        assert "timestamp" in data


# ---------------------------------------------------------------------------
# /api/config
# ---------------------------------------------------------------------------

class TestConfig:
    def test_config_returns_200(self, client):
        resp = client.get("/api/config")
        assert resp.status_code == 200

    def test_config_fields(self, client):
        data = client.get("/api/config").get_json()
        assert "data_mode" in data
        assert "real_data_flats" in data
        assert "simulated_flats" in data


# ---------------------------------------------------------------------------
# /api/leaderboard
# ---------------------------------------------------------------------------

class TestLeaderboard:
    def _mock_simulator_readings(self):
        """Return a minimal dict of flat readings."""
        return {
            flat_id: {
                "unique_id": flat_id,
                "water_used_ml": 1500,
                "daily_threshold_ml": 2500,
                "flow_rate_ml_min": 100,
                "timestamp": "2024-01-01T00:00:00",
            }
            for flat_id in api.SIMULATED_FLATS
        }

    def test_leaderboard_returns_200(self, client):
        with patch.object(
            api.MultiFlatSimulator,
            "generate_readings_for_tick",
            return_value=self._mock_simulator_readings(),
        ):
            resp = client.get("/api/leaderboard")
        assert resp.status_code == 200

    def test_leaderboard_structure(self, client):
        with patch.object(
            api.MultiFlatSimulator,
            "generate_readings_for_tick",
            return_value=self._mock_simulator_readings(),
        ):
            data = client.get("/api/leaderboard").get_json()

        assert "leaderboard" in data
        assert "day" in data
        assert "generated_at" in data
        assert isinstance(data["leaderboard"], list)

    def test_leaderboard_record_fields(self, client):
        with patch.object(
            api.MultiFlatSimulator,
            "generate_readings_for_tick",
            return_value=self._mock_simulator_readings(),
        ):
            data = client.get("/api/leaderboard").get_json()

        if data["leaderboard"]:
            record = data["leaderboard"][0]
            for field in ("rank", "flat_id", "efficiency_score", "status", "usage"):
                assert field in record, f"Missing field: {field}"

    def test_leaderboard_empty_when_no_simulator(self, client):
        """If simulator returns nothing and Firebase is down, list is empty."""
        with patch.object(
            api.MultiFlatSimulator,
            "generate_readings_for_tick",
            return_value={},
        ), patch("api.get_real_data_from_firebase", return_value=None):
            data = client.get("/api/leaderboard").get_json()
        assert data["leaderboard"] == []


# ---------------------------------------------------------------------------
# /api/analytics/<flat_id>
# ---------------------------------------------------------------------------

class TestAnalytics:
    _SIM_FLAT = api.SIMULATED_FLATS[0] if api.SIMULATED_FLATS else "A-102"
    _REAL_FLAT = "A-101"
    _FAKE_READING = {
        "unique_id": _SIM_FLAT,
        "water_used_ml": 1800,
        "daily_threshold_ml": 2500,
        "flow_rate_ml_min": 120,
        "timestamp": "2024-01-01T00:00:00",
    }

    def test_analytics_sim_flat_200(self, client):
        with patch.object(
            api.MultiFlatSimulator,
            "generate_readings_for_tick",
            return_value={self._SIM_FLAT: self._FAKE_READING},
        ):
            resp = client.get(f"/api/analytics/{self._SIM_FLAT}")
        assert resp.status_code == 200

    def test_analytics_sim_flat_fields(self, client):
        with patch.object(
            api.MultiFlatSimulator,
            "generate_readings_for_tick",
            return_value={self._SIM_FLAT: self._FAKE_READING},
        ):
            data = client.get(f"/api/analytics/{self._SIM_FLAT}").get_json()

        for field in ("flat_id", "total_usage", "efficiency_score", "daily_threshold"):
            assert field in data, f"Missing field: {field}"
        assert data["data_source"] == "SIM"

    def test_analytics_real_flat_with_firebase(self, client):
        """Force A-101 into REAL_DATA_FLATS to test the Firebase code path."""
        fake_reading = {
            "unique_id": self._REAL_FLAT,
            "water_used_ml": 1000,
            "daily_threshold_ml": 2500,
            "flow_rate_ml_min": 80,
            "timestamp": "2024-01-01T00:00:00",
        }
        orig_real = api.REAL_DATA_FLATS[:]
        orig_sim = api.SIMULATED_FLATS[:]
        try:
            api.REAL_DATA_FLATS = [self._REAL_FLAT]
            api.SIMULATED_FLATS = [f for f in orig_sim if f != self._REAL_FLAT]
            with patch("api.get_real_data_from_firebase", return_value=fake_reading):
                resp = client.get(f"/api/analytics/{self._REAL_FLAT}")
            assert resp.status_code == 200
            data = resp.get_json()
            assert data["data_source"] == "REAL"
        finally:
            api.REAL_DATA_FLATS = orig_real
            api.SIMULATED_FLATS = orig_sim

    def test_analytics_unknown_flat_404(self, client):
        resp = client.get("/api/analytics/Z-999")
        assert resp.status_code == 404

    def test_analytics_real_flat_no_data_404(self, client):
        """Force A-101 into REAL_DATA_FLATS so the Firebase path returns 404."""
        orig_real = api.REAL_DATA_FLATS[:]
        orig_sim = api.SIMULATED_FLATS[:]
        try:
            api.REAL_DATA_FLATS = [self._REAL_FLAT]
            api.SIMULATED_FLATS = [f for f in orig_sim if f != self._REAL_FLAT]
            with patch("api.get_real_data_from_firebase", return_value=None):
                resp = client.get(f"/api/analytics/{self._REAL_FLAT}")
            assert resp.status_code == 404
        finally:
            api.REAL_DATA_FLATS = orig_real
            api.SIMULATED_FLATS = orig_sim


# ---------------------------------------------------------------------------
# /api/admin/* — authentication
# ---------------------------------------------------------------------------

class TestAdminAuth:
    def test_reset_day_no_token_401(self, client):
        resp = client.post("/api/admin/reset-day")
        assert resp.status_code == 401

    def test_reset_day_wrong_token_403(self, client):
        resp = client.post(
            "/api/admin/reset-day",
            headers={"Authorization": "Bearer wrong-token"},
        )
        assert resp.status_code == 403

    def test_reset_day_correct_token_200(self, client):
        resp = client.post("/api/admin/reset-day", headers=ADMIN_HEADERS)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "success"
        assert data["day"] == 2  # day incremented from 1

    def test_reset_week_no_token_401(self, client):
        resp = client.post("/api/admin/reset-week")
        assert resp.status_code == 401

    def test_reset_week_correct_token_200(self, client):
        resp = client.post("/api/admin/reset-week", headers=ADMIN_HEADERS)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "success"
        assert data["day"] == 1

    def test_toggle_simulation_no_token_401(self, client):
        resp = client.post("/api/admin/toggle-simulation")
        assert resp.status_code == 401

    def test_toggle_simulation_correct_token_200(self, client):
        resp = client.post("/api/admin/toggle-simulation", headers=ADMIN_HEADERS)
        assert resp.status_code == 200

    def test_admin_state_no_token_401(self, client):
        resp = client.get("/api/admin/state")
        assert resp.status_code == 401

    def test_admin_state_correct_token_200(self, client):
        resp = client.get("/api/admin/state", headers=ADMIN_HEADERS)
        assert resp.status_code == 200
        data = resp.get_json()
        assert "current_day" in data
        assert "weekly_points" in data


# ---------------------------------------------------------------------------
# /api/weekly-summary
# ---------------------------------------------------------------------------

class TestWeeklySummary:
    def test_weekly_summary_200(self, client):
        resp = client.get("/api/weekly-summary")
        assert resp.status_code == 200

    def test_weekly_summary_structure(self, client):
        data = client.get("/api/weekly-summary").get_json()
        assert "week_summary" in data
        assert "current_day" in data


# ---------------------------------------------------------------------------
# /api/flats
# ---------------------------------------------------------------------------

class TestFlats:
    def test_flats_200(self, client):
        resp = client.get("/api/flats")
        assert resp.status_code == 200

    def test_flats_returns_list(self, client):
        data = client.get("/api/flats").get_json()
        assert isinstance(data["flats"], list)
        assert len(data["flats"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
