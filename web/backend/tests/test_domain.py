"""Pytest suite for the domain logic, ported from the original CLI unittest suite."""

from __future__ import annotations

import pytest

from app.domain.deck_scorer import DECK_CRITERIA, score_deck, verdict_for
from app.domain.equity_calc import Round, calculate_dilution, dilution_summary
from app.domain.saas_health import (
    METRICS,
    SaaSInputs,
    assess,
    assess_runway,
    compute_runway,
    health_score,
)


# ---------- SaaS health (ported from the --example run) ----------

def _example_inputs() -> SaaSInputs:
    return SaaSInputs(
        arr=1_200_000,
        arr_growth_yoy=85,
        monthly_churn=3.2,
        net_revenue_retention=105,
        cac_payback_months=14,
        gross_margin=78,
        burn_rate_monthly=80_000,
        cash_on_hand=1_500_000,
    )


def test_saas_health_example_metrics_assess_as_amber():
    inputs = _example_inputs()
    statuses = [assess(m, getattr(inputs, m.value_key))[0] for m in METRICS]
    assert statuses == ["AMBER", "AMBER", "AMBER", "AMBER", "AMBER"]


def test_saas_health_example_runway_and_score():
    inputs = _example_inputs()
    runway = compute_runway(inputs)
    assert runway == pytest.approx(18.75)

    results = [(assess(m, getattr(inputs, m.value_key))[0], "", m.label, 0.0) for m in METRICS]
    status, rec = assess_runway(runway)
    assert status == "GREEN"
    assert rec.startswith("Comfortable runway")
    results.append((status, rec, "Runway", runway))

    score, summary = health_score(results)
    # 5 AMBER (1 each) + 1 GREEN (2) = 7 of 12 -> 58
    assert score == 58
    assert summary.startswith("Needs Attention")


def test_saas_health_zero_burn_runway_is_none_and_green():
    inputs = _example_inputs()
    inputs.burn_rate_monthly = 0.0
    assert compute_runway(inputs) is None
    status, rec = assess_runway(None)
    assert status == "GREEN"
    assert rec.startswith("No burn detected")


def test_saas_health_runway_boundary_12_and_18_months():
    assert assess_runway(18.0)[0] == "GREEN"
    assert assess_runway(17.9)[0] == "AMBER"
    assert assess_runway(12.0)[0] == "AMBER"
    assert assess_runway(11.9)[0] == "RED"


def test_saas_health_all_green_score_is_100():
    inputs = SaaSInputs(
        arr=1_000_000,
        arr_growth_yoy=150,
        monthly_churn=1.0,
        net_revenue_retention=130,
        cac_payback_months=6,
        gross_margin=85,
        burn_rate_monthly=50_000,
        cash_on_hand=2_000_000,
    )
    results = [(assess(m, getattr(inputs, m.value_key))[0], "", m.label, 0.0) for m in METRICS]
    results.append((assess_runway(compute_runway(inputs))[0], "", "Runway", 0.0))
    score, summary = health_score(results)
    assert score == 100
    assert summary.startswith("Healthy")


# ---------- Equity dilution (ported from the --example run) ----------

def test_equity_example_dilution_matches_cli():
    rounds = [
        Round(name="Seed", amount_raised=2_000_000, pre_money_valuation=8_000_000, option_pool_pct=10),
        Round(name="Series A", amount_raised=10_000_000, pre_money_valuation=30_000_000, option_pool_pct=5),
        Round(name="Series B", amount_raised=25_000_000, pre_money_valuation=100_000_000, option_pool_pct=0),
    ]
    snapshots = calculate_dilution(10_000_000, 8_000_000, rounds)

    assert len(snapshots) == 4
    assert snapshots[0]["stage"] == "Initial"
    assert snapshots[0]["founder_pct"] == pytest.approx(80.0)
    assert snapshots[0]["price_per_share"] is None
    assert snapshots[0]["post_money"] is None

    for s in snapshots[1:]:
        assert s["post_money"] == s["pre_money"] + s["amount_raised"]

    # First round buckets (founder + others + investors + pool) sum to 100%.
    seed = snapshots[1]
    total_pct = (
        seed["founder_pct"] + seed["others_pct"]
        + seed["cumulative_investor_pct"] + seed["option_pool_pct"]
    )
    assert total_pct == pytest.approx(100.0)

    # Founder ownership strictly decreases each round.
    pcts = [s["founder_pct"] for s in snapshots]
    assert pcts == sorted(pcts, reverse=True) and len(set(pcts)) == len(pcts)

    summary = dilution_summary(snapshots)
    assert summary["initial_founder_pct"] == pytest.approx(80.0)
    assert summary["final_founder_pct"] < 80.0
    assert summary["dilution_pp"] == pytest.approx(
        summary["initial_founder_pct"] - summary["final_founder_pct"]
    )
    assert summary["retention_pct"] == pytest.approx(
        summary["final_founder_pct"] / summary["initial_founder_pct"] * 100
    )


