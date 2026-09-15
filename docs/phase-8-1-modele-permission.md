# Phase 8.1 — Modèle de permission

## Statut

**Validée.**

## Objectif

Définir le contrat déclaratif représentant une permission JARVIS, sans encore implémenter les politiques, l'évaluation, l'autonomie ou la gouvernance.

## Modèle retenu

```text
Permission
├── subject_id
├── action
└── resource
```

- `subject_id` identifie le sujet auquel l'autorisation est accordée.
- `action` identifie l'opération autorisée.
- `resource` identifie la ressource ciblée.

Une permission est immuable, comparable par valeur et validée à la construction. Les trois champs doivent être des chaînes non vides.

## Frontières

La permission décrit **ce qui est autorisé**. Elle ne définit pas encore :

- l'évaluation ou le moteur de décision ;
- les rôles et héritages ;
- les conditions contextuelles ;
- les niveaux d'autonomie ;
- les validations humaines ;
- les règles de gouvernance ;
- le comportement du système en cas de refus.

Ces responsabilités restent réservées aux étapes suivantes de la Phase 8.

## Compatibilité avec l'existant

La Phase 4 possède déjà `SecurityController` et `SecurityRule`, utilisés pour protéger l'exécution des capacités et la communication. Le nouveau modèle `Permission` constitue le contrat de domaine de Phase 8.1 ; il n'introduit pas de changement de comportement dans les contrôleurs existants à cette étape.

## Validation

Les tests vérifient :

1. stockage correct du sujet, de l'action et de la ressource ;
2. égalité et hachage par valeur ;
3. rejet des champs vides ;
4. immutabilité du modèle.
