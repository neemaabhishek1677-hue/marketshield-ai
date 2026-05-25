"""Unified manipulation risk scoring."""

from __future__ import annotations

import json
from dataclasses import dataclass


@dataclass
class FusionResult:
    unified_score: float
    severity: str
    components: dict
    explanation: str
    suggested_action: str


class RiskFusionEngine:
    WEIGHTS = {
        "trade_anomaly": 0.28,
        "sentiment": 0.15,
        "social_hype": 0.17,
        "graph": 0.2,
        "pump_dump": 0.12,
        "event_proximity": 0.08,
    }

    def fuse(
        self,
        trade_anomaly: float,
        sentiment: float,
        social_hype: float,
        graph: float,
        pump_dump: float,
        event_proximity: float,
    ) -> FusionResult:
        components = {
            "trade_anomaly": trade_anomaly,
            "sentiment": sentiment,
            "social_hype": social_hype,
            "graph": graph,
            "pump_dump": pump_dump,
            "event_proximity": event_proximity,
        }
        unified = (
            self.WEIGHTS["trade_anomaly"] * trade_anomaly
            + self.WEIGHTS["sentiment"] * sentiment
            + self.WEIGHTS["social_hype"] * social_hype
            + self.WEIGHTS["graph"] * graph
            + self.WEIGHTS["pump_dump"] * pump_dump
            + self.WEIGHTS["event_proximity"] * event_proximity
        )
        unified = min(1.0, max(0.0, unified))

        if unified >= 0.8:
            severity, action = "critical", "escalate"
        elif unified >= 0.65:
            severity, action = "high", "under_review"
        elif unified >= 0.45:
            severity, action = "medium", "monitor"
        else:
            severity, action = "low", "watchlist"

        top = sorted(components.items(), key=lambda x: -x[1] * self.WEIGHTS.get(x[0].replace("_score", ""), 0.1))[:3]
        explanation = (
            f"Unified risk {unified:.2f} driven mainly by {top[0][0]} ({top[0][1]:.2f}), "
            f"{top[1][0]} ({top[1][1]:.2f}), and {top[2][0]} ({top[2][1]:.2f}). "
            "Surveillance fusion output for compliance review."
        )
        return FusionResult(
            unified_score=round(unified, 4),
            severity=severity,
            components=components,
            explanation=explanation,
            suggested_action=action,
        )

    def to_json(self, components: dict) -> str:
        return json.dumps(components)
