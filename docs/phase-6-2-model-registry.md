# Phase 6.2 — Registre des modèles

## Statut

**Validée.**

## Objectif

Fournir à JARVIS un registre central permettant d'enregistrer, retrouver et gérer les modèles déclaratifs définis par la Phase 6.1.

Le registre reste indépendant des fournisseurs, SDK, credentials, runtimes, stratégies de routage et workflows.

## Contrat

`ModelRegistry` :

- enregistre un `Model` par identifiant stable `id` ;
- refuse les identifiants dupliqués ;
- permet la récupération par identifiant ;
- permet de vérifier l'existence d'un modèle ;
- permet de désenregistrer un modèle ;
- expose une vue immuable et ordonnée des modèles enregistrés ;
- ne contient aucune logique d'exécution ou de sélection intelligente.

## Architecture

```text
Phase 6.1
Model / ModelType / ModelCapability
            │
            ▼
      ModelRegistry
            │
            ├── register
            ├── get
            ├── contains
            ├── unregister
            └── list
```

Le registre constitue uniquement la source de référence des modèles disponibles. Le routage, la sélection selon une tâche, les providers et l'exécution sont volontairement reportés aux étapes suivantes.

## Validation

Les tests couvrent :

- enregistrement et récupération ;
- rejet des doublons ;
- rejet d'un modèle inconnu ;
- ordre déterministe d'enregistrement ;
- désenregistrement ;
- absence de mutation via le résultat de `list()`.

La suite de tests GitHub doit rester le mécanisme de validation de référence.
