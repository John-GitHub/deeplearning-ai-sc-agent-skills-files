# Claude Code: Fullscreen Rendering & Remote Control — Notes and Security Posture

John's derived notes, companion to `claude_code_context_commands.md`. Covers two
**research-preview** features (behavior may change between versions; verified against
docs 2026-07-19): fullscreen rendering (`/tui`) and Remote Control (`/remote-control`).
Both change *how you interact* with a session, not what the model can do.

**Terms, defined once:**

- **Renderer** — how Claude Code draws its interface in the terminal. Two modes:
  `default` (classic) and `fullscreen`.
- **Alternate screen buffer** — a second, temporary screen the terminal switches to,
  the way `vim` or `htop` takes over the window. Your normal scrollback still exists
  underneath and returns when the program exits.
- **Clipboard** — the system-wide copy/paste buffer. Anything on it can be pasted (or
  read by other applications) until overwritten.
- **Remote Control** — an opt-in link between a local Claude Code session and
  claude.ai / the Claude mobile app, so you can steer the session from another device.

---

## Part 1 — Fullscreen rendering

### What it is, and when/why to use it

Fullscreen mode redraws the interface on the alternate screen buffer instead of
printing into normal scrollback. Results: no flicker while output streams, flat memory
use in long conversations, mouse support (click menus, scroll wheel, click-to-expand
tool output), and the input box pinned to the bottom.

**Use it when:** long sessions; terminals where classic mode flickers or the scroll
position jumps (VS Code integrated terminal, tmux); you want mouse-driven navigation.

**Skip it when:** you rely on your terminal's native scrollback, `Ctrl+F`/tmux search,
and native click-drag-copy — in fullscreen those work differently (see the hazard
below). It's also a research preview: on Windows Terminal, stale screen fragments can
appear (fix: set the env var `CLAUDE_CODE_ALT_SCREEN_FULL_REPAINT=1`).

### Invoke, revert, verify

All three are typed inside a Claude Code session:

| Command | Effect |
|---|---|
| `/tui fullscreen` | Switch to fullscreen; saves `"tui": "fullscreen"` to `~/.claude/settings.json` and relaunches with the conversation intact |
| `/tui default` | Switch back to the classic renderer (saves the setting the same way) |
| `/tui` | Print which renderer is active — the verification command |

Telltale sign without typing anything: if the input box stays pinned at the bottom
while output streams, fullscreen is active.

### The clipboard hazard ("oops, I copied a secret")

In fullscreen mode, **click-and-drag selection auto-copies to the system clipboard on
mouse release.** No Ctrl+C needed. If a secret (API key, token, password) is ever on
screen — from a `.env` file, an error message, a pasted config — one stray drag puts
it on your clipboard, where any app can read it and where you might paste it somewhere
public.

Mitigations, strongest first:

1. **Use the default renderer** (`/tui default`) — selection then behaves natively and
   copies only when you explicitly copy.
2. **Or keep fullscreen but disable auto-copy:** run `/config` and turn **Copy on
   select** off. Copying then requires an explicit `Ctrl+Shift+C`.
3. **Keep secrets off the screen entirely** — the upstream fix. Never paste keys into
   a session; never ask Claude to print a `.env`. What is never displayed cannot be
   mis-copied. (Note: Claude Code itself never displays your login credential, and the
   statusline gauge shows costs, not keys.)

### If the renderer choice drifts

The choice lives in one place: the `tui` key in `~/.claude/settings.json`. To audit
from any shell:

```bash
grep '"tui"' ~/.claude/settings.json
```

Expected (John's choice): `"tui": "default"` — or the key absent, since default is the
default. If it says `"fullscreen"` and you didn't choose that, run `/tui default` in
any session, or edit the file directly. Nuclear option: the env var
`CLAUDE_CODE_DISABLE_ALTERNATE_SCREEN=1` forces the classic renderer regardless of
what the setting says.

---

## Part 2 — Remote Control

### What it is

Remote Control connects a session running **on your machine** to claude.ai/code or the
Claude phone app, so you can watch and steer it from another device. Execution and
file access stay local; the other device is a window. It is **off unless you
explicitly start it.**

### How it gets activated (know the spells so you recognize them)

- `claude remote-control` in a terminal (server mode, waits for connections)
- `claude --remote-control` (normal session, also reachable remotely)
- `/remote-control` (or `/rc`) typed inside an existing session — CLI or VS Code
- The only *automatic* path: a `/config` toggle named **"Enable Remote Control for all
  sessions"**. Leave it off/unset and nothing auto-connects, ever.

### How to tell if it's active

- **Terminal:** an `/rc active` indicator appears in the footer below the input box.
  No indicator = not connected.
- **VS Code:** a connection-status banner above the prompt box.
- Failure or disconnect removes the indicator and shows a notification.

### How to turn it off

- **This session:** run `/remote-control` again (or click the banner's close icon in
  VS Code). Closing the terminal/process also ends it — the session cannot outlive the
  local process.
- **Permanently (the hard off-switch):** add `"disableRemoteControl": true` to
  `~/.claude/settings.json`. Sessions then refuse to start it at all.

### Security notes

- The connection is **outbound HTTPS only** — no inbound ports are opened on the
  machine.
- **While connected, the session transcript (messages, responses, tool activity) is
  stored on Anthropic's servers** to sync devices. That is the real privacy trade:
  local-only conversation becomes server-resident conversation. Don't run Remote
  Control on sessions handling material you want to keep strictly local.
- Requires claude.ai subscription login. **API keys cannot use Remote Control at
  all** — so an accidental key exposure cannot happen through this feature; it doesn't
  accept keys.
- Anyone with access to your claude.ai account can steer a connected session, which
  executes on your machine with your permissions. Account security (password, 2FA) is
  therefore machine security while a session is connected.

---

## Part 3 — Drift audit (one command)

John's standing choices: **default renderer, Remote Control never automatic.** All of
it lives in `~/.claude/settings.json`, so one command audits everything:

```bash
grep -E '"tui"|RemoteControl|remoteControl' ~/.claude/settings.json
```

Healthy output: either nothing, or `"tui": "default"`, or `"disableRemoteControl":
true`. Anything else — `"fullscreen"` you didn't choose, an auto-connect toggle you
didn't set — edit the file back or use the in-session commands above. The file is
plain text; it can't hide anything from `grep`.

In-session equivalents: `/tui` (which renderer), look for `/rc active` in the footer
(remote state), `/status` (which account/auth is in use).

## Ledger note

Everything here — `/tui`, the alternate-screen renderer, Remote Control, `settings.json`
keys — is **Claude Code plumbing**, not the open Agent Skills standard. The portable
lesson: an agent's interface conveniences (auto-copy, remote steering) are also its
security surface; know the off switches and where the state lives.
