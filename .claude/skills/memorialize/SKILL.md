---
name: memorialize
description: Review intended Git changes, partition independent concerns, validate them, create meaningful atomic commits, and safely push them. Use when the user invokes /memorialize or $memorialize, or asks to memorialize, commit and push, publish completed work, or preserve finished changes in Git history.
allowed-tools: Bash(git status:*), Bash(git diff:*), Bash(git log:*), Bash(git remote -v), Bash(git branch --show-current), Bash(git rev-parse:*), Bash(git show:*), Bash(python .claude/skills/memorialize/scripts/inspect.py:*), Bash(python .claude/skills/memorialize/scripts/safety_gate.py:*)
---

# Memorialize

Turn completed work into a reviewed, traceable commit and publish it without absorbing
unrelated work or rewriting history.

> Comparison note: the Codex copy at `.agents/skills/memorialize/` keeps the original
> monolithic prose procedure. This copy was deliberately refactored (2026-07-19) down
> the energy gradient — deterministic checks moved to `scripts/`, edge-case playbooks
> to `references/hazards.md` — as a study contrast. The two copies now intentionally
> diverge in implementation while honoring the same contract.

## Authorization

An explicit `/memorialize`, `$memorialize`, or "commit and push" request authorizes
committing the clearly intended changes and a normal fast-forward push. "Commit" alone
does not authorize pushing. If the intended scope is ambiguous, confirm paths and push
intent before changing Git state. Force-push, amend, rebase, history rewriting, hook
bypass, changing remotes, and committing likely secrets each require separate explicit
authorization.

## Procedure

1. **Inspect.** Run `python .claude/skills/memorialize/scripts/inspect.py`. It prints
   branch/upstream/remote, tree state, and recent commit subjects. On any `BLOCKED`
   line (merge/rebase in progress, detached HEAD, conflicts) or pre-existing staged
   work you don't own, stop and read `references/hazards.md` first. Stop too when
   there is nothing commit-worthy.

2. **Scope and partition (judgment).** Derive intended paths from the request and the
   conversation. Group by purpose: separate commits for independently reviewable,
   revertible concerns with distinct motivations; one coherent commit when splitting
   would manufacture fragments. Leave unfinished side work unstaged; never discard or
   rewrite user changes to get a clean commit. Ask only when grouping, ownership, or
   inclusion is genuinely ambiguous — otherwise state the proposed breakdown and
   proceed in dependency order.

3. **Validate.** Run documented checks proportional to the change (tests, lint,
   build). Never claim a check passed that didn't run; report skipped or unavailable
   checks. A failure stops the commit unless the user explicitly accepts it.

4. **Stage.** `git add -- <explicit paths>` only — never `git add .` or `-A`. Review
   `git diff --cached --stat` for coherence.

5. **Gate.** Run `python .claude/skills/memorialize/scripts/safety_gate.py`. Commit
   only on `GATE PASS`. On findings: stop, read `references/hazards.md`, and report
   risks by file/line/category without reproducing sensitive content. The script
   catches mechanical hazards; you still skim the staged diff for what no regex sees —
   private data, production data, proprietary material, wrong ownership. User
   confirmation alone does not make a live credential safe to publish.

6. **Commit.** Describe the staged change, not the conversation: concise imperative
   subject in the repo's own convention, body when motivation or verification context
   helps future readers. No invented issues or attributions. Normal hooks.

   For multiple planned commits, repeat 4–6 per group, gating each staged snapshot.

7. **Push.** Check the outgoing range with `git log @{upstream}..HEAD`; if it holds
   commits beyond those just created and gated, run `safety_gate.py --outgoing` to
   gate the whole range. Push with plain `git push` (add `-u` only when remote and
   branch are unambiguous) after confirming the remote identity matches expectations.
   On any push failure: preserve the local SHA, read `references/hazards.md`, never
   escalate.

8. **Report.** Each commit subject + SHA and contents, validation results, push
   outcome or failure, work left untouched — and when the set was split, the
   partition rationale: what made the concerns independent.
