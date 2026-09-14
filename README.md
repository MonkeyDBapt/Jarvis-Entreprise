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

**Phase 6 — Modèles / intelligence : en cours.**

| Étape | Statut |
|---|---|
| 6.1 — Modèle d’intelligence | ✅ Validée |
| 6.2 — Registre des modèles | ✅ **Validée** |

Phase 6.1 defines the provider-independent declarative `Model`, `ModelType`, and `ModelCapability` contracts. Phase 6.2 adds `ModelRegistry`, which centrally registers models by stable identifier, rejects duplicates, supports lookup and removal, and exposes a deterministic immutable registration view. Model selection/routing, provider adapters, execution, credentials, and intelligence strategies remain outside 6.2 and are reserved for later Phase 6 steps.

The detailed Phase 6.2 record is available in [`docs/phase-6-2-model-registry.md`](docs/phase-6-2-model-registry.md).

## Tests

Run the local test suite with:

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
```

GitHub Actions validates the package and test suite across Python 3.10, 3.11, 3.12, and 3.13.
