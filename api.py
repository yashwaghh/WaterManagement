"""
REST API for Water Management System - Flask backend
Hybrid Mode: Real data for specified flats, simulation for others
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from datetime import datetime
from functools import wraps
import logging
import os
import json
from dotenv import load_dotenv
from src.firebase_client import FirebaseClient
from src.analytics import Analytics
from src.ranking import Ranking
from src.multi_flat_ranking import MultiFlatRanking
from src.report_storage import ReportStorage
from src.storage import (
    load_state, save_day, reset_week_state, save_weekly_points,
    save_redemption, get_total_redeemed, get_redemptions,
)
from simulator import MultiFlatSimulator

load_dotenv()

app = Flask(__name__, static_folder='frontend/build', static_url_path='/')
CORS(app)

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

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
data_mode = os.getenv("DATA_MODE", "simulation").lower()

if data_mode == "simulation":
    REAL_DATA_FLATS = []
    SIMULATED_FLATS = ["A-101", "A-102", "A-103", "A-104", "A-105"]
elif data_mode == "firebase":
    REAL_DATA_FLATS = ["A-101", "A-102", "A-103", "A-104", "A-105"]
    SIMULATED_FLATS = []
else:  # hybrid
    REAL_DATA_FLATS = ["A-101"]
    SIMULATED_FLATS = ["A-102", "A-103", "A-104", "A-105"]

# Per-person daily water allowance in ml.
# Final threshold for a flat = PER_PERSON_ML × family_size.
PER_PERSON_ML = int(os.getenv("PER_PERSON_ML", 500))
DEFAULT_FAMILY_SIZE = int(os.getenv("DEFAULT_FAMILY_SIZE", 4))

# Leak detection — consecutive non-zero flow ticks before an alert is raised.
# At 5 s poll interval, 120 ticks ≈ 10 minutes of continuous flow.
LEAK_TICKS_THRESHOLD = int(os.getenv("LEAK_TICKS_THRESHOLD", 120))

# How many history points to keep in memory per simulated flat.
_HISTORY_MAX = 50

# Session state — load persisted values from SQLite, fall back to defaults
_persisted = load_state()
session_state = {
    "current_cycle_readings_by_flat": {},
    "cycle_start_time": datetime.now(),
    "simulated_day_number": _persisted["simulated_day_number"],
    "weekly_points": _persisted["weekly_points"],
    "completed_daily_leaderboards": _persisted["completed_daily_leaderboards"],
    # Leak detection: flat_id -> consecutive non-zero flow tick count
    "consecutive_flow_ticks": {},
    # In-memory history ring-buffer for simulated flats
    "flat_history": {},
    "peak_flows": {},
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
            logger.info("Firebase initialized successfully")
        except Exception as e:
            logger.warning("Firebase initialization failed: %s", e)
            firebase_client = None


def get_family_size(flat_id: str) -> int:
    """Look up family size for a flat from Firebase user profiles.

    Falls back to DEFAULT_FAMILY_SIZE if not found.
    Results are cached in session_state['flat_family_sizes'].
    """
    cache = session_state.setdefault("flat_family_sizes", {})
    if flat_id in cache:
        return cache[flat_id]

    # Try reading from Firebase RTDB users collection
    try:
        if firebase_client is None:
            initialize_firebase()
        if firebase_client:
            from firebase_admin import db as fb_db
            users_ref = fb_db.reference("users")
            users_data = users_ref.get()
            if users_data and isinstance(users_data, dict):
                for uid, profile in users_data.items():
                    if isinstance(profile, dict) and profile.get("flat_id") == flat_id:
                        fs = int(profile.get("family_size", DEFAULT_FAMILY_SIZE))
                        cache[flat_id] = fs
                        logger.info("Family size for %s: %d (from Firebase)", flat_id, fs)
                        return fs
    except Exception as e:
        logger.warning("Error looking up family size for %s: %s", flat_id, e)

    cache[flat_id] = DEFAULT_FAMILY_SIZE
    return DEFAULT_FAMILY_SIZE


def get_threshold_for_flat(flat_id: str) -> int:
    """Calculate per-flat daily water threshold based on family size."""
    family_size = get_family_size(flat_id)
    return PER_PERSON_ML * family_size


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
        logger.warning("Error fetching Firebase data for %s: %s", flat_id, e)

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
            "per_person_ml": PER_PERSON_ML,
            "default_family_size": DEFAULT_FAMILY_SIZE,
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
            logger.info("[REAL] %s: %sml", flat_id, real_reading.get('water_used_ml'))
        else:
            logger.warning("[WARNING] No real data for %s, check Firebase", flat_id)

    # Get simulated data for SIMULATED_FLATS
    if simulator:
        all_simulated = simulator.generate_readings_for_tick()
        for flat_id in SIMULATED_FLATS:
            if flat_id in all_simulated:
                readings_by_flat[flat_id] = all_simulated[flat_id]
                logger.info("[SIM] %s: %sml", flat_id, all_simulated[flat_id].get('water_used_ml'))

    # Store readings for analytics
    session_state["current_cycle_readings_by_flat"] = readings_by_flat

    # --- Leak detection: update consecutive non-zero flow tick counters ---
    flow_ticks = session_state["consecutive_flow_ticks"]
    flat_history = session_state["flat_history"]
    for flat_id, reading in readings_by_flat.items():
        flow = reading.get("flow_rate_ml_min", 0)
        flow_ticks[flat_id] = flow_ticks.get(flat_id, 0) + 1 if flow > 0 else 0

        # Accumulate in-memory history (used by /api/history for simulated flats)
        usage = reading.get("water_used_ml", 0)
        threshold = reading.get("daily_threshold_ml", 2500)
        efficiency = round(100 - (usage / threshold * 100), 2) if threshold > 0 else 0
        hist = flat_history.setdefault(flat_id, [])
        hist.append({
            "timestamp": reading.get("timestamp"),
            "usage": round(usage, 1),
            "flow_rate": round(flow, 1),
            "efficiency": efficiency,
        })
        if len(hist) > _HISTORY_MAX:
            hist.pop(0)

    if not readings_by_flat:
        return jsonify({"leaderboard": [], "generated_at": datetime.now().isoformat()})

    # Convert readings to reports for ranking
    daily_reports = {}
    for flat_id, reading in readings_by_flat.items():
        current_flow = reading["flow_rate_ml_min"]

        stored_peak = session_state["peak_flows"].get(flat_id, 0)

        # Reset peak if sensor truly idle
        if (
            reading["water_used_ml"] == 0
            and current_flow == 0
        ):
            stored_peak = 0

        new_peak = max(stored_peak, current_flow)

        session_state["peak_flows"][flat_id] = new_peak

        daily_reports[flat_id] = SimpleReport(
            total_usage_ml=reading["water_used_ml"],
            average_flow_ml_min=current_flow,
            peak_flow_ml_min=new_peak,
        )

    # Rank flats with per-flat thresholds
    # We pass the max threshold for global ranking, but include per-flat targets in response
    flat_thresholds = {fid: get_threshold_for_flat(fid) for fid in readings_by_flat}
    # Use per-flat thresholds in ranking by setting each report's threshold
    ranked = ranking_service.rank_flats_per_threshold(
        daily_reports=daily_reports,
        flat_thresholds=flat_thresholds,
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


@app.route("/api/alerts", methods=["GET"])
def get_alerts():
    """Return flats with suspected pipe leak.

    A flat is flagged when its flow_rate_ml_min has been non-zero for more
    than LEAK_TICKS_THRESHOLD consecutive leaderboard ticks (default 120
    ticks × 5 s poll ≈ 10 minutes).  Pass ?ticks=N to override per-request.
    """
    threshold = int(request.args.get("ticks", LEAK_TICKS_THRESHOLD))
    alerts = []
    for flat_id, ticks in session_state["consecutive_flow_ticks"].items():
        if ticks > threshold:
            alerts.append({
                "flat_id": flat_id,
                "consecutive_ticks": ticks,
                "duration_seconds": ticks * 5,
                "alert_type": "probable_leak",
            })
    return jsonify({
        "alerts": alerts,
        "threshold_ticks": threshold,
        "generated_at": datetime.now().isoformat(),
    })


@app.route("/api/history/<flat_id>", methods=["GET"])
def get_history(flat_id):
    """Return recent historical readings for a flat.

    Real flats: reads from Firebase ``readings/{flat_id}/history`` (written by
    the ESP8266 / simulator via ``push()``).
    Simulated flats: returns the in-memory ring-buffer accumulated by
    ``/api/leaderboard`` ticks.
    """
    limit = max(1, min(int(request.args.get("limit", 50)), 200))

    def _to_history_point(r):
        usage = r.get("water_used_ml", 0)
        threshold = r.get("daily_threshold_ml", 2500)
        efficiency = round(100 - (usage / threshold * 100), 2) if threshold > 0 else 0
        return {
            "timestamp": r.get("timestamp"),
            "usage": round(usage, 1),
            "flow_rate": round(r.get("flow_rate_ml_min", 0), 1),
            "efficiency": efficiency,
        }

    if flat_id in REAL_DATA_FLATS:
        if firebase_client is None:
            initialize_firebase()
        history = []
        if firebase_client:
            raw = firebase_client.get_history(flat_id, limit=limit)
            history = [_to_history_point(r) for r in raw]
        return jsonify({"flat_id": flat_id, "history": history, "data_source": "REAL"})

    if flat_id in SIMULATED_FLATS:
        history = session_state["flat_history"].get(flat_id, [])
        return jsonify({
            "flat_id": flat_id,
            "history": history[-limit:],
            "data_source": "SIM",
        })

    return jsonify({"error": "Flat not found"}), 404


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
    daily_threshold = get_threshold_for_flat(flat_id)
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
    """Reset to next day and finalize points (admin control)."""
    # 1. Finalize points for all active readings
    
    # Failsafe: Ensure all flats are processed even if not in current cycle
    all_flats = REAL_DATA_FLATS + SIMULATED_FLATS
    current_readings = session_state.get("current_cycle_readings_by_flat", {})
    
    # If a flat is completely missing, provide a dummy 0 reading so a report is still generated
    for f_id in all_flats:
        if f_id not in current_readings:
            current_readings[f_id] = {
                "water_used_ml": 0,
                "flow_rate_ml_min": 0,
                "daily_threshold_ml": int(os.getenv("USAGE_THRESHOLD_ML", 2500)),
                "timestamp": datetime.now().isoformat()
            }

    if current_readings:
        daily_reports = {}
        for flat_id, reading in current_readings.items():
            daily_reports[flat_id] = SimpleReport(
                total_usage_ml=reading.get("water_used_ml", 0),
                average_flow_ml_min=reading.get("flow_rate_ml_min", 0),
                peak_flow_ml_min=reading.get("flow_rate_ml_min", 0),
            )
            
            # Save actual full report
            report = Analytics.compile_report([reading])
            report.day = session_state["simulated_day_number"]
            report_storage.save_report(report, flat_id)

        flat_thresholds = {fid: get_threshold_for_flat(fid) for fid in daily_reports}
        ranked = ranking_service.rank_flats_per_threshold(
            daily_reports=daily_reports,
            flat_thresholds=flat_thresholds,
            simulated_day=session_state["simulated_day_number"],
            weekly_points=session_state["weekly_points"],
            finalize_points=True,
        )

        session_state["weekly_points"] = MultiFlatRanking.update_weekly_points(
            session_state["weekly_points"], ranked
        )
        save_weekly_points(session_state["weekly_points"])

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
    """Toggle simulation mode.

    Note: This only returns the toggled mode name. To actually apply it,
    update DATA_MODE in your .env and restart the application.
    """
    global data_mode
    current_mode = data_mode
    new_mode = "firebase" if current_mode == "simulation" else "simulation"

    return jsonify(
        {
            "status": "success",
            "current_mode": new_mode,
            "previous_mode": current_mode,
            "message": f"Mode would switch from '{current_mode}' to '{new_mode}'. "
                       f"Update DATA_MODE in .env and restart the app to apply.",
        }
    )


@app.route("/api/points/<flat_id>", methods=["GET"])
def get_points(flat_id):
    """Get current spendable points balance for a flat.

    balance = weekly_points + projected_daily_points - total_redeemed

    Projected daily points come from the current leaderboard cycle
    (before admin finalizes with Reset Day). This lets users see
    and spend their earned points in real-time.
    """
    weekly = session_state["weekly_points"].get(flat_id, 0)

    # Calculate projected daily points from current cycle readings
    projected_daily = 0
    current_readings = session_state.get("current_cycle_readings_by_flat", {})
    if current_readings:
        daily_reports = {}
        for fid, reading in current_readings.items():
            daily_reports[fid] = SimpleReport(
                total_usage_ml=reading.get("water_used_ml", 0),
                average_flow_ml_min=reading.get("flow_rate_ml_min", 0),
                peak_flow_ml_min=reading.get("flow_rate_ml_min", 0),
            )
        flat_thresholds = {fid: get_threshold_for_flat(fid) for fid in daily_reports}
        ranked = ranking_service.rank_flats_per_threshold(
            daily_reports=daily_reports,
            flat_thresholds=flat_thresholds,
            simulated_day=session_state["simulated_day_number"],
            weekly_points=session_state["weekly_points"],
            finalize_points=False,
        )
        for record in ranked:
            if record.unique_id == flat_id:
                projected_daily = record.daily_points
                break

    total_earned = weekly + projected_daily
    redeemed = get_total_redeemed(flat_id)
    balance = max(0, total_earned - redeemed)
    return jsonify({
        "flat_id": flat_id,
        "weekly_points": weekly,
        "projected_daily_points": projected_daily,
        "total_earned": total_earned,
        "total_redeemed": redeemed,
        "balance": balance,
        "redemptions": get_redemptions(flat_id),
    })


@app.route("/api/redeem", methods=["POST"])
def redeem_points():
    """Redeem points for a store item.

    Body JSON: { "flat_id": "A-101", "item_id": "maint-5", "item_title": "5% Maintenance Concession", "points_cost": 4000 }
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    flat_id = data.get("flat_id")
    item_id = data.get("item_id")
    item_title = data.get("item_title", "Unknown Item")
    points_cost = int(data.get("points_cost", 0))

    if not flat_id or not item_id or points_cost <= 0:
        return jsonify({"error": "flat_id, item_id, and points_cost are required"}), 400

    # Check balance (including projected daily points from current cycle)
    weekly = session_state["weekly_points"].get(flat_id, 0)

    # Include projected daily points
    projected_daily = 0
    current_readings = session_state.get("current_cycle_readings_by_flat", {})
    if current_readings:
        daily_reports = {}
        for fid, reading in current_readings.items():
            daily_reports[fid] = SimpleReport(
                total_usage_ml=reading.get("water_used_ml", 0),
                average_flow_ml_min=reading.get("flow_rate_ml_min", 0),
                peak_flow_ml_min=reading.get("flow_rate_ml_min", 0),
            )
        flat_thresholds = {fid: get_threshold_for_flat(fid) for fid in daily_reports}
        ranked = ranking_service.rank_flats_per_threshold(
            daily_reports=daily_reports,
            flat_thresholds=flat_thresholds,
            simulated_day=session_state["simulated_day_number"],
            weekly_points=session_state["weekly_points"],
            finalize_points=False,
        )
        for record in ranked:
            if record.unique_id == flat_id:
                projected_daily = record.daily_points
                break

    total_earned = weekly + projected_daily
    redeemed = get_total_redeemed(flat_id)
    balance = max(0, total_earned - redeemed)

    if points_cost > balance:
        return jsonify({
            "error": "Insufficient points",
            "balance": balance,
            "cost": points_cost,
        }), 400

    # Record redemption
    redemption_id = save_redemption(flat_id, item_id, item_title, points_cost)
    new_balance = balance - points_cost

    logger.info("Redemption: %s redeemed '%s' for %d pts (balance: %d -> %d)",
                flat_id, item_title, points_cost, balance, new_balance)

    return jsonify({
        "status": "success",
        "redemption_id": redemption_id,
        "item_title": item_title,
        "points_deducted": points_cost,
        "new_balance": new_balance,
    })


