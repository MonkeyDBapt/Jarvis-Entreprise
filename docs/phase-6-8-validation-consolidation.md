# Phase 6 — Intelligence des modèles

## 6.8 — Validation / consolidation

### Objectif

Clôturer la Phase 6 après intégration de la gestion de l'intelligence modèle dans l'orchestration JARVIS, en vérifiant que les contrats 6.2 à 6.7 restent cohérents, que les contrôles sont appliqués avant exécution et qu'aucun chemin parallèle ou contournement provider-specific n'a été introduit.

### Périmètre consolidé

| Étape | Statut |
|---|---|
| 6.2 — Registre des modèles | ✅ Validée |
| 6.3 — Configuration | ✅ Validée |
| 6.4 — Sélection / routage | ✅ Validée |
| 6.5 — Stratégies d'utilisation | ✅ Validée |
| 6.6 — Contrôle / contraintes | ✅ Validée |
| 6.7 — Intégration / orchestration | ✅ Validée |
| 6.8 — Validation / consolidation | ✅ Validée |

### Architecture de référence

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

### Frontières consolidées

- `ModelRegistry` reste responsable des modèles déclarés et de leur configuration.
- `ModelRouter` reste responsable de la sélection à partir des contrats de demande et des stratégies.
- `ModelUsageStrategy` exprime une intention déclarative et ne contacte aucun provider.
- `ModelControlConstraints` impose les règles dures avant la sélection/exécution.
- `JarvisOrchestrator` reste la façade JARVIS de composition et d'orchestration.
- MAF reste le moteur de workflow pour les requêtes d'agents.
- `AgentRuntime` reste le contrat d'exécution stable.
- Hermes reste le runtime opérationnel actuel.
- Le routeur transmet uniquement l'identifiant du modèle sélectionné au runtime ; les credentials, appels provider, quotas réels, prix réels, latence réelle et disponibilité restent hors de cette couche.
- Le chemin historique utilisant `model` reste compatible lorsqu'aucun routage d'intelligence n'est demandé.
- Aucun chemin direct `ModelRouter → provider` ni `ModelRegistry → provider` n'est introduit.

### Validation technique

Les tests de Phase 6 couvrent notamment :

- stratégie par défaut et stratégie de raisonnement ;
- conservation des contraintes explicites ;
- sélection via registre + routeur ;
- filtrage et refus déterministe par contraintes ;
- transmission du modèle sélectionné au runtime ;
- maintien du chemin historique sans routage d'intelligence ;
- refus d'un agent inactif.

La CI GitHub Actions exécute l'ensemble des tests sur Python 3.10, 3.11, 3.12 et 3.13.

Aucun secret ou credential réel n'est ajouté au dépôt.

### Décision de clôture

La Phase 6 est considérée comme **consolidée et clôturée** à l'issue de cette étape. Les mécanismes provider-specific, les credentials, l'évaluation dynamique de disponibilité/coût/latence, les fallbacks avancés et l'exécution concrète des providers restent hors périmètre de cette phase et devront être traités dans les phases dédiées.

**6.8 — Validation / consolidation : VALIDÉE.**
