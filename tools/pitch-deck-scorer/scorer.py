"""
Pitch Deck Scorer
==================
Interactive self-assessment checklist for your pitch deck.
Rate each slide against best practices distilled from 500+ funded decks.
Get a readiness score, prioritized fixes, and export to JSON.

Usage:
    python scorer.py              # Interactive mode
    python scorer.py --example    # Run with example responses
    python scorer.py --export     # Export results to JSON file after scoring
    python scorer.py -e           # Short form of --example
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
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


def export_results(
    total_score: int,
    max_score: int,
    breakdown: list[SlideBreakdown],
    filepath: str | None = None,
) -> str:
    """Export scoring results to a JSON file and return the absolute path."""
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

    data = {
        "score": total_score,
        "max_score": max_score,
        "percentage": round(overall_pct, 1),
        "verdict": verdict,
        "verdict_message": verdict_msg,
        "slides": [
            {
                "slide": b["slide"],
                "passed": b["passed"],
                "total": b["total"],
                "percentage": round(b["pct"], 1),
                "weight": b["weight"],
                "missed_criteria": b["missed"],
            }
            for b in breakdown
        ],
    }

    if filepath is None:
        filepath = str(Path(__file__).parent / "pitch_deck_score.json")
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return str(Path(filepath).resolve())


def print_scorecard(
    total_score: int, max_score: int, breakdown: list[SlideBreakdown]
) -> None:
    """Print a formatted pitch deck scorecard."""
    overall_pct = (total_score / max_score) * 100 if max_score > 0 else 0

    print("\n" + "=" * 65)
    print("  PITCH DECK SCORECARD")
    print("=" * 65)

    print(f"\n  Overall Score: {total_score}/{max_score} ({overall_pct:.0f}%)")

    if overall_pct >= 80:
        verdict = "[READY] Investor-ready. Send it."
    elif overall_pct >= 60:
        verdict = "[NEEDS WORK] Good foundation. Fix highlighted gaps before sending."
    else:
        verdict = "[NOT READY] Needs significant work. Don't send this to investors yet."

    print(f"  Verdict: {verdict}")

    print("\n" + "-" * 65)
    print(f"  {'Slide':<25} {'Score':>6} {'Weight':>7}")
    print("-" * 65)

    for b in breakdown:
        filled = int(b["pct"] / 10)
        bar = "#" * filled + "-" * (10 - filled)
        print(
            f"  {b['slide']:<25} {bar} {b['pct']:>4.0f}%  (x{b['weight']})"
        )

    print("-" * 65)

    # Priority fixes: slides with missed items, sorted by weight DESC then % ASC
    print("\n" + "=" * 65)
    print("  PRIORITY FIXES")
    print("=" * 65)

    priority_order = sorted(
        breakdown,
        key=lambda x: (-x["weight"], x["pct"]),
    )
    for b in priority_order:
        if b["missed"]:
            print(f"\n  [{b['slide']}] (weight: x{b['weight']})")
            for item in b["missed"]:
                print(f"  - {item}")

    print()


def interactive_mode(export: bool = False) -> None:
    """Walk user through each slide's checklist."""
    print("\n" + "=" * 55)
    print("  PITCH DECK SCORER")
    print("=" * 55)
    print("\nFor each criterion, answer Y (yes / present) or N (no / missing).")
    print("Be honest — inflating scores only hurts you when investors push back.\n")

    responses: dict[int, list[bool]] = {}
    for i, slide in enumerate(DECK_CRITERIA):
        print(f"\n--- {slide.slide_name} ---")
        checks: list[bool] = []
        for criterion in slide.criteria:
            ans = input(f"  [{criterion}]  (y/n): ").strip().lower()
            checks.append(ans.startswith("y"))
        responses[i] = checks

    total, max_score, breakdown = score_deck(responses)
    print_scorecard(total, max_score, breakdown)

    if export:
        filepath = export_results(total, max_score, breakdown)
        print(f"Results exported to: {filepath}")


def run_example(export: bool = False) -> None:
    """Run with example responses for a decent-but-not-perfect deck."""
    responses: dict[int, list[bool]] = {
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

    total, max_score, breakdown = score_deck(responses)
    print_scorecard(total, max_score, breakdown)

    if export:
        filepath = export_results(total, max_score, breakdown)
        print(f"Results exported to: {filepath}")


if __name__ == "__main__":
    export_flag = "--export" in sys.argv
    if "--example" in sys.argv or "-e" in sys.argv:
        run_example(export=export_flag)
    else:
        interactive_mode(export=export_flag)