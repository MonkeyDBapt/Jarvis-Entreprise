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

3.3 is validated by the GitHub Actions `Validation` workflow on commit `d4bbb36f7fcbf752e9e7d347bf8f3e6c6fdd105c`. The workflow passed on Python 3.10, 3.11, 3.12, and 3.13. The suite ran 11 tests successfully, including the five dedicated `AgentRegistry` tests covering registration, lookup, duplicate rejection, ordering, removal, and unknown identifiers.

**3.3 — Registre des agents: VALIDÉE.**

## 3.4 — Organisation pôles / équipes

### Decision

The existing organizational model remains the source of truth for the hierarchy. Step 3.4 adds a small JARVIS-owned `OrganizationManager` service to manage the **poles and teams** of an `Organization` without introducing routing, permissions, governance, messaging, or runtime behavior.

### Organization management contract

`OrganizationManager` provides:

- `add_pole(pole)`: add a pole to the managed organization;
- `get_pole(pole_id)`: retrieve a pole by stable identifier;
- `remove_pole(pole_id)`: remove and return a pole;
- `add_team(pole_id, team)`: add a team to an existing pole;
- `get_team(pole_id, team_id)`: retrieve a team within a pole;
- `remove_team(pole_id, team_id)`: remove and return a team within a pole.

Duplicate identifiers continue to be rejected by the existing domain model. Unknown poles or teams raise `KeyError`.

### Responsibility boundary

`OrganizationManager` manages **structure only**. It does not execute agents, select agents for tasks, route work, apply permissions or governance, or implement messaging/events.

The resulting separation is:

```text
OrganizationManager
        │
        ├── Pole
        │    └── Team
        │         └── Agent
        │
        └── organizational structure only

AgentRegistry ── indexes Agent definitions
AgentRuntime  ── executes agents
```

### Validation

Step 3.4 is covered by `tests/test_organization_manager.py`, including pole creation/retrieval/removal, team creation/retrieval/removal, duplicate protection, and unknown identifiers.

**3.4 — Organisation pôles / équipes: VALIDÉE.**

## 3.5 — Sélection / affectation

### Decision

Step 3.5 introduces a JARVIS-owned `AgentAssignmentManager` that performs two related organizational operations:

1. **selection** of registered agent definitions using declarative criteria;
2. **affectation** of a registered agent to an existing organizational team.

Selection is intentionally deterministic and does not invoke a runtime. Supported criteria are role, required capabilities, pole membership, and team membership. When multiple criteria are supplied, they are combined as an AND filter.

### Selection contract

`AgentSelectionCriteria` supports:

- `role`: exact role filter;
- `capabilities`: required capability names; an agent must provide all of them;
- `pole_id`: restrict candidates to agents already assigned within a pole;
- `team_id`: restrict candidates to agents assigned to a team, optionally within a specified pole.

`AgentAssignmentManager.select()` returns registered `Agent` definitions in registry order. No runtime is started and no task is executed.

### Assignment contract

`AgentAssignmentManager.assign(agent_id, pole_id, team_id)`:

- requires the agent to exist in `AgentRegistry`;
- requires the target pole and team to exist;
- adds the registered agent definition to the target team;
- preserves the existing duplicate-ID protection of `Team`.

Unknown agents, poles, or teams raise `KeyError`. Reassigning the same agent to the same team is rejected by the domain model with `ValueError`.

The current organizational model does not impose a global one-team-only constraint: an agent definition may be assigned to more than one team when explicitly requested. Any future exclusivity, permissions, governance, workload, or routing policy remains outside 3.5.

### Responsibility boundary

3.5 is **organizational selection and assignment only**. It does not:

- execute agents;
- choose a runtime;
- route a task to an agent;
- invoke MAF or Hermes;
- grant permissions;
- apply governance;
- manage messaging/events;
- implement specialized agent logic.

The separation is therefore:

```text
AgentRegistry
     │
     ▼
AgentAssignmentManager
     │
     ├── select() ──► candidate Agent definitions
     │
     └── assign() ─► OrganizationManager ─► Pole ─► Team ─► Agent

AgentRuntime ──► execution (separate concern)
```

### Validation

The dedicated `tests/test_agent_assignment.py` suite covers role/capability selection, assignment to a team, team-based selection, duplicate assignment rejection, unknown agents, and unknown teams.

