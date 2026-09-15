# Phase 8.6 — Contrôle / supervision

## Objectif

Transformer les décisions de permission et d'autonomie en une décision de contrôle explicite avant exécution.

La chaîne de gouvernance de référence est :

```text
Demande
  ↓
AuthorizationEvaluator
  ↓
Autorisé ? ── non → DENIED
  │
 oui
  ↓
AutonomyPolicy / AutonomyEvaluator
  ↓
Contrôle humain requis ? ── oui → SUPERVISED / APPROVAL_REQUIRED
  │
 non
  ↓
AUTONOMOUS
```

## Contrat logiciel

`ControlEvaluator` combine deux décisions existantes sans les remplacer :

- `AuthorizationDecision` reste la source de vérité pour l'autorisation ;
- `AutonomyPolicy` reste la source de vérité pour le niveau d'autonomie ;
- `ControlDecision` matérialise le résultat de gouvernance.

Les résultats possibles sont :

| Résultat | Signification |
|---|---|
| `DENIED` | l'autorisation est refusée ; l'exécution est bloquée |
| `APPROVAL_REQUIRED` | autorisation accordée mais niveau d'autonomie absent ; validation humaine obligatoire |
| `SUPERVISED` | autorisation accordée mais supervision/validation humaine requise |
| `AUTONOMOUS` | autorisation accordée et niveau d'autonomie suffisant pour agir sans validation préalable |

## Garanties

- une permission refusée reste toujours terminale ;
- l'autonomie ne peut jamais créer une permission ;
- une autonomie absente échoue en mode fermé (`APPROVAL_REQUIRED`) ;
- aucune escalade implicite de niveau d'autonomie ;
- aucune wildcard, héritage ou contournement de permission ;
- les décisions sont déterministes et immuables ;
- le contrôle est séparé des mécanismes d'exécution.

## Validation

`tests/test_control.py` couvre :

- refus terminal malgré une autonomie élevée ;
- autonomie absente ;
- niveaux assisté et supervisé ;
- niveaux borné et délégué ;
- validation des types de contrats.

La CI GitHub doit valider cette étape avec la suite complète existante sur Python 3.10 à 3.13.
