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

**Phase 4 — Capacités : en cours.**

| Étape | Statut |
|---|---|
| 4.1 — Modèle de capacité | ✅ Validée |
| 4.2 — Registre des capacités | ✅ Validée |
| 4.3 — Affectation capacités / agents | ✅ Validée |
| 4.4 — Exécution des capacités | ✅ Validée |
| 4.5 — Gestion des outils | ✅ **Validée** |

The Phase 4 capability architecture is:

```text
CapabilityRegistry
       │
       ▼
CapabilityAssignmentManager
       │
       ▼
CapabilityExecutor
       │
       ▼
Capability handler
       │
       └── may consume reusable tools
                  │
                  ▼
             ToolRegistry
                  │
                  ▼
              Tool definitions
```

`Tool` and `ToolRegistry` provide JARVIS-owned management of reusable tool definitions without creating a second execution path. Capability execution remains the authoritative execution boundary; concrete tool behavior is deliberately deferred to the component that will consume the tool.

The detailed record is available in [`docs/phase-4-5-gestion-outils.md`](docs/phase-4-5-gestion-outils.md).

## Tests

Run the local test suite with:

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
```

GitHub Actions validates the package and test suite across Python 3.10, 3.11, 3.12, and 3.13.
