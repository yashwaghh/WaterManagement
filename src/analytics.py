from typing import List, Dict, Any
from datetime import datetime
import pandas as pd
import statistics


class DailyReport:
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

    @staticmethod
    def compile_report(readings: List[Dict[str, Any]]) -> DailyReport:

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

        df = pd.DataFrame(readings)

        # -------------------------------
        # TOTAL USAGE (correct)
        # -------------------------------
        water_used_values = df["water_used_ml"].tolist()
        if len(water_used_values) > 1:
            total_usage = water_used_values[-1] - water_used_values[0]
        else:
            total_usage = water_used_values[0]

        total_usage = max(0, total_usage)

        # -------------------------------
        # WATER LEFT
        # -------------------------------
        min_water_left = df.get("water_left_ml", pd.Series([0])).min()

        # -------------------------------
        # FLOW LOGIC (FIXED)
        # -------------------------------
        flow_rates = df["flow_rate_ml_min"].fillna(0).tolist()

        # Remove noise (very small values)
        flow_rates = [f for f in flow_rates if f > 10]

        if len(flow_rates) == 0:
            average_flow = 0
            peak_flow = 0

        elif len(flow_rates) == 1:
            # Only one reading → treat it as peak
            average_flow = flow_rates[0]
            peak_flow = flow_rates[0]

        else:
            average_flow = statistics.mean(flow_rates)
            peak_flow = max(flow_rates)

        # -------------------------------
        # PEAK TIMESTAMP
        # -------------------------------
        if "timestamp" in df.columns and len(df) > 0:
            try:
                peak_idx = df["flow_rate_ml_min"].idxmax()
                peak_timestamp = pd.to_datetime(df.loc[peak_idx, "timestamp"]).to_pydatetime()
            except:
                peak_timestamp = datetime.now()
        else:
            peak_timestamp = datetime.now()

        # -------------------------------
        # SUGGESTION
        # -------------------------------
        suggested_reduction = Analytics._suggest_reduction(total_usage, average_flow)

        return DailyReport(
            total_usage_ml=round(total_usage, 2),
            min_water_left_ml=round(min_water_left, 2),
            average_flow_ml_min=round(average_flow, 2),
            peak_flow_ml_min=round(peak_flow, 2),
            peak_usage_timestamp=peak_timestamp,
            suggested_reduction=suggested_reduction,
            report_timestamp=datetime.now(),
        )

    @staticmethod
    def _suggest_reduction(total_usage_ml: float, average_flow: float) -> str:
        if total_usage_ml < 500:
            return "Excellent usage! Keep maintaining this level."
        elif total_usage_ml < 1500:
            return "Good usage. Consider minor optimizations."
        elif total_usage_ml < 2500:
            return "Moderate usage. Look for opportunities to reduce."
        else:
            return "High usage detected. Immediate action recommended."