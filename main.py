# -*- coding: utf-8 -*-
"""
Created on Fri Oct 24 14:14:08 2025

@author: afloch
"""
#################################### ADAPTER A HEXAGONAL GRID ###################################
from grille_hexa import Grille

def jouer():
    """
    Permet de lancer une partie de Minesweeper.
    -------
    """
    print(" ====== MINESWEEPER ====== ")
    print("Difficultés : 0 => facile (10 bombes), 1 => moyen (40 bombes), 2 => difficile (99 bombes)")
    
    # Choix de la difficulté pour le joueur
    while True:
        try:
            difficulte = int(input("Choisissez la difficulté :"))
            if difficulte in [0,1,2]:
                break
            else:
                print("Le code de difficulté doit être de 0 (facile), 1 (moyen) ou 2 (difficile).")
        except ValueError:
            print("Tu fais n'importe quoi recommence.")
    
    # Génération de la grille et affichage de la solution
    g = Grille(difficulte)
    #g.afficher_solution()
    
    # Actions du joueur
    while True: 
        g.afficher()
        action = input("Action (r = révéler, d = drapeau, q = quitter) : ")
        if action == 'q':
            print("Adieu.")
            break
        try:
            x = int(input("Ligne : "))
            y = int(input("Colonne : "))
        except ValueError:
            print("Entrée invalide, recommence avec des nombres.")
            
        case = g.grille[x,y]
        
        if action == "r":
            case.decouvrir()
        elif action == "d":
            case.ajouter_drapeau()
        else:
            print("Action inalide.")
        
if __name__ == "__main__":
    jouer()
