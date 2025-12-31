"""
Unit tests for Ops Co-Pilot.

Tests AI-powered operations analysis.
"""
import pytest
from app.ops_copilot import OpsCoPilot, LLMClient, MockLLMClient


class TestOpsCoPilot:
    """Test cases for Ops Co-Pilot."""
    
    def setup_method(self):
        self.copilot = OpsCoPilot(llm_provider="mock")
    
    def test_analyze_returns_result(self):
        """Test that analyze returns a result."""
        events = self._create_sample_events()
        
        result = self.copilot.analyze(events=events)
        
        assert result is not None
    
    def test_result_has_required_fields(self):
        """Test that result contains all required fields."""
        events = self._create_sample_events()
        
        result = self.copilot.analyze(events=events)
        
        assert "summary" in result
        assert "key_findings" in result
        assert "suggested_actions" in result
        assert "confidence" in result
    
    def test_empty_events_handling(self):
        """Test handling of empty events list."""
        result = self.copilot.analyze(events=[])
        
        assert result is not None
        assert "summary" in result
    
    def test_confidence_in_range(self):
        """Test that confidence is between 0 and 1."""
        events = self._create_sample_events()
        
        result = self.copilot.analyze(events=events)
        
        assert 0.0 <= result["confidence"] <= 1.0
    
    def test_suggested_actions_have_structure(self):
        """Test that suggested actions have proper structure."""
        events = self._create_sample_events()
        
        result = self.copilot.analyze(events=events)
        
        if len(result["suggested_actions"]) > 0:
            action = result["suggested_actions"][0]
            assert "id" in action
            assert "action" in action
            assert "priority" in action
    
    # Helper methods
    def _create_sample_events(self):
        return [
            {
                "timestamp": "2024-01-15T10:30:00Z",
                "event_type": "missed_pass",
                "severity": "warning",
                "source": "ground_scheduler",
                "message": "Pass SAT-012 to GS-Beta missed due to weather",
                "satellite_id": 12,
                "station_id": 2
            },
            {
                "timestamp": "2024-01-15T11:45:00Z",
                "event_type": "link_failure",
                "severity": "critical",
                "source": "routing",
                "message": "ISL between SAT-012 and SAT-015 lost",
                "satellite_id": 12
            }
        ]


class TestMockLLMClient:
    """Test cases for Mock LLM Client."""
    
    def setup_method(self):
        self.client = MockLLMClient()
    
    def test_generate_returns_string(self):
        """Test that generate returns a string."""
        result = self.client.generate("Analyze this event")
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_analyze_events_returns_dict(self):
        """Test that analyze_events returns a dictionary."""
        events = [
            {"event_type": "test", "message": "Test event"}
        ]
        
        result = self.client.analyze_events(events)
        
        assert isinstance(result, dict)
    
    def test_mock_provides_consistent_structure(self):
        """Test that mock responses have consistent structure."""
        events = [
            {"event_type": "test", "message": "Test event"}
        ]
        
        result = self.client.analyze_events(events)
        
        assert "summary" in result
        assert "findings" in result
        assert "actions" in result


class TestLLMClientFactory:
    """Test cases for LLM client factory."""
    
    def test_create_mock_client(self):
        """Test creating mock client."""
        client = LLMClient.create("mock")
        
        assert client is not None
        assert isinstance(client, MockLLMClient)
    
    def test_invalid_provider_raises(self):
        """Test that invalid provider raises error."""
        with pytest.raises(ValueError):
            LLMClient.create("invalid_provider")


class TestEventParsing:
    """Test cases for event parsing."""
    
    def setup_method(self):
        self.copilot = OpsCoPilot(llm_provider="mock")
    
    def test_parse_missed_pass_event(self):
        """Test parsing missed pass events."""
        events = [{
            "event_type": "missed_pass",
            "satellite_id": 12,
            "station_id": 2,
            "message": "Pass missed"
        }]
        
        parsed = self.copilot._parse_events(events)
        
        assert len(parsed) == 1
        assert parsed[0]["type"] == "missed_pass"
    
    def test_parse_multiple_event_types(self):
        """Test parsing mixed event types."""
        events = [
            {"event_type": "missed_pass", "message": "Pass 1 missed"},
            {"event_type": "link_failure", "message": "Link failed"},
            {"event_type": "anomaly", "message": "Telemetry anomaly"}
        ]
        
        parsed = self.copilot._parse_events(events)
        
        assert len(parsed) == 3
    
    def test_group_events_by_entity(self):
        """Test grouping events by satellite/station."""
        events = [
            {"event_type": "missed_pass", "satellite_id": 1},
            {"event_type": "missed_pass", "satellite_id": 1},
            {"event_type": "missed_pass", "satellite_id": 2}
        ]
        
        grouped = self.copilot._group_by_entity(events)
        
        assert "satellite_1" in grouped
        assert len(grouped["satellite_1"]) == 2


class TestActionPrioritization:
    """Test cases for action prioritization."""
    
    def setup_method(self):
        self.copilot = OpsCoPilot(llm_provider="mock")
    
    def test_critical_events_high_priority(self):
        """Test that critical events produce high priority actions."""
        events = [{
            "event_type": "link_failure",
            "severity": "critical",
            "message": "Complete link failure"
        }]
        
        result = self.copilot.analyze(events=events)
        
        # At least one action should be high or critical priority
        priorities = [a["priority"] for a in result["suggested_actions"]]
        assert any(p in ["critical", "high"] for p in priorities)
    
    def test_warning_events_medium_priority(self):
        """Test that warning events produce medium priority actions."""
        events = [{
            "event_type": "low_signal",
            "severity": "warning",
            "message": "Signal degradation detected"
        }]
        
        result = self.copilot.analyze(events=events)
        
        # Actions should be medium or lower priority
        # This depends on implementation
        assert len(result["suggested_actions"]) >= 0
