# -*- coding: utf-8 -*-
"""
Onde : Sinus
============

Génère une onde sinusoïdale pour le guillochage.
L'onde la plus classique et la plus utilisée.

Auteur : GravureStudioV1
Version : 1.0
"""
import math

INFO = {
    "nom": "Sinus",
    "categorie": "Type d'Onde",
    "version": "1.0",
    "description": "Onde sinusoïdale classique pour motifs ondulés",
    "formule": "amplitude * sin(2π * t * nb_cycles + phase)",
    "params_defaut": {
        "amplitude": 2.0,      # Amplitude de l'onde en mm
        "nb_lines": 12.0,      # Nombre de cycles (fréquence)
        "phase": 0.0,          # Phase initiale en degrés
        "period": 1.0,         # Période (non utilisé ici, gardé pour compatibilité)
    }
}

def get_offset(t, params):
    """
    Calcule l'offset ondulé pour un paramètre t.
    
    Args:
        t: Paramètre normalisé [0, 1] représentant la position le long de la trajectoire
        params: Dictionnaire des paramètres de l'onde
    
    Returns:
        float: Valeur de l'offset en mm (perpendiculaire à la trajectoire)
    
    Exemple d'utilisation:
        >>> offset = get_offset(0.5, {"amplitude": 2.0, "nb_lines": 10.0, "phase": 0.0})
        >>> print(offset)  # Valeur entre -2.0 et +2.0
    
    Note:
        L'offset est ensuite multiplié par le vecteur normal de la trajectoire
        pour obtenir le déplacement perpendiculaire.
    """
    # Récupération des paramètres
    amplitude = params.get("amplitude", 2.0)
    nb_cycles = params.get("nb_lines", 12.0)  # Nombre de cycles complets
    phase_deg = params.get("phase", 0.0)
    
    # Conversion de la phase en radians
    phase_rad = math.radians(phase_deg)
    
    # Calcul de l'onde sinusoïdale
    # t varie de 0 à 1, nb_cycles détermine combien de périodes complètes
    result = amplitude * math.sin(2.0 * math.pi * t * nb_cycles + phase_rad)
    
    return result


# === TESTS UNITAIRES (optionnel) ===
if __name__ == "__main__":
    print("Test de l'onde Sinus")
    print("=" * 50)
    
    # Test 1 : Onde standard
    params = {"amplitude": 2.0, "nb_lines": 4.0, "phase": 0.0}
    
    print("\nTest 1 : Amplitude 2mm, 4 cycles, phase 0°")
    print("t    | offset (mm)")
    print("-----|------------")
    
    for i in range(11):  # 11 points de 0.0 à 1.0
        t = i / 10.0
        offset = get_offset(t, params)
        print(f"{t:.1f}  | {offset:+6.3f}")
    
    # Test 2 : Avec phase de 90°
    print("\nTest 2 : Avec phase de 90°")
    params = {"amplitude": 2.0, "nb_lines": 4.0, "phase": 90.0}
    
    print("t    | offset (mm)")
    print("-----|------------")
    
    for i in range(11):
        t = i / 10.0
        offset = get_offset(t, params)
        print(f"{t:.1f}  | {offset:+6.3f}")
    
    # Test 3 : Haute fréquence
    print("\nTest 3 : Haute fréquence (20 cycles)")
    params = {"amplitude": 1.0, "nb_lines": 20.0, "phase": 0.0}
    
    print("t    | offset (mm)")
    print("-----|------------")
    
    for i in range(11):
        t = i / 10.0
        offset = get_offset(t, params)
        print(f"{t:.1f}  | {offset:+6.3f}")
    
    # Test 4 : Vérification des extremums
    print("\nTest 4 : Vérification des extremums")
    params = {"amplitude": 5.0, "nb_lines": 1.0, "phase": 0.0}
    
    # À t=0.25, sin doit être max (+1)
    t_max = 0.25
    offset_max = get_offset(t_max, params)
    print(f"À t={t_max} (max théorique) : {offset_max:.3f} mm (attendu: +5.0)")
    
    # À t=0.75, sin doit être min (-1)
    t_min = 0.75
    offset_min = get_offset(t_min, params)
    print(f"À t={t_min} (min théorique) : {offset_min:.3f} mm (attendu: -5.0)")
    
    # Vérifications
    assert abs(offset_max - 5.0) < 0.01, "Erreur sur le maximum"
    assert abs(offset_min + 5.0) < 0.01, "Erreur sur le minimum"
    
    print("\n✅ Tests terminés - Tous les extremums sont corrects")