@app.route("/api/reports/<flat_id>", methods=["GET"])
def get_reports(flat_id):
    """Get all completed daily reports for a flat."""
    reports = report_storage.load_all_reports(flat_id)
    return jsonify({"flat_id": flat_id, "reports": reports})


@app.route("/api/reports/<flat_id>/day/<int:day>", methods=["GET"])
def get_report_for_day(flat_id, day):
    """Get a single daily report on demand."""
    from src.on_demand_report import ReportGenerator

    report = ReportGenerator.generate_daily_report_on_demand(day, flat_id)
    if report is None:
        return jsonify({"error": f"No report found for {flat_id} day {day}"}), 404
    return jsonify({"flat_id": flat_id, "day": day, "report": report})


@app.route("/api/reports/<flat_id>/weekly", methods=["GET"])
def get_weekly_report(flat_id):
    """Generate a weekly summary report on demand.

    Query params:
        start_day (int): Starting day number (default 1)
        end_day   (int): Ending day number   (default 7)
    """
    from src.on_demand_report import ReportGenerator

    start_day = int(request.args.get("start_day", 1))
    end_day = int(request.args.get("end_day", 7))
    report = ReportGenerator.generate_weekly_report_on_demand(start_day, end_day, flat_id)
    if report is None:
        return jsonify({"error": f"No reports found for {flat_id} in days {start_day}-{end_day}"}), 404
    return jsonify(report)


