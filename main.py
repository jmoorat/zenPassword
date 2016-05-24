#coding : utf-8
#encodage en utf-8 pour éviter certains bug d'après des recherches effectuées
#Importation des modules nécessaires
import os
import time #utile pour gestion du temps
from tkinter import * #interface graphique Tkinter
from tkinter.messagebox import * #Boîtes de dialogues
from tkinter.filedialog import * #Fenêtres d'exploration
import sqlite3 #gestion de la base de données
import hashlib #Permet de hacher les mot de passe et ainsi de garder seulement leur signature MD5 en base de données et non le mot de pas en clair

#importation de la méthode de chiffrement AES depuis le module PyCrypto.
#Attention : extension Python à installer !
#from Crypto.Cipher import AES
#from getpass import getpass

#Alphabet des caractères supportés par le chiffrement
alpha = " ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzéèàùâêîôûïöëñ0123456789!\"#$%&£€§'()[]{|}*+,-./\\:;<=>?@~^_"
lenAlpha = len(alpha)
version ="v0.1"

#Définitions des fonctions

#Fonctions sur la base de données

def creerBoite(nom, hashmdp, chemin):
    """Fonction créant le fichier .spdb (appelé la "boîte") qui est une base de
    données SQLITE qui contient après création la valeur de hachage SHA-256 du
    mot de passe dans une table "hash" et une seconde table "boite" vide qui
    contiendra les futurs entrées."""

    global bdd, connect, cur

    nom = nom.replace(' ', '_') #on remplace les espace par un underscore -> un seul mot = OK pour la requête SQL
    bdd = chemin+"/"+nom+".spdb"
    connect = sqlite3.connect(bdd) #creation de l'objet representant la connexion à la base de données
    cur = connect.cursor() #curseur qui va stocker temporairement les requêtes avant des les envoyer en bdd par un connect.commit()

    #création de la table qui stockera la valeur hachée SHA-256 du mot de passe
    cur.execute('CREATE TABLE hash(sha256 TEXT)')
    cur.execute("CREATE TABLE boite(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, nom TEXT, identifiant TEXT, motdepasse TEXT, note TEXT)")
    connect.commit()

    #Ajout du hash du mot de passe à la base de données
    prepare = (hashmdp,)
    cur.execute("INSERT INTO hash(sha256) VALUES(?)", prepare)
    #insertion d'une entrée dans la liste de nos boîtes
    #le ? sera remplacé respectivement par chaque valeur du tuple (dans l'ordre !)

    connect.commit() #on écrit les changements dans la bdd
    del hashmdp
    return

def ajouterEntreeBoite(nomEntree, identifiant, mdp, note):
    """Fonction ajoutant une nouvelle entrée à la base de données / boîte"""

    global bdd, connect, cur, cle, cheminBoite

    prepareAjout = [(chiffre(nomEntree, cle), chiffre(identifiant, cle), chiffre(mdp, cle), chiffre(note, cle))]
    for tu in prepareAjout:
        cur.execute("INSERT INTO boite(nom, identifiant, motdepasse, note) VALUES (?, ?, ?, ?)", tu)
    connect.commit() #on écrit les changements dans la bdd
    return True

def modifEntreeBoite(nomEntree, identifiant, mdp, note):
    """Fonction modifiant une entrée existante dans la base de données/ boîte courante"""

    global bdd, connect, cur, cle, cheminBoite

    prepareModif = [(chiffre(identifiant, cle), chiffre(mdp, cle), chiffre(note, cle), chiffre(nomEntree, cle))]
    #les champs sont avant le nom de l'entrée car la modif va être demandé avant l'entrée dans la requête SQL
    for tu in prepareModif: #boucle qui va permettre de remplacer chaque données de prepareModif dans la requête (une par une)
        cur.execute("UPDATE boite SET identifiant = ?, motdepasse = ?, note = ? WHERE nom = ?", tu)
        connect.commit() #on écrit les changements dans la bdd
    return True

def supprimerEntreeBoite(nomEntree):
    """Supprime une entrée de la base de données ("boîte") courante"""

    global bdd, connect, cur, cle, cheminBoite, listNom

    prepareSuppr = [(chiffre(nomEntree, cle))]
    cur.execute("DELETE FROM boite WHERE nom = ?", prepareSuppr)
    connect.commit() #on écrit les changements dans la bdd
    listeNom.delete(listeNom.curselection()) #suppression de l'entrée dans la liste de la fenêtre boite
    fenBoite.focus_set() #garde la fenêtre boite au dessus des autres
    return True

