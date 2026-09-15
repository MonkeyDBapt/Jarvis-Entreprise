# Phase 10.2 — Détection / classification

**Statut : validée sous réserve de la CI finale.**

## Objectif

Fournir une frontière provider-independent entre les observations issues de l'observabilité et le contrat `Anomaly` défini en 10.1.

## Modèle retenu

`AnomalyObservation` représente une observation normalisée avec :

- `source` ;
- `component` ;
- `message` ;
- `anomaly_type` ;
- `severity` ;
- `detected_at` optionnel et timezone-aware ;
- `correlation_id` optionnel ;
- `context` ;
- `evidence`.

`AnomalyDetector` transforme cette observation en `Anomaly` et conserve la classification fournie par la source, avec `unknown` comme famille par défaut et `medium` comme sévérité par défaut.

## Frontières

Cette étape ne réalise volontairement pas :

- l'analyse automatique de signaux bruts ;
- la déduplication ou le regroupement d'anomalies ;
- la remédiation ;
- la récupération ;
- la persistance ;
- le transport d'événements.

La détection au sens du pipeline est donc limitée à la normalisation d'une observation déjà identifiée comme anomalie. Les mécanismes d'analyse dynamique pourront être ajoutés plus tard sans modifier le contrat `Anomaly`.

## Validation

`tests/test_anomaly_detection.py` couvre :

- la création d'une anomalie classifiée ;
- la conservation du type et de la sévérité ;
- la conservation du contexte, des preuves et de la corrélation ;
- le repli sur `unknown` / `medium` ;
- le rejet d'un timestamp naïf ;
- le rejet des champs obligatoires vides.

La CI GitHub doit valider l'ensemble de la suite sur Python 3.10 à 3.13.

## Conclusion

La couche de détection/classification fournit désormais une frontière stable entre observabilité et résilience, sans coupler le cœur JARVIS à une source, une méthode de détection ou une stratégie de récupération particulière.
