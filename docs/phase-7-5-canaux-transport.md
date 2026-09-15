# Phase 7.5 — Canaux / transport

## Objectif

Établir une frontière entre les canaux logiques de JARVIS et leurs implémentations de transport, afin que le routage ne dépende d'aucun broker, protocole réseau ou fournisseur concret.

## Contrat retenu

`CommunicationTransport` définit la frontière de transport :

- `channel_kind` : canal logique pris en charge ;
- `send_message(message)` : transport d'un message point-à-point ;
- `publish_event(event)` : transport d'un événement.

`CommunicationTransportRegistry` associe les canaux `message` et `event` à leurs transports concrets.

Le canal `direct` reste volontairement local et synchrone : il est géré par `CommunicationRouter` et n'est pas enregistré comme transport externe.

## Implémentation de référence

`InMemoryCommunicationTransport` fournit le transport local de référence en réutilisant les contrats `MessageDelivery` et `EventDelivery` déjà établis.

Cette implémentation permet de valider la frontière sans introduire de broker, réseau, persistance ou distribution.

## Intégration au routage

`CommunicationRouter` peut maintenant recevoir un `CommunicationTransportRegistry`. Lorsque ce registre est configuré :

- `message` est délégué au transport du canal `message` ;
- `event` est délégué au transport du canal `event` ;
- `direct` reste traité localement.

Le mode historique utilisant directement `MessageDelivery` / `EventDelivery` reste compatible lorsqu'aucun registre de transports n'est fourni.

## Règles

- un transport concret ne peut être enregistré que pour `message` ou `event` ;
- un seul transport est enregistré par canal ;
- le canal `direct` ne passe pas par la registry de transports ;
- une opération incompatible avec le canal du transport produit une erreur explicite ;
- le routeur conserve la sélection logique et le transport reste remplaçable.

## Validation

`tests/test_communication_transports.py` couvre :

- livraison d'un message via le transport mémoire ;
- publication d'un événement via le transport mémoire ;
- rejet des transports dupliqués ;
- rejet d'un transport direct ;
- utilisation du registre par le routeur ;
- rejet d'une opération incompatible avec le transport.

## Limites volontairement conservées

Cette étape ne définit pas encore :

- transport réseau réel ;
- broker distribué ;
- persistance ;
- retry/dead-letter ;
- load balancing ;
- chiffrement réseau ;
- découverte dynamique de transports ;
- observabilité spécialisée.

Ces responsabilités pourront être ajoutées ultérieurement derrière la même frontière.
