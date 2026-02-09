# -*- coding: utf-8 -*-
import math

INFO = {
    "nom": "Concentrique",
    "categorie": "Trajectoire Circulaire",
    "description": "Cercles concentriques expansifs (Rides dans l'eau).",
    "params_defaut": {}
}

def get_trajectoire(t, params):
    """
    Génère des cercles qui grandissent du centre vers les coins.
    t (0..1) parcourt le périmètre du cercle (0° à 360°).
    """
    # 1. Indices
    i = params.get("line_index", 0)
    nb_total = max(1, params.get("total_lines", 1))

    # 2. Bornes des rayons
    # 'gen_len' est la diagonale de la pièce (calculée par le moteur).
    # Le rayon max est donc la moitié de cette diagonale pour être sûr d'atteindre les coins.
    max_radius = params.get("gen_len", 100.0) / 2
    
    # La "Marge" sert de rayon de départ (trou central)
    min_radius = params.get("margin_in", 0.0)

    # 3. Calcul du rayon actuel
    if nb_total > 1:
        # Répartition linéaire : du rayon min au rayon max
        r = min_radius + (i / (nb_total - 1)) * (max_radius - min_radius)
    else:
        # Si une seule ligne, on vise le milieu
        r = (min_radius + max_radius) / 2

    # 4. Position sur le cercle
    # t va de 0 à 1 -> Angle de 0 à 2pi
    angle = t * 2 * math.pi
    
    x = r * math.cos(angle)
    y = r * math.sin(angle)
    
    # 5. Normale (Direction de l'ondulation)
    # Pour un effet "fleur" ou "engrenage", l'onde s'applique dans le sens du rayon.
    nx = math.cos(angle)
    ny = math.sin(angle)

    return ((x, y), (nx, ny))