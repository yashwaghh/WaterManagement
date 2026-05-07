"""
SQLite persistence layer for Water Management System session state.

Persists: current_day, weekly_points, completed_daily_leaderboards.
Uses Python's built-in sqlite3 — no extra dependencies required.
"""

import json
import os
import sqlite3
import threading
from typing import Any, Dict, List


_DEFAULT_DB_PATH = "./water_management.db"

# Module-level connection + lock so that :memory: databases work correctly
# (each sqlite3.connect(":memory:") opens a *new* isolated database, so we
# must reuse one connection for the lifetime of the process).
_conn: sqlite3.Connection | None = None
_conn_lock = threading.Lock()


def _get_connection() -> sqlite3.Connection:
    global _conn
    with _conn_lock:
        db_path = os.getenv("SQLITE_DB_PATH", _DEFAULT_DB_PATH)
        if _conn is None:
            _conn = sqlite3.connect(db_path, check_same_thread=False)
            _conn.row_factory = sqlite3.Row
            _conn.execute(
                """
                CREATE TABLE IF NOT EXISTS app_state (
                    key   TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
                """
            )
            _conn.commit()
    return _conn


def _reset_connection() -> None:
    """Force a new connection (used in tests to swap the DB path)."""
    global _conn
    with _conn_lock:
        if _conn is not None:
            try:
                _conn.close()
            except Exception:
                pass
            _conn = None


def init_db() -> None:
    """Create tables if they do not already exist."""
    conn = _get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS app_state (
            key   TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS redemptions (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            flat_id    TEXT NOT NULL,
            item_id    TEXT NOT NULL,
            item_title TEXT NOT NULL,
            points_cost INTEGER NOT NULL,
            redeemed_at TEXT NOT NULL
        )
        """
    )
    conn.commit()


# ---------------------------------------------------------------------------
# Generic key/value helpers
# ---------------------------------------------------------------------------

def _set(key: str, value: Any) -> None:
    conn = _get_connection()
    conn.execute(
        "INSERT INTO app_state (key, value) VALUES (?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, json.dumps(value)),
    )
    conn.commit()


def _get(key: str, default: Any = None) -> Any:
    conn = _get_connection()
    row = conn.execute(
        "SELECT value FROM app_state WHERE key = ?", (key,)
    ).fetchone()
    if row is None:
        return default
    try:
        return json.loads(row["value"])
    except (json.JSONDecodeError, TypeError):
        return default


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_state() -> Dict[str, Any]:
    """Load persisted session state. Returns defaults for any missing keys."""
    init_db()
    return {
        "simulated_day_number": _get("simulated_day_number", 1),
        "weekly_points": _get("weekly_points", {}),
        "completed_daily_leaderboards": _get("completed_daily_leaderboards", []),
    }


def save_day(day_number: int) -> None:
    """Persist the current day number."""
    _set("simulated_day_number", day_number)


def save_weekly_points(weekly_points: Dict[str, int]) -> None:
    """Persist the weekly points dictionary."""
    _set("weekly_points", weekly_points)


def save_completed_leaderboards(leaderboards: List[Any]) -> None:
    """Persist the completed daily leaderboards list."""
    _set("completed_daily_leaderboards", leaderboards)


def reset_week_state() -> None:
    """Reset weekly state (points + completed leaderboards + redemptions) back to defaults."""
    save_day(1)
    save_weekly_points({})
    save_completed_leaderboards([])
    clear_all_redemptions()


# ---------------------------------------------------------------------------
# Redemption tracking
# ---------------------------------------------------------------------------

def save_redemption(flat_id: str, item_id: str, item_title: str, points_cost: int) -> int:
    """Record a store redemption. Returns the new redemption ID."""
    from datetime import datetime
    conn = _get_connection()
    cursor = conn.execute(
        "INSERT INTO redemptions (flat_id, item_id, item_title, points_cost, redeemed_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (flat_id, item_id, item_title, points_cost, datetime.now().isoformat()),
    )
    conn.commit()
    return cursor.lastrowid


def get_total_redeemed(flat_id: str) -> int:
    """Get the total points redeemed by a flat."""
    conn = _get_connection()
    row = conn.execute(
        "SELECT COALESCE(SUM(points_cost), 0) as total FROM redemptions WHERE flat_id = ?",
        (flat_id,),
    ).fetchone()
    return row["total"] if row else 0


def get_redemptions(flat_id: str) -> List[Dict]:
    """Get all redemptions for a flat."""
    conn = _get_connection()
    rows = conn.execute(
        "SELECT id, item_id, item_title, points_cost, redeemed_at "
        "FROM redemptions WHERE flat_id = ? ORDER BY redeemed_at DESC",
        (flat_id,),
    ).fetchall()
    return [dict(r) for r in rows]


def clear_all_redemptions() -> None:
    """Clear all redemptions (used on weekly reset)."""
    conn = _get_connection()
    conn.execute("DELETE FROM redemptions")
    conn.commit()
