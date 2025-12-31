"""
Graph builder for routing.

Constructs a weighted graph from communication links for path finding.
Nodes are satellites and ground stations, edges are communication links.
"""
from typing import Dict, List, Any, Set


class Graph:
    """
    Weighted directed graph for routing.
    
    Nodes are identified by "type:id" strings (e.g., "satellite:1", "ground_station:5")
    Edges have weight based on latency, cost, and policy preferences.
    """
    
    def __init__(self):
        self.nodes: Set[str] = set()
        self.edges: Dict[str, Dict[str, Dict[str, Any]]] = {}  # source -> {target -> {weight, latency, cost, ...}}
    
    def add_node(self, node_key: str) -> None:
        """Add a node to the graph."""
        self.nodes.add(node_key)
        if node_key not in self.edges:
            self.edges[node_key] = {}
    
    def add_edge(
        self,
        source: str,
        target: str,
        weight: float,
        latency_ms: float = 0,
        cost: float = 1.0,
        bandwidth_mbps: float = None,
        bidirectional: bool = True
    ) -> None:
        """
        Add an edge (link) to the graph.
        
        Args:
            source: Source node key
            target: Target node key
            weight: Edge weight for path finding
            latency_ms: Link latency in milliseconds
            cost: Link cost
            bandwidth_mbps: Link bandwidth
            bidirectional: If True, adds reverse edge too
        """
        self.add_node(source)
        self.add_node(target)
        
        edge_data = {
            'weight': weight,
            'latency_ms': latency_ms,
            'cost': cost,
            'bandwidth_mbps': bandwidth_mbps
        }
        
        self.edges[source][target] = edge_data
        
        if bidirectional:
            if target not in self.edges:
                self.edges[target] = {}
            self.edges[target][source] = edge_data.copy()
    
    def get_neighbors(self, node: str) -> Dict[str, Dict[str, Any]]:
        """Get all neighbors of a node with edge data."""
        return self.edges.get(node, {})
    
    def has_node(self, node: str) -> bool:
        """Check if node exists in graph."""
        return node in self.nodes
    
    def node_count(self) -> int:
        """Return number of nodes."""
        return len(self.nodes)
    
    def edge_count(self) -> int:
        """Return number of edges."""
        count = 0
        for source in self.edges:
            count += len(self.edges[source])
        return count


class GraphBuilder:
    """
    Builds routing graphs from link data.
    """
    
    def __init__(
        self,
        latency_weight: float = 1.0,
        cost_weight: float = 0.5,
        hop_weight: float = 0.3
    ):
        """
        Initialize graph builder with weight parameters.
        
        Args:
            latency_weight: Weight for latency in edge cost calculation
            cost_weight: Weight for monetary cost
            hop_weight: Weight for hop count (uniform per hop)
        """
        self.latency_weight = latency_weight
        self.cost_weight = cost_weight
        self.hop_weight = hop_weight
    
    def build_from_links(self, links: List[Any]) -> Graph:
        """
        Build a graph from a list of link objects.
        
        Args:
            links: List of link ORM objects or dictionaries
            
        Returns:
            Graph object ready for path finding
        """
        graph = Graph()
        
        for link in links:
            # Handle both ORM objects and dictionaries
            if hasattr(link, 'source_type'):
                source_type = link.source_type
                source_id = link.source_id
                target_type = link.target_type
                target_id = link.target_id
                latency = link.latency_ms or 0
                cost = link.cost or 1.0
                bandwidth = link.bandwidth_mbps
            else:
                source_type = link['source_type']
                source_id = link['source_id']
                target_type = link['target_type']
                target_id = link['target_id']
                latency = link.get('latency_ms', 0) or 0
                cost = link.get('cost', 1.0) or 1.0
                bandwidth = link.get('bandwidth_mbps')
            
            source_key = f"{source_type}:{source_id}"
            target_key = f"{target_type}:{target_id}"
            
            # Calculate composite weight
            weight = self._calculate_weight(latency, cost)
            
            graph.add_edge(
                source_key,
                target_key,
                weight=weight,
                latency_ms=latency,
                cost=cost,
                bandwidth_mbps=bandwidth,
                bidirectional=True  # Most satellite links are bidirectional
            )
        
        return graph
    
    def _calculate_weight(self, latency_ms: float, cost: float) -> float:
        """
        Calculate edge weight from link properties.
        
        The weight is a normalized combination of latency, cost, and a base hop penalty.
        Lower weight = better path.
        """
        # Normalize latency (assume typical range 0-500ms)
        norm_latency = latency_ms / 100.0 if latency_ms else 0
        
        # Normalize cost (assume range 0-10)
        norm_cost = cost if cost else 1.0
        
        # Base hop penalty
        hop_penalty = 1.0
        
        weight = (
            self.latency_weight * norm_latency +
            self.cost_weight * norm_cost +
            self.hop_weight * hop_penalty
        )
        
        return max(0.001, weight)  # Ensure positive weight
