"""
Analytics module for processing water usage data.
Generates daily summaries and compiles reports from sensor readings.
"""

from typing import List, Dict, Any
from datetime import datetime
import pandas as pd
import statistics


class DailyReport:
    """Represents a completed daily (60-second cycle) report."""

    def __init__(
        self,
        total_usage_ml: float,
        min_water_left_ml: float,
        average_flow_ml_min: float,
        peak_flow_ml_min: float,
        peak_usage_timestamp: datetime,
        suggested_reduction: str,
        report_timestamp: datetime,
        day: int = None,
    ):
        self.total_usage_ml = total_usage_ml
        self.min_water_left_ml = min_water_left_ml
        self.average_flow_ml_min = average_flow_ml_min
        self.peak_flow_ml_min = peak_flow_ml_min
        self.peak_usage_timestamp = peak_usage_timestamp
        self.suggested_reduction = suggested_reduction
        self.report_timestamp = report_timestamp
        self.day = day

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary."""
        return {
            "total_usage_ml": self.total_usage_ml,
            "min_water_left_ml": self.min_water_left_ml,
            "average_flow_ml_min": self.average_flow_ml_min,
            "peak_flow_ml_min": self.peak_flow_ml_min,
            "peak_usage_timestamp": self.peak_usage_timestamp,
            "suggested_reduction": self.suggested_reduction,
            "report_timestamp": self.report_timestamp,
        }


class Analytics:
    """Processes readings and generates daily summaries."""

    @staticmethod
    def validate_reading(reading: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate a sensor reading for data integrity.

        Returns:
            (is_valid, error_message)
        """
        if not reading:
            return False, "Reading is empty"

        if "unique_id" not in reading:
            return False, "unique_id field missing"

        required_fields = ["water_used_ml", "water_left_ml", "flow_rate_ml_min"]
        for field in required_fields:
            if field not in reading:
                return False, f"{field} field missing"

            try:
                float(reading[field])
            except (ValueError, TypeError):
                return False, f"{field} is not numeric"

            if float(reading[field]) < 0:
                return False, f"{field} cannot be negative"

        return True, ""

    @staticmethod
    def compile_report(readings: List[Dict[str, Any]]) -> DailyReport:
        """
        Compile a daily report from a list of readings.

        Args:
            readings: List of sensor readings from a 60-second cycle

        Returns:
            DailyReport object with aggregated metrics
        """
        if not readings:
            return DailyReport(
                total_usage_ml=0,
                min_water_left_ml=0,
                average_flow_ml_min=0,
                peak_flow_ml_min=0,
                peak_usage_timestamp=datetime.now(),
                suggested_reduction="No data available",
                report_timestamp=datetime.now(),
            )

        # Extract day if available from readings
        day = None
        if readings and "day" in readings[0]:
            day = readings[0]["day"]

        # Convert to DataFrame for easier calculation
        df = pd.DataFrame(readings)

        # Handle cumulative water_used_ml: use difference between last and first
        water_used_values = df["water_used_ml"].tolist()
        if len(water_used_values) > 1:
            total_usage = water_used_values[-1] - water_used_values[0]
        else:
            total_usage = water_used_values[0] if water_used_values else 0

        # Ensure non-negative
        total_usage = max(0, total_usage)

        # Minimum water left during cycle
        min_water_left = df["water_left_ml"].min()

        # Flow rate statistics
        flow_rates = df["flow_rate_ml_min"].tolist()
        average_flow = statistics.mean(flow_rates) if flow_rates else 0
        peak_flow = max(flow_rates) if flow_rates else 0

        # Find peak usage timestamp
        peak_idx = df["flow_rate_ml_min"].idxmax()
        peak_timestamp = (
            pd.to_datetime(df.loc[peak_idx, "timestamp"]).to_pydatetime()
            if "timestamp" in df.columns and pd.notna(df.loc[peak_idx, "timestamp"])
            else datetime.now()
        )

        # Generate reduction suggestion
        suggested_reduction = Analytics._suggest_reduction(total_usage, average_flow)

        return DailyReport(
            total_usage_ml=round(total_usage, 2),
            min_water_left_ml=round(min_water_left, 2),
            average_flow_ml_min=round(average_flow, 2),
            peak_flow_ml_min=round(peak_flow, 2),
            peak_usage_timestamp=peak_timestamp,
            suggested_reduction=suggested_reduction,
            report_timestamp=datetime.now(),
            day=day,
        )

    @staticmethod
    def _suggest_reduction(total_usage_ml: float, average_flow: float) -> str:
        """
        Generate a suggestion for water usage reduction.

        Args:
            total_usage_ml: Total water used in the cycle
            average_flow: Average flow rate

        Returns:
            Suggestion message
        """
        if total_usage_ml < 500:
            return "Excellent usage! Keep maintaining this level."
        elif total_usage_ml < 1500:
            return "Good usage. Consider minor optimizations."
        elif total_usage_ml < 2500:
            return "Moderate usage. Look for opportunities to reduce."
        else:
            return "High usage detected. Immediate action recommended."

    @staticmethod
    def convert_to_dataframe(readings: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Convert readings list to a pandas DataFrame.

        Args:
            readings: List of sensor readings

        Returns:
            DataFrame with readings, or empty DataFrame if no valid data
        """
        if not readings:
            return pd.DataFrame()

        # Filter valid readings
        valid_readings = []
        for reading in readings:
            is_valid, _ = Analytics.validate_reading(reading)
            if is_valid:
                valid_readings.append(reading)

        if not valid_readings:
            return pd.DataFrame()

        df = pd.DataFrame(valid_readings)

        # Ensure timestamp is datetime
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

        return df

    @staticmethod
    def compile_reports_by_flat(
        readings_by_flat: Dict[str, List[Dict[str, Any]]],
        simulated_day: int = None
    ) -> Dict[str, "DailyReport"]:
        """
        Compile reports for multiple flats in a single call.

        Args:
            readings_by_flat: Dictionary keyed by flat_id with lists of readings for each flat
            simulated_day: Current simulated day number (optional)

        Returns:
            Dictionary keyed by flat_id with DailyReport objects
        """
        reports = {}

        for flat_id, readings in readings_by_flat.items():
            report = Analytics.compile_report(readings)
            if simulated_day is not None:
                report.day = simulated_day
            reports[flat_id] = report

        return reports
