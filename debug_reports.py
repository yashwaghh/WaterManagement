"""
Debug script to check if reports are being generated and stored.
Run this to diagnose report generation issues.
"""

import json
import os
from datetime import datetime
from src.report_storage import ReportStorage


def debug_reports():
    """Check report generation status."""
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

    # 3. Load and display reports
    try:
        all_reports = ReportStorage.load_all_reports()
        print(f"\n📊 Total reports stored: {len(all_reports)}")

        if len(all_reports) == 0:
            print("   ⚠️  No reports found!")
            print("   This could mean:")
            print("   1. Simulator hasn't run for 60 seconds yet")
            print("   2. Daily cycle hasn't completed")
            print("   3. Reports aren't being saved")
            return

        print("\n📋 Report Details:")
        for i, report in enumerate(all_reports[-5:], 1):  # Show last 5
            print(f"\n   [{i}] Report {report.get('id', 'N/A')[:10]}...")
            print(f"       Date: {report.get('report_timestamp', 'N/A')}")
            print(f"       Usage: {report.get('total_usage_ml', 'N/A')} ml")
            print(f"       Peak Flow: {report.get('peak_flow_ml_min', 'N/A')} ml/min")

        # 4. Check file size
        file_size = os.path.getsize("data/reports.json")
        print(f"\n💾 File size: {file_size} bytes")

        # 5. Validate JSON
        with open("data/reports.json", "r") as f:
            content = json.load(f)
            if isinstance(content, list):
                print("✅ JSON is valid")
            else:
                print("❌ JSON structure is invalid")

    except json.JSONDecodeError:
        print("❌ JSON file is corrupted!")
        print("   Run: python debug_reports.py --fix")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

    print("\n" + "=" * 60)
    print("✨ Debugging complete")
    print("=" * 60 + "\n")

    # 6. Recommendations
    print("📝 TROUBLESHOOTING TIPS:\n")
    print("   • If 0 reports: Wait 60+ seconds for first daily cycle")
    print("   • Check simulator is running: python simulator.py")
    print("   • Check dashboard shows data in Live Metrics")
    print("   • If still no reports, restart dashboard: streamlit run app.py")
    print("   • Check Firebase connection status\n")


def fix_corrupted_json():
    """Attempt to fix corrupted JSON."""
    print("\n🔧 Attempting to fix corrupted reports.json...")
    try:
        with open("data/reports.json", "w") as f:
            json.dump([], f, indent=2)
        print("✅ File reset to empty array")
    except Exception as e:
        print(f"❌ Failed to fix: {str(e)}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--fix":
        fix_corrupted_json()
    else:
        debug_reports()
