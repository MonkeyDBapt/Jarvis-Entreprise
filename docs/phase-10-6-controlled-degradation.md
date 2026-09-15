# Phase 10.6 — Dégradation contrôlée

## Objectif

Fournir une décision déterministe et bornée permettant à JARVIS de réduire progressivement son niveau de fonctionnement lorsqu'une anomalie ou une récupération l'exige, sans coupler cette décision à une implémentation runtime.

## Contrats

- `DegradationLevel` décrit le niveau opérationnel recommandé : `FULL`, `DEGRADED`, `SAFE`, `HALTED`.
- `DegradationAction` décrit la transition recommandée : `NONE`, `REDUCE`, `SAFE_MODE`, `HALT`.
- `DegradationDecision` porte l'action, le niveau, la cible, la justification et le besoin éventuel de supervision.
- `DegradationManager` combine la sévérité de l'anomalie et la décision de récupération.

## Règles validées

| Situation | Décision |
|---|---|
| Anomalie faible / aucune récupération | `NONE` → `FULL` |
| Anomalie moyenne / retry | `REDUCE` → `DEGRADED` |
| Anomalie élevée / escalade | `SAFE_MODE` → `SAFE` + supervision |
| Anomalie critique / halt | `HALT` → `HALTED` + supervision |
| Décision de récupération `HALT` | `HALT` prioritaire, même si la sévérité de l'anomalie est plus faible |

La dégradation est volontairement conservative : un état de récupération `HALT` ne peut pas être annulé par une anomalie moins sévère.

## Limites et sécurité

La couche de décision n'effectue aucun effet de bord. Elle ne désactive pas directement les capacités, ne révoque pas les permissions, n'arrête pas les agents, ne modifie pas les transports et ne mute pas l'état runtime.

L'exécution de la dégradation reste du ressort du composant appelant, à travers les frontières existantes de permissions, contrôle, containment et runtime.

## Validation

Les tests dédiés couvrent :

- conservation du fonctionnement complet pour une anomalie faible ;
- réduction contrôlée pour une anomalie moyenne ;
- passage en mode sûr pour une anomalie élevée ;
- arrêt supervisé pour une anomalie critique ;
- priorité d'un `HALT` de récupération ;
- absence d'effet de bord d'exécution dans le gestionnaire.

## Périmètre reporté

La désactivation concrète de capacités, le basculement de modèles, l'arrêt d'agents, la modification de transports, la persistance des états de dégradation et leur automatisation dans l'infrastructure restent séparés des contrats de décision.
