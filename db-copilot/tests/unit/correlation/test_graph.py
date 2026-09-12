from db_copilot.correlation.graph import EvidenceGraph, GraphEdge, GraphNode
from db_copilot.domain.enums import EvidenceType, Severity
from db_copilot.domain.models.evidence import Evidence


def test_graph_node_and_edge_creation():
    graph = EvidenceGraph()
    n1 = GraphNode(id="SESSION:101", entity_type="SESSION", entity_id="101")
    n2 = GraphNode(id="SESSION:201", entity_type="SESSION", entity_id="201")
    graph.add_node(n1)
    graph.add_node(n2)

    edge = GraphEdge(source="SESSION:101", target="SESSION:201", relation="BLOCKS")
    graph.add_edge(edge)

    assert "SESSION:101" in graph.nodes
    assert len(graph.adjacency["SESSION:101"]) == 1
    assert len(graph.reverse_adjacency["SESSION:201"]) == 1


def test_build_from_evidences_blocking_chain():
    ev_block = Evidence(
        type=EvidenceType.BLOCKING_SESSION,
        entity_type="SESSION",
        entity_id="101",
        severity=Severity.HIGH,
        data={
            "blocker_sid": 101,
            "blocker_sql_id": "sql_blocker_1",
            "blocked_sessions": [{"sid": 201}, {"sid": 202}],
            "wait_event": "enq: TX - row lock contention",
        },
    )

    graph = EvidenceGraph.build_from_evidences([ev_block])

    assert "SESSION:101" in graph.nodes
    assert "SESSION:201" in graph.nodes
    assert "SESSION:202" in graph.nodes
    assert "SQL:sql_blocker_1" in graph.nodes

    # Check root causes
    root_causes = graph.find_root_causes()
    root_ids = [r.id for r in root_causes]
    assert "SESSION:101" in root_ids
    assert "SESSION:201" not in root_ids

    # Check causal chains
    chains = graph.find_causal_chains()
    chain_representations = [" -> ".join(n.id for n in c) for c in chains]
    assert any("SESSION:101 -> SESSION:201" in rep for rep in chain_representations)
    assert any("SESSION:101 -> SESSION:202" in rep for rep in chain_representations)
    assert any("SESSION:101 -> SQL:sql_blocker_1" in rep for rep in chain_representations)


def test_build_from_evidences_sql_plan_change():
    ev_plan = Evidence(
        type=EvidenceType.SQL_PLAN_CHANGE,
        entity_type="SQL",
        entity_id="sql_bad_plan",
        severity=Severity.HIGH,
        data={"plans": [123456, 789012]},
    )

    graph = EvidenceGraph.build_from_evidences([ev_plan])

    assert "SQL:sql_bad_plan" in graph.nodes
    assert "PLAN:123456" in graph.nodes
    assert "PLAN:789012" in graph.nodes

    roots = graph.find_root_causes()
    assert len(roots) == 1
    assert roots[0].id == "SQL:sql_bad_plan"

    chains = graph.find_causal_chains()
    assert len(chains) == 2
