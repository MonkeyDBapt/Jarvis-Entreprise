# Phase 6.3 — Configuration

## Statut

**Validée.**

## Objectif

Définir une frontière de configuration provider-neutral entre la définition déclarative d'un modèle et son provider/runtime.

## Contrat

`ModelConfiguration` regroupe :

- endpoint optionnel ;
- paramètres génériques ;
- limite de contexte ;
- température ;
- limite de sortie ;
- limites opérationnelles ;
- références de secrets ;
- configuration spécifique au provider.

La configuration est immuable après création et ses mappings sont protégés contre les mutations externes.

Les valeurs secrètes ne sont jamais stockées dans `ModelConfiguration`. Seules des références de secrets, destinées à être résolues par l'environnement d'exécution, peuvent y figurer.

`Model` utilise désormais `ModelConfiguration` comme configuration typée tout en conservant une compatibilité de construction avec les mappings existants.

## Architecture

```text
Model
  │
  ▼
ModelConfiguration
  │
  ├── endpoint
  ├── parameters
  ├── context_limit
  ├── temperature
  ├── output_limit
  ├── limits
  ├── secret_refs
  └── provider_configuration
  │
  ▼
Provider / Runtime
```

La sélection/routage, les stratégies d'utilisation, le contrôle avancé et l'exécution provider restent volontairement hors du périmètre de 6.3.

## Validation

Les tests couvrent :

- configuration provider-neutral ;
- limites de contexte et de sortie ;
- validation de la température ;
- immutabilité ;
- références de secrets ;
- intégration typée avec `Model`.

Aucun secret ou credential réel n'est ajouté au dépôt.
