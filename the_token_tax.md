# The Token Tax: A Thermodynamics of Agent Skills

> *"When the party ends, the tax man comes knocking. It's all about energy."*

Notes derived from working conversations with Claude Code (2026-07-17; Principle 9 and
the parking lot added 2026-07-19), companion to the
DeepLearning.AI short course **"Agent Skills with Anthropic"**. Organized not as a lecture
but as a set of energy-minimization principles: what to do, and why the physics of token
compute makes it the right thing to do.

**The governing idea:** token compute is energy. Every token generated is a forward pass;
every token resident in context is re-attended on every subsequent generation. The
engineer's job is the **minimum energy solution** — placing each piece of knowledge or
logic at the lowest energy level at which it still works. Everything below is a corollary.

---

## The energy ladder

Work can live at four levels. Push everything down the gradient as far as it will go.

| Level | Mechanism | Cost profile |
|---|---|---|
| **Generation** | The model reasons it out in tokens | Most expensive, least reliable |
| **Retrieval** | The model reads a reference file into context | Cheaper, exact, paid only when read |
| **Execution** | A script runs; only its *output* enters context | Near-zero token cost, deterministic |
| **File operation** | A template/asset is copied or filled in | May never enter context at all |

Executing a script isn't a lower-energy state of the same substance — it's a **phase
change**. `scripts/validate.py` moves computation out of the LLM regime entirely, into
classical compute where arithmetic costs nanojoules instead of a forward pass through
billions of parameters. It is also testable and deterministic, which token generation
never is.

---

## Principle 1 — Registration is placement (there is no button)

**The advice.** To make a skill available, put a correctly structured folder in the
predetermined directory (`.claude/skills/` or `~/.claude/skills/` for Claude Code;
`.agents/skills/` per the open standard). That *is* the registration. Expect new skills
to be visible only at the next session start — the startup scan is the closest thing to
a "registration event" that exists.

**Why.** Convention-over-configuration keeps the always-on cost at its floor. The scan
loads only each skill's frontmatter — no manifest, no registry to maintain, no
registration machinery burning tokens or attention.

## Principle 2 — Skills have zero-point energy, not zero energy

**The advice.** Treat every installed skill as a small permanent tax: its frontmatter
`name` + `description` (a few dozen tokens) is loaded into context **every session,
whether the skill ever fires or not**. Uninstall skills nobody triggers; with fifty
skills installed, the zero-point energies sum, and a skill that never fires is leaking
heat.

**Why.** The frontmatter is the ground state — small but irreducibly nonzero, exactly
like the quantum-mechanical zero point. The body and assets are *potential* energy,
released only on excitation (a matching task). This is the entire token-overhead
bargain: pay dozens of tokens always so you pay hundreds only sometimes.

## Principle 3 — Context is rent, not a toll

**The advice.** Judge every addition to context by its *recurring* cost, not its size.
A 500-token skill body loaded needlessly is not a one-time charge — every subsequent
token the model generates attends over it. The question is never "is the window big
enough?" but "what am I paying to keep warm?" (Prompt caching discounts the rent; it
does not zero it.)

**Why.** Attention runs over everything resident. Cost scales with context length times
generation length. This is why keeping things *out* of context beats having a bigger
window.

## Principle 4 — Progressive disclosure is the load-bearing structure

**The advice.** Author skills along the disclosure ladder:

1. **Frontmatter** — always in context (unconditional).
2. **`SKILL.md` body** — loaded when the description matches the task.
3. **Bundled assets** (`references/*.md`, `scripts/`, templates) — read, executed, or
   operated on only when the body's pointers and the task call for them.
4. **Script execution** — logic that never enters context at all.

