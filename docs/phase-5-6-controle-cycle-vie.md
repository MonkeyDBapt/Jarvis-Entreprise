# Phase 5.6 — Contrôle / cycle de vie mémoire

## Statut

**Implémentée et validée fonctionnellement.**

## Objectif

Donner à JARVIS un contrôle explicite du cycle de vie d'une mémoire sans coupler ce contrôle à l'orchestrateur, au runtime ou à une technologie de stockage particulière.

## Décision

JARVIS introduit le contrat `MemoryLifecycle` et l'état `MemoryLifecycleState` dans `jarvis.interfaces`.

Les états opérationnels sont :

- `active` — mémoire utilisable par la recherche ;
- `archived` — mémoire conservée mais exclue de la recherche ;
- `expired` — mémoire arrivée à expiration, conservée jusqu'à purge.

L'implémentation `MemoryLifecycleManager` utilise uniquement le contrat `MemoryStore`.

```text
Memory
  │
  ▼
MemoryLifecycle
  ├── active
  ├── archived
  └── expired
        │
        ▼
     purge
```

## Contrôle

Le gestionnaire fournit :

- lecture de l'état ;
- activation ;
- archivage ;
- restauration ;
- expiration explicite ;
- suppression définitive ;
- purge des mémoires expirées.

Les mémoires existantes qui ne possèdent pas encore de métadonnée de cycle de vie sont considérées comme `active` afin de préserver la compatibilité avec les données créées aux étapes précédentes.

## Rétention / expiration

Une date d'expiration peut être enregistrée dans la métadonnée `expires_at` au format ISO-8601 avec fuseau horaire.

Une mémoire arrivée à expiration est exclue de la recherche. La purge définitive reste une opération distincte et explicite.

## Recherche

`SQLiteMemoryRetriever` applique maintenant le contrôle de cycle de vie : seules les mémoires `active` et non expirées sont retournées.

Cela empêche qu'une mémoire archivée ou expirée soit réinjectée accidentellement dans le contexte.

## Validation

Les tests couvrent :

- état actif par défaut ;
- archivage et restauration ;
- expiration ;
- exclusion d'une mémoire expirée de la recherche ;
- purge définitive ;
- suppression définitive ;
- comportement sûr lorsqu'une mémoire est absente.

## Hors périmètre

Ne sont pas introduits en 5.6 :

- intégration à `JarvisOrchestrator` ;
- politique métier automatique de mémorisation ;
- permissions avancées ;
- vectorisation ou embeddings ;
- scheduling autonome de purge ;
- synchronisation distribuée.

Ces éléments restent réservés aux étapes suivantes.

## Architecture après 5.6

```text
JARVIS Enterprise
       │
       └── Memory
              │
              ├── MemoryStore
              │      └── SQLiteMemoryStore
              │
              ├── MemoryRetriever
              │      └── SQLiteMemoryRetriever
              │
              ├── MemoryContextInjector
              │      └── RetrieverMemoryContextInjector
              │
              └── MemoryLifecycle
                     └── MemoryLifecycleManager
```
