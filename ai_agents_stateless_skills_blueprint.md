# Architectural Blueprint: AI Agents & Stateless Skills

## Systems Architecture, Assertion Testing, & Energy Minimization Matrix

---

## 1. Executive Paradigm Shift: Subject vs. Object

Modern AI systems architecture departs radically from traditional Object-Oriented Programming (OOP) design patterns. To resolve implementation complexities, the developer environment must clearly partition system components along the lines of Subject and Object:

- **The Configuration (The Rules):** A static blueprint or schema (e.g., YAML definitions, `CLAUDE.md` instructions, environment configs). It determines boundaries, naming conventions, and constraints, but has no execution capacity.
- **The Skill (The Tool / Object):** A self-contained package of discrete capabilities. It contains metadata schemas plus executable logic (such as localized Python modules). It is strictly an object—it remains passive until invoked by an orchestration engine.
- **The Agent (The Control Loop / Subject):** The stateful runtime orchestration engine. It consists of a persistent software execution loop (typically a state machine wrapped around an LLM API), tracking operational history inside a context window. It acts as the subject that dynamically utilizes stateless tools.

---

## 2. Directory Topology & Resolution Mechanics

Local developer environments utilize a layered inheritance file engine, mapping capabilities directly to filesystem scopes. This allows for clean segregation between global utilities and domain-specific workspace rules.

### A. Hierarchical Scoping

| Scope Level | Physical Location (Windows 11) | Operational Purpose |
|---|---|---|
| **User Level (Global)** | `C:\Users\<User>\.ai_skills\` | Cross-project, machine-wide utilities (e.g., code linters, structural sanitizers). |
| **Project Level (Local)** | `C:\<ProjectRoot>\.ai_skills\` | Domain-specific tools matched explicitly to the codebase architecture (e.g., custom financial database pipelines). |

### B. Scoped Resolution Mechanics

When an agent initializes within a designated project directory, it runs an isolated lookup sequence to compile available capabilities:

$$\text{Project-Level Scope} \ (\text{.\.ai\_skills\}}) \longrightarrow \text{User-Level Scope} \ (\text{~\.ai\_skills\}})$$

### C. The Version Control System (VCS) Boundary

- **Committed Skills:** Retaining the skill directory inside the main repository branch ensures team-wide automation consistency.
- **Ignored Skills:** Adding specific skill signatures to `.gitignore` enables experimental, user-specific scratchpads containing system-bound physical paths or local debugging routines.

---

## 3. The Architecture of Statelessness and State Management

> **Core Architecture Principle:** To eliminate silent execution failures, capabilities must be designed as stateless, pure functions. Mutual state transformation must be handled explicitly through the central agent, rather than via internal skill drift.

### A. The OOP Encapsulation Anti-Pattern

In classical software engineering, objects encapsulate both state and behavior. Applying this paradigm to AI architecture by allowing skills to stealthily modify files within their own localized subdirectories creates unpredictable side-effects. It destroys idempotency—the guarantee that identical inputs yield identical outputs. Unchecked internal state shifts make historical comparisons (e.g., financial backtests) completely non-reproducible.

### B. Centralized State Registry Workflow

To avoid this, skills operate deterministically, and the agent explicitly writes operational data to a centralized data warehouse or artifact directory:

1. The Agent reviews the state history from a central data registry (e.g., an asset database or a unified `project_state.json`).
2. The Agent calls the Stateless Skill, explicitly feeding the compiled parameters into the tool arguments: `run_backtest(ticker="NVDA", data=payload)`.
3. The Skill computes the logic as a pure engine, transmits the raw execution artifacts back to the Agent, and completely purges its temporary memory.
4. The Agent commits the final output back to the central warehouse ledger.

---

## 4. The Context Window Bottleneck & Macro Efficiency

Context window capacity acts as the primary hardware and cognitive constraint of agentic systems. Because an LLM computes relationships across all tokens simultaneously, flooding the prompt with excessive capabilities introduces severe degradation of focus.

The agent-skills complex represents a massive structural increase in context window (token) efficiency. Specificity and structure in the configuration files significantly improve response effectiveness and reduce the need to iterate and rework. Sub-agents reinforce these improvements by narrowing the required scope of the context window and refining the specificity of the prompt language. This systematic optimization ensures operational resilience before macroeconomic shifts drive API pricing above marginal compute costs.

---

## 5. Semantic Invocation & Tool Routing Mechanics

Mapping human communication directly to code execution loops bypasses traditional keyword lookup matrices. The system handles commands like *"Hey, will you update that report on NVDA that we ran last week?"* through a strict Two-Stage Semantic Resolution framework.

### A. Two-Stage Semantic Resolution

**Stage 1: Entity Extraction & Temporal Resolution:**
The Boss Agent evaluates the context boundaries. It anchors the specific real-world entities (Ticker: `NVDA`, Temporal Bound: *last week* relative to the current clock date, Target: *report*). It isolates the exact configuration parameters used in the historical run by inspecting the localized artifact directory.

**Stage 2: Tool Mapping:**
The Agent cross-references the user's operational intent against the global and local skill directories. It evaluates the natural language descriptions embedded in the tool manifest files, matching semantic equivalents (e.g., *"update,"* *"refresh,"* *"recalculate"*) to the target function definition.

### B. Manifest Construction Blueprint

```yaml
# Example Manifest Configuration Structure
tool_name: "run_asset_backtest"
description: >
  Use this tool to execute a quantitative backtest on a specific equity ticker
  over a designated historical period. Use this when a user asks to generate,
  refresh, recalculate, or update a performance report or trade simulation
  for a given financial instrument.
