"""Synthetic market data generator with embedded demo scenarios."""

from __future__ import annotations

import hashlib
import json
import random
from datetime import datetime, timedelta, timezone

import numpy as np
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.graph.insider_graph import InsiderGraphAnalyzer
from app.ml.anomaly import AnomalyEngine
from app.ml.features import build_trade_features
from app.ml.pump_dump import PumpDumpEngine
from app.ml.risk_fusion import RiskFusionEngine
from app.ml.sentiment import SentimentEngine
from app.ml.social import SocialAnalysisEngine
from app.models.entities import (
    Alert,
    AlertComment,
    Broker,
    CorporateEvent,
    GraphEdge,
    GraphNode,
    InsiderProfile,
    NewsArticle,
    Order,
    RiskScore,
    SocialPost,
    Stock,
    Trade,
    Trader,
    Watchlist,
)

SECTORS = ["Technology", "Finance", "Healthcare", "Energy", "Consumer", "Industrial"]
STOCK_TICKERS = [
    ("NEXA", "Nexa Dynamics Ltd", "Technology", 2.1e9),
    ("ORBIT", "Orbit Fin Holdings", "Finance", 8.5e8),
    ("HELIX", "Helix Bio Systems", "Healthcare", 1.4e9),
    ("VOLT", "Volt Energy Corp", "Energy", 3.2e9),
    ("LUMEN", "Lumen Retail Group", "Consumer", 6.2e8),
    ("FORGE", "Forge Industrial", "Industrial", 1.1e9),
    ("QUANT", "Quant Edge Tech", "Technology", 4.5e8),
    ("APEX", "Apex Micro Cap", "Finance", 1.2e8),
]

SCENARIOS = {
    "insider_earnings": "insider_earnings",
    "pump_dump_social": "pump_dump_social",
    "coordinated_cluster": "coordinated_cluster",
    "spoof_cancel": "spoof_cancel",
}


