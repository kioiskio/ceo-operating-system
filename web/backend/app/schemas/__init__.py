"""Pydantic request/response models matching the fixed API contract."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


# ---------- SaaS health ----------

class SaaSHealthRequest(BaseModel):
    arr: float = Field(ge=0)
    arr_growth_yoy: float = Field(ge=0)
    monthly_churn: float = Field(ge=0)
    net_revenue_retention: float = Field(ge=0)
    cac_payback_months: float = Field(ge=0)
    gross_margin: float = Field(ge=0)
    burn_rate_monthly: float = Field(ge=0)
    cash_on_hand: float = Field(ge=0)


class MetricEntry(BaseModel):
    key: str
    label: str
    value: float | None
    unit: str
    status: Literal["GREEN", "AMBER", "RED"]
    green_range: str
    amber_range: str
    red_range: str
    recommendation: str


class SaaSHealthResponse(BaseModel):
    run_id: int
    runway_months: float | None
    metrics: list[MetricEntry]
    score: int
    summary: str


# ---------- Equity dilution ----------

class RoundInput(BaseModel):
    name: str
    amount_raised: float = Field(gt=0)
    pre_money_valuation: float = Field(gt=0)
    option_pool_pct: float = Field(ge=0, lt=100)


class EquityDilutionRequest(BaseModel):
    initial_shares: float = Field(gt=0)
    founder_shares: float = Field(gt=0)
    rounds: list[RoundInput] = []


class Snapshot(BaseModel):
    stage: str
    total_shares: float
    founder_pct: float
    others_pct: float
    investor_pct: float
    cumulative_investor_pct: float
    option_pool_pct: float
    price_per_share: float | None
    pre_money: float | None
    amount_raised: float | None
    post_money: float | None


class DilutionSummary(BaseModel):
    initial_founder_pct: float
    final_founder_pct: float
    dilution_pp: float
    retention_pct: float


class EquityDilutionResponse(BaseModel):
    run_id: int
    snapshots: list[Snapshot]
    summary: DilutionSummary


# ---------- Deck scorer ----------

class SlideCriteriaOut(BaseModel):
    name: str
    criteria: list[str]
    weight: int


class DeckCriteriaResponse(BaseModel):
    slides: list[SlideCriteriaOut]


class DeckScoreRequest(BaseModel):
    responses: list[list[bool]]


class SlideResult(BaseModel):
    slide: str
    passed: int
    total: int
    percentage: float
    weight: int
    missed_criteria: list[str]


class PriorityFix(BaseModel):
    slide: str
    weight: int
    missed: list[str]


class DeckScoreResponse(BaseModel):
    run_id: int
    score: int
    max_score: int
    percentage: float
    verdict: str
    verdict_message: str
    slides: list[SlideResult]
    priority_fixes: list[PriorityFix]


# ---------- LLM ----------

class LLMTestRequest(BaseModel):
    base_url: str
    api_key: str
    model: str


class LLMTestResponse(BaseModel):
    ok: bool
    message: str


class LLMAnalyzeRequest(BaseModel):
    base_url: str
    api_key: str
    model: str
    tool: Literal["saas-health", "equity-dilution", "deck-score"]
    result: dict[str, Any]
    run_id: int | None = None


class LLMAnalyzeResponse(BaseModel):
    analysis: str


# ---------- History ----------

class RunSummary(BaseModel):
    id: int
    tool: str
    title: str
    score: float | None
    created_at: str


class HistoryListResponse(BaseModel):
    runs: list[RunSummary]


class RunDetail(BaseModel):
    id: int
    tool: str
    title: str
    input: dict[str, Any]
    result: dict[str, Any]
    ai_analysis: str | None
    created_at: str


class OkResponse(BaseModel):
    ok: bool


# ---------- Content ----------

class Framework(BaseModel):
    id: str
    title: str
    content: str


class FrameworksResponse(BaseModel):
    frameworks: list[Framework]


class Template(BaseModel):
    id: str
    title: str
    filename: str
    content: str


class TemplatesResponse(BaseModel):
    templates: list[Template]
