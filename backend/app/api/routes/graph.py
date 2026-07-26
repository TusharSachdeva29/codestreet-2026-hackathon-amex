from fastapi import APIRouter, Query
from app.core.db import MongoDBClient
from app.identity.graph import IdentityGraph

router = APIRouter()
mongo_client = MongoDBClient()

@router.get("", summary="Get full identity graph")
def get_identity_graph(customer_id: str | None = Query(None)):
    """Fetches the identity graph from MongoDB."""
    db = mongo_client.connect()
    if db is None:
        return {"nodes": [], "edges": []}
        
    graph = IdentityGraph(db)
    
    if customer_id:
        # Filter for a specific customer
        nodes = []
        node_docs = graph.nodes_col.find({"customer_id": customer_id})
        node_ids = set()
        
        for doc in node_docs:
            nid = doc["id"]
            node_ids.add(nid)
            nodes.append({
                "id": nid,
                "data": {"label": doc["id_value"], "type": doc["id_type"]},
                "type": "default"
            })
            
        edges = []
        edge_docs = graph.edges_col.find({"source": {"$in": list(node_ids)}})
        for doc in edge_docs:
            if doc["target"] in node_ids:
                edges.append({
                    "id": str(doc["_id"]),
                    "source": doc["source"],
                    "target": doc["target"],
                    "label": f"{doc['confidence']:.2f}",
                    "animated": doc['confidence'] < 1.0,
                    "data": {"confidence": doc['confidence'], "evidence": doc['evidence']}
                })
                
        return {"nodes": nodes, "edges": edges, "stats": {"total_nodes": len(nodes), "total_edges": len(edges)}}
        
    # Return all graph data
    data = graph.get_all_graph_data()
    data["stats"] = {"total_nodes": len(data["nodes"]), "total_edges": len(data["edges"])}
    return data
