#!/usr/bin/env python3
"""Marketing campaign analysis: data quality, funnel, efficiency, reallocation.

Stdlib only. Emits finished Markdown tables so the calling agent presents them
verbatim and spends tokens only on interpretation.

Output contract: terse on success, specific on failure.
"""

import argparse
import csv
import sys
from collections import defaultdict

NUMERIC_COLS = ["impressions", "clicks", "conversions", "spend", "revenue", "orders"]
REQUIRED_COLS = ["date", "campaign_name", "channel", "segment"] + NUMERIC_COLS

DEFAULT_BENCHMARKS = {  # channel: (CTR %, CVR %)
    "Facebook_Ads": (2.5, 3.8),
    "Google_Ads": (5.0, 4.5),
    "TikTok_Ads": (2.0, 0.9),
    "Email": (15.0, 2.1),
}
DEFAULT_TARGET_ROAS = 4.0
DEFAULT_MAX_CPA = 50.0
DEFAULT_SHIPPING_COST = 8.0
DEFAULT_PRODUCT_COST_PCT = 0.35
DEFAULT_INCREASE_CAP = 0.15
MIN_CONVERSIONS_FOR_ELIGIBILITY = 50

VALID_OVERRIDES = {"PAUSE", "DECREASE_HEAVY", "DECREASE_LIGHT", "MAINTAIN"}


def money(x):
    return f"${x:,.2f}"


def parse_args(argv):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("csv_path", help="Campaign data CSV")
    p.add_argument("--target-roas", type=float, default=DEFAULT_TARGET_ROAS)
    p.add_argument("--max-cpa", type=float, default=DEFAULT_MAX_CPA)
    p.add_argument("--shipping-cost", type=float, default=DEFAULT_SHIPPING_COST)
    p.add_argument("--product-cost-pct", type=float, default=DEFAULT_PRODUCT_COST_PCT,
                   help="Product cost as fraction of revenue (default 0.35)")
    p.add_argument("--benchmark", action="append", default=[], metavar="CHANNEL=CTR,CVR",
                   help="Override a channel benchmark, e.g. Facebook_Ads=2.5,3.8 (repeatable)")
    p.add_argument("--reallocate", action="store_true",
                   help="Also run the budget reallocation rules")
    p.add_argument("--increase-cap", type=float, default=DEFAULT_INCREASE_CAP,
                   help="Per-channel increase cap as fraction of spend (default 0.15)")
    p.add_argument("--realloc-limit", type=float, default=None,
                   help="Dollar cap on total increases (applies to increases only)")
    p.add_argument("--override", action="append", default=[], metavar="CHANNEL=CLASS",
                   help="Classification override from user-stated history "
                        "(PAUSE, DECREASE_HEAVY, DECREASE_LIGHT, or MAINTAIN; repeatable)")
    return p.parse_args(argv)


def parse_benchmarks(pairs):
    benchmarks = dict(DEFAULT_BENCHMARKS)
    for pair in pairs:
        try:
            channel, values = pair.split("=", 1)
            ctr, cvr = (float(v) for v in values.split(","))
        except ValueError:
            sys.exit(f"ERROR: bad --benchmark {pair!r}; expected CHANNEL=CTR,CVR")
        benchmarks[channel] = (ctr, cvr)
    return benchmarks


def parse_overrides(pairs):
    overrides = {}
    for pair in pairs:
        try:
            channel, cls = pair.split("=", 1)
        except ValueError:
            sys.exit(f"ERROR: bad --override {pair!r}; expected CHANNEL=CLASS")
        cls = cls.upper()
        if cls not in VALID_OVERRIDES:
            sys.exit(f"ERROR: --override class must be one of {sorted(VALID_OVERRIDES)}")
        overrides[channel] = cls
    return overrides


