# Jarvis-Entreprise

## Runtime

JARVIS Enterprise keeps external runtimes isolated from the main Python environment.

### Hermes Agent

Hermes is integrated as the operational agent runtime through `jarvis.runtime.HermesAdapter`.
Its source checkout and dependencies stay isolated under `.runtime/hermes-agent/` and are not vendored into the JARVIS package.

Setup in a Codespace:

```bash
git pull
bash scripts/setup_hermes.sh
```

The setup script clones the official Hermes repository, runs its supported `uv sync` environment setup, and verifies that `AIAgent` can be imported. Hermes currently requires Python `>=3.11,<3.14`; this is intentionally kept separate from JARVIS's main environment.

After setup, API/provider credentials must be configured according to Hermes' own configuration rules before executing model-backed tasks. Secrets must not be committed to Git.

### Microsoft Agent Framework

The JARVIS orchestration boundary is implemented with `agent-framework-core==1.18.0`.
`JarvisOrchestrator` builds a Microsoft Agent Framework workflow whose `HermesExecutor` delegates execution to the isolated `HermesAdapter` through the JARVIS `AgentRuntime` contract.

### Phase 2 status

**Phase 2 — Socle technique: clôturée.**

The consolidated reference architecture is:

```text
JARVIS Enterprise
       │
       ▼
JarvisOrchestrator
       │
       ▼
Microsoft Agent Framework
       │
       ▼
AgentRuntime
       │
       ▼
HermesAdapter
       │
       ▼
Hermes
       │
       ▼
LLM
```

The detailed consolidation record is available in [`docs/phase-2-socle.md`](docs/phase-2-socle.md).

### Phase 3 status

**Phase 3 — Construction du système d’agents : clôturée / consolidée.**

| Étape | Statut |
|---|---|
| 3.1 — Modèle d’organisation | ✅ Validée |
| 3.2 — Modèle Agent | ✅ Validée |
| 3.3 — Registre des agents | ✅ Validée |
| 3.4 — Organisation pôles / équipes | ✅ Validée |
| 3.5 — Sélection / affectation | ✅ Validée |
| 3.6 — Cycle de vie | ✅ Validée |
| 3.7 — Intégration orchestrateur | ✅ Validée |
| 3.8 — Validation / consolidation | ✅ **Validée** |

The Phase 3 organization is `Organization → Pole → Team → Agent`. JARVIS owns the agent definitions, registry, organization management, selection/assignment, lifecycle, and orchestration resolution. MAF remains the workflow engine, `AgentRuntime` remains the stable execution contract, and Hermes remains the current runtime implementation.

The consolidated Phase 3 architecture is:

```text
JARVIS Enterprise
       │
       ▼
Organization → Pole → Team → Agent
       │
       ▼
AgentRegistry
       │
       ▼
Selection / Assignment
       │
       ▼
Lifecycle
       │
       ▼
JarvisOrchestrator
       │
       ▼
Microsoft Agent Framework
       │
       ▼
AgentRuntime
       │
       ▼
HermesAdapter → Hermes → LLM
```

Permissions, advanced governance, messaging/events, specialized memory, and specialized business agents remain outside the Phase 3 consolidation and are reserved for later phases.

### Phase 4 status

**Phase 4 — Capacités : clôturée / consolidée.**

| Étape | Statut |
|---|---|
| 4.1 — Modèle de capacité | ✅ Validée |
| 4.2 — Registre des capacités | ✅ Validée |
| 4.3 — Affectation capacités / agents | ✅ Validée |
| 4.4 — Exécution des capacités | ✅ Validée |
| 4.5 — Gestion des outils | ✅ Validée |
| 4.6 — Sécurité / contrôle | ✅ Validée |
| 4.7 — Intégration orchestrateur | ✅ Validée |
| 4.8 — Validation / consolidation | ✅ **Validée** |

The consolidated Phase 4 architecture connects the capability and security domains to the existing JARVIS orchestrator without bypassing established boundaries:

