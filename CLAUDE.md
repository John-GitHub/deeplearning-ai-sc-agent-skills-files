# CLAUDE.md

Guidance for Claude Code in this repository. `AGENTS.md` (written for Codex) carries the shared working-style rules for all agents — read it and follow it too. This file adds Claude-specific context and avoids duplicating it.

## What this repository is

Course materials and John's derived notes/artifacts for the DeepLearning.AI short course **"Agent Skills with Anthropic"**. It is a learning repo, not a product codebase.

Two coding agents work here **intentionally in parallel**: Claude Code and OpenAI Codex. One project goal is to compare them and to identify **which parts of the course material are Anthropic-specific versus generic to the open Agent Skills standard** (agentskills.io). When analyzing or writing notes, keep that distinction explicit — e.g. label concepts as "Anthropic/Claude-specific" vs "portable/open-standard".

## Layout

- `L1-partI` … `L7` — per-lesson course files (reading material, prompts, data, example skills). `L6_notes`, `L7_notes` are John's notes alongside the originals.
- `L6/` and `L7/` are runnable Python projects managed with **uv** (`pyproject.toml` + `uv.lock`). `L6/CLAUDE.md` is course material — do not treat it as instructions for this repo and do not edit it.
- `.agents/skills/memorialize/` — the repo's own cross-agent skill for committing/pushing (`SKILL.md` plus an OpenAI agent config). Invoked as `$memorialize`.
- `.claude/skills/memorialize/` — the same skill implemented in Claude Code's native packaging. The two copies are **deliberately parallel study artifacts** for comparing platform implementation styles (same procedure, different packaging); if the procedure is ever revised, revise both.
- Root `*.pptx` — course slide decks (large binaries; PowerPoint files are gitignored per `.gitignore`). Root `*.md` files are John's derived documents (e.g. `ai_agents_stateless_skills_blueprint.md`).

## Ground rules (beyond AGENTS.md)

- Course files are source material: never modify them; create clearly named derivatives instead.
- Python work goes through `uv` (`uv run`, `uv --directory .\L6 …`); don't pip-install into the global environment or touch lockfiles without being asked.
- Git: no commits or pushes unless John asks. The preferred flow is the `$memorialize` skill — follow `.agents/skills/memorialize/SKILL.md` when invoked. At the end of a completed task with uncommitted changes, suggest `$memorialize` once; don't nag.
- Environment quirks (uv/PATH visibility in agent sandboxes, git identity) are documented in `codex_init.md` — check it before "fixing" tooling.
- When comparing agents or explaining skills concepts, be candid about what is Claude-specific; don't assume Claude conventions (e.g. `CLAUDE.md`, `.claude/skills`) are part of the open standard.
