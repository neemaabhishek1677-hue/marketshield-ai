from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import ORMBase, TopDriver


class AlertCommentCreate(BaseModel):
    body: str
    author: str = "analyst"


class AlertCommentOut(ORMBase):
    id: int
    author: str
    body: str
    created_at: datetime


class AlertOut(ORMBase):
    id: int
    alert_type: str
    stock_id: int | None
    trader_id: int | None
    severity: str
    confidence: float
    risk_score: float
    title: str
    explanation: str
    top_drivers: str
    suggested_action: str
    status: str
    scenario_tag: str | None
    created_at: datetime
    updated_at: datetime


class AlertUpdate(BaseModel):
    status: str | None = None


class AlertDetail(AlertOut):
    ticker: str | None = None
    trader_external_id: str | None = None
    drivers_parsed: list[TopDriver] = []
