"""
REST API for Water Management System - Flask backend
Hybrid Mode: Real data for specified flats, simulation for others
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from datetime import datetime, timedelta
from functools import wraps
import os
import json
from dotenv import load_dotenv
from src.firebase_client import FirebaseClient
from src.analytics import Analytics
from src.ranking import Ranking
from src.multi_flat_ranking import MultiFlatRanking
from src.report_storage import ReportStorage
from src.storage import load_state, save_day, reset_week_state
from simulator import MultiFlatSimulator

load_dotenv()

app = Flask(__name__, static_folder='frontend/build', static_url_path='/')
CORS(app)

# ---------------------------------------------------------------------------
# Admin authentication
# ---------------------------------------------------------------------------
ADMIN_SECRET = os.getenv("ADMIN_SECRET", "")


def require_admin(f):
    """Decorator that enforces Bearer-token authentication on admin endpoints."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not ADMIN_SECRET:
            # No secret configured — deny all access rather than allow open access
            return jsonify({"error": "Admin secret not configured on server"}), 503
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Unauthorized"}), 401
        token = auth_header[len("Bearer "):]
        if token != ADMIN_SECRET:
            return jsonify({"error": "Forbidden"}), 403
        return f(*args, **kwargs)
    return decorated

# Initialize services
simulator = None
firebase_client = None
ranking_service = MultiFlatRanking()
analytics_service = Analytics()
report_storage = ReportStorage()

# HYBRID MODE CONFIG
REAL_DATA_FLATS = ["A-101"]  # These use Firebase real data
SIMULATED_FLATS = ["A-102", "A-103", "A-104", "A-105"]  # These use simulation

# Session state — load persisted values from SQLite, fall back to defaults
_persisted = load_state()
session_state = {
    "current_cycle_readings_by_flat": {},
    "cycle_start_time": datetime.now(),
    "simulated_day_number": _persisted["simulated_day_number"],
    "weekly_points": _persisted["weekly_points"],
    "completed_daily_leaderboards": _persisted["completed_daily_leaderboards"],
}


def initialize_simulator():
    """Initialize the simulator for simulated flats."""
    global simulator
    if simulator is None:
        simulator = MultiFlatSimulator()


def initialize_firebase():
    """Initialize Firebase client for real data."""
    global firebase_client
    if firebase_client is None:
        try:
            firebase_client = FirebaseClient()
        except Exception as e:
            print(f"Firebase initialization failed: {e}")
            firebase_client = None


def get_real_data_from_firebase(flat_id):
    """Fetch real data from Firebase for a specific flat."""
    try:
        if firebase_client is None:
            initialize_firebase()

        if firebase_client:
            # Get latest reading from Firebase
            reading = firebase_client.get_latest_reading(flat_id)
            if reading:
                return {
                    "unique_id": flat_id,
                    "water_used_ml": reading.get("water_used_ml", 0),
                    "daily_threshold_ml": reading.get("daily_threshold_ml", 2500),
                    "flow_rate_ml_min": reading.get("flow_rate_ml_min", 0),
                    "timestamp": reading.get("timestamp", datetime.now().isoformat()),
                }
    except Exception as e:
        print(f"Error fetching Firebase data for {flat_id}: {e}")

    return None


@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})


@app.route("/api/config", methods=["GET"])
def get_config():
    """Get app configuration."""
    return jsonify(
        {
            "data_mode": "hybrid",
            "real_data_flats": REAL_DATA_FLATS,
            "simulated_flats": SIMULATED_FLATS,
            "simulated_day_length": int(os.getenv("SIMULATED_DAY_LENGTH_SECONDS", 60)),
            "usage_threshold": int(os.getenv("USAGE_THRESHOLD_ML", 2500)),
        }
    )


class SimpleReport:
    """Simple object to hold report data for ranking."""
    def __init__(self, total_usage_ml, average_flow_ml_min, peak_flow_ml_min):
        self.total_usage_ml = total_usage_ml
        self.average_flow_ml_min = average_flow_ml_min
        self.peak_flow_ml_min = peak_flow_ml_min


