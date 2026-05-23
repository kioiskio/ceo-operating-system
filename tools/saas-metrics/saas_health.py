"""
SaaS Metrics Health Checker
============================
Plug in your key SaaS metrics and get an instant health diagnosis with
red/amber/green indicators and actionable recommendations.

Usage:
    python saas_health.py              # Interactive mode
    python saas_health.py --example    # Run with example data
"""

from __future__ import annotations

import sys
from dataclasses import dataclass


@dataclass
class SaaSInputs:
    arr: float
    arr_growth_yoy: float
    monthly_churn: float
    net_revenue_retention: float
    cac_payback_months: float
    gross_margin: float
    burn_rate_monthly: float
    cash_on_hand: float


@dataclass
class Threshold:
    """Green / amber / red boundary values. `higher_is_better` controls comparison direction."""
    green: float
    amber: float
    red: float
    higher_is_better: bool = True


@dataclass
class Indicator:
    label: str
    value_key: str
    unit: str
    threshold: Threshold
    green_range: str
    amber_range: str
    red_range: str
    recommendation_green: str
    recommendation_amber: str
    recommendation_red: str


METRICS: list[Indicator] = [
    Indicator(
        label="YoY ARR Growth",
        value_key="arr_growth_yoy",
        unit="%",
        threshold=Threshold(green=100, amber=50, red=0, higher_is_better=True),
        green_range=">=100% (early-stage benchmark)",
        amber_range="50-100%",
        red_range="<50%",
        recommendation_green="Growth is strong. Focus on efficiency, not just top-line.",
        recommendation_amber="Growth is decent but not exceptional. Diagnose: is it market, product, or GTM?",
        recommendation_red="Growth is below venture-scale thresholds. Pivot GTM or reassess PMF.",
    ),
    Indicator(
        label="Monthly Churn",
        value_key="monthly_churn",
        unit="%",
        threshold=Threshold(green=2, amber=5, red=100, higher_is_better=False),
        green_range="<=2% (SMB) / <=1% (Enterprise)",
        amber_range="2-5% (SMB) / 1-2% (Enterprise)",
        red_range=">5% (SMB) / >2% (Enterprise)",
        recommendation_green="Retention is healthy. Invest in expansion revenue.",
        recommendation_amber="Churn is eating your growth. Audit onboarding and first 30-day experience.",
        recommendation_red="Critical churn problem. Stop all outbound sales until you fix retention.",
    ),
    Indicator(
        label="Net Revenue Retention",
        value_key="net_revenue_retention",
        unit="%",
        threshold=Threshold(green=120, amber=100, red=0, higher_is_better=True),
        green_range=">=120%",
        amber_range="100-120%",
        red_range="<100%",
        recommendation_green="Expansion is outpacing churn. You have a growth engine within your base.",
        recommendation_amber="You're treading water. Focus on upsells and cross-sells.",
        recommendation_red="Your customer base is shrinking. Expansion revenue is negative.",
    ),
    Indicator(
        label="CAC Payback",
        value_key="cac_payback_months",
        unit="months",
        threshold=Threshold(green=12, amber=18, red=1000, higher_is_better=False),
        green_range="<=12 months",
        amber_range="12-18 months",
        red_range=">18 months",
        recommendation_green="Efficient GTM. Can scale spend confidently.",
        recommendation_amber="Payback is borderline. Optimize sales efficiency before scaling.",
        recommendation_red="Too expensive to acquire customers. Rethink channels or pricing.",
    ),
    Indicator(
        label="Gross Margin",
        value_key="gross_margin",
        unit="%",
        threshold=Threshold(green=80, amber=60, red=0, higher_is_better=True),
        green_range=">=80%",
        amber_range="60-80%",
        red_range="<60%",
        recommendation_green="Healthy SaaS margin. Infrastructure costs are well-controlled.",
        recommendation_amber="Below best-in-class. Audit COGS: hosting, support, third-party fees.",
        recommendation_red="Not a SaaS margin. If this is structural, you may not have a SaaS business model.",
    ),
]


def color_for_status(status: str) -> str:
    """Return ANSI-colored status label."""
    colors = {"GREEN": "\033[92m", "AMBER": "\033[93m", "RED": "\033[91m"}
    reset = "\033[0m"
    return f"{colors.get(status, '')}{status}{reset}"


def assess(indicator: Indicator, value: float) -> tuple[str, str]:
    """
    Classify a metric value as GREEN / AMBER / RED using
    the indicator's built-in threshold configuration.
    """
    t = indicator.threshold
    if t.higher_is_better:
        if value >= t.green:
            return ("GREEN", indicator.recommendation_green)
        if value >= t.amber:
            return ("AMBER", indicator.recommendation_amber)
        return ("RED", indicator.recommendation_red)
    else:
        if value <= t.green:
            return ("GREEN", indicator.recommendation_green)
        if value <= t.amber:
            return ("AMBER", indicator.recommendation_amber)
        return ("RED", indicator.recommendation_red)


def health_score(results: list[tuple[str, str, str, float | None]]) -> tuple[int, str]:
    """Calculate overall health score: GREEN=2, AMBER=1, RED=0."""
    score_map = {"GREEN": 2, "AMBER": 1, "RED": 0}
    total = sum(score_map[r[0]] for r in results)
    max_score = len(results) * 2
    pct = int((total / max_score) * 100)

    if pct >= 83:
        return (pct, "Healthy — You're in a strong position. Keep executing.")
    if pct >= 50:
        return (pct, "Needs Attention — Several metrics need work before you're fundable.")
    return (pct, "Critical — Address red flags before seeking external capital.")


