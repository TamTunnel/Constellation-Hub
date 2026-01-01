"""
Unit tests for Ops Co-Pilot.

Tests AI analysis and response generation.
"""
import pytest
from app.ops_copilot import (
    OpsCoPilot,
    LLMClient,
    MockLLMClient
)


class TestOpsCoPilot:
    """Test cases for Ops Co-Pilot."""
    
    def setup_method(self):
        self.copilot = OpsCoPilot(llm_provider="mock")
    
    def test_analyze_returns_result(self):
        """Test that analyze returns a result dictionary."""
        events = [{"id": 1, "severity": "warning", "msg": "Test event"}]
        result = self.copilot.analyze(events)
        
        assert isinstance(result, dict)
        assert "summary" in result
    
    def test_result_has_required_fields(self):
        """Test that result contains all required fields."""
        events = [{"id": 1, "severity": "info"}]
        result = self.copilot.analyze(events)
        
        assert "summary" in result
        assert "key_findings" in result
        assert "suggested_actions" in result
        assert "risk_level" in result
    
    def test_empty_events_handling(self):
        """Test handling of empty event list."""
        result = self.copilot.analyze([])
        
        assert result is not None
        assert "summary" in result
        assert result["risk_level"] == "low"
    
    def test_confidence_in_range(self):
        """Test that confidence score is between 0 and 1."""
        events = [{"id": 1, "severity": "info"}]
        result = self.copilot.analyze(events)
        
        confidence = result.get("confidence", 0.0)
        assert 0.0 <= confidence <= 1.0
    
    def test_suggested_actions_have_structure(self):
        """Test that actions have required fields."""
        # Force a critical event to generate actions
        events = [{"id": 1, "severity": "critical", "satellite_id": 1}]
        result = self.copilot.analyze(events)

        actions = result.get("suggested_actions", [])
        if actions:
            action = actions[0]
            assert "action" in action
            assert "priority" in action
            assert "estimated_impact" in action


class TestMockLLMClient:
    """Test cases for Mock LLM Client."""
    
    def setup_method(self):
        self.client = MockLLMClient()
    
    def test_generate_returns_string(self):
        """Test simple generation."""
        result = self.client.generate("Analyze this event")
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_analyze_events_returns_dict(self):
        """Test event analysis structure."""
        events = [{"id": 1, "severity": "info"}]
        result = self.client.analyze_events(events)
        
        assert isinstance(result, dict)
        assert "summary" in result
    
    def test_mock_provides_consistent_structure(self):
        """Test that mock client returns consistent structure."""
        events = [{"id": 1, "severity": "info"}]
        result = self.client.analyze_events(events)
        
        assert "summary" in result
        assert "key_findings" in result
        assert "suggested_actions" in result


class TestLLMClientFactory:
    """Test cases for LLM Client Factory."""
    
    def test_create_mock_client(self):
        """Test creating mock client."""
        client = LLMClient.create("mock")
        assert isinstance(client, MockLLMClient)
        assert client.provider_name == "mock"
    
    def test_invalid_provider_raises(self):
        """Test that invalid provider raises error."""
        with pytest.raises(ValueError):
            LLMClient.create("invalid_provider")


class TestActionPrioritization:
    """Test cases for action prioritization."""
    
    def setup_method(self):
        self.copilot = OpsCoPilot(llm_provider="mock")
    
    def test_critical_events_high_priority(self):
        """Test that critical events get high priority."""
        events = [
            {"severity": "critical", "msg": "Major failure", "satellite_id": 1},
            {"severity": "info", "msg": "Routine update"}
        ]
        
        result = self.copilot.analyze(events)
        actions = result.get("suggested_actions", [])
        
        priorities = [a.get("priority") for a in actions]
        # Check if 'critical' or 'high' is in priorities
        assert any(p in ["critical", "high"] for p in priorities)
    
    def test_warning_events_medium_priority(self):
        """Test that warning events get medium priority."""
        events = [
            {"event_type": "link_failure", "severity": "warning", "msg": "Link unstable"}
        ]
        
        result = self.copilot.analyze(events)
        actions = result.get("suggested_actions", [])
        
        # Link failure should generate medium priority action
        priorities = [a.get("priority") for a in actions]
        assert "medium" in priorities
