"""
Ops Co-Pilot - AI-powered operations assistant.

Analyzes system events and telemetry to:
- Summarize incidents in natural language
- Identify patterns and root causes
- Suggest mitigation actions

Uses an LLMClient abstraction to support multiple backends:
- MockLLMClient: Template-based responses for testing
- OpenAIClient: OpenAI GPT models
- AnthropicClient: Anthropic Claude models
- LocalLLMClient: Local LLM servers (Ollama, vLLM)
"""
import os
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import uuid
import json


class LLMClient(ABC):
    """
    Abstract base class for LLM clients.
    
    All LLM integrations must implement the analyze method.
    """
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name."""
        pass
    
    @abstractmethod
    def analyze(
        self,
        events: List[Dict[str, Any]],
        context: Dict[str, Any],
        focus_areas: List[str]
    ) -> Dict[str, Any]:
        """
        Analyze events and generate insights.
        
        Args:
            events: List of system events
            context: Additional context information
            focus_areas: Areas to focus analysis on
            
        Returns:
            Dictionary containing summary, findings, and actions
        """
        pass

    @classmethod
    def create(cls, provider: str) -> 'LLMClient':
        """Factory method to create LLMClient instances."""
        if provider == "mock":
            return MockLLMClient()
        elif provider == "openai":
            return OpenAIClient()
        elif provider == "anthropic":
            return AnthropicClient()
        elif provider == "local":
            return LocalLLMClient()
        else:
            raise ValueError(f"Unknown provider: {provider}")


class MockLLMClient(LLMClient):
    """
    Mock LLM client for testing and demos.
    
    Uses template-based logic to generate realistic-looking responses
    without requiring an actual LLM API.
    """
    
    @property
    def provider_name(self) -> str:
        return "mock"
    
    def analyze(
        self,
        events: List[Dict[str, Any]],
        context: Dict[str, Any],
        focus_areas: List[str]
    ) -> Dict[str, Any]:
        """Generate mock analysis based on event patterns."""
        
        # Count events by type and severity
        event_types = {}
        severity_counts = {'critical': 0, 'warning': 0, 'info': 0}
        affected_satellites = set()
        affected_stations = set()
        
        for event in events:
            evt_type = event.get('event_type', 'unknown')
            event_types[evt_type] = event_types.get(evt_type, 0) + 1
            
            severity = event.get('severity', 'info')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            if event.get('satellite_id'):
                affected_satellites.add(event['satellite_id'])
            if event.get('station_id'):
                affected_stations.add(event['station_id'])
        
        # Generate summary
        summary = self._generate_summary(events, event_types, severity_counts)
        
        # Generate findings
        findings = self._generate_findings(events, event_types)
        
        # Generate actions
        actions = self._generate_actions(events, event_types, severity_counts)
        
        # Calculate risk level
        if severity_counts['critical'] > 2:
            risk_level = "high"
        elif severity_counts['critical'] > 0 or severity_counts['warning'] > 3:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        # Calculate confidence (mock value based on data quality)
        confidence = min(0.95, 0.7 + len(events) * 0.01)
        
        return {
            'summary': summary,
            'key_findings': findings,
            'suggested_actions': actions,
            'risk_level': risk_level,
            'affected_satellites': list(affected_satellites),
            'affected_stations': list(affected_stations),
            'confidence': confidence
        }

    def generate(self, prompt: str) -> str:
        """Mock simple generation."""
        return "Mock response"

    def analyze_events(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Alias for analyze() to match test expectations in TestMockLLMClient.
        The test calls analyze_events(events) without context/focus_areas.
        """
        return self.analyze(events, {}, [])
    
    def _generate_summary(
        self,
        events: List[Dict[str, Any]],
        event_types: Dict[str, int],
        severity_counts: Dict[str, int]
    ) -> str:
        """Generate a natural language summary."""
        
        total_events = len(events)
        critical_count = severity_counts['critical']
        warning_count = severity_counts['warning']
        
        # Build summary
        parts = [f"Analysis of {total_events} events over the review period."]
        
        if critical_count > 0:
            parts.append(f"⚠️ {critical_count} critical event(s) require immediate attention.")
        
        if warning_count > 0:
            parts.append(f"{warning_count} warning(s) detected.")
        
        # Identify patterns
        if 'missed_pass' in event_types and event_types['missed_pass'] >= 2:
            parts.append(
                f"Pattern detected: {event_types['missed_pass']} missed passes may indicate "
                "ground station issues or orbital anomalies."
            )
        
        if 'link_failure' in event_types:
            parts.append(
                f"Link failures observed ({event_types['link_failure']} occurrences). "
                "Recommend reviewing antenna pointing and weather conditions."
            )
        
        if 'schedule_conflict' in event_types:
            parts.append(
                "Scheduling conflicts detected. Consider reviewing resource allocation."
            )
        
        return " ".join(parts)
    
    def _generate_findings(
        self,
        events: List[Dict[str, Any]],
        event_types: Dict[str, int]
    ) -> List[str]:
        """Generate key findings from event analysis."""
        findings = []
        
        # Group events by satellite
        sat_events: Dict[int, List] = {}
        for event in events:
            sat_id = event.get('satellite_id')
            if sat_id:
                if sat_id not in sat_events:
                    sat_events[sat_id] = []
                sat_events[sat_id].append(event)
        
        # Find satellites with multiple issues
        for sat_id, sat_event_list in sat_events.items():
            critical_events = [e for e in sat_event_list if e.get('severity') == 'critical']
            if len(critical_events) >= 2:
                findings.append(
                    f"Satellite {sat_id} has {len(critical_events)} critical events. "
                    "Potential systemic issue requires investigation."
                )
        
        # Group events by station
        station_events: Dict[int, List] = {}
        for event in events:
            station_id = event.get('station_id')
            if station_id:
                if station_id not in station_events:
                    station_events[station_id] = []
                station_events[station_id].append(event)
        
        # Find stations with issues
        for station_id, station_event_list in station_events.items():
            if len(station_event_list) >= 3:
                findings.append(
                    f"Ground station {station_id} involved in {len(station_event_list)} events. "
                    "Consider scheduling maintenance or reducing workload."
                )
        
        # Check for time patterns
        if 'missed_pass' in event_types and event_types['missed_pass'] >= 3:
            findings.append(
                "Multiple missed passes detected. Possible causes: weather, "
                "antenna issues, or satellite attitude problems."
            )
        
        if not findings:
            findings.append("No significant patterns or anomalies detected in the event data.")
        
        return findings
    
    def _generate_actions(
        self,
        events: List[Dict[str, Any]],
        event_types: Dict[str, int],
        severity_counts: Dict[str, int]
    ) -> List[Dict[str, Any]]:
        """Generate suggested actions."""
        actions = []
        
        # Critical severity actions
        if severity_counts['critical'] > 0:
            critical_events = [e for e in events if e.get('severity') == 'critical']
            affected_sats = set(e.get('satellite_id') for e in critical_events if e.get('satellite_id'))
            
            if affected_sats:
                actions.append({
                    'id': str(uuid.uuid4()),
                    'action': f"Review telemetry for satellite(s) {', '.join(map(str, affected_sats))}",
                    'rationale': "Critical events detected that may indicate hardware or software issues",
                    'priority': 'critical',
                    'estimated_impact': "Prevent potential mission impact"
                })
        
        # Missed pass actions
        if 'missed_pass' in event_types:
            missed_events = [e for e in events if e.get('event_type') == 'missed_pass']
            affected_stations = set(e.get('station_id') for e in missed_events if e.get('station_id'))
            
            if affected_stations:
                for station_id in list(affected_stations)[:2]:  # Top 2
                    actions.append({
                        'id': str(uuid.uuid4()),
                        'action': f"Schedule diagnostic check for ground station {station_id}",
                        'rationale': "Multiple missed passes may indicate equipment issues",
                        'priority': 'high',
                        'estimated_impact': "Restore normal operations within 24 hours"
                    })
        
        # Link failure actions
        if 'link_failure' in event_types:
            actions.append({
                'id': str(uuid.uuid4()),
                'action': "Review weather data at affected ground stations",
                'rationale': "Link failures often correlate with weather conditions",
                'priority': 'medium',
                'estimated_impact': "Inform pass planning for next 48 hours"
            })
        
        # General recommendation
        if not actions:
            actions.append({
                'id': str(uuid.uuid4()),
                'action': "Continue monitoring; no immediate action required",
                'rationale': "Event patterns are within normal operational parameters",
                'priority': 'low',
                'estimated_impact': "Maintain situational awareness"
            })
        
        return actions


