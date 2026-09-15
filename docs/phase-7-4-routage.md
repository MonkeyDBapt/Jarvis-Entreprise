# Phase 7.4 — Routage

## Objectif

Établir une frontière de routage indépendante des transports afin que JARVIS puisse choisir le canal de communication approprié sans coupler les composants aux implémentations concrètes.

## Contrat retenu

`CommunicationRouterProtocol` définit deux opérations :

- `route_message(message, channel)` : router un `CommunicationMessage` vers le canal direct ou message ;
- `route_event(event, channel)` : router un `CommunicationEvent` vers le canal événementiel.

`CommunicationRouter` centralise la sélection du canal et délègue ensuite à la frontière de livraison correspondante.

## Canaux

- `direct` : échange local synchrone via un handler enregistré ;
- `message` : livraison point-à-point via `MessageDelivery` ;
- `event` : publication via `EventDelivery`.

Le routage ne connaît aucun broker, protocole réseau ou fournisseur externe.

## Règles

- Un message doit avoir un destinataire.
- Un `CommunicationMessage` ne peut être routé que par `direct` ou `message`.
- Un `CommunicationEvent` ne peut être routé que par `event`.
- Une frontière de livraison absente produit une erreur explicite plutôt qu'un routage implicite.
- Les handlers directs sont uniques par identifiant.
- Les contrats `MessageDelivery` et `EventDelivery` restent remplaçables indépendamment du routeur.

## Validation

`tests/test_communication_routing.py` couvre :

- routage message → `MessageDelivery` ;
- routage message → direct ;
- routage événement → `EventDelivery` ;
- rejet d'un canal incompatible ;
- rejet d'une frontière de livraison manquante ;
- rejet d'un destinataire direct inconnu ;
- rejet d'un événement sur un canal non événementiel.

## Limites volontairement conservées

Cette étape ne définit pas encore :

- routage distribué ;
- load balancing ;
- priorités ou files ;
- retry/dead-letter ;
- wildcard avancé ;
- persistance ;
- politique de sécurité/permission de communication ;
- observabilité spécialisée ;
- intégration applicative obligatoire dans l'orchestrateur.

Ces responsabilités restent séparées et pourront être ajoutées ultérieurement sans remplacer les contrats de livraison existants.
