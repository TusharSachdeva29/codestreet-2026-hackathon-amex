"""Enhanced Identity Graph API with rich data for CDP-grade visualization."""

from fastapi import APIRouter, Query
from pymongo import DESCENDING
from app.core.db import MongoDBClient
from app.identity.graph import IdentityGraph

router = APIRouter()
mongo_client = MongoDBClient()

# Map id_types to semantic relationship labels
RELATIONSHIP_LABELS = {
    "email": "VERIFIED_WITH",
    "phone_number": "VERIFIED_WITH",
    "customer_id": "IDENTIFIED_AS",
    "card_last4": "USED_CARD",
    "device_id": "USED_DEVICE",
    "cookie_id": "USED_COOKIE",
    "session_id": "USED_SESSION",
    "browser_fingerprint": "USED_DEVICE",
    "ip_address": "CONNECTED_TO",
}

TRUSTED_TYPES = {"email", "phone_number", "customer_id", "card_last4"}


def _format_node(doc: dict) -> dict:
    """Convert a MongoDB node doc to a rich React Flow node."""
    id_type = doc.get("id_type", "unknown")
    id_value = doc.get("id_value", "")
    event_count = doc.get("event_count", 1)

    # Mask sensitive values
    if id_type in ("email", "phone_number", "card_last4"):
        if len(id_value) > 5:
            masked = id_value[:3] + "***" + id_value[-2:]
        else:
            masked = "***"
    else:
        masked = id_value[:12] + "..." if len(id_value) > 12 else id_value

    def _iso(val):
        return val.isoformat() if hasattr(val, "isoformat") else val

    return {
        "id": doc["id"],
        "type": "identityNode",  # custom React Flow node type
        "data": {
            "id_type": id_type,
            "id_value": id_value,
            "masked_value": masked,
            "customer_id": doc.get("customer_id", ""),
            "first_seen": _iso(doc.get("first_seen", "")),
            "last_seen": _iso(doc.get("last_seen", "")),
            "event_count": event_count,
            "is_trusted": id_type in TRUSTED_TYPES,
            "connection_count": doc.get("connection_count", 0),
        },
    }


def _format_edge(doc: dict) -> dict:
    """Convert a MongoDB edge doc to a rich React Flow edge."""
    confidence = doc.get("confidence", 0)
    relationship_type = doc.get("relationship_type", "CONNECTED_TO")

    def _iso(val):
        return val.isoformat() if hasattr(val, "isoformat") else val

    return {
        "id": str(doc["_id"]),
        "source": doc["source"],
        "target": doc["target"],
        "type": "identityEdge",
        "animated": confidence < 1.0,
        "data": {
            "confidence": confidence,
            "relationship_type": relationship_type,
            "evidence": doc.get("evidence", []),
            "created_at": _iso(doc.get("created_at", "")),
            "last_updated": _iso(doc.get("last_updated", doc.get("created_at", ""))),
        },
    }


@router.get("", summary="Get full identity graph with rich metadata")
def get_identity_graph(customer_id: str | None = Query(None)):
    """Fetches the identity graph from MongoDB with full CDP-grade metadata."""
    db = mongo_client.connect()
    if db is None:
        return {"nodes": [], "edges": [], "stats": {}, "clusters": []}

    graph = IdentityGraph(db)

    if customer_id:
        node_docs = list(graph.nodes_col.find({"customer_id": customer_id}))
        node_ids = {doc["id"] for doc in node_docs}
        nodes = [_format_node(doc) for doc in node_docs]

        edge_docs = list(graph.edges_col.find({
            "$or": [
                {"source": {"$in": list(node_ids)}},
                {"target": {"$in": list(node_ids)}}
            ]
        }))
        edges = [_format_edge(doc) for doc in edge_docs if doc["source"] in node_ids and doc["target"] in node_ids]

        stats = {
            "total_nodes": len(nodes),
            "total_edges": len(edges),
            "customer_id": customer_id,
        }
        return {"nodes": nodes, "edges": edges, "stats": stats, "clusters": []}

    # Full graph — compute cluster summaries
    all_node_docs = list(graph.nodes_col.find())
    all_edge_docs = list(graph.edges_col.find())

    nodes = [_format_node(doc) for doc in all_node_docs]
    edges = [_format_edge(doc) for doc in all_edge_docs]

    # Build cluster summaries
    cluster_map: dict[str, list] = {}
    for doc in all_node_docs:
        cid = doc.get("customer_id", "unknown")
        cluster_map.setdefault(cid, []).append(doc)

    clusters = []
    for cid, members in cluster_map.items():
        id_types = [m["id_type"] for m in members]
        has_trusted = any(t in TRUSTED_TYPES for t in id_types)
        clusters.append({
            "customer_id": cid,
            "node_count": len(members),
            "identifier_types": list(set(id_types)),
            "has_trusted_id": has_trusted,
        })

    # Sort clusters: largest first
    clusters.sort(key=lambda c: c["node_count"], reverse=True)

    stats = {
        "total_nodes": len(nodes),
        "total_edges": len(edges),
        "total_customers": len(cluster_map),
        "avg_identifiers_per_customer": round(len(nodes) / max(len(cluster_map), 1), 1),
        "largest_cluster": max((c["node_count"] for c in clusters), default=0),
        "connected_components": len(cluster_map),
    }

    return {"nodes": nodes, "edges": edges, "stats": stats, "clusters": clusters}


@router.get("/stats", summary="Get graph-level statistics only")
def get_graph_stats():
    """Returns aggregate stats for the identity graph dashboard header."""
    db = mongo_client.connect()
    if db is None:
        return {}

    graph = IdentityGraph(db)
    total_nodes = graph.nodes_col.count_documents({})
    total_edges = graph.edges_col.count_documents({})
    customers = graph.nodes_col.distinct("customer_id")
    total_customers = len(customers)

    return {
        "total_nodes": total_nodes,
        "total_edges": total_edges,
        "total_customers": total_customers,
        "avg_identifiers": round(total_nodes / max(total_customers, 1), 1),
    }
