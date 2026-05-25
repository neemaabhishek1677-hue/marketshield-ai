"""NetworkX-based insider trading graph analysis."""

from __future__ import annotations

import json
from dataclasses import dataclass

import networkx as nx


@dataclass
class GraphMetrics:
    degree_centrality: dict[str, float]
    cluster_score: float
    event_coordination_score: float
    insider_proximity_score: float
    suspicious_nodes: list[str]


@dataclass
class GraphVisualization:
    nodes: list[dict]
    edges: list[dict]
    metrics: GraphMetrics


class InsiderGraphAnalyzer:
    def build_from_records(self, nodes: list[dict], edges: list[dict]) -> nx.Graph:
        G = nx.Graph()
        for n in nodes:
            G.add_node(n["node_id"], **n)
        for e in edges:
            G.add_edge(e["source_id"], e["target_id"], edge_type=e["edge_type"], weight=e.get("weight", 1.0))
        return G

    def analyze(self, nodes: list[dict], edges: list[dict], event_active_traders: set[str]) -> GraphVisualization:
        G = self.build_from_records(nodes, edges)
        if G.number_of_nodes() == 0:
            empty = GraphMetrics({}, 0.0, 0.0, 0.0, [])
            return GraphVisualization(nodes=[], edges=[], metrics=empty)

        centrality = nx.degree_centrality(G)
        suspicious = [
            n
            for n, d in G.nodes(data=True)
            if d.get("node_type") == "trader" and centrality.get(n, 0) > 0.35
        ]

        sub_edges = [e for e in edges if e.get("is_suspicious")]
        cluster_score = min(1.0, len(sub_edges) / max(len(edges), 1) * 1.5)

        event_nodes = {n for n in event_active_traders if n in G}
        coord = 0.0
        for a in event_nodes:
            for b in event_nodes:
                if a != b and G.has_edge(a, b):
                    coord += G[a][b].get("weight", 1.0)
        event_coordination_score = min(1.0, coord / 5.0)

        insider_nodes = [n for n, d in G.nodes(data=True) if d.get("node_type") == "insider"]
        proximity = 0.0
        for ins in insider_nodes:
            for tr in event_nodes:
                if G.has_edge(ins, tr):
                    try:
                        proximity = max(proximity, 1.0 - (nx.shortest_path_length(G, ins, tr) - 1) * 0.3)
                    except nx.NetworkXNoPath:
                        pass
        insider_proximity_score = min(1.0, proximity + cluster_score * 0.3)

        metrics = GraphMetrics(
            degree_centrality={k: round(v, 4) for k, v in list(centrality.items())[:20]},
            cluster_score=round(cluster_score, 4),
            event_coordination_score=round(event_coordination_score, 4),
            insider_proximity_score=round(insider_proximity_score, 4),
            suspicious_nodes=suspicious[:10],
        )

        vis_nodes = [
            {
                "id": n["node_id"],
                "label": n.get("label", n["node_id"]),
                "type": n.get("node_type", "unknown"),
                "centrality": round(centrality.get(n["node_id"], 0), 4),
            }
            for n in nodes
        ]
        vis_edges = [
            {
                "source": e["source_id"],
                "target": e["target_id"],
                "type": e["edge_type"],
                "suspicious": e.get("is_suspicious", False),
            }
            for e in edges
        ]
        return GraphVisualization(nodes=vis_nodes, edges=vis_edges, metrics=metrics)

    def metrics_to_json(self, metrics: GraphMetrics) -> str:
        return json.dumps(
            {
                "cluster_score": metrics.cluster_score,
                "event_coordination_score": metrics.event_coordination_score,
                "insider_proximity_score": metrics.insider_proximity_score,
                "suspicious_nodes": metrics.suspicious_nodes,
            }
        )
