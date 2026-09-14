# Phase 6.5 — Stratégies d'utilisation

## Statut

**Validée.**

## Objectif

Définir une frontière provider-neutral permettant à JARVIS d'exprimer **comment un modèle doit être utilisé** avant de sélectionner ou d'exécuter un modèle.

La stratégie est une intention déclarative. Elle ne contacte aucun provider, ne résout aucun secret et n'exécute aucun modèle.

## Contrat

`ModelUsageStrategy` définit les intentions générales :

- `balanced` — usage général équilibré ;
- `fast` — priorité à un usage rapide ;
- `quality` — priorité à la qualité ;
- `economical` — priorité à l'économie de ressources ;
- `reasoning` — usage orienté raisonnement.

`ModelUsageRequest` permet de combiner cette intention avec des contraintes explicites :

- identifiant de modèle ;
- provider préféré ;
- type de modèle ;
- capacités requises.

La stratégie est ensuite traduite vers le contrat existant `ModelSelectionRequest`. Ainsi, 6.5 ajoute une couche d'intention sans dupliquer le mécanisme de sélection de 6.4.

## Règles

1. Une contrainte explicitement fournie reste prioritaire et est conservée.
2. Une stratégie de raisonnement impose au minimum le type `reasoning` et la capacité `reasoning` lorsqu'ils ne sont pas déjà précisés.
3. Les stratégies générales utilisent par défaut un modèle `llm` avec la capacité `text_generation`.
4. Aucune métrique provider-specific (prix, latence réelle, disponibilité, quota) n'est inventée ou évaluée à cette étape.
5. L'exécution, les fallbacks avancés, l'optimisation dynamique et l'évaluation des performances restent hors périmètre.

## Architecture

```text
ModelUsageRequest
       │
       ▼
ModelUsageStrategy
       │
       ▼
ModelSelectionRequest
       │
       ▼
ModelRouter
       │
       ▼
ModelRegistry
```

## Validation

Les tests couvrent :

- stratégie par défaut ;
- stratégie de raisonnement ;
- conservation des contraintes explicites ;
- compatibilité avec le contrat `ModelSelectionRequest`.

Aucun credential réel n'est ajouté au dépôt.
