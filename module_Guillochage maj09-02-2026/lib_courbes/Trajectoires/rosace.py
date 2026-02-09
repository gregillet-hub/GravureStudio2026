# -*- coding: utf-8 -*-
import math

INFO = {
    "nom": "Rosace",
    "categorie": "Trajectoire Circulaire",
    "description": "Cercles concentriques lobés (Fleur).",
    "params_defaut": {
        "nb_petales": 12.0,   # C'est CELUI-CI qu'il faut changer !
        "amplitude": 2.0,     # Profondeur des pétales (mm)
        "phase": 0.0,         # Rotation de départ (degrés)
        "torsade": 0.0        # Effet vortex (0 = droit, 1 = incliné)
    }
}

def get_trajectoire(t, params):
    """
    Génère une trajectoire en forme de fleur.
    """
    # 1. Gestion de la progression (Cercles concentriques)
    i = params.get("line_index", 0)
    nb_total = max(1, params.get("total_lines", 1))
    
    # Rayons
    max_radius_base = params.get("gen_len", 100.0) / 2
    min_radius = params.get("margin_in", 0.0)

    if nb_total > 1:
        progress = i / (nb_total - 1)
        r_base = min_radius + progress * (max_radius_base - min_radius)
    else:
        progress = 0
        r_base = (min_radius + max_radius_base) / 2

    # 2. Récupération des paramètres
    # On utilise .get() avec une valeur par défaut de sécurité
    nb_lobes = params.get("nb_petales", 12.0)
    amp = params.get("amplitude", 2.0)
    phase_deg = params.get("phase", 0.0)
    torsade_factor = params.get("torsade", 0.0)

    # 3. Calcul de la Phase (Rotation)
    base_phase_rad = math.radians(phase_deg)
    
    # Effet Torsade : décale les pétales selon la ligne (i)
    torsade_phase = 0
    if nb_total > 1:
        cycle_rad = (2 * math.pi) / nb_lobes if nb_lobes != 0 else 0
        torsade_phase = progress * torsade_factor * cycle_rad

    total_phase = base_phase_rad + torsade_phase

    # 4. Position
    angle = t * 2 * math.pi
    
    # FORMULE MAJEURE : cos(angle * NOMBRE_DE_PETALES)
    r_actual = r_base + amp * math.cos(angle * nb_lobes + total_phase)

    x = r_actual * math.cos(angle)
    y = r_actual * math.sin(angle)

    # 5. Normale (Direction de l'outil)
    dr_dtheta = -amp * nb_lobes * math.sin(angle * nb_lobes + total_phase)

    dx_dt = dr_dtheta * math.cos(angle) - r_actual * math.sin(angle)
    dy_dt = dr_dtheta * math.sin(angle) + r_actual * math.cos(angle)

    norm_len = math.sqrt(dx_dt*dx_dt + dy_dt*dy_dt)
    
    if norm_len == 0:
        nx, ny = math.cos(angle), math.sin(angle)
    else:
        nx = dy_dt / norm_len
        ny = -dx_dt / norm_len

    return ((x, y), (nx, ny))