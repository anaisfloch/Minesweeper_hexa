# -*- coding: utf-8 -*-
"""
Created on Fri Oct 24 09:05:11 2025

@author: afloch
"""

#################################### ADAPTER A HEXAGONAL GRID ###################################

### Imports ###
import sys
import random
import numpy as np
from abc import abstractmethod

### Définition d'une grille de jeu ###

class Grille():
    
    config = {0: ((8, 8), 10), 1: ((16, 16), 40), 2: ((16, 30), 99)}
    
    def __init__(self, difficulte):
        """Initialise la grille de jeu du démineur avec une certaine 
        taille et un nombre de bombes en fonction de la difficulté choisie, 
        et dévoile automatiquement une partie de la grille.
        
        Paramètres
        ---------
        grille : array
            Matrice vide représentant la grille de jeu.
        taille :  tuple
            Longeur et largeur de la grille.
        bombe : int
            Nombre de bombes présentes dans la grille.
        difficulte : int
            Codes de difficulté :
                0 - facile, 8x8, 10 bombes
                1 - moyen, 16x16, 40 bombes
                2 - difficile, 30x16, 99 bombes
        """
        self.difficulte = difficulte
        self.cases_decouvertes = 0
        
        # Choix de config en fonction de la difficulté
        if difficulte not in self.config:
            raise ValueError("Difficulté invalide : choisir 0, 1 ou 2.")
        self.taille, self.bombe = self.config[difficulte]
        self.cases_decouvertes = 0
         
        # Création d'un tableau objet : Grille préalable
        self.grille = [[None for _ in range(self.taille[1])] for _ in range(self.taille[0])]
        
        positions = [(l, c)
                     for l in range(self.taille[0])
                     for c in range(self.taille[1])]
        
        # Création des cases
        for l, c in random.sample(positions, self.bombe):
            self.grille[l][c] = CaseBombe((l, c), self)
            
        
        for l in range(self.taille[0]):
            for c in range(self.taille[1]):
                if self.grille[l][c] is None:
                    self.grille[l][c] = CaseVide((l, c), self)
        
        # Calcul des indices des bombes voisines
        for r in range(self.taille[0]):
            for c in range(self.taille[1]):
                case = self.grille[r][c]
                if isinstance(case, CaseVide):
                    case.nbr_bombes_voisines = case.get_nbr_bomb()

        self.decouverte_initiale()
        self.verifier_victoire()
        
        
    ########## TEST POUR DEFINITION DE LA GRILLE AVEC DECALAGE DES CASES ########    
    def voisins(self, ligne, colonne):
        """Retourne les coordonnées des six voisins hexagonaux."""
        directions = [(-1, 0), (1,0), (-1,1), (0, -1), (-1, 1), (0, 1)]
        voisins = []
        for tmpl, tmpc in directions:
            nl, nc = ligne + tmpl, colonne + tmpc
            # définir la condition d'ajout
            voisins.append((nl, nc))
            return voisins
            
            
                    
    def afficher(self):
        """
        Affiche visuellement les cases de la grille et leur état en temps réel.

        -------
        """
        """for i in range(self.taille[0]):
            ligne = []
            for j in range(self.taille[1]):
                c = self.grille[i,j]
                if c.drapeau == 1 :
                    ligne.append("*")
                elif not c.decouverte:
                    ligne.append("_")
                elif isinstance(c, CaseBombe):
                    ligne.append("BOUM")
                elif isinstance(c, CaseVide) and c.nbr_bombes_voisines > 0:
                    ligne.append(str(c.nbr_bombes_voisines))
                else:
                    ligne.append("0")
            print(" ".join(ligne))
        print()  """
        
            
    def afficher_solution(self):
        """
        Affiche visuellement la solution de la grille.

        -------
        """
        """print("Soluce")
        for i in range(self.taille[0]):
            ligne = []
            for j in range(self.taille[1]):
                c = self.grille[i,j]
                if isinstance(c, CaseBombe):
                    ligne.append("*")
                elif isinstance(c, CaseVide) and (c.nbr_bombes_voisines >= 0):
                    ligne.append(str(c.nbr_bombes_voisines))
                else:
                    ligne.append("?")
            print(" ".join(ligne))
        print() """
    
    def decouverte_initiale(self):
        """
        Initialise la partie en découvrant des cases automatiquement.

        -------
        """
        # Liste des cases vides
        case_vides = [case for ligne in self.grille for case in ligne
                      if isinstance(case, CaseVide)
                      and case.nbr_bombes_voisines == 0]
        if not case_vides:
            case_vides = [case for ligne in self.grille for case in ligne
                          if isinstance(case, CaseVide)]
        if case_vides:
            random.choice(case_vides).decouvrir()
        

    def compter_drapeaux(self):
        pass                     
         
    def verifier_victoire(self):
        """
        Vérifie que toutes les cases vides ne soient pas découvertes.

        -------
        """
        """total_cases = self.taille[0]*self.taille[1]
        if self.cases_decouvertes >= total_cases - self.bombe:
            return self.victoire()
        return False"""
            
    def victoire(self):
        """
        Renvoie un message de victoire suivi de la fermeture du jeu.

        -------
        """
        print("\n Victoire !")
        self.afficher_solution()
        return True           
                
        

