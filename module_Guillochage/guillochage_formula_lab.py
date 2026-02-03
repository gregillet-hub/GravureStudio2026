# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
import math
import os

class FormulaLab(tk.Toplevel):
    def __init__(self, parent, app_instance=None, on_update_callback=None):
        super().__init__(parent)
        self.app = app_instance
        self.on_update_callback = on_update_callback 
        
        self.title(self.t("lab_title"))
        self.geometry("1100x700")
        self.configure(bg="#1e1e1e")
        self.transient(parent)
        
        self.var_nom = tk.StringVar(value=self.t("lab_def_name"))
        self.var_type = tk.StringVar(value=self.t("lab_cat_wave"))
        self.var_desc = tk.StringVar(value=self.t("lab_def_desc"))
        
        self.paned = tk.PanedWindow(self, orient=tk.HORIZONTAL, bg="#1e1e1e", sashwidth=4, sashrelief="flat")
        self.paned.pack(fill="both", expand=True, padx=5, pady=5)
        
        # GAUCHE
        self.frame_left = tk.Frame(self.paned, bg="#252526")
        self.paned.add(self.frame_left, width=500)
        
        self.grp_meta = tk.LabelFrame(self.frame_left, text=self.t("lab_grp_id"), bg="#252526", fg="#007acc", font=("Segoe UI", 9, "bold"))
        self.grp_meta.pack(fill="x", padx=10, pady=5)
        
        self._entry_row(self.grp_meta, self.t("lab_lbl_name"), self.var_nom)
        
        f_type = tk.Frame(self.grp_meta, bg="#252526")
        f_type.pack(fill="x", padx=5, pady=2)
        tk.Label(f_type, text=self.t("lab_lbl_cat"), fg="#d4d4d4", bg="#252526", width=15, anchor="w").pack(side="left")
        self.cb_type = ttk.Combobox(f_type, textvariable=self.var_type, values=[self.t("lab_cat_traj"), self.t("lab_cat_wave")], state="readonly")
        self.cb_type.pack(side="right", fill="x", expand=True)
        self.cb_type.bind("<<ComboboxSelected>>", self.on_type_change)

        self._entry_row(self.grp_meta, self.t("lab_lbl_desc"), self.var_desc)

        self.grp_params = tk.LabelFrame(self.frame_left, text=self.t("lab_grp_param"), bg="#252526", fg="#007acc", font=("Segoe UI", 9, "bold"))
        self.grp_params.pack(fill="x", padx=10, pady=5)
        
        self.tree_params = ttk.Treeview(self.grp_params, columns=("Nom", "Defaut"), show="headings", height=4)
        self.tree_params.heading("Nom", text=self.t("lab_col_name"))
        self.tree_params.heading("Defaut", text=self.t("lab_col_def"))
        self.tree_params.column("Nom", width=150)
        self.tree_params.column("Defaut", width=100)
        self.tree_params.pack(fill="x", padx=5, pady=5)
        
        f_btn_p = tk.Frame(self.grp_params, bg="#252526")
        f_btn_p.pack(fill="x", padx=5, pady=2)
        tk.Button(f_btn_p, text=self.t("lab_btn_add"), command=self.add_param_dialog, bg="#3e3e42", fg="white", bd=0, padx=5).pack(side="left")
        tk.Button(f_btn_p, text=self.t("lab_btn_del"), command=self.del_param, bg="#3e3e42", fg="white", bd=0, padx=5).pack(side="left", padx=5)
        
        # PARAMETRES PAR DEFAUT TRADUITS
        self.tree_params.insert("", "end", values=(self.t("p_amplitude"), "2.0"))
        self.tree_params.insert("", "end", values=(self.t("p_nb_lines"), "12.0"))
        self.tree_params.insert("", "end", values=(self.t("p_phase"), "0.0"))

        self.grp_code = tk.LabelFrame(self.frame_left, text=self.t("lab_grp_code"), bg="#252526", fg="#007acc", font=("Segoe UI", 9, "bold"))
        self.grp_code.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.f_snippets = tk.Frame(self.grp_code, bg="#252526")
        self.f_snippets.pack(fill="x", padx=5, pady=2)
        snippets = ["math.sin()", "math.cos()", "math.pi", "abs()", "math.radians()", "t", "amplitude", "nb_lines"]
        for s in snippets:
            tk.Button(self.f_snippets, text=s, command=lambda x=s: self.insert_code(x), bg="#333333", fg="#d4d4d4", bd=0, font=("Consolas", 8)).pack(side="left", padx=1)

        self.txt_code = tk.Text(self.grp_code, bg="#1e1e1e", fg="#d4d4d4", font=("Consolas", 10), insertbackground="white", height=10)
        self.txt_code.pack(fill="both", expand=True, padx=5, pady=5)
        
        # CODE INITIAL TRADUIT
        v_amp = self.t("p_amplitude")
        v_nb = self.t("p_nb_lines")
        code_init = self.t("lab_code_wave") + f"\n\nval = t * {v_nb}\nresult = {v_amp} * math.sin(val)"
        self.txt_code.insert("1.0", code_init)

        f_act = tk.Frame(self.frame_left, bg="#252526", pady=10)
        f_act.pack(fill="x")
        tk.Button(f_act, text=self.t("lab_btn_preview"), command=self.update_preview, bg="#007acc", fg="white", bd=0, font=("Segoe UI", 10, "bold"), padx=10, pady=5).pack(side="right", padx=10)

        # DROITE
        self.frame_right = tk.Frame(self.paned, bg="#1e1e1e")
        self.paned.add(self.frame_right)
        
        tk.Label(self.frame_right, text=self.t("lab_grp_preview"), fg="#969696", bg="#1e1e1e").pack(pady=5)
        self.canvas = tk.Canvas(self.frame_right, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.footer = tk.Frame(self.frame_right, bg="#333333", height=50)
        self.footer.pack(fill="x", side="bottom")
        tk.Button(self.footer, text=self.t("lab_btn_save"), command=self.save_to_library, bg="#4CAF50", fg="white", bd=0, font=("Segoe UI", 11, "bold"), padx=20, pady=10).pack(fill="both", expand=True, padx=5, pady=5)

    def t(self, key):
        if self.app: return self.app.t(key)
        return key

    def _entry_row(self, parent, label, var):
        f = tk.Frame(parent, bg="#252526")
        f.pack(fill="x", padx=5, pady=2)
        tk.Label(f, text=label, fg="#d4d4d4", bg="#252526", width=15, anchor="w").pack(side="left")
        tk.Entry(f, textvariable=var, bg="#3e3e42", fg="white", insertbackground="white", bd=0).pack(side="right", fill="x", expand=True)

    def insert_code(self, text):
        self.txt_code.insert(tk.INSERT, text)
        self.txt_code.focus()

    def add_param_dialog(self):
        self.tree_params.insert("", "end", values=("nouveau_param", "1.0"))

    def del_param(self):
        sel = self.tree_params.selection()
        for s in sel: self.tree_params.delete(s)

    def on_type_change(self, event):
        t_val = self.var_type.get()
        if t_val == self.t("lab_cat_traj"):
            v_long = self.t("p_longueur")
            code_txt = self.t("lab_code_traj") + f"\n\n{v_long} = params.get('{v_long}', 100)\nx = t * {v_long}\ny = 0\nnx, ny = 0, 1\n\n# La variable de sortie doit être un tuple\nresult = ((x, y), (nx, ny))"
            self.txt_code.delete("1.0", tk.END)
            self.txt_code.insert("1.0", code_txt)
        else:
            v_amp = self.t("p_amplitude")
            v_nb = self.t("p_nb_lines")
            code_txt = self.t("lab_code_wave") + f"\n\nval = t * {v_nb}\nresult = {v_amp} * math.sin(val)"
            self.txt_code.delete("1.0", tk.END)
            self.txt_code.insert("1.0", code_txt)

    def update_preview(self):
        self.canvas.delete("all")
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        cy = h / 2
        params = {}
        for item in self.tree_params.get_children():
            vals = self.tree_params.item(item)["values"]
            try: params[vals[0]] = float(vals[1])
            except: pass
        user_code = self.txt_code.get("1.0", tk.END)
        points = []
        try:
            local_context = {"math": math, "abs": abs, "params": params}
            steps = 200
            for i in range(steps):
                t = i / (steps - 1)
                local_context["t"] = t
                for k, v in params.items(): local_context[k] = v
                exec(user_code, {}, local_context)
                res = local_context.get("result", 0)
                
                is_traj = (self.var_type.get() == self.t("lab_cat_traj"))
                if not is_traj:
                    px = t * w
                    py = cy - (res * 10) 
                    points.extend([px, py])
                else:
                    pos, vec = res
                    px = w/2 + pos[0] - 50 
                    py = h/2 - pos[1]
                    points.extend([px, py])

            if len(points) >= 4:
                self.canvas.create_line(points, fill="#00ff00", width=2)
            else:
                self.canvas.create_text(w/2, h/2, text="Pas de points", fill="red")
        except Exception as e:
            self.canvas.create_text(w/2, h/2, text=f"Erreur: {str(e)}", fill="red", width=w-20)

    def save_to_library(self):
        name = self.var_nom.get().strip()
        filename = name.lower().replace(" ", "_") + ".py"
        cat_disp = self.var_type.get()
        if cat_disp == self.t("lab_cat_traj"):
            cat_internal = "Trajectoire Base"
            target_dir_name = "Trajectoires"
        else:
            cat_internal = "Type d'Onde"
            target_dir_name = "Ondes"
            
        desc = self.var_desc.get()
        base_dir = os.path.join(os.path.dirname(__file__), "lib_courbes")
        target_dir = os.path.join(base_dir, target_dir_name)
        full_path = os.path.join(target_dir, filename)
        
        params_dict_str = "{\n"
        for item in self.tree_params.get_children():
            vals = self.tree_params.item(item)["values"]
            params_dict_str += f'        "{vals[0]}": {vals[1]},\n'
        params_dict_str += "    }"
        
        user_code = self.txt_code.get("1.0", tk.END).strip()
        indented_code = "\n    ".join(user_code.splitlines())
        
        func_def = "def get_offset(t, params):" if cat_internal == "Type d'Onde" else "def get_trajectoire(t, params):"
        return_stmt = "return result"
        
        file_content = f'''# -*- coding: utf-8 -*-
import math

INFO = {{
    "nom": "{name}",
    "categorie": "{cat_internal}",
    "version": "1.0",
    "description": "{desc}",
    "formule": "Généré par Formula Lab",
    "params_defaut": {params_dict_str}
}}

{func_def}
    {indented_code}
    {return_stmt}
'''
        try:
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(file_content)
            if self.on_update_callback:
                try: self.on_update_callback()
                except: pass
            messagebox.showinfo(self.t("msg_success"), f"Fichier sauvegardé !")
            self.destroy()
        except Exception as e:
            messagebox.showerror(self.t("msg_error"), f"Échec: {e}")