def load_rows(csv_path):
    try:
        with open(csv_path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            missing = [c for c in REQUIRED_COLS if c not in (reader.fieldnames or [])]
            if missing:
                sys.exit(f"ERROR: CSV missing required columns: {', '.join(missing)}")
            rows = list(reader)
    except OSError as e:
        sys.exit(f"ERROR: cannot read {csv_path}: {e}")
    if not rows:
        sys.exit("ERROR: CSV contains no data rows")
    return rows


def quality_check(rows):
    """Return (clean_rows, issues). Email rows may legitimately lack impressions."""
    issues = []
    clean = []
    for i, row in enumerate(rows, start=2):  # header is line 1
        row_ok = True
        for col in NUMERIC_COLS:
            raw = (row[col] or "").strip()
            if raw == "":
                if col == "impressions" and row["channel"] == "Email":
                    row[col] = None
                    continue
                issues.append(f"line {i}: missing {col} ({row['channel']}/{row['campaign_name']})")
                row_ok = False
                continue
            try:
                val = float(raw)
            except ValueError:
                issues.append(f"line {i}: non-numeric {col}={raw!r}")
                row_ok = False
                continue
            if val < 0:
                issues.append(f"line {i}: negative {col}={val}")
                row_ok = False
            row[col] = val
        if row_ok:
            clicks, conv = row["clicks"], row["conversions"]
            imp = row["impressions"]
            if conv > 0 and clicks == 0:
                issues.append(f"line {i}: {conv:.0f} conversions with zero clicks")
            if imp is not None and clicks > imp:
                issues.append(f"line {i}: clicks ({clicks:.0f}) exceed impressions ({imp:.0f})")
            clean.append(row)
    return clean, issues


def aggregate(rows):
    totals = defaultdict(lambda: {c: 0.0 for c in NUMERIC_COLS})
    has_impressions = defaultdict(bool)
    for row in rows:
        t = totals[row["channel"]]
        for col in NUMERIC_COLS:
            if row[col] is not None:
                t[col] += row[col]
        if row["impressions"] is not None:
            has_impressions[row["channel"]] = True
    return totals, has_impressions


def compute_metrics(totals, has_impressions, args):
    metrics = {}
    for channel, t in sorted(totals.items()):
        ctr = (t["clicks"] / t["impressions"] * 100) if has_impressions[channel] and t["impressions"] else None
        cvr = (t["conversions"] / t["clicks"] * 100) if t["clicks"] else None
        roas = (t["revenue"] / t["spend"]) if t["spend"] else None
        cpa = (t["spend"] / t["conversions"]) if t["conversions"] else None
        total_costs = t["spend"] + t["orders"] * args.shipping_cost + t["revenue"] * args.product_cost_pct
        metrics[channel] = {
            **t,
            "ctr": ctr, "cvr": cvr, "roas": roas, "cpa": cpa,
            "net_profit": t["revenue"] - total_costs,
        }
    return metrics


def print_funnel_table(metrics, benchmarks):
    print("**Funnel Analysis Table:**\n")
    print("| Channel | CTR Actual | CTR Benchmark | CTR Diff | CVR Actual | CVR Benchmark | CVR Diff |")
    print("|---------|-----------|---------------|----------|-----------|---------------|----------|")
    for channel, m in metrics.items():
        bench = benchmarks.get(channel)
        ctr_a = f"{m['ctr']:.2f}%" if m["ctr"] is not None else "N/A"
        cvr_a = f"{m['cvr']:.2f}%" if m["cvr"] is not None else "N/A"
        if bench:
            ctr_b, cvr_b = f"{bench[0]:.1f}%", f"{bench[1]:.1f}%"
            ctr_d = f"{m['ctr'] - bench[0]:+.2f} pp" if m["ctr"] is not None else "N/A"
            cvr_d = f"{m['cvr'] - bench[1]:+.2f} pp" if m["cvr"] is not None else "N/A"
        else:
            ctr_b = cvr_b = ctr_d = cvr_d = "no benchmark"
        print(f"| {channel} | {ctr_a} | {ctr_b} | {ctr_d} | {cvr_a} | {cvr_b} | {cvr_d} |")
    print()


def print_efficiency_table(metrics, args):
    print("**Efficiency Analysis Table:**\n")
    print(f"(Target ROAS {args.target_roas:.1f}x | Max CPA {money(args.max_cpa)} | "
          f"Shipping {money(args.shipping_cost)}/order | Product cost {args.product_cost_pct:.0%} of revenue)\n")
    print("| Channel | ROAS | Status | CPA | Status | Net Profit | Status |")
    print("|---------|------|--------|-----|--------|------------|--------|")
    for channel, m in metrics.items():
        roas = f"{m['roas']:.2f}x" if m["roas"] is not None else "N/A"
        roas_s = "[OK] Above" if m["roas"] is not None and m["roas"] >= args.target_roas else "[X] Below"
        cpa = money(m["cpa"]) if m["cpa"] is not None else "N/A"
        cpa_s = "[OK] Below" if m["cpa"] is not None and m["cpa"] <= args.max_cpa else "[X] Above"
        np_s = "[OK] Positive" if m["net_profit"] > 0 else "[X] Negative"
        print(f"| {channel} | {roas} | {roas_s} | {cpa} | {cpa_s} | {money(m['net_profit'])} | {np_s} |")
    print()


def classify(m, args, override):
    """Apply reallocation rules in order; first match wins. Returns (class, reason)."""
    if m["conversions"] < MIN_CONVERSIONS_FOR_ELIGIBILITY:
        return "MAINTAIN", f"INSUFFICIENT_DATA (<{MIN_CONVERSIONS_FOR_ELIGIBILITY} conversions)"
    if override:
        return override, "user-stated history (override)"
    roas_pct = (m["roas"] / args.target_roas * 100) if m["roas"] is not None else 0.0
    cpa_pct = (m["cpa"] / args.max_cpa * 100) if m["cpa"] is not None else float("inf")
    np_ = m["net_profit"]
    if roas_pct < 50 and np_ <= 0:
        return "DECREASE_HEAVY", "ROAS < 50% of target and Net Profit <= 0"
    if cpa_pct > 150 and np_ <= 0:
        return "DECREASE_HEAVY", "CPA > 150% of max and Net Profit <= 0"
    if roas_pct < 100 and cpa_pct > 100 and np_ <= 0:
        return "DECREASE_HEAVY", "fails ROAS, CPA, and Net Profit"
    if roas_pct >= 115 and cpa_pct <= 80 and np_ > 0:
        return "INCREASE", "ROAS >= 115% of target, CPA <= 80% of max, Net Profit > 0"
    if roas_pct < 80:
        return "DECREASE_LIGHT", "ROAS < 80% of target"
    if cpa_pct > 120:
        return "DECREASE_LIGHT", "CPA > 120% of max"
    return "MAINTAIN", "no rule triggered"


def print_reallocation(metrics, args, overrides):
    unknown = sorted(set(overrides) - set(metrics))
    if unknown:
        sys.exit(f"ERROR: --override for unknown channel(s): {', '.join(unknown)}")

    classes = {ch: classify(m, args, overrides.get(ch)) for ch, m in metrics.items()}

    print("**Reallocation Classification Table:**\n")
    print("| Channel | ROAS | % of Target | CPA | % of Max | Net Profit | Classification |")
    print("|---------|------|-------------|-----|----------|------------|----------------|")
    for channel, m in metrics.items():
        cls, _ = classes[channel]
        roas_pct = f"{m['roas'] / args.target_roas * 100:.0f}%" if m["roas"] is not None else "N/A"
        cpa_pct = f"{m['cpa'] / args.max_cpa * 100:.0f}%" if m["cpa"] is not None else "N/A"
        roas = f"{m['roas']:.2f}x" if m["roas"] is not None else "N/A"
        cpa = money(m["cpa"]) if m["cpa"] is not None else "N/A"
        print(f"| {channel} | {roas} | {roas_pct} | {cpa} | {cpa_pct} | {money(m['net_profit'])} | {cls} |")
    print("\nClassification reasons:")
    for channel, (cls, reason) in classes.items():
        print(f"- {channel}: {cls} — {reason}")

    decreases = {}
    for channel, (cls, _) in classes.items():
        spend = metrics[channel]["spend"]
        if cls == "PAUSE":
            decreases[channel] = spend
        elif cls == "DECREASE_HEAVY":
            decreases[channel] = spend * 0.45
        elif cls == "DECREASE_LIGHT":
            decreases[channel] = spend * 0.25
    freed = sum(decreases.values())

    increase_channels = [ch for ch, (cls, _) in classes.items() if cls == "INCREASE"]
    total_np = sum(metrics[ch]["net_profit"] for ch in increase_channels)
    proposed = {}
    for ch in increase_channels:
        weight = metrics[ch]["net_profit"] / total_np if total_np > 0 else 1 / len(increase_channels)
        proposed[ch] = freed * weight

    capped = {ch: min(amt, metrics[ch]["spend"] * args.increase_cap) for ch, amt in proposed.items()}
    scale_note = ""
    if args.realloc_limit is not None and sum(capped.values()) > args.realloc_limit:
        scale = args.realloc_limit / sum(capped.values())
        capped = {ch: amt * scale for ch, amt in capped.items()}
        scale_note = f" (scaled to user limit {money(args.realloc_limit)})"
    unallocated = freed - sum(capped.values())

    print("\n**Calculation Steps:**\n")
    print(f"- Freed budget: {money(freed)}"
          + (f" ({', '.join(f'{ch} -{money(amt)}' for ch, amt in decreases.items())})" if decreases else ""))
    if increase_channels:
        for ch in increase_channels:
            weight = metrics[ch]["net_profit"] / total_np if total_np > 0 else 1 / len(increase_channels)
            print(f"- {ch}: weight {weight:.1%}, proposed +{money(proposed[ch])}, "
                  f"after cap{scale_note} +{money(capped[ch])}")
    else:
        print("- No channels qualified for INCREASE")
    print(f"- Unallocated (available for reserve): {money(unallocated)}")

    print("\n**Final Reallocation Table:**\n")
    print("| Channel | Current | Change | New Budget | Classification |")
    print("|---------|---------|--------|------------|----------------|")
    for channel, m in metrics.items():
        cls, _ = classes[channel]
        change = capped.get(channel, 0.0) - decreases.get(channel, 0.0)
        sign = "+" if change >= 0 else "-"
        print(f"| {channel} | {money(m['spend'])} | {sign}{money(abs(change))} | "
              f"{money(m['spend'] + change)} | {cls} |")
    if unallocated > 0.005:
        print(f"| Reserve | — | +{money(unallocated)} | {money(unallocated)} | — |")
    print()


def main(argv=None):
    args = parse_args(argv)
    benchmarks = parse_benchmarks(args.benchmark)
    overrides = parse_overrides(args.override)

    rows = load_rows(args.csv_path)
    clean, issues = quality_check(rows)
    if issues:
        print(f"**Data Quality: {len(issues)} issue(s) found** (affected rows excluded from totals)\n")
        for issue in issues:
            print(f"- {issue}")
        print()
    else:
        print(f"**Data Quality: OK** ({len(clean)} rows)\n")
    if not clean:
        sys.exit("ERROR: no valid rows after quality checks")

    totals, has_impressions = aggregate(clean)
    metrics = compute_metrics(totals, has_impressions, args)
    print_funnel_table(metrics, benchmarks)
    print_efficiency_table(metrics, args)
    if args.reallocate:
        print_reallocation(metrics, args, overrides)


if __name__ == "__main__":
    main()
