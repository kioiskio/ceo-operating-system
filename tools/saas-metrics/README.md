# SaaS Metrics Health Checker

**Problem:** You're tracking ARR, churn, and CAC in separate places. You need a single view that tells you whether your numbers are fundable — or burnable.

**Run:**
```bash
python saas_health.py           # Interactive mode
python saas_health.py --example # See a sample early-stage SaaS report
```

**What you get:**
- Red / Amber / Green assessment for 6 key metrics (ARR growth, churn, NRR, CAC payback, gross margin, runway)
- Overall health score out of 100
- Actionable recommendations for every red and amber metric

**Metrics assessed:**
| Metric | Green | Amber | Red |
|--------|-------|-------|-----|
| YoY ARR Growth | ≥100% | 50-100% | <50% |
| Monthly Churn | <2% | 2-5% | >5% |
| Net Revenue Retention | ≥120% | 100-120% | <100% |
| CAC Payback | <12 mo | 12-18 mo | >18 mo |
| Gross Margin | ≥80% | 60-80% | <60% |
| Runway | ≥18 mo | 12-18 mo | <12 mo |

*Thresholds use early-stage SMB SaaS benchmarks. Enterprise thresholds are stricter on churn and CAC.*

**Stage:** Pre-seed through Series B.