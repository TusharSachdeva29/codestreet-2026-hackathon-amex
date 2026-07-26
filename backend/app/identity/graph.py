"""Identity Graph with MongoDB Persistence for Hybrid Resolution."""

import uuid
import logging
from datetime import datetime, timezone
from pymongo.database import Database
from app.identity.models import IdentityNode, GraphNode, GraphEdge

logger = logging.getLogger("app.identity.graph")

class IdentityGraph:
    """
    Maintains a persistent graph of identifier relationships in MongoDB.
    Implements Connected Components via shared customer_id to simulate Union-Find.
    """

    def __init__(self, db: Database = None) -> None:
        self.db = db
        if self.db is not None:
            self.nodes_col = self.db["identity_nodes"]
            self.edges_col = self.db["identity_edges"]
            self.nodes_col.create_index("id", unique=True)
            self.nodes_col.create_index("id_type")
            self.nodes_col.create_index("id_value")
            self.nodes_col.create_index("customer_id")
            self.edges_col.create_index("source")
            self.edges_col.create_index("target")
        else:
            logger.warning("IdentityGraph initialized without DB connection. Operations will fail.")

    def _get_node_id(self, node: IdentityNode) -> str:
        return f"{node.id_type}:{node.id_value}"

    def get_node(self, node: IdentityNode) -> GraphNode | None:
        if self.db is None: return None
        doc = self.nodes_col.find_one({"id": self._get_node_id(node)})
        if doc:
            doc.pop('_id', None)
            return GraphNode(**doc)
        return None

    def get_nodes_by_type(self, id_type: str) -> list[GraphNode]:
        if self.db is None: return []
        docs = self.nodes_col.find({"id_type": id_type})
        return [GraphNode(**{k: v for k, v in d.items() if k != '_id'}) for d in docs]

    def upsert_node(self, node: IdentityNode, customer_id: str) -> GraphNode:
        """Upsert a node. If it exists, update last_seen, but DO NOT change customer_id here."""
        if self.db is None: 
            return GraphNode(id=self._get_node_id(node), id_type=node.id_type, id_value=node.id_value, customer_id=customer_id)
            
        node_id = self._get_node_id(node)
        now = datetime.now(timezone.utc)
        
        doc = self.nodes_col.find_one({"id": node_id})
        if doc:
            # Update last_seen
            self.nodes_col.update_one({"id": node_id}, {"$set": {"last_seen": now}})
            doc["last_seen"] = now
            doc.pop('_id', None)
            return GraphNode(**doc)
        else:
            # Create new
            g_node = GraphNode(id=node_id, id_type=node.id_type, id_value=node.id_value, customer_id=customer_id, first_seen=now, last_seen=now)
            self.nodes_col.insert_one(g_node.model_dump())
            return g_node

    def add_edge(self, source: IdentityNode, target: IdentityNode, confidence: float, evidence: list[str]) -> None:
        if self.db is None: return
        src_id = self._get_node_id(source)
        tgt_id = self._get_node_id(target)
        if src_id == tgt_id:
            return
            
        edge = GraphEdge(
            source=src_id,
            target=tgt_id,
            confidence=confidence,
            evidence=evidence
        )
        self.edges_col.insert_one(edge.model_dump())

    def merge_customers(self, from_customer_id: str, to_customer_id: str) -> None:
        """Merge operation for Union-Find: All nodes in from_customer_id become to_customer_id."""
        if self.db is None: return
        if from_customer_id == to_customer_id:
            return
            
        self.nodes_col.update_many(
            {"customer_id": from_customer_id},
            {"$set": {"customer_id": to_customer_id}}
        )

    def get_cluster_identifiers(self, customer_id: str) -> dict[str, str]:
        """Return all unique identity nodes belonging to a resolved customer ID."""
        if self.db is None: return {}
        cluster_dict = {}
        docs = self.nodes_col.find({"customer_id": customer_id})
        for doc in docs:
            # Keep one value per type for simplicity in the resolved event
            cluster_dict[doc["id_type"]] = doc["id_value"]
        return cluster_dict

    def get_all_graph_data(self) -> dict:
        """Helper for visualization."""
        if self.db is None: return {"nodes": [], "edges": []}
        
        nodes = []
        for doc in self.nodes_col.find():
            nodes.append({
                "id": doc["id"],
                "data": {
                    "label": doc["id_value"], 
                    "type": doc["id_type"],
                    "customer_id": doc.get("customer_id", ""),
                    "first_seen": doc.get("first_seen", "").isoformat() if hasattr(doc.get("first_seen"), 'isoformat') else doc.get("first_seen"),
                    "last_seen": doc.get("last_seen", "").isoformat() if hasattr(doc.get("last_seen"), 'isoformat') else doc.get("last_seen")
                },
                "type": "default"
            })
            
        edges = []
        for doc in self.edges_col.find():
            edges.append({
                "id": str(doc["_id"]),
                "source": doc["source"],
                "target": doc["target"],
                "label": f"{doc['confidence']:.2f}",
                "animated": doc['confidence'] < 1.0,
                "data": {
                    "confidence": doc['confidence'], 
                    "evidence": doc['evidence'],
                    "created_at": doc.get("created_at", "").isoformat() if hasattr(doc.get("created_at"), 'isoformat') else doc.get("created_at")
                }
            })
            
        return {"nodes": nodes, "edges": edges}
