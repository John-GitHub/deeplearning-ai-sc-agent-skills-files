# Energy notes: why this variant is lower energy

Study artifact (John's derivative, 2026-07-19) comparing this skill against the original
`../analyzing-marketing-campaign/`, applying the principles in `the_token_tax.md` (repo
root). This file is documentation only — nothing in `SKILL.md` points to it, so it sits
outside the progressive-disclosure ladder and costs zero tokens at runtime.

## What moved down the energy ladder

| Work | Original (rung) | Low-energy variant (rung) |
|---|---|---|
| Data quality checks | Generation — model scans CSV in tokens | Execution — `quality_check()` |
| CTR/CVR/ROAS/CPA/Net Profit arithmetic | Generation | Execution — exact, deterministic |
| Status thresholds (`[OK]`/`[X]`) | Generation | Execution |
| Markdown table assembly | Generation, token by token | Execution — printed by script |
| Benchmark + cost defaults | SKILL.md body (paid every trigger) | Script constants (never in context) |
| Reallocation rules 0–2 (classify, free, allocate, cap) | Retrieval + Generation — model reads rules file, then computes | Execution — `classify()` + `print_reallocation()` |
| Multi-week judgment (user-stated history) | Retrieval + Generation | Same — **correctly stays high**: interpreting "TikTok has been negative for 3 weeks" is judgment; the model maps it to `--override` |
| Channel-by-channel interpretation | Generation | Same — correctly stays high |

## Principle scorecard

- **P4 (progressive disclosure):** body shrank from ~700 to ~350 tokens; the reference
  file is now consulted only for the judgment branch (multi-week adjustments), not for
  the math the script already encodes.
- **P5 (dispatch):** description kept deliberately rich — same trigger phrases as the
  original so it fires on the same tasks. Low energy ≠ starved frontmatter.
- **P6 (ship a script):** the model can run `analyze_campaign.py` without ever reading
  it — only the command and its output enter context. Output is designed terse on
  success ("Data Quality: OK (70 rows)") and specific on failure (per-line issues).
  The arithmetic went from sampled to calculated.

## What was learned in testing (week 1 data)

The script surfaced a genuine edge the prose version would likely fuzz over:
Facebook_Ads lands at ROAS 4.51x — above the 4.0x target ("[OK]") yet at 113% of
target, just under the 115% INCREASE threshold, so it classifies MAINTAIN. Exact
threshold behavior like this is precisely what token generation gets wrong.

## Portability

Everything here stays in the open-standard (agentskills.io) column: Markdown + YAML
frontmatter, bundled `scripts/` and `references/`, stdlib-only Python. The only new
platform assumption is that the harness grants script-execution permission — that is
per-platform plumbing, not part of the skill format.
