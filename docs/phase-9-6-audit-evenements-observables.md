# Phase 9.6 — Audit / événements observables

## Statut

**Validée / consolidée.**

## Objectif

Fournir un contrat indépendant des fournisseurs pour représenter les événements qui doivent être observables et auditables dans JARVIS Enterprise, en complément des logs, métriques et traces.

## Contrat

`AuditEvent` représente un événement immuable avec :

- identité stable de l'événement ;
- horodatage UTC ;
- type d'événement ;
- action et composant à l'origine de l'observation ;
- identifiants optionnels d'acteur, agent et tâche ;
- corrélation avec une opération et une trace ;
- résultat et motif optionnels ;
- métadonnées structurées.

`AuditEventType` couvre les catégories génériques nécessaires au socle : demande, autorisation, refus, démarrage, achèvement, échec, blocage, configuration et cycle de vie.

`AuditRecorder` fournit un stockage en mémoire thread-safe et des filtres par type, corrélation et trace. Il ne choisit volontairement aucun backend persistant, transport ou fournisseur externe.

## Séparation des responsabilités

```text
Logs       → journal technique détaillé
Métriques  → mesures quantitatives
Traces     → causalité et chronologie d'une opération
Audit      → événements observables et décisions/actions auditables
Santé      → état courant du système
```

Ces contrats restent indépendants et composables. L'étape 9.6 n'impose donc ni base de données, ni broker, ni système SIEM, ni fournisseur d'observabilité.

## Validation

Les tests couvrent :

- création et identité des événements ;
- horodatage UTC ;
- validation des champs obligatoires ;
- enregistrement et ordre d'observation ;
- filtrage par type, corrélation et trace ;
- représentation structurée sérialisable.

Les fonctionnalités d'intégration automatique dans tous les composants, de persistance et d'expédition externe restent hors périmètre de 9.6 et pourront être traitées dans les étapes/phases d'intégration et d'infrastructure appropriées.
