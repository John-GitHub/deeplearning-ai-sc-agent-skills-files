# Memorialize — Hazard Playbooks

Read this only when `inspect.py` reports a blocker, `safety_gate.py` reports findings,
or a push fails. The clean path never needs this file.

## Blocked repository states

- **Merge or rebase in progress, conflicts present**: do not commit, stage, or clean up.
  Report the state to the user and stop; resolving it is their call.
- **Detached HEAD**: committing here strands work. Stop and ask which branch the work
  belongs on.
- **Nothing commit-worthy**: report that and stop. Do not manufacture a commit.
- **Pre-existing staged changes you don't own**: leave them staged. Either ask, or
  partition around them only if they can be cleanly excluded from your `git add` paths.

## Gate findings: how to respond

General rules for every finding class:

- Name the risk by **file, line, and category only** — never reproduce the matched
  content in conversation, commit messages, or logs.
- User confirmation alone does not make a live credential safe to publish. If a real
  secret was committed in *any* outgoing commit, recommend rotating it and checking
  history (`git log -p -- <file>`), since removal from the tip does not unpublish it.
- The gate is regex-based evidence, not a verdict. Judge each finding: a docs file
  explaining "never write `password=...`" is a false positive; an `.env` with real
  values is not. When unsure, treat it as real and ask.

Per category:

- **Private key / API key / token / authorization header / connection string**: almost
  never legitimate in a commit. Remove from the change; recommend rotation if it may
  already be in history or was pasted anywhere.
- **Possible credential assignment**: highest false-positive rate (docs, test fixtures,
  clearly fake values). Inspect the line in place; commit only if convincingly inert.
- **Suspicious name** (`.env`, `.npmrc`, SSH keys, keystores, cloud-credential JSON,
  kubeconfig): filenames are warning signals, not proof. Inspect contents without
  printing secret values; usually these belong in `.gitignore`, not the repo.
- **Large file (>10 MiB)**: pause. Recommend Git LFS or an artifact store, or
  `.gitignore` if generated. Follow any repository size policy first.
- **Executable / archive / minified bundle / database dump**: confirm it is intentional
  source material, not build output, cached artifact, or data that shouldn't leave the
  machine. Database dumps and anything resembling production or personal data stop the
  commit outright.
- **Symlink**: verify the target is inside the repo and unsurprising.
- **Force-added ignored file**: the repo's `.gitignore` says no. Confirm the override
  is deliberate before proceeding.

## Content hazards no regex sees

While reviewing the staged diff, stop for: personal information, customer records,
production data, proprietary or third-party material of unclear license or ownership,
and debug/temporary files. These are judgment calls the gate cannot make.

## Push failures

- **Authentication, branch protection, or policy failure**: preserve the local commit,
  report its SHA and the exact error. Do not retry with any riskier operation.
- **Non-fast-forward (remote has new commits)**: never force-push. Report the state;
  integrating remote changes is a separate, explicitly authorized task.
- **Unexpected destination** (fork, different org/account, protected branch): stop
  before pushing and confirm. Verify with `git remote -v` and the outgoing commit list.
- Never switch branches, change remotes, or push other refs to overcome a failure.

## Operations requiring separate explicit authorization

Force-push, `--amend`, rebase, history rewriting or deletion, `--no-verify` or any
hook bypass, changing remotes, and committing anything the gate credibly flags as a
secret. An authorized "memorialize" covers none of these.