@app.route("/api/reports/<flat_id>/pdf/daily/<int:day>", methods=["GET"])
def download_daily_pdf(flat_id, day):
    """Download a daily report as a professionally formatted PDF."""
    from src.on_demand_report import ReportGenerator
    from src.pdf_generator import PDFReportGenerator
    from flask import Response

    report = ReportGenerator.generate_daily_report_on_demand(day, flat_id)
    
    # If no saved report is found, check if it's the current ongoing day to generate a live report!
    if report is None and day == session_state.get("simulated_day_number"):
        readings = []
        if flat_id in SIMULATED_FLATS:
            readings = session_state.get("flat_history", {}).get(flat_id, [])
        elif flat_id in REAL_DATA_FLATS:
            # For real flats we could fetch from RTDB, but we'll use whatever history is loaded
            readings = session_state.get("flat_history", {}).get(flat_id, [])
            
        if not readings:
            # If no history at all, provide a dummy reading so they still get a PDF
            readings = [{
                "water_used_ml": 0,
                "flow_rate_ml_min": 0,
                "timestamp": datetime.now().isoformat()
            }]
            
        # Map history keys to expected format for compile_report
        mapped_readings = []
        for r in readings:
            mapped_readings.append({
                "water_used_ml": r.get("usage", r.get("water_used_ml", 0)),
                "flow_rate_ml_min": r.get("flow_rate", r.get("flow_rate_ml_min", 0)),
                "water_left_ml": r.get("water_left_ml", 0),
                "timestamp": r.get("timestamp", datetime.now().isoformat())
            })
            
        live_report = Analytics.compile_report(mapped_readings)
        report = {
            "id": live_report.report_timestamp.isoformat(),
            "flat_id": flat_id,
            "day": day,
            "total_usage_ml": float(live_report.total_usage_ml),
            "min_water_left_ml": float(live_report.min_water_left_ml),
            "average_flow_ml_min": float(live_report.average_flow_ml_min),
            "peak_flow_ml_min": float(live_report.peak_flow_ml_min),
            "peak_usage_timestamp": live_report.peak_usage_timestamp.isoformat(),
            "suggested_reduction": str(live_report.suggested_reduction),
            "report_timestamp": live_report.report_timestamp.isoformat(),
        }

    if report is None:
        return jsonify({"error": f"No report found for {flat_id} day {day}. Wait for the day to finish or click Reset Day in Admin."}), 404

    pdf_bytes = PDFReportGenerator.generate_daily_report_pdf(report, flat_id)
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={flat_id}_daily_day_{day}.pdf"
        },
    )


