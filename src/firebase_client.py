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
        """Ensure singleton pattern - only one Firebase app instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize Firebase client from environment variables."""
        if self._initialized:
            return

        self.service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
        self.database_url = os.getenv("FIREBASE_DATABASE_URL")
        self.db_path = os.getenv("FIREBASE_DB_PATH", "/readings")

        # Validate required configuration
        if not self.service_account_path:
            raise ValueError("FIREBASE_SERVICE_ACCOUNT_PATH not set in .env")
        if not self.database_url:
            raise ValueError("FIREBASE_DATABASE_URL not set in .env")
        if not os.path.exists(self.service_account_path):
            raise FileNotFoundError(
                f"Service account JSON not found: {self.service_account_path}"
            )

        try:
            cred = credentials.Certificate(self.service_account_path)
            firebase_admin.initialize_app(cred, {"databaseURL": self.database_url})
            self._initialized = True
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Firebase: {str(e)}")

    def get_latest_reading(self) -> Optional[Dict[str, Any]]:
        """
        Fetch the latest reading from Firebase Realtime Database.

        Returns:
            Dict with latest sensor reading or None if no data available.
            Expected fields: unique_id, water_used_ml, water_left_ml, flow_rate_ml_min, timestamp
        """
        try:
            # First try to read from "current" (simulator structure)
            ref = db.reference(f"{self.db_path}/current")
            data = ref.get()

            if data is not None and isinstance(data, dict):
                return data

            # Fallback: read from root path for other structures
            ref = db.reference(self.db_path)
            data = ref.get()

            if data is None:
                return None

            # If data is a list, return the last element
            if isinstance(data, list):
                return data[-1] if data else None

            # If data is a dict with nested readings, return the latest
            if isinstance(data, dict):
                # Check if it has "current" and "history" structure
                if "current" in data and isinstance(data["current"], dict):
                    return data["current"]

                # Assume last key is the latest reading
                latest_key = max(data.keys(), key=lambda k: data[k].get("timestamp", 0) if isinstance(data[k], dict) else 0)
                return data[latest_key] if isinstance(data[latest_key], dict) else None

            return data

        except Exception as e:
            raise RuntimeError(f"Failed to fetch data from Firebase: {str(e)}")

    def get_all_readings(self) -> Optional[list]:
        """
        Fetch all readings from Firebase Realtime Database.

        Returns:
            List of readings or None if no data available.
        """
        try:
            # First try to read from "history" (simulator structure)
            ref = db.reference(f"{self.db_path}/history")
            data = ref.get()

            if data is not None:
                if isinstance(data, list):
                    return data
                if isinstance(data, dict):
                    return list(data.values())

            # Fallback: read from root path
            ref = db.reference(self.db_path)
            data = ref.get()

            if data is None:
                return None

            if isinstance(data, list):
                return data

            if isinstance(data, dict):
                # Check if it has "history" key
                if "history" in data:
                    history = data["history"]
                    if isinstance(history, list):
                        return history
                    if isinstance(history, dict):
                        return list(history.values())

                # Otherwise return all values
                return list(data.values())

            return [data]

        except Exception as e:
            raise RuntimeError(f"Failed to fetch readings from Firebase: {str(e)}")
