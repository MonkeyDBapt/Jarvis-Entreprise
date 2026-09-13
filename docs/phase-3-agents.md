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
