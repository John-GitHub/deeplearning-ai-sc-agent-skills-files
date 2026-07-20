"""Deterministic safety gate for the memorialize skill.

Scans a snapshot (staged by default, or the full outgoing range with
--outgoing) for mechanical hazards: credential patterns, suspicious
filenames, oversized files, unexpected binaries, symlinks, and
force-added ignored files.

Prints GATE PASS or GATE FAIL with findings as file:line + category.
Never prints matched secret values. Exit 0 on pass, 1 on findings.
The model retains the judgment call on anything reported here and on
context-dependent hazards (private data, ownership) no regex can see.
"""
import os
import re
import subprocess
import sys

MAX_BYTES = 10 * 1024 * 1024

NAME_PATTERNS = [
    (r"(^|/)\.env(\..+)?$", "env file"),
    (r"(^|/)\.(npmrc|pypirc|netrc)$", "credential config"),
    (r"(^|/)id_(rsa|ed25519|ecdsa|dsa)(\.pub)?$", "SSH key"),
    (r"\.(pem|key|p12|pfx|keystore|jks)$", "key material"),
    (r"(^|/)(kubeconfig|\.kube/config)$", "kubeconfig"),
    (r"(service[-_]?account|credentials).*\.json$", "cloud credential JSON"),
    (r"\.(exe|dll|so|dylib|bin)$", "executable"),
    (r"\.(zip|tar|gz|tgz|7z|rar)$", "archive"),
    (r"\.min\.(js|css)$", "minified bundle"),
    (r"\.(sql|dump|bak)$", "database dump/backup"),
]

CONTENT_PATTERNS = [
    (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "private key"),
    (r"\bsk-(ant-)?[A-Za-z0-9_-]{20,}", "API key (sk- prefix)"),
    (r"\bgh[opsu]_[A-Za-z0-9]{36}", "GitHub token"),
    (r"\bAKIA[0-9A-Z]{16}\b", "AWS access key"),
    (r"\bxox[baprs]-[A-Za-z0-9-]{10,}", "Slack token"),
    (r"(?i)authorization:\s*(bearer|basic)\s+[A-Za-z0-9._~+/=-]{16,}", "authorization header"),
    (r"[a-z][a-z0-9+.-]*://[^/\s:@]+:[^@\s]{4,}@", "connection string with credentials"),
    (r"(?i)\b(password|passwd|secret|api[_-]?key|access[_-]?token)\b\s*[:=]\s*['\"]?[^\s'\"<$]{8,}",
     "possible credential assignment"),
]

PLACEHOLDER = re.compile(r"(?i)example|placeholder|changeme|your[_-]|xxxx|redacted|dummy|\.\.\.")


def git(*args):
    r = subprocess.run(["git", *args], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return r.returncode, r.stdout


def main():
    # self-locate the repo root: check-ignore and cat-file take root-relative
    # paths from git's own output, so the cwd must be the root
    code, top = git("rev-parse", "--show-toplevel")
    if code != 0:
        print("GATE FAIL: 1 finding(s)")
        print("- RANGE not a git repository")
        return 1
    os.chdir(top.strip())

    outgoing = "--outgoing" in sys.argv
    if outgoing:
        code, _ = git("rev-parse", "@{upstream}")
        if code != 0:
            print("GATE FAIL: 1 finding(s)")
            print("- RANGE no upstream configured; cannot determine outgoing range")
            return 1
        base = ["diff", "@{upstream}", "HEAD"]
    else:
        base = ["diff", "--cached"]

    findings = []

    code, raw = git(*base, "--raw")
    code, numstat = git(*base, "--numstat")
    files = {}
    for line in numstat.splitlines():
        parts = line.split("\t")
        if len(parts) == 3:
            files[parts[2]] = (parts[0], parts[1])
    if not files:
        print("GATE PASS: 0 files (nothing in snapshot)")
        return 0

    for line in raw.splitlines():
        if "\t" in line and line.split()[1].startswith("120000"):
            findings.append((line.split("\t")[-1], "", "symlink"))

    adds = dels = 0
    for path, (a, d) in files.items():
        binary = a == "-"
        if not binary:
            adds += int(a)
            dels += int(d)
        for pat, label in NAME_PATTERNS:
            if re.search(pat, path):
                findings.append((path, "", f"suspicious name: {label}"))
        code, size = git("cat-file", "-s",
                         f"HEAD:{path}" if outgoing else f":{path}")
        if code == 0 and size.strip().isdigit() and int(size) > MAX_BYTES:
            findings.append((path, "", f"large file {int(size) / 2**20:.1f} MiB"))
        # --no-index: plain check-ignore skips files already in the index,
        # which is precisely the force-add case this check exists to catch
        code, ignored = git("check-ignore", "--no-index", "--", path)
        if code == 0 and not outgoing:
            findings.append((path, "", "matches .gitignore rules (force-added?)"))

    code, diff = git(*base, "-U0")
    path, lineno = "", 0
    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            path = line[6:]
        elif line.startswith("@@"):
            m = re.search(r"\+(\d+)", line)
            lineno = int(m.group(1)) - 1 if m else 0
        elif line.startswith("+") and not line.startswith("+++"):
            lineno += 1
            for pat, label in CONTENT_PATTERNS:
                m = re.search(pat, line)
                if m and not PLACEHOLDER.search(m.group(0)):
                    findings.append((path, str(lineno), label))
                    break

    if findings:
        print(f"GATE FAIL: {len(findings)} finding(s)")
        for path, line, label in findings:
            loc = f"{path}:{line}" if line else path
            print(f"- {loc} {label}")
        return 1
    scope = "outgoing" if outgoing else "staged"
    print(f"GATE PASS: {len(files)} {scope} files, +{adds} -{dels}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