**3.5 — Sélection / affectation: VALIDÉE.**

## 3.6 — Cycle de vie

### Decision

Step 3.6 introduces a JARVIS-owned `AgentLifecycleManager` for the lifecycle of registered agent definitions.

The lifecycle is deliberately separate from runtime execution. An `AgentLifecycleState` describes the organizational availability of an agent definition; it does not mean that Hermes, MAF, or another runtime process is currently running.

### States

```text
REGISTERED → ACTIVE ↔ INACTIVE → RETIRED
      └──────────────────────→ RETIRED
```

- `REGISTERED`: known to the lifecycle manager and not yet activated;
- `ACTIVE`: lifecycle-enabled and eligible for future execution/routing layers;
- `INACTIVE`: deliberately disabled without removing the agent definition;
- `RETIRED`: permanently removed from active lifecycle use.

### Transition rules

- `register()` validates that the agent exists in `AgentRegistry` and starts it at `REGISTERED`;
- `activate()` allows `REGISTERED → ACTIVE` and `INACTIVE → ACTIVE`;
- `deactivate()` allows `ACTIVE → INACTIVE`;
- `retire()` allows `REGISTERED → RETIRED` and `INACTIVE → RETIRED`;
- retired agents have no transition back to an active state;
- unknown agents and invalid transitions are rejected explicitly.

### Responsibility boundary

3.6 manages lifecycle state only. It does not:

- start or stop a runtime process;
- invoke Hermes or MAF;
- route tasks;
- grant permissions;
- apply governance;
- manage messaging/events;
- implement specialized agent logic.

This preserves the separation established by Phase 2 and the preceding Phase 3 steps.

### Validation

`tests/test_agent_lifecycle.py` covers initial registration, activation/deactivation, reactivation, terminal retirement, invalid transitions, unknown agents, and duplicate lifecycle registration.

The GitHub Actions `Validation` workflow for the lifecycle implementation passed on Python 3.10, 3.11, 3.12, and 3.13. The final documentation commit is also covered by a successful validation run.

**3.6 — Cycle de vie: VALIDÉE.**

## 3.7 — Intégration orchestrateur

### Decision

Step 3.7 connects the Phase 3 agent-management services to the existing Phase 2 orchestration boundary without moving runtime concerns into the domain model.

The orchestrator now performs the complete resolution path:

```text
OrchestrationRequest
        │
        ▼
AgentRegistry
        │
        ▼
AgentAssignmentManager / direct agent id
        │
        ▼
AgentLifecycleManager
        │
        ▼
ResolvedAgentRequest
        │
        ▼
Microsoft Agent Framework
        │
        ▼
AgentRuntime
        │
        ▼
HermesAdapter → Hermes
```

### Orchestration contract

`OrchestrationRequest` now supports:

- `agent_id`: explicit agent selection;
- `selection`: declarative `AgentSelectionCriteria` when the caller wants the orchestrator to resolve an agent.

The orchestrator resolves exactly one **active** agent before invoking MAF. An explicit inactive/unknown agent is rejected. A selection producing no active candidate is rejected, and a selection producing multiple active candidates is rejected rather than making an arbitrary choice.

The agent's declarative `configuration["model"]` supplies the model when the request does not specify one. Explicit request parameters remain authoritative.

### Responsibility boundary

3.7 deliberately keeps the responsibilities separated:

- Phase 3 core services define, index, organize, select, assign, and lifecycle-manage agents;
- `JarvisOrchestrator` resolves the organizational agent and creates the execution request;
- MAF remains the workflow engine;
- `AgentRuntime` remains the stable execution contract;
- `HermesAdapter` remains the current runtime implementation.

No permissions, governance, messaging/events, memory implementation, or specialized agent logic is introduced by 3.7.

### Validation

The orchestration tests verify:

- active agent resolution by explicit identifier;
- MAF → runtime execution through the resolved agent;
- agent configuration as the default model;
- refusal to execute an inactive agent.

GitHub Actions `Validation` run #44 for commit `c1da67fc88ca1a3f6886eeb030b2a5f850095b9f` passed its Python 3.10, 3.12, and 3.13 jobs; the Python 3.11 job was still queued when this documentation was prepared.

**3.7 — Intégration orchestrateur: IMPLÉMENTÉE ET VALIDÉE TECHNIQUEMENT, sous réserve de la fin du job CI Python 3.11.**
