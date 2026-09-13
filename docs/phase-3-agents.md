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

The model deliberately does not yet define routing, permissions, governance policies, messaging/events, or specialized agent capabilities. Those concerns remain subsequent Phase 3 work unless a later validated decision changes the scope.
