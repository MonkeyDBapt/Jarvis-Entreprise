# Phase 6.7 — Intégration / orchestration

## Statut

**Validée.**

## Objectif

Connecter la couche d'intelligence de Phase 6 au point d'entrée d'orchestration JARVIS sans déplacer l'exécution provider dans cette couche.

## Intégration

`JarvisOrchestrator` peut maintenant recevoir un `ModelRegistry` et utiliser le `ModelRouter` pour résoudre le modèle à employer avant le workflow MAF.

Le flux est :

```text
OrchestrationRequest
       │
       ├── Agent resolution
       │
       ├── ModelUsageRequest
       │       │
       │       ▼
       │   ModelRouter
       │       │
       │       ▼
       │   ModelControlConstraints
       │       │
       │       ▼
       │   ModelRegistry
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
HermesAdapter / runtime concret
```

Le routeur reste provider-neutral : il sélectionne un modèle déclaré et transmet son identifiant fournisseur au runtime. Les credentials, appels provider, quotas réels, prix, latence et disponibilité restent hors de cette étape.

## Compatibilité

- L'ancien champ `model` reste disponible pour les appels existants.
- Une `ModelUsageRequest` permet désormais de sélectionner le modèle via les contrats de Phase 6.
- Les `ModelControlConstraints` sont appliquées avant l'exécution.
- Sans registre/routage d'intelligence explicite, le chemin existant reste inchangé.

## Validation

Les tests couvrent :

- résolution d'un modèle via stratégie + registre + routeur ;
- transmission de l'identifiant fournisseur sélectionné au runtime ;
- application des contraintes avant exécution ;
- refus déterministe d'une sélection incompatible ;
- conservation du chemin historique sans routage d'intelligence.

Aucun secret ou credential réel n'est ajouté au dépôt.
