# Phase 5.7 — Intégration orchestrateur

## Statut

**Phase 5.7 — Validée.**

## Objectif

Relier la mémoire contextuelle déjà construite en Phase 5 à la frontière d'orchestration JARVIS, sans casser les frontières validées des phases 1 à 4.

## Architecture

```text
Requête utilisateur
       │
       ▼
JarvisOrchestrator
       │
       ├── résolution Agent + cycle de vie
       │
       ├── MemoryContextInjector
       │       │
       │       ├── MemoryRetriever
       │       └── MemoryLifecycle
       │
       ▼
Contexte mémoire borné
       │
       ▼
Microsoft Agent Framework
       │
       ▼
HermesExecutor
       │
       ▼
AgentRuntime
       │
       ▼
Hermes
```

## Décision

`JarvisOrchestrator` accepte désormais une implémentation de `MemoryContextInjector` par injection de dépendance.

Lorsqu'elle est configurée :

1. l'agent actif est résolu avec les mécanismes de Phase 3 ;
2. le contexte mémoire est construit à partir du message utilisateur ;
3. la quantité de mémoire demandée est bornée par `OrchestrationRequest.memory_limit` ;
4. le contexte produit est transmis au workflow MAF ;
5. `HermesExecutor` ajoute ce contexte au message envoyé au runtime ;
6. l'exécution continue par `AgentRuntime` puis `Hermes`.

Lorsqu'aucun injecteur n'est configuré, le message original est transmis inchangé. L'intégration reste donc compatible avec les usages existants et les tests antérieurs.

## Frontières préservées

- L'orchestrateur ne dépend pas d'une implémentation de stockage mémoire.
- L'orchestrateur dépend du contrat `MemoryContextInjector`, pas de SQLite.
- La recherche reste derrière `MemoryRetriever`.
- Le cycle de vie reste appliqué par la couche mémoire existante.
- MAF reste le moteur de workflow.
- `AgentRuntime` reste la frontière d'exécution.
- Hermes reste un runtime remplaçable derrière son adaptateur.

## Validation

Le test d'intégration `tests/test_memory_orchestrator.py` vérifie :

- la construction du contexte avant l'exécution MAF/runtime ;
- la présence du contexte mémoire dans le message transmis au runtime ;
- le respect de `memory_limit` ;
- la conservation du chemin d'exécution original sans mémoire configurée ;
- le rejet d'une limite mémoire invalide.

La CI GitHub exécute la suite sur Python 3.10, 3.11, 3.12 et 3.13.

## Périmètre volontairement exclu

Cette étape ne crée pas de recherche vectorielle, d'embeddings, de reranking, de mémoire autonome, de synthèse automatique ou de nouvelle politique de persistance. Ces évolutions restent séparées et pourront être ajoutées derrière les contrats existants.
