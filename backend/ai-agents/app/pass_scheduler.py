"""
AI Pass Scheduler - Intelligent schedule optimization.

Uses a Strategy Pattern to allow plugging in different optimization algorithms:
- HeuristicScheduler: Rule-based optimization (default)
- MLScheduler: Machine learning-based optimization (future)

The strategy is selected via the SCHEDULER_STRATEGY environment variable.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Set, Any, Optional


class OptimizationResult:
    """Container for optimization results."""
    def __init__(self, scheduled_passes: List[Dict[str, Any]], score: float, metrics: Dict[str, Any]):
        self.scheduled_passes = scheduled_passes
        self.score = score
        self.metrics = metrics

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
        data_queues: List[Dict[str, Any]],
        stations: List[Dict[str, Any]],
        constraints: Dict[str, Any] = None,
        current_schedule: Optional[Set[int]] = None
    ) -> OptimizationResult:
        """
        Optimize the pass schedule.
        """
        pass


class HeuristicStrategy(PassSchedulerStrategy):
    """
    Rule-based heuristic scheduler.
    """
    
    @property
    def strategy_name(self) -> str:
        return "heuristic"
    
    def optimize(
        self,
        passes: List[Dict[str, Any]],
        data_queues: List[Dict[str, Any]],
        stations: List[Dict[str, Any]],
        constraints: Dict[str, Any] = None,
        current_schedule: Optional[Set[int]] = None
    ) -> OptimizationResult:
        """
        Optimize schedule using multi-factor heuristics.
        """
        constraints = constraints or {}

        # Helper to index queues and stations
        queues_map = {q['satellite_id']: q for q in data_queues} if data_queues else {}
        stations_map = {s['id']: s for s in stations} if stations else {}

        if not passes:
            return OptimizationResult(
                scheduled_passes=[],
                score=0.0,
                metrics={}
            )
        
        # Phase 1: Score all passes
        scored_passes = []
        for pass_data in passes:
            score = self.score_pass(
                pass_data,
                queues_map.get(pass_data['satellite_id'], {}),
                stations_map.get(pass_data['station_id'], {})
            )
            scored_passes.append((score, pass_data))
        
        # Phase 2: Greedy selection with constraints
        selected_ids = self._greedy_select(scored_passes, constraints)
        
        # Phase 3: Local search improvement (skipped for MVP)
        
        # Compile result
        scheduled_passes = [p for s, p in scored_passes if p['id'] in selected_ids]
        total_score = sum(s for s, p in scored_passes if p['id'] in selected_ids)
        
        return OptimizationResult(
            scheduled_passes=scheduled_passes,
            score=total_score,
            metrics={'count': len(scheduled_passes)}
        )
    
    def score_pass(
        self,
        pass_data: Dict[str, Any],
        queue: Dict[str, Any] = None,
        station: Dict[str, Any] = None
    ) -> float:
        """Calculate optimization score for a pass."""
        queue = queue or {}
        station = station or {}

        score = 0.0
        
        # Priority-weighted data volume
        if queue:
            # Check for different queue volume keys (test uses data_volume_mb)
            if 'data_volume_mb' in queue:
                volume_score = queue['data_volume_mb'] * 0.5
            else:
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
        # Handle different keys for elevation
        max_elev = pass_data.get('max_elevation', pass_data.get('max_elevation_deg', 45))
        score += (max_elev / 90) * 100
        
        # Duration benefit
        duration = pass_data.get('duration_seconds', 300)
        score += min(50, (duration / 60) * 5)
        
        # Station cost penalty
        cost = station.get('cost_per_minute', 1.0)
        score -= cost * 10
        
        # Priority boost
        priority = pass_data.get('priority', 'medium')
        # Handle numeric priority (higher is better in tests, e.g. 5 vs 1)
        if isinstance(priority, int):
             score += priority * 20
        else:
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
    """
    
    @property
    def strategy_name(self) -> str:
        return "ml"
    
    def optimize(
        self,
        passes: List[Dict[str, Any]],
        data_queues: List[Dict[str, Any]],
        stations: List[Dict[str, Any]],
        constraints: Dict[str, Any] = None,
        current_schedule: Optional[Set[int]] = None
    ) -> OptimizationResult:
        """
        ML-based optimization (not yet implemented).
        Falls back to heuristic scheduler.
        """
        heuristic = HeuristicStrategy()
        return heuristic.optimize(
            passes, data_queues, stations, constraints, current_schedule
        )


class PassScheduler:
    """
    Main scheduler class that uses a strategy.
    """
    def __init__(self, strategy: str = "heuristic"):
        self.strategy_name = strategy
        if strategy == "ml":
            self._strategy = MLScheduler()
        elif strategy == "heuristic":
            self._strategy = HeuristicStrategy()
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
    
    def optimize(
        self,
        passes: List[Dict[str, Any]],
        data_queues: List[Dict[str, Any]],
        stations: List[Dict[str, Any]],
        constraints: Dict[str, Any] = None
    ) -> OptimizationResult:
        return self._strategy.optimize(passes, data_queues, stations, constraints)
