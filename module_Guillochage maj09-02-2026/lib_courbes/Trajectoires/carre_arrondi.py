# -*- coding: utf-8 -*-
import math

INFO = {
    "nom": "Carré Arrondi (Coussin)",
    "categorie": "Trajectoire Forme",
    "description": "Trajectoire carrée avec coins arrondis (Superellipse).",
    "params_defaut": {
        "courbure": 4.0 # 2 = Cercle, 4+ = Carré arrondi
    }
}

def sign(x):
    """Fonction utilitaire pour le signe"""
    if x > 0: return 1
    if x < 0: return -1
    return 0

def get_trajectoire(t, params):
    i = params.get("line_index", 0)
    nb_total = max(1, params.get("total_lines", 1))
    
    # Taille (Demi-diagonale)
    size_max = params.get("gen_len", 100.0) / 2
    size_min = params.get("margin_in", 0.0)
    
    # Interpolation de la taille
    if nb_total > 1:
        scale = size_min + (i / (nb_total - 1)) * (size_max - size_min)
    else:
        scale = (size_min + size_max) / 2

    # Paramètre de forme (n)
    # n=2 est un cercle. n=4 est un coussin doux. n=10 est presque un carré.
    n = params.get("courbure", 4.0)
    
    angle = t * 2 * math.pi
    
    # Formule de la Superellipse (Lamé curve)
    # |x/a|^n + |y/b|^n = 1
    
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    
    # Astuce mathématique pour éviter les erreurs de puissance sur les nombres négatifs
    # x = scale * sign(cos) * |cos|^(2/n)
    x = scale * sign(cos_a) * (abs(cos_a) ** (2 / n))
    y = scale * sign(sin_a) * (abs(sin_a) ** (2 / n))
    
    # Normale approximative (suffisante pour le guillochage visuel ici)
    # Pour un calcul exact, il faudrait la dérivée de la superellipse,
    # mais utiliser l'angle polaire fonctionne souvent assez bien visuellement.
    nx = math.cos(angle)
    ny = math.sin(angle)

    return ((x, y), (nx, ny))