# Equity Dilution Calculator

**Problem:** You're raising a seed round and want to know how much ownership you'll retain after multiple rounds. Spreadsheets are brittle; this is instant.

**Run:**
```bash
python equity_calc.py           # Interactive mode
python equity_calc.py --example # See a realistic seed → Series B scenario
```

**What you get:**
- Per-round ownership breakdown (founder / investors / option pool)
- Price per share and post-money valuation
- Total founder dilution across all rounds
- ASCII-formatted cap table

**Example output:**
```
Seed:      Founder 64.0%  |  Investor 20.0%  |  Pool 16.0%
Series A:  Founder 46.8%  |  Investor 20.5%  |  Pool 12.3%
Series B:  Founder 36.5%  |  Investor 17.2%  |  Pool 9.6%

Founder dilution: 80.0% → 36.5% (lost 43.5 percentage points)
```

**Stage:** Pre-seed through Series B+.