# Phase 8.6 — Contrôle / supervision

## Statut

**Validée.**

## Objectif

Ajouter une dernière frontière de contrôle après l'autorisation et l'évaluation du niveau d'autonomie. Cette frontière doit pouvoir limiter, suspendre ou soumettre à validation humaine une action déjà autorisée.

## Chaîne de décision

```text
Demande d'action
      ↓
AuthorizationEvaluator
      ↓
ControlEvaluator
      ↓
SupervisionEvaluator
      ↓
ALLOW / APPROVAL_REQUIRED / RESTRICTED / REVOKED / EXPIRED / DENIED
      ↓
Exécution uniquement si le contrôle final l'autorise
```

## Contrôles implémentés

- **Refus** : une autorisation refusée reste terminale.
- **Validation humaine** : une politique peut imposer une approbation ; les niveaux d'autonomie nécessitant un contrôle humain restent soumis à cette barrière.
- **Révocation** : une politique révoquée bloque immédiatement l'action.
- **Restrictions d'action** : une politique peut limiter les actions autorisées.
- **Restrictions de ressource** : une politique peut limiter les ressources accessibles.
- **Expiration** : une autorisation de supervision peut expirer à une date déterminée.
- **Fail closed** : une politique absente ne transforme pas une autorisation contrôlée en privilège implicite ; le niveau d'autonomie existant reste appliqué.

## Séparation des responsabilités

- `AuthorizationEvaluator` décide si l'action est autorisée.
- `ControlEvaluator` combine autorisation et autonomie.
- `SupervisionEvaluator` applique les garde-fous de supervision.
- L'exécution reste dans la couche de capacités/runtime déjà construite.

Cette étape ne modifie pas le contrat des phases précédentes et ne crée pas encore l'intégration complète de ces décisions dans le flux de `JarvisOrchestrator`, qui relève de **8.7 — Intégration orchestrateur**.

## Validation

Tests dédiés dans `tests/test_supervision.py` couvrant :

- refus terminal ;
- révocation ;
- restrictions d'action ;
- restrictions de ressource ;
- expiration ;
- approbation humaine ;
- respect du niveau d'autonomie ;
- autorisation d'une action dans un périmètre valide ;
- isolation par sujet ;
- validation des types.
