"""
Unit tests for Pass Scheduler.

Tests AI-based schedule optimization.
"""
import pytest
from datetime import datetime, timezone, timedelta
from app.pass_scheduler import (
    PassScheduler,
    HeuristicStrategy,
    OptimizationResult
)


class TestPassScheduler:
    """Test cases for Pass Scheduler."""
    
    def setup_method(self):
        self.scheduler = PassScheduler(strategy="heuristic")
    
    def test_optimize_returns_result(self):
        """Test that optimize returns an OptimizationResult."""
        passes = self._create_sample_passes()
        data_queues = self._create_sample_data_queues()
        stations = self._create_sample_stations()
        
        result = self.scheduler.optimize(
            passes=passes,
            data_queues=data_queues,
            stations=stations
        )
        
        assert isinstance(result, OptimizationResult)
    
    def test_result_has_required_fields(self):
        """Test that result contains all required fields."""
        passes = self._create_sample_passes()
        data_queues = self._create_sample_data_queues()
        stations = self._create_sample_stations()
        
        result = self.scheduler.optimize(
            passes=passes,
            data_queues=data_queues,
            stations=stations
        )
        
        assert hasattr(result, 'scheduled_passes')
        assert hasattr(result, 'score')
        assert hasattr(result, 'metrics')
    
    def test_empty_input_handling(self):
        """Test handling of empty input."""
        result = self.scheduler.optimize(
            passes=[],
            data_queues=[],
            stations=[]
        )
        
        assert len(result.scheduled_passes) == 0
    
    def test_score_is_positive(self):
        """Test that optimization score is non-negative."""
        passes = self._create_sample_passes()
        data_queues = self._create_sample_data_queues()
        stations = self._create_sample_stations()
        
        result = self.scheduler.optimize(
            passes=passes,
            data_queues=data_queues,
            stations=stations
        )
        
        assert result.score >= 0
    
    # Helper methods
    def _create_sample_passes(self):
        base = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        return [
            {
                "id": 1, "satellite_id": 1, "station_id": 1,
                "aos": base.isoformat(),
                "los": (base + timedelta(minutes=10)).isoformat(),
                "max_elevation": 75.0
            },
            {
                "id": 2, "satellite_id": 1, "station_id": 2,
                "aos": (base + timedelta(hours=1)).isoformat(),
                "los": (base + timedelta(hours=1, minutes=15)).isoformat(),
                "max_elevation": 60.0
            }
        ]
    
    def _create_sample_data_queues(self):
        return [
            {"satellite_id": 1, "data_volume_mb": 500, "priority": 1}
        ]
    
    def _create_sample_stations(self):
        return [
            {"id": 1, "name": "GS-Alpha", "cost_per_minute": 1.0},
            {"id": 2, "name": "GS-Beta", "cost_per_minute": 1.5}
        ]


class TestHeuristicStrategy:
    """Test cases for heuristic optimization strategy."""
    
    def setup_method(self):
        self.strategy = HeuristicStrategy()
    
    def test_scores_high_elevation_higher(self):
        """Test that high elevation passes are scored higher."""
        pass_high = {
            "max_elevation": 85.0,
            "duration_seconds": 600,
            "priority": 1
        }
        pass_low = {
            "max_elevation": 15.0,
            "duration_seconds": 600,
            "priority": 1
        }
        
        score_high = self.strategy.score_pass(pass_high)
        score_low = self.strategy.score_pass(pass_low)
        
        assert score_high > score_low
    
    def test_scores_longer_duration_higher(self):
        """Test that longer passes are scored higher."""
        pass_long = {
            "max_elevation": 45.0,
            "duration_seconds": 900,
            "priority": 1
        }
        pass_short = {
            "max_elevation": 45.0,
            "duration_seconds": 300,
            "priority": 1
        }
        
        score_long = self.strategy.score_pass(pass_long)
        score_short = self.strategy.score_pass(pass_short)
        
        assert score_long > score_short
    
    def test_scores_high_priority_higher(self):
        """Test that high priority passes are scored higher."""
        pass_high_pri = {
            "max_elevation": 45.0,
            "duration_seconds": 600,
            "priority": 5
        }
        pass_low_pri = {
            "max_elevation": 45.0,
            "duration_seconds": 600,
            "priority": 1
        }
        
        score_high = self.strategy.score_pass(pass_high_pri)
        score_low = self.strategy.score_pass(pass_low_pri)
        
        assert score_high > score_low


class TestStrategySelection:
    """Test cases for strategy selection."""
    
    def test_select_heuristic_strategy(self):
        """Test selecting heuristic strategy."""
        scheduler = PassScheduler(strategy="heuristic")
        
        assert scheduler.strategy_name == "heuristic"
    
    def test_default_strategy(self):
        """Test default strategy is heuristic."""
        scheduler = PassScheduler()
        
        assert scheduler.strategy_name == "heuristic"
    
    def test_invalid_strategy_raises(self):
        """Test that invalid strategy raises error."""
        with pytest.raises(ValueError):
            PassScheduler(strategy="invalid_strategy")


class TestOptimizationConstraints:
    """Test cases for optimization constraints."""
    
    def setup_method(self):
        self.scheduler = PassScheduler(strategy="heuristic")
    
    def test_max_passes_per_satellite(self):
        """Test maximum passes per satellite constraint."""
        base = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        
        # Create many passes for same satellite
        passes = [
            {
                "id": i, "satellite_id": 1, "station_id": 1,
                "aos": (base + timedelta(hours=i)).isoformat(),
                "los": (base + timedelta(hours=i, minutes=10)).isoformat(),
                "max_elevation": 45.0
            }
            for i in range(20)
        ]
        
        result = self.scheduler.optimize(
            passes=passes,
            data_queues=[],
            stations=[{"id": 1, "name": "GS-Alpha", "cost_per_minute": 1.0}],
            constraints={"max_passes_per_satellite": 5}
        )
        
        # Should limit to 5 passes for satellite-1
        sat1_passes = [p for p in result.scheduled_passes if p.get("satellite_id") == 1]
        assert len(sat1_passes) <= 5