def getId(nomEntree):
    """Fonction qui récupère le champ "identifiant" associé au nom d'une entrée dans la base de données ("boîte") courante"""

    global bdd, connect, cur, cle, cheminBoite

    prepare = (chiffre(nomEntree, cle),)
    cur.execute("SELECT identifiant FROM boite WHERE nom = ?", prepare)
    data = list(cur) # On stocke le contenu du curseur dans une liste
    identifiant = dechiffre(data[0][0], cle) # On extrait la données correspondant au mot de passe dans la liste data
    return identifiant

def getMdp(nomEntree):
    """Fonction qui récupère le champ "mot de passe" associé au nom d'une entrée dans la base de données ("boîte") courante"""

    global bdd, connect, cur, cle, cheminBoite

    prepare = (chiffre(nomEntree, cle),) #on prépare ce qu'on va intégrer à la requête
    cur.execute("SELECT motdepasse FROM boite WHERE nom = ?", prepare)
    data = list(cur) # On stocke le contenu du curseur dans une liste
    mdp = dechiffre(data[0][0], cle) # On extrait la données correspondant au mot de passe dans la liste data
    return mdp

def getNote(nomEntree):
    """Fonction qui récupère le champ "note" associée au nom d'une entrée dans la base de données ("boîte") courante"""

    global bdd, connect, cur, cle, cheminBoite

    prepare = (chiffre(nomEntree, cle),)
    cur.execute("SELECT note FROM boite WHERE nom = ?", prepare)
    data = list(cur) # On stocke le contenu du curseur dans une liste
    note = dechiffre(data[0][0], cle) # On extrait la données correspondant au mot de passe dans la liste data
    return note

#Fonctions de sécurité
def chiffre(chaineIn, cle):
    """Fonction chiffrant une chaîne de caractère donnée à l'aide d'une clé de chiffrement donnée

    Chiffrement de Vigenère"""

    listIndiceChaineOut = []
    i = 0
    chaineOut = ""

    #Cryptage des caractères de la chaine
    for char in chaineIn:
        """Pour chaque caractère de la chaineIn, on lui affecte un nouvel indice
         en lui ajoutant l'indice du premier caractère de la clé puis du deuxième ..."""
        listIndiceChaineOut.append(alpha.find(char)+alpha.find(cle[i%len(cle)]))
        i += 1
    #DEBUG print (listIndiceChaineOut)

    #Formation de la chaine cryptée
    for indice in listIndiceChaineOut:
        chaineOut += alpha[indice%lenAlpha]

    return chaineOut

def dechiffre(chaineIn, cle):
    """Fonction déchiffrant une chaîne de caractère donnée à l'aide d'une clé de chiffrement donnée

    Chiffrement de Vigenère"""

    listIndiceChaineOut = []
    i = 0
    chaineOut = ""

    #Cryptage des caractères de la chaine
    for char in chaineIn:
        """Pour chaque caractère de la chaineIn, on lui affecte un nouvel indice
         en lui ajoutant l'indice du premier caractère de la clé puis du deuxième ..."""
        listIndiceChaineOut.append(alpha.find(char)-alpha.find(cle[i%len(cle)]))
        i += 1
    #DEBUG print (listIndiceChaineOut)

    #Formation de la chaine cryptée
    for indice in listIndiceChaineOut:
        chaineOut += alpha[indice%lenAlpha]

    return chaineOut

def sha256(mdp):
    """Fonction renvoyant une chaîne de caractère comportant la valeur de hachage SHA-256 de la chaîne en entrée"""

    #utilisation du module hashlib pour générer la valeur hashé du mdp
    hash_output = hashlib.sha256(mdp.encode('utf-8')).hexdigest()
    return hash_output

#TKINTER
def browse():
    """Fenêtre permettant de sélectionner le chemin du fichier à ouvrir"""
    fichier = ""
    fichier = askopenfilename(title="Ouvrir une boîte",filetypes=[('Fichiers SPDB','.spdb'),('Tous les fichiers','.*')])
    if fichier == "":
        return
    else:
        unlock(fichier)

