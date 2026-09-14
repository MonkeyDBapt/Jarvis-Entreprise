# Phase 5.2 — Types de mémoire

## Statut

**Validée.**

## Objectif

Définir les formes fonctionnelles de mémoire de JARVIS sans imposer de technologie de stockage, de persistance, de recherche ou de cycle de vie.

## Décision retenue

JARVIS distingue cinq formes de mémoire :

| Type | Fonction | Exemple conceptuel |
|---|---|---|
| `working` | Informations nécessaires à l'activité immédiate | contexte actif d'une tâche |
| `episodic` | Événements ou expériences mémorisés | résultat d'une interaction passée |
| `semantic` | Connaissances et faits | connaissance générale ou domaine |
| `user` | Informations persistantes utiles relatives à un utilisateur | préférence explicitement conservée |
| `system` | Informations relatives au fonctionnement et à l'état de JARVIS | état ou historique système pertinent |

## Distinction avec 5.1

La Phase 5.1 avait défini trois catégories de haut niveau :

- `short_term`
- `long_term`
- `contextual`

Ces catégories restent inchangées et continuent de décrire le caractère temporel ou contextuel d'une mémoire.

La Phase 5.2 ajoute une seconde dimension, `MemoryKind`, qui décrit **la forme et la fonction de l'information mémorisée**.

```text
Memory
├── MemoryType   → short_term / long_term / contextual
└── MemoryKind   → working / episodic / semantic / user / system
```

Cette séparation évite de mélanger durée/contexte et nature de l'information.

## Règles de périmètre

5.2 ne définit volontairement pas :

- stockage physique ;
- base de données ;
- vector store ;
- embeddings ;
- recherche ou ranking ;
- expiration ;
- oubli ;
- politique détaillée de mémorisation ;
- synchronisation entre agents ;
- injection dans les prompts.

Ces responsabilités restent réservées aux étapes suivantes de la Phase 5.

## Intégration

Le type est matérialisé par l'énumération `MemoryKind` dans `src/jarvis/core/memory_types.py` et exposé par `jarvis.core`.

Le modèle `Memory` de 5.1 n'est pas modifié fonctionnellement : aucune dépendance au stockage ou au runtime Hermes/MAF n'est introduite.

## Validation

Les tests vérifient :

1. la présence explicite des cinq types ;
2. leurs identifiants stables ;
3. l'unicité des valeurs ;
4. la séparation entre la taxonomie 5.2 et les catégories de haut niveau de 5.1.

## Décision de clôture

**5.2 — Types de mémoire est validée et clôturée.**

La prochaine étape est **5.3 — Stockage**, où la couche physique de persistance pourra être étudiée sans remettre en cause cette classification.
