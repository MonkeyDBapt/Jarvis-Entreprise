# Phase 10.7 — Intégration orchestrateur

## Objectif

Connecter les contrats de résilience des étapes 10.1 à 10.6 à la frontière d'orchestration sans introduire d'effets de bord implicites.

## Intégration

`OrchestratorResilience` reçoit les échecs produits par un `JarvisOrchestrator` et exécute la chaîne décisionnelle :

```text
Orchestrator
    ↓ échec
AnomalyDetector
    ↓
ErrorManager
    ↓
RecoveryManager
    ↓
DegradationManager
    ↓
OrchestrationResilienceReport
```

Le contrôleur reste séparé du runtime. Il ne réalise ni retry effectif, ni attente/backoff, ni arrêt, ni désactivation de capacité, ni révocation de permission, ni mutation d'infrastructure.

## Contrat d'intégration

- `OrchestratorResilience.run()` conserve le comportement d'échec existant en relançant l'exception originale.
- `last_report` expose la classification et les décisions de résilience produites pour le dernier échec.
- `classify_failure()` permet de tester directement toute la chaîne décisionnelle avec une sévérité et un contexte explicitement fournis.
- La corrélation de la requête est propagée vers l'anomalie et l'enregistrement d'erreur.

## Validation

Les tests couvrent :

- passage d'un échec d'orchestration dans les quatre couches de décision ;
- décision `RETRY` bornée pour une anomalie moyenne ;
- décision `HALT` supervisée pour une anomalie critique ;
- absence de second appel runtime : l'intégration ne déclenche pas elle-même le retry.

## Limites

L'exécution concrète des décisions de récupération ou de dégradation reste volontairement hors de cette étape. Elle pourra être ajoutée dans une infrastructure dédiée sans modifier les contrats de décision.
