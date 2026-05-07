"""
Water Management Analytics Hub - Simplified 2-Tab Design
Analytics Hub | Leaderboard & Ranking
"""

import streamlit as st
import os
from datetime import datetime
from dotenv import load_dotenv
import time
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from src.firebase_client import FirebaseClient
from src.analytics import Analytics
from src.ranking import Ranking
from src.multi_flat_ranking import MultiFlatRanking
from src.report_storage import ReportStorage
from src.theme import apply_custom_theme, ICONS
from simulator import MultiFlatSimulator

load_dotenv()


def validate_config():
    """Validate required environment variables."""
    required_config = {
        "SIMULATED_DAY_LENGTH_SECONDS": int,
        "USAGE_THRESHOLD_ML": int,
    }
    for key, expected_type in required_config.items():
        value = os.getenv(key)
        if not value:
            st.error(f"❌ Missing required configuration: {key}")
            st.stop()


def initialize_session_state():
    """Initialize session state for multi-flat support."""
    if "data_mode" not in st.session_state:
        st.session_state.data_mode = os.getenv("DATA_MODE", "simulation")

    if "current_cycle_readings_by_flat" not in st.session_state:
        st.session_state.current_cycle_readings_by_flat = {}

    if "cycle_start_time" not in st.session_state:
        st.session_state.cycle_start_time = datetime.now()

    if "simulated_day_number" not in st.session_state:
        st.session_state.simulated_day_number = 1

    if "completed_daily_reports" not in st.session_state:
        st.session_state.completed_daily_reports = {}

    if "completed_daily_leaderboards" not in st.session_state:
        st.session_state.completed_daily_leaderboards = {}

    if "current_leaderboard" not in st.session_state:
        st.session_state.current_leaderboard = []

    if "weekly_points" not in st.session_state:
        st.session_state.weekly_points = {}

    if "firebase_error" not in st.session_state:
        st.session_state.firebase_error = None

    if "firebase_client" not in st.session_state and st.session_state.data_mode == "firebase":
        try:
            st.session_state.firebase_client = FirebaseClient()
        except Exception as e:
            st.session_state.firebase_error = str(e)

    if "multi_flat_simulator" not in st.session_state:
        threshold = int(os.getenv("USAGE_THRESHOLD_ML", 2500))
        day_length = int(os.getenv("SIMULATED_DAY_LENGTH_SECONDS", 60))
        poll_interval = int(os.getenv("POLL_INTERVAL_SECONDS", 5))

        st.session_state.multi_flat_simulator = MultiFlatSimulator(
            threshold_ml=threshold,
            simulated_day_length=day_length,
            poll_interval=poll_interval,
        )

    if "selected_flat" not in st.session_state:
        st.session_state.selected_flat = "All Flats"


def fetch_and_process_readings():
    """Fetch readings from Firebase or generate from simulator."""
    if st.session_state.data_mode == "simulation":
        readings_by_flat = st.session_state.multi_flat_simulator.generate_readings_for_tick()

        for flat_id, reading in readings_by_flat.items():
            if flat_id not in st.session_state.current_cycle_readings_by_flat:
                st.session_state.current_cycle_readings_by_flat[flat_id] = []

            is_valid, _ = Analytics.validate_reading(reading)
            if is_valid:
                if "timestamp" not in reading:
                    reading["timestamp"] = datetime.now().isoformat()
                st.session_state.current_cycle_readings_by_flat[flat_id].append(reading)

    else:
        if st.session_state.firebase_error:
            return

        try:
            # Fetch readings for each known flat from Firebase
            known_flats = ["A-101", "A-102", "A-103", "A-104", "A-105"]
            for flat_id in known_flats:
                latest_reading = st.session_state.firebase_client.get_latest_reading(flat_id)
                if latest_reading is None:
                    continue

                is_valid, _ = Analytics.validate_reading(latest_reading)
                if not is_valid:
                    continue

                if "timestamp" not in latest_reading:
                    latest_reading["timestamp"] = datetime.now().isoformat()

                if flat_id not in st.session_state.current_cycle_readings_by_flat:
                    st.session_state.current_cycle_readings_by_flat[flat_id] = []

                st.session_state.current_cycle_readings_by_flat[flat_id].append(latest_reading)

        except Exception as e:
            st.session_state.firebase_error = str(e)