@app.route("/api/leaderboard", methods=["GET"])
def get_leaderboard():
    """Get current leaderboard with rankings (hybrid real + simulated data)."""
    initialize_simulator()

    readings_by_flat = {}

    # Get real data for REAL_DATA_FLATS
    for flat_id in REAL_DATA_FLATS:
        real_reading = get_real_data_from_firebase(flat_id)
        if real_reading:
            readings_by_flat[flat_id] = real_reading
            print(f"[REAL] {flat_id}: {real_reading.get('water_used_ml')}ml")
        else:
            print(f"[WARNING] No real data for {flat_id}, check Firebase")

    # Get simulated data for SIMULATED_FLATS
    if simulator:
        all_simulated = simulator.generate_readings_for_tick()
        for flat_id in SIMULATED_FLATS:
            if flat_id in all_simulated:
                readings_by_flat[flat_id] = all_simulated[flat_id]
                print(f"[SIM] {flat_id}: {all_simulated[flat_id].get('water_used_ml')}ml")

    # Store readings for analytics
    session_state["current_cycle_readings_by_flat"] = readings_by_flat

    if not readings_by_flat:
        return jsonify({"leaderboard": [], "generated_at": datetime.now().isoformat()})

    # Convert readings to reports for ranking
    daily_reports = {}
    for flat_id, reading in readings_by_flat.items():
        daily_reports[flat_id] = SimpleReport(
            total_usage_ml=reading["water_used_ml"],
            average_flow_ml_min=reading["flow_rate_ml_min"],
            peak_flow_ml_min=reading["flow_rate_ml_min"],
        )

    # Get threshold from config
    threshold_ml = int(os.getenv("USAGE_THRESHOLD_ML", 2500))

    # Rank flats
    ranked = ranking_service.rank_flats(
        daily_reports=daily_reports,
        threshold_ml=threshold_ml,
        simulated_day=session_state["simulated_day_number"],
        weekly_points=session_state["weekly_points"],
        finalize_points=False,
    )

    leaderboard = []
    for record in ranked:
        data_source = "REAL" if record.unique_id in REAL_DATA_FLATS else "SIM"
        leaderboard.append(
            {
                "rank": record.rank,
                "flat_id": record.unique_id,
                "efficiency_score": record.efficiency_score,
                "status": record.status,
                "usage": record.total_usage_ml,
                "target": record.threshold_ml,
                "peak_flow": record.peak_flow_rate_ml_min,
                "daily_points": record.daily_points,
                "weekly_points": session_state["weekly_points"].get(record.unique_id, 0),
                "data_source": data_source,
            }
        )

    return jsonify(
        {
            "leaderboard": leaderboard,
            "day": session_state["simulated_day_number"],
            "generated_at": datetime.now().isoformat(),
            "mode": "hybrid",
        }
    )


@app.route("/api/analytics/<flat_id>", methods=["GET"])
def get_analytics(flat_id):
    """Get analytics for a specific flat (hybrid: real or simulated data)."""

    # Determine data source
    if flat_id in REAL_DATA_FLATS:
        # Get real data from Firebase
        reading = get_real_data_from_firebase(flat_id)
        if not reading:
            return jsonify({"error": "No real data available for flat"}), 404
        data_source = "REAL"
    elif flat_id in SIMULATED_FLATS:
        # Get simulated data
        initialize_simulator()
        if not simulator:
            return jsonify({"error": "Simulator not initialized"}), 500

        all_simulated = simulator.generate_readings_for_tick()
        reading = all_simulated.get(flat_id)
        if not reading:
            return jsonify({"error": "No simulated data for flat"}), 404
        data_source = "SIM"
    else:
        return jsonify({"error": "Flat not found"}), 404

    # Extract data from reading (dict format)
    total_usage = reading.get("water_used_ml", 0)
    peak_flow = reading.get("flow_rate_ml_min", 0)
    daily_threshold = reading.get("daily_threshold_ml", 2500)
    timestamp = reading.get("timestamp", datetime.now().isoformat())

    # Calculate efficiency
    ratio = total_usage / daily_threshold if daily_threshold > 0 else 0
    efficiency = 100 - (ratio * 100) if ratio <= 1.0 else -((ratio - 1) * 100)

    # Calculate statistics
    average_usage = total_usage / 2 if total_usage > 0 else 0

    # Prepare analytics data
    analytics_data = {
        "flat_id": flat_id,
        "total_usage": round(total_usage, 1),
        "average_usage": round(average_usage, 1),
        "peak_usage": round(peak_flow, 1),
        "efficiency_score": round(efficiency, 2),
        "daily_threshold": daily_threshold,
        "data_source": data_source,
        "efficiency_trend": [
            {
                "timestamp": timestamp,
                "efficiency": round(efficiency, 2),
                "usage": round(total_usage, 1),
            }
        ],
    }

    return jsonify(analytics_data)


