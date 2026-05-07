"""
Debug script to check if reports are being generated and stored.
Run this to diagnose report generation issues.
"""

import json
import os
import sys
from datetime import datetime
from src.report_storage import ReportStorage

# All known flat IDs in the system
DEFAULT_FLATS = ["A-101", "A-102", "A-103", "A-104", "A-105"]


def debug_reports(flat_ids=None):
    """Check report generation status."""
    if flat_ids is None:
        flat_ids = DEFAULT_FLATS

    print("\n" + "=" * 60)
    print("🔍 REPORT STORAGE DEBUG")
    print("=" * 60 + "\n")

    # 1. Check if data directory exists
    if os.path.exists("data"):
        print("✅ data/ directory exists")
    else:
        print("❌ data/ directory NOT found")
        return

    # 2. Check if reports.json exists
    if os.path.exists("data/reports.json"):
        print("✅ data/reports.json exists")
    else:
        print("❌ data/reports.json NOT found")
        return

    # 3. Check file size
    file_size = os.path.getsize("data/reports.json")
    print(f"💾 File size: {file_size} bytes")

    # 4. Validate JSON
    try:
        with open("data/reports.json", "r") as f:
            content = json.load(f)
            if isinstance(content, list):
                print(f"✅ JSON is valid — {len(content)} total records")
            else:
                print("❌ JSON structure is invalid (expected list)")
                return
    except json.JSONDecodeError:
        print("❌ JSON file is corrupted!")
        print("   Run: python debug_reports.py --fix")
        return
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return

    # 5. Load and display reports per flat
    print(f"\n📊 Reports by flat:")
    total_reports = 0
    for flat_id in flat_ids:
        reports = ReportStorage.load_all_reports(flat_id)
        total_reports += len(reports)
        print(f"   {flat_id}: {len(reports)} reports")

        if reports:
            for i, report in enumerate(reports[-3:], 1):  # Show last 3
                print(f"      [{i}] Day {report.get('day', 'N/A')} | "
                      f"Usage: {report.get('total_usage_ml', 'N/A')} ml | "
                      f"Peak: {report.get('peak_flow_ml_min', 'N/A')} ml/min")

    if total_reports == 0:
        print("\n   ⚠️  No reports found across any flat!")
        print("   This could mean:")
        print("   1. Simulator hasn't run for 60 seconds yet")
        print("   2. No daily cycles have been finalized (click 'Reset Day' in Admin)")
        print("   3. Reports aren't being saved")

    print("\n" + "=" * 60)
    print("✨ Debugging complete")
    print("=" * 60 + "\n")

    # 6. Recommendations
    print("📝 TROUBLESHOOTING TIPS:\n")
    print("   • If 0 reports: Finalize a day via Admin → 'Reset Day'")
    print("   • Check API is running: python api.py")
    print("   • Check dashboard shows data in Leaderboard tab")
    print("   • Check Firebase connection status\n")


def fix_corrupted_json():
    """Attempt to fix corrupted JSON."""
    print("\n🔧 Attempting to fix corrupted reports.json...")
    try:
        os.makedirs("data", exist_ok=True)
        with open("data/reports.json", "w") as f:
            json.dump([], f, indent=2)
        print("✅ File reset to empty array")
    except Exception as e:
        print(f"❌ Failed to fix: {str(e)}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--fix":
        fix_corrupted_json()
    else:
        debug_reports()
