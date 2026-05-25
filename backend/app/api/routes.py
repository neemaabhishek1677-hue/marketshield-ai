import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.graph.insider_graph import InsiderGraphAnalyzer
from app.ml.pump_dump import PumpDumpEngine
from app.ml.sentiment import SentimentEngine
from app.models.entities import (
    Alert,
    AlertComment,
    CorporateEvent,
    GraphEdge,
    GraphNode,
    NewsArticle,
    RiskScore,
    SocialPost,
    Stock,
    Trade,
    Trader,
)
from app.schemas.alerts import AlertCommentCreate, AlertCommentOut, AlertDetail, AlertOut, AlertUpdate
from app.schemas.common import DemoScenario, HealthResponse, SeedRequest, SeedResponse
from app.schemas.dashboard import DashboardOverview, MarketHeatmapResponse
from app.seed.demo_generator import DemoDataGenerator, SCENARIOS
from app.services.analytics import AnalyticsService
from app.services.insights import InsightsService
from app.ml.anomaly import AnomalyEngine

router = APIRouter()
analytics = AnalyticsService()
insights = InsightsService()
sentiment_engine = SentimentEngine()
pump_engine = PumpDumpEngine()
graph_analyzer = InsiderGraphAnalyzer()
anomaly_engine = AnomalyEngine()
demo_gen = DemoDataGenerator()

alert_connections: list[WebSocket] = []