def check_and_compile_report():
    """Check if cycle complete and compile reports for all flats."""
    simulated_day_length = int(os.getenv("SIMULATED_DAY_LENGTH_SECONDS", 60))
    threshold = int(os.getenv("USAGE_THRESHOLD_ML", 2500))
    elapsed = (datetime.now() - st.session_state.cycle_start_time).total_seconds()

    if elapsed >= simulated_day_length and st.session_state.current_cycle_readings_by_flat:
        daily_reports = Analytics.compile_reports_by_flat(
            st.session_state.current_cycle_readings_by_flat,
            simulated_day=st.session_state.simulated_day_number,
        )

        leaderboard = MultiFlatRanking.rank_flats(
            daily_reports,
            threshold_ml=threshold,
            simulated_day=st.session_state.simulated_day_number,
            weekly_points=st.session_state.weekly_points,
            finalize_points=True,
        )

        day_num = st.session_state.simulated_day_number
        st.session_state.completed_daily_reports[day_num] = {
            flat_id: report.to_dict() if hasattr(report, 'to_dict') else report
            for flat_id, report in daily_reports.items()
        }
        st.session_state.completed_daily_leaderboards[day_num] = [
            r.to_dict() if hasattr(r, 'to_dict') else r for r in leaderboard
        ]

        for record in leaderboard:
            if record.unique_id not in st.session_state.weekly_points:
                st.session_state.weekly_points[record.unique_id] = 0
            st.session_state.weekly_points[record.unique_id] += record.daily_points

        st.session_state.current_cycle_readings_by_flat = {}
        st.session_state.cycle_start_time = datetime.now()
        st.session_state.simulated_day_number += 1

        return leaderboard

    return None


