#coding : utf-8
from tkinter import *
from tkinter.messagebox import *
from tkinter.filedialog import *
import os

#Importation modules persos
from zp.db import *
from zp.security import *
import zp.pyperclip as clipboard
import zp.generator as passgen

version = "v0.3a"

class gui:
    def __init__(self):
        self.main = Tk()
        self.main.title("ZenPassword "+version)
        self.main['bg']="white"

        menu = Menu(self.main)
        menu.add_command(label="Create", command=self.fenCreationBoite)
        menu.add_command(label="Open", command=self.browse)
        self.main.config(menu=menu)

        buttonCreer = Button(
            self.main,
            text="Create a database",
            command=self.fenCreationBoite,
            background="#60bb87",
            foreground="white",
            activebackground="#518c5e",
            activeforeground="white",
            relief=FLAT,
            width="16")
        buttonOuvrir = Button(
            self.main,
            text="Open a database",
            command=self.browse,
            background="#60bb87",
            foreground="white",
            activebackground="#518c5e",
            activeforeground="white",
            relief=FLAT,
            width="16")

        logo = PhotoImage(file="img/logo_96.png")
        labelLogo = Label(self.main, image=logo, bg="white")
        labelVersion = Label(self.main, text="ZenPassword "+version+"\nby Julien Moorat", bg="white")
        labelLogo.pack()
        buttonCreer.pack(pady=8)
        buttonOuvrir.pack(pady=8)
        labelVersion.pack(side=BOTTOM, pady=8)

        self.main.mainloop()

    def browse(self):
        """Ouvre une fenêtre permettant de sélectionner le chemin du fichier à ouvrir"""
        self.chemin = ""
        self.chemin = askopenfilename(title="Open a database",filetypes=[('ZenPassword files','.zpdb'),('All files','.*')])
        if self.chemin == "":
            return
        else:
            self.unlock(self.chemin)

    def unlock(self, chemin):
        """Fenêtre d'authentification (demande du mot de passe de la boîte)"""
        self.fichier = bddFile(chemin) #On initialise notre le fichier

        #Elements de la fenêtre
        self.fenUnlock = Toplevel()
        self.fenUnlock.title("Unlock database")
        self.fenUnlock.geometry("300x128")
        cadenas = PhotoImage(file="img/cadenas_64.png")
        labelCadenas = Label(self.fenUnlock, image=cadenas)
        mdp = StringVar()
        labelMdp = Label(self.fenUnlock, text="Main password")
        champMdp = Entry(self.fenUnlock, textvariable=mdp, show="●") #show="●" va permettre de masquer ce qu'écrit l'utilisateur
        champMdp.focus_set()
        buttonValider = Button(self.fenUnlock, text="Ok", command=lambda:self.verifMdp(mdp.get()))

        #Positionnement des éléments de la fenêtre
        labelCadenas.pack()
        labelMdp.pack(side=LEFT, padx=5, pady=5)
        champMdp.pack(side=LEFT, padx=5, pady=5)
        buttonValider.pack(side=LEFT, padx=5, pady=5)

        self.fenUnlock.mainloop()
        return

    def verifMdp(self, mdp):
        """Vérification du mot de passe par comparaison des valeurs de hachages en
        SHA-256"""

        #On vérifie que la valeur hashée du mot de passe correspond à celle stockée en base de données
        if sha256(mdp) == self.fichier.getHash(): #Correspondance -> on ouvre la boite
            self.cle = mdp
            mdp = None
            del mdp
            self.fenUnlock.destroy()
            return self.boite()
        else: #Erreur > on ouvre pas la boite
            self.alerte = showerror("Wrong password", "Access refused")
            self.fenUnlock.focus()
            return

    def fenCreationBoite(self):
        """Fenêtre permettant la création d'une nouvelle boîte"""

        #Elements de la fenêtre
        self.fenCreation = Toplevel()
        self.fenCreation.title("Create a database")
        self.fenCreation.geometry("220x230")
        nomBoite = StringVar()
        mdpBoite = StringVar()
        cheminBoite = StringVar()
        labelNom = Label(self.fenCreation, text="Name : ")
        labelMdp = Label(self.fenCreation, text="Main password : ")
        labelChemin = Label(self.fenCreation, text="Path to your file : ")
        entryNom = Entry(self.fenCreation, textvariable=nomBoite)
        entryMdp = Entry(self.fenCreation, textvariable=mdpBoite, show="●")
        entryChemin = Entry(self.fenCreation, textvariable=cheminBoite)
        buttonChemin = Button(self.fenCreation, text="Explore", command=lambda:cheminBoite.set(askdirectory()))
        buttonValider = Button(self.fenCreation, text="Ok", command=lambda:self.verifCreationBoite(nomBoite.get(), mdpBoite.get(), cheminBoite.get()))
        buttonQuitter = Button(self.fenCreation, text="Quit", command=self.fenCreation.destroy)

        #Positionnement des éléments
        labelNom.pack(pady=1)
        entryNom.pack(pady=2)
        labelMdp.pack(pady=1)
        entryMdp.pack(pady=2)
        labelChemin.pack(pady=1)
        entryChemin.pack(pady=2)
        buttonChemin.pack(pady=2)
        buttonValider.pack(side=LEFT, pady=5, padx=5)
        buttonQuitter.pack(side=RIGHT, pady=5, padx=5)

        self.fenCreationBoite.mainloop()

    def verifCreationBoite(self, nomBoite, mdpBoite, cheminBoite):
        """Fonction vérifiant les données rentrées dans fenCreationBoite avant création d'une boîte"""
        if nomBoite == "":
            showwarning("No name specified", "Please set a name for your file")
            self.fenCreation.focus()
            return
        elif len(mdpBoite) < 8:
            showwarning("Main password too short", "Your main password must be 8 characters long")
            self.fenCreation.focus()
            return
        elif os.path.isfile(cheminBoite+"/"+nomBoite+".spdb") == True:
            showerror("Error", "A file with the same name already exist !")
            self.fenCreation.focus()
            return
        elif cheminBoite == "":
            showerror("No path specified", "Please choose a path for your file")
            self.fenCreation.focus()

        else:
            question = askquestion("Confirmation", "Database \"" + nomBoite +
            "\" will be created in "+cheminBoite)

            if question == "yes":
                fichier = bddFile(cheminBoite, True, nomBoite, zps.sha256(mdpBoite))
                mdpBoite = None
                del mdpBoite, nomBoite, cheminBoite, fichier
                showinfo("Database created", "Operation successful")
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

        buttonVoir = Button(self.fenBoite, text="Display entry", command=lambda:self.afficheEntree(self.listeNom.get(self.listeNom.curselection()[0])))
        buttonFermerBoite = Button(self.fenBoite, text="Close database", command=self.fermerBoite)

        #Définition du menu
        menuBoite = Menu(self.fenBoite)
        menuEntrees = Menu(menuBoite, tearoff=0)
        menuEntrees.add_command(label="Display selected entry", command=lambda:self.afficheEntree(self.listeNom.get(self.listeNom.curselection()[0])))
        menuEntrees.add_command(label="Add an entry", command=self.fenAjoutEntreeBoite)
        menuEntrees.add_command(label="Edit selected entry", command=lambda:self.fenModifEntreeBoite(self.listeNom.get(self.listeNom.curselection()[0])))
        menuEntrees.add_command(label="Delete selected entry", command=lambda:self.supprEntree(self.listeNom.get(self.listeNom.curselection()[0])))
        menuBoite.add_cascade(label="Entries", menu=menuEntrees)
        menuBoite.add_command(label="Close database", command=self.fermerBoite)
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
        self.fenAjout.title("Add an entry")
        entreeNom = StringVar()
        entreeId = StringVar()
        self.entreeMdp = StringVar() #self pour accès depuis le générateur
        entreeNote = StringVar()

        labelNom = Label(self.fenAjout, text="Name : ")
        labelId = Label(self.fenAjout, text="Login : ")
        labelMdp = Label(self.fenAjout, text="Password : ")
        labelNote = Label(self.fenAjout, text="Comment : ")
        entryNom = Entry(self.fenAjout, textvariable=entreeNom)
        entryId = Entry(self.fenAjout, textvariable=entreeId)
        entryMdp = Entry(self.fenAjout, textvariable=self.entreeMdp)
        entryNote = Entry(self.fenAjout, textvariable=entreeNote)
        buttonValider = Button(self.fenAjout, text="Ok", command=lambda:self.verifAjoutEntreeBoite(entreeNom.get(), entreeId.get(), self.entreeMdp.get(), entreeNote.get()))
        buttonGenerer = Button(self.fenAjout, text="Password generator", command=self.fenGenerator)

        #Positionnement des éléments
        labelNom.grid(row=1, column=1)
        entryNom.grid(row=2, column=1)
        labelId.grid(row=3, column=1)
        entryId.grid(row=4, column=1)
        labelMdp.grid(row=5, column=1)
        entryMdp.grid(row=6, column=1)
        labelNote.grid(row=7, column=1)
        entryNote.grid(row=8, column=1)
        buttonValider.grid(row=4, column=2)
        buttonGenerer.grid(row=5, column=2)

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

        labelId = Label(self.fenModif, text="Login : ")
        labelMdp = Label(self.fenModif, text="Password : ")
        labelNote = Label(self.fenModif, text="Comment : ")

        entryId = Entry(self.fenModif, textvariable=entreeId)
        entryMdp = Entry(self.fenModif, textvariable=entreeMdp)
        entryNote = Entry(self.fenModif, textvariable=entreeNote)

        buttonValider = Button(self.fenModif, text="Ok", command=lambda:self.verifModifEntreeBoite(nomEntree, entreeId.get(), entreeMdp.get(), entreeNote.get()))
        buttonAnnuler = Button(self.fenModif, text="Cancel", command=self.fenModif.destroy)

        #Positionnement des éléments
        labelId.pack(side=LEFT, pady=1, padx=2)
        entryId.pack(side=LEFT, pady=1, padx=2)
        labelMdp.pack(side=LEFT, pady=1, padx=2)
        entryMdp.pack(side=LEFT, pady=1, padx=2)
        labelNote.pack(side=LEFT, pady=1, padx=2)
        entryNote.pack(side=LEFT, pady=1, padx=2)
        buttonValider.pack(side=RIGHT, pady=1, padx=2)
        buttonAnnuler.pack(side=RIGHT, pady=1, padx=2)

        self.fenModif.mainloop()
        return

    def afficheEntree(self, nomEntree):
        """Fenêtre d'affichage de l'entrée sélectionnée"""

        #Définition de la fenêtre et de ses éléments
        self.fenEntree = Toplevel()
        self.fenEntree.title(nomEntree)
        self.fenEntree.geometry("200x250")
        labelId = Label(self.fenEntree, text="Login : ")
        labelMdp = Label(self.fenEntree, text="Password : ")
        labelNote = Label(self.fenEntree, text="Comment : ")

        labelGetId = Label(self.fenEntree, text=self.fichier.getId(nomEntree, self.cle))
        labelGetMdp = Label(self.fenEntree, text=self.fichier.getMdp(nomEntree, self.cle))
        labelGetNote = Label(self.fenEntree, text=self.fichier.getNote(nomEntree, self.cle))

        buttonCopyId = Button(self.fenEntree, text="Copy login", command=lambda:clipboard.copy(str(self.fichier.getId(nomEntree, self.cle))))
        buttonCopyMdp = Button(self.fenEntree, text="Copy password", command=lambda:clipboard.copy(str(self.fichier.getMdp(nomEntree, self.cle))))

        #Positionnement des éléments
        labelId.pack()
        labelGetId.pack()
        labelMdp.pack()
        labelGetMdp.pack()
        labelNote.pack()
        labelGetNote.pack()
        buttonCopyId.pack()
        buttonCopyMdp.pack()
        return

    def supprEntree(self, nomEntree):
        self.fichier.supprimerEntreeBoite(nomEntree, self.cle)
        self.listeNom.delete(self.listeNom.curselection())
        self.fenBoite.focus_set()

    def fenGenerator(self):
        self.fenGen = Toplevel()
        self.fenGen.title("ZenPassword Generator")

        self.pass_generated = StringVar()

        entree = Entry(self.fenGen, textvariable=self.pass_generated, width=30)
        entree.pack()

        lenght = Spinbox(self.fenGen, from_=1, to=8)
        lenght.pack()

        var_lowerCase = IntVar()
        var_lowerCase.set(1)
        lowerCase = Checkbutton(self.fenGen, text="Lower case", variable=var_lowerCase)
        lowerCase.pack()

        var_upperCase = IntVar()
        upperCase = Checkbutton(self.fenGen, text="Upper case", variable=var_upperCase)
        upperCase.pack()

        var_digits = IntVar()
        digits = Checkbutton(self.fenGen, text="Digits", variable=var_digits)
        digits.pack()

        var_special = IntVar()
        special = Checkbutton(self.fenGen, text="Special", variable=var_special)
        special.pack()

        var_space = IntVar()
        space = Checkbutton(self.fenGen, text="Space", variable=var_space)
        space.pack()


        bGenerate = Button(self.fenGen, text="Generate",
        command=lambda:self.generator(
        var_lowerCase.get(),
        var_upperCase.get(),
        var_digits.get(),
        var_special.get(),
        var_space.get(),
        int(lenght.get())))

        bGenerate.pack()

        bCopy = Button(self.fenGen, text="OK", command=self.setPasswordGenerated)
        bCopy.pack()

        self.fenGen.mainloop()
        return delPassGenerated()

    def setPasswordGenerated(self):
        self.entreeMdp.set(self.pass_generated.get())
        self.fenGen.destroy()
        del self.pass_generated
        self.fenAjout.focus()
        return
    def generator(self, lowercase, uppercase, digits, special, space, lenght):
        if lowercase==0 and uppercase==0 and digits==0 and special==0 and space==0:
            error = showerror("No parameter", "Please select at least 1 parameter to generate a password")
        else:
            self.pass_generated.set(passgen.gen(lowercase, uppercase, digits, special, space, lenght))

    def fermerBoite(self):
        """Fonction permettant de fermer correctement une boîte en effaçant toutes
        les variables globales liées à la boîte ouverte dont la clé de zps.chiffrement"""
        del self.fichier
        del self.cle
        self.fenBoite.destroy()
        self.main.focus()
        return

    def verifAjoutEntreeBoite(self, nom, identifiant, mdp, note):
        """Fonction de vérification avant la création d'une nouvelle entrée"""
        #accès à listeNom définie en globale dans boite pour l'ajout automatique de la nouvelle entrée

        if nom == "":
            error = showerror("Error", "Please specifiy a name for your entry")
            self.fenAjout.focus() #garde la fenêtre boite au dessus des autres
            return
        elif self.fichier.ajouterEntreeBoite(nom, identifiant, mdp, note, self.cle) == True:
            self.listeNom.insert(END, nom) #*
            self.fenAjout.destroy()
            del self.fenAjout, nom, identifiant, mdp, note
            self.fenBoite.focus() #garde la fenêtre boite au dessus des autres
            return

    def verifModifEntreeBoite(self, nom, identifiant, mdp, note):
        """Vérification de la modification d'une boite"""

        if self.fichier.modifEntreeBoite(nom, identifiant, mdp, note, self.cle) == True:
            info = showinfo("Entry changed", "Entry successfully changed")
            self.fenModif.destroy()
            del self.fenModif, nom, identifiant, mdp, note
            self.fenModif.focus() #garde la fenêtre boite au dessus des autres
            return

application = gui()