@router.get("/health", response_model=HealthResponse)
async def health(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(select(1))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
    return HealthResponse(status="ok", app="MarketShield AI", database=db_status)


@router.post("/seed/generate-demo-data", response_model=SeedResponse)
async def seed_demo(body: SeedRequest, db: AsyncSession = Depends(get_db)):
    stats = await demo_gen.generate(db, days=body.days)
    return SeedResponse(
        message="Demo dataset generated with embedded surveillance scenarios",
        stocks=stats["stocks"],
        traders=stats["traders"],
        trades=stats["trades"],
        alerts=stats["alerts"],
        scenarios_embedded=stats["scenarios_embedded"],
    )


@router.get("/dashboard/overview", response_model=DashboardOverview)
async def dashboard_overview(db: AsyncSession = Depends(get_db)):
    return await analytics.dashboard_overview(db)


@router.get("/dashboard/market-heatmap", response_model=MarketHeatmapResponse)
async def market_heatmap(db: AsyncSession = Depends(get_db)):
    return await analytics.market_heatmap(db)


@router.get("/alerts", response_model=list[AlertOut])
async def list_alerts(
    status: str | None = None,
    severity: str | None = None,
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(Alert).order_by(Alert.created_at.desc()).limit(limit)
    if status:
        q = q.where(Alert.status == status)
    if severity:
        q = q.where(Alert.severity == severity)
    return (await db.execute(q)).scalars().all()


@router.get("/alerts/{alert_id}", response_model=AlertDetail)
async def get_alert(alert_id: int, db: AsyncSession = Depends(get_db)):
    alert = (await db.execute(select(Alert).where(Alert.id == alert_id))).scalar_one_or_none()
    if not alert:
        raise HTTPException(404, "Alert not found")
    ticker = trader_ext = None
    if alert.stock_id:
        s = (await db.execute(select(Stock).where(Stock.id == alert.stock_id))).scalar_one_or_none()
        ticker = s.ticker if s else None
    if alert.trader_id:
        t = (await db.execute(select(Trader).where(Trader.id == alert.trader_id))).scalar_one_or_none()
        trader_ext = t.external_id if t else None
    drivers = []
    try:
        drivers = json.loads(alert.top_drivers)
    except json.JSONDecodeError:
        pass
    return AlertDetail(
        id=alert.id,
        alert_type=alert.alert_type,
        stock_id=alert.stock_id,
        trader_id=alert.trader_id,
        severity=alert.severity,
        confidence=alert.confidence,
        risk_score=alert.risk_score,
        title=alert.title,
        explanation=alert.explanation,
        top_drivers=alert.top_drivers,
        suggested_action=alert.suggested_action,
        status=alert.status,
        scenario_tag=alert.scenario_tag,
        created_at=alert.created_at,
        updated_at=alert.updated_at,
        ticker=ticker,
        trader_external_id=trader_ext,
        drivers_parsed=drivers,
    )


@router.patch("/alerts/{alert_id}", response_model=AlertOut)
async def patch_alert(alert_id: int, body: AlertUpdate, db: AsyncSession = Depends(get_db)):
    alert = (await db.execute(select(Alert).where(Alert.id == alert_id))).scalar_one_or_none()
    if not alert:
        raise HTTPException(404, "Alert not found")
    if body.status:
        alert.status = body.status
        alert.updated_at = datetime.now(timezone.utc)
    await db.flush()
    return alert


@router.post("/alerts/{alert_id}/comments", response_model=AlertCommentOut)
async def add_comment(alert_id: int, body: AlertCommentCreate, db: AsyncSession = Depends(get_db)):
    alert = (await db.execute(select(Alert).where(Alert.id == alert_id))).scalar_one_or_none()
    if not alert:
        raise HTTPException(404, "Alert not found")
    c = AlertComment(alert_id=alert_id, author=body.author, body=body.body)
    db.add(c)
    await db.flush()
    return c


@router.get("/stocks")
async def list_stocks(db: AsyncSession = Depends(get_db)):
    stocks = (await db.execute(select(Stock).order_by(Stock.ticker))).scalars().all()
    return [
        {
            "id": s.id,
            "ticker": s.ticker,
            "name": s.name,
            "sector": s.sector,
            "market_cap": s.market_cap,
        }
        for s in stocks
    ]


@router.get("/stocks/{ticker}")
async def get_stock(ticker: str, db: AsyncSession = Depends(get_db)):
    stock = (await db.execute(select(Stock).where(Stock.ticker == ticker.upper()))).scalar_one_or_none()
    if not stock:
        raise HTTPException(404, "Stock not found")
    trade_count = (await db.execute(select(func.count(Trade.id)).where(Trade.stock_id == stock.id))).scalar()
    return {
        "stock": {
            "id": stock.id,
            "ticker": stock.ticker,
            "name": stock.name,
            "sector": stock.sector,
            "market_cap": stock.market_cap,
        },
        "trade_count": trade_count,
        "insight": await insights.stock_insight(db, stock),
    }


@router.get("/stocks/{ticker}/risk")
async def stock_risk(ticker: str, db: AsyncSession = Depends(get_db)):
    stock = (await db.execute(select(Stock).where(Stock.ticker == ticker.upper()))).scalar_one_or_none()
    if not stock:
        raise HTTPException(404, "Stock not found")
    risk = (
        await db.execute(
            select(RiskScore).where(RiskScore.stock_id == stock.id).order_by(RiskScore.unified_score.desc()).limit(1)
        )
    ).scalar_one_or_none()
    if not risk:
        return {"ticker": ticker, "unified_score": 0.0, "message": "Run seed to compute risk scores"}
    return {
        "ticker": stock.ticker,
        "unified_score": risk.unified_score,
        "components": json.loads(risk.explainability_json),
        "trade_anomaly": risk.trade_anomaly_score,
        "sentiment": risk.sentiment_score,
        "social_hype": risk.social_hype_score,
        "graph": risk.graph_score,
        "pump_dump": risk.pump_dump_score,
    }


@router.get("/stocks/{ticker}/sentiment")
async def stock_sentiment(ticker: str, db: AsyncSession = Depends(get_db)):
    stock = (await db.execute(select(Stock).where(Stock.ticker == ticker.upper()))).scalar_one_or_none()
    if not stock:
        raise HTTPException(404, "Stock not found")
    articles = (
        await db.execute(select(NewsArticle).where(NewsArticle.stock_id == stock.id).order_by(NewsArticle.published_at.desc()))
    ).scalars().all()
    return {
        "ticker": stock.ticker,
        "articles": [
            {
                "headline": a.headline,
                "label": a.sentiment_label,
                "score": a.sentiment_score,
                "tone": a.tone,
                "hype_score": a.hype_score,
                "published_at": a.published_at.isoformat(),
            }
            for a in articles
        ],
        "aggregate_score": sum(a.sentiment_score for a in articles) / max(len(articles), 1),
    }


@router.get("/stocks/{ticker}/anomalies")
async def stock_anomalies(ticker: str, db: AsyncSession = Depends(get_db)):
    stock = (await db.execute(select(Stock).where(Stock.ticker == ticker.upper()))).scalar_one_or_none()
    if not stock:
        raise HTTPException(404, "Stock not found")
    alerts = (
        await db.execute(select(Alert).where(Alert.stock_id == stock.id).order_by(Alert.risk_score.desc()))
    ).scalars().all()
    return {"ticker": stock.ticker, "anomalies": [{"id": a.id, "title": a.title, "risk_score": a.risk_score, "explanation": a.explanation} for a in alerts]}


@router.get("/stocks/{ticker}/pump-dump-prediction")
async def pump_dump(ticker: str, db: AsyncSession = Depends(get_db)):
    stock = (await db.execute(select(Stock).where(Stock.ticker == ticker.upper()))).scalar_one_or_none()
    if not stock:
        raise HTTPException(404, "Stock not found")
    risk = (
        await db.execute(select(RiskScore).where(RiskScore.stock_id == stock.id).order_by(RiskScore.unified_score.desc()).limit(1))
    ).scalar_one_or_none()
    social_count = (await db.execute(select(func.count(SocialPost.id)).where(SocialPost.stock_id == stock.id))).scalar() or 0
    pred = pump_engine.predict(
        volume_spike=4.0 if stock.ticker == "APEX" else 1.2,
        price_acceleration=0.1 if stock.ticker == "APEX" else 0.02,
        social_burst=min(1.0, social_count / 20.0),
        market_cap=stock.market_cap,
        sentiment_hype=risk.social_hype_score if risk else 0.3,
        buy_concentration=risk.trade_anomaly_score if risk else 0.2,
    )
    return {"ticker": stock.ticker, **pred.__dict__}


@router.get("/traders")
async def list_traders(db: AsyncSession = Depends(get_db)):
    traders = (await db.execute(select(Trader).order_by(Trader.external_id))).scalars().all()
    return [
        {
            "id": t.id,
            "external_id": t.external_id,
            "name": t.name,
            "is_insider_linked": t.is_insider_linked,
            "account_type": t.account_type,
        }
        for t in traders
    ]


@router.get("/traders/{trader_id}")
async def get_trader(trader_id: str, db: AsyncSession = Depends(get_db)):
    t = (
        await db.execute(select(Trader).where((Trader.external_id == trader_id) | (Trader.id == int(trader_id) if trader_id.isdigit() else -1)))
    ).scalar_one_or_none()
    if not t:
        raise HTTPException(404, "Trader not found")
    return {"trader": {"id": t.id, "external_id": t.external_id, "name": t.name}, "insight": await insights.trader_insight(db, t)}


@router.get("/traders/{trader_id}/risk")
async def trader_risk(trader_id: str, db: AsyncSession = Depends(get_db)):
    t = (await db.execute(select(Trader).where(Trader.external_id == trader_id))).scalar_one_or_none()
    if not t:
        raise HTTPException(404, "Trader not found")
    risk = (
        await db.execute(select(RiskScore).where(RiskScore.trader_id == t.id).order_by(RiskScore.unified_score.desc()).limit(1))
    ).scalar_one_or_none()
    return {"trader_id": t.external_id, "unified_score": risk.unified_score if risk else 0.0, "components": json.loads(risk.explainability_json) if risk else {}}


@router.get("/traders/{trader_id}/graph")
async def trader_graph(trader_id: str, db: AsyncSession = Depends(get_db)):
    nodes = (await db.execute(select(GraphNode))).scalars().all()
    edges = (await db.execute(select(GraphEdge))).scalars().all()
    nlist = [{"node_id": n.node_id, "node_type": n.node_type, "label": n.label} for n in nodes]
    elist = [
        {"source_id": e.source_id, "target_id": e.target_id, "edge_type": e.edge_type, "weight": e.weight, "is_suspicious": e.is_suspicious}
        for e in edges
    ]
    gviz = graph_analyzer.analyze(nlist, elist, {f"trader:{trader_id}"})
    return {"trader_id": trader_id, "nodes": gviz.nodes, "edges": gviz.edges, "metrics": gviz.metrics.__dict__}


@router.get("/events")
async def list_events(db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(select(CorporateEvent, Stock).join(Stock, CorporateEvent.stock_id == Stock.id))).all()
    return [
        {
            "id": e.id,
            "ticker": s.ticker,
            "event_type": e.event_type,
            "title": e.title,
            "event_date": e.event_date.isoformat(),
            "impact_level": e.impact_level,
        }
        for e, s in rows
    ]


@router.get("/graphs/insider-network")
async def insider_network(db: AsyncSession = Depends(get_db)):
    nodes = (await db.execute(select(GraphNode))).scalars().all()
    edges = (await db.execute(select(GraphEdge))).scalars().all()
    nlist = [{"node_id": n.node_id, "node_type": n.node_type, "label": n.label} for n in nodes]
    elist = [
        {"source_id": e.source_id, "target_id": e.target_id, "edge_type": e.edge_type, "weight": e.weight, "is_suspicious": e.is_suspicious}
        for e in edges
    ]
    active = {n.node_id for n in nodes if n.node_type == "trader" and "TR-00" in n.label}
    gviz = graph_analyzer.analyze(nlist, elist, active)
    return {"nodes": gviz.nodes, "edges": gviz.edges, "metrics": gviz.metrics.__dict__}


@router.get("/analytics/top-suspicious")
async def top_suspicious(db: AsyncSession = Depends(get_db)):
    stocks = (
        await db.execute(select(Stock, RiskScore).join(RiskScore, RiskScore.stock_id == Stock.id).order_by(RiskScore.unified_score.desc()).limit(10))
    ).all()
    traders = (
        await db.execute(select(Trader, RiskScore).join(RiskScore, RiskScore.trader_id == Trader.id).order_by(RiskScore.unified_score.desc()).limit(10))
    ).all()
    return {
        "stocks": [{"ticker": s.ticker, "score": r.unified_score} for s, r in stocks],
        "traders": [{"id": t.external_id, "score": r.unified_score} for t, r in traders],
    }


@router.get("/analytics/anomaly-timeseries")
async def anomaly_timeseries(db: AsyncSession = Depends(get_db)):
    overview = await analytics.dashboard_overview(db)
    return {"series": overview.anomaly_timeseries}


@router.post("/ml/retrain")
async def ml_retrain(db: AsyncSession = Depends(get_db)):
    stats = await demo_gen.generate(db, days=14)
    return {"status": "completed", "message": "Models retrained on refreshed synthetic dataset", "stats": stats}


@router.get("/demo/scenarios", response_model=list[DemoScenario])
async def demo_scenarios():
    return [
        DemoScenario(
            id="insider_earnings",
            name="Insider buildup before earnings",
            description="Linked accounts accumulate HELIX before high-impact earnings.",
            scenario_tag=SCENARIOS["insider_earnings"],
            walkthrough=[
                "Open Dashboard → note HELIX risk",
                "Stocks → HELIX → view risk & sentiment",
                "Insider Graph → trace director links",
                "Alerts → open insider earnings alert",
            ],
        ),
        DemoScenario(
            id="pump_dump_social",
            name="Pump-and-dump social hype",
            description="APEX shows social burst, hype news, and pump-risk elevation.",
            scenario_tag=SCENARIOS["pump_dump_social"],
            walkthrough=["Dashboard pump watchlist", "Sentiment & Social page", "APEX pump-dump prediction"],
        ),
        DemoScenario(
            id="coordinated_cluster",
            name="Coordinated trading cluster",
            description="QUANT accounts share device fingerprint and coordinated buys.",
            scenario_tag=SCENARIOS["coordinated_cluster"],
            walkthrough=["Trader TR-005 graph", "Heatmaps social coordination", "Alerts cluster"],
        ),
        DemoScenario(
            id="spoof_cancel",
            name="Spoof-like cancel pattern",
            description="NEXA experiences high cancel-to-fill ratio with thin executed volume.",
            scenario_tag=SCENARIOS["spoof_cancel"],
            walkthrough=["Stocks NEXA anomalies", "Alerts spoof alert", "Trader TR-008 profile"],
        ),
    ]


@router.websocket("/stream/alerts")
async def stream_alerts(websocket: WebSocket):
    await websocket.accept()
    alert_connections.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        alert_connections.remove(websocket)
