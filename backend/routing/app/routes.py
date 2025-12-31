"""
API routes for Routing service.
"""
from datetime import datetime, timezone
from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .db import get_db
from .models import LinkORM, PolicyORM
from .schemas import (
    LinkCreate, LinkResponse, LinkList,
    PolicyCreate, PolicyResponse,
    RouteRequest, RouteResponse, RouteHop
)
from .services.path_finder import PathFinder
from .services.graph_builder import GraphBuilder

router = APIRouter()


# ============ Link Endpoints ============

@router.get("/links", response_model=LinkList)
async def list_links(
    link_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """List all links with optional filtering."""
    query = select(LinkORM)
    
    if link_type:
        query = query.where(LinkORM.link_type == link_type)
    if is_active is not None:
        query = query.where(LinkORM.is_active == is_active)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    links = result.scalars().all()
    
    return LinkList(
        data=[_link_to_response(l) for l in links],
        total=len(links)
    )


@router.post("/links", response_model=LinkResponse, status_code=201)
async def create_link(
    link: LinkCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new communication link."""
    db_link = LinkORM(
        link_type=link.link_type.value,
        source_type=link.source_type,
        source_id=link.source_id,
        target_type=link.target_type,
        target_id=link.target_id,
        latency_ms=link.latency_ms,
        bandwidth_mbps=link.bandwidth_mbps,
        cost=link.cost,
        is_active=link.is_active,
        metadata_=link.metadata
    )
    db.add(db_link)
    await db.commit()
    await db.refresh(db_link)
    
    return _link_to_response(db_link)


@router.get("/links/{link_id}", response_model=LinkResponse)
async def get_link(link_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific link."""
    link = await db.get(LinkORM, link_id)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    return _link_to_response(link)


@router.delete("/links/{link_id}", status_code=204)
async def delete_link(link_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a link."""
    link = await db.get(LinkORM, link_id)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    await db.delete(link)
    await db.commit()


# ============ Policy Endpoints ============

@router.get("/policies", response_model=List[PolicyResponse])
async def list_policies(db: AsyncSession = Depends(get_db)):
    """List all routing policies."""
    result = await db.execute(select(PolicyORM))
    policies = result.scalars().all()
    return [_policy_to_response(p) for p in policies]


@router.post("/policies", response_model=PolicyResponse, status_code=201)
async def create_policy(
    policy: PolicyCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new routing policy."""
    db_policy = PolicyORM(
        name=policy.name,
        description=policy.description,
        latency_weight=policy.latency_weight,
        cost_weight=policy.cost_weight,
        hop_weight=policy.hop_weight,
        max_latency_ms=policy.max_latency_ms,
        max_hops=policy.max_hops,
        max_cost=policy.max_cost,
        preferred_ground_stations=policy.preferred_ground_stations,
        avoided_ground_stations=policy.avoided_ground_stations,
        is_default=policy.is_default
    )
    db.add(db_policy)
    await db.commit()
    await db.refresh(db_policy)
    
    return _policy_to_response(db_policy)


# ============ Routing Endpoints ============

@router.post("/routing/paths", response_model=RouteResponse)
async def compute_path(
    request: RouteRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Compute the optimal path between origin and destination.
    
    Uses Dijkstra's algorithm with policy-based weights.
    """
    # Get all active links
    result = await db.execute(
        select(LinkORM).where(LinkORM.is_active == True)
    )
    links = result.scalars().all()
    
    if not links:
        return RouteResponse(
            request_id=str(uuid.uuid4()),
            origin=RouteHop(
                node_type=request.origin_type,
                node_id=request.origin_id
            ),
            destination=RouteHop(
                node_type=request.destination_type,
                node_id=request.destination_id
            ),
            hops=[],
            total_latency_ms=0,
            total_cost=0,
            total_hops=0,
            computed_at=datetime.now(timezone.utc),
            feasible=False,
            message="No active links available"
        )
    
    # Get policy if specified
    policy = None
    if request.policy_id:
        policy = await db.get(PolicyORM, request.policy_id)
        if not policy:
            raise HTTPException(status_code=404, detail="Policy not found")
    else:
        # Try to get default policy
        result = await db.execute(
            select(PolicyORM).where(PolicyORM.is_default == True)
        )
        policy = result.scalar_one_or_none()
    
    # Build graph and find path
    graph_builder = GraphBuilder()
    graph = graph_builder.build_from_links(links)
    
    path_finder = PathFinder(policy=policy)
    
    origin_key = f"{request.origin_type}:{request.origin_id}"
    dest_key = f"{request.destination_type}:{request.destination_id}"
    
    try:
        path_result = path_finder.find_path(graph, origin_key, dest_key)
    except Exception as e:
        return RouteResponse(
            request_id=str(uuid.uuid4()),
            origin=RouteHop(
                node_type=request.origin_type,
                node_id=request.origin_id
            ),
            destination=RouteHop(
                node_type=request.destination_type,
                node_id=request.destination_id
            ),
            hops=[],
            total_latency_ms=0,
            total_cost=0,
            total_hops=0,
            computed_at=datetime.now(timezone.utc),
            feasible=False,
            message=str(e)
        )
    
    # Convert path to response
    hops = []
    for node_key in path_result['path'][1:-1]:  # Exclude origin and destination
        node_type, node_id = node_key.split(':')
        hops.append(RouteHop(
            node_type=node_type,
            node_id=int(node_id),
            latency_ms=path_result.get('hop_latencies', {}).get(node_key),
            cost=path_result.get('hop_costs', {}).get(node_key)
        ))
    
    return RouteResponse(
        request_id=str(uuid.uuid4()),
        origin=RouteHop(
            node_type=request.origin_type,
            node_id=request.origin_id
        ),
        destination=RouteHop(
            node_type=request.destination_type,
            node_id=request.destination_id
        ),
        hops=hops,
        total_latency_ms=path_result['total_latency'],
        total_cost=path_result['total_cost'],
        total_hops=len(path_result['path']) - 1,
        computed_at=datetime.now(timezone.utc),
        policy_name=policy.name if policy else None,
        feasible=path_result['feasible'],
        message=path_result.get('message')
    )


# ============ Helper Functions ============

def _link_to_response(link: LinkORM) -> LinkResponse:
    return LinkResponse(
        id=link.id,
        link_type=link.link_type,
        source_type=link.source_type,
        source_id=link.source_id,
        target_type=link.target_type,
        target_id=link.target_id,
        latency_ms=link.latency_ms,
        bandwidth_mbps=link.bandwidth_mbps,
        cost=link.cost,
        is_active=link.is_active,
        metadata=link.metadata_ or {},
        created_at=link.created_at,
        updated_at=link.updated_at
    )


def _policy_to_response(policy: PolicyORM) -> PolicyResponse:
    return PolicyResponse(
        id=policy.id,
        name=policy.name,
        description=policy.description,
        latency_weight=policy.latency_weight,
        cost_weight=policy.cost_weight,
        hop_weight=policy.hop_weight,
        max_latency_ms=policy.max_latency_ms,
        max_hops=policy.max_hops,
        max_cost=policy.max_cost,
        preferred_ground_stations=policy.preferred_ground_stations or [],
        avoided_ground_stations=policy.avoided_ground_stations or [],
        is_default=policy.is_default,
        created_at=policy.created_at,
        updated_at=policy.updated_at
    )
