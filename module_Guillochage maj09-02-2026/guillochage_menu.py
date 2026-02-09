# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox
import os
import glob

# Import des modules liés (Gestionnaires)
try:
    from guillochage_lib_manager import LibraryManager
except ImportError:
    LibraryManager = None
    print("[Menu] Erreur import LibraryManager")

try:
    from guillochage_formula_lab import FormulaLab
except ImportError:
    FormulaLab = None
    print("[Menu] Erreur import FormulaLab")

class GuillochageMenu:
    def __init__(self, frame_parent, app_instance):
        self.frame_parent = frame_parent
        self.app = app_instance 
        
        self.main_window = self.frame_parent.winfo_toplevel()
        
        # --- SYNCHRONISATION 2.5D (Menu <-> Bouton Zone 4) ---
        self.var_25d = tk.BooleanVar(value=False)
        
        # On intercepte la méthode toggle_25d de l'application pour mettre à jour
        # la variable du menu à chaque fois que la 2.5D change (peu importe la source).
        if hasattr(self.app, 'toggle_25d'):
            self._original_app_toggle = self.app.toggle_25d # Sauvegarde de la vraie fonction
            self.app.toggle_25d = self._synced_toggle_25d   # Remplacement par la nôtre
            
            # Initialisation de la variable selon l'état actuel
            if hasattr(self.app, 'is_25d_active'):
                self.var_25d.set(self.app.is_25d_active)

        self.menubar = tk.Menu(self.main_window)
        self.build_menu()
        self.main_window.config(menu=self.menubar)
        
        # Raccourcis Clavier
        self.main_window.bind("<Control-n>", lambda e: self.app.action_new())
        self.main_window.bind("<Control-s>", lambda e: self.app.action_save())
        self.main_window.bind("<Control-o>", lambda e: self.app.action_open())
        self.main_window.bind("<Control-z>", lambda e: self.app.undo())
        self.main_window.bind("<Control-y>", lambda e: self.app.redo())

    def _synced_toggle_25d(self):
        """Méthode injectée : Exécute l'action réelle PUIS met à jour le menu."""
        if self._original_app_toggle:
            self._original_app_toggle()
        
        # Mise à jour visuelle de la coche dans le menu
        if hasattr(self.app, 'is_25d_active'):
            self.var_25d.set(self.app.is_25d_active)

    def on_menu_25d_click(self):
        """Action déclenchée par le clic dans le menu."""
        # La Checkbox a déjà changé self.var_25d visuellement.
        # On vérifie si l'app est synchro avec cette nouvelle demande.
        app_state = getattr(self.app, 'is_25d_active', False)
        target_state = self.var_25d.get()
        
        if app_state != target_state:
            # On appelle la méthode (qui est maintenant _synced_toggle_25d)
            self.app.toggle_25d()

    def t(self, key):
        """Raccourci pour traduire"""
        return self.app.t(key)

    def build_menu(self):
        # 1. FICHIER
        self.file_menu = tk.Menu(self.menubar, tearoff=0)
        self.file_menu.add_command(label=self.t("m_new"), command=self.app.action_new, accelerator="Ctrl+N")
        self.file_menu.add_command(label="Ouvrir...", command=self.app.action_open, accelerator="Ctrl+O") 
        self.file_menu.add_separator()
        self.file_menu.add_command(label=self.t("m_save"), command=self.app.action_save, accelerator="Ctrl+S")
        self.file_menu.add_command(label=self.t("m_save_as"), command=self.app.action_save_as)
        self.file_menu.add_separator()
        
        # --- EXPORT SVG ---
        self.svg_menu = tk.Menu(self.file_menu, tearoff=0)
        self.svg_menu.add_command(label="Export Dossier (Séparé)", command=lambda: self.app.action_export_batch_folder("svg"))
        self.svg_menu.add_separator()
        self.svg_menu.add_command(label="Global (Tous les calques)", command=self.app.action_export_global_svg)
        self.svg_menu.add_command(label="Calque Actif Seulement", command=self.app.action_export_layer_svg)
        self.file_menu.add_cascade(label=self.t("m_export_svg"), menu=self.svg_menu)
        
        # --- EXPORT DXF ---
        self.dxf_menu = tk.Menu(self.file_menu, tearoff=0)
        self.dxf_menu.add_command(label="Export Dossier (Séparé)", command=lambda: self.app.action_export_batch_folder("dxf"))
        self.dxf_menu.add_separator()
        self.dxf_menu.add_command(label="Global (Tous les calques)", command=self.app.action_export_global_dxf)
        self.dxf_menu.add_command(label="Calque Actif Seulement", command=self.app.action_export_layer_dxf)
        self.file_menu.add_cascade(label=self.t("m_export_dxf"), menu=self.dxf_menu)
        
        self.file_menu.add_separator()
        self.var_autosave = tk.BooleanVar(value=True)
        self.file_menu.add_checkbutton(label=self.t("m_autosave"), variable=self.var_autosave, command=self.toggle_autosave)
        self.file_menu.add_separator()
        self.file_menu.add_command(label=self.t("m_quit"), command=self.app.on_closing)
        self.menubar.add_cascade(label=self.t("m_file"), menu=self.file_menu)

        # 2. ÉDITION
        self.edit_menu = tk.Menu(self.menubar, tearoff=0)
        self.edit_menu.add_command(label=self.t("m_copy"), command=self.app.action_copy)
        self.edit_menu.add_command(label=self.t("m_paste"), command=self.app.action_paste)
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label=self.t("m_undo"), command=self.app.undo, accelerator="Ctrl+Z")
        self.edit_menu.add_command(label=self.t("m_redo"), command=self.app.redo, accelerator="Ctrl+Y")
        self.menubar.add_cascade(label=self.t("m_edit"), menu=self.edit_menu)

        # 3. LIBRAIRIE
        self.lib_menu = tk.Menu(self.menubar, tearoff=0)
        self.lib_menu.add_command(label=self.t("m_lib_man"), command=self.open_library_manager)
        self.lib_menu.add_separator()
        self.lib_menu.add_command(label=self.t("m_formula"), command=self.open_formula_lab)
        self.menubar.add_cascade(label=self.t("m_lib"), menu=self.lib_menu)

        # 4. LANGUE
        self.lang_menu = tk.Menu(self.menubar, tearoff=0)
        self.refresh_languages()
        self.menubar.add_cascade(label=self.t("m_lang"), menu=self.lang_menu)

        # 5. AFFICHAGE
        self.view_menu = tk.Menu(self.menubar, tearoff=0)
        self.view_menu.add_command(label=self.t("m_fs_app"), command=self.toggle_fullscreen_app)
        self.view_menu.add_command(label=self.t("m_fs_z3"), command=self.toggle_fullscreen_zone3)
        
        # Checkbutton 2.5D synchronisé
        self.view_menu.add_checkbutton(label=self.t("m_view_25d"), variable=self.var_25d, command=self.on_menu_25d_click)
        
        self.menubar.add_cascade(label=self.t("m_view"), menu=self.view_menu)

        # 6. AIDE
        self.help_menu = tk.Menu(self.menubar, tearoff=0)
        self.help_menu.add_command(label=self.t("m_about"), command=lambda: self.show_doc("ABOUT.txt"))
        self.help_menu.add_command(label=self.t("m_licenses"), command=lambda: self.show_doc("LICENSE.txt"))
        self.menubar.add_cascade(label=self.t("m_help"), menu=self.help_menu)

    def rebuild_menu(self):
        """Reconstruit le menu (utile lors du changement de langue)"""
        self.menubar.destroy()
        self.menubar = tk.Menu(self.main_window)
        self.build_menu()
        self.main_window.config(menu=self.menubar)

    def refresh_languages(self):
        self.lang_menu.delete(0, "end")
        lang_path = os.path.join(os.path.dirname(__file__), "lang", "*.json")
        for f in glob.glob(lang_path):
            lang_code = os.path.basename(f).replace(".json", "")
            lang_name = lang_code.upper()
            self.lang_menu.add_command(
                label=lang_name, 
                command=lambda l=lang_code: self.app.change_language(l)
            )

    def show_doc(self, filename):
        doc_path = os.path.join(os.path.dirname(__file__), "docs", filename)
        if os.path.exists(doc_path):
            try:
                with open(doc_path, "r", encoding="utf-8") as f:
                    content = f.read()
                messagebox.showinfo(filename.replace(".txt", ""), content)
            except Exception as e:
                messagebox.showerror("Err", f"{e}")
        else:
            messagebox.showinfo("Info", f"File {filename} not found.")

    def toggle_fullscreen_app(self):
        state = not self.main_window.attributes("-fullscreen")
        self.main_window.attributes("-fullscreen", state)

    def toggle_fullscreen_zone3(self):
        if hasattr(self.app, 'toggle_zone3_fullscreen'):
            self.app.toggle_zone3_fullscreen()

    def toggle_autosave(self):
        pass

    def open_library_manager(self):
        if LibraryManager:
            cb = self.app.panneau_courbes.refresh_library if hasattr(self.app, 'panneau_courbes') else None
            LibraryManager(self.main_window, app_instance=self.app, on_update_callback=cb)
        else:
            messagebox.showerror("Err", "LibraryManager module missing.")

    def open_formula_lab(self):
        if FormulaLab:
            cb = self.app.panneau_courbes.refresh_library if hasattr(self.app, 'panneau_courbes') else None
            FormulaLab(self.main_window, app_instance=self.app, on_update_callback=cb)
        else:
            messagebox.showerror("Err", "FormulaLab module missing.")