def unlock(fichier):
    """Fenêtre d'authentification (demande du mot de passe de la boîte)"""
    global bdd, connect, cur, cle, cheminBoite, fenUnlock

    #-- Ouverture du fichier de base de données
    bdd = fichier
    cheminBoite = fichier
    connect = sqlite3.connect(bdd) #creation de l'objet representant la connexion à la base de données
    cur = connect.cursor() #curseur qui va stocker temporairement les requêtes avant des les envoyer en bdd par un connect.commit()
    cur.execute("SELECT sha256 FROM hash")
    data = list(cur)
    hash_mdp_bdd = str(data[0][0]) #premier element du premier tuple -> deux [0] index 00
    #-----

    #Elements de la fenêtre
    fenUnlock = Toplevel()
    fenUnlock.title("Déverrouillage")
    cadenas = PhotoImage(file="img/cadenas_64.png")
    labelCadenas = Label(fenUnlock, image=cadenas)
    mdp = StringVar()
    labelMdp = Label(fenUnlock, text="Mot de passe")
    champMdp = Entry(fenUnlock, textvariable=mdp, show="●") #show="●" va permettre de masquer ce qu'écrit l'utilisateur
    champMdp.focus_set()
    buttonValider = Button(fenUnlock, text="Valider", command=lambda:verifMdp(mdp.get(), hash_mdp_bdd))

    #Positionnement des éléments de la fenêtre
    labelCadenas.pack()
    labelMdp.pack(side=LEFT, padx=5, pady=5)
    champMdp.pack(side=LEFT, padx=5, pady=5)
    buttonValider.pack(side=LEFT, padx=5, pady=5)

    fenUnlock.mainloop()
    return fenUnlock.destroy

def verifMdp(mdp, hash_mdp_bdd):
    """Vérification du mot de passe par comparaison des valeurs de hachages en
    SHA-256"""
    global bdd, connect, cur, cle, cheminBoite, fenUnlock

    #On vérifie que la valeur hashée du mot de passe correspond à celle stockée en base de données
    if sha256(mdp) == hash_mdp_bdd: #Correspondance -> on ouvre la boite
        cle = mdp
        mdp =""
        del mdp
        del hash_mdp_bdd
        fenUnlock.destroy()
        return boite()
    else: #Erreur > on ouvre pas la boite
        alerte = showerror("Mot de passe incorrect", "Accès refusé")
        return

def boite():
    """Fenêtre principale de la boîte"""
    global bdd, connect, cur, cle, cheminBoite, fenBoite, listeNom

    #Definition de la fenêtre
    fenBoite = Toplevel()
    fenBoite.title(cheminBoite)
    fenBoite.geometry("300x175")

    #Définition de la liste des entrées
    listeNom = Listbox(fenBoite)
    cur.execute("SELECT nom FROM boite")
    data = list(cur)
    i = 0
    for element in data:
        listeNom.insert(END, dechiffre(data[i][0], cle)) #on utilise i+1 pour la correspondance avec les id des entrées
        i += 1
    listeNom.select_set(0) #On sélectionne par défaut la première entrée de la liste

    buttonVoir = Button(fenBoite, text="Voir l'entrée", command=lambda:afficheEntree(listeNom.get(listeNom.curselection()[0])))
    buttonFermerBoite = Button(fenBoite, text="Fermer la boîte", command=fermerBoite)

    #Définition du menu
    menuBoite = Menu(fenBoite)
    menuEntrees = Menu(menuBoite, tearoff=0)
    menuEntrees.add_command(label="Voir l'entrée sélectionnée", command=lambda:afficheEntree(listeNom.get(listeNom.curselection()[0])))
    menuEntrees.add_command(label="Ajouter une entrée", command=fenAjoutEntreeBoite)
    menuEntrees.add_command(label="Modifier une entrée", command=lambda:fenModifEntreeBoite(listeNom.get(listeNom.curselection()[0])))
    menuEntrees.add_command(label="Supprimer l'entrée sélectionnée", command=lambda:supprimerEntreeBoite(listeNom.get(listeNom.curselection()[0])))
    menuBoite.add_cascade(label="Entrées", menu=menuEntrees)
    menuBoite.add_command(label="Fermer la boîte", command=fermerBoite)
    fenBoite.config(menu=menuBoite)
    #listeNom.get(listeNom.curselection()[0]) permet de récupérer le contenu de l'élément de la liste sélectionné

    #Positionnement des éléments
    listeNom.pack(side=LEFT)
    buttonVoir.pack(side=RIGHT, padx=25)

    fenBoite.mainloop()

    return fermerBoite()

