# Phase 8.2 — Registres de permission

## Statut

**Validée.**

## Objectif

Fournir un registre central des permissions déclaratives de JARVIS Enterprise, sans encore implémenter l'évaluation des autorisations, les politiques, l'autonomie ou la gouvernance.

## Modèle retenu

`PermissionRegistry` indexe les objets `Permission` par leur valeur immuable :

```text
PermissionRegistry
├── register(permission)
├── get(permission)
├── unregister(permission)
├── contains(permission)
├── list_permissions()
└── len(registry)
```

L'identité d'une permission est le triplet :

```text
(subject_id, action, resource)
```

Deux permissions portant exactement le même triplet sont donc considérées comme identiques et une seconde inscription est rejetée.

## Frontières

Le registre conserve et retrouve les permissions. Il ne décide pas si une action est autorisée et ne définit pas encore :

- les politiques ou règles d'évaluation ;
- les rôles et héritages ;
- les conditions contextuelles ;
- les niveaux d'autonomie ;
- les validations humaines ;
- la gouvernance ;
- le comportement en cas de refus.

Ces responsabilités restent réservées aux étapes suivantes de la Phase 8.

## Compatibilité avec l'existant

Le registre réutilise le contrat `Permission` défini en 8.1 et reste indépendant des `SecurityController` / `SecurityRule` existants. Il n'introduit pas de changement de comportement dans les contrôles déjà validés en Phase 4 et Phase 7.

## Validation

Les tests vérifient :

1. enregistrement et récupération d'une permission ;
2. présence et taille du registre ;
3. rejet d'une permission déjà enregistrée ;
4. erreur sur une permission inconnue ;
5. conservation de l'ordre d'enregistrement ;
6. suppression correcte d'une permission.
