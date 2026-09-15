# Phase 10.1 — Modèle d'anomalie

**Statut : validée**

## Objectif

Définir un contrat stable et provider-independent pour représenter une anomalie détectée par JARVIS Enterprise.

## Modèle retenu

`Anomaly` contient :

- `id` : identifiant stable de l'anomalie ;
- `anomaly_type` : famille normalisée de l'anomalie ;
- `severity` : niveau d'impact (`low`, `medium`, `high`, `critical`) ;
- `source` : origine de l'observation ;
- `component` : composant concerné ;
- `message` : description humaine ;
- `detected_at` : date/heure de détection timezone-aware ;
- `status` : état du cycle de vie ;
- `correlation_id` : corrélation optionnelle avec une exécution ou une trace ;
- `context` : contexte structuré ;
- `evidence` : éléments observés permettant de caractériser l'anomalie.

## Familles d'anomalies

Le contrat couvre les domaines déjà matérialisés dans JARVIS : exécution, communication, capacités, mémoire, intelligence, permissions, runtime, observabilité et infrastructure, avec `unknown` comme valeur de repli.

## Frontières

Le modèle ne décide volontairement pas :

- comment une anomalie est détectée ;
- comment elle est classifiée dynamiquement ;
- comment elle est corrigée ;
- quelle stratégie de récupération est appliquée ;
- comment elle est persistée ou transportée.

Ces responsabilités appartiennent aux étapes ultérieures de la Phase 10.

## Validation

`tests/test_anomaly_model.py` vérifie :

- l'état initial `detected` ;
- les timestamps timezone-aware ;
- la sérialisation du contrat ;
- le rejet des champs obligatoires vides ;
- le rejet des timestamps naïfs.

La CI reste responsable de la validation multi-version Python et de la suite complète de tests.

## Conclusion

Le contrat d'anomalie est suffisamment stable pour servir de frontière aux étapes suivantes de la résilience, sans coupler le cœur JARVIS à un mécanisme de détection ou de récupération particulier.
