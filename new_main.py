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
        self.menu.add_command(label="Créer")
        self.menu.add_command(label="Ouvrir", command=self.browse)
        self.main.config(menu=self.menu)

        self.buttonCreer = Button(self.main, text="Créer une boîte")
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
        self.chemin = askopenfilename(title="Ouvrir une boîte",filetypes=[('Fichiers SPDB','.spdb'),('Tous les fichiers','.*')])
        if self.chemin == "":
            return
        else:
            self.unlock(self.chemin)

    def unlock(self, chemin):
        """Fenêtre d'authentification (demande du mot de passe de la boîte)"""

        fichier = bddFile(chemin)

        #Elements de la fenêtre
        self.fenUnlock = Toplevel()
        self.fenUnlock.title("Déverrouillage")
        self.cadenas = PhotoImage(file="img/cadenas_64.png")
        self.labelCadenas = Label(self.fenUnlock, image=self.cadenas)
        self.mdp = StringVar()
        self.labelMdp = Label(self.fenUnlock, text="Mot de passe")
        self.champMdp = Entry(self.fenUnlock, textvariable=self.mdp, show="●") #show="●" va permettre de masquer ce qu'écrit l'utilisateur
        self.champMdp.focus_set()
        self.buttonValider = Button(self.fenUnlock, text="Valider", command=lambda:self.verifMdp(mdp.get(), hash_mdp_bdd))

        #Positionnement des éléments de la fenêtre
        self.labelCadenas.pack()
        self.labelMdp.pack(side=LEFT, padx=5, pady=5)
        self.champMdp.pack(side=LEFT, padx=5, pady=5)
        self.buttonValider.pack(side=LEFT, padx=5, pady=5)

        self.fenUnlock.mainloop()
        return



application = gui()
