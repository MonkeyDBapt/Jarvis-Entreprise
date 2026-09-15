# Phase 7.3 — Événements

## Objectif

Établir une frontière de communication événementielle indépendante du transport afin que les composants JARVIS puissent publier des faits et que d'autres composants puissent s'y abonner sans connaître l'implémentation de transport.

## Contrat retenu

`EventDelivery` définit trois opérations :

- `subscribe(event_type, handler)` : enregistrer un consommateur pour un type d'événement ;
- `unsubscribe(event_type, handler)` : retirer un consommateur ;
- `publish(event)` : publier un `CommunicationEvent` aux consommateurs du type concerné.

Le contrat est indépendant de tout broker ou bus externe.

## Implémentation de référence

`InMemoryEventDelivery` fournit l'implémentation locale de référence pour cette étape :

- exécution synchrone ;
- ordre de livraison déterministe selon l'ordre d'abonnement ;
- plusieurs abonnés possibles pour un même type ;
- refus des abonnements dupliqués ;
- aucun stockage ou transport externe ;
- événement sans abonné accepté comme publication sans effet ;
- frontière remplaçable par un futur bus/broker distribué.

## Modèle d'événement

`CommunicationEvent` fournit déjà l'enveloppe transport-neutre : identifiant de source, type d'événement, payload, catégorie (`domain`, `lifecycle`, `system`), identifiant d'événement, corrélation, causalité, session, tâche, horodatage et métadonnées.

## Validation

Les tests de `tests/test_event_delivery.py` couvrent :

- livraison à plusieurs abonnés ;
- ordre déterministe ;
- désabonnement ;
- rejet d'un abonnement dupliqué ;
- publication sans abonné ;
- rejet d'un objet qui n'est pas un `CommunicationEvent`.

## Limites volontairement conservées

Cette étape ne définit pas encore :

- broker ou transport distribué ;
- persistance des événements ;
- replay ;
- garantie durable de livraison ;
- retry/dead-letter ;
- routage avancé ou wildcard ;
- observabilité spécialisée ;
- intégration applicative obligatoire dans l'orchestrateur.

Ces éléments pourront être traités dans les étapes ultérieures sans modifier le contrat `EventDelivery`.