parameters:
  type: "object"
  properties:
    ticker:
      type: "string"
      description: "The uppercase stock ticker symbol (e.g., 'NVDA', 'AAPL')."
  required: ["ticker"]
```

---

## 6. Objective Assertion-Based Testing Framework

Prompt optimization must transition from heuristic adjustments to deterministic verification. Prompt language is validated using an engineering test harness that enforces programmatic checks on execution structures, syntax, and resource thresholds.

### A. Static Control Matrix (`tests/prompt_eval_matrix.json`)

```json
[
  {
    "test_id": "001_ambiguous_update",
    "user_input": "Hey, will you update that report on NVDA that we ran last week?",
    "expected_ticker": "NVDA",
    "requires_historical_lookup": true
  },
  {
    "test_id": "002_explicit_bounds",
    "user_input": "Run a backtest on AAPL from 2025-01-01 to 2025-12-31",
    "expected_ticker": "AAPL",
    "requires_historical_lookup": false
  }
]
```

### B. Programmatic Test Harness (`tests/test_agent_prompts.py`)

```python
import json
import pytest
from my_agent_core import run_agent_loop


def load_test_matrix():
    with open("tests/prompt_eval_matrix.json", "r") as f:
        return json.load(f)


@pytest.mark.parametrize("case", load_test_matrix())
def test_prompt_structural_robustness(case):
    # Execute the agent loop with the static control input
    response_object, metrics = run_agent_loop(case["user_input"])

    # Assertion 1: Verify prompt forces structured, parsable output
    assert isinstance(response_object, dict), "Prompt failed to enforce JSON schema."

    # Assertion 2: Verify parameter extraction accuracy
    assert response_object.get("ticker") == case["expected_ticker"], \
        f"Failed ticker extraction: {case['test_id']}"
    assert response_object.get("history_lookup") == case["requires_historical_lookup"], \
        f"Failed temporal routing: {case['test_id']}"

    # Assertion 3: Enforce token efficiency thresholds (Energy Minimization Gate)
    MAX_TOKEN_BUDGET = 1200
    assert metrics["total_tokens"] <= MAX_TOKEN_BUDGET, \
        f"Token leakage detected in prompt: {metrics['total_tokens']} used."
```

---

## 7. Macro Synthesis: Energy Minimization & The Human Lever

The systematic structural choices detailed in this document align with a deeper macroeconomic reality highlighted by researchers like Yann LeCun: frontier LLMs operate completely devoid of intrinsic world models or physical intuition. They are text-based probability engines bounded by statistical boundaries.

Because these computational networks possess no native salience mechanisms, they process noise and signal with identical mathematical weight. Unconstrained, they operate as thermodynamic sinks, burning immense amounts of compute power and token volume to reconstruct simple execution trajectories.

This reality cleanly delineates the barrier between human and machine roles:

- **The Human Lever (Subject):** The sole source of intent, context priority, structural design, and the ultimate willpower to act. The human operates via radical energy minimization, knowing intuitively which levers determine the final outcome and filtering out infinite background noise before a single token is generated.
- **The Bot Core (Object):** The processing engine, automated parsing matrix, and data synthesis system. It provides raw execution velocity but requires deterministic constraints to prevent catastrophic context loops and runaway compute costs.

By forcing AI systems into stateless micro-skills and strictly scoped sub-agents, the developer structures the environment so that the bot's computational velocity is entirely harnessed by human design. The architecture minimizes energy dissipation, optimizes token economics, and locks down the functional stability of local execution systems.