class OpenAIClient(LLMClient):
    """
    OpenAI GPT client for production use.
    
    Requires OPENAI_API_KEY environment variable.
    """
    
    @property
    def provider_name(self) -> str:
        return "openai"
    
    def __init__(self):
        self.api_key = os.getenv('LLM_API_KEY', '')
        self.model = os.getenv('LLM_MODEL', 'gpt-4')
    
    def analyze(
        self,
        events: List[Dict[str, Any]],
        context: Dict[str, Any],
        focus_areas: List[str]
    ) -> Dict[str, Any]:
        """
        Analyze events using OpenAI API.
        
        NOTE: This is a placeholder. Full implementation would:
        1. Format events into a prompt
        2. Call OpenAI API with structured output
        3. Parse and validate response
        """
        if not self.api_key:
            # Fall back to mock if no API key
            mock = MockLLMClient()
            result = mock.analyze(events, context, focus_areas)
            result['_note'] = "OpenAI API key not configured. Using mock responses."
            return result
        
        # TODO: Implement actual OpenAI API call
        # For now, use mock
        mock = MockLLMClient()
        return mock.analyze(events, context, focus_areas)


class AnthropicClient(LLMClient):
    """
    Anthropic Claude client for production use.
    
    Requires ANTHROPIC_API_KEY environment variable.
    """
    
    @property
    def provider_name(self) -> str:
        return "anthropic"
    
    def __init__(self):
        self.api_key = os.getenv('LLM_API_KEY', '')
        self.model = os.getenv('LLM_MODEL', 'claude-3-sonnet-20240229')
    
    def analyze(
        self,
        events: List[Dict[str, Any]],
        context: Dict[str, Any],
        focus_areas: List[str]
    ) -> Dict[str, Any]:
        """Analyze events using Anthropic API."""
        if not self.api_key:
            mock = MockLLMClient()
            result = mock.analyze(events, context, focus_areas)
            result['_note'] = "Anthropic API key not configured. Using mock responses."
            return result
        
        # TODO: Implement actual Anthropic API call
        mock = MockLLMClient()
        return mock.analyze(events, context, focus_areas)