@app.route("/api/reports/<flat_id>/pdf/weekly", methods=["GET"])
def download_weekly_pdf(flat_id):
    """Download a weekly summary as a professionally formatted PDF."""
    from src.on_demand_report import ReportGenerator
    from src.pdf_generator import PDFReportGenerator
    from flask import Response

    start_day = int(request.args.get("start_day", 1))
    end_day = int(request.args.get("end_day", 7))
    reports = ReportGenerator.get_reports_by_day_range(start_day, end_day, flat_id)
    
    current_day = session_state.get("simulated_day_number")
    if start_day <= current_day <= end_day:
        # Check if we already have the current day in saved reports (unlikely if not reset)
        if not any(r.get("day") == current_day for r in reports):
            readings = session_state.get("flat_history", {}).get(flat_id, [])
            if not readings:
                readings = [{"water_used_ml": 0, "flow_rate_ml_min": 0, "timestamp": datetime.now().isoformat()}]
            
            mapped_readings = []
            for r in readings:
                mapped_readings.append({
                    "water_used_ml": r.get("usage", r.get("water_used_ml", 0)),
                    "flow_rate_ml_min": r.get("flow_rate", r.get("flow_rate_ml_min", 0)),
                    "water_left_ml": r.get("water_left_ml", 0),
                    "timestamp": r.get("timestamp", datetime.now().isoformat())
                })
                
            live_report = Analytics.compile_report(mapped_readings)
            reports.append({
                "id": live_report.report_timestamp.isoformat(),
                "flat_id": flat_id, "day": current_day,
                "total_usage_ml": float(live_report.total_usage_ml),
                "min_water_left_ml": float(live_report.min_water_left_ml),
                "average_flow_ml_min": float(live_report.average_flow_ml_min),
                "peak_flow_ml_min": float(live_report.peak_flow_ml_min),
                "peak_usage_timestamp": live_report.peak_usage_timestamp.isoformat(),
                "suggested_reduction": str(live_report.suggested_reduction),
                "report_timestamp": live_report.report_timestamp.isoformat(),
            })

    if not reports:
        return jsonify({"error": f"No reports found for {flat_id} in days {start_day}-{end_day}"}), 404

    pdf_bytes = PDFReportGenerator.generate_weekly_report_pdf(reports, flat_id)
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={flat_id}_weekly_days_{start_day}-{end_day}.pdf"
        },
    )

