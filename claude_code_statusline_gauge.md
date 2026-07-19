# Claude Code: Statusline Gauge — Context & Cost Widget

John's derived notes, companion to `claude_code_context_commands.md`. Documents the
two-line status line installed 2026-07-19: a permanent fuel gauge for the context
window, replacing the habit of typing `/context` ("automate out the human").

## What it shows

```
[Fable 5] 15.5k/200.0k (8%)                        ← line 1, color-coded
LAST API in:8.5k cache-r:2.0k cache-w:5.0k out:1.2k | $0.01
```

- **Line 1** — model name, tokens currently in the context window / window size,
  percentage used. Color: **green** below 50%, **yellow** 50–69%, **orange** 70–84%,
  **red** at 85%+. Red means "auto-compaction is imminent — write anything precious to
  a file now," since compaction fires well before 100%.
- **Line 2** — the most recent API call's token breakdown, labeled `LAST API` because
  one prompt from you triggers *many* API calls (every tool round-trip is one):
  - `in:` fresh input tokens (full price)
  - `cache-r:` tokens read from the prompt cache (~10% of full price)
  - `cache-w:` tokens written to cache (~125% of full price, pays off on reuse)
  - `out:` tokens the model generated
  - `$` cumulative estimated session cost (client-side estimate; resets on `/clear`)

Watching `cache-r` dwarf `in` on most calls is the prompt-caching discount from
Principle 3 of `the_token_tax.md`, made visible.

## Where it lives (two files, both user-level)

| File | Role |
|---|---|
| `~/.claude/statusline.py` | The widget: ~40 lines of Python, reads session JSON on stdin, prints two lines |
| `~/.claude/settings.json` | The wiring: a `statusLine` entry pointing at the script |

The settings entry:

```json
"statusLine": {
  "type": "command",
  "command": "python C:/Users/johnp/.claude/statusline.py"
}
```

`~` is your home directory (`C:\Users\johnp`). **User-level means global:** every
project on this machine gets the gauge automatically. There is nothing to port to a
new project — that step was deliberately engineered away.

## How it works (and why it's free)

Claude Code runs the script after each assistant message (debounced at 300 ms),
piping it a JSON snapshot of the session — model, `context_window` (including
`used_percentage` and the per-call `current_usage` breakdown), and `cost`. The script
prints; Claude Code displays. It runs locally and **consumes zero tokens** — it is
Principle 6 of `the_token_tax.md` (deterministic logic as a script, outside the token
regime) applied to instrumentation.

Null-safety: token fields are `null` before the first API call and briefly after
`/compact`; the script prints zeros instead of erroring.

## Porting

- **New project on this machine:** nothing to do. It's already there.
- **New machine:** copy `statusline.py` to `~/.claude/`, add the `statusLine` block to
  `~/.claude/settings.json`, adjust the path. Requires Python on PATH (any 3.x); no
  other dependencies — deliberately no `jq`, which Git Bash on Windows lacks.
- **Per-project variant** (e.g. to share with a team via git): put the script in the
  repo, add the `statusLine` block to the project's `.claude/settings.json` instead.
  Project settings override user settings, so a repo can carry its own gauge.

## Changing it

Edit `~/.claude/statusline.py` and it takes effect on your next interaction — no
restart. Test any change from a shell without touching Claude Code:

```bash
echo '{}' | python ~/.claude/statusline.py          # must print zeros, never errors
```

## Ledger note

The status line, its JSON contract, and `settings.json` are **Claude Code plumbing**,
not part of the open Agent Skills standard. The *idea* — zero-token local
instrumentation over the agent's session state — is portable; every field name here
is not.
