"""Routes for the three founder tools."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from .. import db
from ..domain.deck_scorer import DECK_CRITERIA, score_deck, verdict_for
from ..domain.equity_calc import Round, calculate_dilution, dilution_summary
from ..domain.saas_health import (
    METRICS,
    SaaSInputs,
    assess,
    assess_runway,
    compute_runway,
    health_score,
)
from ..schemas import (
    DeckCriteriaResponse,
    DeckScoreRequest,
    DeckScoreResponse,
    EquityDilutionRequest,
    EquityDilutionResponse,
    MetricEntry,
    PriorityFix,
    SaaSHealthRequest,
    SaaSHealthResponse,
    SlideCriteriaOut,
    SlideResult,
    Snapshot,
)

router = APIRouter(prefix="/tools", tags=["tools"])


@router.post("/saas-health", response_model=SaaSHealthResponse)
def saas_health(req: SaaSHealthRequest) -> SaaSHealthResponse:
    inputs = SaaSInputs(**req.model_dump())
    runway_months = compute_runway(inputs)

    results: list[tuple[str, str, str, float | None]] = []
    metrics: list[MetricEntry] = []
    for m in METRICS:
        val = getattr(inputs, m.value_key, 0)
        status, rec = assess(m, val)
        results.append((status, rec, m.label, val))
        metrics.append(
            MetricEntry(
                key=m.value_key,
                label=m.label,
                value=val,
                unit=m.unit,
                status=status,  # type: ignore[arg-type]
                green_range=m.green_range,
                amber_range=m.amber_range,
                red_range=m.red_range,
                recommendation=rec,
            )
        )

    runway_status, runway_rec = assess_runway(runway_months)
    results.append((runway_status, runway_rec, "Runway", runway_months))
    metrics.append(
        MetricEntry(
            key="runway",
            label="Runway",
            value=runway_months,
            unit="months",
            status=runway_status,  # type: ignore[arg-type]
            green_range=">=18 months",
            amber_range="12-18 months",
            red_range="<12 months",
            recommendation=runway_rec,
        )
    )

    score, summary = health_score(results)

    response = SaaSHealthResponse(
        run_id=-1,
        runway_months=runway_months,
        metrics=metrics,
        score=score,
        summary=summary,
    )
    run_id = db.insert_run(
        tool="saas-health",
        title=f"SaaS Health Check · {score} pts",
        score=float(score),
        input_data=req.model_dump(),
        result_data=response.model_dump(exclude={"run_id"}),
    )
    response.run_id = run_id
    return response


@router.post("/equity-dilution", response_model=EquityDilutionResponse)
def equity_dilution(req: EquityDilutionRequest) -> EquityDilutionResponse:
    rounds = [
        Round(
            name=r.name,
            amount_raised=r.amount_raised,
            pre_money_valuation=r.pre_money_valuation,
            option_pool_pct=r.option_pool_pct,
        )
        for r in req.rounds
    ]
    try:
        snapshots = calculate_dilution(req.initial_shares, req.founder_shares, rounds)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    summary = dilution_summary(snapshots)
    response = EquityDilutionResponse(
        run_id=-1,
        snapshots=[Snapshot(**s) for s in snapshots],
        summary=summary,  # type: ignore[arg-type]
    )
    num_rounds = len(rounds)
    run_id = db.insert_run(
        tool="equity-dilution",
        title=f"Equity Dilution · {num_rounds} round{'s' if num_rounds != 1 else ''}",
        score=None,
        input_data=req.model_dump(),
        result_data=response.model_dump(exclude={"run_id"}),
    )
    response.run_id = run_id
    return response


@router.get("/deck-criteria", response_model=DeckCriteriaResponse)
def deck_criteria() -> DeckCriteriaResponse:
    return DeckCriteriaResponse(
        slides=[
            SlideCriteriaOut(name=s.slide_name, criteria=s.criteria, weight=s.weight)
            for s in DECK_CRITERIA
        ]
    )


@router.post("/deck-score", response_model=DeckScoreResponse)
def deck_score(req: DeckScoreRequest) -> DeckScoreResponse:
    if len(req.responses) != len(DECK_CRITERIA):
        raise HTTPException(
            status_code=422,
            detail=(
                f"Expected {len(DECK_CRITERIA)} response arrays, "
                f"got {len(req.responses)}."
            ),
        )
    for i, (slide, checks) in enumerate(zip(DECK_CRITERIA, req.responses)):
        if len(checks) != len(slide.criteria):
            raise HTTPException(
                status_code=422,
                detail=(
                    f"Slide {i} ('{slide.slide_name}') expects "
                    f"{len(slide.criteria)} answers, got {len(checks)}."
                ),
            )

    responses = {i: list(checks) for i, checks in enumerate(req.responses)}
    total, max_score, breakdown = score_deck(responses)
    percentage, verdict, verdict_msg = verdict_for(total, max_score)

    slides = [
        SlideResult(
            slide=b["slide"],
            passed=b["passed"],
            total=b["total"],
            percentage=round(b["pct"], 1),
            weight=b["weight"],
            missed_criteria=b["missed"],
        )
        for b in breakdown
    ]
    priority_fixes = [
        PriorityFix(slide=b["slide"], weight=b["weight"], missed=b["missed"])
        for b in sorted(breakdown, key=lambda x: (-x["weight"], x["pct"]))
        if b["missed"]
    ]

    response = DeckScoreResponse(
        run_id=-1,
        score=total,
        max_score=max_score,
        percentage=percentage,
        verdict=verdict,
        verdict_message=verdict_msg,
        slides=slides,
        priority_fixes=priority_fixes,
    )
    run_id = db.insert_run(
        tool="deck-score",
        title=f"Pitch Deck Score · {percentage}%",
        score=float(percentage),
        input_data=req.model_dump(),
        result_data=response.model_dump(exclude={"run_id"}),
    )
    response.run_id = run_id
    return response
