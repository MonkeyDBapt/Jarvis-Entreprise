# Phase 5.4 — Recherche / récupération mémoire

## Statut

**Validée.**

## Objectif

Permettre à JARVIS de retrouver les mémoires pertinentes à partir d'une requête textuelle, sans coupler le domaine mémoire à une technologie de recherche particulière.

## Décision

JARVIS introduit une frontière `MemoryRetriever` dans `jarvis.interfaces`.

Le backend initial est `SQLiteMemoryRetriever`, dans `jarvis.memory`.

```text
Memory
  │
  ▼
MemoryRetriever          ← contrat JARVIS
  │
  ▼
SQLiteMemoryRetriever    ← implémentation initiale
  │
  ▼
SQLiteMemoryStore / SQLite
```

La première implémentation utilise une recherche lexicale locale déterministe. Elle ne nécessite ni service externe, ni modèle d'embeddings, ni base vectorielle.

## Recherche

`MemoryRetriever.search()` accepte :

- `query` — requête textuelle non vide ;
- `limit` — nombre maximal de résultats ;
- `memory_type` — filtre optionnel sur le type fonctionnel ;
- `scope` — filtre optionnel sur la portée.

Les résultats sont renvoyés sous forme de `MemorySearchResult`, contenant la mémoire et un score de pertinence.

## Classement

Le classement initial repose sur :

- correspondance des termes dans le contenu ;
- nombre de termes distincts retrouvés ;
- bonus de correspondance de la phrase recherchée ;
- identifiant comme critère de départage pour garantir un ordre déterministe.

Cette stratégie est volontairement simple et remplaçable. Elle constitue un mécanisme de récupération fonctionnel, pas le moteur sémantique final de JARVIS.

## Validation

Les tests couvrent :

- conformité de `SQLiteMemoryRetriever` au contrat `MemoryRetriever` ;
- récupération et classement ;
- limitation du nombre de résultats ;
- filtrage par type et portée ;
- recherche insensible à la casse ;
- absence de résultat lorsqu'aucune mémoire ne correspond ;
- rejet d'une requête vide ;
- rejet d'une limite invalide.

## Hors périmètre

Ne sont pas introduits en 5.4 :

- embeddings ;
- recherche vectorielle ;
- reranking par modèle ;
- recherche hybride avancée ;
- injection de contexte ;
- expiration / cycle de vie ;
- intégration avec l'orchestrateur.

Ces éléments restent réservés aux étapes suivantes.

## Architecture après 5.4

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
              └── MemoryRetriever
                     └── SQLiteMemoryRetriever
```
