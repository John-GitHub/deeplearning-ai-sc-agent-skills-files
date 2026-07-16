# Adding the `memorialize` Skill

## Proposed plan

### 1. Place the skill in the repository

Create:

```text
.agents/
└── skills/
    └── memorialize/
```

This makes `memorialize` a repository-scoped skill available to anyone using Codex in this project. Codex automatically scans `$REPO_ROOT/.agents/skills`, so no installation script or global configuration is required.

### 2. Keep the skill intentionally small

Initial contents:

```text
.agents/skills/memorialize/
├── SKILL.md
└── agents/
    └── openai.yaml
```

No helper script is necessary initially. Git already provides reliable commands, and keeping the decision-making in `SKILL.md` makes this a useful learning example. A script can be added later if repeated preflight logic proves useful.

### 3. Define discovery metadata in `SKILL.md`

The YAML frontmatter will contain only:

- `name: memorialize`
- A precise `description` explaining its behavior and triggers, such as “Memorialize these changes,” “Commit and push my work,” or “Create a meaningful commit and publish it.”

The description matters because Codex uses it to decide when the skill applies.

### 4. Implement a guarded Git workflow

The body of `SKILL.md` will direct Codex to:

1. Confirm it is inside a Git repository.
2. Inspect the current branch, worktree status, remotes, and upstream.
3. Review staged and unstaged diffs.
4. Detect unrelated changes, generated or oversized files, likely secrets, private data, suspicious credential files, conflicts, detached HEAD state, and default-branch concerns.
5. Determine the intended change set from the conversation.
6. Partition independent completed concerns, such as housekeeping and feature work, into separate atomic commits when they have different purposes.
7. Show a concise commit breakdown; ask only when grouping or completeness is genuinely ambiguous.
8. Stage explicit paths instead of blindly using `git add .`.
9. Review the staged diff before each commit.
10. Run appropriate validation when available.
11. Scan each exact staged snapshot for credentials, private data, suspicious files, whitespace errors, and unexpectedly large artifacts without printing secret values.
12. Write an imperative, concise subject and an optional body explaining motivation or important context.
13. Commit normally without bypassing hooks or amending unless requested.
14. Verify each commit and record its SHA.
15. Inspect every outgoing commit for secrets and other hazards, including local commits created before the current invocation.
16. Push only with explicit authorization, after verifying the remote repository, account, branch, and outgoing commit list; never force-push unless separately requested.
17. Report exactly what was committed, tested, and pushed.

### 5. Define sensible stopping conditions

The skill will pause rather than guess when:

- The intended files cannot be separated from unrelated changes.
- Credentials, private data, suspicious credential files, unexpected executables, or unexplained large artifacts appear staged or in any outgoing commit.
- Tests fail.
- No remote exists.
- The destination repository, account, visibility, or branch is ambiguous or unexpected.
- Pushing would require overwriting history.
- Authentication or repository policy blocks the push.

A failed push will not undo a successful local commit; the skill will report the local SHA and failure clearly.

### 6. Add UI metadata

`agents/openai.yaml` will provide:

- `display_name: "Memorialize"`
- A short UI description.
- A default prompt explicitly invoking `$memorialize`.

This improves how the skill appears in Codex skill lists. Placement under `.agents/skills` provides registration and discovery.

### 7. Initialize it using the official scaffold

Use the `skill-creator` initialization script rather than manually inventing the structure. Replace the generated placeholders with finalized instructions and metadata.

### 8. Validate without publishing repository changes

Run the official skill validator, inspect the files, and confirm the repository path is discoverable. Test commit-and-push behavior only in a controlled scenario or with separate authorization to publish real repository changes.

If the skill does not appear in the current session, restart Codex or begin a new thread so the skill inventory reloads.

### 9. Preserve the current repository state

Creating the skill does not automatically invoke it. Existing edits and untracked course artifacts remain uncommitted unless a later `$memorialize` request identifies the intended subset.

### 10. Suggest memorialization at task boundaries

Add a lightweight repository instruction to `AGENTS.md`: at the end of a coherent task, mention `$memorialize` once when completed changes remain uncommitted and call out obviously independent commit groups. Do not interrupt active work, repeat the reminder, or commit and push without an explicit request.
