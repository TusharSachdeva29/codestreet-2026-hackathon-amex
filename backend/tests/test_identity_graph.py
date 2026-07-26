import pytest
from app.identity.graph import IdentityGraph
from app.identity.models import IdentityNode


def test_add_single_identifier():
    graph = IdentityGraph()
    node = IdentityNode(id_type="email", id_value="test@example.com")
    customer_id = graph.add_identifiers([node])
    
    assert customer_id is not None
    assert isinstance(customer_id, str)
    
    # Should resolve to the same customer id on repeat
    customer_id_2 = graph.add_identifiers([node])
    assert customer_id == customer_id_2


def test_merge_identifiers():
    graph = IdentityGraph()
    node1 = IdentityNode(id_type="email", id_value="john@example.com")
    node2 = IdentityNode(id_type="device_id", id_value="dev_123")
    
    # Event 1: Email + Device
    customer_id_1 = graph.add_identifiers([node1, node2])
    
    # Event 2: Device + Phone
    node3 = IdentityNode(id_type="phone_number", id_value="1234567890")
    customer_id_2 = graph.add_identifiers([node2, node3])
    
    # The components should have merged
    assert customer_id_1 == customer_id_2
    
    # Check cluster identifiers
    cluster = graph.get_cluster_identifiers(customer_id_1)
    assert cluster.get("email") == "john@example.com"
    assert cluster.get("device_id") == "dev_123"
    assert cluster.get("phone_number") == "1234567890"


def test_merge_existing_components():
    graph = IdentityGraph()
    node_email = IdentityNode(id_type="email", id_value="alice@example.com")
    node_phone = IdentityNode(id_type="phone_number", id_value="99999999")
    node_device = IdentityNode(id_type="device_id", id_value="dev_999")

    # Component A: Alice's email
    cid_a = graph.add_identifiers([node_email])
    
    # Component B: Alice's phone + device
    cid_b = graph.add_identifiers([node_phone, node_device])
    
    # Initially disjoint
    assert cid_a != cid_b
    
    # Bridge event: Alice logs in with her device (Email + Device)
    cid_merged = graph.add_identifiers([node_email, node_device])
    
    # The IDs should now resolve to the SAME root component
    # Specifically, it will be either cid_a or cid_b depending on union logic
    assert cid_merged in (cid_a, cid_b)
    
    # The cluster should contain all three identifiers
    cluster = graph.get_cluster_identifiers(cid_merged)
    assert "email" in cluster
    assert "phone_number" in cluster
    assert "device_id" in cluster
