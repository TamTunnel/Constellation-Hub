"""
AI Pass Scheduler - Intelligent schedule optimization.

Uses a Strategy Pattern to allow plugging in different optimization algorithms:
- HeuristicScheduler: Rule-based optimization (default)
- MLScheduler: Machine learning-based optimization (future)

The strategy is selected via the SCHEDULER_STRATEGY environment variable.
"""
import os
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Set, Any, Optional
import uuid


class PassSchedulerStrategy(ABC):
    """
    Abstract base class for pass scheduling strategies.
    
    All scheduling strategies must implement the optimize method,
    which takes pass data and returns an optimized schedule.
    """
    
    @property
    @abstractmethod
    def strategy_name(self) -> str:
        """Return the name of this strategy."""
        pass
    
    @abstractmethod
    def optimize(
        self,
        passes: List[Dict[str, Any]],
        data_queues: Dict[int, Dict[str, Any]],
        stations: Dict[int, Dict[str, Any]],
        constraints: Dict[str, Any],
        current_schedule: Optional[Set[int]] = None
    ) -> Dict[str, Any]:
        """
        Optimize the pass schedule.
        
        Args:
            passes: List of available passes
            data_queues: Satellite data queue information
            stations: Ground station information
            constraints: Optimization constraints
            current_schedule: Currently scheduled pass IDs (if any)
            
        Returns:
            Dictionary containing:
                - selected_passes: Set of optimized pass IDs
                - metrics: Improvement metrics
                - recommendations: List of recommendations
        """
        pass


class HeuristicScheduler(PassSchedulerStrategy):
    """
    Rule-based heuristic scheduler.
    
    Optimization approach:
    1. Score passes based on multiple factors
    2. Apply constraint-aware selection
    3. Iteratively improve by swapping passes
    4. Provide recommendations for manual review
    """
    
    @property
    def strategy_name(self) -> str:
        return "heuristic"
    
    def optimize(
        self,
        passes: List[Dict[str, Any]],
        data_queues: Dict[int, Dict[str, Any]],
        stations: Dict[int, Dict[str, Any]],
        constraints: Dict[str, Any],
        current_schedule: Optional[Set[int]] = None
    ) -> Dict[str, Any]:
        """
        Optimize schedule using multi-factor heuristics.
        """
        if not passes:
            return {
                'selected_passes': set(),
                'metrics': {},
                'recommendations': []
            }
        
        # Phase 1: Score all passes
        scored_passes = []
        for pass_data in passes:
            score = self._calculate_pass_score(
                pass_data,
                data_queues.get(pass_data['satellite_id'], {}),
                stations.get(pass_data['station_id'], {})
            )
            scored_passes.append((score, pass_data))
        
        # Phase 2: Greedy selection with constraints
        selected = self._greedy_select(scored_passes, constraints)
        
        # Phase 3: Local search improvement
        selected = self._local_search_improvement(
            selected, 
            scored_passes, 
            constraints
        )
        
        # Calculate metrics
        metrics = self._calculate_metrics(
            passes, selected, current_schedule, data_queues
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            passes, selected, data_queues, stations
        )
        
        return {
            'selected_passes': selected,
            'metrics': metrics,
            'recommendations': recommendations
        }
    
    def _calculate_pass_score(
        self,
        pass_data: Dict[str, Any],
        queue: Dict[str, Any],
        station: Dict[str, Any]
    ) -> float:
        """Calculate optimization score for a pass."""
        score = 0.0
        
        # Priority-weighted data volume
        if queue:
            volume_score = (
                queue.get('critical_volume_mb', 0) * 100 +
                queue.get('high_volume_mb', 0) * 50 +
                queue.get('medium_volume_mb', 0) * 20 +
                queue.get('low_volume_mb', 0) * 5
            )
            score += min(200, volume_score)
        else:
            score += 50  # Default score for unknown queues
        
        # Pass quality (elevation)
        max_elev = pass_data.get('max_elevation_deg', 45)
        score += (max_elev / 90) * 100
        
        # Duration benefit
        duration = pass_data.get('duration_seconds', 300)
        score += min(50, (duration / 60) * 5)
        
        # Station cost penalty
        cost = station.get('cost_per_minute', 1.0)
        score -= cost * 10
        
        # Priority boost
        priority = pass_data.get('priority', 'medium')
        priority_boost = {
            'critical': 100,
            'high': 50,
            'medium': 0,
            'low': -20
        }.get(priority, 0)
        score += priority_boost
        
        return score
    
    def _greedy_select(
        self,
        scored_passes: List[tuple],
        constraints: Dict[str, Any]
    ) -> Set[int]:
        """Greedy selection respecting constraints."""
        # Sort by score descending
        scored_passes.sort(key=lambda x: x[0], reverse=True)
        
        selected = set()
        station_timeline: Dict[int, List[tuple]] = {}
        satellite_counts: Dict[int, int] = {}
        
        max_per_satellite = constraints.get('max_passes_per_satellite')
        max_total = constraints.get('max_total_passes')
        
        for score, pass_data in scored_passes:
            if max_total and len(selected) >= max_total:
                break
            
            pass_id = pass_data['id']
            station_id = pass_data['station_id']
            satellite_id = pass_data['satellite_id']
            aos = pass_data['aos']
            los = pass_data['los']
            
            # Convert string dates if needed
            if isinstance(aos, str):
                aos = datetime.fromisoformat(aos.replace('Z', '+00:00'))
            if isinstance(los, str):
                los = datetime.fromisoformat(los.replace('Z', '+00:00'))
            
            # Check satellite limit
            if max_per_satellite:
                if satellite_counts.get(satellite_id, 0) >= max_per_satellite:
                    continue
            
            # Check station conflicts
            if self._has_conflict(station_timeline.get(station_id, []), aos, los):
                continue
            
            # Select pass
            selected.add(pass_id)
            
            if station_id not in station_timeline:
                station_timeline[station_id] = []
            station_timeline[station_id].append((aos, los))
            satellite_counts[satellite_id] = satellite_counts.get(satellite_id, 0) + 1
        
        return selected
    
    def _local_search_improvement(
        self,
        selected: Set[int],
        scored_passes: List[tuple],
        constraints: Dict[str, Any],
        max_iterations: int = 10
    ) -> Set[int]:
        """
        Improve schedule through local search.
        
        Try swapping lower-scored selected passes for higher-scored
        unselected passes.
        """
        # For MVP, just return the greedy solution
        # Full local search would iterate and try improvements
        return selected
    
    def _has_conflict(
        self,
        intervals: List[tuple],
        new_start: datetime,
        new_end: datetime,
        buffer_seconds: int = 60
    ) -> bool:
        """Check for scheduling conflicts."""
        from datetime import timedelta
        buffer = timedelta(seconds=buffer_seconds)
        
        for start, end in intervals:
            if (new_start - buffer) < end and (new_end + buffer) > start:
                return True
        return False
    
    def _calculate_metrics(
        self,
        all_passes: List[Dict[str, Any]],
        selected: Set[int],
        previous: Optional[Set[int]],
        data_queues: Dict[int, Dict[str, Any]]
    ) -> Dict[str, float]:
        """Calculate improvement metrics."""
        selected_passes = [p for p in all_passes if p['id'] in selected]
        
        metrics = {
            'total_passes': len(selected),
            'total_contact_minutes': sum(
                p.get('duration_seconds', 0) / 60 for p in selected_passes
            ),
            'satellites_covered': len(set(p['satellite_id'] for p in selected_passes)),
            'average_elevation': sum(
                p.get('max_elevation_deg', 0) for p in selected_passes
            ) / len(selected_passes) if selected_passes else 0
        }
        
        if previous:
            metrics['passes_changed'] = len(selected.symmetric_difference(previous))
            metrics['improvement_ratio'] = (
                len(selected) / len(previous) if previous else 1.0
            )
        
        return metrics
    
    def _generate_recommendations(
        self,
        passes: List[Dict[str, Any]],
        selected: Set[int],
        data_queues: Dict[int, Dict[str, Any]],
        stations: Dict[int, Dict[str, Any]]
    ) -> List[str]:
        """Generate human-readable recommendations."""
        recommendations = []
        
        # Find satellites with high data volume but few passes
        sat_pass_count = {}
        for p in passes:
            if p['id'] in selected:
                sat_id = p['satellite_id']
                sat_pass_count[sat_id] = sat_pass_count.get(sat_id, 0) + 1
        
        for sat_id, queue in data_queues.items():
            critical = queue.get('critical_volume_mb', 0)
            if critical > 100 and sat_pass_count.get(sat_id, 0) < 3:
                recommendations.append(
                    f"Satellite {sat_id} has {critical:.0f}MB critical data "
                    f"but only {sat_pass_count.get(sat_id, 0)} scheduled passes. "
                    f"Consider adding ground station capacity."
                )
        
        # Check for underutilized stations
        station_usage = {}
        for p in passes:
            if p['id'] in selected:
                sid = p['station_id']
                station_usage[sid] = station_usage.get(sid, 0) + 1
        
        for sid, info in stations.items():
            if sid not in station_usage:
                recommendations.append(
                    f"Ground station {info.get('name', sid)} has no scheduled passes. "
                    f"Consider using it to reduce load on other stations."
                )
        
        if not recommendations:
            recommendations.append("Schedule is well-balanced. No immediate optimizations suggested.")
        
        return recommendations