def main():
    """Main app with 2 tabs: Analytics Hub and Leaderboard."""
    st.set_page_config(
        page_title="Water Management Analytics Hub",
        page_icon=ICONS["water"],
        layout="wide",
    )

    apply_custom_theme()
    validate_config()
    initialize_session_state()

    # Background logic
    fetch_and_process_readings()
    finalized_leaderboard = check_and_compile_report()

    # Calculate current leaderboard
    threshold = int(os.getenv("USAGE_THRESHOLD_ML", 2500))
    if st.session_state.current_cycle_readings_by_flat:
        daily_reports = Analytics.compile_reports_by_flat(
            st.session_state.current_cycle_readings_by_flat,
            simulated_day=st.session_state.simulated_day_number,
        )
        st.session_state.current_leaderboard = [
            r.to_dict() if hasattr(r, 'to_dict') else r
            for r in MultiFlatRanking.rank_flats(
                daily_reports,
                threshold_ml=threshold,
                simulated_day=st.session_state.simulated_day_number,
                weekly_points=st.session_state.weekly_points,
                finalize_points=False,
            )
        ]

    # Sidebar
    with st.sidebar:
        st.header(f"{ICONS['water']} Water Management")
        st.write(f"**Mode:** {st.session_state.data_mode.title()}")
        st.write(f"**Day:** {st.session_state.simulated_day_number}")

        st.divider()

        flat_options = ["All Flats"] + sorted(
            list(st.session_state.current_cycle_readings_by_flat.keys())
        )
        st.session_state.selected_flat = st.selectbox("View Flat", flat_options, index=0)

        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Threshold", f"{threshold} ml")
        with col2:
            st.metric("Capacity", "5000 ml")

        st.divider()

        if st.button("Reset Day", use_container_width=True):
            st.session_state.current_cycle_readings_by_flat = {}
            st.session_state.cycle_start_time = datetime.now()
            if st.session_state.data_mode == "simulation":
                st.session_state.multi_flat_simulator.reset()
            st.rerun()

        if st.button("Reset Week", use_container_width=True):
            st.session_state.weekly_points = {}
            st.session_state.completed_daily_reports = {}
            st.session_state.completed_daily_leaderboards = {}
            st.session_state.simulated_day_number = 1
            st.session_state.current_cycle_readings_by_flat = {}
            st.session_state.cycle_start_time = datetime.now()
            if st.session_state.data_mode == "simulation":
                st.session_state.multi_flat_simulator.reset()
            st.rerun()

    # Header
    st.markdown(f"# {ICONS['water']} Water Management Analytics Hub")
    st.markdown("*Save water. Sustain life. Track impact.*")
    st.divider()

    # Two Tabs
    tab1, tab2 = st.tabs(["📈 Analytics Hub", "🏆 Leaderboard & Ranking"])

    # ============ TAB 1: ANALYTICS HUB ============
    with tab1:
        # Live Metrics
        st.subheader("Live Metrics")

        if not st.session_state.current_cycle_readings_by_flat:
            st.info("Waiting for sensor data...")
        else:
            simulated_day_length = int(os.getenv("SIMULATED_DAY_LENGTH_SECONDS", 60))
            elapsed = (datetime.now() - st.session_state.cycle_start_time).total_seconds()
            time_remaining = max(0, simulated_day_length - elapsed)
            progress = min(elapsed / simulated_day_length, 1.0)

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("📅 Day", st.session_state.simulated_day_number)
            col2.metric("⏱️ Remaining", f"{int(time_remaining)}s")
            col3.metric("🏢 Active Flats", len(st.session_state.current_cycle_readings_by_flat))
            if st.session_state.current_leaderboard:
                leader = st.session_state.current_leaderboard[0].get("unique_id", "—")
                col4.metric("🏆 Leader", leader)

            st.progress(progress)

        st.divider()

        # Charts
        st.subheader("Water Usage Analysis")

        if st.session_state.current_cycle_readings_by_flat:
            col1, col2 = st.columns(2)

            # Water Usage Trend
            with col1:
                st.write("**Water Usage Trend**")
                if st.session_state.selected_flat == "All Flats":
                    all_readings = []
                    for flat_id, readings in st.session_state.current_cycle_readings_by_flat.items():
                        for reading in readings:
                            reading_copy = reading.copy()
                            reading_copy["flat_id"] = flat_id
                            all_readings.append(reading_copy)
                    df = Analytics.convert_to_dataframe(all_readings)
                    if not df.empty:
                        fig = px.line(df, x="timestamp", y="water_used_ml", color="flat_id")
                        fig.update_layout(height=300, margin=dict(l=0, r=0, t=0, b=0))
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    readings = st.session_state.current_cycle_readings_by_flat.get(
                        st.session_state.selected_flat, []
                    )
                    df = Analytics.convert_to_dataframe(readings)
                    if not df.empty:
                        fig = px.line(df, x="timestamp", y="water_used_ml")
                        fig.update_layout(height=300, margin=dict(l=0, r=0, t=0, b=0))
                        st.plotly_chart(fig, use_container_width=True)

            # Water Consumption Pie
            with col2:
                st.write("**Water Consumption**")
                if st.session_state.selected_flat != "All Flats":
                    readings = st.session_state.current_cycle_readings_by_flat.get(
                        st.session_state.selected_flat, []
                    )
                    if readings:
                        latest = readings[-1]
                        water_used = latest.get("water_used_ml", 0)
                        water_remaining = max(0, threshold - water_used)

                        fig = go.Figure(
                            data=[
                                go.Pie(
                                    labels=["Used", "Remaining"],
                                    values=[water_used, max(water_remaining, 0)],
                                    marker=dict(colors=["#ff9999", "#99ff99"]),
                                )
                            ]
                        )
                        fig.update_layout(height=300, margin=dict(l=0, r=0, t=0, b=0))
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Select a flat to view consumption")

            st.divider()

            # Flat Status Table
            st.subheader("Current Status by Flat")
            status_data = []
            for flat_id in sorted(st.session_state.current_cycle_readings_by_flat.keys()):
                readings = st.session_state.current_cycle_readings_by_flat[flat_id]
                if readings:
                    latest = readings[-1]
                    water_used = latest.get("water_used_ml", 0)
                    status = Ranking.classify_usage(water_used, threshold)
                    emoji = Ranking.get_status_emoji(status)

                    rank = "—"
                    for record in st.session_state.current_leaderboard:
                        if record.get("unique_id") == flat_id:
                            rank = record.get("rank", "—")
                            break

                    status_data.append({
                        "🏆": rank,
                        "Flat": flat_id,
                        "Status": f"{emoji} {status}",
                        "Usage": f"{water_used:.0f} ml",
                        "Water Left": f"{latest.get('water_left_ml', 0):.0f} ml",
                    })

            if status_data:
                df = pd.DataFrame(status_data)
                st.dataframe(df, use_container_width=True, hide_index=True)

    # ============ TAB 2: LEADERBOARD & RANKING ============
    with tab2:
        # Live Leaderboard
        st.subheader("Live Leaderboard (Current Day)")

        if st.session_state.current_leaderboard:
            leaderboard_data = []
            for record in st.session_state.current_leaderboard:
                status_emoji = Ranking.get_status_emoji(record.get("status", "Normal"))
                leaderboard_data.append({
                    "🏆": record.get("rank", "—"),
                    "Flat": record.get("unique_id", "—"),
                    "Status": f"{status_emoji} {record.get('status', '—')}",
                    "Usage": f"{record.get('total_usage_ml', 0):.0f} ml",
                    "Ratio": f"{record.get('usage_ratio', 0):.0%}",
                    "Score": f"{record.get('efficiency_score', 0):.1f}",
                    "Daily Pts": f"{record.get('daily_points', 0):+d}",
                    "Weekly": f"{record.get('weekly_points', 0)}",
                })

            df = pd.DataFrame(leaderboard_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Waiting for data...")

        st.divider()

        # Weekly Points
        st.subheader("Weekly Points Accumulation")

        if st.session_state.weekly_points:
            weekly_data = []
            for flat_id in sorted(st.session_state.weekly_points.keys()):
                points = st.session_state.weekly_points[flat_id]
                weekly_data.append({"Flat": flat_id, "Weekly Points": points})

            weekly_data.sort(key=lambda x: x["Weekly Points"], reverse=True)

            df = pd.DataFrame(weekly_data)
            df.insert(0, "Rank", range(1, len(df) + 1))

            st.dataframe(df, use_container_width=True, hide_index=True)

            col1, col2 = st.columns(2)
            with col1:
                leader = max(st.session_state.weekly_points.items(), key=lambda x: x[1])[0]
                st.metric("Weekly Leader", leader)
            with col2:
                total = sum(st.session_state.weekly_points.values())
                st.metric("Total Weekly Points", total)
        else:
            st.info("Weekly tracking starts after first day completes...")

        st.divider()

        # Reports Section
        st.subheader("Reports")

        available_days = sorted(st.session_state.completed_daily_reports.keys())

        if available_days:
            all_flats = sorted(set(
                flat_id for day_reports in st.session_state.completed_daily_reports.values()
                for flat_id in day_reports.keys()
            ))

            col1, col2 = st.columns([1, 1])

            with col1:
                report_flat = st.selectbox("Flat", all_flats, key="report_flat")

            with col2:
                report_day = st.selectbox(
                    "Day",
                    available_days,
                    format_func=lambda x: f"Day {x}",
                    key="report_day"
                )

            if report_day in st.session_state.completed_daily_reports:
                day_reports = st.session_state.completed_daily_reports[report_day]

                if report_flat in day_reports:
                    report = day_reports[report_flat]

                    st.success(f"Report: {report_flat} - Day {report_day}")

                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Usage", f"{report.get('total_usage_ml', 0):.1f} ml")
                    col2.metric("Peak Flow", f"{report.get('peak_flow_ml_min', 0):.1f} ml/min")
                    col3.metric("Avg Flow", f"{report.get('average_flow_ml_min', 0):.1f} ml/min")
                    col4.metric("Min Water", f"{report.get('min_water_left_ml', 0):.1f} ml")

                    st.info(f"💡 {report.get('suggested_reduction', 'No suggestion')}")

                    # Download as JSON (simple alternative to PDF)
                    import json
                    json_str = json.dumps(report, indent=2, default=str)
                    st.download_button(
                        "📥 Download Report (JSON)",
                        json_str,
                        f"report_{report_flat}_day_{report_day}.json",
                        "application/json",
                        use_container_width=True,
                    )

        else:
            st.info("No completed reports yet. Check back after first day finishes!")

    # Auto-refresh
    poll_interval = int(os.getenv("POLL_INTERVAL_SECONDS", 5))
    time.sleep(poll_interval)
    st.rerun()


if __name__ == "__main__":
    main()