```text
Subject
  │
  ▼
JarvisOrchestrator
  │
  ├── Agent resolution / lifecycle
  │
  ├── CapabilityRegistry
  │      │
  │      ▼
  │   CapabilityAssignmentManager
  │      │
  │      ▼
  │   SecurityControlledExecutor
  │      │
  │      ▼
  │   CapabilityExecutor
  │      │
  │      ▼
  │   Capability handler
  │
  └── Agent request → MAF → AgentRuntime → Hermes
```

The detailed Phase 4 consolidation record is available in [`docs/phase-4-8-validation-consolidation.md`](docs/phase-4-8-validation-consolidation.md).

### Phase 5 status

**Phase 5 — Mémoire : clôturée / consolidée.**

| Étape | Statut |
|---|---|
| 5.1 — Modèle de mémoire | ✅ Validée |
| 5.2 — Types / catégories | ✅ **Validée** |
| 5.3 — Stockage | ✅ **Validée** |
| 5.4 — Recherche / récupération | ✅ **Validée** |
| 5.5 — Contexte / injection | ✅ **Validée** |
| 5.6 — Contrôle / cycle de vie | ✅ **Validée** |
| 5.7 — Intégration orchestrateur | ✅ **Validée** |
| 5.8 — Validation / consolidation | ✅ **Validée** |

Phase 5.2 distinguishes the five functional memory forms `working`, `episodic`, `semantic`, `user`, and `system` through `MemoryKind`, while preserving the three high-level categories from 5.1 (`short_term`, `long_term`, `contextual`).

Phase 5.3 adds the `MemoryStore` persistence contract and the initial `SQLiteMemoryStore` backend. Memory data is persisted locally under `.data/memory.sqlite3`, which is excluded from Git. Storage remains independent from retrieval, ranking, expiration, embeddings, context injection, and orchestration integration.

Phase 5.4 adds the `MemoryRetriever` contract and the initial `SQLiteMemoryRetriever`. Retrieval is currently lexical, local, deterministic, case-insensitive, filterable by memory type/scope, and limited by result count. Embeddings, vector search, reranking, context injection, lifecycle and orchestration integration remain outside this step.

Phase 5.5 adds the `MemoryContextInjector` contract and the initial `RetrieverMemoryContextInjector`. It converts retrieved memories into bounded, deterministic prompt-ready context without coupling memory to MAF, Hermes, or the orchestrator. The injector preserves retrieval order and excludes a memory when it would exceed the configured character budget.

Phase 5.6 adds the `MemoryLifecycle` contract and `MemoryLifecycleManager`. Memories support explicit `active`, `archived`, and `expired` lifecycle states, optional ISO-8601 expiration metadata, restoration, permanent deletion, and explicit purge. Retrieval now excludes archived and expired memories, while legacy memories without lifecycle metadata remain active by default.

Phase 5.7 integrates the memory context boundary into `JarvisOrchestrator`. When a `MemoryContextInjector` is supplied, the orchestrator resolves the active organizational agent, retrieves bounded memory context from the user's request, and passes that context through the existing MAF workflow to the configured runtime. The integration remains optional and preserves the original execution path when no memory injector is configured. `memory_limit` bounds the number of memories requested per orchestration call.

Phase 5.8 validates and consolidates the complete memory architecture. The memory contracts remain separated, lifecycle rules remain enforced during retrieval, the orchestrator depends only on the context-injection boundary, and the existing Phase 1–4 execution and security boundaries remain intact. The detailed consolidation record is available in [`docs/phase-5-8-validation-consolidation.md`](docs/phase-5-8-validation-consolidation.md).

### Phase 6 status

**Phase 6 — Modèles / intelligence : clôturée / consolidée.**

| Étape | Statut |
|---|---|
| 6.1 — Modèle d’intelligence | ✅ Validée |
| 6.2 — Registre des modèles | ✅ Validée |
| 6.3 — Configuration | ✅ Validée |
| 6.4 — Sélection / routage | ✅ Validée |
| 6.5 — Stratégies d’utilisation | ✅ Validée |
| 6.6 — Contrôle / contraintes | ✅ Validée |
| 6.7 — Intégration / orchestration | ✅ Validée |
| 6.8 — Validation / consolidation | ✅ **Validée** |

