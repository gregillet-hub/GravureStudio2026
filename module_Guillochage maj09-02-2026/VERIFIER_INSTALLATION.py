#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de vérification de l'installation
Vérifie que tous les fichiers nécessaires sont présents
"""

import os
import sys

def check_installation():
    """Vérifie l'installation du module Guillochage"""
    print("=" * 60)
    print("VÉRIFICATION DE L'INSTALLATION")
    print("=" * 60)
    print()
    
    errors = []
    warnings = []
    
    # Vérifier les fichiers Python principaux
    print("1. Fichiers Python principaux...")
    python_files = [
        "guillochage_main.py",
        "guillochage_menu.py",
        "guillochage_forme.py",
        "guillochage_calques.py",
        "guillochage_canvas.py",
        "guillochage_courbes.py",
        "guillochage_lignes.py",
        "guillochage_lib_manager.py",
        "guillochage_formula_lab.py"
    ]
    
    for file in python_files:
        if os.path.exists(file):
            print(f"   ✓ {file}")
        else:
            print(f"   ✗ {file} MANQUANT")
            errors.append(file)
    print()
    
    # Vérifier les fichiers de configuration
    print("2. Fichiers de configuration...")
    config_files = ["config.json", "info.json"]
    for file in config_files:
        if os.path.exists(file):
            print(f"   ✓ {file}")
        else:
            print(f"   ⚠ {file} MANQUANT")
            warnings.append(file)
    print()
    
    # Vérifier la structure lib_courbes
    print("3. Bibliothèque de courbes...")
    
    # Trajectoires
    print("   Trajectoires:")
    trajectoires = ["ligne_droite.py", "cercle.py", "spirale.py"]
    for file in trajectoires:
        path = os.path.join("lib_courbes", "Trajectoires", file)
        if os.path.exists(path):
            print(f"      ✓ {file}")
        else:
            print(f"      ✗ {file} MANQUANT")
            errors.append(path)
    
    # Ondes
    print("   Ondes:")
    ondes = ["sinus.py", "carre.py", "triangle.py", "dents_scie.py"]
    for file in ondes:
        path = os.path.join("lib_courbes", "Ondes", file)
        if os.path.exists(path):
            print(f"      ✓ {file}")
        else:
            print(f"      ✗ {file} MANQUANT")
            errors.append(path)
    
    # Préréglages
    print("   Préréglages:")
    prereglages = ["clous_paris.json", "grain_orge.json", "soleil.json"]
    for file in prereglages:
        path = os.path.join("lib_courbes", "Prereglages", file)
        if os.path.exists(path):
            print(f"      ✓ {file}")
        else:
            print(f"      ✗ {file} MANQUANT")
            errors.append(path)
    print()
    
    # Vérifier les langues
    print("4. Fichiers de traduction...")
    langs = ["fr.json", "en.json", "de.json"]
    for file in langs:
        path = os.path.join("lang", file)
        if os.path.exists(path):
            print(f"   ✓ {file}")
        else:
            print(f"   ✗ {file} MANQUANT")
            errors.append(path)
    print()
    
    # Vérifier la documentation
    print("5. Documentation...")
    docs = ["ABOUT.txt", "LICENSE.txt"]
    for file in docs:
        path = os.path.join("docs", file)
        if os.path.exists(path):
            print(f"   ✓ {file}")
        else:
            print(f"   ⚠ {file} MANQUANT")
            warnings.append(path)
    print()
    
    # Vérifier le lanceur
    print("6. Fichier de lancement...")
    if os.path.exists("LANCER.bat"):
        print("   ✓ LANCER.bat")
    else:
        print("   ⚠ LANCER.bat MANQUANT")
        warnings.append("LANCER.bat")
    print()
    
    # Vérifier Python et les modules
    print("7. Environnement Python...")
    print(f"   ✓ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    try:
        import tkinter
        print("   ✓ tkinter (interface graphique)")
    except ImportError:
        print("   ✗ tkinter MANQUANT")
        errors.append("module tkinter")
    print()
    
    # Résumé
    print("=" * 60)
    if not errors and not warnings:
        print("✓ INSTALLATION COMPLÈTE ET FONCTIONNELLE !")
        print()
        print("Pour lancer le programme:")
        print("  - Double-cliquez sur LANCER.bat")
        print("  OU exécutez: python guillochage_main.py")
    elif errors:
        print(f"✗ {len(errors)} ERREUR(S) CRITIQUE(S) DÉTECTÉE(S)")
        print()
        print("Fichiers manquants:")
        for err in errors:
            print(f"  - {err}")
        print()
        print("Le programme ne fonctionnera pas correctement.")
        print("Téléchargez à nouveau le dossier complet.")
    else:
        print(f"⚠ {len(warnings)} AVERTISSEMENT(S)")
        print()
        print("Fichiers optionnels manquants:")
        for warn in warnings:
            print(f"  - {warn}")
        print()
        print("Le programme devrait fonctionner, mais certaines")
        print("fonctionnalités peuvent être limitées.")
    
    print("=" * 60)
    print()
    input("Appuyez sur Entrée pour fermer...")

if __name__ == "__main__":
    try:
        check_installation()
    except Exception as e:
        print(f"Erreur lors de la vérification: {e}")
        input("Appuyez sur Entrée pour fermer...")
