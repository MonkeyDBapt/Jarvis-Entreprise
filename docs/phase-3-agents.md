# Phase 3 — Agents

## 3.1 — Modèle d'organisation

Phase 3 begins by defining the organizational domain above the Phase 2 execution socle.

### Hierarchy

```text
Organization
└── Pole
    └── Team
        └── Agent
```

### Responsibility boundaries

- `Organization`, `Pole`, `Team`, and `Agent` describe the JARVIS organizational structure.
- An `Agent` in this model is an organizational definition, not an execution runtime.
- Execution remains delegated to the existing runtime/orchestration layers from Phase 2.
- No specialized agent implementation is introduced in step 3.1.

### Current model

The domain model provides:

- stable identifiers (`id`);
- human-readable names;
- optional descriptions;
- explicit parent/child collections;
- duplicate identifier protection within each parent scope.

## 3.2 — Modèle Agent

### Decision

The `Agent` model is kept declarative and deliberately separated from execution.

Three possible levels were considered:

1. **Minimal identity only** — `id`, `name`, `description`.
2. **Declarative operational definition** — identity plus role, capabilities, and configuration.
3. **Runtime-coupled model** — add lifecycle/status and execution methods directly to the agent.

Option **2** is retained because it gives JARVIS enough information to describe and configure an agent without coupling the organizational model to Hermes or another runtime. Option 3 is rejected at this stage because it would mix responsibilities already separated in the Phase 2 architecture.

### Agent contract

An `Agent` contains:

- `id`: stable identifier;
- `name`: human-readable name;
- `role`: organizational/function role;
- `description`: optional human-readable description;
- `capabilities`: declared capabilities, represented as names for now;
- `configuration`: declarative agent configuration, kept generic for future evolution.

The model does **not** contain runtime status, lifecycle methods, routing, permissions, governance, messaging/events, memory implementation, or specialized business logic. Those concerns remain separate and can be connected by later Phase 3 steps.

### Compatibility

`role`, `capabilities`, and `configuration` have defaults so the existing Phase 3.1 organizational hierarchy remains valid without forcing premature detail into existing callers.

## 3.3 — Registre des agents

### Decision

The agent registry is a JARVIS-owned domain service that indexes declarative `Agent` definitions by their stable identifier. It is deliberately independent from runtime execution and from the organizational hierarchy's parent/child collections.

### Registry contract

`AgentRegistry` provides:

- `register(agent)`: register an agent by stable `id`;
- `get(agent_id)`: retrieve a registered agent;
- `contains(agent_id)`: check whether an identifier is registered;
- `list_agents()`: list registered agents in registration order;
- `unregister(agent_id)`: remove and return an agent.

Agent identifiers are unique within the registry. Registering an existing identifier raises `ValueError`; retrieving or removing an unknown identifier raises `KeyError`.

### Responsibility boundary

The registry is an index, not an execution manager. It does **not** start or stop agents, invoke runtimes, perform routing, grant permissions, apply governance, manage messaging/events, or implement specialized agent logic.

This keeps the separation established in Phase 2 and 3.2: the declarative agent definition remains independent from `AgentRuntime`, MAF, Hermes, and future runtime implementations.

### Validation

3.3 is validated by the GitHub Actions `Validation` workflow on commit `d4bbb36f7fcbf752e9e7d347bf8f3e6c6fdd105c`.

The workflow passed on Python 3.10, 3.11, 3.12, and 3.13. The suite ran 11 tests successfully, including the five dedicated `AgentRegistry` tests covering registration, lookup, duplicate rejection, ordering, removal, and unknown identifiers.

**3.3 — Registre des agents: VALIDÉE.**
