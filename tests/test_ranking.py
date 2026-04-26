"""
Test suite for ranking formulas and leaderboard logic.
Tests all formulas from rankinginstruction.md
"""

import pytest
from datetime import datetime
from unittest.mock import Mock
from src.multi_flat_ranking import MultiFlatRanking, RankingRecord
from src.ranking import Ranking


class TestEfficiencyScore:
    """Test efficiency score calculation formula."""

    def test_efficiency_score_zero_usage(self):
        """Usage 0ml with 3000ml threshold should score 100."""
        ratio = 0.0
        score = MultiFlatRanking.calculate_efficiency_score(ratio)
        assert score == 100.0

    def test_efficiency_score_half_threshold(self):
        """Usage 1500ml (50%) with 3000ml threshold should score 50."""
        ratio = 0.5
        score = MultiFlatRanking.calculate_efficiency_score(ratio)
        assert score == 50.0

    def test_efficiency_score_at_threshold(self):
        """Usage exactly at threshold (1.0 ratio) should score 0."""
        ratio = 1.0
        score = MultiFlatRanking.calculate_efficiency_score(ratio)
        assert score == 0.0

    def test_efficiency_score_above_threshold_10_percent(self):
        """Usage 10% over threshold (1.10 ratio) should score -10."""
        ratio = 1.10
        score = MultiFlatRanking.calculate_efficiency_score(ratio)
        assert score == -10.0

    def test_efficiency_score_above_threshold_20_percent(self):
        """Usage 20% over threshold (1.20 ratio) should score -20."""
        ratio = 1.20
        score = MultiFlatRanking.calculate_efficiency_score(ratio)
        assert score == -20.0

    def test_efficiency_score_rounding(self):
        """Score should round to 2 decimal places."""
        ratio = 0.333333
        score = MultiFlatRanking.calculate_efficiency_score(ratio)
        assert score == pytest.approx(66.67, abs=0.01)

    def test_efficiency_score_examples_from_instruction(self):
        """Test all examples from rankinginstruction.md section."""
        examples = [
            (0.00, 100.0),    # 0 ml
            (0.50, 50.0),     # 1500 ml (50%)
            (0.70, 30.0),     # 2100 ml
            (1.00, 0.0),      # 3000 ml
            (1.10, -10.0),    # 3300 ml
            (1.20, -20.0),    # 3600 ml
        ]
        for ratio, expected_score in examples:
            score = MultiFlatRanking.calculate_efficiency_score(ratio)
            assert score == expected_score, f"Failed for ratio {ratio}"


class TestDailyPoints:
    """Test daily points calculation formula."""

    def test_points_efficient_rank_1(self):
        """Efficient status, rank 1 should get 5000 points."""
        points = MultiFlatRanking.calculate_daily_points(1, 5, "Efficient")
        assert points == 5000

    def test_points_efficient_rank_2(self):
        """Efficient status, rank 2 should get 4000 points."""
        points = MultiFlatRanking.calculate_daily_points(2, 5, "Efficient")
        assert points == 4000

    def test_points_efficient_rank_3(self):
        """Efficient status, rank 3 should get 3000 points."""
        points = MultiFlatRanking.calculate_daily_points(3, 5, "Efficient")
        assert points == 3000

    def test_points_efficient_rank_4_plus(self):
        """Efficient status, rank 4+ should get 2000 points."""
        points = MultiFlatRanking.calculate_daily_points(4, 5, "Efficient")
        assert points == 2000
        points = MultiFlatRanking.calculate_daily_points(5, 5, "Efficient")
        assert points == 2000

    def test_points_normal_above_midpoint(self):
        """Normal status, rank above midpoint should get 0 points."""
        # 5 flats: midpoint = 2, so rank 3+ gets 0
        points = MultiFlatRanking.calculate_daily_points(3, 5, "Normal")
        assert points == 0
        points = MultiFlatRanking.calculate_daily_points(5, 5, "Normal")
        assert points == 0

    def test_points_normal_at_or_below_midpoint(self):
        """Normal status, rank at/below midpoint should get 1000 points."""
        # 5 flats: midpoint = 2
        points = MultiFlatRanking.calculate_daily_points(1, 5, "Normal")
        assert points == 1000
        points = MultiFlatRanking.calculate_daily_points(2, 5, "Normal")
        assert points == 1000

    def test_points_normal_with_even_flats(self):
        """Normal status with even flat count - midpoint should split correctly."""
        # 20 flats: midpoint = 10, ranks 1-10 get 1000, 11-20 get 0
        points = MultiFlatRanking.calculate_daily_points(10, 20, "Normal")
        assert points == 1000
        points = MultiFlatRanking.calculate_daily_points(11, 20, "Normal")
        assert points == 0

    def test_points_normal_with_one_flat(self):
        """Normal status with single flat (edge case)."""
        points = MultiFlatRanking.calculate_daily_points(1, 1, "Normal")
        assert points == 1000

    def test_points_high_usage(self):
        """High Usage status should always get -1000 points."""
        points = MultiFlatRanking.calculate_daily_points(1, 5, "High Usage")
        assert points == -1000
        points = MultiFlatRanking.calculate_daily_points(5, 5, "High Usage")
        assert points == -1000

    def test_points_penalty_zone(self):
        """Penalty Zone status should always get -2500 points."""
        points = MultiFlatRanking.calculate_daily_points(1, 5, "Penalty Zone")
        assert points == -2500
        points = MultiFlatRanking.calculate_daily_points(5, 5, "Penalty Zone")
        assert points == -2500

    def test_points_unknown_status(self):
        """Unknown status should return 0 points."""
        points = MultiFlatRanking.calculate_daily_points(1, 5, "Unknown Status")
        assert points == 0


