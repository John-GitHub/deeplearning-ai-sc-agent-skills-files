---
name: analyzing-marketing-campaign-low-energy
description: Analyze weekly marketing campaign performance data across channels by running a bundled script. Use when analyzing multi-channel digital marketing CSV data to calculate funnel metrics (CTR, CVR) against benchmarks, compute cost and revenue efficiency metrics (ROAS, CPA, Net Profit), or get budget reallocation recommendations based on performance rules. Low-energy variant — all deterministic computation is delegated to scripts/analyze_campaign.py; the model only interprets results.
---

# Marketing Campaign Analysis (Low Energy)

All data quality checks, metric calculations, status thresholds, and reallocation
math are handled by the bundled script. **Run it — do not reason through the
arithmetic yourself.**

## Usage

```
python scripts/analyze_campaign.py <campaign_data.csv> [options]
```

The CSV needs columns: date, campaign_name, channel, segment, impressions, clicks,
conversions, spend, revenue, orders (Email rows may have empty impressions). The
script validates this and reports any data quality issues.

Options (defaults apply when the user specifies nothing):

- `--target-roas 4.0` `--max-cpa 50` `--shipping-cost 8` `--product-cost-pct 0.35`
- `--benchmark CHANNEL=CTR,CVR` — override a channel's historical benchmark (repeatable)
- `--reallocate` — add budget reallocation analysis
- `--increase-cap 0.15` `--realloc-limit <dollars>` — reallocation constraints
- `--override CHANNEL=CLASS` — classification override from user-stated history (repeatable)

## Workflow

1. Translate any user-provided benchmarks, targets, or cost assumptions into flags.
2. Run the script. Present its tables **verbatim** — do not recompute or reformat.
3. Add brief channel-by-channel interpretation: key insights and recommended actions.
   This judgment is your only computational job.

## Budget reallocation

If the user asks about reallocation, rerun with `--reallocate`. The script applies
the full rule set (eligibility, classification, caps, proportional allocation).

Only when the user supplies **historical context** ("TikTok has been negative for
3 weeks", "we changed Google's budget last week") do you exercise judgment: read
the Multi-Week Adjustments section of `references/budget_reallocation_rules.md`,
map the statement to a classification, and pass it as `--override CHANNEL=CLASS`.
Read that file also if the user asks to explain the rules.
