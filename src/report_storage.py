"""
Report Storage Module
Manages persistence of daily reports to JSON file.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from src.analytics import DailyReport


class ReportStorage:
    """Handles storing and retrieving daily reports."""

    REPORTS_FILE = "data/reports.json"

    @staticmethod
    def _ensure_data_dir():
        """Ensure data directory exists."""
        os.makedirs("data", exist_ok=True)

    @staticmethod
    def save_report(report: DailyReport, flat_id: str = "flat_001"):
        """
        Save a report to persistent storage.

        Args:
            report: DailyReport object
            flat_id: Identifier for the flat
        """
        ReportStorage._ensure_data_dir()

        # Load existing reports
        reports = ReportStorage.load_all_reports(flat_id)

        # Convert report to dict
        report_dict = {
            "id": report.report_timestamp.isoformat(),
            "flat_id": flat_id,
            "day": report.day,  # NEW: Store day number
            "total_usage_ml": float(report.total_usage_ml),
            "min_water_left_ml": float(report.min_water_left_ml),
            "average_flow_ml_min": float(report.average_flow_ml_min),
            "peak_flow_ml_min": float(report.peak_flow_ml_min),
            "peak_usage_timestamp": report.peak_usage_timestamp.isoformat(),
            "suggested_reduction": str(report.suggested_reduction),
            "report_timestamp": report.report_timestamp.isoformat(),
        }

        # Add to reports
        reports.append(report_dict)

        # Save to file with atomic write (write to temp, then rename)
        try:
            import tempfile
            temp_fd, temp_path = tempfile.mkstemp(dir="data", suffix=".json")
            with open(temp_fd, 'w') as f:
                json.dump(reports, f, indent=2)

            # Atomic rename
            import os
            import shutil
            shutil.move(temp_path, ReportStorage.REPORTS_FILE)
            print(f"✅ Report saved: {report.report_timestamp}")
        except Exception as e:
            print(f"❌ Failed to save report: {str(e)}")
            # Clean up temp file if it exists
            try:
                os.remove(temp_path)
            except:
                pass

    @staticmethod
    def load_all_reports(flat_id: str = "flat_001") -> List[Dict[str, Any]]:
        """
        Load all reports from storage.

        Args:
            flat_id: Identifier for the flat

        Returns:
            List of report dictionaries
        """
        if not os.path.exists(ReportStorage.REPORTS_FILE):
            return []

        try:
            with open(ReportStorage.REPORTS_FILE, "r") as f:
                all_reports = json.load(f)
                # Filter by flat_id
                return [r for r in all_reports if r.get("flat_id") == flat_id]
        except Exception as e:
            print(f"⚠️ Failed to load reports: {str(e)}")
            return []

    @staticmethod
    def get_latest_report(flat_id: str = "flat_001") -> Optional[Dict[str, Any]]:
        """
        Get the most recent report.

        Args:
            flat_id: Identifier for the flat

        Returns:
            Latest report dictionary or None
        """
        reports = ReportStorage.load_all_reports(flat_id)
        return reports[-1] if reports else None

    @staticmethod
    def get_weekly_reports(flat_id: str = "flat_001") -> List[Dict[str, Any]]:
        """
        Get reports from the last 7 days.

        Args:
            flat_id: Identifier for the flat

        Returns:
            List of reports from last 7 days
        """
        from datetime import timedelta

        reports = ReportStorage.load_all_reports(flat_id)
        cutoff = datetime.now() - timedelta(days=7)

        return [
            r
            for r in reports
            if datetime.fromisoformat(r["report_timestamp"]) >= cutoff
        ]

    @staticmethod
    def delete_report(report_id: str, flat_id: str = "flat_001"):
        """
        Delete a specific report.

        Args:
            report_id: ISO format timestamp of report
            flat_id: Identifier for the flat
        """
        reports = ReportStorage.load_all_reports(flat_id)
        reports = [r for r in reports if r["id"] != report_id]

        try:
            with open(ReportStorage.REPORTS_FILE, "w") as f:
                json.dump(reports, f, indent=2)
        except Exception as e:
            print(f"⚠️ Failed to delete report: {str(e)}")

    @staticmethod
    def clear_all_reports(flat_id: str = "flat_001"):
        """
        Clear all reports for a flat.

        Args:
            flat_id: Identifier for the flat
        """
        all_reports = []
        if os.path.exists(ReportStorage.REPORTS_FILE):
            try:
                with open(ReportStorage.REPORTS_FILE, "r") as f:
                    all_reports = json.load(f)
            except:
                pass

        # Remove reports for this flat
        all_reports = [r for r in all_reports if r.get("flat_id") != flat_id]

        try:
            with open(ReportStorage.REPORTS_FILE, "w") as f:
                json.dump(all_reports, f, indent=2)
        except Exception as e:
            print(f"⚠️ Failed to clear reports: {str(e)}")
