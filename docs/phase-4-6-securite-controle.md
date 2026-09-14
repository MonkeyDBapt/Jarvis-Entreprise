# Phase 4.6 — Sécurité / contrôle

## Objectif

Introduire une frontière JARVIS explicite de contrôle d'accès avant l'exécution des capacités, sans mélanger la sécurité avec le runtime Hermes, MAF ou les modèles organisationnels.

## Architecture

```text
Sujet
  │
  ▼
SecurityController
  │  default deny
  ▼
SecurityControlledExecutor
  │
  ▼
CapabilityExecutor
  │
  ▼
Capability handler
```

## Règles retenues

- JARVIS possède la politique d'autorisation.
- Les autorisations sont explicites et révocables.
- Le comportement par défaut est **refusé**.
- Une autorisation est définie par `subject_id + action + resource`.
- Le contrôle de sécurité ne remplace pas les contrôles métier existants : l'affectation agent/capacité reste obligatoire.
- Le contrôle de sécurité est placé avant l'exécution de la capacité.
- Aucun secret, identifiant externe ou credential n'est stocké dans cette couche.
- L'authentification, les rôles complexes, l'audit persistant et les politiques distribuées sont volontairement reportés à une étape dédiée lorsqu'ils seront nécessaires.

## Éléments implémentés

- `SecurityRule` : règle d'autorisation déclarative.
- `SecurityController` : ajout, révocation, vérification et autorisation.
- `SecurityControlledExecutor` : frontière de contrôle avant `CapabilityExecutor`.
- Tests : refus par défaut, autorisation explicite, révocation et maintien du contrôle d'affectation.

## Validation

La phase est considérée comme validée lorsque la suite de tests GitHub Actions confirme que :

1. une opération non autorisée est refusée ;
2. une opération explicitement autorisée peut passer ;
3. une autorisation révoquée ne permet plus l'opération ;
4. la sécurité ne contourne pas l'affectation existante des capacités.

## Périmètre reporté

Cette étape ne crée pas encore de système d'identité complet, de gestion de secrets, de chiffrement applicatif, de RBAC/ABAC avancé ou de journal d'audit persistant. Ces mécanismes pourront être ajoutés sans casser la frontière `SecurityController`.
