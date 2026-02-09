# -*- coding: utf-8 -*-
import math

INFO = {
    "nom": "Radial",
    "categorie": "Trajectoire Circulaire",
    "description": "Lignes rayonnantes depuis le centre vers l'extérieur (Soleil).",
    "params_defaut": {}
}

def get_trajectoire(t, params):
    """
    Génère une ligne qui part du centre (ou d'une marge) vers l'extérieur.
    """
    # 1. Récupération de l'index de la ligne (0, 1, 2...)
    i = params.get("line_index", 0)
    # Nombre total de lignes (pour diviser le cercle en parts égales)
    # On s'assure d'avoir au moins 1 pour éviter la division par zéro
    nb_total = max(1, params.get("total_lines", 1))

    # 2. Calcul de l'Angle de la ligne
    # On répartit les lignes sur 360 degrés (2*pi radians)
    angle = (i / nb_total) * 2 * math.pi
    
    # 3. Calcul de la Longueur du rayon
    # gen_len est la diagonale calculée par le moteur (garantit d'aller au bout)
    # On divise par 2 car on part du centre (rayon)
    max_radius = params.get("gen_len", 100.0) / 2
    
    # La "Marge Int" (margin_in) sert ici de "Trou central"
    min_radius = params.get("margin_in", 0.0)
    
    # 4. Interpolation de la position actuelle (t va de 0 à 1)
    # À t=0, on est à min_radius (centre). À t=1, on est à max_radius (bord).
    current_r = min_radius + t * (max_radius - min_radius)
    
    # 5. Conversion Polaire -> Cartésien
    x = current_r * math.cos(angle)
    y = current_r * math.sin(angle)
    
    # 6. Calcul de la Normale (Pour l'ondulation)
    # L'onde doit être perpendiculaire au rayon.
    # Le vecteur perpendiculaire à (cos, sin) est (-sin, cos)
    nx = -math.sin(angle)
    ny = math.cos(angle)

    return ((x, y), (nx, ny))