@app.route("/api/weekly-summary", methods=["GET"])
def get_weekly_summary():
    """Get weekly summary and accumulated points."""
    summary = []
    for flat_id, points in session_state["weekly_points"].items():
        summary.append({"flat_id": flat_id, "weekly_points": points})

    return jsonify(
        {
            "week_summary": sorted(summary, key=lambda x: x["weekly_points"], reverse=True),
            "current_day": session_state["simulated_day_number"],
            "generated_at": datetime.now().isoformat(),
        }
    )


@app.route("/api/admin/reset-day", methods=["POST"])
@require_admin
def reset_day():
    """Reset to next day (admin control)."""
    session_state["cycle_start_time"] = datetime.now()
    session_state["simulated_day_number"] += 1
    session_state["current_cycle_readings_by_flat"] = {}

    save_day(session_state["simulated_day_number"])

    return jsonify(
        {
            "status": "success",
            "day": session_state["simulated_day_number"],
            "message": f"Reset to day {session_state['simulated_day_number']}",
        }
    )


@app.route("/api/admin/reset-week", methods=["POST"])
@require_admin
def reset_week():
    """Reset weekly points (admin control)."""
    session_state["weekly_points"] = {}
    session_state["simulated_day_number"] = 1
    session_state["current_cycle_readings_by_flat"] = {}
    session_state["cycle_start_time"] = datetime.now()

    reset_week_state()

    return jsonify(
        {
            "status": "success",
            "message": "Weekly reset complete",
            "day": 1,
        }
    )


@app.route("/api/admin/toggle-simulation", methods=["POST"])
@require_admin
def toggle_simulation():
    """Toggle simulation mode."""
    data_mode = os.getenv("DATA_MODE", "simulation")
    new_mode = "firebase" if data_mode == "simulation" else "simulation"

    return jsonify(
        {
            "status": "success",
            "current_mode": new_mode,
            "message": f"Switched to {new_mode} mode (restart app to apply)",
        }
    )


@app.route("/api/flats", methods=["GET"])
def get_flats():
    """Get list of all flats in the system."""
    all_flats = sorted(REAL_DATA_FLATS + SIMULATED_FLATS)
    return jsonify({"flats": all_flats})


@app.route("/api/admin/state", methods=["GET"])
@require_admin
def get_admin_state():
    """Get current app state (admin debug)."""
    return jsonify(
        {
            "current_day": session_state["simulated_day_number"],
            "cycle_start_time": session_state["cycle_start_time"].isoformat(),
            "flats_count": len(session_state["current_cycle_readings_by_flat"]),
            "weekly_points": session_state["weekly_points"],
        }
    )


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    if path != "" and os.path.exists(app.static_folder + "/" + path):
        return send_from_directory(app.static_folder, path)
    else:
        # Check if index.html exists, else return API info
        if os.path.exists(app.static_folder + "/index.html"):
            return send_from_directory(app.static_folder, "index.html")
        else:
            return jsonify({"status": "API is running. Frontend not found.", "version": "1.0"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
