# -*- coding: utf-8 -*-
import math

INFO = {
    "nom": "Spirale (Colimaçon)",
    "categorie": "Trajectoire Circulaire",
    "description": "Spirale d'Archimède continue (Pour rochets et colimaçonnage).",
    "params_defaut": {
        "tours": 15.0,     # Nombre de révolutions
        "sens_horaire": 1  # 1 pour horaire, -1 pour anti-horaire
    }
}

def get_trajectoire(t, params):
    """
    Génère une Spirale d'Archimède.
    Contrairement aux cercles, t parcourt toute la longueur de la spirale (plusieurs tours).
    """
    # 1. Gestion du "Multi-start" (Optionnel)
    # Si l'utilisateur demande 1 ligne (cas normal), i=0.
    # Si l'utilisateur demande 3 lignes, on décale le départ de 120° pour chaque ligne.
    i = params.get("line_index", 0)
    nb_total = max(1, params.get("total_lines", 1))
    
    # Décalage angulaire de départ pour les spirales multiples
    angle_offset = (i / nb_total) * 2 * math.pi

    # 2. Bornes des rayons
    max_radius = params.get("gen_len", 100.0) / 2
    min_radius = params.get("margin_in", 0.0)
    
    # 3. Paramètres de la spirale
    nb_tours = params.get("tours", 15.0)
    sens = params.get("sens_horaire", 1) # 1 ou -1
    
    # 4. Calculs principaux
    # Rayon actuel : il grandit linéairement avec t (Archimède)
    # t=0 -> min_radius, t=1 -> max_radius
    r = min_radius + t * (max_radius - min_radius)
    
    # Angle actuel : il tourne 'nb_tours' fois
    # On multiplie par 2*pi pour avoir des radians
    total_angle = t * nb_tours * 2 * math.pi
    
    # On applique le sens et le décalage initial
    theta = (total_angle * sens) + angle_offset

    # 5. Position (x, y)
    x = r * math.cos(theta)
    y = r * math.sin(theta)

    # 6. Normale (Vecteur perpendiculaire)
    # Pour un colimaçonnage propre, l'outil doit rester perpendiculaire au sillon.
    # Sur une spirale serrée, la normale est presque radiale (comme un cercle).
    # Mais mathématiquement, elle est légèrement inclinée.
    
    # Dérivées (Vitesse) par rapport à t pour avoir la tangente
    # r' = dr/dt = (max - min)
    # theta' = dtheta/dt = nb_tours * 2pi * sens
    
    dr = max_radius - min_radius
    dtheta = nb_tours * 2 * math.pi * sens
    
    # Dérivée en x et y (Règle de la chaîne)
    # x = r * cos(theta) -> x' = r'cos(theta) - r*theta'sin(theta)
    dx_dt = dr * math.cos(theta) - r * dtheta * math.sin(theta)
    dy_dt = dr * math.sin(theta) + r * dtheta * math.cos(theta)
    
    # La normale est (-dy, dx) ou (dy, -dx) normalisée
    # On calcule la longueur du vecteur vitesse
    norm_len = math.sqrt(dx_dt**2 + dy_dt**2)
    
    if norm_len == 0:
        nx, ny = math.cos(theta), math.sin(theta)
    else:
        # Normale pointant vers l'extérieur (approximativement)
        nx = dy_dt / norm_len
        ny = -dx_dt / norm_len
        
        # Correction de sens si besoin (pour que l'onde soit du bon côté)
        # Si le produit scalaire avec le rayon est négatif, on inverse
        if (nx * x + ny * y) < 0:
            nx = -nx
            ny = -ny

    return ((x, y), (nx, ny))