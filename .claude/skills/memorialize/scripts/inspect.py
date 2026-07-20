"""Read-only repository inspection for the memorialize skill.

Prints a compact digest of everything step 1 needs. Never mutates Git state.
Output is ASCII, terse on the happy path, explicit about blockers.
"""
import os
import subprocess
import sys


def git(*args):
    r = subprocess.run(["git", *args], capture_output=True, text=True)
    # rstrip only: porcelain status lines are position-sensitive, and a
    # leading space on the first line (" M file") must survive parsing
    return r.returncode, r.stdout.rstrip("\n")


def main():
    code, top = git("rev-parse", "--show-toplevel")
    if code != 0:
        print("BLOCKED: not a git repository")
        return 1
    # self-locate: later git add/commit steps are cwd-sensitive, so surface
    # any mismatch instead of relying on the caller's discipline
    cwd = os.path.normcase(os.path.realpath(os.getcwd()))
    if cwd != os.path.normcase(os.path.realpath(top)):
        print(f"NOTE cwd is not the repo root -- run subsequent git commands from: {top}")
    os.chdir(top)
    print(f"ROOT {top}")

    blockers = []
    gitdir = git("rev-parse", "--git-dir")[1]
    if os.path.exists(os.path.join(gitdir, "MERGE_HEAD")):
        blockers.append("merge in progress")
    if os.path.exists(os.path.join(gitdir, "rebase-merge")) or os.path.exists(
            os.path.join(gitdir, "rebase-apply")):
        blockers.append("rebase in progress")
    if git("symbolic-ref", "-q", "HEAD")[0] != 0:
        blockers.append("detached HEAD")

    code, status = git("status", "--porcelain")
    lines = [l for l in status.splitlines() if l]
    conflicts = [l[3:] for l in lines if l[:2] in ("UU", "AA", "DD", "AU", "UA", "DU", "UD")]
    if conflicts:
        blockers.append("conflicts: " + ", ".join(conflicts))

    branch = git("branch", "--show-current")[1] or "(detached)"
    code, upstream = git("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}")
    if code != 0:
        upstream = "none"
        ahead = behind = "?"
    else:
        counts = git("rev-list", "--left-right", "--count", f"{upstream}...HEAD")[1].split()
        behind, ahead = (counts + ["?", "?"])[:2]

    remote = git("remote", "-v")[1].splitlines()
    push_remote = next((l for l in remote if "(push)" in l), "none")

    staged = [l[3:] for l in lines if l[0] not in (" ", "?", "U")]
    modified = [l[3:] for l in lines if l[1] in ("M", "D") and l[0] != "U"]
    untracked = [l[3:] for l in lines if l.startswith("??")]

    print(f"BRANCH {branch} upstream {upstream} ahead {ahead} behind {behind}")
    print(f"REMOTE {push_remote}")
    for b in blockers:
        print(f"BLOCKED: {b}")
    if not blockers and not lines:
        print("STATE clean, nothing to commit")
    for label, group in (("STAGED", staged), ("MODIFIED", modified), ("UNTRACKED", untracked)):
        if group:
            print(f"{label} ({len(group)}): " + ", ".join(group))
    subjects = git("log", "-5", "--format=%s")[1]
    if subjects:
        print("RECENT: " + " | ".join(subjects.splitlines()))
    return 1 if blockers else 0


if __name__ == "__main__":
    sys.exit(main())
