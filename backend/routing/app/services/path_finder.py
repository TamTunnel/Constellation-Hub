"""
Path finding algorithms for routing.

Implements Dijkstra's algorithm for finding optimal paths through
the satellite-ground network, with support for policy-based constraints.
"""
from typing import Dict, List, Any, Optional
import heapq

from .graph_builder import Graph
from .models import RoutingPolicy


class PathFinder:
    """
    Finds optimal paths in a routing graph using Dijkstra's algorithm.
    
    Supports policy-based constraints like:
    - Maximum latency
    - Maximum hops
    - Maximum cost
    - Preferred/avoided ground stations
    """
    
    def __init__(self, policy: Optional[Any] = None):
        """
        Initialize path finder with optional routing policy.
        
        Args:
            policy: Routing policy ORM object or dictionary
        """
        self.policy = policy
    
    def find_path(
        self,
        graph: Graph,
        origin: str,
        destination: str
    ) -> Dict[str, Any]:
        """
        Find the optimal path from origin to destination.
        
        Uses Dijkstra's algorithm with policy constraints.
        
        Args:
            graph: Routing graph
            origin: Origin node key (e.g., "satellite:1")
            destination: Destination node key
            
        Returns:
            Dictionary containing:
                - path: List of node keys from origin to destination
                - total_latency: Total path latency in ms
                - total_cost: Total path cost
                - feasible: Whether a valid path was found
                - message: Error message if not feasible
        """
        if not graph.has_node(origin):
            return self._no_path_result(origin, destination, f"Origin node {origin} not in graph")
        
        if not graph.has_node(destination):
            return self._no_path_result(origin, destination, f"Destination node {destination} not in graph")
        
        # Dijkstra's algorithm
        distances: Dict[str, float] = {node: float('infinity') for node in graph.nodes}
        distances[origin] = 0
        
        previous: Dict[str, Optional[str]] = {node: None for node in graph.nodes}
        latencies: Dict[str, float] = {node: 0 for node in graph.nodes}
        costs: Dict[str, float] = {node: 0 for node in graph.nodes}
        hop_counts: Dict[str, int] = {node: 0 for node in graph.nodes}
        
        # Priority queue: (distance, node)
        pq = [(0, origin)]
        visited = set()
        
        while pq:
            current_dist, current = heapq.heappop(pq)
            
            if current in visited:
                continue
            visited.add(current)
            
            if current == destination:
                break
            
            if current_dist > distances[current]:
                continue
            
            for neighbor, edge_data in graph.get_neighbors(current).items():
                if neighbor in visited:
                    continue
                
                # Check policy constraints
                if not self._check_constraints(
                    neighbor,
                    latencies[current] + edge_data['latency_ms'],
                    costs[current] + edge_data['cost'],
                    hop_counts[current] + 1
                ):
                    continue
                
                new_dist = distances[current] + edge_data['weight']
                
                if new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    previous[neighbor] = current
                    latencies[neighbor] = latencies[current] + edge_data['latency_ms']
                    costs[neighbor] = costs[current] + edge_data['cost']
                    hop_counts[neighbor] = hop_counts[current] + 1
                    heapq.heappush(pq, (new_dist, neighbor))
        
        # Reconstruct path
        if previous[destination] is None and destination != origin:
            return self._no_path_result(origin, destination, "No path found")
        
        path = self._reconstruct_path(previous, origin, destination)
        
        # Calculate hop-by-hop metrics
        hop_latencies = {}
        hop_costs = {}
        for i in range(1, len(path)):
            prev_node = path[i-1]
            curr_node = path[i]
            edge = graph.edges.get(prev_node, {}).get(curr_node, {})
            hop_latencies[curr_node] = edge.get('latency_ms', 0)
            hop_costs[curr_node] = edge.get('cost', 0)
        
        return {
            'path': path,
            'total_latency': latencies[destination],
            'total_cost': costs[destination],
            'total_hops': hop_counts[destination],
            'feasible': True,
            'message': None,
            'hop_latencies': hop_latencies,
            'hop_costs': hop_costs
        }
    
    def find_k_paths(
        self,
        graph: Graph,
        origin: str,
        destination: str,
        k: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Find k-best paths (Yen's algorithm simplified).
        
        Returns up to k different paths ordered by total weight.
        
        Args:
            graph: Routing graph
            origin: Origin node key
            destination: Destination node key
            k: Maximum number of paths to return
            
        Returns:
            List of path result dictionaries
        """
        # For now, just return the single best path
        # Full Yen's algorithm is more complex
        best_path = self.find_path(graph, origin, destination)
        return [best_path] if best_path['feasible'] else []
    
    def _check_constraints(
        self,
        node: str,
        total_latency: float,
        total_cost: float,
        hop_count: int
    ) -> bool:
        """
        Check if path to node satisfies policy constraints.
        
        Returns False if any constraint is violated.
        """
        if not self.policy:
            return True
        
        # Get policy constraints (handle both ORM and dict)
        if hasattr(self.policy, 'max_latency_ms'):
            max_latency = self.policy.max_latency_ms
            max_hops = self.policy.max_hops
            max_cost = self.policy.max_cost
            avoided = self.policy.avoided_ground_stations or []
        else:
            max_latency = self.policy.get('max_latency_ms')
            max_hops = self.policy.get('max_hops')
            max_cost = self.policy.get('max_cost')
            avoided = self.policy.get('avoided_ground_stations', [])
        
        # Check latency constraint
        if max_latency is not None and total_latency > max_latency:
            return False
        
        # Check hop constraint
        if max_hops is not None and hop_count > max_hops:
            return False
        
        # Check cost constraint
        if max_cost is not None and total_cost > max_cost:
            return False
        
        # Check avoided ground stations
        if avoided and node.startswith('ground_station:'):
            station_id = int(node.split(':')[1])
            if station_id in avoided:
                return False
        
        return True
    
    def _reconstruct_path(
        self,
        previous: Dict[str, Optional[str]],
        origin: str,
        destination: str
    ) -> List[str]:
        """Reconstruct path from previous pointers."""
        path = []
        current = destination
        
        while current is not None:
            path.append(current)
            current = previous[current]
        
        path.reverse()
        return path
    
    def _no_path_result(
        self,
        origin: str,
        destination: str,
        message: str
    ) -> Dict[str, Any]:
        """Return a result indicating no path was found."""
        return {
            'path': [],
            'total_latency': 0,
            'total_cost': 0,
            'total_hops': 0,
            'feasible': False,
            'message': message,
            'hop_latencies': {},
            'hop_costs': {}
        }
