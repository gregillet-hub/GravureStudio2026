# -*- coding: utf-8 -*-
import math

INFO = {
    "nom": "Ligne Droite",
    "categorie": "Type d'Onde",
    "version": "1.0",
    "description": "Aucune modulation (plat). Suit strictement la trajectoire.",
    "formule": "0",
    "params_defaut": {}
}

def get_offset(t, params):
    """
    Retourne 0 quelle que soit la valeur de t.
    Cela annule l'effet d'ondulation.
    """
    return 0.0