def test_equity_option_pool_dilutes_founders_pre_money():
    rounds = [
        Round(name="Seed", amount_raised=1_000_000, pre_money_valuation=4_000_000, option_pool_pct=10),
    ]
    snapshots = calculate_dilution(10_000_000, 10_000_000, rounds)
    seed = snapshots[1]
    # pool shares = 10M * 10 / 90 = 1.1111M, added pre-money
    assert seed["option_pool_pct"] == pytest.approx(1_111_111.1111 / 13_888_888.8889 * 100)
    # founder 10M / (10M + 1.111M pool + 2.778M new) = 72%
    assert seed["founder_pct"] == pytest.approx(72.0)
    assert seed["cumulative_investor_pct"] == pytest.approx(20.0)


def test_equity_empty_rounds_returns_only_initial():
    snapshots = calculate_dilution(1_000, 500, [])
    assert len(snapshots) == 1
    assert snapshots[0]["founder_pct"] == pytest.approx(50.0)
    summary = dilution_summary(snapshots)
    assert summary["dilution_pp"] == pytest.approx(0.0)
    assert summary["retention_pct"] == pytest.approx(100.0)


@pytest.mark.parametrize(
    "initial,founder,rounds",
    [
        (0, 0, []),
        (100, 0, []),
        (100, 200, []),
        (100, 50, [Round("Bad", 0, 1_000_000)]),
        (100, 50, [Round("Bad", 1_000, 0)]),
        (100, 50, [Round("Bad", 1_000, 1_000_000, option_pool_pct=100)]),
    ],
)
def test_equity_invalid_inputs_raise_value_error(initial, founder, rounds):
    with pytest.raises(ValueError):
        calculate_dilution(initial, founder, rounds)


# ---------- Deck scorer (ported from the --example run) ----------

EXAMPLE_RESPONSES: dict[int, list[bool]] = {
    0: [True, True, False],
    1: [True, True, True, True],
    2: [True, True, False, True],
    3: [True, False, True, False],
    4: [True, True, False, False],
    5: [True, False, False, True],
    6: [False, True, True, True],
    7: [True, False, True, False],
    8: [True, True, False, False],
    9: [False, False, True, True],
}


def test_deck_criteria_has_10_slides():
    assert len(DECK_CRITERIA) == 10
    assert DECK_CRITERIA[0].slide_name == "Title / One-Liner"
    assert DECK_CRITERIA[-1].slide_name == "Financials / Ask"


def test_deck_example_score_and_verdict():
    total, max_score, breakdown = score_deck(EXAMPLE_RESPONSES)
    assert max_score == sum(len(s.criteria) * s.weight for s in DECK_CRITERIA)
    assert len(breakdown) == 10
    # Title slide: 2 of 3 passed -> 1 missed criterion
    assert breakdown[0]["passed"] == 2
    assert len(breakdown[0]["missed"]) == 1

    percentage, verdict, _ = verdict_for(total, max_score)
    assert percentage == pytest.approx(round(total / max_score * 100, 1))
    assert 60 <= percentage < 80
    assert verdict == "NEEDS WORK"


def test_deck_all_true_is_ready_all_false_is_not_ready():
    all_true = {i: [True] * len(s.criteria) for i, s in enumerate(DECK_CRITERIA)}
    total, max_score, _ = score_deck(all_true)
    assert total == max_score
    pct, verdict, _ = verdict_for(total, max_score)
    assert pct == 100.0
    assert verdict == "READY"

    all_false = {i: [False] * len(s.criteria) for i, s in enumerate(DECK_CRITERIA)}
    total0, max0, breakdown0 = score_deck(all_false)
    assert total0 == 0
    pct0, verdict0, _ = verdict_for(total0, max0)
    assert pct0 == 0.0
    assert verdict0 == "NOT READY"
    assert all(len(b["missed"]) == b["total"] for b in breakdown0)


def test_deck_verdict_boundary_80_percent():
    # weight-3 slide with 4 criteria: 16 of 20 points = 80%
    total, max_score = 16, 20
    pct, verdict, msg = verdict_for(total, max_score)
    assert pct == 80.0
    assert verdict == "READY"
    assert msg == "Investor-ready. Send it."
