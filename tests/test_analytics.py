from datetime import datetime
from src.analytics import DailyReport, Analytics
import pytest

def test_daily_report_to_dict():
    dt = datetime(2026, 5, 7, 12, 0, 0)
    report = DailyReport(
        total_usage_ml=1500.5,
        min_water_left_ml=500.0,
        average_flow_ml_min=10.5,
        peak_flow_ml_min=20.0,
        peak_usage_timestamp=dt,
        suggested_reduction="Fix leak",
        report_timestamp=dt,
        day=5
    )
    data = report.to_dict()
    assert data["total_usage_ml"] == 1500.5
    assert data["day"] == 5
    assert data["suggested_reduction"] == "Fix leak"
    assert data["peak_usage_timestamp"] == dt.isoformat()

def test_validate_reading():
    valid_reading = {"water_used_ml": 200.5, "flow_rate_ml_min": 10.0}
    is_valid, _ = Analytics.validate_reading(valid_reading)
    assert is_valid is True

    invalid_reading = {"amount_ml": 200}
    is_valid, _ = Analytics.validate_reading(invalid_reading)
    assert is_valid is False