class LocalLLMClient(LLMClient):
    """
    Local LLM server client (Ollama, vLLM, etc.).
    
    Requires LOCAL_LLM_URL environment variable.
    """
    
    @property
    def provider_name(self) -> str:
        return "local"
    
    def __init__(self):
        self.url = os.getenv('LOCAL_LLM_URL', 'http://localhost:11434')
        self.model = os.getenv('LLM_MODEL', 'llama2')
    
    def analyze(
        self,
        events: List[Dict[str, Any]],
        context: Dict[str, Any],
        focus_areas: List[str]
    ) -> Dict[str, Any]:
        """Analyze events using local LLM."""
        # TODO: Implement actual local LLM API call
        mock = MockLLMClient()
        result = mock.analyze(events, context, focus_areas)
        result['_note'] = "Local LLM integration not yet implemented. Using mock responses."
        return result


def get_llm_client() -> LLMClient:
    """
    Factory function to get the configured LLM client.
    
    Set LLM_PROVIDER environment variable to:
    - 'mock' (default)
    - 'openai'
    - 'anthropic'
    - 'local'
    """
    provider = os.getenv('LLM_PROVIDER', 'mock').lower()
    
    if provider == 'openai':
        return OpenAIClient()
    elif provider == 'anthropic':
        return AnthropicClient()
    elif provider == 'local':
        return LocalLLMClient()
    else:
        return MockLLMClient()


class OpsCoPilot:
    """
    High-level operations co-pilot interface.
    
    Combines event analysis with operational knowledge
    to provide actionable insights.
    """
    
    def __init__(self, llm_client: Optional[LLMClient] = None, llm_provider: str = None):
        if llm_client:
            self.llm_client = llm_client
        elif llm_provider:
            self.llm_client = LLMClient.create(llm_provider)
        else:
            self.llm_client = get_llm_client()
    
    def analyze(
        self,
        events: List[Dict[str, Any]],
        context: Dict[str, Any] = None,
        focus_areas: List[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze events and provide operational insights.
        
        Args:
            events: List of system events to analyze
            context: Additional context (e.g., current schedule, constellation status)
            focus_areas: Specific areas to focus on (e.g., ['missed_passes', 'link_quality'])
            
        Returns:
            Analysis result with summary, findings, and actions
        """
        context = context or {}
        focus_areas = focus_areas or []
        
        return self.llm_client.analyze(events, context, focus_areas)
