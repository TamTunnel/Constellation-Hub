"""
Unit tests for Graph Builder.

Tests network graph construction from link data.
"""
from app.services.graph_builder import Graph, GraphBuilder


class TestGraph:
    """Test cases for Graph data structure."""
    
    def test_add_node(self):
        """Test adding nodes to graph."""
        graph = Graph()
        graph.add_node("sat-1", {"type": "satellite"})
        
        assert "sat-1" in graph.nodes
        assert graph.nodes["sat-1"]["type"] == "satellite"
    
    def test_add_edge(self):
        """Test adding edges to graph."""
        graph = Graph()
        graph.add_node("sat-1", {})
        graph.add_node("gs-1", {})
        graph.add_edge("sat-1", "gs-1", latency_ms=50, bandwidth_mbps=100)
        
        assert "gs-1" in graph.edges["sat-1"]
        assert graph.edges["sat-1"]["gs-1"]["latency_ms"] == 50
    
    def test_add_edge_creates_nodes_if_missing(self):
        """Test that adding edge creates nodes if they don't exist."""
        graph = Graph()
        graph.add_edge("sat-1", "gs-1", weight=1.0)
        
        assert "sat-1" in graph.nodes
        assert "gs-1" in graph.nodes
    
    def test_get_neighbors(self):
        """Test getting neighbors of a node."""
        graph = Graph()
        graph.add_edge("sat-1", "gs-1", weight=1.0)
        graph.add_edge("sat-1", "gs-2", weight=2.0)
        graph.add_edge("sat-2", "gs-1", weight=1.5)
        
        neighbors = graph.get_neighbors("sat-1")
        
        assert len(neighbors) == 2
        assert "gs-1" in neighbors
        assert "gs-2" in neighbors
    
    def test_get_neighbors_empty(self):
        """Test getting neighbors of node with no edges."""
        graph = Graph()
        graph.add_node("isolated", {})
        
        neighbors = graph.get_neighbors("isolated")
        
        assert neighbors == {}
    
    def test_get_edge(self):
        """Test getting edge data."""
        graph = Graph()
        graph.add_edge("sat-1", "gs-1", latency_ms=50, cost=1.5)
        
        edge = graph.get_edge("sat-1", "gs-1")
        
        assert edge["latency_ms"] == 50
        assert edge["cost"] == 1.5
    
    def test_get_edge_nonexistent(self):
        """Test getting nonexistent edge returns None."""
        graph = Graph()
        graph.add_node("sat-1", {})
        
        edge = graph.get_edge("sat-1", "gs-1")
        
        assert edge is None


class TestGraphBuilder:
    """Test cases for GraphBuilder."""
    
    def setup_method(self):
        self.builder = GraphBuilder()
    
    def test_build_empty_graph(self):
        """Test building graph with no links."""
        graph = self.builder.build([])
        
        assert len(graph.nodes) == 0
    
    def test_build_with_satellite_ground_links(self):
        """Test building graph with satellite-ground links."""
        links = [
            {
                "source_type": "satellite",
                "source_id": 1,
                "target_type": "ground_station",
                "target_id": 1,
                "latency_ms": 50,
                "bandwidth_mbps": 100,
                "cost_per_mb": 0.01,
                "is_active": True
            },
            {
                "source_type": "satellite",
                "source_id": 2,
                "target_type": "ground_station",
                "target_id": 1,
                "latency_ms": 60,
                "bandwidth_mbps": 80,
                "cost_per_mb": 0.015,
                "is_active": True
            }
        ]
        
        graph = self.builder.build(links)
        
        assert "sat-1" in graph.nodes
        assert "sat-2" in graph.nodes
        assert "gs-1" in graph.nodes
    
    def test_build_ignores_inactive_links(self):
        """Test that inactive links are ignored."""
        links = [
            {
                "source_type": "satellite",
                "source_id": 1,
                "target_type": "ground_station",
                "target_id": 1,
                "is_active": True
            },
            {
                "source_type": "satellite",
                "source_id": 2,
                "target_type": "ground_station",
                "target_id": 1,
                "is_active": False
            }
        ]
        
        graph = self.builder.build(links)
        
        # sat-2 should have no neighbors since its only link is inactive
        neighbors = graph.get_neighbors("sat-2")
        assert len(neighbors) == 0
    
    def test_build_creates_bidirectional_edges(self):
        """Test that edges are bidirectional by default."""
        links = [
            {
                "source_type": "satellite",
                "source_id": 1,
                "target_type": "ground_station",
                "target_id": 1,
                "is_active": True
            }
        ]
        
        graph = self.builder.build(links)
        
        # Edge should exist in both directions
        assert graph.get_edge("sat-1", "gs-1") is not None
        assert graph.get_edge("gs-1", "sat-1") is not None
    
    def test_build_with_inter_satellite_links(self):
        """Test building graph with inter-satellite links."""
        links = [
            {
                "source_type": "satellite",
                "source_id": 1,
                "target_type": "satellite",
                "target_id": 2,
                "latency_ms": 10,
                "is_active": True
            }
        ]
        
        graph = self.builder.build(links)
        
        assert "sat-1" in graph.nodes
        assert "sat-2" in graph.nodes
        assert graph.get_edge("sat-1", "sat-2") is not None


class TestGraphSerialization:
    """Test cases for graph serialization."""
    
    def test_to_dict(self):
        """Test converting graph to dictionary."""
        graph = Graph()
        graph.add_node("sat-1", {"type": "satellite"})
        graph.add_node("gs-1", {"type": "ground_station"})
        graph.add_edge("sat-1", "gs-1", weight=1.0)
        
        result = graph.to_dict()
        
        assert "nodes" in result
        assert "edges" in result
        assert "sat-1" in result["nodes"]
    
    def test_node_count(self):
        """Test getting node count."""
        graph = Graph()
        graph.add_node("a", {})
        graph.add_node("b", {})
        graph.add_node("c", {})
        
        assert graph.node_count() == 3
    
    def test_edge_count(self):
        """Test getting edge count."""
        graph = Graph()
        graph.add_edge("a", "b", weight=1)
        graph.add_edge("b", "c", weight=1)
        
        # Each edge is bidirectional = 2 directed edges each = 4 total
        assert graph.edge_count() == 4
