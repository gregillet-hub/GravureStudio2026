# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, colorchooser
import os
import glob

class ToolTip:
    def __init__(self, widget, text_getter):
        self.widget = widget
        self.text_getter = text_getter
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)
    def show_tip(self, event=None):
        val = self.text_getter() if callable(self.text_getter) else self.text_getter
        if self.tip_window or not val: return
        try:
            x, y, cx, cy = self.widget.bbox("insert")
            x += self.widget.winfo_rootx() + 25
            y += self.widget.winfo_rooty() + 25
            self.tip_window = tw = tk.Toplevel(self.widget)
            tw.wm_overrideredirect(True)
            tw.wm_geometry(f"+{x}+{y}")
            label = tk.Label(tw, text=val, justify=tk.LEFT, background="#ffffe0", relief=tk.SOLID, borderwidth=1, font=("Segoe UI", 8))
            label.pack(ipadx=1)
        except: pass
    def hide_tip(self, event=None):
        if self.tip_window: self.tip_window.destroy(); self.tip_window = None

class CourbesPanel:
    def __init__(self, parent, app_instance=None, on_change_callback=None, on_calque_modified_callback=None):
        self.parent = parent
        self.app = app_instance
        self.on_change_callback = on_change_callback
        self.on_calque_modified_callback = on_calque_modified_callback
        self.current_calque_color = "#555555"
        self.is_updating = False
        
        # Gestion Résolution
        self.res_keys = ["z4_val_res_low", "z4_val_res_med", "z4_val_res_high", "z4_val_res_ultra"]
        self.res_internal = ["Faible (Rapide)", "Moyenne", "Haute", "Ultra (Export)"]
        
        self.map_traj_disp_to_int = {}
        self.map_traj_int_to_disp = {}
        self.map_wave_disp_to_int = {}
        self.map_wave_int_to_disp = {}

        # --- Header ---
        self.main_frame = tk.Frame(self.parent, bg="#252526")
        self.main_frame.pack(fill="both", expand=True)
        self.header_frame = tk.Frame(self.main_frame, bg="#333333", pady=5)
        self.header_frame.pack(fill="x", side="top", pady=(0, 5))
        
        self.color_indicator = tk.Canvas(self.header_frame, width=16, height=16, bg="#333333", highlightthickness=0, cursor="hand2")
        self.color_indicator.pack(side="left", padx=(10, 5))
        self.rect_color = self.color_indicator.create_rectangle(0, 0, 16, 16, fill="#555", outline="#777")
        self.color_indicator.bind("<Button-1>", self.on_header_color_click)
        
        self.var_calque_name = tk.StringVar(value="Aucun")
        self.entry_calque_name = tk.Entry(self.header_frame, textvariable=self.var_calque_name, bg="#333333", fg="white", bd=0, font=("Segoe UI", 10, "bold"), width=15)
        self.entry_calque_name.pack(side="left", padx=5)
        self.entry_calque_name.bind("<Return>", self.on_header_name_change)
        self.entry_calque_name.bind("<FocusOut>", self.on_header_name_change)

        # --- Groupe 1: Définition ---
        self.group_def = tk.LabelFrame(self.main_frame, text="Définition", bg="#252526", fg="#969696", font=("Segoe UI", 8, "bold"), bd=1, relief="flat")
        self.group_def.pack(fill="x", padx=5, pady=2)
        
        self.var_traj_display = tk.StringVar()
        self.combo_traj = ttk.Combobox(self.group_def, textvariable=self.var_traj_display, state="readonly")
        self.combo_traj.bind("<<ComboboxSelected>>", self.on_change)
        self.combo_traj.pack(fill="x", padx=10, pady=2)
        
        self.var_wave_display = tk.StringVar()
        self.combo_wave = ttk.Combobox(self.group_def, textvariable=self.var_wave_display, state="readonly")
        self.combo_wave.bind("<<ComboboxSelected>>", self.on_change)
        self.combo_wave.pack(fill="x", padx=10, pady=2)

        # --- Groupe 2: Paramètres Géométriques ---
        self.group_params = tk.LabelFrame(self.main_frame, text="Géométrie", bg="#2d2d30", fg="#007acc", font=("Segoe UI", 9, "bold"), bd=1, relief="solid")
        self.group_params.pack(fill="x", padx=5, pady=10)
        self.grid_frame = tk.Frame(self.group_params, bg="#2d2d30")
        self.grid_frame.pack(fill="x", padx=5, pady=5)
        self.grid_frame.columnconfigure(0, weight=1)
        self.grid_frame.columnconfigure(1, weight=1)

        # Grille de paramètres
        self.var_nb_lines = self.create_grid_input(0, 0, 10.0, "Nb Lignes", step=1)
        self.var_amp = self.create_grid_input(0, 1, 2.0, "Amplitude", step=0.1)
        
        self.var_period = self.create_grid_input(1, 0, 10.0, "Nb Périodes", step=1)
        self.var_phase = self.create_grid_input(1, 1, 0.0, "Phase", step=0.1)
        
        self.var_rot = self.create_grid_input(2, 0, 0.0, "Rotation", step=1)
        # La thickness est déplacée en bas
        
        self.var_pos_x = self.create_grid_input(3, 0, 0.0, "Pos X", step=0.5)
        self.var_pos_y = self.create_grid_input(3, 1, 0.0, "Pos Y", step=0.5)

        # --- Groupe 3: Finition ---
        self.group_fin = tk.LabelFrame(self.main_frame, text="Finition", bg="#252526", fg="#969696", font=("Segoe UI", 8, "bold"), bd=1, relief="flat")
        self.group_fin.pack(fill="x", padx=5, pady=5)
        
        # --- AJOUT RÉSOLUTION (RESTAURÉ) ---
        f_res = tk.Frame(self.group_fin, bg="#252526")
        f_res.pack(fill="x", padx=10, pady=2)
        self.lbl_res = tk.Label(f_res, text="Résolution", fg="#d4d4d4", bg="#252526", width=15, anchor="w")
        self.lbl_res.pack(side="left")
        
        self.combo_res = ttk.Combobox(f_res, state="readonly")
        self.combo_res["values"] = self.res_internal
        if self.res_internal: self.combo_res.current(1) # Moyenne par défaut
        self.combo_res.bind("<<ComboboxSelected>>", self.on_change)
        self.combo_res.pack(side="right", fill="x", expand=True)
        
        # Paramètres de finition
        self.var_thickness = self.create_input_row(self.group_fin, 1.0, "Épaisseur")
        self.var_margin_in = self.create_input_row(self.group_fin, 0.0, "Marge (Haut/Bas)", step=0.5)
        
        self.var_flambage = tk.BooleanVar(value=False)
        self.chk_flambage = tk.Checkbutton(self.group_fin, text="Activer Flambage", variable=self.var_flambage, bg="#252526", fg="#007acc", selectcolor="#252526", activebackground="#252526", command=self.on_change)
        self.chk_flambage.pack(anchor="w", padx=10)
        
        self.frame_flambage = tk.Frame(self.group_fin, bg="#252526")
        self.var_amp_start = self.create_input_row(self.frame_flambage, 1.0, "Amp Début")
        self.var_amp_end = self.create_input_row(self.frame_flambage, 3.0, "Amp Fin")
        
        self.refresh_library()
        self.toggle_flambage()

    def t(self, key):
        if self.app: return self.app.t(key)
        return key

    def create_grid_input(self, r, c, default, lbl, step=0.1):
        f = tk.Frame(self.grid_frame, bg="#2d2d30")
        f.grid(row=r, column=c, sticky="ew", padx=2, pady=2)
        tk.Label(f, text=lbl, fg="#d4d4d4", bg="#2d2d30", font=("Segoe UI", 8)).pack(anchor="w")
        v = tk.StringVar(value=str(default))
        s = tk.Spinbox(f, from_=-9999, to=9999, increment=step, textvariable=v, bg="#3e3e42", fg="white", bd=0, command=self.on_change)
        s.pack(fill="x")
        s.bind("<Return>", self.on_change)
        s.bind("<FocusOut>", self.on_change)
        return v

    def create_input_row(self, parent, default, lbl, step=0.1):
        f = tk.Frame(parent, bg="#252526")
        f.pack(fill="x", padx=10, pady=2)
        tk.Label(f, text=lbl, fg="#d4d4d4", bg="#252526", width=15, anchor="w").pack(side="left")
        v = tk.StringVar(value=str(default))
        s = tk.Spinbox(f, from_=-9999, to=9999, increment=step, textvariable=v, bg="#3e3e42", fg="white", bd=0, command=self.on_change)
        s.pack(side="right", fill="x", expand=True)
        s.bind("<Return>", self.on_change)
        s.bind("<FocusOut>", self.on_change)
        return v

    def _get_safe(self, var, default=0.0):
        try:
            val = var.get().replace(",", ".")
            if not val or val == "-": return default
            return float(val)
        except ValueError:
            return default

    def get_current_params(self):
        # Récupération Résolution
        res_idx = self.combo_res.current()
        res_val = self.res_internal[res_idx] if res_idx != -1 and res_idx < len(self.res_internal) else "Moyenne"

        return {
            "traj_type": self.map_traj_disp_to_int.get(self.var_traj_display.get(), "Ligne Droite"),
            "wave_type": self.map_wave_disp_to_int.get(self.var_wave_display.get(), "Sinus"),
            "nb_lines": self._get_safe(self.var_nb_lines, 10.0),
            "amplitude": self._get_safe(self.var_amp, 2.0),
            "period": self._get_safe(self.var_period, 10.0),
            "phase": self._get_safe(self.var_phase, 0.0),
            "rotation": self._get_safe(self.var_rot, 0.0),
            "pos_x": self._get_safe(self.var_pos_x, 0.0),
            "pos_y": self._get_safe(self.var_pos_y, 0.0),
            "thickness": self._get_safe(self.var_thickness, 1.0),
            "margin_in": self._get_safe(self.var_margin_in, 0.0),
            "flambage": self.var_flambage.get(),
            "amp_start": self._get_safe(self.var_amp_start, 1.0),
            "amp_end": self._get_safe(self.var_amp_end, 3.0),
            "resolution": res_val # Ajouté
        }

    def set_params(self, data):
        self.is_updating = True
        int_traj = data.get("traj_type", "Ligne Droite")
        int_wave = data.get("wave_type", "Sinus")
        self.var_traj_display.set(self.map_traj_int_to_disp.get(int_traj, int_traj))
        self.var_wave_display.set(self.map_wave_int_to_disp.get(int_wave, int_wave))
        
        nb = float(data.get("nb_lines", 10.0))
        self.var_nb_lines.set(str(int(nb)) if nb.is_integer() else str(nb))
        
        self.var_amp.set(str(data.get("amplitude", 2.0)))
        per = float(data.get("period", 10.0))
        self.var_period.set(str(int(per)) if per.is_integer() else str(per))
        
        self.var_phase.set(str(data.get("phase", 0.0)))
        self.var_rot.set(str(data.get("rotation", 0.0)))
        self.var_pos_x.set(str(data.get("pos_x", 0.0)))
        self.var_pos_y.set(str(data.get("pos_y", 0.0)))
        self.var_thickness.set(str(data.get("thickness", 1.0)))
        self.var_margin_in.set(str(data.get("margin_in", 0.0)))
        self.var_flambage.set(data.get("flambage", False))
        self.var_amp_start.set(str(data.get("amp_start", 1.0)))
        self.var_amp_end.set(str(data.get("amp_end", 3.0)))
        
        # Restauration Résolution
        res_val = data.get("resolution", "Moyenne")
        try:
            idx = self.res_internal.index(res_val)
            self.combo_res.current(idx)
        except:
            if self.res_internal: self.combo_res.current(1)
        
        self.toggle_flambage()
        self.is_updating = False

    def toggle_flambage(self):
        if self.var_flambage.get(): self.frame_flambage.pack(fill="x", padx=10, pady=5)
        else: self.frame_flambage.pack_forget()
        self.on_change()

    def on_change(self, event=None):
        if not self.is_updating and self.on_change_callback:
            self.on_change_callback()

    def update_active_layer(self, name, color):
        self.var_calque_name.set(name)
        self.current_calque_color = color
        self.color_indicator.itemconfig(self.rect_color, fill=color)

    def on_header_name_change(self, event=None):
        if self.on_calque_modified_callback: self.on_calque_modified_callback(self.var_calque_name.get(), self.current_calque_color)
        self.parent.focus()

    def on_header_color_click(self, event=None):
        color = colorchooser.askcolor(title="Couleur", initialcolor=self.current_calque_color)[1]
        if color:
            self.current_calque_color = color
            self.color_indicator.itemconfig(self.rect_color, fill=color)
            if self.on_calque_modified_callback: self.on_calque_modified_callback(self.var_calque_name.get(), color)

    def refresh_library(self):
        base = os.path.join(os.path.dirname(__file__), "lib_courbes")
        
        traj_path = os.path.join(base, "Trajectoires")
        traj_files = glob.glob(os.path.join(traj_path, "*.py"))
        display_traj = []
        for f in traj_files:
            name = os.path.basename(f).replace(".py", "")
            display = name.replace("_", " ").title()
            self.map_traj_disp_to_int[display] = name
            self.map_traj_int_to_disp[name] = display
            display_traj.append(display)
        self.combo_traj['values'] = display_traj
        if display_traj: self.combo_traj.current(0)
        
        wave_path = os.path.join(base, "Ondes")
        wave_files = glob.glob(os.path.join(wave_path, "*.py"))
        display_wave = []
        for f in wave_files:
            name = os.path.basename(f).replace(".py", "")
            display = name.replace("_", " ").title()
            self.map_wave_disp_to_int[display] = name
            self.map_wave_int_to_disp[name] = display
            display_wave.append(display)
        self.combo_wave['values'] = display_wave
        if display_wave: self.combo_wave.current(0)