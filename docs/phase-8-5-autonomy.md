# Phase 8.5 — Niveaux d'autonomie

## Objectif

Définir le niveau d'autonomie d'un sujet sans confondre autonomie et permission.

- **Capacité** : ce que l'agent peut techniquement faire.
- **Permission** : ce que l'agent est autorisé à faire.
- **Autonomie** : le niveau de décision/exécution qui peut être exercé sans validation humaine.
- **Gouvernance** : les règles qui imposent supervision, approbation ou interdiction.

Une autonomie élevée ne contourne jamais une permission refusée.

## Niveaux de référence

| Niveau | Nom | Règle |
|---|---|---|
| 0 | `NONE` | Aucune décision ou exécution autonome. |
| 1 | `ASSISTED` | Préparation/proposition ; validation humaine requise. |
| 2 | `SUPERVISED` | Exécution dans un cadre défini ; supervision/validation requise. |
| 3 | `BOUNDED` | Décision et exécution autonomes dans les limites autorisées. |
| 4 | `DELEGATED` | Pilotage autonome d'une mission déléguée dans le périmètre autorisé. |

Les niveaux sont ordonnés et extensibles. Le niveau ne donne aucune permission par lui-même.

## Contrat logiciel

`AutonomyPolicy` associe un sujet à un `AutonomyLevel`.

`AutonomyEvaluator` détermine uniquement si une validation humaine est requise. Il ne remplace pas `AuthorizationEvaluator`.

La chaîne de décision de référence devient :

```text
Demande
  ↓
Permission / AuthorizationEvaluator
  ↓
Autorisé ? ── non → REFUS
  │
 oui
  ↓
AutonomyPolicy / AutonomyEvaluator
  ↓
Validation requise ? ── oui → APPROBATION / SUPERVISION
  │
 non
  ↓
Exécution autonome dans le périmètre autorisé
```

## Garanties

- séparation permission/autonomie ;
- comportement déterministe ;
- niveaux 0 à 2 soumis à validation/supervision ;
- niveaux 3 et 4 autonomes uniquement après autorisation ;
- aucune escalade implicite ;
- aucune wildcard ou héritage de permission introduit par cette étape ;
- aucune autonomie par défaut non explicitement attribuée.

## Validation

Tests dédiés dans `tests/test_autonomy.py` couvrant l'ordre des niveaux, les seuils de validation et les contrôles de contrat.
