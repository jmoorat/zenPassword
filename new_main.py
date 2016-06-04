from tkinter import *
from tkinter.messagebox import *
from tkinter.filedialog import *
from zp_bdd import *
from zp_security import *

version = "v0.1"

class gui:
    def __init__(self):
        self.main = Tk()
        self.main.title("ZenPassword "+version)
        self.main['bg']="white"

        self.menu = Menu(self.main)
        self.menu.add_command(label="Créer", command=self.fenCreationBoite)
        self.menu.add_command(label="Ouvrir", command=self.browse)
        self.main.config(menu=self.menu)

        self.buttonCreer = Button(self.main, text="Créer une boîte", command=self.fenCreationBoite)
        self.buttonOuvrir = Button(self.main, text="Ouvrir une boîte", command=self.browse)

        self.logo = PhotoImage(file="img/logo_96.png")
        self.labelLogo = Label(self.main, image=self.logo, bg="white")
        self.labelVersion = Label(self.main, text="ZenPassword "+version+"\nby Julien Moorat", bg="white")
        self.labelLogo.pack()
        self.buttonCreer.pack(pady=8)
        self.buttonOuvrir.pack(pady=8)
        self.labelVersion.pack(side=BOTTOM, pady=8)

        self.main.mainloop()

    def browse(self):
        """Ouvre une fenêtre permettant de sélectionner le chemin du fichier à ouvrir"""
        self.chemin = ""
        self.chemin = askopenfilename(title="Ouvrir une boîte",filetypes=[('Fichiers ZenPassword','.zpdb'),('Tous les fichiers','.*')])
        if self.chemin == "":
            return
        else:
            self.unlock(self.chemin)

    def unlock(self, chemin):
        """Fenêtre d'authentification (demande du mot de passe de la boîte)"""
        self.fichier = bddFile(chemin)

        #Elements de la fenêtre
        self.fenUnlock = Toplevel()
        self.fenUnlock.title("Déverrouillage")
        self.cadenas = PhotoImage(file="img/cadenas_64.png")
        self.labelCadenas = Label(self.fenUnlock, image=self.cadenas)
        mdp = StringVar()
        self.labelMdp = Label(self.fenUnlock, text="Mot de passe")
        self.champMdp = Entry(self.fenUnlock, textvariable=mdp, show="●") #show="●" va permettre de masquer ce qu'écrit l'utilisateur
        self.champMdp.focus_set()
        self.buttonValider = Button(self.fenUnlock, text="Valider", command=lambda:self.verifMdp(mdp.get()))

        #Positionnement des éléments de la fenêtre
        self.labelCadenas.pack()
        self.labelMdp.pack(side=LEFT, padx=5, pady=5)
        self.champMdp.pack(side=LEFT, padx=5, pady=5)
        self.buttonValider.pack(side=LEFT, padx=5, pady=5)

        self.fenUnlock.mainloop()
        return

    def verifMdp(self, mdp):
        """Vérification du mot de passe par comparaison des valeurs de hachages en
        SHA-256"""

        #On vérifie que la valeur hashée du mot de passe correspond à celle stockée en base de données
        if zps.sha256(mdp) == self.fichier.getHash(): #Correspondance -> on ouvre la boite
            self.cle = mdp
            mdp = None
            del mdp
            self.fenUnlock.destroy()
            return self.boite()
        else: #Erreur > on ouvre pas la boite
            self.alerte = showerror("Mot de passe incorrect", "Accès refusé")
            return

    def fenCreationBoite(self):
        """Fenêtre permettant la création d'une nouvelle boîte"""

        #Elements de la fenêtre
        self.fenCreationBoite = Toplevel()
        self.fenCreationBoite.title("Créer une boîte")
        self.fenCreationBoite.geometry("220x200")
        nomBoite = StringVar()
        mdpBoite = StringVar()
        cheminBoite = StringVar()
        self.labelNom = Label(self.fenCreationBoite, text="Nom de la boîte : ")
        self.labelMdp = Label(self.fenCreationBoite, text="Mot de passe principal : ")
        self.entryNom = Entry(self.fenCreationBoite, textvariable=nomBoite)
        self.entryMdp = Entry(self.fenCreationBoite, textvariable=mdpBoite, show="●")
        self.buttonChemin = Button(self.fenCreationBoite, text="Choisir un répertoire", command=lambda:cheminBoite.set(askdirectory()))
        self.buttonValider = Button(self.fenCreationBoite, text="Valider", command=lambda:self.verifCreationBoite(nomBoite.get(), mdpBoite.get(), cheminBoite.get()))
        self.buttonQuitter = Button(self.fenCreationBoite, text="Quitter", command=self.fenCreationBoite.destroy)

        #Positionnement des éléments
        self.labelNom.pack(pady=1)
        self.entryNom.pack(pady=2)
        self.labelMdp.pack(pady=1)
        self.entryMdp.pack(pady=2)
        self.buttonChemin.pack(pady=2)
        self.buttonValider.pack(side=LEFT, pady=5, padx=5)
        self.buttonQuitter.pack(side=RIGHT, pady=5, padx=5)

        self.fenCreationBoite.mainloop()

    def verifCreationBoite(self, nomBoite, mdpBoite, cheminBoite):
        """Fonction vérifiant les données rentrées dans fenCreationBoite avant création d'une boîte"""
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
                fichier = bddFile(cheminBoite, True, nomBoite, zps.sha256(mdpBoite))
                mdpBoite = None
                del mdpBoite, nomBoite, cheminBoite, fichier
                info = showinfo("Boîte créée", "La boîte a bien été créée")
                self.fenCreationBoite.destroy()
                return
            else:
                return

    def boite(self):
        """Fenêtre principale de la boîte"""

        #Definition de la fenêtre
        self.fenBoite = Toplevel()
        self.fenBoite.title(self.fichier.chemin)
        self.fenBoite.geometry("300x175")

        #Définition de la liste des entrées
        self.listeNom = Listbox(self.fenBoite)
        noms = self.fichier.getListeNoms()
        i = 0
        for elements in noms:
            self.listeNom.insert(END, zps.dechiffre(noms[i][0], self.cle)) #on utilise i+1 pour la correspondance avec les id des entrées
            i += 1
        self.listeNom.select_set(0) #On sélectionne par défaut la première entrée de la liste

        buttonVoir = Button(self.fenBoite, text="Voir l'entrée", command=lambda:self.afficheEntree(self.listeNom.get(self.listeNom.curselection()[0])))
        buttonFermerBoite = Button(self.fenBoite, text="Fermer la boîte", command=self.fermerBoite)

        #Définition du menu
        menuBoite = Menu(self.fenBoite)
        menuEntrees = Menu(menuBoite, tearoff=0)
        menuEntrees.add_command(label="Voir l'entrée sélectionnée", command=lambda:self.afficheEntree(self.listeNom.get(self.listeNom.curselection()[0])))
        menuEntrees.add_command(label="Ajouter une entrée", command=self.fenAjoutEntreeBoite)
        menuEntrees.add_command(label="Modifier une entrée", command=lambda:self.fenModifEntreeBoite(self.listeNom.get(self.listeNom.curselection()[0])))
        menuEntrees.add_command(label="Supprimer l'entrée sélectionnée", command=lambda:self.supprimerEntreeBoite(self.listeNom.get(self.listeNom.curselection()[0])))
        menuBoite.add_cascade(label="Entrées", menu=menuEntrees)
        menuBoite.add_command(label="Fermer la boîte", command=self.fermerBoite)
        self.fenBoite.config(menu=menuBoite)
        #listeNom.get(listeNom.curselection()[0]) permet de récupérer le contenu de l'élément de la liste sélectionné

        #Positionnement des éléments
        self.listeNom.pack(side=LEFT)
        buttonVoir.pack(side=RIGHT, padx=25)

        self.fenBoite.mainloop()

        return self.fermerBoite()

    def fenAjoutEntreeBoite(self):
        """Fonction créant la fenêtre d'ajout d'entrée à une boîte"""

        #Définition de la fenêtre et ses éléments
        self.fenAjout = Toplevel()
        self.fenAjout.title("Ajouter une entrée")
        entreeNom = StringVar()
        entreeId = StringVar()
        entreeMdp = StringVar()
        entreeNote = StringVar()

        labelNom = Label(self.fenAjout, text="Nom de l'entrée : ")
        labelId = Label(self.fenAjout, text="Identifiant : ")
        labelMdp = Label(self.fenAjout, text="Mot de passe : ")
        labelNote = Label(self.fenAjout, text="Note/Commentaire : ")
        entryNom = Entry(self.fenAjout, textvariable=entreeNom)
        entryId = Entry(self.fenAjout, textvariable=entreeId)
        entryMdp = Entry(self.fenAjout, textvariable=entreeMdp)
        entryNote = Entry(self.fenAjout, textvariable=entreeNote)
        buttonValider = Button(self.fenAjout, text="Valider", command=lambda:self.verifAjoutEntreeBoite(entreeNom.get(), entreeId.get(), entreeMdp.get(), entreeNote.get()))

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

        self.fenAjout.mainloop()
        return

    def fenModifEntreeBoite(self, nomEntree):
        """Fenêtre de modification de l'entrée sélectionnée"""

        #Définition de la fenêtre et de ses éléments
        self.fenModif = Toplevel()
        entreeId = StringVar()
        entreeMdp = StringVar()
        entreeNote = StringVar()
        entreeId.set(self.fichier.getId(nomEntree, self.cle))
        entreeMdp.set(self.fichier.getMdp(nomEntree, self.cle))
        entreeNote.set(self.fichier.getNote(nomEntree, self.cle))

        labelId = Label(self.fenModif, text="Identifiant : ")
        labelMdp = Label(self.fenModif, text="Mot de passe : ")
        labelNote = Label(self.fenModif, text="Note : ")

        entryId = Entry(self.fenModif, textvariable=entreeId)
        entryMdp = Entry(self.fenModif, textvariable=entreeMdp)
        entryNote = Entry(self.fenModif, textvariable=entreeNote)

        buttonValider = Button(self.fenModif, text="Valider", command=lambda:self.verifModifEntreeBoite(nomEntree, entreeId.get(), entreeMdp.get(), entreeNote.get()))
        buttonAnnuler = Button(self.fenModif, text="Annuler", command=self.fenModif.destroy)

        #Positionnement des éléments
        labelId.pack(pady=1, padx=2)
        entryId.pack(pady=1, padx=2)
        labelMdp.pack(pady=1, padx=2)
        entryMdp.pack(pady=1, padx=2)
        labelNote.pack(pady=1, padx=2)
        entryNote.pack(pady=1, padx=2)
        buttonValider.pack(pady=1, padx=2)
        buttonAnnuler.pack(pady=1, padx=2)

        self.fenModif.mainloop()
        return

    def afficheEntree(self, nomEntree):
        """Fenêtre d'affichage de l'entrée sélectionnée"""

        #Définition de la fenêtre et de ses éléments
        self.fenEntree = Toplevel()
        self.fenEntree.title(nomEntree)
        self.fenEntree.geometry("200x250")
        labelId = Label(self.fenEntree, text="Identifiant : ")
        labelMdp = Label(self.fenEntree, text="Mot de passe : ")
        labelNote = Label(self.fenEntree, text="Note : ")

        labelGetId = Label(self.fenEntree, text=self.fichier.getId(nomEntree, self.cle))
        labelGetMdp = Label(self.fenEntree, text=self.fichier.getMdp(nomEntree, self.cle))
        labelGetNote = Label(self.fenEntree, text=self.fichier.getNote(nomEntree, self.cle))

        #Positionnement des éléments
        labelId.pack()
        labelGetId.pack()
        labelMdp.pack()
        labelGetMdp.pack()
        labelNote.pack()
        labelGetNote.pack()

    def fermerBoite(self):
        """Fonction permettant de fermer correctement une boîte en effaçant toutes
        les variables globales liées à la boîte ouverte dont la clé de zps.chiffrement"""
        del self.fichier
        del self.cle
        self.fenBoite.destroy()
        return

    def verifAjoutEntreeBoite(self, nom, identifiant, mdp, note):
        """Fonction de vérification avant la création d'une nouvelle entrée"""
        #accès à listeNom définie en globale dans boite pour l'ajout automatique de la nouvelle entrée

        if nom == "":
            error = showerror("Erreur", "Vous devez spécifier un nom pour l'entrée")
            self.fenBoite.focus_set() #garde la fenêtre boite au dessus des autres
            return
        elif self.fichier.ajouterEntreeBoite(nom, identifiant, mdp, note, self.cle) == True:
            self.listeNom.insert(END, nom) #*
            self.fenAjout.destroy()
            del self.fenAjout, nom, identifiant, mdp, note
            self.fenBoite.focus_set() #garde la fenêtre boite au dessus des autres
            return

    def verifModifEntreeBoite(self, nom, identifiant, mdp, note):
        """Vérification de la modification d'une boite"""

        if self.fichier.modifEntreeBoite(nom, identifiant, mdp, note, self.cle) == True:
            info = showinfo("Entrée modifiée", "L'entrée a bien été modifiée.")
            self.fenModif.destroy()
            del self.fenModif, nom, identifiant, mdp, note
            self.fenBoite.focus_set() #garde la fenêtre boite au dessus des autres
            return

application = gui()
