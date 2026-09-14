# Phase 5.3 — Stockage mémoire

## Statut

**Validée.**

## Objectif

Fournir une persistance réelle des objets `Memory` sans coupler le domaine mémoire à une technologie de stockage.

## Décision

JARVIS utilise une frontière `MemoryStore` dans `jarvis.interfaces`.

Le backend initial est `SQLiteMemoryStore`, dans `jarvis.memory`.

```text
Memory
  │
  ▼
MemoryStore              ← contrat JARVIS
  │
  ▼
SQLiteMemoryStore        ← implémentation initiale
  │
  ▼
SQLite
```

SQLite est retenu comme stockage initial car il est intégré à Python, persistant, transactionnel, sans serveur externe et adapté au socle actuel. Le contrat permet de remplacer le backend ultérieurement sans modifier le modèle `Memory` ni les couches qui dépendent de l'interface.

## Données persistées

Le stockage conserve :

- `id` — identifiant stable et clé primaire ;
- `content` — contenu de la mémoire ;
- `memory_type` — catégorie `short_term`, `long_term` ou `contextual` ;
- `scope` — portée logique ;
- `metadata` — métadonnées sérialisées en JSON.

Les données sont persistées dans `.data/memory.sqlite3` par défaut. Le répertoire `.data/` est ignoré par Git afin que les données locales ne soient jamais versionnées par erreur.

## Opérations validées

`MemoryStore` expose volontairement uniquement le périmètre nécessaire au stockage :

- `save()` — création ou remplacement par identifiant ;
- `get()` — récupération directe par identifiant ;
- `delete()` — suppression ;
- `count()` — comptage ;
- `close()` — libération de la ressource.

La recherche sémantique, le classement, l'expiration, les embeddings, l'injection de contexte, le cycle de vie et l'intégration avec l'orchestrateur restent hors périmètre de 5.3.

## Validation

Les tests vérifient :

- conformité de `SQLiteMemoryStore` au contrat `MemoryStore` ;
- aller-retour mémoire → SQLite → mémoire ;
- conservation des métadonnées ;
- remplacement d'une mémoire existante ;
- suppression et gestion d'un identifiant absent ;
- comptage des éléments persistés.

## Architecture consolidée après 5.3

```text
JARVIS Enterprise
       │
       ├── Organization → Pole → Team → Agent
       ├── CapabilityRegistry → SecurityControlledExecutor
       │
       └── Memory
              │
              ▼
         MemoryStore
              │
              ▼
      SQLiteMemoryStore
              │
              ▼
           SQLite
```

## Hors périmètre

Aucune technologie vectorielle ou service externe n'est imposé à ce stade. Une évolution vers plusieurs backends pourra être réalisée derrière `MemoryStore` lorsque les besoins de recherche/récupération seront définis en 5.4.
