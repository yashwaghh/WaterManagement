"""
On-Demand Report Generator
Generate reports for custom date/day ranges on demand.
"""

from datetime import datetime
from typing import List, Dict, Any
from src.report_storage import ReportStorage
from src.analytics import Analytics


class ReportGenerator:
    """Generate reports on demand for custom ranges."""

    @staticmethod
    def get_reports_by_day_range(start_day: int, end_day: int, flat_id: str = None) -> List[Dict[str, Any]]:
        """
        Get all reports within a day range.

        Args:
            start_day: Starting day number (1, 2, 3...)
            end_day: Ending day number
            flat_id: Optional flat ID to filter by specific flat

        Returns:
            List of reports in range
        """
        if flat_id:
            all_reports = ReportStorage.load_all_reports(flat_id)
        else:
            all_reports = ReportStorage.load_all_reports()

        # Filter by day range
        filtered = []
        for report in all_reports:
            day = report.get("day")
            if day and start_day <= day <= end_day:
                filtered.append(report)

        return sorted(filtered, key=lambda r: r.get("day", 0))

    @staticmethod
    def generate_daily_report_on_demand(day: int, flat_id: str = None) -> Dict[str, Any] or None:
        """
        Generate a report for a specific day.

        Args:
            day: Day number (1, 2, 3...)
            flat_id: Optional flat ID to filter by specific flat

        Returns:
            Report dictionary or None if not found
        """
        if flat_id:
            all_reports = ReportStorage.load_all_reports(flat_id)
        else:
            all_reports = ReportStorage.load_all_reports()

        # Find report by day
        for report in all_reports:
            if report.get("day") == day:
                return report

        return None

    @staticmethod
    def generate_weekly_report_on_demand(
        start_day: int, end_day: int, flat_id: str = None
    ) -> Dict[str, Any] or None:
        """
        Generate a weekly report for a day range.

        Args:
            start_day: Starting day number
            end_day: Ending day number
            flat_id: Optional flat ID to filter by specific flat

        Returns:
            Compiled weekly report or None
        """
        reports = ReportGenerator.get_reports_by_day_range(start_day, end_day, flat_id)

        if not reports:
            return None

        # Compile weekly statistics
        total_usage = sum(r.get("total_usage_ml", 0) for r in reports)
        avg_daily = total_usage / len(reports) if reports else 0
        peak_flow = max((r.get("peak_flow_ml_min", 0) for r in reports), default=0)
        min_water = min((r.get("min_water_left_ml", 0) for r in reports), default=0)

        return {
            "period": f"Days {start_day}-{end_day}",
            "flat_id": flat_id,
            "num_days": len(reports),
            "total_usage_ml": total_usage,
            "average_daily_usage_ml": avg_daily,
            "peak_flow_ml_min": peak_flow,
            "min_water_left_ml": min_water,
            "daily_reports": reports,
            "generated_timestamp": datetime.now().isoformat(),
        }

    @staticmethod
    def get_available_days() -> List[int]:
        """
        Get list of available day numbers.

        Returns:
            Sorted list of day numbers
        """
        all_reports = ReportStorage.load_all_reports()
        days = set()

        for report in all_reports:
            day = report.get("day")
            if day:
                days.add(day)

        return sorted(list(days))

