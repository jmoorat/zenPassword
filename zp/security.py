import hashlib

alpha = " ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzéèàùâêîôûïöëñ0123456789!\"#$%&£€§'()[]{|}*+,-./\\:;<=>?@~^_"
lenAlpha = len(alpha)

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

def sha512(mdp):
    """Fonction renvoyant une chaîne de caractère comportant la valeur de hachage SHA-512 de la chaîne en entrée"""

    #utilisation du module hashlib pour générer la valeur hashé du mdp
    hash_output = hashlib.sha512(mdp.encode('utf-8')).hexdigest()
    return hash_output

def generateKey(mdp):
    key = sha512(mdp)
    del mdp
    i = 0
    while i < 128:
        key = sha512(key)
        print(key)
        i += 1
    return key
