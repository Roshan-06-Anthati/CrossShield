from pydantic import BaseModel
from typing import Optional

class GraphNodeRequest(BaseModel):
    node_type: str  # e.g. "email_sender", "domain", "ip"
    node_id: str    # the actual value, e.g. "attacker@fake.com"
    related_to: Optional[list[str]] = None
    risk_score: Optional[float] = 0