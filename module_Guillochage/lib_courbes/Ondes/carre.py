# -*- coding: utf-8 -*-
import math

INFO = {
    "nom": "Carre",
    "categorie": "Type d'Onde",
    "version": "2.0",
    "description": "Signal carré avec micro-pentes pour affichage garanti",
    "formule": "Trapèze raide",
    "params_defaut": {
        "amplitude": 2.0,
        "douceur": 0.02 # 2% de la période sert à la transition (trait vertical)
    }
}

def get_offset(t, params):
    """
    Génère un carré avec des transitions forcées pour que le tracé soit continu.
    t est l'angle en radians fourni par le moteur.
    """
    # Normalisation de t sur [0, 1] pour faciliter le calcul du trapèze
    # On divise par 2pi et on garde la partie décimale
    prog = (t / (2 * math.pi)) % 1.0
    
    # Largeur de la transition (le trait vertical)
    # 0.02 = très raide (vertical), 0.2 = trapèze visible
    pente = params.get("douceur", 0.02)
    
    # 1. Montée (Trait vertical gauche)
    if prog < pente:
        # On passe de -1 à +1
        ratio = prog / pente
        return -1.0 + (ratio * 2.0)
        
    # 2. Plateau Haut
    elif prog < 0.5:
        return 1.0
        
    # 3. Descente (Trait vertical droit)
    elif prog < 0.5 + pente:
        # On passe de +1 à -1
        ratio = (prog - 0.5) / pente
        return 1.0 - (ratio * 2.0)
        
    # 4. Plateau Bas
    else:
        return -1.0