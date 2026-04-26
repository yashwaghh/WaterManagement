"""
Dummy Sensor Simulator for Water Management System
Generates realistic water usage data and writes to Firebase every 5 seconds.
Simulates water tank depletion and usage patterns.
"""

import firebase_admin
from firebase_admin import credentials, db
import os
import random
import time
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
SERVICE_ACCOUNT_PATH = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "./service_account.json")
DATABASE_URL = os.getenv("FIREBASE_DATABASE_URL")
DB_PATH = os.getenv("FIREBASE_DB_PATH", "/readings")
POLL_INTERVAL = 5  # seconds

# Simulator constants
INITIAL_WATER_ML = 5000  # 5 liters
MIN_USAGE_ML = 10
MAX_USAGE_ML = 60

# Profile multipliers for simulated flats (from rankinginstruction.md)
PROFILE_MULTIPLIERS = {
    "efficient": 0.55,
    "normal": 0.90,
    "normal_variable": 1.00,
    "high": 1.15,
    "penalty": 1.35,
}


class WaterSensorSimulator:
    """Simulates water sensor readings and sends to Firebase."""

    def __init__(self, flat_id: str = "flat_001"):
        """
        Initialize the simulator.

        Args:
            flat_id: Identifier for the simulated flat/unit
        """
        self.flat_id = flat_id
        self.water_left = INITIAL_WATER_ML
        self.cumulative_daily_usage = 0  # Resets each day
        self.daily_cycle_count = 0  # Track which day we're on
        self.start_time = datetime.now()
        self.initialized = False

        self._initialize_firebase()

    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK."""
        if not os.path.exists(SERVICE_ACCOUNT_PATH):
            raise FileNotFoundError(f"Service account not found: {SERVICE_ACCOUNT_PATH}")

        if not DATABASE_URL:
            raise ValueError("FIREBASE_DATABASE_URL not set in .env")

        try:
            # Check if Firebase is already initialized
            try:
                firebase_admin.get_app()
            except ValueError:
                # App not initialized, create it
                cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
                firebase_admin.initialize_app(cred, {"databaseURL": DATABASE_URL})

            self.initialized = True
            print(f"✅ Firebase initialized successfully")
            print(f"📍 Database: {DATABASE_URL}")
            print(f"📁 Path: {DB_PATH}")

        except Exception as e:
            raise RuntimeError(f"Failed to initialize Firebase: {str(e)}")

    def generate_reading(self) -> dict:
        """
        Generate a single sensor reading.

        Returns:
            Dictionary with sensor data
        """
        # Generate random water usage for this interval (5 seconds)
        water_used_interval = random.randint(MIN_USAGE_ML, MAX_USAGE_ML)

        # Update daily cumulative usage (resets each day)
        self.cumulative_daily_usage += water_used_interval

        # Daily threshold is INITIAL_WATER_ML (reset each day)
        self.water_left = max(0, INITIAL_WATER_ML - self.cumulative_daily_usage)

        # Calculate flow rate: ml per minute
        flow_rate_ml_min = water_used_interval * 12

        # Calculate current day based on elapsed time
        # Assuming 1 real minute = 1 simulated day
        elapsed_minutes = (datetime.now() - self.start_time).total_seconds() / 60
        current_day = int(elapsed_minutes) + 1  # Day 1, 2, 3, etc.

        # Create reading object
        reading = {
            "unique_id": self.flat_id,
            "water_used_ml": self.cumulative_daily_usage,  # Daily cumulative
            "water_left_ml": self.water_left,
            "flow_rate_ml_min": flow_rate_ml_min,
            "timestamp": datetime.now().isoformat(),
            "day": current_day,  # Track which day
            "daily_threshold_ml": INITIAL_WATER_ML,  # Daily threshold
        }

        return reading

    def send_to_firebase(self, reading: dict):
        """
        Send reading to Firebase.

        Args:
            reading: Dictionary with sensor data
        """
        try:
            ref = db.reference(DB_PATH)

            # Write to "current" for live dashboard
            ref.child("current").set(reading)

            # Also append to "history" for analytics
            history_ref = ref.child("history")
            history_ref.push(reading)

            return True

        except Exception as e:
            print(f"❌ Failed to write to Firebase: {str(e)}")
            return False

    def run_simulation(self, duration: int = None, test_cycles: int = None):
        """
        Run continuous simulation.

        Args:
            duration: Run for X seconds (None = infinite)
            test_cycles: Run for X cycles then stop (None = infinite)
        """
        if not self.initialized:
            print("❌ Firebase not initialized")
            return

        print(f"\n🚀 Starting Water Sensor Simulator")
        print(f"   Flat ID: {self.flat_id}")
        print(f"   Daily Threshold: {INITIAL_WATER_ML} ml")
        print(f"   Poll Interval: {POLL_INTERVAL} seconds")
        print(f"   Usage per cycle: {MIN_USAGE_ML}-{MAX_USAGE_ML} ml")
        print(f"\n📊 Generating readings...\n")

        cycle = 0
        start_time = time.time()
        last_day = 0

        try:
            while True:
                # Check duration limit
                if duration and (time.time() - start_time) >= duration:
                    print(f"\n⏱️  Duration limit reached ({duration}s)")
                    break

                # Check cycle limit
                if test_cycles and cycle >= test_cycles:
                    print(f"\n✅ Test cycles completed ({test_cycles})")
                    break

                # Generate reading
                reading = self.generate_reading()
                current_day = reading.get("day", 1)

                # Reset water usage at start of new day
                if current_day > last_day:
                    self.cumulative_daily_usage = 0
                    self.water_left = INITIAL_WATER_ML
                    print(f"\n📅 Day {current_day} started - Water reset to {INITIAL_WATER_ML} ml\n")
                    last_day = current_day

                success = self.send_to_firebase(reading)

                if success:
                    cycle += 1
                    elapsed = time.time() - start_time
                    cycles_per_minute = cycle / (elapsed / 60) if elapsed > 0 else 0

                    print(
                        f"[{cycle:3d}] ✓ Day {current_day} | {reading['timestamp']} | "
                        f"Used: {reading['water_used_ml']:6.1f}ml | "
                        f"Left: {reading['water_left_ml']:6.1f}ml | "
                        f"Flow: {reading['flow_rate_ml_min']:6.1f}ml/min"
                    )

                # Wait before next reading
                time.sleep(POLL_INTERVAL)

        except KeyboardInterrupt:
            print(f"\n\n⏹️  Simulator stopped by user")
            print(f"   Total readings sent: {cycle}")
            print(f"   Total days simulated: {last_day}")
            print(f"   Current day usage: {self.cumulative_daily_usage:.1f} ml")


def main():
    """Main entry point."""
    try:
        # Create simulator for one flat
        simulator = WaterSensorSimulator(flat_id="flat_001")

        # Run indefinitely (Ctrl+C to stop)
        simulator.run_simulation()

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print(f"   Check that .env file exists and contains:")
        print(f"   - FIREBASE_SERVICE_ACCOUNT_PATH")
        print(f"   - FIREBASE_DATABASE_URL")
        exit(1)


class MultiFlatSimulator:
    """Factory for generating readings from multiple simulated flats without Firebase dependency."""

    # Default flats with profile assignments
    DEFAULT_FLATS = {
        "A-101": "efficient",       # 0.55x multiplier
        "A-102": "normal",          # 0.90x multiplier
        "A-103": "normal_variable", # 1.00x multiplier
        "A-104": "high",            # 1.15x multiplier
        "A-105": "penalty",         # 1.35x multiplier
    }

    def __init__(
        self,
        flats: dict = None,
        threshold_ml: int = 2500,
        simulated_day_length: int = 60,
        poll_interval: int = 5,
    ):
        """
        Initialize multi-flat simulator.

        Args:
            flats: Dict mapping flat_id -> profile (or None for defaults)
            threshold_ml: Daily usage threshold
            simulated_day_length: Duration of simulated day in seconds
            poll_interval: Time between polls in seconds
        """
        self.flats = flats or self.DEFAULT_FLATS.copy()
        self.threshold_ml = threshold_ml
        self.simulated_day_length = simulated_day_length
        self.poll_interval = poll_interval
        self.start_time = datetime.now()

        # Track state per flat
        self.flat_states = {
            flat_id: {
                "cumulative_daily_usage": 0,
                "water_left": INITIAL_WATER_ML,
                "profile": profile,
            }
            for flat_id, profile in self.flats.items()
        }

    def generate_readings_for_tick(self) -> dict:
        """
        Generate readings for all flats at current tick.

        Returns:
            Dict keyed by flat_id with sensor readings
        """
        readings = {}
        elapsed_seconds = (datetime.now() - self.start_time).total_seconds()

        # Calculate progress within current simulated day
        elapsed_in_day = elapsed_seconds % self.simulated_day_length
        day_progress = elapsed_in_day / self.simulated_day_length

        # Calculate current day
        current_day = int(elapsed_seconds // self.simulated_day_length) + 1

        # Ticks per day
        ticks_per_day = self.simulated_day_length / self.poll_interval

        # Base interval usage for a normal flat to reach threshold by end of day
        base_interval_usage = self.threshold_ml / ticks_per_day

        for flat_id, state in self.flat_states.items():
            profile = state["profile"]
            multiplier = PROFILE_MULTIPLIERS.get(profile, 1.0)

            # Random factor: 0.75 to 1.25
            random_factor = random.uniform(0.75, 1.25)

            # Calculate interval usage
            interval_usage = base_interval_usage * multiplier * random_factor

            # Reset at start of new day
            if elapsed_in_day < self.poll_interval:
                state["cumulative_daily_usage"] = 0
                state["water_left"] = INITIAL_WATER_ML

            # Update cumulative usage (capped at bottle capacity)
            state["cumulative_daily_usage"] = min(
                state["cumulative_daily_usage"] + interval_usage,
                INITIAL_WATER_ML
            )

            # Calculate water left
            state["water_left"] = max(
                0,
                INITIAL_WATER_ML - state["cumulative_daily_usage"]
            )

            # Calculate flow rate: (interval_usage / poll_interval) * 60
            flow_rate_ml_min = (interval_usage / self.poll_interval) * 60

            reading = {
                "unique_id": flat_id,
                "water_used_ml": round(state["cumulative_daily_usage"], 1),
                "water_left_ml": round(state["water_left"], 1),
                "flow_rate_ml_min": round(flow_rate_ml_min, 1),
                "timestamp": datetime.now().isoformat(),
                "day": current_day,
                "daily_threshold_ml": self.threshold_ml,
            }

            readings[flat_id] = reading

        return readings

    def reset(self):
        """Reset simulator state for new session."""
        self.start_time = datetime.now()
        for flat_id in self.flat_states:
            self.flat_states[flat_id]["cumulative_daily_usage"] = 0
            self.flat_states[flat_id]["water_left"] = INITIAL_WATER_ML





if __name__ == "__main__":
    main()
