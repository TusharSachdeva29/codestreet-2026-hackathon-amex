"""Identity Resolution Engine to attach canonical events to specific customers."""

import logging
from app.normalization.models import CanonicalEvent
from app.identity.models import IdentityNode, ResolvedCustomerEvent
from app.identity.graph import IdentityGraph

logger = logging.getLogger("app.identity.engine")

class IdentityResolutionEngine:
    """
    Orchestrates the resolution of an incoming event into a specific customer identity.
    """

    def __init__(self, graph: IdentityGraph) -> None:
        self.graph = graph

    def resolve(self, canonical: CanonicalEvent) -> ResolvedCustomerEvent:
        """
        Extract identifiers from the canonical event, update the graph,
        and return the fully resolved event.
        """
        nodes: list[IdentityNode] = []
        
        # 1. Extract non-null identifiers from the canonical identity block
        identity_data = canonical.identity.model_dump(exclude_none=True)
        for id_type, id_value in identity_data.items():
            # We skip empty strings as well
            if id_value and str(id_value).strip():
                nodes.append(IdentityNode(id_type=id_type, id_value=str(id_value).strip()))

        # 2. Update the graph and retrieve the unified customer ID
        resolved_customer_id = self.graph.add_identifiers(nodes)

        # 3. Retrieve all linked identifiers for this customer
        linked_identifiers = self.graph.get_cluster_identifiers(resolved_customer_id)

        # 4. Construct the resolved event (assuming deterministic resolution -> confidence 1.0)
        resolved_event = ResolvedCustomerEvent(
            canonical_event=canonical,
            resolved_customer_id=resolved_customer_id,
            confidence_score=1.0,
            linked_identifiers=linked_identifiers,
        )

        return resolved_event
