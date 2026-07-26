"""Identity Resolution Engine (Phase 4 Enhanced) with Deterministic and Probabilistic Matching."""

import uuid
import logging
import difflib
from collections import defaultdict
from app.normalization.models import CanonicalEvent
from app.identity.models import IdentityNode, ResolvedCustomerEvent
from app.identity.graph import IdentityGraph

logger = logging.getLogger("app.identity.engine")

# Configurable Weights for Probabilistic Signals
WEIGHTS = {
    "cookie_id": 0.4,
    "device_id": 0.4,
    "browser_fingerprint": 0.3,
    "ip_address": 0.2,
}

# Thresholds
MERGE_THRESHOLD = 0.95
PROBABILISTIC_MERGE_THRESHOLD = 0.75

# Highly trusted identifiers that trigger deterministic matches
TRUSTED_IDENTIFIERS = {"email", "phone_number", "card_number", "customer_id"}


class IdentityResolutionEngine:
    """
    Orchestrates the resolution of an incoming event into a specific customer identity
    using both Deterministic and Probabilistic matching.
    """

    def __init__(self, graph: IdentityGraph) -> None:
        self.graph = graph

    def resolve(self, canonical: CanonicalEvent) -> ResolvedCustomerEvent:
        nodes: list[IdentityNode] = []
        
        # 1. Extract non-null identifiers
        identity_data = canonical.identity.model_dump(exclude_none=True)
        for id_type, id_value in identity_data.items():
            if id_value and str(id_value).strip():
                nodes.append(IdentityNode(id_type=id_type, id_value=str(id_value).strip()))

        if not nodes:
            # Anonymous event, no identifiers
            new_customer_id = str(uuid.uuid4())
            return self._build_resolved_event(canonical, new_customer_id, 1.0, [])

        # 2. Check for Deterministic Matches
        # If any trusted identifier exactly matches a known node, we deterministically merge.
        trusted_nodes = [n for n in nodes if n.id_type in TRUSTED_IDENTIFIERS]
        deterministic_customer_ids = set()
        
        for n in trusted_nodes:
            g_node = self.graph.get_node(n)
            if g_node:
                deterministic_customer_ids.add(g_node.customer_id)

        if deterministic_customer_ids:
            # We found deterministic links! Merge all these customer graphs together.
            primary_customer = list(deterministic_customer_ids)[0]
            for other_cust in list(deterministic_customer_ids)[1:]:
                self.graph.merge_customers(other_cust, primary_customer)
                
            # Upsert all incoming nodes to this primary customer
            for n in nodes:
                self.graph.upsert_node(n, primary_customer)
                # Add deterministic edges between the first node and others
                if n != nodes[0]:
                    self.graph.add_edge(nodes[0], n, confidence=1.0, evidence=["Deterministic Match"])
                    
            explanation = ["Deterministic Match via Trusted Identifier(s)"]
            return self._build_resolved_event(canonical, primary_customer, 1.0, explanation)

        # 3. Candidate Search & Probabilistic Matching
        # No exact trusted match. Let's find candidates via probabilistic signals or fuzzy matching.
        candidates = defaultdict(float)  # customer_id -> score
        evidence_map = defaultdict(list) # customer_id -> list of evidence strings
        
        # A. Fuzzy search on trusted identifiers (e.g. misspelled email)
        for n in trusted_nodes:
            existing_nodes = self.graph.get_nodes_by_type(n.id_type)
            for e_node in existing_nodes:
                ratio = difflib.SequenceMatcher(None, e_node.id_value.lower(), n.id_value.lower()).ratio()
                if ratio >= 0.85:
                    candidates[e_node.customer_id] += ratio
                    evidence_map[e_node.customer_id].append(f"Fuzzy {n.id_type} Match (+{ratio:.2f})")

        # B. Exact match on low-trust identifiers (Cookie, IP, Device)
        untrusted_nodes = [n for n in nodes if n.id_type not in TRUSTED_IDENTIFIERS]
        for n in untrusted_nodes:
            g_node = self.graph.get_node(n)
            if g_node:
                weight = WEIGHTS.get(n.id_type, 0.1)
                candidates[g_node.customer_id] += weight
                evidence_map[g_node.customer_id].append(f"Exact {n.id_type} Match (+{weight})")
                
        # 4. Identity Decision Engine
        best_candidate = None
        best_score = 0.0
        for cid, score in candidates.items():
            if score > best_score:
                best_score = score
                best_candidate = cid

        if best_candidate and best_score >= PROBABILISTIC_MERGE_THRESHOLD:
            # We have a probabilistic merge!
            # Cap confidence at 0.99 for probabilistic
            final_confidence = min(best_score, 0.99)
            
            for n in nodes:
                self.graph.upsert_node(n, best_candidate)
                if n != nodes[0]:
                    self.graph.add_edge(nodes[0], n, confidence=final_confidence, evidence=evidence_map[best_candidate])
                    
            return self._build_resolved_event(canonical, best_candidate, final_confidence, evidence_map[best_candidate])

        # 5. Fallback: Create New Customer
        new_customer_id = str(uuid.uuid4())
        for n in nodes:
            self.graph.upsert_node(n, new_customer_id)
            if n != nodes[0]:
                self.graph.add_edge(nodes[0], n, confidence=1.0, evidence=["New Customer Creation"])
                
        return self._build_resolved_event(canonical, new_customer_id, 1.0, ["Created New Customer (No strong candidates)"])

    def _build_resolved_event(self, canonical: CanonicalEvent, customer_id: str, confidence: float, explanation: list[str]) -> ResolvedCustomerEvent:
        linked_identifiers = self.graph.get_cluster_identifiers(customer_id)
        return ResolvedCustomerEvent(
            canonical_event=canonical,
            resolved_customer_id=customer_id,
            confidence_score=confidence,
            linked_identifiers=linked_identifiers,
            explanation=explanation
        )
