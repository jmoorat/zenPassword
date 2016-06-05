import random

def gen(lowerCase, upperCase, digits, special, space, lenghtMdp):
    charList = ""
    i=0
    mdp = ""
    if lowerCase == 1:
        charList += lowerCaseList
    if upperCase == 1:
        charList += upperCaseList
    if digits == 1:
        charList += digitsList
    if special == 1:
        charList += specialList
    if space == 1:
        charList += spaceList

    while i < lenghtMdp:
        mdp += charList[random.randint(0, len(charList)-1)]
        i += 1
    return mdp



lowerCaseList = "abcdefghijklmnopqrstuvwxyz"
upperCaseList = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
digitsList = "0123456789"
specialList = "!\"#$%&£€§'()[]{|}*+,-./\\:;<=>?@~^_"
spaceList = " "
