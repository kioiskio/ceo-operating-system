# Tool Invocation Protocol

All paths are relative to the **skill root** (directory containing `SKILL.md`).

## Hard rule

When the user supplies **numeric inputs** that match a tool below, **run the script** and base advice on its output. Do not invent health scores, dilution percentages, or deck scores in prose.

Use the Shell tool from the consuming project's workspace, or ask the user to run the command if execution is blocked.

---

## SaaS Metrics Health Checker

**When:** User asks if metrics are fundable, runway, churn, NRR, SaaS health, or fundraising readiness with ARR/burn numbers.

```bash
python tools/saas-metrics/saas_health.py              # interactive
python tools/saas-metrics/saas_health.py --example      # demo report
python tools/saas-metrics/saas_health.py -e
```

**Inputs needed:** ARR, YoY growth %, monthly churn %, NRR %, CAC payback months, gross margin %, monthly burn, cash on hand.

**Output:** RAG per metric, score /100, recommendations for non-green metrics.

**Stage note:** Thresholds target **early-stage venture-scale SMB SaaS**; say so if user is bootstrap/profitable.

---

## Equity Dilution Calculator

**When:** User asks about dilution, cap table, option pool, seed/Series A/B ownership, or "how much will I own after raising."

```bash
python tools/equity-calculator/equity_calc.py
python tools/equity-calculator/equity_calc.py --example
python tools/equity-calculator/equity_calc.py -e
```

**Output:** Cap table waterfall, founder % after each round, cumulative investor %.

**Pair with:** [fundraising.md](fundraising.md) for raise size / dilution targets.

---

## Pitch Deck Scorer

**When:** User preparing investor deck, pitch review, or "is my deck ready."

```bash
python tools/pitch-deck-scorer/scorer.py
python tools/pitch-deck-scorer/scorer.py --example
python tools/pitch-deck-scorer/scorer.py --export    # writes pitch_deck_score.json
```

**Also load:** [templates/pitch-deck-outline.md](../templates/pitch-deck-outline.md) for slide structure.

**Limitation:** Self-assessment checklist only — cannot parse PDF/PPTX decks.

---

## Templates (no script)

| Template | Path | Use when |
|----------|------|----------|
| Pitch deck outline | `templates/pitch-deck-outline.md` | Building or restructuring a deck |
| 1:1 agenda | `templates/one-on-one-agenda.md` | Founder ↔ report meetings |

See [templates-index.md](templates-index.md).

---

## Suggested workflows

| User intent | Load | Run |
|-------------|------|-----|
| Should we raise? | `fundraising.md` | `saas_health.py` if SaaS metrics exist |
| PMF check | `pmf.md` | `saas_health.py` if SaaS |
| Model dilution | `fundraising.md` | `equity_calc.py` |
| Deck ready? | `templates/pitch-deck-outline.md` | `scorer.py` |

---

## Disclaimer

Tools produce **decision support**, not legal, tax, or investment advice. Equity math is illustrative; term sheets vary (SAFE vs priced, pro-rata, etc.).
