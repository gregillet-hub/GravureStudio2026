# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import glob
import importlib.util
import shutil
import sys

class LibraryManager(tk.Toplevel):
    def __init__(self, parent, app_instance=None, on_update_callback=None):
        super().__init__(parent)
        self.app = app_instance
        self.on_update_callback = on_update_callback 
        
        self.title(self.t("lib_title"))
        self.geometry("1000x650")
        self.configure(bg="#1e1e1e")
        self.transient(parent)
        self.grab_set()

        # --- BARRE D'OUTILS ---
        self.toolbar = tk.Frame(self, bg="#333333", height=40)
        self.toolbar.pack(fill="x", side="top")
        
        self.btn_import = self._create_toolbar_btn(self.t("lib_btn_import"), self.action_import)
        self.btn_export = self._create_toolbar_btn(self.t("lib_btn_export"), self.action_export)
        self.btn_refresh = self._create_toolbar_btn(self.t("lib_btn_refresh"), self.refresh_tree)
        
        # --- CORPS PRINCIPAL ---
        self.paned = tk.PanedWindow(self, orient=tk.HORIZONTAL, bg="#1e1e1e", sashwidth=4, sashrelief="flat")
        self.paned.pack(fill="both", expand=True, padx=5, pady=5)

        # 1. ARBORESCENCE
        self.frame_left = tk.Frame(self.paned, bg="#252526")
        self.paned.add(self.frame_left, width=300)
        
        tk.Label(self.frame_left, text=self.t("lib_col_explorer"), fg="#007acc", bg="#252526", font=("Segoe UI", 10, "bold")).pack(pady=5, fill="x")
        
        self.tree = ttk.Treeview(self.frame_left, show="tree", selectmode="browse")
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#2d2d30", foreground="white", fieldbackground="#2d2d30", borderwidth=0)
        style.map("Treeview", background=[("selected", "#007acc")])

        # 2. DÉTAILS
        self.frame_right = tk.Frame(self.paned, bg="#1e1e1e")
        self.paned.add(self.frame_right)

        self.header_info = tk.Frame(self.frame_right, bg="#252526", padx=10, pady=10)
        self.header_info.pack(fill="x", padx=5, pady=5)
        
        self.lbl_titre = tk.Label(self.header_info, text=self.t("lib_info_select"), fg="white", bg="#252526", font=("Segoe UI", 16, "bold"), anchor="w")
        self.lbl_titre.pack(fill="x")
        
        self.lbl_desc = tk.Label(self.header_info, text="", fg="#d4d4d4", bg="#252526", font=("Segoe UI", 10, "italic"), anchor="w", wraplength=500, justify="left")
        self.lbl_desc.pack(fill="x", pady=(5,0))

        self.lbl_formula = tk.Label(self.header_info, text="", fg="#6a9955", bg="#252526", font=("Consolas", 10), anchor="w")
        self.lbl_formula.pack(fill="x", pady=(5,0))

        tk.Label(self.frame_right, text=self.t("lib_grp_default"), fg="#007acc", bg="#1e1e1e", font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.param_tree = ttk.Treeview(self.frame_right, columns=("Key", "Value"), show="headings")
        self.param_tree.heading("Key", text=self.t("lib_col_key"))
        self.param_tree.heading("Value", text=self.t("lib_col_val"))
        self.param_tree.column("Key", width=200)
        self.param_tree.column("Value", width=200)
        self.param_tree.pack(fill="both", expand=True, padx=10, pady=5)

        self.footer = tk.Frame(self.frame_right, bg="#1e1e1e", pady=10)
        self.footer.pack(fill="x")
        self.btn_suppr = tk.Button(self.footer, text=self.t("lib_btn_del"), bg="#f48771", fg="white", bd=0, padx=10, pady=5, command=self.action_delete)
        self.btn_suppr.pack(side="right", padx=10)

        self.refresh_tree()

    def t(self, key):
        if self.app: return self.app.t(key)
        return key

    def _create_toolbar_btn(self, text, cmd):
        btn = tk.Button(self.toolbar, text=text, command=cmd, bg="#333333", fg="white", bd=0, padx=15, activebackground="#505050", activeforeground="white", cursor="hand2")
        btn.pack(side="left", fill="y", padx=1)
        return btn

    def refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        
        root_traj = self.tree.insert("", "end", text=self.t("lib_root_traj"), open=True)
        root_onde = self.tree.insert("", "end", text=self.t("lib_root_wave"), open=True)
        root_pre = self.tree.insert("", "end", text=self.t("lib_root_pre"), open=True)
        
        base_path = os.path.join(os.path.dirname(__file__), "lib_courbes")
        
        self._scan_folder(os.path.join(base_path, "Trajectoires"), root_traj, is_python=True)
        self._scan_folder(os.path.join(base_path, "Ondes"), root_onde, is_python=True)
        self._scan_folder(os.path.join(base_path, "Prereglages"), root_pre, is_python=False)
        
        if self.on_update_callback:
            try: self.on_update_callback()
            except: pass

    def _scan_folder(self, path, parent_node, is_python):
        if not os.path.exists(path): return
        ext = "*.py" if is_python else "*.json"
        for f in glob.glob(os.path.join(path, ext)):
            filename = os.path.basename(f)
            if filename.startswith("__") or filename.startswith("init"): continue
            
            display_name = filename
            try:
                if is_python:
                    info = self._load_py_info(f)
                    if info and "nom" in info: display_name = info["nom"]
            except: pass
            
            file_key = "file_" + filename.replace(".py", "").replace(".json", "").lower()
            trans_name = self.t(file_key)
            if trans_name != file_key: display_name = trans_name

            self.tree.insert(parent_node, "end", text=display_name, values=(f, "py" if is_python else "json"))

    def _load_py_info(self, filepath):
        try:
            spec = importlib.util.spec_from_file_location("temp_module", filepath)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            if hasattr(mod, "INFO"): return mod.INFO
        except: pass
        return None

    def on_select(self, event):
        item = self.tree.selection()
        if not item: return
        values = self.tree.item(item, "values")
        if not values: return
        
        filepath, type_file = values[0], values[1]
        
        self.lbl_titre.config(text="...")
        self.lbl_desc.config(text="")
        self.lbl_formula.config(text="")
        self.param_tree.delete(*self.param_tree.get_children())
        
        if type_file == "py":
            info = self._load_py_info(filepath)
            if info:
                # Traduction du Titre du fichier
                file_key = "file_" + os.path.basename(filepath).replace(".py", "").lower()
                trans_name = self.t(file_key)
                name_display = trans_name if trans_name != file_key else info.get("nom", os.path.basename(filepath))
                
                self.lbl_titre.config(text=name_display)
                self.lbl_desc.config(text=info.get("description", ""))
                
                lbl_form = self.t("lib_lbl_formula")
                self.lbl_formula.config(text=f"{lbl_form} {info.get('formule', 'N/A')}")
                
                params = info.get("params_defaut", {})
                for k, v in params.items():
                    # --- TRADUCTION DES VARIABLES DU TABLEAU ---
                    # On construit la clé (ex: "p_amplitude")
                    trans_key = "p_" + k.lower()
                    display_k = self.t(trans_key)
                    # Si pas de trad, on affiche la clé technique propre
                    if display_k == trans_key: display_k = k
                    
                    self.param_tree.insert("", "end", values=(display_k, str(v)))
            else:
                self.lbl_titre.config(text=os.path.basename(filepath))

    def action_import(self):
        file_path = filedialog.askopenfilename(title=self.t("msg_import_title"), filetypes=[("Scripts", "*.py *.json")])
        if not file_path: return
        try:
            filename = os.path.basename(file_path)
            target_folder = None
            if file_path.endswith(".py"):
                info = self._load_py_info(file_path)
                if not info:
                    messagebox.showerror(self.t("msg_error"), "Fichier invalide (Manque INFO)")
                    return
                cat = info.get("categorie", "")
                if cat == "Trajectoire Base": target_folder = "Trajectoires"
                elif cat == "Type d'Onde": target_folder = "Ondes"
                else:
                    messagebox.showerror(self.t("msg_error"), f"Catégorie inconnue: {cat}")
                    return
            elif file_path.endswith(".json"): target_folder = "Prereglages"
            
            if target_folder:
                dest_path = os.path.join(os.path.dirname(__file__), "lib_courbes", target_folder, filename)
                shutil.copy2(file_path, dest_path)
                self.refresh_tree()
                messagebox.showinfo(self.t("msg_success"), f"Fichier importé !")
        except Exception as e:
            messagebox.showerror(self.t("msg_error"), str(e))

    def action_export(self):
        item = self.tree.selection()
        if not item: return
        vals = self.tree.item(item, "values")
        if not vals: return
        src_path = vals[0]
        filename = os.path.basename(src_path)
        dest_folder = filedialog.askdirectory(title=self.t("msg_export_title"))
        if dest_folder:
            try:
                dest_path = os.path.join(dest_folder, filename)
                shutil.copy2(src_path, dest_path)
                messagebox.showinfo(self.t("msg_success"), f"Fichier exporté.")
            except Exception as e:
                messagebox.showerror(self.t("msg_error"), str(e))

    def action_delete(self):
        item = self.tree.selection()
        if not item: return
        vals = self.tree.item(item, "values")
        if vals and messagebox.askyesno(self.t("msg_warning"), self.t("msg_confirm_del")):
            try:
                os.remove(vals[0])
                self.refresh_tree()
                self.lbl_titre.config(text="Supprimé")
            except Exception as e:
                messagebox.showerror(self.t("msg_error"), str(e))
