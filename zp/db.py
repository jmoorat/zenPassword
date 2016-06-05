import sqlite3
from zp import security as zps

class bddFile:
    def __init__(self, chemin, isNew=False, nom="", hashmdp=""):
        if isNew == True:
            self.bdd = chemin+"/"+nom+".zpdb"
        else:
            self.bdd=chemin
        self.chemin = chemin
        self.connect = sqlite3.connect(self.bdd) #creation de l'objet representant la connexion à la base de données
        self.cur = self.connect.cursor() #curseur qui va stocker temporairement les requêtes avant des les envoyer en bdd par un connect.commit()

        if isNew == True :
            self.cur.execute('CREATE TABLE hash(sha256 TEXT)')
            self.cur.execute("CREATE TABLE boite(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, nom TEXT, identifiant TEXT, motdepasse TEXT, note TEXT)")
            self.connect.commit()

            #Ajout du hash du mot de passe à la base de données
            prepare = (hashmdp,)
            self.cur.execute("INSERT INTO hash(sha256) VALUES(?)", prepare)
            #insertion d'une entrée dans la liste de nos boîtes
            #le ? sera remplacé respectivement par chaque valeur du tuple (dans l'ordre !)

            self.connect.commit() #on écrit les changements dans la bdd
            del hashmdp
            return

    def ajouterEntreeBoite(self, nomEntree, identifiant, mdp, note, cle):
        """Fonction ajoutant une nouvelle entrée à la base de données / boîte"""

        prepareAjout = [(zps.chiffre(nomEntree, cle), zps.chiffre(identifiant, cle), zps.chiffre(mdp, cle), zps.chiffre(note, cle))]
        for tu in prepareAjout:
            self.cur.execute("INSERT INTO boite(nom, identifiant, motdepasse, note) VALUES (?, ?, ?, ?)", tu)
        self.connect.commit() #on écrit les changements dans la bdd
        return True

    def modifEntreeBoite(self, nomEntree, identifiant, mdp, note, cle):
        """Fonction modifiant une entrée existante dans la base de données/ boîte courante"""

        prepareModif = [(zps.chiffre(identifiant, cle), zps.chiffre(mdp, cle), zps.chiffre(note, cle), zps.chiffre(nomEntree, cle))]
        #les champs sont avant le nom de l'entrée car la modif va être demandé avant l'entrée dans la requête SQL
        for tu in prepareModif: #boucle qui va permettre de remplacer chaque données de prepareModif dans la requête (une par une)
            self.cur.execute("UPDATE boite SET identifiant = ?, motdepasse = ?, note = ? WHERE nom = ?", tu)
            self.connect.commit() #on écrit les changements dans la bdd
        return True

    def supprimerEntreeBoite(self, nomEntree, cle):
        """Supprime une entrée de la base de données ("boîte") courante"""

        prepareSuppr = [(zps.chiffre(nomEntree, cle))]
        self.cur.execute("DELETE FROM boite WHERE nom = ?", prepareSuppr)
        self.connect.commit() #on écrit les changements dans la bdd
        return True

    def getId(self, nomEntree, cle):
        """Fonction qui récupère le champ "identifiant" associé au nom d'une entrée dans la base de données ("boîte") courante"""

        prepare = (zps.chiffre(nomEntree, cle),)
        self.cur.execute("SELECT identifiant FROM boite WHERE nom = ?", prepare)
        data = list(self.cur) # On stocke le contenu du curseur dans une liste
        identifiant = zps.dechiffre(data[0][0], cle) # On extrait la données correspondant au mot de passe dans la liste data
        return identifiant

    def getMdp(self, nomEntree, cle):
        """Fonction qui récupère le champ "mot de passe" associé au nom d'une entrée dans la base de données ("boîte") courante"""

        prepare = (zps.chiffre(nomEntree, cle),) #on prépare ce qu'on va intégrer à la requête
        self.cur.execute("SELECT motdepasse FROM boite WHERE nom = ?", prepare)
        data = list(self.cur) # On stocke le contenu du curseur dans une liste
        mdp = zps.dechiffre(data[0][0], cle) # On extrait la données correspondant au mot de passe dans la liste data
        return mdp

    def getNote(self, nomEntree, cle):
        """Fonction qui récupère le champ "note" associée au nom d'une entrée dans la base de données ("boîte") courante"""

        prepare = (zps.chiffre(nomEntree, cle),)
        self.cur.execute("SELECT note FROM boite WHERE nom = ?", prepare)
        data = list(self.cur) # On stocke le contenu du curseur dans une liste
        note = zps.dechiffre(data[0][0], cle) # On extrait la données correspondant au mot de passe dans la liste data
        return note

    def getHash(self):
        self.cur.execute("SELECT sha256 FROM hash")
        data = list(self.cur)
        hashmdp = str(data[0][0]) #premier element du premier tuple -> deux [0] index 00
        return hashmdp

    def getListeNoms(self):
        self.cur.execute("SELECT nom FROM boite")
        data = list(self.cur)
        return data
