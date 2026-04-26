"""
Ranking module for classifying water usage efficiency.
Provides usage status labels and ranking logic.
"""

from typing import Tuple


class Ranking:
    """Classifies and ranks water usage based on configured thresholds."""

    @staticmethod
    def classify_usage(total_usage_ml: float, threshold_ml: float) -> str:
        """
        Classify water usage into efficiency categories.

        Args:
            total_usage_ml: Total water used in ml
            threshold_ml: Usage threshold in ml

        Returns:
            Status label: "Efficient", "Normal", "High Usage", or "Penalty Zone"
        """
        if total_usage_ml <= threshold_ml * 0.7:
            return "Efficient"
        elif total_usage_ml <= threshold_ml:
            return "Normal"
        elif total_usage_ml <= threshold_ml * 1.2:
            return "High Usage"
        else:
            return "Penalty Zone"

    @staticmethod
    def get_status_color(status: str) -> str:
        """
        Get a color code for the status label.

        Args:
            status: Status label from classify_usage

        Returns:
            Color code for Streamlit
        """
        colors = {
            "Efficient": "green",
            "Normal": "blue",
            "High Usage": "orange",
            "Penalty Zone": "red",
        }
        return colors.get(status, "gray")

    @staticmethod
    def get_ranking_score(status: str) -> int:
        """
        Get a numeric ranking score for the status.

        Args:
            status: Status label from classify_usage

        Returns:
            Score where higher is better (0-100)
        """
        scores = {
            "Efficient": 100,
            "Normal": 75,
            "High Usage": 50,
            "Penalty Zone": 0,
        }
        return scores.get(status, 0)

    @staticmethod
    def get_status_emoji(status: str) -> str:
        """
        Get an emoji representation for the status.

        Args:
            status: Status label from classify_usage

        Returns:
            Emoji character
        """
        emojis = {
            "Efficient": "✅",
            "Normal": "⚪",
            "High Usage": "⚠️",
            "Penalty Zone": "❌",
        }
        return emojis.get(status, "❓")