def print_report(inputs: SaaSInputs, runway_months: float | None) -> None:
    """Print a formatted health report with per-metric RAG status and recommendations."""
    print("\n" + "=" * 70)
    print("  SaaS METRICS HEALTH REPORT")
    print("=" * 70)

    runway_display = (
        f"Runway: {runway_months:.1f} months"
        if runway_months is not None
        else "Runway: N/A (no burn)"
    )
    print(
        f"\n  ARR: ${inputs.arr:,.0f}  |  Growth: {inputs.arr_growth_yoy:.1f}%  |  "
        f"{runway_display}  |  Burn: ${inputs.burn_rate_monthly:,.0f}/mo"
    )
    print(f"  Cash: ${inputs.cash_on_hand:,.0f}")

    print("\n" + "-" * 70)
    print(f"  {'Metric':<28} {'Value':>10} {'Status':>8}")
    print("-" * 70)

    results: list[tuple[str, str, str, float | None]] = []
    for m in METRICS:
        val = getattr(inputs, m.value_key, 0)
        status, rec = assess(m, val)
        results.append((status, rec, m.label, val))
        print(f"  {m.label:<28} {val:>8.1f}{m.unit:<4} {color_for_status(status):>16}")

    # Runway as a separate line (not in METRICS dataclass since it's derived)
    if runway_months is not None:
        if runway_months >= 18:
            runway_status = "GREEN"
            runway_rec = "Comfortable runway. You have time to experiment and get PMF right."
        elif runway_months >= 12:
            runway_status = "AMBER"
            runway_rec = "12-18 months. Start planning your next raise now, not later."
        else:
            runway_status = "RED"
            runway_rec = "Under 12 months runway. Fundraise immediately or cut burn drastically."
    else:
        runway_status = "GREEN"
        runway_rec = "No burn detected. Verify this is intentional (profitable or pre-launch)."

    results.append((runway_status, runway_rec, "Runway", runway_months if runway_months is not None else None))
    print(
        f"  {'Runway':<28} "
        f"{f'{runway_months:>8.1f}months' if runway_months is not None else '     N/A':>12} "
        f"{color_for_status(runway_status):>16}"
    )

    print("-" * 70)

    score, summary = health_score(results)
    print(f"\n  Overall Health Score: {score}/100  —  {summary}")

    print("\n" + "=" * 70)
    print("  RECOMMENDATIONS")
    print("=" * 70)
    for status, rec, label, _ in results:
        if status != "GREEN":
            print(f"\n  [{status}] {label}")
            print(f"  → {rec}")
    print()


def _parse_numeric(msg: str) -> float:
    """Prompt user for a numeric value, retrying on invalid input."""
    while True:
        raw = input(msg).replace(",", "").replace("$", "").replace("%", "").strip()
        if not raw:
            print("  Value cannot be empty. Please enter a number.")
            continue
        try:
            val = float(raw)
        except ValueError:
            print(f"  '{raw}' is not a valid number. Please try again.")
            continue
        return val


def _parse_nonnegative(msg: str) -> float:
    """Prompt user for a non-negative numeric value."""
    while True:
        val = _parse_numeric(msg)
        if val < 0:
            print(f"  Value cannot be negative. Please try again.")
            continue
        return val


def interactive_mode() -> None:
    """Prompt user for SaaS metrics interactively with validation."""
    print("\n" + "=" * 50)
    print("  SaaS METRICS HEALTH CHECKER")
    print("=" * 50)

    arr = _parse_nonnegative("\nAnnual Recurring Revenue ($): ")
    growth = _parse_nonnegative("YoY ARR Growth rate (%): ")
    churn = _parse_nonnegative("Monthly logo churn rate (%): ")
    nrr = _parse_nonnegative("Net Revenue Retention (%): ")
    cac = _parse_nonnegative("CAC payback period (months): ")
    gm = _parse_nonnegative("Gross Margin (%): ")

    burn = _parse_nonnegative("Monthly net burn rate ($): ")

    cash = _parse_nonnegative("Cash on hand ($): ")

    inputs = SaaSInputs(
        arr=arr,
        arr_growth_yoy=growth,
        monthly_churn=churn,
        net_revenue_retention=nrr,
        cac_payback_months=cac,
        gross_margin=gm,
        burn_rate_monthly=burn,
        cash_on_hand=cash,
    )
    runway = cash / burn if burn > 0 else None
    print_report(inputs, runway)


def run_example() -> None:
    """Run with example data for a typical early-stage SaaS."""
    inputs = SaaSInputs(
        arr=1_200_000,
        arr_growth_yoy=85,
        monthly_churn=3.2,
        net_revenue_retention=105,
        cac_payback_months=14,
        gross_margin=78,
        burn_rate_monthly=80_000,
        cash_on_hand=1_500_000,
    )
    runway = inputs.cash_on_hand / inputs.burn_rate_monthly
    print_report(inputs, runway)


if __name__ == "__main__":
    if "--example" in sys.argv or "-e" in sys.argv:
        run_example()
    else:
        interactive_mode()