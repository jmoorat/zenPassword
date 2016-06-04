# Présentation
ZenPassword permet la création d'un espace chiffré (appelé "boîte") et sécurisé par un mot de passe principal pour y entreposer tous ses mots de passes !

Ce pogramme est développé dans un cadre éducatif et n'utilise pas (encore) de technologies de chiffrement avancées comme AES.
Actuellement, le contenu des boîtes est chiffré avec la technique du chiffre de Vigenère utilisant une clé SHA-512 généré d'après le mot de passe de la boîte.

# Fonctionnement relatif aux boîtes
## Création d'une boîte
En créant une boîte, vous devrez lui donner une nom et lui assigner un mot de passe principal.
Ce mot de passe devra être long d'au moins 8 caractères afin d'assurer une sécurité minimale au futur contenu.
Le programme créera ensuite votre boîte qui sera stockée dans un fichier .zpdb dans son répertoire.

## Ouvrir une boîte
Pour ouvrir une boîte. Cliquez sur "Ouvrir une boîte" dans le menu principal et sélectionnez la boîte à ouvrir puis tappez votre mot de passe pour accéder à son contenu.

## Supprimer une boîte
La suppression d'une boite ne s'effectue pas depuis le logiciel.

# Gestion du contenu d'une boîte

## Fonctionnement des entrées
Chaque entrée comprend un nom (inchangeable pour le moment), un identifiant, un mot de passe et une note. Lors de la création d'une entrée chacun des champs est chiffré grâce à votre mot de passe puis stocké dans la boîte.

## Attention
Votre boîte étant stocké sur votre disque dur, elle peut tout à fait être supprimé. Prenez garde !
