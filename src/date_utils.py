"""
Date Utilities Module
Handles date-based report organization and week grouping.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Tuple


class DateUtils:
    """Utility functions for date and week handling."""

    @staticmethod
    def get_date_from_timestamp(timestamp_str: str) -> str:
        """
        Extract date (YYYY-MM-DD) from ISO timestamp.

        Args:
            timestamp_str: ISO format timestamp

        Returns:
            Date string (YYYY-MM-DD)
        """
        try:
            dt = datetime.fromisoformat(timestamp_str)
            return dt.strftime("%Y-%m-%d")
        except Exception:
            return timestamp_str[:10]

    @staticmethod
    def get_week_number(timestamp_str: str) -> int:
        """
        Get ISO week number from timestamp.

        Args:
            timestamp_str: ISO format timestamp

        Returns:
            Week number (1-53)
        """
        try:
            dt = datetime.fromisoformat(timestamp_str)
            return dt.isocalendar()[1]
        except Exception:
            return 1

    @staticmethod
    def get_week_start_end(timestamp_str: str) -> Tuple[str, str]:
        """
        Get the start and end date of the week containing the timestamp.

        Args:
            timestamp_str: ISO format timestamp

        Returns:
            Tuple of (start_date, end_date) in YYYY-MM-DD format
        """
        try:
            dt = datetime.fromisoformat(timestamp_str)
            # ISO week starts on Monday
            start = dt - timedelta(days=dt.weekday())
            end = start + timedelta(days=6)
            return (start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
        except Exception:
            return ("N/A", "N/A")

    @staticmethod
    def group_by_date(reports: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Group reports by date.

        Args:
            reports: List of report dictionaries

        Returns:
            Dictionary with dates as keys and report lists as values
        """
        grouped = {}
        for report in reports:
            date = DateUtils.get_date_from_timestamp(
                report.get("report_timestamp", "")
            )
            if date not in grouped:
                grouped[date] = []
            grouped[date].append(report)
        return dict(sorted(grouped.items()))

    @staticmethod
    def group_by_week(reports: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Group reports by week.

        Args:
            reports: List of report dictionaries

        Returns:
            Dictionary with week labels as keys and report lists as values
        """
        grouped = {}
        for report in reports:
            timestamp = report.get("report_timestamp", "")
            week_num = DateUtils.get_week_number(timestamp)
            start, end = DateUtils.get_week_start_end(timestamp)
            week_label = f"Week {week_num} ({start} - {end})"

            if week_label not in grouped:
                grouped[week_label] = []
            grouped[week_label].append(report)

        return dict(sorted(grouped.items()))

    @staticmethod
    def get_reports_for_date_range(
        reports: List[Dict], start_date: str, end_date: str
    ) -> List[Dict]:
        """
        Filter reports for a date range.

        Args:
            reports: List of report dictionaries
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            Filtered list of reports
        """
        filtered = []
        for report in reports:
            report_date = DateUtils.get_date_from_timestamp(
                report.get("report_timestamp", "")
            )
            if start_date <= report_date <= end_date:
                filtered.append(report)
        return filtered

    @staticmethod
    def get_last_n_days(reports: List[Dict], n: int = 7) -> List[Dict]:
        """
        Get reports from the last N days.

        Args:
            reports: List of report dictionaries
            n: Number of days

        Returns:
            Filtered list of reports
        """
        if not reports:
            return []

        # Get the most recent report date
        latest_date_str = reports[-1].get("report_timestamp", "")
        latest_date = datetime.fromisoformat(latest_date_str)

        # Calculate start date (n days ago)
        start_date = latest_date - timedelta(days=n - 1)

        filtered = []
        for report in reports:
            report_date_str = report.get("report_timestamp", "")
            try:
                report_date = datetime.fromisoformat(report_date_str)
                if report_date >= start_date:
                    filtered.append(report)
            except Exception:
                pass

        return filtered
