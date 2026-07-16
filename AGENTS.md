# Repository instructions for Codex

This workspace is a learning and course-materials repository for DeepLearning.AI content. The priority is to help John learn, document, and build useful artifacts without losing the integrity of the source course material.

## Working style

- Prefer small, inspectable changes over large rewrites.
- Explain the reasoning clearly when a task is conceptual or educational.
- Ask clarifying questions when the request is ambiguous, especially for notebooks, assignments, or course content.
- Preserve the original course files unless the user explicitly asks for a modification or derivative.

## Repository conventions

- Keep course materials intact when possible; if a copy is needed, create a clearly named derivative file.
- Add notes and summaries in a lightweight, readable format.
- Favor documentation that supports learning and future reference.
- When working with notebooks, keep changes explicit and easy to review.

## Coding guidance

- Use Python tooling through uv where available.
- Prefer simple, reproducible commands and avoid unnecessary dependencies.
- Validate changes before claiming success.
- Keep changes focused on the task and avoid unrelated refactors.

## Assignment help

- Treat assignments as learning exercises first.
- Explain the concept clearly and provide the smallest helpful correction.
- Avoid silently changing answers when the user may want to understand the reasoning.

## Default approach

- Understand the request and repository context first.
- Make the minimum change needed to satisfy the goal.
- Summarize what changed, what was preserved, and any follow-up suggestions.

## Git handoff

- At the end of a coherent task, if completed changes remain uncommitted, briefly suggest using `$memorialize` once during the final handoff.
- Identify obviously independent completed changes that would be clearer as separate commits, including small housekeeping such as `.gitignore` updates.
- Do not interrupt active work, repeatedly remind the user, or imply that unfinished and unrelated changes should be committed.
- Do not commit or push merely because a reminder is appropriate; wait for the user to invoke `$memorialize` or otherwise explicitly request the Git action.
