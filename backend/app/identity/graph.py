"""Identity Graph with MongoDB Persistence for Hybrid Resolution."""

import logging
from datetime import datetime, timezone
from pymongo.database import Database
from app.identity.models import IdentityNode, GraphNode, GraphEdge

logger = logging.getLogger("app.identity.graph")

# Maps identifier types to semantic relationship labels
RELATIONSHIP_MAP = {
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
            self.edges_col.create_index([("source", 1), ("target", 1)])
            self.edges_col.create_index("source")
            self.edges_col.create_index("target")
        else:
            logger.warning("IdentityGraph initialized without DB connection.")

    def _get_node_id(self, node: IdentityNode) -> str:
        return f"{node.id_type}:{node.id_value}"

    def get_node(self, node: IdentityNode) -> GraphNode | None:
        if self.db is None:
            return None
        doc = self.nodes_col.find_one({"id": self._get_node_id(node)})
        if doc:
            doc.pop("_id", None)
            return GraphNode(**doc)
        return None

    def get_nodes_by_type(self, id_type: str) -> list[GraphNode]:
        if self.db is None:
            return []
        docs = self.nodes_col.find({"id_type": id_type})
        return [GraphNode(**{k: v for k, v in d.items() if k != "_id"}) for d in docs]

    def upsert_node(self, node: IdentityNode, customer_id: str) -> GraphNode:
        """Upsert a node. Update last_seen and event_count on every touch."""
        if self.db is None:
            return GraphNode(
                id=self._get_node_id(node),
                id_type=node.id_type,
                id_value=node.id_value,
                customer_id=customer_id,
            )

        node_id = self._get_node_id(node)
        now = datetime.now(timezone.utc)

        doc = self.nodes_col.find_one({"id": node_id})
        if doc:
            self.nodes_col.update_one(
                {"id": node_id},
                {"$set": {"last_seen": now}, "$inc": {"event_count": 1}},
            )
            doc["last_seen"] = now
            doc.pop("_id", None)
            return GraphNode(**doc)
        else:
            g_node = GraphNode(
                id=node_id,
                id_type=node.id_type,
                id_value=node.id_value,
                customer_id=customer_id,
                first_seen=now,
                last_seen=now,
            )
            data = g_node.model_dump()
            data["event_count"] = 1
            data["connection_count"] = 0
            self.nodes_col.insert_one(data)
            return g_node

    def add_edge(
        self,
        source: IdentityNode,
        target: IdentityNode,
        confidence: float,
        evidence: list[str],
    ) -> None:
        if self.db is None:
            return

        src_id = self._get_node_id(source)
        tgt_id = self._get_node_id(target)
        if src_id == tgt_id:
            return

        # Determine relationship type from the target node type
        relationship_type = RELATIONSHIP_MAP.get(target.id_type, "CONNECTED_TO")
        now = datetime.now(timezone.utc)

        # Check if edge already exists; if so update confidence and evidence
        existing = self.edges_col.find_one({"source": src_id, "target": tgt_id})
        if existing:
            new_conf = max(existing["confidence"], confidence)
            existing_evidence = existing.get("evidence", [])
            merged_evidence = list(set(existing_evidence + evidence))
            self.edges_col.update_one(
                {"_id": existing["_id"]},
                {
                    "$set": {
                        "confidence": new_conf,
                        "evidence": merged_evidence,
                        "last_updated": now,
                    }
                },
            )
        else:
            edge = GraphEdge(
                source=src_id,
                target=tgt_id,
                relationship_type=relationship_type,
                confidence=confidence,
                evidence=evidence,
            )
            data = edge.model_dump()
            data["last_updated"] = now
            self.edges_col.insert_one(data)

            # Increment connection count on both nodes
            self.nodes_col.update_many(
                {"id": {"$in": [src_id, tgt_id]}},
                {"$inc": {"connection_count": 1}},
            )

    def merge_customers(self, from_customer_id: str, to_customer_id: str) -> None:
        """Merge: all nodes in from_customer_id become to_customer_id."""
        if self.db is None:
            return
        if from_customer_id == to_customer_id:
            return
        self.nodes_col.update_many(
            {"customer_id": from_customer_id},
            {"$set": {"customer_id": to_customer_id}},
        )

    def get_cluster_identifiers(self, customer_id: str) -> dict[str, str]:
        """Return all unique identity nodes belonging to a resolved customer ID."""
        if self.db is None:
            return {}
        cluster_dict = {}
        docs = self.nodes_col.find({"customer_id": customer_id})
        for doc in docs:
            cluster_dict[doc["id_type"]] = doc["id_value"]
        return cluster_dict

    def get_all_graph_data(self) -> dict:
        """Helper for full-graph visualization."""
        if self.db is None:
            return {"nodes": [], "edges": []}

        def _iso(val):
            return val.isoformat() if hasattr(val, "isoformat") else val

        nodes = []
        for doc in self.nodes_col.find():
            nodes.append(
                {
                    "id": doc["id"],
                    "type": "identityNode",
                    "data": {
                        "id_type": doc["id_type"],
                        "id_value": doc["id_value"],
                        "customer_id": doc.get("customer_id", ""),
                        "first_seen": _iso(doc.get("first_seen", "")),
                        "last_seen": _iso(doc.get("last_seen", "")),
                        "event_count": doc.get("event_count", 1),
                        "connection_count": doc.get("connection_count", 0),
                        "is_trusted": doc["id_type"]
                        in ("email", "phone_number", "customer_id", "card_last4"),
                    },
                }
            )

        edges = []
        for doc in self.edges_col.find():
            edges.append(
                {
                    "id": str(doc["_id"]),
                    "source": doc["source"],
                    "target": doc["target"],
                    "type": "identityEdge",
                    "animated": doc["confidence"] < 1.0,
                    "data": {
                        "confidence": doc["confidence"],
                        "relationship_type": doc.get("relationship_type", "CONNECTED_TO"),
                        "evidence": doc.get("evidence", []),
                        "created_at": _iso(doc.get("created_at", "")),
                        "last_updated": _iso(doc.get("last_updated", "")),
                    },
                }
            )

        return {"nodes": nodes, "edges": edges}
