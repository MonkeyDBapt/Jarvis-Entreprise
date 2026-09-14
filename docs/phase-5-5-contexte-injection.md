# Phase 5.5 — Contexte / injection mémoire

## Statut

**Implémentée et validée fonctionnellement.**

## Objectif

Transformer les mémoires récupérées en un contexte borné et déterministe pouvant être transmis ultérieurement à un agent ou à un runtime, sans intégrer cette étape à l'orchestrateur.

## Décision

JARVIS introduit une frontière `MemoryContextInjector` dans `jarvis.interfaces`.

L'implémentation initiale `RetrieverMemoryContextInjector`, dans `jarvis.memory`, consomme uniquement le contrat `MemoryRetriever`.

```text
Requête
  │
  ▼
MemoryRetriever
  │
  ▼
MemorySearchResult[]
  │
  ▼
MemoryContextInjector
  │
  ▼
MemoryContext
  │
  └── texte borné prêt à être injecté dans un contexte d'agent
```

## Règles d'injection

- la requête doit être non vide ;
- la limite de mémoires doit être strictement positive ;
- la taille maximale du contexte est configurable ;
- les mémoires sont conservées dans leur ordre de pertinence fourni par le retriever ;
- une mémoire qui dépasse la taille restante n'est pas injectée ;
- aucun appel direct à MAF, Hermes ou à l'orchestrateur n'est effectué ;
- aucune nouvelle stratégie de stockage ou de recherche n'est introduite.

Le format initial est volontairement simple et déterministe :

```text
[type | scope=...] contenu
```

## Séparation des responsabilités

5.5 ne décide pas :

- quelles mémoires doivent être créées ;
- comment elles sont persistées ;
- comment elles sont recherchées ;
- comment elles expirent ;
- comment un agent reçoit effectivement le contexte dans le workflow ;
- comment les permissions gouvernent la mémoire.

Ces responsabilités restent réservées aux étapes suivantes.

## Validation

Les tests couvrent :

- construction d'un contexte depuis le retriever ;
- conservation des mémoires effectivement injectées ;
- respect de la limite de caractères ;
- rejet d'une requête vide ;
- rejet d'une taille maximale invalide.

## Hors périmètre

Ne sont pas introduits en 5.5 :

- intégration à `JarvisOrchestrator` ;
- injection automatique dans MAF ou Hermes ;
- mémoire sémantique/vectorielle ;
- embeddings ;
- reranking ;
- expiration et cycle de vie ;
- contrôle d'accès avancé.

## Architecture après 5.5

```text
JARVIS Enterprise
       │
       ├── Organization → Pole → Team → Agent
       ├── CapabilityRegistry → SecurityControlledExecutor
       │
       └── Memory
              │
              ├── MemoryStore
              │      └── SQLiteMemoryStore
              │
              ├── MemoryRetriever
              │      └── SQLiteMemoryRetriever
              │
              └── MemoryContextInjector
                     └── RetrieverMemoryContextInjector
```
