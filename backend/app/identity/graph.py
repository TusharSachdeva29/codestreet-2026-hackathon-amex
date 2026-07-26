"""In-memory Identity Graph using Union-Find (Disjoint Set) for deterministic resolution."""

import uuid
from typing import Optional
from app.identity.models import IdentityNode


class IdentityGraph:
    """
    Maintains an in-memory graph of identifier relationships.
    Uses a Union-Find algorithm to efficiently merge identifier clusters.
    """

    def __init__(self) -> None:
        # parent[node] = parent_node
        self._parent: dict[IdentityNode, IdentityNode] = {}
        # cluster_id[root_node] = customer_id (UUID string)
        self._cluster_id: dict[IdentityNode, str] = {}
        # Allows reverse lookup to find all nodes in a cluster
        self._nodes: set[IdentityNode] = set()

    def _find(self, node: IdentityNode) -> IdentityNode:
        """Find the root of the connected component, with path compression."""
        if node not in self._parent:
            self._parent[node] = node
            self._cluster_id[node] = str(uuid.uuid4())
            self._nodes.add(node)
            return node

        if self._parent[node] == node:
            return node

        self._parent[node] = self._find(self._parent[node])
        return self._parent[node]

    def _union(self, node1: IdentityNode, node2: IdentityNode) -> None:
        """Merge two connected components."""
        root1 = self._find(node1)
        root2 = self._find(node2)

        if root1 != root2:
            # For simplicity, make root1 the parent of root2
            self._parent[root2] = root1
            # We can discard root2's cluster_id, root1's takes over.

    def add_identifiers(self, nodes: list[IdentityNode]) -> str:
        """
        Add a list of co-occurring identifiers to the graph.
        Returns the resolved customer ID (cluster ID) for this group.
        """
        if not nodes:
            # If an event has no identifiers at all, generate an anonymous customer ID
            return str(uuid.uuid4())

        # Link all nodes in the list together
        first_node = nodes[0]
        for i in range(1, len(nodes)):
            self._union(first_node, nodes[i])

        # The resolved customer ID is the ID of the root component
        root = self._find(first_node)
        return self._cluster_id[root]

    def get_cluster_identifiers(self, customer_id: str) -> dict[str, str]:
        """
        Return all identity nodes belonging to a given resolved customer ID.
        This provides the full context of a user's identifiers.
        """
        cluster_dict = {}
        # Re-evaluating find for all nodes might be necessary if paths aren't fully compressed,
        # but iterating the set and checking the root works.
        for node in self._nodes:
            if self._cluster_id.get(self._find(node)) == customer_id:
                # We can store multiple of the same type? 
                # For simplicity, we just keep the last one if there are duplicates of the same type,
                # though a real system might want a list per type.
                cluster_dict[node.id_type] = node.id_value
        return cluster_dict
