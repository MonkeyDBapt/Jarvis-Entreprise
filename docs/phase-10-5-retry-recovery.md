# Phase 10.5 — Retry / récupération

## Objectif

Fournir une décision de récupération déterministe et bornée après une anomalie ou une erreur, sans coupler JARVIS à un mécanisme concret d'exécution, de transport ou de persistance.

## Contrats

- `RetryPolicy` définit une limite explicite de tentatives.
- `RecoveryDecision` décrit l'action recommandée, la tentative courante, la limite et le besoin éventuel de supervision.
- `RecoveryManager` combine la décision de gestion d'erreur avec la sévérité de l'anomalie.

## Règles validées

| Situation | Décision |
|---|---|
| Erreur faible / `record` | `NONE` |
| Erreur moyenne / `retry`, budget disponible | `RETRY` borné |
| Erreur moyenne / budget épuisé | `ESCALATE` + supervision |
| Erreur élevée / `escalate` | `ESCALATE` + supervision |
| Erreur critique / `halt` | `HALT` + supervision |

Les décisions sont déterministes et ne réalisent aucun effet de bord : pas de `sleep`, pas de nouvel appel runtime, pas de mutation d'état, pas de restauration automatique et pas de persistance.

L'exécution effective d'une récupération reste du ressort du composant appelant, dans les frontières déjà établies par les permissions, le contrôle, le containment et le runtime.

## Validation

Les tests dédiés couvrent :

- retry dans la limite ;
- épuisement du budget ;
- absence de récupération pour `record` ;
- escalade supervisée ;
- arrêt critique ;
- rejet d'un compteur de tentative négatif.

## Limites de l'étape

La persistance des tentatives, les délais/backoff réels, la reprise de tâche, la restauration d'état et l'intégration complète dans l'orchestrateur restent séparés afin de ne pas mélanger décision et exécution.
