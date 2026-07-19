# Claude Code: Context Commands — Quick Reference

John's derived notes, companion to `the_token_tax.md`. Commands are typed into the
Claude Code prompt and start with `/`.

**Terms, defined once:**

- **Token** — the unit of model text, roughly ¾ of a word.
- **Context window** — the model's working memory: one finite, append-only sequence of
  tokens. Everything in it is re-read on every token generated (the "rent"). It exists
  only for the current session.
- **Session** — one conversation, one context window.
- **Persistent state** — plain files on disk that outlive every session: `CLAUDE.md`,
  memory files, `settings.json`. A new session is "empty" *except* that these are
  loaded into it at start.

## The map: two kinds of state, three kinds of command

There are exactly two places state lives:

1. **Session state** — the context window. Evaporates when the session ends.
2. **Persistent state** — files on disk. Survives everything; loaded fresh each session.

Every command below does one of three things. This is the whole structure:

| Group | Commands | Touches | Risk |
|---|---|---|---|
| **Look around** | `/context`, `/cost` | Nothing. Read-only. | None. Run freely. |
| **Change session state** | `/compact`, `/clear`, `/resume` | The context window only. | `/compact` is lossy and irreversible. Files on disk are never touched. |
| **Change persistent state** | `/memory`, `/init`, `/config` | Files on disk. | Effects recur every future session. But they're just files — git can diff and revert them. |

Monkey-brain rule: the first group is a window, the second group is the gearbox, the
third group is opening the hood. Experiment freely with group one; understand what
you're doing before touching groups two and three.

---

## Group 1 — Look around (read-only, always safe)

### `/context` — map of the window

Shows what currently occupies the context window (system prompt, tools, memory,
messages) and how much is free. Changes nothing.

- **Example 1 — baseline check:** type `/context` at the start of a session, before
  doing anything. What you see is the always-on load: the tax you pay before work begins.
- **Example 2 — before/after measurement:** run `/context`, ask Claude to read a large
  file, run `/context` again. The delta is what that file costs you *per session it's
  loaded in*. Same trick measures a skill invocation.

### `/cost` — the meter

Shows cumulative token usage and cost for this session. Changes nothing.

- **Example 1 — post-task reading:** after a big task, `/cost` tells you what it burned.
  Do this for a week and you'll price tasks by feel.
- **Example 2 — comparing approaches:** run the same job once with a sub-agent, once
  without, `/cost` after each. Now Principle 7 of `the_token_tax.md` is a number, not a
  claim.

---

## Group 2 — Change session state (the window changes; disk does not)

### `/compact` — summarize and continue

Replaces the conversation with a short summary, then continues in a mostly-empty window.
**Lossy and irreversible:** detail not captured in the summary is gone. Nothing on disk
is affected.

- **Example 1 — plain:** `/compact` at a milestone ("the bug is fixed, tests pass")
  before starting the next phase. You choose the boundary instead of letting
  auto-compaction fire blind at a random moment when the window fills.
- **Example 2 — steered:** `/compact focus on the final design decisions and the list of
  files we changed` — you tell the summarizer what must survive. Use this when the
  session held one crucial conclusion and lots of disposable exploration.
- **Before compacting:** if a hard-won detail must survive verbatim, have Claude write
  it to a file first. Files don't get summarized.

### `/clear` — start over

Empties the conversation entirely. The next message begins a fresh window holding only
the always-on load. Nothing on disk is affected; the old transcript remains in session
history on disk (see `/resume`), but your working window is gone.

- **Example 1 — task boundary:** bug fix done and committed; next task is unrelated
  documentation. `/clear`. The fix's conversation is pure rent with zero relevance.
- **Example 2 — poisoned context:** Claude has gone down a wrong path and keeps
  re-anchoring on its own earlier mistake. `/clear`, then restate the task cleanly.
  Cheaper than arguing with the residue.

### `/resume` — reload a previous session

Shows a picker of past sessions and reopens one, conversation intact. Changes which
session state you're *in*; touches nothing on disk.

- **Example 1 — interrupted work:** you closed the laptop mid-task yesterday. `/resume`,
  pick the session, continue where it left off — full context restored (and its full
  rent restored with it).
- **Example 2 — from the shell:** `claude --continue` (or `claude -c`) skips the picker
  and reopens the most recent session directly.

---

## Group 3 — Change persistent state (files on disk; every future session inherits this)

These edit real files. That's the power (set once, applies forever) and the cost (a
careless line here is rent in *every* future session — zero-point energy you added by
hand). All three targets are text files git can track: diff and revert like any code.

### `/memory` — edit the always-loaded instruction files

Opens the memory files for editing: project `CLAUDE.md`, user-level memory, and
auto-memory. These load into every session's context at start.

- **Example 1 — add a standing rule:** `/memory`, choose project memory (`CLAUDE.md`),
  add "Python work goes through uv; never pip-install globally." Every future session
  obeys without being told.
- **Example 2 — quick capture:** start a message with `#`, e.g.
  `# always run tests before claiming a fix works` — Claude offers to save it to the
  right memory file without opening an editor.
- **Prune it like a garden:** when a rule stops being true, delete it. Stale memory is
  worse than no memory — it's rent paid to be misled.

### `/init` — generate CLAUDE.md for a repo

Scans the repository and writes a starter `CLAUDE.md` (build commands, layout,
conventions). A file-writing act: review the result like a PR.

- **Example 1 — new project:** first time running Claude Code in a repo, `/init` gives
  you a baseline instead of a blank page. Then prune — it drafts generously, and every
  surviving line is permanent rent.
- **Example 2 — after a big restructure:** directories moved, build system changed.
  Re-run `/init`; it proposes updates to the existing file. Review the diff with git
  before keeping it.

### `/config` — settings

Opens settings (model, theme, statusline, permissions...), stored in `settings.json`
files (user-level and per-project). Persistent across sessions.

- **Example 1 — context fuel gauge:** configure the statusline to show
  context-percentage permanently. The structural fix: you stop needing to remember
  `/context` ("automate out the human").
- **Example 2 — model choice:** set the default model — e.g. a cheaper model for routine
  sessions in this learning repo, the strongest one when it matters. This is an
  energy-ladder decision made once, in persistent state, instead of per-session.

---

## Best practices, restated against the map

1. **`/clear` between unrelated tasks.** Highest-value habit. Session state is
   disposable by design — dispose of it.
2. **`/compact` at boundaries you choose,** steered with a focus instruction. Never let
   auto-compaction pick what survives.
3. **Anything that must survive a compact or a clear goes to disk** — a file, or memory
   if it's a standing rule. Session state is for work in flight, never for storage.
4. **Treat group 3 edits as code.** They're files in this repo (or your home dir):
   review them, keep them lean, let git be the undo button.
5. **Watch `/context` while learning; then make the statusline watch it for you.**
