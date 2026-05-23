# CEO Operating System

> The founder's second brain. Not another bookmark folder.

**Agent Skill + runnable tools** for fundraising, SaaS metrics, cap table modeling, and pitch deck readiness.

**Related:** [clinical-skills](https://github.com/kimogrant/clinical-skills) · [allergos](https://github.com/kimogrant/allergos) · [Web3 bounty PoC](https://github.com/kimogrant/web3-bounty-poc-report-skill) · [EVM audit](https://github.com/kimogrant/evm-audit-skill)

English | [简体中文](./README.zh.md)

---

## Install as Agent Skill (recommended)

```bash
git clone https://github.com/kimogrant/ceo-operating-system.git
cd ceo-operating-system
chmod +x skill.sh
./skill.sh install /path/to/your/project
```

Installs to `.cursor/skills/ceo-operating-system/` (`SKILL.md`, `references/`, `tools/`, `templates/`).

Reload Cursor → **`/ceo-operating-system`**

## Run tools directly

```bash
python tools/saas-metrics/saas_health.py -e
python tools/equity-calculator/equity_calc.py -e
python tools/pitch-deck-scorer/scorer.py -e
python tools/pitch-deck-scorer/scorer.py --export   # JSON output
```

## What's inside

| Category | Contents |
|----------|----------|
| **Skill** | `SKILL.md` — triggers, hard rules, module index |
| **References** | Fundraising, PMF, tool invocation, templates index |
| **Tools** | SaaS health, equity dilution, pitch deck scorer (stdlib) |
| **Templates** | Pitch deck outline, 1:1 agenda |
| **Frameworks** | Legacy copy; canonical playbooks in `references/` |

## Agent behavior

1. Classify intent (fundraise / PMF / dilution / deck).
2. Load matching `references/*.md`.
3. **Run Python tools when user supplies numbers** — see [references/tool-invocation.md](references/tool-invocation.md).

## Tests

```bash
python -m unittest tests/test_tools.py -v
```

## Philosophy

- **Runnable over readable** — scripts produce scores and tables.
- **Opinionated over exhaustive** — one framework that works.
- **Stage-aware** — note when VC SaaS benchmarks don't apply.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT — see [LICENSE](LICENSE).
