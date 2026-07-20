"""Regression self-test for the memorialize skill scripts.

Builds a throwaway git repo, plants known hazards, and asserts that
inspect.py classifies state correctly and safety_gate.py passes clean
snapshots while catching every planted category. Run after any change
to the sibling scripts. Prints SELF-TEST PASS or the first failure.

Planted secrets are assembled by concatenation so this file's own
source never matches the gate's patterns when it is itself committed.
"""
import os
import shutil
import stat
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
INSPECT = os.path.join(HERE, "inspect.py")
GATE = os.path.join(HERE, "safety_gate.py")

FAKE_AWS = "AKIA" + "ABCDEFGHIJKLMNOP"
FAKE_PW = "pass" + "word = hunter2secret99"

checks = 0


def expect(cond, label):
    global checks
    checks += 1
    if not cond:
        print(f"SELF-TEST FAIL: {label}")
        sys.exit(1)


def run(args, cwd):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True)


def git(cwd, *args):
    return run(["git", *args], cwd)


def rm_force(path):
    def onerr(func, p, _):
        os.chmod(p, stat.S_IWRITE)
        func(p)
    shutil.rmtree(path, onerror=onerr)


def main():
    d = tempfile.mkdtemp(prefix="memorialize-selftest-")
    try:
        git(d, "init", "-q")
        git(d, "config", "user.email", "t@t")
        git(d, "config", "user.name", "t")
        with open(os.path.join(d, "clean.md"), "w") as f:
            f.write("clean content\n")
        git(d, "add", "clean.md")
        git(d, "commit", "-qm", "init")

        # inspect: unstaged modification must classify MODIFIED, not STAGED
        # (regression for the porcelain leading-space parsing bug)
        with open(os.path.join(d, "clean.md"), "a") as f:
            f.write("more\n")
        r = run([sys.executable, INSPECT], d)
        expect("MODIFIED (1): clean.md" in r.stdout, "inspect MODIFIED classification")
        expect("STAGED" not in r.stdout, "inspect must not misreport STAGED")
        expect("ROOT " in r.stdout, "inspect prints repo root")

        # gate: clean staged change passes
        git(d, "add", "clean.md")
        r = run([sys.executable, GATE], d)
        expect(r.returncode == 0 and "GATE PASS" in r.stdout, "gate passes clean snapshot")

        # gate: planted hazards are all caught, values never printed
        with open(os.path.join(d, ".env"), "w") as f:
            f.write(f"AWS_KEY={FAKE_AWS}\n{FAKE_PW}\n")
        with open(os.path.join(d, ".gitignore"), "w") as f:
            f.write("build/\n")
        os.makedirs(os.path.join(d, "build"))
        with open(os.path.join(d, "build", "out.txt"), "w") as f:
            f.write("x\n")
        git(d, "add", "-f", ".env", ".gitignore", "build/out.txt")
        r = run([sys.executable, GATE], d)
        expect(r.returncode == 1 and "GATE FAIL" in r.stdout, "gate fails dirty snapshot")
        for label in ("env file", "AWS access key", "credential assignment",
                      ".gitignore rules"):
            expect(label in r.stdout, f"gate reports: {label}")
        expect(FAKE_AWS not in r.stdout and "hunter2" not in r.stdout,
               "gate never prints secret values")

        # gate: cwd-independence — same result from a subdirectory
        r = run([sys.executable, GATE], os.path.join(d, "build"))
        expect(r.returncode == 1 and "AWS access key" in r.stdout,
               "gate self-locates repo root from subdir")

        print(f"SELF-TEST PASS ({checks} checks)")
        return 0
    finally:
        rm_force(d)


if __name__ == "__main__":
    sys.exit(main())
