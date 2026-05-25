"""Hybrid anomaly detection: rules + Isolation Forest."""

from __future__ import annotations

import json
from dataclasses import dataclass

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from app.ml.features import FEATURE_NAMES


@dataclass
class AnomalyResult:
    anomaly_score: float
    severity: str
    is_anomaly: bool
    top_drivers: list[dict]
    explanation: str


class AnomalyEngine:
    def __init__(self):
        self.model = IsolationForest(n_estimators=100, contamination=0.08, random_state=42)
        self.scaler = StandardScaler()
        self._fitted = False

    def fit(self, X: np.ndarray) -> dict:
        if len(X) < 10:
            return {"status": "skipped", "reason": "insufficient_samples"}
        Xs = self.scaler.fit_transform(X)
        self.model.fit(Xs)
        self._fitted = True
        preds = self.model.predict(Xs)
        labels = (X[:, 0] > 2) | (X[:, 4] > 3) | (X[:, 5] > 5)
        if labels.sum() > 0:
            acc = float(((preds == -1) == labels).mean())
        else:
            acc = float((preds == -1).mean())
        return {"status": "ok", "samples": len(X), "pseudo_accuracy": round(acc, 3)}

    def predict_one(self, x: np.ndarray) -> AnomalyResult:
        rule_score = self._rule_score(x)
        if self._fitted:
            xs = self.scaler.transform(x.reshape(1, -1))
            raw = -self.model.decision_function(xs)[0]
            ml_score = float(1 / (1 + np.exp(-raw)))
        else:
            ml_score = rule_score

        combined = 0.55 * ml_score + 0.45 * rule_score
        severity = self._severity(combined)
        drivers = self._top_drivers(x, combined)
        explanation = self._explain(drivers, combined)
        return AnomalyResult(
            anomaly_score=round(combined, 4),
            severity=severity,
            is_anomaly=combined >= 0.55,
            top_drivers=drivers,
            explanation=explanation,
        )

    def _rule_score(self, x: np.ndarray) -> float:
        signals = [
            min(x[0] / 3.0, 1.0),
            min(x[4] / 5.0, 1.0),
            min(x[5] / 8.0, 1.0),
            min(x[6] / 2.0, 1.0),
            min(abs(x[10]) / 0.15, 1.0),
        ]
        return float(np.mean(signals))

    def _severity(self, score: float) -> str:
        if score >= 0.85:
            return "critical"
        if score >= 0.7:
            return "high"
        if score >= 0.55:
            return "medium"
        return "low"

    def _top_drivers(self, x: np.ndarray, score: float) -> list[dict]:
        contrib = x * np.array([0.15, 0.05, 0.08, 0.1, 0.18, 0.14, 0.12, 0.05, 0.04, 0.04, 0.1, 0.05])
        order = np.argsort(-np.abs(contrib))[:4]
        desc_map = {
            "trade_size_ratio": "Trade size vs historical baseline",
            "intraday_volume_spike": "Intraday volume spike",
            "cancel_to_fill_ratio": "Order cancel-to-fill ratio",
            "account_coordination_score": "Coordinated account activity",
            "price_acceleration_score": "Price acceleration",
            "event_window_distance": "Proximity to corporate event",
        }
        drivers = []
        for i in order:
            name = FEATURE_NAMES[i]
            drivers.append(
                {
                    "feature": name,
                    "contribution": round(float(contrib[i]), 4),
                    "description": desc_map.get(name, name.replace("_", " ").title()),
                }
            )
        return drivers

    def _explain(self, drivers: list[dict], score: float) -> str:
        parts = [f"{d['description']} (weight {d['contribution']:.2f})" for d in drivers[:3]]
        return (
            f"Surveillance signal score {score:.2f}: elevated due to "
            + "; ".join(parts)
            + ". This is an investigative signal, not a legal determination."
        )

    def drivers_to_json(self, drivers: list[dict]) -> str:
        return json.dumps(drivers)
