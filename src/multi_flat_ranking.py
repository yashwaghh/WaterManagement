"""
Multi-flat ranking and leaderboard module.
Implements complete ranking, points, and leaderboard logic per rankinginstruction.md
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from src.ranking import Ranking


@dataclass
class RankingRecord:
    """Complete ranking record for a single flat per the instruction spec."""
    simulated_day: int
    unique_id: str
    total_usage_ml: float
    threshold_ml: float
    usage_ratio: float
    average_flow_rate_ml_min: float
    peak_flow_rate_ml_min: float
    efficiency_score: float
    status: str
    rank: int
    daily_points: int
    reward_or_penalty: str
    weekly_points: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class MultiFlatRanking:
    """Ranking system for multiple flats with leaderboard, points, and weekly tracking."""

    @staticmethod
    def calculate_efficiency_score(usage_ratio: float) -> float:
        """
        Calculate efficiency score per instruction formula.

        Args:
            usage_ratio: total_usage_ml / threshold_ml

        Returns:
            Score rounded to 2 decimals:
            - If usage_ratio <= 1.0: score = 100 - (usage_ratio * 100)
            - If usage_ratio > 1.0: score = -((usage_ratio - 1) * 100)
        """
        if usage_ratio <= 0:
            return 100.0

        if usage_ratio <= 1.0:
            score = 100 - (usage_ratio * 100)
        else:
            score = -((usage_ratio - 1) * 100)

        return round(score, 2)

    @staticmethod
    def calculate_daily_points(rank: int, total_flats: int, status: str) -> int:
        """
        Calculate daily points per instruction formula.

        Args:
            rank: Current rank (1-based, 1 is best)
            total_flats: Total number of flats in leaderboard
            status: Usage status from classify_usage()

        Returns:
            Daily points earned/deducted
        """
        if status == "Efficient":
            if rank == 1:
                return 5000
            elif rank == 2:
                return 4000
            elif rank == 3:
                return 3000
            else:
                return 2000

        elif status == "Normal":
            midpoint = max(1, total_flats // 2)
            if rank <= midpoint:
                return 1000
            else:
                return 0

        elif status == "High Usage":
            return -1000

        elif status == "Penalty Zone":
            return -2500

        return 0

    @staticmethod
    def classify_reward_or_penalty(daily_points: int) -> str:
        """
        Classify reward/penalty status based on daily points.

        Args:
            daily_points: Points from calculate_daily_points()

        Returns:
            "Reward", "Neutral", or "Penalty"
        """
        if daily_points > 0:
            return "Reward"
        elif daily_points < 0:
            return "Penalty"
        else:
            return "Neutral"

    @staticmethod
    def rank_flats(
        daily_reports: Dict[str, Any],
        threshold_ml: float,
        simulated_day: int = 1,
        weekly_points: Optional[Dict[str, int]] = None,
        finalize_points: bool = False,
    ) -> List[RankingRecord]:
        """
        Rank multiple flats and generate leaderboard.

        Args:
            daily_reports: Dict keyed by flat_id with DailyReport objects
                          (must have: total_usage_ml, average_flow_rate_ml_min, peak_flow_rate_ml_min)
            threshold_ml: Daily usage threshold
            simulated_day: Current simulated day number
            weekly_points: Optional dict tracking cumulative weekly points by flat_id
            finalize_points: If True, use final formulas; if False, projections

        Returns:
            List of RankingRecord objects sorted by rank (best first)
        """
        if not daily_reports:
            return []

        if weekly_points is None:
            weekly_points = {}

        # Step 1: Calculate metrics for each flat
        flat_metrics = []
        for flat_id, report in daily_reports.items():
            total_usage = getattr(report, 'total_usage_ml', 0)
            avg_flow = getattr(report, 'average_flow_ml_min', 0)
            peak_flow = getattr(report, 'peak_flow_ml_min', 0)

            usage_ratio = total_usage / threshold_ml if threshold_ml > 0 else 0
            efficiency_score = MultiFlatRanking.calculate_efficiency_score(usage_ratio)
            status = Ranking.classify_usage(total_usage, threshold_ml)

            flat_metrics.append({
                'unique_id': flat_id,
                'total_usage_ml': total_usage,
                'threshold_ml': threshold_ml,
                'usage_ratio': round(usage_ratio, 2),
                'average_flow_rate_ml_min': avg_flow,
                'peak_flow_rate_ml_min': peak_flow,
                'efficiency_score': efficiency_score,
                'status': status,
                'weekly_points_current': weekly_points.get(flat_id, 0),
            })

        # Step 2: Sort by ranking criteria (tier 1-4)
        # Primary: efficiency_score (higher better)
        # Secondary: total_usage_ml (lower better)
        # Tertiary: peak_flow_rate_ml_min (lower better)
        # Quaternary: unique_id (alphabetical for stability)
        sorted_flats = sorted(
            flat_metrics,
            key=lambda x: (
                -x['efficiency_score'],  # Higher score first (negated for descending)
                x['total_usage_ml'],  # Lower usage first
                x['peak_flow_rate_ml_min'],  # Lower peak flow first
                x['unique_id'],  # Alphabetical last
            ),
        )

        # Step 3: Assign ranks and calculate points
        total_flats = len(sorted_flats)
        ranking_records = []

        for rank_idx, flat_data in enumerate(sorted_flats, start=1):
            daily_points = MultiFlatRanking.calculate_daily_points(
                rank_idx, total_flats, flat_data['status']
            )

            reward_or_penalty = MultiFlatRanking.classify_reward_or_penalty(daily_points)

            # Weekly points: accumulate if finalizing
            weekly_total = flat_data['weekly_points_current']
            if finalize_points and daily_points != 0:
                weekly_total += daily_points

            record = RankingRecord(
                simulated_day=simulated_day,
                unique_id=flat_data['unique_id'],
                total_usage_ml=flat_data['total_usage_ml'],
                threshold_ml=flat_data['threshold_ml'],
                usage_ratio=flat_data['usage_ratio'],
                average_flow_rate_ml_min=flat_data['average_flow_rate_ml_min'],
                peak_flow_rate_ml_min=flat_data['peak_flow_rate_ml_min'],
                efficiency_score=flat_data['efficiency_score'],
                status=flat_data['status'],
                rank=rank_idx,
                daily_points=daily_points,
                reward_or_penalty=reward_or_penalty,
                weekly_points=weekly_total,
            )

            ranking_records.append(record)

        return ranking_records

    @staticmethod
    def rank_flats_per_threshold(
        daily_reports: Dict[str, Any],
        flat_thresholds: Dict[str, float],
        simulated_day: int = 1,
        weekly_points: Optional[Dict[str, int]] = None,
        finalize_points: bool = False,
    ) -> List[RankingRecord]:
        """Rank flats using per-flat thresholds (based on family size).

        Like rank_flats() but each flat has its own threshold_ml value
        calculated from family_size × PER_PERSON_ML.
        """
        if not daily_reports:
            return []

        if weekly_points is None:
            weekly_points = {}

        flat_metrics = []
        for flat_id, report in daily_reports.items():
            total_usage = getattr(report, 'total_usage_ml', 0)
            avg_flow = getattr(report, 'average_flow_ml_min', 0)
            peak_flow = getattr(report, 'peak_flow_ml_min', 0)
            threshold_ml = flat_thresholds.get(flat_id, 2000)

            usage_ratio = total_usage / threshold_ml if threshold_ml > 0 else 0
            efficiency_score = MultiFlatRanking.calculate_efficiency_score(usage_ratio)
            status = Ranking.classify_usage(total_usage, threshold_ml)

            flat_metrics.append({
                'unique_id': flat_id,
                'total_usage_ml': total_usage,
                'threshold_ml': threshold_ml,
                'usage_ratio': round(usage_ratio, 2),
                'average_flow_rate_ml_min': avg_flow,
                'peak_flow_rate_ml_min': peak_flow,
                'efficiency_score': efficiency_score,
                'status': status,
                'weekly_points_current': weekly_points.get(flat_id, 0),
            })

        sorted_flats = sorted(
            flat_metrics,
            key=lambda x: (
                -x['efficiency_score'],
                x['total_usage_ml'],
                x['peak_flow_rate_ml_min'],
                x['unique_id'],
            ),
        )

        total_flats = len(sorted_flats)
        ranking_records = []

        for rank_idx, flat_data in enumerate(sorted_flats, start=1):
            daily_points = MultiFlatRanking.calculate_daily_points(
                rank_idx, total_flats, flat_data['status']
            )
            reward_or_penalty = MultiFlatRanking.classify_reward_or_penalty(daily_points)

            weekly_total = flat_data['weekly_points_current']
            if finalize_points and daily_points != 0:
                weekly_total += daily_points

            record = RankingRecord(
                simulated_day=simulated_day,
                unique_id=flat_data['unique_id'],
                total_usage_ml=flat_data['total_usage_ml'],
                threshold_ml=flat_data['threshold_ml'],
                usage_ratio=flat_data['usage_ratio'],
                average_flow_rate_ml_min=flat_data['average_flow_rate_ml_min'],
                peak_flow_rate_ml_min=flat_data['peak_flow_rate_ml_min'],
                efficiency_score=flat_data['efficiency_score'],
                status=flat_data['status'],
                rank=rank_idx,
                daily_points=daily_points,
                reward_or_penalty=reward_or_penalty,
                weekly_points=weekly_total,
            )
            ranking_records.append(record)

        return ranking_records

    @staticmethod
    def update_weekly_points(
        weekly_points: Dict[str, int],
        ranking_records: List[RankingRecord],
    ) -> Dict[str, int]:
        """
        Update weekly points accumulation from final daily rankings.

        Args:
            weekly_points: Current weekly points dict
            ranking_records: Finalized ranking records from rank_flats()

        Returns:
            Updated weekly_points dict
        """
        updated = weekly_points.copy() if weekly_points else {}

        for record in ranking_records:
            if record.unique_id not in updated:
                updated[record.unique_id] = 0

            updated[record.unique_id] += record.daily_points

        return updated

    @staticmethod
    def get_leaderboard_dataframe(ranking_records: List[RankingRecord]):
        """
        Convert ranking records to pandas DataFrame for display.

        Args:
            ranking_records: List of RankingRecord objects

        Returns:
            pandas.DataFrame with leaderboard data
        """
        try:
            import pandas as pd
            data = [r.to_dict() for r in ranking_records]
            df = pd.DataFrame(data)
            # Reorder columns for readability
            column_order = [
                'rank', 'unique_id', 'status', 'total_usage_ml', 'usage_ratio',
                'efficiency_score', 'average_flow_rate_ml_min', 'peak_flow_rate_ml_min',
                'daily_points', 'reward_or_penalty', 'weekly_points',
            ]
            # Only include columns that exist
            column_order = [c for c in column_order if c in df.columns]
            return df[column_order]
        except ImportError:
            return None