Phase 6 establishes a provider-independent intelligence layer. `Model`, `ModelType`, and `ModelCapability` define declarative model contracts. `ModelRegistry` centrally registers models by stable identifier, rejects duplicates, supports lookup/removal, and exposes a deterministic immutable registration view. `ModelConfiguration` provides the provider-neutral configuration boundary for endpoints, parameters, context/output limits, operational limits, secret references, and provider-specific configuration; secrets themselves are never stored in model configuration or committed to Git.

`ModelSelectionRequest`, `ModelSelectionResult`, and `ModelRouter` provide deterministic provider-neutral routing. An explicit model id takes precedence, followed by requested capabilities, model type, provider, and registration order as a stable tie-breaker. `ModelUsageStrategy` expresses high-level intent (`balanced`, `fast`, `quality`, `economical`, `reasoning`) and translates it into the existing selection contract without provider execution or secret resolution.

`ModelControlConstraints` forms the hard control boundary. It can restrict providers and model types and enforce declared maximum context, output, and temperature limits. `ModelRouter` applies these controls before accepting a model, including explicit model requests, and deterministically rejects incompatible requests. Live quotas, real prices, latency, availability lookup, credentials, and provider execution remain outside this layer.

Phase 6.7 integrates model routing into `JarvisOrchestrator` while preserving the existing execution boundaries. The consolidated architecture is:

```text
OrchestrationRequest
  │
  ├── Agent resolution / lifecycle
  │
  ├── ModelUsageRequest
  │       │
  │       ▼
  │   ModelUsageStrategy
  │       │
  │       ▼
  │   ModelSelectionRequest
  │       │
  │       ├──────────────► ModelControlConstraints
  │       │
  │       ▼
  │   ModelRouter
  │       │
  │       ▼
  │   ModelRegistry
  │       │
  │       ▼
  │   Resolved model identifier
  │
  ▼
Microsoft Agent Framework
  │
  ▼
AgentRuntime
  │
  ▼
HermesAdapter / runtime concret
```

The router transmits only the selected model identifier to the runtime. No direct `ModelRouter → provider` or `ModelRegistry → provider` path exists. The historical `model` execution path remains compatible when intelligence routing is not requested.

Phase 6 validation covers default and reasoning strategies, explicit constraint preservation, registry/router selection, deterministic constraint filtering and rejection, selected-model transmission to the runtime, the historical path without intelligence routing, and inactive-agent rejection. GitHub Actions validates the package and test suite across Python 3.10, 3.11, 3.12, and 3.13. No real secret or credential is committed.

The detailed Phase 6 consolidation record is available in [`docs/phase-6-8-validation-consolidation.md`](docs/phase-6-8-validation-consolidation.md), with detailed records for 6.2–6.6 in the corresponding `docs/phase-6-*` files.

Provider-specific execution, credentials, dynamic availability/cost/latency evaluation, advanced fallbacks, and concrete provider integrations remain outside Phase 6 and are reserved for dedicated later phases.

### Phase 7 status

**Phase 7 — Communication : en cours.**

| Étape | Statut |
|---|---|
| 7.1 — Modèle de communication | ✅ Validée |
| 7.2 — Messages | ✅ Validée |
| **7.3 — Événements** | **✅ Validée** |

Phase 7.3 adds the transport-independent `EventDelivery` contract and the deterministic `InMemoryEventDelivery` baseline. Components can subscribe to event types, unsubscribe, and publish `CommunicationEvent` instances without depending on a concrete broker or transport. Delivery is synchronous and ordered by subscription registration. Duplicate subscriptions are rejected and publishing an event with no subscribers is a no-op.

The event boundary is intentionally limited at this stage: persistence, replay, durable delivery, retries/dead-letter handling, distributed brokers, wildcard routing, and specialized observability remain outside 7.3. The detailed record is available in [`docs/phase-7-3-evenements.md`](docs/phase-7-3-evenements.md).

## Tests

Run the local test suite with:

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
```

GitHub Actions validates the package and test suite across Python 3.10, 3.11, 3.12, and 3.13.
