# -*- coding: utf-8 -*-
import math

INFO = {
    "nom": "Eventail Centré (Bas)",
    "categorie": "Trajectoire Base",
    "version": "1.0",
    "description": "Toutes les lignes partent précisément du point bas-central.",
    "params_defaut": {
        "angle_debut": 45.0,    # Angle du premier rayon (en degrés)
        "angle_fin": 135.0,     # Angle du dernier rayon
        "longueur": 100.0,      # Longueur des rayons (pour dépasser la forme)
        "decale_y": 0.0         # Pour ajuster le point si besoin (0 = pile au bord)
    }
}

def get_trajectoire(t, params):
    """
    Génère des rayons qui partent tous d'un point unique en bas (0, -H/2).
    """
    # 1. Définition du POINT D'ORIGINE (Pivot Unique)
    # On récupère la hauteur du brut définie en Zone 1
    h_brut = params.get("brut_h", 50.0)
    
    # Le point (0, 0) est au centre de la pièce.
    # Le bas est donc à Y = -Hauteur / 2
    pivot_x = 0.0
    pivot_y = (-h_brut / 2) + params.get("decale_y", 0.0)

    # 2. Calcul de l'ANGLE du rayon courant
    idx = params.get("line_index", 0)
    nb_total = max(1, params.get("total_lines", 1))
    
    deg_start = params.get("angle_debut", 45.0)
    deg_end = params.get("angle_fin", 135.0)
    
    # Répartition des angles
    if nb_total > 1:
        # On distribue de start à end
        ratio = idx / (nb_total - 1)
        angle_deg = deg_start + ratio * (deg_end - deg_start)
    else:
        # Si une seule ligne, on la met au milieu (90° = vertical)
        angle_deg = 90.0

    angle_rad = math.radians(angle_deg)

    # 3. Calcul de la position le long du rayon
    # t varie de 0 (au pivot) à 1 (au bout de la longueur définie)
    longueur_max = params.get("longueur", 100.0)
    current_dist = t * longueur_max
    
    # 4. Projection polaire vers cartésien
    # x = x_origine + distance * cos(angle)
    x = pivot_x + current_dist * math.cos(angle_rad)
    y = pivot_y + current_dist * math.sin(angle_rad)

    # 5. Calcul de la Normale (pour que l'onde soit perpendiculaire au rayon)
    nx = -math.sin(angle_rad)
    ny = math.cos(angle_rad)

    return ((x, y), (nx, ny))