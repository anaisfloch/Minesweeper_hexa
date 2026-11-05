# -*- coding: utf-8 -*-
"""
Created on Fri Oct 24 09:05:11 2025

@author: afloch
"""

### Imports ###
import random
from abc import abstractmethod

### Définition d'une grille de jeu ###

class Grille():
    
    config = {0: ((8, 8), 10), 1: ((16, 16), 40), 2: ((16, 30), 99)}
    
    def __init__(self, difficulte):
        """Initialise la grille de jeu du démineur avec une certaine 
        taille et un nombre de bombes en fonction de la difficulté choisie, 
        et dévoile automatiquement une partie de la grille.
        ---------
        difficulte : int
            Codes de difficulté :
                0 - facile, 8x8, 10 bombes
                1 - moyen, 16x16, 40 bombes
                2 - difficile, 30x16, 99 bombes
        """
        self.difficulte = difficulte
        self.premier_clic = True
        
        # Choix de config en fonction de la difficulté
        if difficulte not in self.config:
            raise ValueError("Difficulté invalide : choisir 0, 1 ou 2.")
        self.taille, self.bombe = self.config[difficulte]
        self.cases_decouvertes = 0
         
        # Création d'un tableau objet : Grille préalable
        self.grille = [[None for _ in range(self.taille[1])] for _ in range(self.taille[0])]
        
        positions = [(l, c) for l in range(self.taille[0]) for c in range(self.taille[1])]
        
        # Création des cases bombes
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
                    
    def securite_premier_clic(self, ligne, colonne):
        if not self.premier_clic:
            return
        self.premier_clic = False
        safe = {(ligne, colonne)}   
        safe.update(self.voisins(ligne, colonne))
        bomb = []
        for r, c in safe:
            if isinstance(self.grille[r][c], CaseBombe):
                bomb.append((r,c))
        cases_dispo = []
        for r in range(self.taille[0]):
            for c in range(self.taille[1]):
                if (r,c) not in safe:
                    if isinstance(self.grille[r][c], CaseVide):
                        cases_dispo.append((r,c))
                        
        #pour déplacer les bombes mtn
        for r, c in bomb:
            if not cases_dispo:
                break
            nl, nc = random.choice(cases_dispo)
            cases_dispo.remove((nl, nc))
            self.grille[r][c] = CaseVide((r, c), self)
            self.grille[nl][nc] = CaseBombe((nl, nc), self) 
            
        for r in range(self.taille[0]):
            for c in range(self.taille[1]):
                case = self.grille[r][c]
                if isinstance(case, CaseVide):
                    case.nbr_bombes_voisines = case.get_nbr_bomb()

        
    def voisins(self, ligne, colonne):
        """Retourne les coordonnées des six voisins hexagonaux."""
        # Utiliser la parité des colonnes pour compter les voisins
        if colonne % 2 == 0:
            directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, 0)]
        else:
            directions = [(-1, 0), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        voisins = []
        for tmpl, tmpc in directions:
            nl, nc = ligne + tmpl, colonne + tmpc
            # définir la condition d'ajout
            if 0 <= nl < self.taille[0] and 0 <= nc < self.taille[1]:
                voisins.append((nl, nc))
        return voisins
            
                      
    def afficher(self):
        """
        Affiche visuellement les cases de la grille et leur état en temps réel.
        """
        pass
        
            
    def afficher_solution(self):
        """
        Affiche visuellement la solution de la grille.
        """
        pass
    
    def decouverte_initiale(self):
        """
        Initialise la partie en découvrant des cases automatiquement.
        """
        # Liste des cases vides
        case_vides = [case for ligne in self.grille for case in ligne if isinstance(case, CaseVide) and case.nbr_bombes_voisines == 0]
        if not case_vides:
            case_vides = [case for ligne in self.grille for case in ligne if isinstance(case, CaseVide)]
        if case_vides:
            random.choice(case_vides).decouvrir()
        
    def compter_drapeaux(self):
        return sum(case.drapeau for ligne in self.grille for case in ligne)                     
         
            
    def victoire(self):
        """
        Renvoie un message de victoire suivi de la fermeture du jeu.
        """
        print("\n Victoire !")
        self.afficher_solution()
        return True           
                
        

### Définition d'une case de jeu ###

class Case():
    
    def __init__(self, position, grille):
        """Initialise une case de la grille de jeu du démineur à une position 
        particulière dans une grille.
        """
        self.drapeau = False
        self.grille = grille
        self.position = position
        self.decouverte = False
    
    @abstractmethod
    def decouvrir(self):
        """
        Révéler la case sélectionnée, sauf si elle présente un drapeau.
        """
        pass
    
    def ajouter_drapeau(self):
        """
        Ajouter un drapeau sur la case sélectionnée ou le retirer si déjà présent.
        """
        if not self.decouverte:
            self.drapeau = not self.drapeau


class CaseBombe(Case):

    def __init__(self, position, grille):
        super().__init__(position, grille)
        
    def decouvrir(self):
        # Ne peut être découverte si marquée par un drapeau
        if not self.drapeau:
            self.decouverte = True
           
         
class CaseVide(Case):

    def __init__(self, position, grille):
        super().__init__(position, grille)
        self.nbr_bombes_voisines = 0

    def get_nbr_bomb(self):
        """
        Donne le nombre de bombes présentes dans le voisinage immédiat de la case sélectionnée.
        """
        return sum(isinstance(self.grille.grille[r][c], CaseBombe) for r, c in self.grille.voisins(*self.position))
        
    def decouvrir(self):
        if self.drapeau or self.decouverte :
            return
        
        self.decouverte = True
        self.grille.cases_decouvertes += 1
        
        # Propagation depuis cases vides sans bombe voisine
        if self.nbr_bombes_voisines == 0:
            for r, c in self.grille.voisins(*self.position):
                self.grille.grille[r][c].decouvrir()
        
   
    
