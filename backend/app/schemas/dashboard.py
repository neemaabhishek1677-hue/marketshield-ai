from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import HeatmapCell, TimeSeriesPoint


class KPICard(BaseModel):
    label: str
    value: str | float | int
    delta: str | None = None
    trend: str | None = None


class RiskTickerRow(BaseModel):
    ticker: str
    name: str
    sector: str
    unified_score: float
    pump_risk: str
    alert_count: int


class TraderRiskRow(BaseModel):
    external_id: str
    name: str
    risk_score: float
    alert_count: int
    is_insider_linked: bool


class DashboardOverview(BaseModel):
    kpis: list[KPICard]
    top_risk_tickers: list[RiskTickerRow]
    high_risk_traders: list[TraderRiskRow]
    alerts_today: int
    anomaly_timeseries: list[TimeSeriesPoint]
    sentiment_trend: list[TimeSeriesPoint]
    sector_heatmap: list[HeatmapCell]
    pump_watchlist: list[RiskTickerRow]
    graph_summary: dict
    recent_alerts: list[dict]
    disclaimer: str


class MarketHeatmapResponse(BaseModel):
    sector_risk: list[HeatmapCell]
    stock_risk: list[HeatmapCell]
    event_window: list[HeatmapCell]
    sentiment_burst: list[HeatmapCell]
    social_coordination: list[HeatmapCell]
