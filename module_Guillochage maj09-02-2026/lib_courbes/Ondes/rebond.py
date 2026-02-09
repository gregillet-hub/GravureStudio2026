# -*- coding: utf-8 -*-
import math

INFO = {
    "nom": "Rebond",
    "categorie": "Type d'Onde",
    "version": "1.0",
    "description": "Arcs successifs (Valeur absolue du Sinus).",
    "formule": "|sin(t)|",
    "params_defaut": {
        "amplitude": 2.0
    }
}

def get_offset(t, params):
    """
    Renvoie la valeur absolue du sinus.
    Cela crée une courbe qui reste toujours du même côté de la ligne (positive),
    avec des pointes en bas et des arrondis en haut.
    """
    # t est l'angle en radians fourni par le moteur
    return abs(math.sin(t))
