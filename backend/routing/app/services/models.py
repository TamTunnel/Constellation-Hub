from typing import List, Optional
from pydantic import BaseModel

class RoutingPolicy(BaseModel):
    optimize_for: str = "latency"
    weight_latency: float = 1.0
    weight_cost: float = 0.0
    max_latency_ms: Optional[float] = None
    max_hops: Optional[int] = None
    max_cost: Optional[float] = None
    avoided_ground_stations: Optional[List[int]] = None

    def __init__(self, **data):
        super().__init__(**data)
        if self.optimize_for == "latency":
            self.weight_latency = 1.0
            self.weight_cost = 0.0
        elif self.optimize_for == "cost":
            self.weight_latency = 0.0
            self.weight_cost = 1.0