def fenCreationBoite():
    """Fenêtre permettant la création d'une nouvelle boîte"""
    global fenCreationBoite

    #Elements de la fenêtre
    fenCreationBoite = Toplevel()
    fenCreationBoite.title("Créer une boîte")
    fenCreationBoite.geometry("220x200")
    nomBoite = StringVar()
    mdpBoite = StringVar()
    cheminBoite = StringVar()
    labelNom = Label(fenCreationBoite, text="Nom de la boîte : ")
    labelMdp = Label(fenCreationBoite, text="Mot de passe principal : ")
    entryNom = Entry(fenCreationBoite, textvariable=nomBoite)
    entryMdp = Entry(fenCreationBoite, textvariable=mdpBoite, show="●")
    buttonChemin = Button(fenCreationBoite, text="Choisir un répertoire", command=lambda:cheminBoite.set(askdirectory()))
    buttonValider = Button(fenCreationBoite, text="Valider", command=lambda:verifCreationBoite(nomBoite.get(), mdpBoite.get(), cheminBoite.get()))
    buttonQuitter = Button(fenCreationBoite, text="Quitter", command=fenCreationBoite.destroy)

    #Positionnement des éléments
    labelNom.pack(pady=1)
    entryNom.pack(pady=2)
    labelMdp.pack(pady=1)
    entryMdp.pack(pady=2)
    buttonChemin.pack(pady=2)
    buttonValider.pack(side=LEFT, pady=5, padx=5)
    buttonQuitter.pack(side=RIGHT, pady=5, padx=5)

    fenCreationBoite.mainloop()

def fenAjoutEntreeBoite():
    """Fonction créant la fenêtre d'ajout d'entrée à une boîte"""
    global fenAjout

    #Définition de la fenêtre et ses éléments
    fenAjout = Toplevel()
    fenAjout.title("Ajouter une entrée")
    entreeNom = StringVar()
    entreeId = StringVar()
    entreeMdp = StringVar()
    entreeNote = StringVar()

    labelNom = Label(fenAjout, text="Nom de l'entrée : ")
    labelId = Label(fenAjout, text="Identifiant : ")
    labelMdp = Label(fenAjout, text="Mot de passe : ")
    labelNote = Label(fenAjout, text="Note/Commentaire : ")
    entryNom = Entry(fenAjout, textvariable=entreeNom)
    entryId = Entry(fenAjout, textvariable=entreeId)
    entryMdp = Entry(fenAjout, textvariable=entreeMdp)
    entryNote = Entry(fenAjout, textvariable=entreeNote)
    buttonValider = Button(fenAjout, text="Valider", command=lambda:verifAjoutEntreeBoite(entreeNom.get(), entreeId.get(), entreeMdp.get(), entreeNote.get()))

    #Positionnement des éléments
    labelNom.pack(pady=1)
    entryNom.pack(pady=1)
    labelId.pack(pady=1)
    entryId.pack(pady=1)
    labelMdp.pack(pady=1)
    entryMdp.pack(pady=1)
    labelNote.pack(pady=1)
    entryNote.pack(pady=1)
    buttonValider.pack(pady=1)
    return

def fenModifEntreeBoite(nomEntree):
    """Fenêtre de modification de l'entrée sélectionnée"""

    global fenModif

    #Définition de la fenêtre et de ses éléments
    fenModif = Toplevel()
    entreeId = StringVar()
    entreeMdp = StringVar()
    entreeNote = StringVar()
    entreeId.set(getId(nomEntree))
    entreeMdp.set(getMdp(nomEntree))
    entreeNote.set(getNote(nomEntree))

    labelId = Label(fenModif, text="Identifiant : ")
    labelMdp = Label(fenModif, text="Mot de passe : ")
    labelNote = Label(fenModif, text="Note : ")

    entryId = Entry(fenModif, textvariable=entreeId)
    entryMdp = Entry(fenModif, textvariable=entreeMdp)
    entryNote = Entry(fenModif, textvariable=entreeNote)

    buttonValider = Button(fenModif, text="Valider", command=lambda:verifModifEntreeBoite(nomEntree, entreeId.get(), entreeMdp.get(), entreeNote.get()))
    buttonAnnuler = Button(fenModif, text="Annuler", command=fenModif.destroy)

    #Positionnement des éléments
    labelId.pack(pady=1, padx=2)
    entryId.pack(pady=1, padx=2)
    labelMdp.pack(pady=1, padx=2)
    entryMdp.pack(pady=1, padx=2)
    labelNote.pack(pady=1, padx=2)
    entryNote.pack(pady=1, padx=2)
    buttonValider.pack(pady=1, padx=2)
    buttonAnnuler.pack(pady=1, padx=2)

    fenModif.mainloop()
    return

