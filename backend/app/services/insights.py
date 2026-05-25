"""Human-language investor/analyst insight cards."""

from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import Alert, RiskScore, Stock, Trader


class InsightsService:
    async def stock_insight(self, db: AsyncSession, stock: Stock) -> dict:
        risk = (
            await db.execute(
                select(RiskScore).where(RiskScore.stock_id == stock.id).order_by(RiskScore.unified_score.desc()).limit(1)
            )
        ).scalar_one_or_none()
        alerts = (
            await db.execute(select(Alert).where(Alert.stock_id == stock.id).order_by(Alert.created_at.desc()).limit(5))
        ).scalars().all()

        components = json.loads(risk.explainability_json) if risk else {}
        return {
            "ticker": stock.ticker,
            "summary": f"{stock.ticker} shows elevated surveillance risk in {stock.sector}.",
            "why_risky": [
                f"Unified risk score {risk.unified_score:.2f}" if risk else "Limited risk history",
                f"{len(alerts)} active surveillance alerts",
                f"Pump-and-dump component {risk.pump_dump_score:.2f}" if risk else "Pump signal pending",
            ],
            "suggested_actions": ["monitor", "review order book", "escalate if social burst continues"],
            "alerts": [{"id": a.id, "title": a.title, "severity": a.severity} for a in alerts],
            "components": components,
            "disclaimer": "Synthetic demo — not a legal or trading recommendation.",
        }

    async def trader_insight(self, db: AsyncSession, trader: Trader) -> dict:
        risk = (
            await db.execute(
                select(RiskScore).where(RiskScore.trader_id == trader.id).order_by(RiskScore.unified_score.desc()).limit(1)
            )
        ).scalar_one_or_none()
        alerts = (
            await db.execute(select(Alert).where(Alert.trader_id == trader.id).order_by(Alert.created_at.desc()).limit(5))
        ).scalars().all()

        links = []
        if trader.is_insider_linked:
            links.append("Insider-profile linkage detected")
        if trader.device_hash and "cluster" in trader.device_hash:
            links.append("Shared device cluster with coordinated accounts")

        return {
            "trader_id": trader.external_id,
            "summary": f"Trader {trader.external_id} flagged for cross-signal review.",
            "why_flagged": links or ["Trade anomaly score above baseline"],
            "interaction": "Sentiment and graph signals reinforce trade anomaly patterns around corporate events.",
            "suggested_actions": ["under_review", "request KYC refresh", "monitor linked accounts"],
            "alerts": [{"id": a.id, "title": a.title} for a in alerts],
            "risk_score": risk.unified_score if risk else 0.0,
            "disclaimer": "Investigative signal only.",
        }
