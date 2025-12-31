"""
API routes for AI Agents service.
"""
from datetime import datetime, timezone
import time
from fastapi import APIRouter, HTTPException

from .schemas import (
    OptimizeRequest, OptimizeResponse,
    AnalyzeRequest, AnalyzeResponse,
    ActionUpdateRequest, ActionStatus
)
from .pass_scheduler import get_scheduler
from .ops_copilot import OpsCoPilot

router = APIRouter()

# Store action statuses (in production, would use database)
action_store: dict = {}


# ============ Pass Scheduler Endpoints ============

@router.post("/ai/pass-scheduler/optimize", response_model=OptimizeResponse)
async def optimize_schedule(request: OptimizeRequest):
    """
    Optimize a downlink schedule using AI.
    
    The optimizer uses a pluggable strategy pattern:
    - Default: HeuristicScheduler (rule-based optimization)
    - Future: MLScheduler (machine learning-based)
    
    The strategy is selected via environment variable SCHEDULER_STRATEGY.
    """
    start_time = time.time() * 1000
    
    if not request.passes:
        raise HTTPException(status_code=400, detail="No passes provided for optimization")
    
    # Get the configured scheduler strategy
    scheduler = get_scheduler()
    
    # Get currently scheduled passes
    original_scheduled = [p.id for p in request.passes if p.is_scheduled]
    
    # Convert Pydantic models to dicts for the scheduler
    passes_data = [p.model_dump() for p in request.passes]
    queues_data = {q.satellite_id: q.model_dump() for q in request.data_queues}
    stations_data = {s.id: s.model_dump() for s in request.stations}
    
    # Run optimization
    result = scheduler.optimize(
        passes=passes_data,
        data_queues=queues_data,
        stations=stations_data,
        constraints=request.constraints,
        current_schedule=set(original_scheduled)
    )
    
    computation_time = time.time() * 1000 - start_time
    
    # Calculate changes
    optimized_ids = list(result['selected_passes'])
    original_set = set(original_scheduled)
    optimized_set = set(optimized_ids)
    
    passes_added = list(optimized_set - original_set)
    passes_removed = list(original_set - optimized_set)
    
    return OptimizeResponse(
        original_pass_ids=original_scheduled,
        optimized_pass_ids=optimized_ids,
        passes_added=passes_added,
        passes_removed=passes_removed,
        improvement_metrics=result.get('metrics', {}),
        optimization_strategy=scheduler.strategy_name,
        computation_time_ms=computation_time,
        recommendations=result.get('recommendations', [])
    )


@router.get("/ai/pass-scheduler/strategies")
async def list_strategies():
    """List available scheduling strategies."""
    return {
        "available_strategies": [
            {
                "name": "heuristic",
                "description": "Rule-based optimization using priority scoring and conflict resolution",
                "is_default": True
            },
            {
                "name": "ml",
                "description": "Machine learning-based optimization (coming soon)",
                "is_default": False,
                "status": "not_implemented"
            }
        ],
        "current_strategy": get_scheduler().strategy_name
    }


# ============ Ops Co-Pilot Endpoints ============

@router.post("/ai/ops-copilot/analyze", response_model=AnalyzeResponse)
async def analyze_events(request: AnalyzeRequest):
    """
    Analyze system events and provide operational insights.
    
    The Ops Co-Pilot:
    1. Summarizes recent events in natural language
    2. Identifies patterns and anomalies
    3. Suggests mitigation actions
    
    Uses an LLM client abstraction that can be configured to use:
    - Mock responses (default, for testing)
    - OpenAI API
    - Anthropic API
    - Local LLM server
    """
    if not request.events:
        raise HTTPException(status_code=400, detail="No events provided for analysis")
    
    copilot = OpsCoPilot()
    
    # Convert events to dicts
    events_data = [e.model_dump() for e in request.events]
    
    # Run analysis
    result = copilot.analyze(
        events=events_data,
        context=request.context,
        focus_areas=request.focus_areas
    )
    
    # Store actions for later status updates
    for action in result['suggested_actions']:
        action_store[action['id']] = {
            'action': action,
            'status': ActionStatus.PENDING,
            'created_at': datetime.now(timezone.utc)
        }
    
    return AnalyzeResponse(
        summary=result['summary'],
        key_findings=result['key_findings'],
        suggested_actions=result['suggested_actions'],
        risk_level=result['risk_level'],
        affected_satellites=result['affected_satellites'],
        affected_stations=result['affected_stations'],
        confidence=result['confidence'],
        analyzed_at=datetime.now(timezone.utc)
    )


@router.put("/ai/ops-copilot/actions/{action_id}")
async def update_action_status(action_id: str, request: ActionUpdateRequest):
    """Update the status of a suggested action."""
    if action_id not in action_store:
        raise HTTPException(status_code=404, detail="Action not found")
    
    action_store[action_id]['status'] = request.status
    if request.notes:
        action_store[action_id]['notes'] = request.notes
    action_store[action_id]['updated_at'] = datetime.now(timezone.utc)
    
    return {
        "action_id": action_id,
        "status": request.status,
        "updated_at": action_store[action_id]['updated_at']
    }


@router.get("/ai/ops-copilot/actions")
async def list_actions(status: ActionStatus = None):
    """List all suggested actions, optionally filtered by status."""
    actions = []
    for action_id, data in action_store.items():
        if status is None or data['status'] == status:
            actions.append({
                'id': action_id,
                **data['action'],
                'status': data['status'],
                'created_at': data['created_at'],
                'updated_at': data.get('updated_at'),
                'notes': data.get('notes')
            })
    
    return {"actions": actions, "total": len(actions)}


@router.get("/ai/ops-copilot/providers")
async def list_llm_providers():
    """List available LLM providers for the Ops Co-Pilot."""
    copilot = OpsCoPilot()
    return {
        "available_providers": [
            {
                "name": "mock",
                "description": "Template-based responses for testing and demos",
                "requires_api_key": False
            },
            {
                "name": "openai",
                "description": "OpenAI GPT models",
                "requires_api_key": True
            },
            {
                "name": "anthropic",
                "description": "Anthropic Claude models",
                "requires_api_key": True
            },
            {
                "name": "local",
                "description": "Local LLM server (e.g., Ollama, vLLM)",
                "requires_api_key": False
            }
        ],
        "current_provider": copilot.llm_client.provider_name
    }