class DemoDataGenerator:
    def __init__(self):
        self.sentiment = SentimentEngine()
        self.social = SocialAnalysisEngine()
        self.anomaly = AnomalyEngine()
        self.pump = PumpDumpEngine()
        self.fusion = RiskFusionEngine()
        self.graph_analyzer = InsiderGraphAnalyzer()
        self.rng = random.Random(42)

    async def clear_all(self, db: AsyncSession) -> None:
        for model in [
            AlertComment, Alert, RiskScore, Watchlist, GraphEdge, GraphNode,
            SocialPost, NewsArticle, Order, Trade, CorporateEvent,
            InsiderProfile, Trader, Broker, Stock,
        ]:
            await db.execute(delete(model))
        await db.flush()

    async def generate(self, db: AsyncSession, days: int = 30) -> dict:
        await self.clear_all(db)
        now = datetime.now(timezone.utc)
        start = now - timedelta(days=days)

        brokers = [Broker(code=f"BR{i:02d}", name=f"Broker {i}") for i in range(1, 4)]
        db.add_all(brokers)
        await db.flush()

        stocks = []
        for ticker, name, sector, mcap in STOCK_TICKERS:
            s = Stock(
                ticker=ticker,
                name=name,
                sector=sector,
                market_cap=mcap,
                liquidity_score=min(1.0, mcap / 5e9),
            )
            stocks.append(s)
        db.add_all(stocks)
        await db.flush()

        traders = []
        for i in range(1, 41):
            device = f"dev-{i % 7}"
            addr = f"addr-{i % 11}"
            t = Trader(
                external_id=f"TR-{i:03d}",
                name=f"Trader {i}",
                broker_id=brokers[i % 3].id,
                account_type="retail" if i > 5 else "institutional",
                device_hash=device,
                address_hash=addr,
                bank_id_hash=f"bank-{i % 9}",
                is_insider_linked=i <= 3,
            )
            traders.append(t)
        db.add_all(traders)
        await db.flush()

        for t in traders[:3]:
            db.add(
                InsiderProfile(
                    trader_id=t.id,
                    company_ticker="HELIX" if t.id == traders[0].id else "NEXA",
                    role="Director" if t.id == traders[0].id else "Associate",
                    relation_type="employee" if t.id != traders[2].id else "relative",
                )
            )

        events = []
        helix = next(s for s in stocks if s.ticker == "HELIX")
        apex = next(s for s in stocks if s.ticker == "APEX")
        nexa = next(s for s in stocks if s.ticker == "NEXA")
        quant = next(s for s in stocks if s.ticker == "QUANT")

        events.append(
            CorporateEvent(
                stock_id=helix.id,
                event_type="earnings",
                title="Q4 Earnings Release",
                event_date=now + timedelta(days=2),
                impact_level="high",
                description="Scheduled earnings — demo insider scenario anchor",
            )
        )
        events.append(
            CorporateEvent(
                stock_id=apex.id,
                event_type="regulatory",
                title="Micro-cap liquidity review",
                event_date=now + timedelta(days=5),
                impact_level="medium",
            )
        )
        db.add_all(events)
        await db.flush()

        trades, orders = [], []
        trade_rows_for_ml = []

        def add_trade(trader, stock, side, qty, price, ts, suspicious=False, tag=None):
            notional = qty * price
            tr = Trade(
                trader_id=trader.id,
                stock_id=stock.id,
                side=side,
                quantity=qty,
                price=price,
                notional=notional,
                executed_at=ts,
                is_suspicious_label=suspicious,
                scenario_tag=tag,
            )
            trades.append(tr)
            trade_rows_for_ml.append(
                {
                    "trader_id": trader.id,
                    "stock_id": stock.id,
                    "side": side,
                    "quantity": qty,
                    "price": price,
                    "notional": notional,
                    "executed_at": ts,
                }
            )

        # Baseline activity
        for day in range(days):
            ts_base = start + timedelta(days=day, hours=10)
            for _ in range(25):
                t = self.rng.choice(traders[5:])
                s = self.rng.choice(stocks)
                side = self.rng.choice(["buy", "sell"])
                price = 50 + self.rng.random() * 100
                qty = self.rng.randint(10, 200)
                add_trade(t, s, side, qty, price, ts_base + timedelta(hours=self.rng.randint(0, 6)))

        # Scenario 1: Insider buildup before earnings (HELIX, traders 1-3)
        for d in range(5, 0, -1):
            ts = now - timedelta(days=d)
            for tr in traders[:3]:
                add_trade(tr, helix, "buy", 800 + d * 100, 42.0 + d * 0.5, ts, True, SCENARIOS["insider_earnings"])

        # Scenario 2: Pump-and-dump on APEX
        for d in range(7):
            ts = now - timedelta(days=6 - d)
            add_trade(self.rng.choice(traders[10:20]), apex, "buy", 500 + d * 80, 3.2 + d * 0.4, ts, True, SCENARIOS["pump_dump_social"])

        # Scenario 3: Coordinated cluster on QUANT (shared device)
        cluster = [traders[4], traders[5], traders[6]]
        for tr in cluster:
            tr.device_hash = "dev-cluster-99"
        for d in range(4):
            ts = now - timedelta(days=3 - d)
            for tr in cluster:
                add_trade(tr, quant, "buy", 600, 18.0 + d * 0.3, ts, True, SCENARIOS["coordinated_cluster"])

        # Scenario 4: Spoof-like cancels on NEXA
        spoof_trader = traders[7]
        for i in range(30):
            ts = now - timedelta(hours=12 - i // 3)
            o = Order(
                trader_id=spoof_trader.id,
                stock_id=nexa.id,
                side="buy",
                quantity=1000,
                price=120.0,
                status="cancelled" if i % 3 != 0 else "filled",
                placed_at=ts,
                cancelled_at=ts + timedelta(seconds=30) if i % 3 != 0 else None,
            )
            orders.append(o)
        add_trade(spoof_trader, nexa, "buy", 50, 120.0, now - timedelta(hours=2), True, SCENARIOS["spoof_cancel"])

        db.add_all(trades)
        db.add_all(orders)
        await db.flush()

        # News & social
        news_headlines = [
            (helix, "Helix beats estimates in preliminary channel checks", "positive"),
            (apex, "APEX to the moon — retail chat rooms erupt", "hype"),
            (apex, "Unverified rumor claims major partnership for Apex Micro", "suspicious"),
            (quant, "Quant Edge sees unusual block activity ahead of index rebalance", "neutral"),
            (nexa, "Nexa order book depth spikes amid cancellation surge", "neutral"),
        ]
        for stock, headline, _ in news_headlines:
            sr = self.sentiment.analyze(headline)
            db.add(
                NewsArticle(
                    stock_id=stock.id,
                    headline=headline,
                    source="DemoWire",
                    published_at=now - timedelta(hours=self.rng.randint(1, 48)),
                    sentiment_label=sr.label,
                    sentiment_score=sr.score,
                    hype_score=sr.hype_score,
                    tone=sr.tone,
                )
            )

        social_templates = [
            (apex, "Telegram", "APEX going parabolic 🚀 don't miss", True, True),
            (apex, "X", "Buy APEX now guaranteed gains!!!", True, True),
            (apex, "Forum", "APEX pump starting", False, True),
            (quant, "X", "QUANT accumulation pattern forming", False, False),
        ]
        for stock, platform, content, bot, burst in social_templates:
            sr = self.sentiment.analyze(content)
            for i in range(8 if burst else 2):
                db.add(
                    SocialPost(
                        stock_id=stock.id,
                        platform=platform,
                        author=f"user_{hashlib.md5(content.encode()).hexdigest()[:6]}",
                        content=content,
                        posted_at=now - timedelta(hours=i),
                        sentiment_score=sr.score,
                        is_bot_like=bot,
                        mention_burst=burst,
                    )
                )

        # Graph nodes/edges
        nodes, edges = [], []
        for t in traders[:15]:
            nid = f"trader:{t.external_id}"
            nodes.append(GraphNode(node_id=nid, node_type="trader", label=t.name, metadata_json="{}"))
        for s in stocks[:5]:
            nid = f"stock:{s.ticker}"
            nodes.append(GraphNode(node_id=nid, node_type="company", label=s.ticker, metadata_json="{}"))
        nodes.append(GraphNode(node_id="device:cluster-99", node_type="device", label="Shared Device", metadata_json="{}"))
        nodes.append(GraphNode(node_id="insider:HELIX-DIR", node_type="insider", label="Helix Director", metadata_json="{}"))

        for t in traders[:3]:
            edges.append(
                GraphEdge(
                    source_id=f"trader:{t.external_id}",
                    target_id="insider:HELIX-DIR",
                    edge_type="employment",
                    weight=2.0,
                    is_suspicious=True,
                )
            )
            edges.append(
                GraphEdge(
                    source_id=f"trader:{t.external_id}",
                    target_id="stock:HELIX",
                    edge_type="co_trade_event",
                    weight=1.5,
                    is_suspicious=True,
                )
            )
        for t in traders[4:7]:
            edges.append(
                GraphEdge(
                    source_id=f"trader:{t.external_id}",
                    target_id="device:cluster-99",
                    edge_type="same_device",
                    weight=2.5,
                    is_suspicious=True,
                )
            )
        db.add_all(nodes)
        db.add_all(edges)
        await db.flush()

        # ML pipeline + alerts
        import pandas as pd

        trades_df = pd.DataFrame(trade_rows_for_ml)
        trades_df["executed_at"] = pd.to_datetime(trades_df["executed_at"], utc=True)
        orders_df = pd.DataFrame(
            [{"trader_id": o.trader_id, "stock_id": o.stock_id, "status": o.status, "placed_at": o.placed_at} for o in orders]
        ) if orders else pd.DataFrame(columns=["trader_id", "stock_id", "status", "placed_at"])
        events_df = pd.DataFrame([{"stock_id": e.stock_id, "event_date": e.event_date} for e in events])

        feature_matrix = []
        pairs = trades_df.groupby(["trader_id", "stock_id"]).size().reset_index()[["trader_id", "stock_id"]]
        for _, row in pairs.head(80).iterrows():
            fv = build_trade_features(trades_df, orders_df, events_df, int(row["trader_id"]), int(row["stock_id"]), now)
            feature_matrix.append(fv.values)
        if feature_matrix:
            self.anomaly.fit(np.array(feature_matrix))

        alerts_created = 0
        stock_map = {s.ticker: s for s in stocks}
        trader_map = {t.external_id: t for t in traders}

        scenario_specs = [
            ("insider_earnings", "Insider-linked accumulation pre-earnings", traders[0], helix, 0.82),
            ("pump_dump_social", "Pump-and-dump social hype campaign", traders[10], apex, 0.88),
            ("coordinated_cluster", "Coordinated multi-account buying cluster", traders[4], quant, 0.79),
            ("spoof_cancel", "Spoof-like cancel ratio anomaly", traders[7], nexa, 0.76),
        ]

        for tag, title, trader, stock, base_score in scenario_specs:
            subset = trades_df[(trades_df["trader_id"] == trader.id) & (trades_df["stock_id"] == stock.id)]
            if subset.empty:
                continue
            fv = build_trade_features(trades_df, orders_df, events_df, trader.id, stock.id, now)
            ar = self.anomaly.predict_one(fv.values)

            graph_nodes = [{"node_id": n.node_id, "node_type": n.node_type, "label": n.label} for n in nodes]
            graph_edges = [
                {"source_id": e.source_id, "target_id": e.target_id, "edge_type": e.edge_type, "weight": e.weight, "is_suspicious": e.is_suspicious}
                for e in edges
            ]
            gviz = self.graph_analyzer.analyze(graph_nodes, graph_edges, {f"trader:{trader.external_id}"})

            pump_res = self.pump.predict(4.2, 0.09, 0.7 if stock.ticker == "APEX" else 0.2, stock.market_cap, 0.6, 0.55)
            fusion_res = self.fusion.fuse(
                ar.anomaly_score,
                0.55 if stock.ticker == "HELIX" else 0.35,
                0.75 if stock.ticker == "APEX" else 0.2,
                gviz.metrics.insider_proximity_score,
                pump_res.likelihood,
                0.7 if stock.ticker == "HELIX" else 0.3,
            )

            db.add(
                RiskScore(
                    stock_id=stock.id,
                    trader_id=trader.id,
                    unified_score=fusion_res.unified_score,
                    trade_anomaly_score=ar.anomaly_score,
                    sentiment_score=0.55,
                    social_hype_score=0.75 if stock.ticker == "APEX" else 0.2,
                    graph_score=gviz.metrics.insider_proximity_score,
                    pump_dump_score=pump_res.likelihood,
                    explainability_json=self.fusion.to_json(fusion_res.components),
                )
            )

            explanation = (
                f"Trader {trader.external_id} flagged on {stock.ticker}: "
                f"{ar.explanation} Graph proximity {gviz.metrics.insider_proximity_score:.2f}. "
                f"{pump_res.explanation}"
            )
            db.add(
                Alert(
                    alert_type="manipulation_surveillance",
                    stock_id=stock.id,
                    trader_id=trader.id,
                    severity=fusion_res.severity,
                    confidence=round(min(0.95, base_score + 0.05), 2),
                    risk_score=fusion_res.unified_score,
                    title=title,
                    explanation=explanation,
                    top_drivers=self.anomaly.drivers_to_json(ar.top_drivers),
                    suggested_action=fusion_res.suggested_action,
                    status="new",
                    scenario_tag=tag,
                )
            )
            alerts_created += 1

        if apex:
            db.add(Watchlist(stock_id=apex.id, reason="Elevated pump-and-dump indicators", pump_risk_level="elevated"))

        await db.flush()
        return {
            "stocks": len(stocks),
            "traders": len(traders),
            "trades": len(trades),
            "alerts": alerts_created,
            "scenarios_embedded": list(SCENARIOS.values()),
        }
