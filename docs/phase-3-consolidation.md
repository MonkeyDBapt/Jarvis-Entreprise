# Phase 3 — Consolidation

## Statut

**Phase 3 — Construction du système d’agents : consolidée.**

Les étapes 3.1 à 3.7 sont validées avant clôture de la consolidation.

## Périmètre consolidé

- **3.1 — Modèle d’organisation :** `Organization → Pole → Team → Agent`.
- **3.2 — Modèle Agent :** définition déclarative avec identité, rôle, description, capacités et configuration.
- **3.3 — Registre des agents :** index JARVIS des définitions d’agents par identifiant stable.
- **3.4 — Organisation pôles / équipes :** gestion de la structure organisationnelle via `OrganizationManager`.
- **3.5 — Sélection / affectation :** sélection déterministe et affectation d’agents via `AgentAssignmentManager`.
- **3.6 — Cycle de vie :** états `REGISTERED`, `ACTIVE`, `INACTIVE`, `RETIRED` via `AgentLifecycleManager`.
- **3.7 — Intégration orchestrateur :** résolution d’un agent actif puis exécution via MAF → `AgentRuntime` → `HermesAdapter` → Hermes.

## Architecture de référence

```text
JARVIS Enterprise
       │
       ▼
Organisation
       │
       ├── Pole
       │    └── Team
       │         └── Agent
       │
       ▼
AgentRegistry
       │
       ▼
Sélection / Affectation
       │
       ▼
Cycle de vie
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

## Frontières de responsabilité

JARVIS Enterprise conserve la propriété du modèle organisationnel, du registre, de la sélection, de l’affectation, du cycle de vie et de la résolution orchestrée des agents.

MAF reste le moteur de workflow. `AgentRuntime` reste le contrat d’exécution stable. Hermes reste le runtime concret actuel.

La Phase 3 n’introduit volontairement pas encore les permissions, la gouvernance avancée, le messaging/event bus, la mémoire spécialisée ou les capacités métier spécialisées. Ces sujets restent des extensions ultérieures et ne doivent pas être réintroduits rétroactivement dans les fondations validées.

## Validation

La validation CI de l’intégration orchestrateur (run #45) a terminé avec succès sur Python 3.10, 3.11, 3.12 et 3.13. Les tests de Phase 3 couvrent les modèles, le registre, l’organisation, la sélection/affectation, le cycle de vie et le routage orchestré.

**Décision de consolidation :** la Phase 3 est considérée comme techniquement cohérente et prête à servir de base aux phases suivantes.

**3.8 — Validation / consolidation : VALIDÉE.**