class TestRewardOrPenalty:
    """Test reward/penalty classification."""

    def test_reward_classification(self):
        """Positive points should be classified as 'Reward'."""
        label = MultiFlatRanking.classify_reward_or_penalty(5000)
        assert label == "Reward"
        label = MultiFlatRanking.classify_reward_or_penalty(1)
        assert label == "Reward"

    def test_penalty_classification(self):
        """Negative points should be classified as 'Penalty'."""
        label = MultiFlatRanking.classify_reward_or_penalty(-1000)
        assert label == "Penalty"
        label = MultiFlatRanking.classify_reward_or_penalty(-1)
        assert label == "Penalty"

    def test_neutral_classification(self):
        """Zero points should be classified as 'Neutral'."""
        label = MultiFlatRanking.classify_reward_or_penalty(0)
        assert label == "Neutral"


class TestMultiFlatRanking:
    """Test multi-flat ranking and leaderboard generation."""

    def _create_mock_report(self, flat_id, total_usage, avg_flow=100, peak_flow=120):
        """Helper to create mock report object."""
        report = Mock()
        report.total_usage_ml = total_usage
        report.average_flow_ml_min = avg_flow
        report.peak_flow_rate_ml_min = peak_flow
        report.peak_flow_ml_min = peak_flow  # Alternative name
        return report

    def test_rank_single_flat(self):
        """Test ranking with single flat."""
        reports = {
            "A-101": self._create_mock_report("A-101", 2000)
        }
        threshold = 3000

        records = MultiFlatRanking.rank_flats(reports, threshold, simulated_day=1)

        assert len(records) == 1
        assert records[0].unique_id == "A-101"
        assert records[0].rank == 1
        # 2000/3000 = 0.667 which is ≤ 0.70, so Efficient
        assert records[0].status == "Efficient"
        assert records[0].efficiency_score == pytest.approx(33.33, abs=0.01)
        assert records[0].usage_ratio == pytest.approx(0.67, abs=0.01)

    def test_rank_multiple_flats_different_usage(self):
        """Test ranking multiple flats with different usage levels."""
        reports = {
            "A-101": self._create_mock_report("A-101", 1000),  # Efficient
            "A-102": self._create_mock_report("A-102", 2500),  # Normal
            "A-103": self._create_mock_report("A-103", 3500),  # High Usage
        }
        threshold = 3000

        records = MultiFlatRanking.rank_flats(reports, threshold, simulated_day=1)

        assert len(records) == 3
        # Verify sorting: higher efficiency_score first
        assert records[0].unique_id == "A-101"  # Best: 1000ml, score 66.67
        assert records[0].rank == 1
        assert records[1].unique_id == "A-102"  # Middle: 2500ml, score 16.67
        assert records[1].rank == 2
        assert records[2].unique_id == "A-103"  # Worst: 3500ml, score -16.67
        assert records[2].rank == 3

    def test_rank_tie_breaking_by_usage(self):
        """Test that tied efficiency scores are broken by total usage."""
        reports = {
            "A-101": self._create_mock_report("A-101", 1000, avg_flow=100, peak_flow=150),
            "A-102": self._create_mock_report("A-102", 1000, avg_flow=100, peak_flow=200),
        }
        threshold = 3000

        records = MultiFlatRanking.rank_flats(reports, threshold, simulated_day=1)

        assert len(records) == 2
        # Same usage, so next tiebreaker is peak_flow
        assert records[0].unique_id == "A-101"
        assert records[0].rank == 1
        assert records[1].unique_id == "A-102"
        assert records[1].rank == 2

    def test_rank_tie_breaking_by_alphabetical(self):
        """Test that complete ties are broken alphabetically."""
        reports = {
            "A-102": self._create_mock_report("A-102", 1000, avg_flow=100, peak_flow=150),
            "A-101": self._create_mock_report("A-101", 1000, avg_flow=100, peak_flow=150),
        }
        threshold = 3000

        records = MultiFlatRanking.rank_flats(reports, threshold, simulated_day=1)

        assert len(records) == 2
        assert records[0].unique_id == "A-101"  # Alphabetically first
        assert records[0].rank == 1
        assert records[1].unique_id == "A-102"
        assert records[1].rank == 2

    def test_points_assigned_correctly(self):
        """Test that points are calculated correctly in leaderboard."""
        reports = {
            "A-101": self._create_mock_report("A-101", 1500),  # Efficient
            "A-102": self._create_mock_report("A-102", 2500),  # Normal, rank 2
            "A-103": self._create_mock_report("A-103", 3500),  # High Usage
        }
        threshold = 3000

        records = MultiFlatRanking.rank_flats(reports, threshold, simulated_day=1)

        # A-101: Efficient, rank 1 -> 5000
        assert records[0].daily_points == 5000
        assert records[0].reward_or_penalty == "Reward"

        # A-102: Normal, rank 2, midpoint=1 (3//2=1), rank 2 > 1 -> 0 points
        assert records[1].daily_points == 0
        assert records[1].reward_or_penalty == "Neutral"

        # A-103: High Usage -> -1000
        assert records[2].daily_points == -1000
        assert records[2].reward_or_penalty == "Penalty"

    def test_weekly_points_accumulation(self):
        """Test weekly points accumulation across days."""
        reports = {
            "A-101": self._create_mock_report("A-101", 1500),  # Efficient
            "A-102": self._create_mock_report("A-102", 2500),  # Normal
        }
        threshold = 3000

        # Day 1
        records_day1 = MultiFlatRanking.rank_flats(
            reports, threshold, simulated_day=1, finalize_points=True
        )
        weekly_points = {}
        for record in records_day1:
            weekly_points[record.unique_id] = record.weekly_points

        # Day 2
        records_day2 = MultiFlatRanking.rank_flats(
            reports, threshold, simulated_day=2,
            weekly_points=weekly_points, finalize_points=True
        )

        # A-101 should have accumulated 5000 + 5000 = 10000
        assert any(r.unique_id == "A-101" and r.weekly_points == 10000 for r in records_day2)

    def test_empty_reports(self):
        """Test with empty reports dict."""
        records = MultiFlatRanking.rank_flats({}, 3000, simulated_day=1)
        assert records == []

    def test_usage_ratio_calculation(self):
        """Test that usage_ratio is calculated correctly."""
        reports = {
            "A-101": self._create_mock_report("A-101", 1500),  # 50%
            "A-102": self._create_mock_report("A-102", 3000),  # 100%
            "A-103": self._create_mock_report("A-103", 3600),  # 120%
        }
        threshold = 3000

        records = MultiFlatRanking.rank_flats(reports, threshold, simulated_day=1)

        assert records[0].usage_ratio == 0.50
        assert records[1].usage_ratio == 1.0
        assert records[2].usage_ratio == 1.2

    def test_status_classification_in_ranking(self):
        """Test that status is correctly classified in ranking records."""
        reports = {
            "A-101": self._create_mock_report("A-101", 1500),  # 50%: Efficient
            "A-102": self._create_mock_report("A-102", 2100),  # 70%: Efficient
            "A-103": self._create_mock_report("A-103", 2500),  # 83%: Normal
            "A-104": self._create_mock_report("A-104", 3300),  # 110%: High Usage
            "A-105": self._create_mock_report("A-105", 3700),  # 123%: Penalty Zone
        }
        threshold = 3000

        records = MultiFlatRanking.rank_flats(reports, threshold, simulated_day=1)

        status_map = {r.unique_id: r.status for r in records}
        assert status_map["A-101"] == "Efficient"
        assert status_map["A-102"] == "Efficient"
        assert status_map["A-103"] == "Normal"
        assert status_map["A-104"] == "High Usage"
        assert status_map["A-105"] == "Penalty Zone"


class TestRankingRecord:
    """Test RankingRecord data structure."""

    def test_ranking_record_to_dict(self):
        """Test conversion to dictionary."""
        record = RankingRecord(
            simulated_day=1,
            unique_id="A-101",
            total_usage_ml=1500.5,
            threshold_ml=3000.0,
            usage_ratio=0.50,
            average_flow_rate_ml_min=100.0,
            peak_flow_rate_ml_min=150.0,
            efficiency_score=50.0,
            status="Normal",
            rank=1,
            daily_points=1000,
            reward_or_penalty="Reward",
            weekly_points=1000,
        )

        d = record.to_dict()

        assert d["unique_id"] == "A-101"
        assert d["total_usage_ml"] == 1500.5
        assert d["rank"] == 1
        assert d["daily_points"] == 1000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
