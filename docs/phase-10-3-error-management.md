# Phase 10.3 — Gestion des erreurs

**Statut : validation technique en attente de la CI finale.**

## Objectif

Fournir une frontière provider-independent pour normaliser les erreurs d'exécution et déterminer une stratégie de traitement sans exécuter directement les effets de bord.

## Modèle retenu

`ErrorRecord` normalise :

- identité de l'erreur ;
- source et composant ;
- message ;
- famille d'anomalie ;
- sévérité ;
- type d'exception ;
- date/heure timezone-aware ;
- corrélation ;
- contexte.

`ErrorManager` transforme une exception en `ErrorRecord` et produit une `ErrorHandlingDecision` déterministe.

Les actions disponibles sont :

- `record` : enregistrer et poursuivre ;
- `retry` : le composant appelant peut tenter une nouvelle exécution ;
- `escalate` : supervision requise avant continuation ;
- `halt` : arrêter l'exécution en attendant une récupération.

## Sécurité des effets de bord

Le gestionnaire ne réalise volontairement ni retry, ni escalade, ni arrêt, ni persistance. Il fournit une décision au composant responsable de l'exécution. Cela évite qu'une politique d'erreur puisse déclencher implicitement une action opérationnelle non contrôlée.

## Politique par défaut

| Sévérité | Action |
|---|---|
| `low` | `record` |
| `medium` | `retry` |
| `high` | `escalate` |
| `critical` | `halt` |

Cette politique est déterministe et remplaçable. Les mécanismes avancés de retry, backoff, circuit breaker, récupération et persistance restent hors de cette étape.

## Validation

`tests/test_error_management.py` couvre :

- normalisation d'une exception ;
- conservation du contexte et de la corrélation ;
- fallback sur le nom du type d'exception lorsque le message est vide ;
- décision déterministe par sévérité ;
- rejet des timestamps naïfs.

La CI doit valider l'installation et l'ensemble de la suite sur Python 3.10 à 3.13.

## Conclusion

La gestion des erreurs fournit désormais une frontière stable entre une erreur d'exécution et son traitement. Elle reste découplée de la remédiation et de la récupération qui seront traitées dans les étapes suivantes de la Phase 10.
