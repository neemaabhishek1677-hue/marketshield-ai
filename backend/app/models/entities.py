import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AlertStatus(str, enum.Enum):
    NEW = "new"
    UNDER_REVIEW = "under_review"
    ESCALATED = "escalated"
    DISMISSED = "dismissed"
    RESOLVED = "resolved"


class AlertSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Stock(Base):
    __tablename__ = "stocks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticker: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128))
    sector: Mapped[str] = mapped_column(String(64), index=True)
    market_cap: Mapped[float] = mapped_column(Float)
    liquidity_score: Mapped[float] = mapped_column(Float, default=0.5)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    trades: Mapped[list["Trade"]] = relationship(back_populates="stock")
    risk_scores: Mapped[list["RiskScore"]] = relationship(back_populates="stock")


class Broker(Base):
    __tablename__ = "brokers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True)
    name: Mapped[str] = mapped_column(String(128))


class Trader(Base):
    __tablename__ = "traders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    external_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128))
    broker_id: Mapped[int | None] = mapped_column(ForeignKey("brokers.id"))
    account_type: Mapped[str] = mapped_column(String(32), default="retail")
    device_hash: Mapped[str | None] = mapped_column(String(64), index=True)
    address_hash: Mapped[str | None] = mapped_column(String(64), index=True)
    bank_id_hash: Mapped[str | None] = mapped_column(String(64))
    is_insider_linked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    broker: Mapped["Broker | None"] = relationship()
    trades: Mapped[list["Trade"]] = relationship(back_populates="trader")
    insider_profile: Mapped["InsiderProfile | None"] = relationship(back_populates="trader", uselist=False)


class InsiderProfile(Base):
    __tablename__ = "insider_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    trader_id: Mapped[int] = mapped_column(ForeignKey("traders.id"), unique=True)
    company_ticker: Mapped[str] = mapped_column(String(16), index=True)
    role: Mapped[str] = mapped_column(String(64))
    relation_type: Mapped[str] = mapped_column(String(64))

    trader: Mapped["Trader"] = relationship(back_populates="insider_profile")


class CorporateEvent(Base):
    __tablename__ = "corporate_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id"), index=True)
    event_type: Mapped[str] = mapped_column(String(64), index=True)
    title: Mapped[str] = mapped_column(String(256))
    event_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    impact_level: Mapped[str] = mapped_column(String(16), default="medium")
    description: Mapped[str | None] = mapped_column(Text)


class Trade(Base):
    __tablename__ = "trades"
    __table_args__ = (Index("ix_trades_stock_ts", "stock_id", "executed_at"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    trader_id: Mapped[int] = mapped_column(ForeignKey("traders.id"), index=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id"), index=True)
    side: Mapped[str] = mapped_column(String(8))
    quantity: Mapped[float] = mapped_column(Float)
    price: Mapped[float] = mapped_column(Float)
    notional: Mapped[float] = mapped_column(Float)
    executed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    is_suspicious_label: Mapped[bool] = mapped_column(Boolean, default=False)
    scenario_tag: Mapped[str | None] = mapped_column(String(64))

    trader: Mapped["Trader"] = relationship(back_populates="trades")
    stock: Mapped["Stock"] = relationship(back_populates="trades")


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (Index("ix_orders_stock_ts", "stock_id", "placed_at"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    trader_id: Mapped[int] = mapped_column(ForeignKey("traders.id"), index=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id"), index=True)
    side: Mapped[str] = mapped_column(String(8))
    quantity: Mapped[float] = mapped_column(Float)
    price: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(16))
    placed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class NewsArticle(Base):
    __tablename__ = "news_articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id"), index=True)
    headline: Mapped[str] = mapped_column(String(512))
    source: Mapped[str] = mapped_column(String(64))
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    sentiment_label: Mapped[str] = mapped_column(String(16))
    sentiment_score: Mapped[float] = mapped_column(Float)
    hype_score: Mapped[float] = mapped_column(Float, default=0.0)
    tone: Mapped[str] = mapped_column(String(32), default="neutral")


class SocialPost(Base):
    __tablename__ = "social_posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id"), index=True)
    platform: Mapped[str] = mapped_column(String(32))
    author: Mapped[str] = mapped_column(String(64))
    content: Mapped[str] = mapped_column(Text)
    posted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    sentiment_score: Mapped[float] = mapped_column(Float)
    is_bot_like: Mapped[bool] = mapped_column(Boolean, default=False)
    mention_burst: Mapped[bool] = mapped_column(Boolean, default=False)


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    alert_type: Mapped[str] = mapped_column(String(64), index=True)
    stock_id: Mapped[int | None] = mapped_column(ForeignKey("stocks.id"), index=True)
    trader_id: Mapped[int | None] = mapped_column(ForeignKey("traders.id"), index=True)
    severity: Mapped[str] = mapped_column(String(16), index=True)
    confidence: Mapped[float] = mapped_column(Float)
    risk_score: Mapped[float] = mapped_column(Float)
    title: Mapped[str] = mapped_column(String(256))
    explanation: Mapped[str] = mapped_column(Text)
    top_drivers: Mapped[str] = mapped_column(Text)
    suggested_action: Mapped[str] = mapped_column(String(128))
    status: Mapped[str] = mapped_column(String(32), default=AlertStatus.NEW.value, index=True)
    scenario_tag: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    comments: Mapped[list["AlertComment"]] = relationship(back_populates="alert")


class AlertComment(Base):
    __tablename__ = "alert_comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    alert_id: Mapped[int] = mapped_column(ForeignKey("alerts.id"), index=True)
    author: Mapped[str] = mapped_column(String(64), default="analyst")
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    alert: Mapped["Alert"] = relationship(back_populates="comments")


class Watchlist(Base):
    __tablename__ = "watchlists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stocks.id"))
    reason: Mapped[str] = mapped_column(String(256))
    pump_risk_level: Mapped[str] = mapped_column(String(32))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class RiskScore(Base):
    __tablename__ = "risk_scores"
    __table_args__ = (Index("ix_risk_stock_ts", "stock_id", "computed_at"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    stock_id: Mapped[int | None] = mapped_column(ForeignKey("stocks.id"), index=True)
    trader_id: Mapped[int | None] = mapped_column(ForeignKey("traders.id"), index=True)
    unified_score: Mapped[float] = mapped_column(Float, index=True)
    trade_anomaly_score: Mapped[float] = mapped_column(Float)
    sentiment_score: Mapped[float] = mapped_column(Float)
    social_hype_score: Mapped[float] = mapped_column(Float)
    graph_score: Mapped[float] = mapped_column(Float)
    pump_dump_score: Mapped[float] = mapped_column(Float)
    explainability_json: Mapped[str] = mapped_column(Text)
    computed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    stock: Mapped["Stock | None"] = relationship(back_populates="risk_scores")


class GraphNode(Base):
    __tablename__ = "graph_nodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    node_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    node_type: Mapped[str] = mapped_column(String(32))
    label: Mapped[str] = mapped_column(String(128))
    metadata_json: Mapped[str | None] = mapped_column(Text)


class GraphEdge(Base):
    __tablename__ = "graph_edges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_id: Mapped[str] = mapped_column(String(64), index=True)
    target_id: Mapped[str] = mapped_column(String(64), index=True)
    edge_type: Mapped[str] = mapped_column(String(64))
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    is_suspicious: Mapped[bool] = mapped_column(Boolean, default=False)


class ModelRun(Base):
    __tablename__ = "model_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    model_name: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32))
    metrics_json: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