Anything in the body is paid on *every* trigger, so material needed only sometimes
belongs in a reference file behind an explicit pointer ("for PDF form fields, read
`references/forms.md`"). The model doesn't rummage speculatively — the author signposts
what *can* be loaded and when; the model decides whether *this* task needs it.

Note the format precisely: `SKILL.md` is a **Markdown file with a YAML frontmatter
block** — not a YAML file. Only the frontmatter is preloaded.

**Why.** This is encapsulation reinvented for context economy. Unlike object-oriented
encapsulation, nothing is *enforced* — no private state, no compiler-checked interface;
a skill is an open text document. What survives from OO is only the
interface/implementation split as an energy device: the description plays the interface,
the body plays the implementation you don't pay for until you need it. And the binding
differs fundamentally: an OO method dispatches deterministically; a skill is selected
**semantically** — the model reads the description and judges relevance. That semantic
matching is also what makes skills *discoverable* in a way class libraries are not.

## Principle 5 — Minimize energy *subject to correct dispatch*

**The advice.** Do not starve the frontmatter description. It is not documentation —
it is the **dispatch mechanism**. Spend enough tokens on it (trigger phrases, concrete
task shapes) to guarantee the skill fires when it should.

**Why.** This is a *constrained* minimization. Over-compress the description and the
skill stops triggering; the model then flails without it — expensive retries, wrong
answers, far more tokens than the description would have cost. A skill that never fires
is a **false vacuum**: it looks like the ground state, but the system is stuck in the
wrong minimum. Reliable dispatch is what makes every other saving reachable.

## Principle 6 — When the logic is deterministic, ship a script

**The advice.** Any part of a skill that is a *procedure* rather than a *judgment* —
validation, arithmetic, data transformation, file generation, format checking — belongs
in a bundled script (`scripts/validate.py`), with the `SKILL.md` body instructing the
model to **run it, not reason through it**. The model can execute a script it has never
read: only the command and the script's *output* enter the context window; the source
never does. Design script output accordingly — terse on success, specific on failure —

**Why.** This is the phase change from the energy ladder, and it pays twice. First,
energy: logic of arbitrary complexity drops out of the token regime entirely — a
thousand-line validator costs the same handful of context tokens as a one-liner,
because only its invocation and result are ever seen. Second, and just as important,
**reliability**: token generation is probabilistic, so an LLM "computing" a sum or
applying a rule set is sampling, not calculating. A script is deterministic, testable
in isolation, and version-controlled. Asking the model to do fuzzy arithmetic when a
script could do exact arithmetic is paying *more* energy for a *worse* answer — the
only square on the board that loses on both axes.

## Principle 7 — Sub-agents are recursion, and recursion is energy containment

**The advice.** Delegate to a sub-agent when the exploration is bulky relative to the
answer (big search, small conclusion). Do not delegate small tasks — you pay a cold
start and prompt-serialization overhead to save nothing.

**Why.** A sub-agent is the same LLM invoked again with a **fresh, empty context** —
same function, new stack frame. The context window is the activation record:

- **No inheritance.** The child sees none of the parent's conversation. It gets its
  system prompt (possibly a specialized agent definition), a restricted tool set, and
  the task prompt. It shares the *environment* (filesystem, working directory, skill
  directories — the heap), but that is common access, not inheritance.
- **Pass-by-value.** Everything the child needs must be serialized into the task prompt.
  The most common sub-agent failure is a missing argument — the parent knows something
  crucial and forgets the child won't.
- **The final report is the return value.** The parent never sees the child's tool
  calls or dead ends. The child may burn 100k tokens exploring; all that rent is paid
  inside the child's frame, and when the child returns, **the frame is freed**. The
  parent absorbs only the summary. That containment is the entire point.
- **Self-similar, one level down.** The child re-scans skill directories (paying the
  zero-point energies afresh in its frame) and relates to the harness exactly as the
  parent does. In practice recursion is capped at one level — sub-agents usually lack
  the Agent tool — so the shape is fork/join, not deep nesting. The more powerful
  pattern is breadth anyway: fan out parallel children over independent subproblems
  and join on their summaries. That's `map`, not recursion.

## Principle 8 — Files are the state channel: handoff, not whiteboard

**The advice.** Use the shared filesystem to pass bulk state between frames — it is
pass-by-reference through the heap, and it is the recommended idiom **when done as a
disciplined handoff**:

- Pass paths **explicitly by name** in the prompt ("analyze `L5/data/`, write findings
  to `scratchpad/findings.md`") — never "look around and figure out what I meant."
- **Write-once** outputs; **one writer per file**.
- Parent reads results only **after the child returns** — a clean join.
- Rules of thumb: **files for bulk, prompts for instructions, return summaries for
  conclusions.** Use a scratch area for intermediates rather than littering the repo.

Avoid the **shared-whiteboard pattern**: parallel children writing to the same file, or
a child mutating files the parent is simultaneously reasoning about.

**Why.** A file reference costs a dozen prompt tokens where inlining costs thousands.
But there is no locking, no transactions, no change notification — concurrent writers
interleave or clobber, and the parent's mental model of a file silently goes stale the
moment a child edits it: classic shared-memory hazards with none of the classic
mitigations. And files outlive the frames that created them — which is the feature
(persistence across sessions) and the hazard (stale debris a future session reads as
truth).

**The elegant closure:** a skill *is* this pattern, standardized. A skill folder is
precisely "state communicated through assets on disk" — one session authors `SKILL.md`;
a later session, a sub-agent, or a different CLI entirely discovers and reads it. Skills
are the disciplined endpoint of file-based state sharing.

## Principle 9 — Crystallization: the gradient toward colder engines

**The advice.** Author skills with the most capable model available, then *freeze* the
result: deterministic logic into scripts, invariants into a bundled test suite,
judgment reduced to its irreducible remnant in the body. Once frozen, execute the
skill with the cheapest engine that clears the remaining judgment bar. Pay for genius
once, at design time; pay commodity rates at runtime, forever.

**Why.** The token tax has two axes — *fewer* tokens and *cheaper* tokens — and this
principle serves the second. Temperature, in this system, is model capability. Running
hot anneals the problem: the expensive model finds the minimum-energy structure.
Crystallization freezes that structure into artifacts on disk, and the latent heat
released is the one-time engineering cost of writing the scripts and their tests. The
crystal then performs at any temperature above a floor — set not by the average task
but by the **hardest surviving judgment call** (dispatch, interpreting user context,
the stop-veto on a safety finding). And crystals travel: a skill folder is crystallized
competence in the open-standard lattice, wieldable by any compatible engine — the
premium model's reasoning, amortized across every cheap engine that ever picks it up.

**The corollary, learned the hard way.** The phase change is incomplete until the
script is *self-testing*. Prose cannot have a parsing bug; a script can, and it fails
silently and precisely rather than loudly and fuzzily. Moving work down the ladder
converts a recurring token tax into a one-time engineering **mortgage — and the
mortgage payments are called tests.** Ship the script *and* its test, or you have only
moved the fuzziness somewhere harder to see.

---

## Parking lot: the thermometer we don't have

Deliberately deferred — one breakthrough at a time. The bundled tests protect the
**crystal**, not the **engine wielding it**. A test suite proves the gate still catches
the planted key; it proves nothing about whether a colder model *runs* the gate, heeds
a BLOCKED line, or exercises the veto on a genuine finding. The judgment remnant is
precisely the part with no test suite — so the claim "no degradation in capability"
is, today, verified only at the temperature it was authored at.

The missing artifact is a **judgment eval**: synthetic scenarios that probe the engine,
not the lattice — *here is a gate finding; does the bot stop?* Until that exists, we
can X-ray the crystal but cannot take the temperature of the fluid, and we do not know
at what temperature the logic snaps. Parked, not forgotten.

---

## The ledger: Anthropic-specific vs. open standard

| Open standard (agentskills.io) — portable | Per-platform plumbing |
|---|---|
| `SKILL.md` format: Markdown + YAML frontmatter | Scan paths (`.claude/skills/` vs others) |
| Frontmatter-as-dispatch (name + description) | Session-start scan timing |
| Progressive disclosure ladder (all four levels) | How the CLI surfaces skills to the model |
| Registration-by-placement convention | `CLAUDE.md` / `AGENTS.md` instruction files |
| Bundled `references/`, `scripts/`, assets | Slash-command invocation |
| The thermodynamics — every compatible platform inherits them | **All orchestration**: the Agent tool, sub-agent definitions, report/return mechanics, nesting limits (Claude Code, Agent SDK, and Codex each differ) |

The *concept* of fresh-context recursion with pass-by-value prompts and summary returns
is generic agentic architecture that serious harnesses converge on — but none of it is
part of the skills standard.

---

## The whole game, restated

Frontmatter = zero-point energy (spend enough to guarantee excitation).
Body = pay-per-trigger (only what every invocation needs).
References = pay-per-branch.
Scripts = out of the token regime entirely — and self-testing, or the move isn't finished.
Sub-agents = disposable frames that contain the burn.
Files = the heap, handled with handoff discipline.
Crystallization = anneal hot once, run cold forever; the floor is the hardest
surviving judgment call.

Put each piece of knowledge or logic at the lowest energy level at which it still
works, executed by the coldest engine that still clears the bar. That is the minimum
energy solution, and it is the job — as ever.