@app.route("/api/reports/<flat_id>/pdf/monthly", methods=["GET"])
def download_monthly_pdf(flat_id):
    """Download a monthly summary as a professionally formatted PDF."""
    from src.on_demand_report import ReportGenerator
    from src.pdf_generator import PDFReportGenerator
    from flask import Response

    start_day = int(request.args.get("start_day", 1))
    end_day = int(request.args.get("end_day", 30))
    reports = ReportGenerator.get_reports_by_day_range(start_day, end_day, flat_id)
    
    current_day = session_state.get("simulated_day_number")
    if start_day <= current_day <= end_day:
        if not any(r.get("day") == current_day for r in reports):
            readings = session_state.get("flat_history", {}).get(flat_id, [])
            if not readings:
                readings = [{"water_used_ml": 0, "flow_rate_ml_min": 0, "timestamp": datetime.now().isoformat()}]
            
            mapped_readings = []
            for r in readings:
                mapped_readings.append({
                    "water_used_ml": r.get("usage", r.get("water_used_ml", 0)),
                    "flow_rate_ml_min": r.get("flow_rate", r.get("flow_rate_ml_min", 0)),
                    "water_left_ml": r.get("water_left_ml", 0),
                    "timestamp": r.get("timestamp", datetime.now().isoformat())
                })
                
            live_report = Analytics.compile_report(mapped_readings)
            reports.append({
                "id": live_report.report_timestamp.isoformat(),
                "flat_id": flat_id, "day": current_day,
                "total_usage_ml": float(live_report.total_usage_ml),
                "min_water_left_ml": float(live_report.min_water_left_ml),
                "average_flow_ml_min": float(live_report.average_flow_ml_min),
                "peak_flow_ml_min": float(live_report.peak_flow_ml_min),
                "peak_usage_timestamp": live_report.peak_usage_timestamp.isoformat(),
                "suggested_reduction": str(live_report.suggested_reduction),
                "report_timestamp": live_report.report_timestamp.isoformat(),
            })

    if not reports:
        return jsonify({"error": f"No reports found for {flat_id} in days {start_day}-{end_day}"}), 404

    # Reuse weekly PDF generator since it handles lists of reports cleanly
    pdf_bytes = PDFReportGenerator.generate_weekly_report_pdf(reports, flat_id)
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={flat_id}_monthly_days_{start_day}-{end_day}.pdf"
        },
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
