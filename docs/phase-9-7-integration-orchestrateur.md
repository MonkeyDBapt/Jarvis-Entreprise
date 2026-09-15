# Phase 9.7 — Intégration orchestrateur

**Statut : validée / consolidée**

## Objectif

Relier les contrats d'observabilité des étapes 9.1 à 9.6 au point d'entrée `JarvisOrchestrator`, sans imposer de backend externe.

## Intégration

`JarvisOrchestrator` expose désormais des dépendances injectables pour :

- `StructuredLogger` — journalisation structurée ;
- `MetricRegistry` — compteurs et durée des orchestrations ;
- `TraceRecorder` — trace causale d'une exécution ;
- `AuditRecorder` — événements `requested`, `completed` et `failed` ;
- `HealthRegistry` — état de disponibilité du workflow MAF.

Chaque appel à `run()` :

1. crée ou reprend une identité de trace ;
2. associe une corrélation stable à la requête ;
3. enregistre la demande ;
4. exécute les contrôles, la résolution agent/modèle, la mémoire puis le workflow MAF ;
5. enregistre succès ou échec ;
6. mesure la durée ;
7. clôture un span de trace avec son statut.

Les interfaces restent provider-independent et les enregistreurs restent en mémoire, conformément aux frontières définies par les étapes 9.1 à 9.6.

## Vérifications

Le test `tests/test_orchestrator_observability.py` vérifie :

- une exécution complète observable ;
- les compteurs requêtes/succès/échecs ;
- l'observation de durée ;
- la séquence d'audit ;
- la présence et la corrélation du trace ;
- l'état de santé du workflow ;
- la remontée d'un échec d'orchestration dans l'audit, les métriques et la trace.

## Limites conservées

Cette étape n'introduit volontairement :

- aucun backend de logs externe ;
- aucun backend de métriques externe ;
- aucun backend de traces externe ;
- aucune persistance d'audit ;
- aucun broker ou transport distribué ;
- aucune modification du runtime Hermes ou du workflow MAF lui-même.

Ces éléments restent des responsabilités d'infrastructure ou de phases ultérieures.
