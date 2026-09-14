# Phase 6.4 — Sélection / routage

## Statut

**Validée.**

## Objectif

Définir une frontière provider-neutral permettant à JARVIS de sélectionner un modèle enregistré à partir de contraintes déclaratives, sans exécuter le modèle ni dépendre d'un SDK provider.

## Contrat

`ModelSelectionRequest` peut exprimer :

- un identifiant de modèle explicite ;
- un type de modèle ;
- des capacités requises ;
- un provider préféré.

`ModelSelectionResult` retourne le modèle sélectionné et la raison de sélection.

`ModelRouter` applique une sélection déterministe :

1. identifiant explicite lorsqu'il est fourni ;
2. capacités requises ;
3. type de modèle ;
4. provider ;
5. ordre d'enregistrement comme départage stable.

Une contrainte non satisfaite ou l'absence de modèle compatible produit une erreur explicite. Aucun provider, secret ou runtime n'est appelé par le routeur.

## Architecture

```text
Selection Request
       │
       ▼
   ModelRouter
       │
       ▼
  ModelRegistry
       │
       ▼
     Model
       │
       ▼
Provider / Runtime
```

La résolution des secrets, les adaptateurs provider, l'exécution, le fallback avancé et les stratégies d'intelligence restent hors du périmètre de 6.4.

## Validation

Les tests couvrent :

- sélection explicite ;
- sélection par contraintes ;
- contrainte provider ;
- départage déterministe par ordre d'enregistrement ;
- absence de correspondance ;
- incompatibilité entre modèle explicite et contraintes.

Aucun credential réel n'est ajouté au dépôt.
