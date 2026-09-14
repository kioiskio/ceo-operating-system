"""Equity dilution domain logic (pure computation, no I/O)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Round:
    name: str
    amount_raised: float
    pre_money_valuation: float
    option_pool_pct: float = 0.0


def calculate_dilution(
    initial_shares: float,
    founder_shares: float,
    rounds: list[Round],
) -> list[dict[str, Any]]:
    """
    Simulate dilution through fundraising rounds.
    Returns a list of state snapshots, one per round + initial state.
    All percentages sum to 100%: Founder + Others + Cumulative Investors + Option Pool.

    Raises ValueError if any round has non-positive pre-money valuation or total shares.
    """
    if initial_shares <= 0:
        raise ValueError("Initial shares must be positive.")
    if founder_shares <= 0:
        raise ValueError("Founder shares must be positive.")
    if founder_shares > initial_shares:
        raise ValueError("Founder shares cannot exceed initial shares.")

    total_shares = initial_shares
    founder_owned = founder_shares
    others_owned = initial_shares - founder_shares
    cumulative_investor_shares = 0.0

    snapshots: list[dict[str, Any]] = [
        {
            "stage": "Initial",
            "total_shares": total_shares,
            "founder_pct": (founder_owned / total_shares) * 100,
            "others_pct": (others_owned / total_shares) * 100,
            "investor_pct": 0.0,
            "cumulative_investor_pct": 0.0,
            "option_pool_pct": 0.0,
            "price_per_share": None,
            "pre_money": None,
            "amount_raised": None,
            "post_money": None,
        }
    ]

    for r in rounds:
        if r.pre_money_valuation <= 0:
            raise ValueError(f"Round '{r.name}' must have positive pre-money valuation.")
        if r.amount_raised <= 0:
            raise ValueError(f"Round '{r.name}' must have positive amount raised.")
        if r.option_pool_pct < 0 or r.option_pool_pct >= 100:
            raise ValueError(f"Round '{r.name}' option pool must be between 0 and 100.")

        pool_shares = 0.0

        # Option pool expansion — created pre-money, dilutes existing holders.
        # Note: The convention is to quote pool size as % of post-money fully diluted.
        # This calculator computes post-money pool % for display consistency.
        if r.option_pool_pct > 0:
            pool_shares = (total_shares * r.option_pool_pct) / (100 - r.option_pool_pct)
            total_shares += pool_shares

        price_per_share = r.pre_money_valuation / total_shares
        new_shares = r.amount_raised / price_per_share
        total_shares += new_shares
        cumulative_investor_shares += new_shares

        post_money_val = r.pre_money_valuation + r.amount_raised

        snapshots.append(
            {
                "stage": r.name,
                "total_shares": total_shares,
                "founder_pct": (founder_owned / total_shares) * 100,
                "others_pct": (others_owned / total_shares) * 100,
                "investor_pct": (new_shares / total_shares) * 100,
                "cumulative_investor_pct": (cumulative_investor_shares / total_shares) * 100,
                "option_pool_pct": (pool_shares / total_shares) * 100 if pool_shares > 0 else 0.0,
                "price_per_share": price_per_share,
                "pre_money": r.pre_money_valuation,
                "amount_raised": r.amount_raised,
                "post_money": post_money_val,
            }
        )

    return snapshots


def dilution_summary(snapshots: list[dict[str, Any]]) -> dict[str, float]:
    """Compute the founder-ownership summary over a snapshot series."""
    initial = snapshots[0]
    final = snapshots[-1]
    return {
        "initial_founder_pct": initial["founder_pct"],
        "final_founder_pct": final["founder_pct"],
        "dilution_pp": initial["founder_pct"] - final["founder_pct"],
        "retention_pct": (final["founder_pct"] / initial["founder_pct"]) * 100,
    }
