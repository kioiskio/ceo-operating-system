"""SaaS metrics health check domain logic (pure computation, no I/O)."""

from __future__ import annotations

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


def compute_runway(inputs: SaaSInputs) -> float | None:
    """Runway in months; None when there is no burn."""
    return inputs.cash_on_hand / inputs.burn_rate_monthly if inputs.burn_rate_monthly > 0 else None


def assess_runway(runway_months: float | None) -> tuple[str, str]:
    """Classify runway as GREEN / AMBER / RED with its recommendation."""
    if runway_months is None:
        return ("GREEN", "No burn detected. Verify this is intentional (profitable or pre-launch).")
    if runway_months >= 18:
        return ("GREEN", "Comfortable runway. You have time to experiment and get PMF right.")
    if runway_months >= 12:
        return ("AMBER", "12-18 months. Start planning your next raise now, not later.")
    return ("RED", "Under 12 months runway. Fundraise immediately or cut burn drastically.")
