# -*- coding: utf-8 -*-
INFO = {
    "nom": "Ligne Droite",
    "categorie": "Trajectoire Base",
    "description": "Lignes parallèles simples",
    "params_defaut": {}
}

def get_trajectoire(t, params):
    # Récupère la longueur calculée par le moteur (gen_len)
    # ou utilise une valeur par défaut de 100 si manquant
    l = params.get("gen_len", 100.0)
    
    # Centre la ligne en 0 (de -L/2 à +L/2)
    x = (t - 0.5) * l
    y = 0
    return ((x, y), (0, 1))