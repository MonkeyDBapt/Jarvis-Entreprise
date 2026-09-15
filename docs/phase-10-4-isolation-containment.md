# Phase 10.4 — Isolation / containment

**Statut : validée.**

## Objectif

Définir une frontière provider-independent permettant de déterminer quand et à quel périmètre une anomalie doit être contenue, sans exécuter directement l'action de confinement.

## Modèle retenu

`ContainmentDecision` décrit :

- `action` : `none` ou `isolate` ;
- `scope` : composant ou exécution ;
- `target` : cible connue de l'isolation, lorsqu'elle peut être déterminée ;
- `reason` : justification déterministe ;
- `requires_supervision` : indique si une supervision est nécessaire avant continuation.

`ContainmentManager` transforme une `Anomaly` en décision de confinement déterministe.

## Politique par défaut

| Sévérité | Action | Périmètre | Supervision |
|---|---|---|---|
| `low` | `none` | — | non |
| `medium` | `isolate` | composant | non |
| `high` | `isolate` | exécution | oui |
| `critical` | `isolate` | exécution | oui |

Pour les anomalies `high` et `critical`, la cible privilégiée est la `correlation_id` de l'exécution. Si elle est absente, la décision conserve une cible indéterminée afin d'éviter d'isoler arbitrairement un autre composant.

## Sécurité des effets de bord

Le gestionnaire ne réalise volontairement aucune isolation réelle. Il ne :

- n'annule pas de tâche ;
- ne désactive pas d'agent ;
- ne révoque pas de permission ;
- ne ferme pas de transport ;
- ne modifie pas l'état du runtime.

La décision doit être appliquée par le composant d'exécution compétent, en respectant les frontières de permissions, d'autonomie, de contrôle et de supervision déjà établies.

Cette séparation évite qu'une anomalie puisse déclencher implicitement un effet de bord non contrôlé.

## Validation

`tests/test_containment.py` couvre :

- l'absence de confinement pour une anomalie faible ;
- l'isolation du composant pour une anomalie moyenne ;
- l'isolation de l'exécution et la supervision pour les anomalies élevée et critique ;
- l'absence de cible arbitraire lorsque la corrélation est inconnue.

La CI GitHub reste responsable de la validation multi-version Python et de la suite complète de tests.

## Frontières

Cette étape ne réalise volontairement pas :

- la remédiation ;
- la récupération ;
- les retries ou backoff ;
- le circuit breaker ;
- la persistance ;
- le transport d'événements ;
- l'intégration complète de la décision dans l'orchestrateur.

Ces responsabilités restent séparées pour les étapes ultérieures de la Phase 10.

## Conclusion

JARVIS dispose maintenant d'un contrat stable permettant de passer d'une anomalie à une décision de confinement explicite et contrôlable, sans coupler le cœur du système à une mécanique d'isolation particulière.