### Définition d'une case de jeu ###

class Case():
    
    def __init__(self, position, grille, drapeau = 0):
        """Initialise une case de la grille de jeu du démineur à une position 
        particulière dans une grille.
        
        Paramètres
        ---------
        position : tuple
            Coordonnées de la case dans la grille de jeu.
        grille : array
            Matrice à laquelle la case est rattachée.
        drapeau : int
            Indique la présence ou non d'un drapeau sur la case. Par défaut 
            égal à 0.
        """
        self.drapeau = drapeau
        self.grille = grille
        self.position = position
        self.decouverte = False
    
    @abstractmethod
    def decouvrir(self):
        """
        Révéler la case sélectionnée, sauf si elle présente un drapeau.

        """
        pass
    
    @abstractmethod
    def ajouter_drapeau(self):
        """
        Ajouter un drapeau sur la case sélectionnée ou le retirer si un drapeau est déjà présent.

        """
        pass


class CaseBombe(Case):
    
    def __init__(self, position, grille, drapeau = 0):
        super().__init__(position, grille, drapeau)
        
    def decouvrir(self):
        # Ne peut être découverte si marquée par un drapeau
        if self.drapeau == 1:
            return
        self.decouverte = True
        return
           
            
    def ajouter_drapeau(self):
        self.drapeau = 1 - self.drapeau
        
    
class CaseVide(Case):
    
    def __init__(self, position, grille, drapeau = 0, voisins_calcules = True):
        super().__init__(position, grille, drapeau)
        self.nbr_bombes_voisines = 0 if voisins_calcules else None
        if voisins_calcules:
            self.nbr_bombes_voisines = self.get_nbr_bomb()
        
    def decouvrir(self):
        if self.drapeau == 1 or self.decouverte :
            return
        
        self.decouverte = True
        self.grille.cases_decouvertes += 1
        self.grille.verifier_victoire()
        
        # Au cas-où ça n'a pas marché avant
        if self.nbr_bombes_voisines is None:
            self.nbr_bombes_voisines = self.get_nbr_bomb()
        
        # Si bombes voisines
        if self.nbr_bombes_voisines > 0:
            print(f"Case {self.position} : {self.nbr_bombes_voisines} bombes voisines.")
            return
            
        # Sinon découvrir les cases vides adjointes
        """x, y = self.position
        for i in range(x-1, x+2):
            for j in range(y-1, y+2):
                if (0 <= i < self.grille.taille[0]) and (0 <= j < self.grille.taille[1]) and (i,j) != (x,y):
                    self.grille.grille[i,j].decouvrir()
          """          
        
    
    def ajouter_drapeau(self):
        self.drapeau = 1 - self.drapeau
    
    
    def get_nbr_bomb(self):
        """
        Donne le nombre de bombes présentes dans le voisinage immédiat de la case sélectionnée.

        Returns
        -------
        voisins : int
            Nombre de bombes présentes dans le voisinage immédiat.
        """
        """x, y = self.position
        voisins = 0
        for i in range(x-1, x+2):
            for j in range(y-1, y+2):
                if (0 <= i < self.grille.taille[0]) and (0 <= j < self.grille.taille[1]) and (i,j) != (x,y):
                    if isinstance(self.grille.grille[i,j], CaseBombe):
                        voisins += 1
        return voisins"""
                
    
    
