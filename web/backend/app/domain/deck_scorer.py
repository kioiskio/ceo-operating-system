"""Pitch deck scoring domain logic (pure computation, no I/O)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypedDict


@dataclass
class SlideCriteria:
    slide_name: str
    criteria: list[str]
    weight: int = 1  # 1-3


class SlideBreakdown(TypedDict):
    slide: str
    passed: int
    total: int
    pct: float
    weight: int
    missed: list[str]


DECK_CRITERIA: list[SlideCriteria] = [
    SlideCriteria(
        "Title / One-Liner",
        [
            "Company name and logo are clear",
            "One sentence that explains what you do (mom test: would your mom get it?)",
            "No jargon, no buzzwords, no 'revolutionary' claims",
        ],
        weight=2,
    ),
    SlideCriteria(
        "Problem",
        [
            "Defines a specific, painful problem the customer has today",
            "Quantifies the problem (dollars lost, hours wasted, customers unhappy)",
            "Makes the problem visceral — investor feels the pain",
            "Avoids 'solution in search of a problem' framing",
        ],
        weight=3,
    ),
    SlideCriteria(
        "Solution",
        [
            "Shows the product (screenshot, demo, mockup — not just text)",
            "Clear value proposition: what changes for the customer after using your product?",
            "Defensible: why can't incumbents copy this in a weekend?",
            "Ties back directly to the problem slide",
        ],
        weight=3,
    ),
    SlideCriteria(
        "Market Size",
        [
            "Bottom-up TAM calculation (not just 'Gartner says $X billion')",
            "SOM (Serviceable Obtainable Market) is realistic and specific",
            "Market is growing (tailwind, not headwind)",
            "Explains why now (why hasn't this been built before?)",
        ],
        weight=2,
    ),
    SlideCriteria(
        "Traction",
        [
            "Real numbers: revenue, users, growth rate, retention — not vanity metrics",
            "Shows momentum (graph going up and right, with time axis)",
            "Explains how you got here (not just the numbers, but the story)",
            "If pre-revenue: customer letters of intent, pilot results, waitlist size",
        ],
        weight=3,
    ),
    SlideCriteria(
        "Business Model",
        [
            "Clear unit economics: how you make money per customer",
            "Pricing is specific (not 'freemium' — actual price points)",
            "Customer LTV and CAC are estimated with reasonable assumptions",
            "Shows path to profitability, not just growth at all costs",
        ],
        weight=2,
    ),
    SlideCriteria(
        "Competition",
        [
            "Honest competitive landscape (not 'we have no competitors')",
            "2x2 matrix or feature comparison table with clear differentiator",
            "Explains your unfair advantage / moat",
            "Shows awareness of indirect competition and substitutes",
        ],
        weight=2,
    ),
    SlideCriteria(
        "Go-to-Market",
        [
            "Specific channels, not 'content marketing and word of mouth'",
            "Customer acquisition cost by channel (actual data or researched estimates)",
            "Sales motion defined: self-serve, inside sales, or enterprise?",
            "Timeline: what does GTM look like over the next 6-12 months?",
        ],
        weight=2,
    ),
    SlideCriteria(
        "Team",
        [
            "Founders shown with relevant background (why *this* team?)",
            "Key hires identified and timeline for filling gaps",
            "Advisors or angels that add credibility (if relevant)",
            "No 'we'll hire someone later' for critical roles",
        ],
        weight=1,
    ),
    SlideCriteria(
        "Financials / Ask",
        [
            "Clear ask amount and use of funds (specific line items, not 'for growth')",
            "Projected runway post-raise (how many months will this last?)",
            "Key milestones you'll hit with this money",
            "Next fundraise trigger: what metrics will justify Series A?",
        ],
        weight=3,
    ),
]


def score_deck(
    responses: dict[int, list[bool]],
) -> tuple[int, int, list[SlideBreakdown]]:
    """
    Calculate pitch deck score.
    Returns (raw_score, max_possible, per_slide_breakdown).
    """
    total_score = 0
    max_score = 0
    breakdown: list[SlideBreakdown] = []

    for i, slide in enumerate(DECK_CRITERIA):
        checks: list[bool] = responses.get(i, [False] * len(slide.criteria))
        passed = sum(checks)
        total = len(checks)
        weighted_score = passed * slide.weight
        weighted_max = total * slide.weight

        total_score += weighted_score
        max_score += weighted_max

        pct = (passed / total) * 100 if total > 0 else 0
        missed: list[str] = [slide.criteria[j] for j, ok in enumerate(checks) if not ok]

        breakdown.append(
            {
                "slide": slide.slide_name,
                "passed": passed,
                "total": total,
                "pct": pct,
                "weight": slide.weight,
                "missed": missed,
            }
        )

    return total_score, max_score, breakdown


def verdict_for(total_score: int, max_score: int) -> tuple[float, str, str]:
    """Return (percentage, verdict, verdict_message) for a raw score."""
    overall_pct = (total_score / max_score) * 100 if max_score > 0 else 0

    if overall_pct >= 80:
        verdict = "READY"
        verdict_msg = "Investor-ready. Send it."
    elif overall_pct >= 60:
        verdict = "NEEDS WORK"
        verdict_msg = "Good foundation. Fix highlighted gaps before sending."
    else:
        verdict = "NOT READY"
        verdict_msg = "Needs significant work. Don't send this to investors yet."

    return round(overall_pct, 1), verdict, verdict_msg
