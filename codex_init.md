# Codex initialization notes

Last checked: 2026-07-15

This file records the preliminary configuration checked for this repository and explains an environment issue that may affect other coding agents.

## Repository instructions

- Removed the Copilot-specific `.github/copilot-instructions.md` file.
- Added the Codex-native repository guidance in the root `AGENTS.md` file.
- The repository instructions preserve the original learning-focused guidance.

## Verified tools and authentication

The following were verified in the normal Windows user environment:

- Codex CLI `0.144.2`, authenticated through ChatGPT.
- GitHub CLI `2.96.0`, authenticated as `John-GitHub`.
- Git `2.51.0.windows.1`.
- Python `3.14.3`.
- `uv 0.11.28`.
- GitHub repository access with `ADMIN` permission.
- A global Codex configuration at `C:\Users\johnp\.codex\config.toml`.
- The `C:\projects` directory is trusted by Codex.

Do not place authentication tokens or other secrets in this file.

## Important `uv` environment note

Codex's restricted shell initially reported that `uv` was missing and did not recognize the `uv` command. Windows Package Manager then reported that `astral-sh.uv` version `0.11.28` was already installed.

The likely cause was environment visibility: Claude Code and Copilot could see the normal user's command alias or `PATH`, while Codex's restricted shell could not.

To repair the command registration, the verified Winget package was installed again:

```powershell
winget install --id astral-sh.uv --exact --accept-package-agreements --accept-source-agreements
```

Winget detected the existing package, reinstalled it, and registered the `uv`, `uvx`, and `uvw` command aliases. No project dependencies were changed.

Afterward, `uv --version` succeeded in the normal user environment. Existing lockfiles were checked with:

```powershell
uv --directory .\L6 lock --check
uv --directory .\L7 lock --check
```

Both checks succeeded. Neither `uv sync` nor a package upgrade was run. No `pyproject.toml`, `uv.lock`, or virtual environment was modified.

If `uv` is visible in a normal terminal but missing inside an agent sandbox, compare the sandbox's `PATH` and command-alias visibility before reinstalling it again. Reopening an older terminal may also be necessary after Winget updates command aliases.

## Git configuration

The global Git configuration originally contained the placeholder email `john@example.com`. It was replaced with the verified GitHub account identity:

```text
user.name = John-GitHub
user.email = 8096858+John-GitHub@users.noreply.github.com
```

The GitHub private commit address associates commits with the account without publishing a personal email.

## Project-specific Codex configuration

No repository-level `.codex/config.toml` was added. The existing global Codex configuration plus the root `AGENTS.md` file are sufficient for the current repository.
