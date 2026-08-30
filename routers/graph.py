from fastapi import APIRouter
from schemas.graph_schema import GraphNodeRequest
from services.graph_service import add_scan_result, find_campaigns, get_graph_summary

router = APIRouter()

@router.post("/add")
def add_node(request: GraphNodeRequest):
    return add_scan_result(
        node_type=request.node_type,
        node_id=request.node_id,
        related_to=request.related_to,
        risk_score=request.risk_score
    )

@router.get("/campaigns")
def get_campaigns():
    return {"campaigns": find_campaigns()}

@router.get("/summary")
def get_summary():
    return get_graph_summary()