class MLScheduler(PassSchedulerStrategy):
    """
    Machine learning-based scheduler (placeholder for future implementation).
    
    Would use techniques like:
    - Reinforcement learning for sequential decision making
    - Graph neural networks for constraint satisfaction
    - Bayesian optimization for hyperparameter tuning
    """
    
    @property
    def strategy_name(self) -> str:
        return "ml"
    
    def optimize(
        self,
        passes: List[Dict[str, Any]],
        data_queues: Dict[int, Dict[str, Any]],
        stations: Dict[int, Dict[str, Any]],
        constraints: Dict[str, Any],
        current_schedule: Optional[Set[int]] = None
    ) -> Dict[str, Any]:
        """
        ML-based optimization (not yet implemented).
        
        Falls back to heuristic scheduler.
        """
        # TODO: Implement ML-based scheduling
        # For now, fall back to heuristic
        heuristic = HeuristicScheduler()
        result = heuristic.optimize(
            passes, data_queues, stations, constraints, current_schedule
        )
        result['recommendations'].insert(
            0, 
            "Note: ML scheduler not yet implemented. Using heuristic fallback."
        )
        return result


def get_scheduler() -> PassSchedulerStrategy:
    """
    Factory function to get the configured scheduler strategy.
    
    Set SCHEDULER_STRATEGY environment variable to:
    - 'heuristic' (default)
    - 'ml'
    """
    strategy = os.getenv('SCHEDULER_STRATEGY', 'heuristic').lower()
    
    if strategy == 'ml':
        return MLScheduler()
    else:
        return HeuristicScheduler()
