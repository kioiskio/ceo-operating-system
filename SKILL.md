---
name: ceo-operating-system
description: >-
  Founder CEO operating system: run Python tools for SaaS health scoring, equity
  dilution modeling, and pitch deck readiness; apply fundraising and PMF
  frameworks; use pitch deck and 1:1 templates. Use when user asks about
  fundraising, runway, cap table, dilution, investor deck, PMF, SaaS metrics,
  ARR, churn, or founder operating decisions. Run tools for numbers — do not
  guess scores. Not legal or investment advice.
license: MIT
metadata:
  version: "1.1.0"
  author: "kimogrant"
  display_name: "CEO Operating System"
  tags: "founder, startup, fundraising, saas, cap-table, pitch-deck, pmf"
  language: en
---

# CEO Operating System

> Runnable founder tools + decision frameworks · Not a bookmark list  
> Compatible with Cursor · Claude Code · Codex · OpenCode · Gemini CLI  
> Sibling skills: [clinical-skills](https://github.com/kimogrant/clinical-skills) · [allergos](https://github.com/kimogrant/allergos)

**Progressive disclosure:** Load one `references/` file per task. Read [references/tool-invocation.md](references/tool-invocation.md) before running scripts.

---

## Trigger Conditions

Activate when the user asks about:

- Fundraising (raise or not, how much, when, investor type, process)
- Runway, burn, default alive, survival round
- SaaS metrics, ARR, churn, NRR, CAC payback, gross margin, fundability
- Cap table, dilution, option pool, seed/Series A/B modeling
- Pitch deck, investor readiness, deck review
- Product-market fit, Sean Ellis test, retention, ICP
- Founder 1:1s, operating cadence (templates)

---

## Hard Rules

1. **Numbers → run tools.** If inputs exist for SaaS health, dilution, or deck scoring, execute the matching script per [references/tool-invocation.md](references/tool-invocation.md). Never fabricate scores or cap table percentages.
2. **Pre-action checklists** in `fundraising.md` and `pmf.md` — gather stage, runway, and metrics before strategic advice.
3. **Stage awareness.** State which benchmarks apply (early-stage VC SaaS vs bootstrap). Thresholds in `saas_health.py` are venture-oriented.
4. **Disclaimer** on outputs: *"Decision support only — not legal, tax, or investment advice. Verify with counsel and accountants."*
5. **No PDF deck parsing.** Pitch review is checklist-based unless user pastes slide content.

---

## Module Index

| Topic | Reference | Tools / templates |
|-------|-----------|-------------------|
| Fundraising strategy | [references/fundraising.md](references/fundraising.md) | `saas_health.py`, `equity_calc.py` |
| Product-market fit | [references/pmf.md](references/pmf.md) | `saas_health.py` (SaaS) |
| Tool commands | [references/tool-invocation.md](references/tool-invocation.md) | all `tools/*` |
| Templates | [references/templates-index.md](references/templates-index.md) | `templates/*` |

**Changelog:** [references/changelog.md](references/changelog.md)

---

## Default Workflow

1. Classify intent (fundraise / PMF / dilution / deck / ops template).
2. Load the matching reference file.
3. If numeric SaaS or cap table data → **run tool first**, then interpret with framework.
4. If deck → outline template + optional scorer interactive session.
5. Summarize: verdict, top 3 actions, disclaimer.

---

## Skill root layout

```text
ceo-operating-system/
├── SKILL.md
├── tools/          # Python CLI (stdlib only)
├── templates/
├── references/
└── frameworks/     # Legacy paths; prefer references/
```

---

## Version

See [VERSION](VERSION).
