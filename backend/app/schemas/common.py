from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class HealthResponse(BaseModel):
    status: str
    app: str
    database: str


class TopDriver(BaseModel):
    feature: str
    contribution: float
    description: str


class ExplainabilityPayload(BaseModel):
    score: float
    severity: str
    confidence: float
    top_drivers: list[TopDriver]
    explanation: str
    suggested_action: str


class PaginatedMeta(BaseModel):
    total: int
    page: int
    page_size: int


class TimeSeriesPoint(BaseModel):
    timestamp: datetime
    value: float
    label: str | None = None


class HeatmapCell(BaseModel):
    row: str
    col: str
    value: float
    label: str | None = None


class DemoScenario(BaseModel):
    id: str
    name: str
    description: str
    scenario_tag: str
    walkthrough: list[str]


class SeedRequest(BaseModel):
    days: int = Field(default=30, ge=7, le=90)
    scenarios: list[str] = Field(default_factory=lambda: ["all"])


class SeedResponse(BaseModel):
    message: str
    stocks: int
    traders: int
    trades: int
    alerts: int
    scenarios_embedded: list[str]
