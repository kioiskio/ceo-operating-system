"""
Equity Dilution Calculator
===========================
Model how fundraising rounds dilute founder ownership over multiple rounds.
Includes option pool expansion and cap table visualization.

Usage:
    python equity_calc.py              # Interactive mode
    python equity_calc.py --example    # Run with example data
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import sys


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


def format_dollars(value: float) -> str:
    if value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f}B"
    if value >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    if value >= 1_000:
        return f"${value / 1_000:.0f}K"
    return f"${value:.0f}"


def print_cap_table(snapshots: list[dict[str, Any]]) -> None:
    """Print a formatted cap table with dilution waterfall."""
    print("\n" + "=" * 98)
    print("  CAP TABLE & DILUTION WATERFALL")
    print("=" * 98)

    header = (
        f"{'Stage':<12} {'Founder %':>9} {'Others %':>8} "
        f"{'New Inv %':>9} {'Cum.Inv %':>9} {'Pool %':>7} "
        f"{'Price/Sh':>10} {'Post-$':>12}"
    )
    print(header)
    print("-" * 98)

    for s in snapshots:
        price = format_dollars(s["price_per_share"]) if s["price_per_share"] else "—"
        post = format_dollars(s["post_money"]) if s["post_money"] else "—"
        print(
            f"{s['stage']:<12} {s['founder_pct']:>8.2f}% {s['others_pct']:>7.2f}% "
            f"{s['investor_pct']:>8.2f}% {s['cumulative_investor_pct']:>8.2f}% "
            f"{s['option_pool_pct']:>6.2f}% {price:>10} {post:>12}"
        )

    print("=" * 98)

    initial = snapshots[0]
    final = snapshots[-1]
    dilution = initial["founder_pct"] - final["founder_pct"]
    print(
        f"\nFounder dilution: {initial['founder_pct']:.1f}% → {final['founder_pct']:.1f}%  "
        f"(lost {dilution:.1f} pp)"
    )
    print(
        f"Effective ownership retained: "
        f"{(final['founder_pct'] / initial['founder_pct']) * 100:.1f}%"
    )


def _parse_nonnegative(msg: str) -> float:
    """Prompt user for a non-negative numeric value, retrying on invalid input."""
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
        if val < 0:
            print(f"  Value cannot be negative. Please enter a non-negative number.")
            continue
        return val


def interactive_mode() -> None:
    """Prompt user for inputs interactively with validation."""
    print("\n" + "=" * 50)
    print("  EQUITY DILUTION CALCULATOR")
    print("=" * 50)

    while True:
        initial = _parse_nonnegative("\nTotal initial shares (e.g. 10000000): ")
        if initial > 0:
            break
        print("  Total initial shares must be greater than 0. Please try again.")
    while True:
        founder_pct = _parse_nonnegative("Founder ownership % at start (e.g. 80): ")
        if founder_pct > 100:
            print("  Founder ownership cannot exceed 100%. Please try again.")
            continue
        if founder_pct == 0:
            print("  Founder ownership cannot be 0%. Please enter a positive number.")
            continue
        break
    founder_shares = initial * (founder_pct / 100)

    rounds: list[Round] = []
    num_rounds = int(_parse_nonnegative("Number of funding rounds to model: "))

    for i in range(num_rounds):
        print(f"\n--- Round {i + 1} ---")
        name = input("Round name (e.g. Seed, Series A): ").strip()
        while True:
            amount = _parse_nonnegative("Amount raised (e.g. 2000000): ")
            if amount > 0:
                break
            print("  Amount raised must be greater than 0. Please try again.")
        while True:
            pre = _parse_nonnegative("Pre-money valuation (e.g. 8000000): ")
            if pre > 0:
                break
            print("  Pre-money valuation must be greater than 0. Please try again.")
        pool_input = input("Option pool increase % before round (0 if none): ").strip()
        try:
            pool_pct = float(pool_input) if pool_input else 0.0
        except ValueError:
            pool_pct = 0.0
            print(f"  '{pool_input}' is not a valid number. Using 0%.")
        if pool_pct < 0 or pool_pct >= 100:
            pool_pct = 0.0
            print("  Invalid pool %. Using 0%.")
        rounds.append(
            Round(name=name, amount_raised=amount, pre_money_valuation=pre, option_pool_pct=pool_pct)
        )

    snapshots = calculate_dilution(initial, founder_shares, rounds)
    print_cap_table(snapshots)


def run_example() -> None:
    """Run with pre-built example data (seed → Series A → Series B)."""
    initial = 10_000_000
    founder_shares = 8_000_000  # 80%

    rounds = [
        Round(name="Seed", amount_raised=2_000_000, pre_money_valuation=8_000_000, option_pool_pct=10),
        Round(name="Series A", amount_raised=10_000_000, pre_money_valuation=30_000_000, option_pool_pct=5),
        Round(name="Series B", amount_raised=25_000_000, pre_money_valuation=100_000_000, option_pool_pct=0),
    ]

    print("\nExample: Founder starts with 80%, raises Seed → Series A → Series B")
    print(
        f"Initial shares: {initial:,}  |  Founder shares: {founder_shares:,}"
        f"  |  Others (co-founders/employees): {initial - founder_shares:,}\n"
    )

    for r in rounds:
        print(
            f"  {r.name}: raise {format_dollars(r.amount_raised)} at "
            f"{format_dollars(r.pre_money_valuation)} pre-money, "
            f"option pool +{r.option_pool_pct}%"
        )

    snapshots = calculate_dilution(initial, founder_shares, rounds)
    print_cap_table(snapshots)


if __name__ == "__main__":
    if "--example" in sys.argv or "-e" in sys.argv:
        run_example()
    else:
        interactive_mode()