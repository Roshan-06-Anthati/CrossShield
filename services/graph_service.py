import networkx as nx
from datetime import datetime

# In-memory graph - resets when server restarts (fine for a demo/portfolio project)
fraud_graph = nx.Graph()


def add_scan_result(node_type: str, node_id: str, related_to: list[str] = None, risk_score: float = 0):
    """
    Adds a node (email sender, domain, etc.) to the graph and connects it
    to related nodes from the same scan.
    """
    fraud_graph.add_node(node_id, type=node_type, risk_score=risk_score, last_seen=datetime.now().isoformat())

    if related_to:
        for related_node in related_to:
            if not fraud_graph.has_node(related_node):
                fraud_graph.add_node(related_node, type="unknown", risk_score=0)
            fraud_graph.add_edge(node_id, related_node)

    return {"node_id": node_id, "added": True}


def find_campaigns(min_cluster_size: int = 2) -> list[dict]:
    """
    Finds clusters of connected nodes - groups of senders/domains/IPs
    that are linked together, which may indicate a coordinated campaign.
    """
    components = list(nx.connected_components(fraud_graph))
    campaigns = []

    for component in components:
        if len(component) >= min_cluster_size:
            nodes_data = []
            total_risk = 0
            for node in component:
                data = fraud_graph.nodes[node]
                nodes_data.append({
                    "id": node,
                    "type": data.get("type", "unknown"),
                    "risk_score": data.get("risk_score", 0)
                })
                total_risk += data.get("risk_score", 0)

            avg_risk = round(total_risk / len(component), 2) if component else 0

            campaigns.append({
                "cluster_size": len(component),
                "nodes": nodes_data,
                "average_risk_score": avg_risk,
                "is_suspicious_cluster": avg_risk > 50
            })

    return campaigns


def get_graph_summary() -> dict:
    return {
        "total_nodes": fraud_graph.number_of_nodes(),
        "total_edges": fraud_graph.number_of_edges(),
        "campaigns_detected": len(find_campaigns())
    }