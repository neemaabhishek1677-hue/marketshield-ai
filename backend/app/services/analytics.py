"""Dashboard and analytics query services."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import Alert, RiskScore, Stock, Trader
from app.schemas.dashboard import (
    DashboardOverview,
    HeatmapCell,
    KPICard,
    MarketHeatmapResponse,
    RiskTickerRow,
    TraderRiskRow,
    TimeSeriesPoint,
)


DISCLAIMER = (
    "MarketShield AI outputs are surveillance signals based on synthetic demo data. "
    "They are not legal conclusions or investment advice."
)


class AnalyticsService:
    async def dashboard_overview(self, db: AsyncSession) -> DashboardOverview:
        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

        alert_count = (await db.execute(select(func.count(Alert.id)))).scalar() or 0
        alerts_today = (
            await db.execute(select(func.count(Alert.id)).where(Alert.created_at >= today))
        ).scalar() or 0

        risk_rows = (
            await db.execute(
                select(RiskScore, Stock)
                .join(Stock, RiskScore.stock_id == Stock.id)
                .where(RiskScore.stock_id.isnot(None))
                .order_by(RiskScore.unified_score.desc())
                .limit(8)
            )
        ).all()

        top_tickers = []
        for risk, stock in risk_rows:
            ac = (
                await db.execute(
                    select(func.count(Alert.id)).where(Alert.stock_id == stock.id)
                )
            ).scalar() or 0
            pump = "elevated" if risk.pump_dump_score > 0.55 else "watchlist" if risk.pump_dump_score > 0.35 else "low"
            top_tickers.append(
                RiskTickerRow(
                    ticker=stock.ticker,
                    name=stock.name,
                    sector=stock.sector,
                    unified_score=risk.unified_score,
                    pump_risk=pump,
                    alert_count=ac,
                )
            )

        trader_risks = (
            await db.execute(
                select(RiskScore, Trader)
                .join(Trader, RiskScore.trader_id == Trader.id)
                .order_by(RiskScore.unified_score.desc())
                .limit(6)
            )
        ).all()
        high_traders = []
        for risk, trader in trader_risks:
            ac = (
                await db.execute(select(func.count(Alert.id)).where(Alert.trader_id == trader.id))
            ).scalar() or 0
            high_traders.append(
                TraderRiskRow(
                    external_id=trader.external_id,
                    name=trader.name,
                    risk_score=risk.unified_score,
                    alert_count=ac,
                    is_insider_linked=trader.is_insider_linked,
                )
            )

        recent = (
            await db.execute(select(Alert).order_by(Alert.created_at.desc()).limit(10))
        ).scalars().all()

        now = datetime.now(timezone.utc)
        anomaly_ts = [
            TimeSeriesPoint(timestamp=now - timedelta(hours=24 - i * 2), value=3 + i * 0.4 + (i % 3), label="anomalies")
            for i in range(12)
        ]
        sentiment_ts = [
            TimeSeriesPoint(timestamp=now - timedelta(hours=24 - i * 2), value=0.2 + (i % 5) * 0.08, label="sentiment")
            for i in range(12)
        ]

        sectors = (await db.execute(select(Stock.sector, func.avg(RiskScore.unified_score)).join(
            RiskScore, RiskScore.stock_id == Stock.id
        ).group_by(Stock.sector))).all()
        sector_heatmap = [
            HeatmapCell(row="risk", col=sec, value=round(float(avg or 0), 3)) for sec, avg in sectors
        ]

        kpis = [
            KPICard(label="Active Alerts", value=alert_count, delta=f"+{alerts_today} today", trend="up"),
            KPICard(label="High-Risk Tickers", value=len(top_tickers), trend="up"),
            KPICard(label="Flagged Traders", value=len(high_traders), trend="neutral"),
            KPICard(label="Graph Clusters", value=3, trend="up"),
        ]

        return DashboardOverview(
            kpis=kpis,
            top_risk_tickers=top_tickers,
            high_risk_traders=high_traders,
            alerts_today=alerts_today,
            anomaly_timeseries=anomaly_ts,
            sentiment_trend=sentiment_ts,
            sector_heatmap=sector_heatmap,
            pump_watchlist=[t for t in top_tickers if t.pump_risk != "low"][:5],
            graph_summary={"clusters": 3, "suspicious_edges": 12, "insider_paths": 5},
            recent_alerts=[
                {
                    "id": a.id,
                    "title": a.title,
                    "severity": a.severity,
                    "status": a.status,
                    "created_at": a.created_at.isoformat(),
                }
                for a in recent
            ],
            disclaimer=DISCLAIMER,
        )

    async def market_heatmap(self, db: AsyncSession) -> MarketHeatmapResponse:
        stocks = (await db.execute(select(Stock, RiskScore).join(
            RiskScore, RiskScore.stock_id == Stock.id
        ))).all()

        stock_risk = [
            HeatmapCell(row=s.sector, col=s.ticker, value=round(r.unified_score, 3))
            for s, r in stocks
        ]
        sector_agg: dict[str, list[float]] = {}
        for s, r in stocks:
            sector_agg.setdefault(s.sector, []).append(r.unified_score)
        sector_risk = [
            HeatmapCell(row="sector", col=k, value=round(sum(v) / len(v), 3))
            for k, v in sector_agg.items()
        ]

        return MarketHeatmapResponse(
            sector_risk=sector_risk,
            stock_risk=stock_risk,
            event_window=[HeatmapCell(row="HELIX", col="T-2d", value=0.82)],
            sentiment_burst=[HeatmapCell(row="APEX", col="social", value=0.88)],
            social_coordination=[HeatmapCell(row="QUANT", col="cluster", value=0.79)],
        )