def afficheEntree(nomEntree):
    """Fenêtre d'affichage de l'entrée sélectionnée"""

    #Définition de la fenêtre et de ses éléments
    fenEntree = Toplevel()
    fenEntree.title(nomEntree)
    fenEntree.geometry("200x250")
    labelId = Label(fenEntree, text="Identifiant : ")
    labelMdp = Label(fenEntree, text="Mot de passe : ")
    labelNote = Label(fenEntree, text="Note : ")

    labelGetId = Label(fenEntree, text=getId(nomEntree))
    labelGetMdp = Label(fenEntree, text=getMdp(nomEntree))
    labelGetNote = Label(fenEntree, text=getNote(nomEntree))

    #Positionnement des éléments
    labelId.pack()
    labelGetId.pack()
    labelMdp.pack()
    labelGetMdp.pack()
    labelNote.pack()
    labelGetNote.pack()

def fermerBoite():
    """Fonction permettant de fermer correctement une boîte en effaçant toutes
    les variables globales liées à la boîte ouverte dont la clé de chiffrement"""
    global bdd, connect, cur, cle, cheminBoite, fenBoite

    #On ferme "proprement" la boîte en supprimant les variables la concernant
    del cur
    del connect
    del bdd
    del cheminBoite
    cle = ""
    del cle
    #on quitte la fenêtre de la boîte
    fenBoite.destroy()
    del fenBoite
    return

def verifCreationBoite(nomBoite, mdpBoite, cheminBoite):
    """Fonction vérifiant les données rentrées dans fenCreationBoite avant création d'une boîte"""
    global fenCreationBoite, bdd, connect, cur

    if len(mdpBoite) < 8:
        alerte = showwarning("Mot de passe trop court", "Votre mot de passe doit faire plus de 8 caractères")
        return
    elif os.path.isfile(cheminBoite+"/"+nomBoite+".spdb") == True:
        alerte = showerror("Erreur", "Un fichier portant le même nom existe déjà")
        return
    elif cheminBoite == "":
        error = showerror("Aucun chemin spécifié", "Aucun chemin n'a été spécifié")

    else:
        question = askquestion("Confirmation", "Etes-vous sûr de créer la boîte \"" + nomBoite +
        "\" dans "+cheminBoite+" ?")

        if question == "yes":
            creerBoite(nomBoite, sha256(mdpBoite), cheminBoite)
            del mdpBoite
            info = showinfo("Boîte créée", "La boîte a bien été créée")
            fenCreationBoite.destroy()
            del fenCreationBoite
            #On supprime les variables de bdd pour arrêter d'utiliser le fichier créé
            del bdd
            del connect
            del cur
            return
        else:
            return

def verifAjoutEntreeBoite(nom, identifiant, mdp, note):
    """Fonction de vérification avant la création d'une nouvelle entrée"""
    global fenAjout, listeNom
    #accès à listeNom définie en globale dans boite pour l'ajout automatique de la nouvelle entrée

    if nom == "":
        error = showerror("Erreur", "Vous devez spécifier un nom pour l'entrée")
        fenBoite.focus_set() #garde la fenêtre boite au dessus des autres
        return
    elif ajouterEntreeBoite(nom, identifiant, mdp, note) == True:
        listeNom.insert(END, nom) #*
        fenAjout.destroy()
        del fenAjout
        fenBoite.focus_set() #garde la fenêtre boite au dessus des autres
        return

def verifModifEntreeBoite(nom, identifiant, mdp, note):
    """Vérification de la modification d'une boite"""
    global fenModif

    if modifEntreeBoite(nom, identifiant, mdp, note) == True:
        info = showinfo("Entrée modifiée", "L'entrée a bien été modifiée.")
        fenModif.destroy()
        fenBoite.focus_set() #garde la fenêtre boite au dessus des autres
        return

#Programme principale
main = Tk()
main.title("ZenPassword "+version)
main['bg']="white"

menu = Menu(main)
menu.add_command(label="Créer", command=fenCreationBoite)
menu.add_command(label="Ouvrir", command=browse)
main.config(menu=menu)

buttonCreer = Button(main, text="Créer une boîte", command=fenCreationBoite)
buttonOuvrir = Button(main, text="Ouvrir une boîte", command=browse)

logo = PhotoImage(file="img/logo_96.png")
labelLogo = Label(main, image=logo, bg="white")
labelVersion = Label(main, text="ZenPassword "+version+"\nJulien Moorat & Juliette Duron", bg="white")
labelLogo.pack()
buttonCreer.pack(pady=8)
buttonOuvrir.pack(pady=8)
labelVersion.pack(side=BOTTOM, pady=8)


main.mainloop()
