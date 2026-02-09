# -*- coding: utf-8 -*-
import math

INFO = {
    "nom": "Eventail (Auto-Centré)",
    "categorie": "Trajectoire Base",
    "version": "1.1",
    "description": "Rayons partant du bas de la pièce (pivot automatique).",
    "params_defaut": {
        "pivot_offset_y": 0.0, # Décalage optionnel par rapport au bas (0 = pile sur le bord)
        "angle_debut": 45.0,   # Angle de départ (en degrés)
        "angle_fin": 135.0,    # Angle de fin (en degrés)
        "rayon_min": 10.0,     # Début de la gravure (distance du pivot)
        "rayon_max": 90.0      # Fin de la gravure
    }
}

def get_trajectoire(t, params):
    """
    Génère une ligne rayonnante depuis le bas de la forme brute.
    """
    # 1. Récupération des dimensions du brut (transmises par le moteur)
    # Si non défini, on prend 50.0 par défaut
    h_brut = params.get("brut_h", 50.0)
    
    # 2. Calcul du Pivot
    # Le bas de la pièce est à Y = -h_brut / 2
    # On ajoute un 'pivot_offset_y' si l'utilisateur veut le monter/descendre un peu
    base_y = -h_brut / 2
    p_y = base_y + params.get("pivot_offset_y", 0.0)
    
    # Le pivot X est centré par défaut (0), mais on pourrait ajouter un offset
    p_x = 0.0 

    # 3. Paramètres de l'éventail
    idx = params.get("line_index", 0)
    nb_total = max(1, params.get("total_lines", 1))
    
    ang_start = math.radians(params.get("angle_debut", 45.0))
    ang_end = math.radians(params.get("angle_fin", 135.0))
    
    r_min = params.get("rayon_min", 10.0)
    r_max = params.get("rayon_max", 100.0)

    # 4. Calcul de l'angle courant
    if nb_total > 1:
        ratio = idx / (nb_total - 1)
        current_angle = ang_start + ratio * (ang_end - ang_start)
    else:
        current_angle = (ang_start + ang_end) / 2

    # 5. Position le long du rayon
    current_r = r_min + t * (r_max - r_min)
    
    # 6. Conversion en coordonnées (Mathématiques)
    x = p_x + current_r * math.cos(current_angle)
    y = p_y + current_r * math.sin(current_angle)

    # 7. Vecteur Normal (pour l'ondulation)
    nx = -math.sin(current_angle)
    ny = math.cos(current_angle)

    return ((x, y), (nx, ny))