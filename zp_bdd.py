import sqlite3
import zp_security as zps

class bddFile:
    def __init__(self, chemin, isNew=False, nom="", hashmdp=""):
        self.bdd = chemin
        self.cheminBoite = chemin
        self.connect = sqlite3.connect(self.bdd) #creation de l'objet representant la connexion à la base de données
        self.cur = self.connect.cursor() #curseur qui va stocker temporairement les requêtes avant des les envoyer en bdd par un connect.commit()

        if isNew == True :
            self.cur.execute('CREATE TABLE hash(zps.sha256 TEXT)')
            self.cur.execute("CREATE TABLE boite(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, nom TEXT, identifiant TEXT, motdepasse TEXT, note TEXT)")
            self.connect.commit()

            #Ajout du hash du mot de passe à la base de données
            prepare = (hashmdp,)
            self.cur.execute("INSERT INTO hash(zps.sha256) VALUES(?)", prepare)
            #insertion d'une entrée dans la liste de nos boîtes
            #le ? sera remplacé respectivement par chaque valeur du tuple (dans l'ordre !)

            self.connect.commit() #on écrit les changements dans la bdd
            del hashmdp
            return
        else:
            self.cur.execute("SELECT sha256 FROM hash")
            data = list(self.cur)
            self.hash_mdp_bdd = str(data[0][0]) #premier element du premier tuple -> deux [0] index 00

    def ajouterEntreeBoite(nomEntree, identifiant, mdp, note):
        """Fonction ajoutant une nouvelle entrée à la base de données / boîte"""

        prepareAjout = [(zps.chiffre(nomEntree, cle), zps.chiffre(identifiant, cle), zps.chiffre(mdp, cle), zps.chiffre(note, cle))]
        for tu in prepareAjout:
            self.cur.execute("INSERT INTO boite(nom, identifiant, motdepasse, note) VALUES (?, ?, ?, ?)", tu)
        self.connect.commit() #on écrit les changements dans la bdd
        return True

    def modifEntreeBoite(nomEntree, identifiant, mdp, note):
        """Fonction modifiant une entrée existante dans la base de données/ boîte courante"""

        prepareModif = [(zps.chiffre(identifiant, cle), zps.chiffre(mdp, cle), zps.chiffre(note, cle), zps.chiffre(nomEntree, cle))]
        #les champs sont avant le nom de l'entrée car la modif va être demandé avant l'entrée dans la requête SQL
        for tu in prepareModif: #boucle qui va permettre de remplacer chaque données de prepareModif dans la requête (une par une)
            self.cur.execute("UPDATE boite SET identifiant = ?, motdepasse = ?, note = ? WHERE nom = ?", tu)
            self.connect.commit() #on écrit les changements dans la bdd
        return True

    def supprimerEntreeBoite(nomEntree):
        """Supprime une entrée de la base de données ("boîte") courante"""

        prepareSuppr = [(zps.chiffre(nomEntree, cle))]
        self.cur.execute("DELETE FROM boite WHERE nom = ?", prepareSuppr)
        self.connect.commit() #on écrit les changements dans la bdd
        application.listeNom.delete(listeNom.curselection()) #A transferer dans main si nécessaire !
        application.fenBoite.focus_set() #A transferer dans main si nécessaire !
        return True

    def getId(nomEntree):
        """Fonction qui récupère le champ "identifiant" associé au nom d'une entrée dans la base de données ("boîte") courante"""

        prepare = (zps.chiffre(nomEntree, cle),)
        self.cur.execute("SELECT identifiant FROM boite WHERE nom = ?", prepare)
        data = list(self.cur) # On stocke le contenu du curseur dans une liste
        identifiant = zps.dechiffre(data[0][0], cle) # On extrait la données correspondant au mot de passe dans la liste data
        return identifiant

    def getMdp(nomEntree):
        """Fonction qui récupère le champ "mot de passe" associé au nom d'une entrée dans la base de données ("boîte") courante"""

        prepare = (zps.chiffre(nomEntree, cle),) #on prépare ce qu'on va intégrer à la requête
        self.cur.execute("SELECT motdepasse FROM boite WHERE nom = ?", prepare)
        data = list(self.cur) # On stocke le contenu du curseur dans une liste
        mdp = zps.dechiffre(data[0][0], cle) # On extrait la données correspondant au mot de passe dans la liste data
        return mdp

    def getNote(nomEntree):
        """Fonction qui récupère le champ "note" associée au nom d'une entrée dans la base de données ("boîte") courante"""

        prepare = (zps.chiffre(nomEntree, cle),)
        self.cur.execute("SELECT note FROM boite WHERE nom = ?", prepare)
        data = list(self.cur) # On stocke le contenu du curseur dans une liste
        note = zps.dechiffre(data[0][0], cle) # On extrait la données correspondant au mot de passe dans la liste data
        return note
