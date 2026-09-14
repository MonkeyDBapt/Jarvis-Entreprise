# Phase 5.1 — Modèle de mémoire

## Statut

**Validée.**

## Objectif

Définir ce qu'est une mémoire JARVIS au niveau du domaine, avant de traiter la persistance, le stockage, la recherche ou l'optimisation.

Le modèle doit rester déclaratif et indépendant de toute technologie de stockage.

## Modèle retenu

```text
Memory
├── id
├── content
├── memory_type
├── scope
└── metadata
```

### Propriétés

| Propriété | Rôle |
|---|---|
| `id` | Identifiant stable de la mémoire |
| `content` | Information mémorisée |
| `memory_type` | Catégorie fonctionnelle de mémoire |
| `scope` | Périmètre logique auquel la mémoire appartient |
| `metadata` | Métadonnées extensibles sans imposer de schéma prématuré |

## Types de mémoire

Le modèle distingue trois catégories fonctionnelles initiales :

- `short_term` — mémoire à court terme, liée aux informations temporaires d'une activité ;
- `long_term` — mémoire à long terme, destinée aux informations persistantes et pertinentes ;
- `contextual` — mémoire utilisée pour fournir du contexte à une interaction, une tâche ou un processus.

Ces catégories décrivent la fonction de la mémoire. Elles ne définissent pas encore leur technologie de stockage ni leur durée exacte de conservation.

## Frontières de 5.1

Le modèle ne définit volontairement pas :

- base de données ou moteur de stockage ;
- embeddings ou recherche vectorielle ;
- algorithme de récupération/ranking ;
- expiration ou oubli automatique ;
- consolidation ;
- politique détaillée de mémorisation ;
- synchronisation entre agents ;
- API de persistance.

Ces sujets appartiennent aux étapes suivantes de la Phase 5.

## Intégration architecturale

La mémoire devient un domaine JARVIS supplémentaire, sans modifier les frontières déjà validées des phases 2 à 4.

```text
JARVIS Enterprise
       │
       ├── Organization / Agents
       ├── Capabilities / Security
       ├── Orchestration
       │
       └── Memory
             │
             └── Memory model
```

Le modèle reste indépendant du runtime Hermes, de MAF et des capacités. Il pourra donc être relié ultérieurement aux agents et à l'orchestrateur via des interfaces dédiées.

## Validation

Les tests de 5.1 vérifient :

1. les propriétés déclaratives du modèle ;
2. les trois types de mémoire ;
3. le rejet d'un identifiant ou contenu vide ;
4. l'absence de responsabilité de stockage/récupération dans le modèle.

## Décision de clôture

**5.1 — Modèle de mémoire est validée et clôturée.**

Aucune technologie de mémoire n'est imposée à ce stade. La prochaine étape peut traiter le registre et la gestion des mémoires sans remettre en cause ce modèle.
