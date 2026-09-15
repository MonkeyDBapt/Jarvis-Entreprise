# Jarvis-Entreprise

JARVIS Enterprise is a modular assistant and orchestration system. JARVIS owns the architecture and keeps external implementations behind stable contracts.

## Reference architecture

```text
JARVIS Enterprise
       │
       ├── Organization → Pole → Team → Agent
       │
       ├── Capabilities → SecurityControlledExecutor
       │
       ├── Memory → Context Injection
       │
       ├── Intelligence → ModelRouter → ModelRegistry
       │
       ├── Communication → Router → Security → Delivery / Transport
       │
       ├── Permissions → Authorization → Autonomy → Control / Supervision
       │
       ├── Verification → VerificationReport → VerificationCheck
       │
       └── Observability → StructuredLogger → LogEntry
       │                 → MetricRegistry → MetricSnapshot
       │                 → TraceContext → TraceSpan → TraceRecorder
       │                 → HealthRegistry → SystemHealth
       │                 → AuditEvent → AuditRecorder
       │
       └── Resilience → Anomaly → Detection → Error Management → Containment → Recovery → Controlled Degradation
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

## Runtime

JARVIS Enterprise keeps external runtimes isolated from the main Python environment. Hermes is integrated through `jarvis.runtime.HermesAdapter`, with its checkout and dependencies isolated under `.runtime/hermes-agent/`.

Microsoft Agent Framework is provided by `agent-framework-core==1.18.0`. `JarvisOrchestrator` uses MAF workflows and delegates agent execution through the JARVIS `AgentRuntime` contract.

Secrets and provider credentials are never committed to Git.

## Phase 2 — Socle technique

**Clôturée / consolidée.** MAF, Hermes, interfaces/adaptateurs, orchestration, tests and CI are validated. See [`docs/phase-2-socle.md`](docs/phase-2-socle.md).

## Phase 3 — Construction du système d’agents

**Clôturée / consolidée.** Organization, agent model, registry, pole/team organization, selection/assignment, lifecycle and orchestrator integration are validated. See [`docs/phase-3-consolidation.md`](docs/phase-3-consolidation.md).

## Phase 4 — Capacités

**Clôturée / consolidée.** Capability model, registry, assignments, execution, tools, security/control and orchestrator integration are validated. See [`docs/phase-4-8-validation-consolidation.md`](docs/phase-4-8-validation-consolidation.md).

## Phase 5 — Mémoire

**Clôturée / consolidée.** Memory model, types, SQLite storage, retrieval, bounded context injection, lifecycle and orchestrator integration are validated. See [`docs/phase-5-8-validation-consolidation.md`](docs/phase-5-8-validation-consolidation.md).

## Phase 6 — Modèles / intelligence

**Clôturée / consolidée.** Provider-independent model contracts, registry, configuration, deterministic routing, usage strategies, hard constraints and orchestrator integration are validated. See [`docs/phase-6-8-validation-consolidation.md`](docs/phase-6-8-validation-consolidation.md).

## Phase 7 — Communication

**Clôturée / consolidée.**

| Étape | Statut |
|---|---|
| 7.1 — Modèle de communication | ✅ Validée |
| 7.2 — Messages | ✅ Validée |
| 7.3 — Événements | ✅ Validée |
| 7.4 — Routage | ✅ Validée |
| 7.5 — Canaux / transport | ✅ Validée |
| 7.6 — Contrôle / sécurité | ✅ Validée |
| 7.7 — Intégration orchestrateur | ✅ Validée |
| **7.8 — Validation / consolidation** | **✅ Validée** |

The communication layer is transport-independent. Messages and events use explicit contracts; routing selects direct/message/event paths; channel transports remain behind transport contracts; `SecurityController` authorizes communication before delivery; and `JarvisOrchestrator.run_and_reply()` integrates responses without bypassing these boundaries.

## Phase 8 — Permissions / autonomie

**Clôturée / consolidée.**

| Étape | Statut |
|---|---|
| 8.1 — Modèle de permission | ✅ Validée |
| 8.2 — Registre des permissions | ✅ Validée |
| 8.3 — Attribution / périmètre | ✅ Validée |
| 8.4 — Autorisation / décision | ✅ Validée |
| 8.5 — Niveaux d’autonomie | ✅ Validée |
| 8.6 — Contrôle / supervision | ✅ Validée |
| 8.7 — Intégration orchestrateur | ✅ Validée |
| **8.8 — Validation / consolidation** | **✅ Validée** |

The permission and autonomy layer remains distinct from capabilities. `AuthorizationEvaluator` decides whether an action is authorized; `ControlEvaluator` combines authorization and autonomy; `SupervisionEvaluator` applies control policies; and `JarvisOrchestrator` enforces these decisions before entering the MAF workflow.

## Phase 9 — Vérification / observabilité

**Clôturée / consolidée.**

| Étape | Domaine | Statut |
|---|---|---|
| 9.1 | Modèle de vérification | ✅ Validée |
| 9.2 | Journalisation / logs | ✅ Validée |
| 9.3 | Métriques / indicateurs | ✅ Validée |
| 9.4 | Traces / traçabilité | ✅ Validée |
| 9.5 | État / santé système | ✅ Validée |
| 9.6 | Audit / événements observables | ✅ Validée |
| 9.7 | Intégration orchestrateur | ✅ Validée |
| **9.8** | **Validation / consolidation** | **✅ Validée** |

The verification and observability layer is provider-independent. It exposes verification reports, structured logs, metrics, causal traces, health state and audit events, and integrates them into `JarvisOrchestrator` without imposing external observability infrastructure. See [`docs/phase-9-8-validation-consolidation.md`](docs/phase-9-8-validation-consolidation.md).

## Phase 10 — Anomalies / résilience

**En cours.**

| Étape | Domaine | Statut |
|---|---|---|
| 10.1 | Modèle d’anomalie | ✅ Validée |
| 10.2 | Détection / classification | ✅ Validée |
| 10.3 | Gestion des erreurs | ✅ Validée |
| 10.4 | Isolation / containment | ✅ Validée |
| 10.5 | Retry / récupération | ✅ Validée |
| 10.6 | Dégradation contrôlée | ✅ Validée |
| **10.7** | **Intégration orchestrateur** | **✅ Validée** |

The resilience layer is integrated at the orchestration boundary through `OrchestratorResilience`. Orchestration failures can be normalized through anomaly detection, error handling, bounded recovery and controlled degradation decisions while preserving the original exception semantics. The integration performs no automatic retry, sleep/backoff, shutdown, capability disabling, permission revocation or infrastructure mutation. See [`docs/phase-10-6-controlled-degradation.md`](docs/phase-10-6-controlled-degradation.md) and [`docs/phase-10-7-orchestrator-integration.md`](docs/phase-10-7-orchestrator-integration.md).

## Validation and CI

The repository validates package installation and the complete unittest suite through GitHub Actions on Python 3.10, 3.11, 3.12 and 3.13.

```bash
python -m pip install -e .
python -m unittest discover -s ./tests -p "test_*.py" -v
```

## Scope boundaries

The project deliberately keeps external runtimes, providers, transports and infrastructure behind replaceable contracts. Distributed brokers, persistent messaging, retries with concrete execution/backoff, advanced observability, concrete provider execution and other infrastructure concerns remain available for later dedicated phases.
