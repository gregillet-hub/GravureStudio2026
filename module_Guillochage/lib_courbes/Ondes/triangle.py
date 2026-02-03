# -*- coding: utf-8 -*-
import math

INFO = {
    "nom": "Triangle",
    "categorie": "Type d'Onde",
    "version": "1.0",
    "description": "Onde triangulaire",
    "formule": "y = A·(4/T)|t mod T - T/2| - A",
    "params_defaut": {
        "amplitude": 2.0,
        "nb_lines": 12.0,
        "phase": 0.0,
    }
}

def get_offset(t, params):
    """
    Retourne l'offset (déplacement perpendiculaire) pour t ∈ [0, 1]
    
    Args:
        t: Paramètre de progression (0 à 1)
        params: Dictionnaire des paramètres
        
    Returns:
        float: Valeur de l'offset
    """
    amplitude = params.get('amplitude', 2.0)
    nb_lines = params.get('nb_lines', 12.0)
    phase = params.get('phase', 0.0)
    
    # Normalisation avec phase
    phase_norm = phase / 360.0
    t_phase = (t + phase_norm) % 1.0
    
    # Calcul de l'onde triangulaire
    val = (t_phase * nb_lines) % 1.0
    
    if val < 0.5:
        result = amplitude * (4 * val - 1)
    else:
        result = amplitude * (3 - 4 * val)
    
    return result
