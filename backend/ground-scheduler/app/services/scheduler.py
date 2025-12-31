"""
Baseline schedule generation.

Creates an initial downlink schedule using heuristic algorithms.
This serves as the starting point for AI optimization.
"""
from datetime import datetime
from typing import List, Dict, Set, Any, Optional


class BaselineScheduler:
    """
    Generates baseline downlink schedules using greedy heuristics.
    
    The baseline scheduler considers:
    - Satellite data queues (priority-weighted volume)
    - Pass quality (maximum elevation)
    - Ground station costs
    - Conflict avoidance (no overlapping station usage)
    """
    
    def __init__(self):
        pass
    
    def generate_baseline(
        self,
        passes: List[Dict[str, Any]],
        data_queues: Dict[int, Dict[str, Any]],
        station_costs: Dict[int, float],
        prefer_high_elevation: bool = True,
        max_passes_per_satellite: Optional[int] = None
    ) -> Set[int]:
        """
        Generate a baseline schedule using a greedy algorithm.
        
        Algorithm:
        1. Score each pass based on satellite priority and pass quality
        2. Sort passes by score (descending)
        3. Greedily select passes, avoiding conflicts
        
        Args:
            passes: List of pass dictionaries with timing info
            data_queues: Satellite data queues by satellite_id
            station_costs: Cost per minute by station_id
            prefer_high_elevation: Weight higher elevation passes
            max_passes_per_satellite: Optional limit per satellite
            
        Returns:
            Set of selected pass IDs
        """
        if not passes:
            return set()
        
        # Score each pass
        scored_passes = []
        for pass_data in passes:
            score = self._calculate_pass_score(
                pass_data,
                data_queues.get(pass_data['satellite_id'], {}),
                station_costs.get(pass_data['station_id'], 1.0),
                prefer_high_elevation
            )
            scored_passes.append((score, pass_data))
        
        # Sort by score (highest first)
        scored_passes.sort(key=lambda x: x[0], reverse=True)
        
        # Greedily select passes
        selected_ids = set()
        station_timeline: Dict[int, List[tuple]] = {}  # station_id -> [(start, end), ...]
        satellite_pass_count: Dict[int, int] = {}  # satellite_id -> count
        
        for score, pass_data in scored_passes:
            pass_id = pass_data['id']
            station_id = pass_data['station_id']
            satellite_id = pass_data['satellite_id']
            aos = pass_data['aos']
            los = pass_data['los']
            
            # Check satellite limit
            if max_passes_per_satellite:
                current_count = satellite_pass_count.get(satellite_id, 0)
                if current_count >= max_passes_per_satellite:
                    continue
            
            # Check for station conflicts
            if self._has_conflict(station_timeline.get(station_id, []), aos, los):
                continue
            
            # Select this pass
            selected_ids.add(pass_id)
            
            # Update constraints
            if station_id not in station_timeline:
                station_timeline[station_id] = []
            station_timeline[station_id].append((aos, los))
            
            satellite_pass_count[satellite_id] = satellite_pass_count.get(satellite_id, 0) + 1
        
        return selected_ids
    
    def _calculate_pass_score(
        self,
        pass_data: Dict[str, Any],
        data_queue: Dict[str, Any],
        station_cost: float,
        prefer_high_elevation: bool
    ) -> float:
        """
        Calculate a score for a pass based on multiple factors.
        
        Higher score = higher priority for scheduling.
        """
        score = 0.0
        
        # Factor 1: Satellite data priority
        # Critical data is worth most, then high, medium, low
        if data_queue:
            priority_score = (
                data_queue.get('critical_volume_mb', 0) * 10 +
                data_queue.get('high_volume_mb', 0) * 5 +
                data_queue.get('medium_volume_mb', 0) * 2 +
                data_queue.get('low_volume_mb', 0) * 1
            )
            # Normalize to 0-100 range
            score += min(100, priority_score)
        else:
            # No queue data = medium priority
            score += 30
        
        # Factor 2: Pass quality (elevation)
        max_elev = pass_data.get('max_elevation_deg', 45)
        if prefer_high_elevation:
            # Higher elevation = better link quality
            elevation_score = (max_elev / 90) * 50
            score += elevation_score
        
        # Factor 3: Pass duration (longer is generally better)
        duration_seconds = pass_data.get('duration_seconds', 300)
        duration_score = min(30, (duration_seconds / 60) * 3)  # Cap at 30
        score += duration_score
        
        # Factor 4: Station cost (lower is better)
        cost_penalty = station_cost * 5
        score -= cost_penalty
        
        # Factor 5: Pass priority if set
        priority = pass_data.get('priority', 'medium')
        priority_bonus = {
            'critical': 50,
            'high': 25,
            'medium': 0,
            'low': -10
        }.get(priority, 0)
        score += priority_bonus
        
        return score
    
    def _has_conflict(
        self,
        existing_intervals: List[tuple],
        new_start: datetime,
        new_end: datetime,
        buffer_seconds: int = 60
    ) -> bool:
        """
        Check if a new pass conflicts with existing scheduled passes.
        
        A buffer is added between passes to account for antenna slewing
        and setup time.
        """
        from datetime import timedelta
        buffer = timedelta(seconds=buffer_seconds)
        
        for start, end in existing_intervals:
            # Check for overlap with buffer
            if (new_start - buffer) < end and (new_end + buffer) > start:
                return True
        
        return False
    
    def calculate_schedule_metrics(
        self,
        passes: List[Dict[str, Any]],
        selected_ids: Set[int],
        data_queues: Dict[int, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate metrics for a schedule.
        
        Returns:
            Dictionary with schedule statistics
        """
        selected_passes = [p for p in passes if p['id'] in selected_ids]
        
        total_contact_minutes = sum(
            p.get('duration_seconds', 0) / 60 for p in selected_passes
        )
        
        satellites_covered = len(set(p['satellite_id'] for p in selected_passes))
        stations_used = len(set(p['station_id'] for p in selected_passes))
        
        # Estimate data volume downloaded (simplified)
        # Assume 10 Mbps average downlink rate
        estimated_volume_mb = total_contact_minutes * 60 * 10 / 8  # MB
        
        return {
            'total_passes': len(selected_passes),
            'total_contact_minutes': total_contact_minutes,
            'satellites_covered': satellites_covered,
            'stations_used': stations_used,
            'estimated_volume_mb': estimated_volume_mb
        }
