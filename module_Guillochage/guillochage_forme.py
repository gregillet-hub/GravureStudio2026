# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk

class FormePanel:
    def __init__(self, parent, app_instance=None, on_change_callback=None):
        self.parent = parent
        self.app = app_instance
        self.on_change_callback = on_change_callback
        
        self.frame = tk.Frame(self.parent, bg="#252526")
        self.frame.pack(fill="both", expand=True, padx=5, pady=5)

        # 1. Type de forme
        self.lbl_type = tk.Label(self.frame, text="Type de forme :", fg="#d4d4d4", bg="#252526", font=("Segoe UI", 9))
        self.lbl_type.pack(anchor="w")
        
        self.forme_var = tk.StringVar()
        self.combo_forme = ttk.Combobox(self.frame, textvariable=self.forme_var, state="readonly", font=("Segoe UI", 9))
        self.combo_forme['values'] = ["Cercle / Ovale", "Carré / Rectangle"]
        self.combo_forme.current(0)
        self.combo_forme.pack(fill="x", pady=(0, 10))
        self.combo_forme.bind("<<ComboboxSelected>>", self.on_ui_change)

        # 2. Dimensions
        self.frame_dims = tk.Frame(self.frame, bg="#252526")
        self.frame_dims.pack(fill="x")

        self.var_dim1, self.lbl_dim1 = self.create_dim_block(self.frame_dims, 0, "Diamètre X / Largeur", 50.0)
        self.var_dim2, self.lbl_dim2 = self.create_dim_block(self.frame_dims, 1, "Diamètre Y / Hauteur", 50.0)

        # 3. Rayon de coin (Optionnel pour Rectangle)
        self.frame_radius = tk.Frame(self.frame, bg="#252526")
        
        self.var_radius_active = tk.BooleanVar(value=True)
        self.chk_radius = tk.Checkbutton(self.frame_radius, text="Rayon (mm)", variable=self.var_radius_active, 
                                        bg="#252526", fg="#d4d4d4", selectcolor="#3e3e42", 
                                        activebackground="#252526", command=self.on_ui_change)
        self.chk_radius.pack(side="left")
        
        self.var_radius = tk.DoubleVar(value=5.0)
        self.spin_radius = tk.Spinbox(self.frame_radius, from_=0.0, to=100.0, increment=0.5, 
                                     textvariable=self.var_radius, bg="#3e3e42", fg="white", 
                                     bd=0, width=8, command=self.on_ui_change)
        self.spin_radius.pack(side="left", padx=5)
        self.spin_radius.bind("<KeyRelease>", self.on_ui_change)

        # Initialisation de l'affichage
        self.on_ui_change()

    def create_dim_block(self, parent, row, label_text, default_val):
        lbl = tk.Label(parent, text=label_text, fg="#d4d4d4", bg="#252526", font=("Segoe UI", 8))
        lbl.grid(row=row, column=0, sticky="w")
        var = tk.DoubleVar(value=default_val)
        spin = tk.Spinbox(parent, from_=0.1, to=1000.0, increment=1.0, textvariable=var, 
                          bg="#3e3e42", fg="white", bd=0, width=10, command=self.on_ui_change)
        spin.grid(row=row, column=1, sticky="ew", padx=5, pady=2)
        spin.bind("<KeyRelease>", self.on_ui_change)
        return var, lbl

    def on_ui_change(self, event=None):
        idx = self.combo_forme.current()
        # 0 = Cercle, 1 = Rectangle
        if idx == 0:
            self.lbl_dim1.config(text="Diamètre X (mm)")
            self.lbl_dim2.config(text="Diamètre Y (mm)")
            self.frame_radius.pack_forget()
        else:
            self.lbl_dim1.config(text="Largeur (mm)")
            self.lbl_dim2.config(text="Hauteur (mm)")
            self.frame_radius.pack(fill="x", pady=5)
            # Gestion état spinbox rayon
            state = "normal" if self.var_radius_active.get() else "disabled"
            self.spin_radius.config(state=state)

        if self.on_change_callback:
            self.on_change_callback(self.get_shape_data())

    def get_shape_data(self):
        try: d1 = float(self.var_dim1.get())
        except: d1 = 50.0
        try: d2 = float(self.var_dim2.get())
        except: d2 = 50.0
        
        idx = self.combo_forme.current()
        radius = 0.0
        if idx == 1 and self.var_radius_active.get():
            try: radius = float(self.var_radius.get())
            except: radius = 0.0
            
        return {
            "type_index": idx, # 0=Cercle, 1=Rect
            "dim1": d1,
            "dim2": d2,
            "radius": radius
        }
    
    def set_shape_data(self, data):
        if not data: return
        self.combo_forme.current(data.get("type_index", 0))
        self.var_dim1.set(data.get("dim1", 50.0))
        self.var_dim2.set(data.get("dim2", 50.0))
        self.var_radius.set(data.get("radius", 0.0))
        self.on_ui_change()
