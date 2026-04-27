"""
Firebase client module for reading water management data.
Handles Firebase Admin SDK initialization and data retrieval.
"""

import firebase_admin
from firebase_admin import credentials, db
from typing import Optional, Dict, Any
import os


class FirebaseClient:
    """Manages Firebase connection and data operations."""

    _instance = None

    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize Firebase client."""
        if self._initialized:
            return

        self.service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
        self.database_url = os.getenv("FIREBASE_DATABASE_URL")

        if not self.service_account_path:
            raise ValueError("FIREBASE_SERVICE_ACCOUNT_PATH not set")
        if not self.database_url:
            raise ValueError("FIREBASE_DATABASE_URL not set")
        if not os.path.exists(self.service_account_path):
            raise FileNotFoundError("Service account JSON not found")

        try:
            cred = credentials.Certificate(self.service_account_path)
            firebase_admin.initialize_app(cred, {
                "databaseURL": self.database_url
            })
            self._initialized = True
        except Exception as e:
            raise RuntimeError(f"Firebase init failed: {str(e)}")

    # 🔥 FIXED FUNCTION (IMPORTANT)
    def get_latest_reading(self, flat_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch latest reading for a specific flat.

        Args:
            flat_id: e.g., "A-101"

        Returns:
            Latest reading dict or None
        """
        try:
            ref = db.reference(f"readings/{flat_id}/current")
            data = ref.get()

            if data and isinstance(data, dict):
                return data

            return None

        except Exception as e:
            print(f"Firebase fetch error for {flat_id}: {e}")
            return None

    def get_history(self, flat_id: str, limit: int = 50) -> list:
        """
        Fetch the most-recent *limit* historical readings for a flat.

        The ESP8266 / simulator writes to ``readings/{flat_id}/history`` via
        Firebase ``push()``, so keys are time-ordered.  We retrieve the last
        *limit* entries ordered by key and return them as a plain list.

        Args:
            flat_id: e.g., "A-101"
            limit: Maximum number of readings to return (default 50).

        Returns:
            List of reading dicts, oldest first, or [] on error / no data.
        """
        try:
            ref = db.reference(f"readings/{flat_id}/history")
            data = ref.order_by_key().limit_to_last(limit).get()
            if not data:
                return []
            # data is an OrderedDict[push_id -> reading_dict] — return values only
            return list(data.values())
        except Exception as e:
            print(f"Firebase history fetch error for {flat_id}: {e}")
            return []

    # Optional (unchanged)
    def get_all_readings(self) -> Optional[list]:
        try:
            ref = db.reference("readings")
            data = ref.get()

            if not data:
                return None

            readings = []
            for flat_id, flat_data in data.items():
                if isinstance(flat_data, dict) and "current" in flat_data:
                    readings.append(flat_data["current"])

            return readings

        except Exception as e:
            raise RuntimeError(f"Failed to fetch readings: {str(e)}")