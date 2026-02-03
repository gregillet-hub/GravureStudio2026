# GravureStudioV1 - Module Guillochage

## 🚀 DÉMARRAGE RAPIDE

### Double-cliquez sur `LANCER.bat`

OU en ligne de commande :
```bash
python guillochage_main.py
```

---

## 📋 Prérequis

- Python 3.8 ou supérieur
- Tkinter (inclus avec Python)

Vérifiez que Python est installé :
```bash
python --version
```

---

## 📁 Structure du projet

```
GravureStudioV1_Guillochage/
├── LANCER.bat                    # Lanceur Windows
├── README.md                     # Ce fichier
├── guillochage_main.py           # Point d'entrée
├── guillochage_menu.py           # Barre de menu
├── guillochage_forme.py          # Zone 1: Définition du brut
├── guillochage_calques.py        # Zone 2: Gestion des calques
├── guillochage_canvas.py         # Zone 3: Visualisation
├── guillochage_courbes.py        # Zone 4: Paramètres courbes
├── guillochage_lignes.py         # Zone 5: Gestion des lignes
├── guillochage_lib_manager.py    # Gestionnaire de bibliothèque
├── guillochage_formula_lab.py    # Créateur de courbes
├── config.json                   # Configuration
├── info.json                     # Métadonnées module
│
├── lib_courbes/                  # Bibliothèque de courbes
│   ├── Trajectoires/             # Trajectoires de base
│   │   ├── ligne_droite.py
│   │   ├── cercle.py
│   │   └── spirale.py
│   ├── Ondes/                    # Types d'ondes
│   │   ├── sinus.py
│   │   ├── carre.py
│   │   ├── triangle.py
│   │   └── dents_scie.py
│   └── Prereglages/              # Configurations prédéfinies
│       ├── clous_paris.json
│       ├── grain_orge.json
│       └── soleil.json
│
├── lang/                         # Fichiers de traduction
│   ├── fr.json
│   ├── en.json
│   └── de.json
│
└── docs/                         # Documentation
    ├── ABOUT.txt
    └── LICENSE.txt
```

---

## 🎯 Utilisation rapide

1. **Zone 1 - Définir le brut**
   - Choisir la forme (Cercle/Ovale ou Carré/Rectangle)
   - Définir les dimensions en mm

2. **Zone 2 - Créer des calques**
   - Ajouter un calque avec le bouton `+`
   - Nommer et colorer chaque calque
   - Organiser l'ordre (boutons ↑ ↓)

3. **Zone 4 - Configurer les paramètres**
   - Choisir une **Trajectoire Base** (Ligne droite, Cercle, Spirale)
   - Choisir un **Type d'Onde** (Sinus, Carré, Triangle, etc.)
   - Ajuster les paramètres

4. **Zone 3 - Visualisation**
   - Observer le résultat en temps réel
   - Bouton `#` : Activer/désactiver la grille
   - Bouton `⌂` : Recentrer la vue
   - Clic droit + Glisser : Déplacer la vue
   - Molette : Zoomer/Dézoomer

5. **Zone 5 - Gestion ligne par ligne** (optionnel)
   - Cliquer sur bouton `≣` en haut à droite de la Zone 4
   - Modifier les paramètres de lignes individuelles

6. **Export**
   - Menu Fichier → Exporter SVG ou DXF
   - Choisir "Global" ou "Calque par calque"

---

## 🌍 Langues disponibles

- Français (FR)
- English (EN)
- Deutsch (DE)

Changez la langue via le menu **Langue**.

---

## 🧪 Outils avancés

### Formula Lab
Menu **Librairie** → **Créer info courbe (Formula Lab)**
- Créez vos propres trajectoires et ondes
- Utilisez des formules mathématiques personnalisées

### Gestionnaire de Bibliothèque
Menu **Librairie** → **Gestionnaire de bibliothèque**
- Importez/Exportez des courbes
- Gérez votre bibliothèque de motifs

---

## 📞 Support

Consultez :
- `docs/ABOUT.txt` pour plus d'informations
- `docs/LICENSE.txt` pour les conditions d'utilisation

---

## ✨ Préréglages horlogers inclus

- **Clous de Paris** : Motif pyramidal classique
- **Grain d'Orge** : Motif allongé caractéristique
- **Soleil** : Rayons partant du centre

---

**Bon guillochage ! 🎨⚙️**
