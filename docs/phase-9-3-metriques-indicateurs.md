# Phase 9.3 — Métriques / indicateurs

## Statut

**Validée / consolidée.**

## Objectif

Fournir à JARVIS Enterprise un contrat de métriques indépendant du fournisseur, permettant de mesurer les comportements et performances utiles à la vérification et à l'observabilité.

## Modèle retenu

```text
MetricDefinition
      │
      ▼
 MetricRegistry
      │
      ├── Counter
      ├── Gauge
      └── Histogram
             │
             ▼
       MetricSnapshot
```

### Types

- `counter` : valeur cumulative non décroissante ;
- `gauge` : valeur instantanée remplaçable ;
- `histogram` : observations agrégées avec nombre, total, minimum, maximum et moyenne.

## Principes

- métriques nommées et définies explicitement ;
- labels structurés et déterministes ;
- valeurs numériques finies ;
- registre local thread-safe ;
- aucun backend ou fournisseur imposé ;
- snapshots indépendants de la collecte ou de l'expédition ;
- aucune confusion avec les logs de Phase 9.2 ;
- aucune dépendance à une plateforme de monitoring ajoutée à cette étape.

## Garanties

- une métrique doit être enregistrée avant utilisation ;
- une définition existante ne peut pas être remplacée par une définition incompatible ;
- les compteurs refusent les décréments ;
- les labels vides et valeurs non finies sont rejetés ;
- les snapshots sont déterministes et séparés par jeu de labels ;
- les opérations sont protégées par un verrou pour l'utilisation concurrente.

## Périmètre volontairement exclu

La visualisation, les dashboards, l'export Prometheus/OpenTelemetry, la persistance longue durée, les alertes, la rétention et le stockage distant restent hors périmètre.

## Indicateurs de référence rendus possibles

Le contrat permet notamment de mesurer ultérieurement :

- nombre de requêtes / tâches ;
- tâches réussies ou échouées ;
- agents actifs ;
- durée d'exécution ;
- volume d'appels modèle ;
- erreurs par composant ;
- consommation de ressources lorsqu'une source de mesure sera intégrée.

## Validation

`tests/test_observability_metrics.py` couvre les compteurs, jauges, histogrammes, labels, validation des valeurs, incompatibilités de type et définitions dupliquées.

La CI du dépôt valide l'ensemble de la suite sur Python 3.10, 3.11, 3.12 et 3.13.
