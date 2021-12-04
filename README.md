# Projet PCD :  RAMI ET THIBAULT

## DERNIERE MAJ

- 04/12/21

## Server

- launch side server : python3 irc_server.py **server_name**

## Client

- launch side client : python3 irc_client.py **user_name  server_name**

## DONE

irc_client:

- class irc_client
- deux threads (1 pour écouter le server, 1 pour parler au server( à voir s'il ne faut pas 1 thread par message))

irc_server:

- class channel
- class irc_server
- 1 thread continue pour écouter chaque client / 1 thread par message(à revoir?)
- parsing argument des fichiers (sauf pour la liste des serveurs cf. étape 2)

## TODO

- parser les arguements côté serveur pour réagir en conséquence
- une fois le parser, coder les différents fonctions
- lorsqu'un client se connecte à un server, l'ajouter à la liste des utilisateurs (il faut envoyer l'username au serveur)
- tkinter (interface graphique côté client avec une zone affichage et une zone d'entrée)

## Main pb

- Est ce qu'on peut utiliser un thread continue pour parler avec un input pour envoyer ce qu'on veut niveau code ?
