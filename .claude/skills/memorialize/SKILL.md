---
name: memorialize
description: Review intended Git changes, partition independent concerns, validate them, create meaningful atomic commits, and safely push them. Use when the user invokes /memorialize or $memorialize, or asks to memorialize, commit and push, publish completed work, or preserve finished changes in Git history.
allowed-tools: Bash(git status:*), Bash(git diff:*), Bash(git log:*), Bash(git remote -v), Bash(git branch --show-current), Bash(git rev-parse:*), Bash(git show:*)
---

# Memorialize

Turn completed work into a reviewed, traceable commit and publish it without absorbing unrelated work or rewriting history.

> Comparison note: this is the Claude Code implementation of the same skill defined for
> Codex at `.agents/skills/memorialize/`. The procedure is intentionally identical; only
> the platform packaging differs. It exists as a study artifact, not because two copies
> are operationally necessary. If the procedure changes, revise both copies.

## Interpret authorization

- Treat an explicit request to use `/memorialize`, `$memorialize`, or “memorialize these changes” as authorization to commit the clearly intended changes and make a normal fast-forward push.
- Honor narrower wording. If the user asks only to commit, do not push.
- If selected implicitly, or if “these changes” is ambiguous, confirm the intended paths and whether to push before changing Git state.
- Require separate explicit authorization for force-pushing, amending, rebasing, deleting, bypassing hooks, changing remotes, or committing likely secrets.

## 1. Inspect

Run read-only checks before staging:

```text
git status --short --branch
git diff --stat
git diff
git diff --cached --stat
git diff --cached
git remote -v
git branch --show-current
git rev-parse --abbrev-ref --symbolic-full-name @{upstream}
git log -5 --format=%s
```

Adapt the upstream command to the active shell. Stop for conflicts, a merge or rebase in progress, detached HEAD, or no commit-worthy changes. Do not disturb unrelated worktree or index changes.

## 2. Establish scope

Derive the intended paths from the request and work completed in the conversation. Check them for:

- Credentials, tokens, keys, `.env` contents, or other sensitive data.
- Suspicious credential files such as `.npmrc`, `.pypirc`, `.netrc`, cloud service-account JSON, SSH keys, certificates, keystores, kubeconfig files, and database connection exports.
- Large binaries, generated output, caches, or files better handled by `.gitignore` or Git LFS.
- Database dumps, production data, personal information, customer records, or proprietary material not meant for the remote repository.
- Debug output, temporary files, and editor artifacts.
- Independent concerns that deserve separate commits.

Pause when safe separation is impossible. Never discard, restore, stash, or rewrite user changes merely to obtain a clean commit.

Treat filenames as warning signals, not proof. Inspect suspicious files without printing secret values into the conversation or command logs. Redact findings to the credential type, file, and line number when possible.

## 3. Partition the work

Group completed changes by purpose before staging. Prefer a separate commit when a group:

- Represents housekeeping, documentation, tests, formatting, or generated metadata independent of the main feature or fix.
- Could be reviewed, reverted, or cherry-picked on its own.
- Has a different motivation that deserves a different commit subject.

Keep unfinished or uncertain side work unstaged. Do not split tightly coupled implementation and its focused tests merely to increase the commit count. Do not manufacture tiny commits when one coherent commit tells the story better.

When multiple groups are clearly complete and their intent is established by the conversation, show a concise proposed commit breakdown and create them in dependency order without asking a redundant question. Ask for direction only when ownership, completeness, grouping, or inclusion is genuinely ambiguous.

Validate and run the safety gate for each proposed commit's exact staged snapshot. After each commit, continue only with the paths assigned to the next group.

## 4. Validate

Run relevant documented checks in proportion to the change: focused tests, formatting, linting, type checks, builds, or artifact validation. Never claim a check passed unless it ran successfully.

If a check fails, diagnose it and stop before committing unless the user explicitly accepts the known failure. Report unavailable or skipped checks.

## 5. Stage deliberately

Stage explicit intended paths with `git add -- <paths>`. Do not use `git add .` or `git add -A`.

Review `git diff --cached --stat`, `git diff --cached`, and `git status --short`. Confirm the staged snapshot is coherent and contains no unintended files. If unrelated changes were already staged, do not unstage them without permission.

## 6. Run the safety gate

Inspect the exact staged snapshot before committing:

```text
git diff --cached --name-status
git diff --cached --numstat
git diff --cached --check
git diff --cached
```

- Search added content for high-confidence credential forms: private-key headers; provider token prefixes; authorization headers; passwords, secrets, or tokens assigned non-placeholder values; connection strings with credentials; and unusually long encoded values near credential names.
- Check full contents of newly added text files, because a diff excerpt or ordinary review may miss relevant context.
- Use a repository-provided secret scanner or an already-installed local scanner when available. Do not upload the diff to an external scanning service or install new tooling without authorization.
- Flag unexpected executables, archives, media, office documents, minified bundles, lockfile explosions, submodule changes, and symlinks with surprising targets.
- Follow repository size policy. If none exists, pause on any unexpected new file over 10 MiB and recommend Git LFS or an artifact store where appropriate.
- Confirm ignored files are not being force-added and generated artifacts are intentional.

Stop before committing on any credible secret, private data, malware-like artifact, unexplained large file, or unclear ownership/licensing concern. Name the risk without reproducing sensitive content. Recommend removing the item from the change, rotating an exposed credential, and checking history if it may already have been committed. Do not treat user confirmation alone as making a live credential safe to publish.

## 7. Commit meaningfully

Describe the staged change, not the conversation. Follow an evident repository convention; do not impose Conventional Commits unless the project uses them.

- Use a concise imperative subject describing the outcome.
- Add a body when motivation, tradeoffs, migration, or verification context helps future readers.
- Avoid vague subjects such as “updates,” “changes,” or “work in progress.”
- Do not invent issue numbers, claims, or attribution trailers.

Create each atomic commit with normal hooks. Do not use `--no-verify` or `--amend` without separate authorization.

## 8. Verify and push

Inspect `git status --short --branch`, `git show --stat --oneline --decorate HEAD`, and `git rev-parse HEAD`.

Before pushing, determine the complete outgoing range, such as `@{upstream}..HEAD`, and inspect its commits and changed files. Apply the same secret, privacy, and large-file checks to all outgoing commits, not only `HEAD`. This catches hazards in earlier local commits that the push would also publish.

- With an existing upstream, use `git push`.
- Without one, use `git push -u <remote> <branch>` only when both are unambiguous.
- Verify the remote URL, repository identity, branch, and outgoing commit list. Pause if the destination is an unexpected fork, organization, public repository, protected branch, or different account.
- Never force-push, switch branches, change remotes, or push other refs to overcome failure.

If authentication, protection, non-fast-forward history, or policy blocks the push, preserve the local commit and report its SHA. Do not retry with a riskier operation.

## 9. Report

State each commit subject and SHA, its included change, validation results, pushed remote branch or failure, and any unrelated or unfinished changes left untouched.

When the change set was split into multiple commits, explain the reasoning behind the partition — what made the concerns independent and why each boundary was drawn where it was.
