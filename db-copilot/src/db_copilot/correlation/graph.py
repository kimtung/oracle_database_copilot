from __future__ import annotations

from collections import deque
from typing import Any

from pydantic import BaseModel, Field

from db_copilot.domain.enums import EvidenceType
from db_copilot.domain.models.evidence import Evidence


class GraphNode(BaseModel):
    """Node in the Evidence Correlation Graph."""

    id: str
    entity_type: str  # "SQL", "SESSION", "PLAN", "TABLE", "PROCEDURE", "JOB", "TABLESPACE"
    entity_id: str
    evidences: list[Evidence] = Field(default_factory=list)
    properties: dict[str, Any] = Field(default_factory=dict)


class GraphEdge(BaseModel):
    """Directed edge in the Evidence Correlation Graph."""

    source: str
    target: str
    relation: str  # "BLOCKS", "HAS_PLAN", "EXECUTES", "ACCESSES", "CALLS", "CAUSES"
    weight: float = 1.0
    data: dict[str, Any] = Field(default_factory=dict)


class EvidenceGraph:
    """
    Evidence Correlation Graph representing entities, their interactions,
    and causal dependency chains.
    """

    def __init__(self):
        self.nodes: dict[str, GraphNode] = {}
        self.adjacency: dict[str, list[GraphEdge]] = {}
        self.reverse_adjacency: dict[str, list[GraphEdge]] = {}

    def add_node(self, node: GraphNode) -> GraphNode:
        if node.id not in self.nodes:
            self.nodes[node.id] = node
            self.adjacency[node.id] = []
            self.reverse_adjacency[node.id] = []
        else:
            # Merge evidences and properties
            existing = self.nodes[node.id]
            for ev in node.evidences:
                if not any(e.id == ev.id for e in existing.evidences):
                    existing.evidences.append(ev)
            existing.properties.update(node.properties)
        return self.nodes[node.id]

    def get_or_create_node(
        self,
        entity_type: str,
        entity_id: str,
        evidence: Evidence | None = None,
        properties: dict[str, Any] | None = None,
    ) -> GraphNode:
        node_id = f"{entity_type}:{entity_id}"
        ev_list = [evidence] if evidence else []
        node = GraphNode(
            id=node_id,
            entity_type=entity_type,
            entity_id=entity_id,
            evidences=ev_list,
            properties=properties or {},
        )
        return self.add_node(node)

    def add_edge(self, edge: GraphEdge) -> None:
        if edge.source not in self.adjacency:
            self.adjacency[edge.source] = []
        if edge.target not in self.reverse_adjacency:
            self.reverse_adjacency[edge.target] = []

        # Avoid duplicate edges
        for existing in self.adjacency[edge.source]:
            if existing.target == edge.target and existing.relation == edge.relation:
                existing.weight = max(existing.weight, edge.weight)
                existing.data.update(edge.data)
                return

        self.adjacency[edge.source].append(edge)
        self.reverse_adjacency[edge.target].append(edge)

    def link(
        self,
        source_id: str,
        target_id: str,
        relation: str,
        weight: float = 1.0,
        data: dict[str, Any] | None = None,
    ) -> None:
        edge = GraphEdge(
            source=source_id,
            target=target_id,
            relation=relation,
            weight=weight,
            data=data or {},
        )
        self.add_edge(edge)

    @classmethod
    def build_from_evidences(cls, evidences: list[Evidence]) -> EvidenceGraph:
        """Construct a graph automatically from a collection of evidence objects."""
        graph = cls()

        for ev in evidences:
            entity_type = ev.entity_type or "UNKNOWN"
            entity_id = ev.entity_id or str(ev.id)
            main_node = graph.get_or_create_node(entity_type, entity_id, evidence=ev)

            # 1. Blocking session chains
            if ev.type == EvidenceType.BLOCKING_SESSION:
                blocker_sid = str(ev.data.get("blocker_sid", entity_id))
                blocker_node = graph.get_or_create_node(
                    "SESSION", blocker_sid, evidence=ev, properties=ev.data
                )

                # Link blocker to SQL if available
                blocker_sql = ev.data.get("blocker_sql_id")
                if blocker_sql:
                    sql_node = graph.get_or_create_node("SQL", str(blocker_sql))
                    graph.link(blocker_node.id, sql_node.id, "EXECUTES")

                # Link blocker to all blocked sessions
                blocked_list = ev.data.get("blocked_sessions", [])
                for b in blocked_list:
                    b_sid = str(b.get("sid") if isinstance(b, dict) else b)
                    blocked_node = graph.get_or_create_node("SESSION", b_sid)
                    graph.link(
                        blocker_node.id,
                        blocked_node.id,
                        "BLOCKS",
                        data={"wait_event": ev.data.get("wait_event")},
                    )

            # 2. SQL regression & plan changes
            elif ev.type in [EvidenceType.SQL_REGRESSION, EvidenceType.SQL_PLAN_CHANGE]:
                plans = ev.data.get("plans", [])
                for p in plans:
                    plan_node = graph.get_or_create_node("PLAN", str(p))
                    graph.link(main_node.id, plan_node.id, "HAS_PLAN")

            # 3. Long running sessions
            elif ev.type == EvidenceType.LONG_RUNNING_SESSION:
                sql_id = ev.data.get("sql_id")
                if sql_id:
                    sql_node = graph.get_or_create_node("SQL", str(sql_id))
                    graph.link(main_node.id, sql_node.id, "EXECUTES")

        return graph

    def find_root_causes(self) -> list[GraphNode]:
        """
        Identify potential root cause nodes:
        Nodes that have outgoing influence (out-degree > 0)
        but no incoming blockers (in-degree == 0),
        or specific standalone root types (TABLESPACE, JOB_FAILURE).
        """
        root_causes: list[GraphNode] = []

        for node_id, node in self.nodes.items():
            in_edges = self.reverse_adjacency.get(node_id, [])
            out_edges = self.adjacency.get(node_id, [])

            # Case A: Root Blocker session (has outgoing BLOCKS edges, no incoming BLOCKS edges)
            has_incoming_block = any(e.relation == "BLOCKS" for e in in_edges)
            has_outgoing_block = any(e.relation == "BLOCKS" for e in out_edges)
            if has_outgoing_block and not has_incoming_block:
                root_causes.append(node)
                continue

            # Case B: Root resource exhaustion or job failure
            if node.entity_type in ["TABLESPACE", "JOB"]:
                root_causes.append(node)
                continue

            # Case C: SQL with plan changes
            if node.entity_type == "SQL" and any(e.relation == "HAS_PLAN" for e in out_edges):
                root_causes.append(node)
                continue

        # Fallback: if no root causes identified, return all nodes with in_degree == 0
        if not root_causes:
            for node_id, node in self.nodes.items():
                if len(self.reverse_adjacency.get(node_id, [])) == 0:
                    root_causes.append(node)

        return root_causes

    def find_causal_chains(self) -> list[list[GraphNode]]:
        """
        Traverse the graph via BFS starting from root cause nodes to discover
        complete causal impact paths.
        """
        roots = self.find_root_causes()
        chains: list[list[GraphNode]] = []

        for root in roots:
            queue: deque[list[GraphNode]] = deque([[root]])
            visited_paths: set[str] = set()

            while queue:
                current_path = queue.popleft()
                last_node = current_path[-1]

                out_edges = self.adjacency.get(last_node.id, [])
                if not out_edges:
                    # End of a causal chain
                    if len(current_path) > 1 or len(roots) == len(self.nodes):
                        path_key = "->".join(n.id for n in current_path)
                        if path_key not in visited_paths:
                            visited_paths.add(path_key)
                            chains.append(current_path)
                    continue

                for edge in out_edges:
                    next_node = self.nodes.get(edge.target)
                    if next_node and next_node not in current_path:  # Prevent cycles
                        queue.append(current_path + [next_node])

        return chains
