# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk
from tkinter import colorchooser

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
            x+=self.widget.winfo_rootx()+25
            y+=self.widget.winfo_rooty()+25
            self.tip_window = tw = tk.Toplevel(self.widget)
            tw.wm_overrideredirect(True)
            tw.wm_geometry(f"+{x}+{y}")
            label = tk.Label(tw, text=val, justify=tk.LEFT, background="#ffffe0", relief=tk.SOLID, borderwidth=1, font=("Segoe UI", 8, "normal"))
            label.pack(ipadx=1)
        except: pass
    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

class CalqueRow(tk.Frame):
    def __init__(self, parent, panel_manager, name="Nouveau Calque", color="#ff0000", data=None):
        super().__init__(parent, bg="#2d2d30", pady=1)
        self.manager = panel_manager
        self.name = name
        self.color = color 
        
        # Données par défaut ou chargées
        if data:
            self.data = data
        else:
            self.data = {
                "global": {
                    "traj_type": "Ligne Droite", "wave_type": "Sinus", "preset": "Défaut",
                    "nb_lines": 12.0, "amplitude": 2.0, "invert": False, "height": 10.0,
                    "period": 1.0, "phase": 0.0, "rotation": 0.0, "pos_x": 0.0, "pos_y": 0.0,
                    "thickness": 1.0, "margin_in": 0.0, "margin_out": 0.0,
                    "flambage": False, "amp_start": 1.0, "amp_end": 3.0, "resolution": "Moyenne",
                    "mirror_h": False, "mirror_v": False
                },
                "lines": []
            }
            self.regenerate_lines()

        self.is_visible = True
        self.btn_eye = tk.Button(self, text="👁", command=self.toggle_visible, bg="#2d2d30", fg="#d4d4d4", bd=0, width=2, cursor="hand2")
        self.btn_eye.pack(side="left", padx=2)
        ToolTip(self.btn_eye, lambda: self.manager.t("z2_tt_eye"))

        self.is_locked = False
        self.btn_lock = tk.Button(self, text="🔓", command=self.toggle_lock, bg="#2d2d30", fg="#969696", bd=0, width=2, cursor="hand2")
        self.btn_lock.pack(side="left", padx=0)
        ToolTip(self.btn_lock, lambda: self.manager.t("z2_tt_lock"))

        self.color_frame = tk.Frame(self, bg=self.color, width=15, height=15, cursor="hand2")
        self.color_frame.pack(side="left", padx=5)
        self.color_frame.bind("<Button-1>", self.change_color_manual)
        ToolTip(self.color_frame, lambda: self.manager.t("z2_tt_color"))

        self.var_name = tk.StringVar(value=name)
        self.entry_name = tk.Entry(self, textvariable=self.var_name, bg="#2d2d30", fg="#d4d4d4", bd=0, insertbackground="white", font=("Segoe UI", 9))
        self.entry_name.pack(side="left", fill="x", expand=True, padx=5)
        self.entry_name.bind("<FocusIn>", self.select_me)
        self.entry_name.bind("<KeyRelease>", self.on_rename_typing)
        self.bind("<Button-1>", self.select_me)

    def regenerate_lines(self):
        try: nb = int(self.data["global"]["nb_lines"])
        except: nb = 1
        current_lines = self.data["lines"]
        new_lines = []
        for i in range(nb):
            if i < len(current_lines): 
                current_lines[i]["id"] = i + 1
                new_lines.append(current_lines[i])
            else: 
                new_lines.append({"id": i + 1, "is_active": True, "override": {}})
        self.data["lines"] = new_lines

    def update_params_from_zone4(self, new_params, target_line_index=None):
        if self.is_locked: return

        if target_line_index is None:
            self.data["global"].update(new_params)
            self.regenerate_lines()
        else:
            if target_line_index < len(self.data["lines"]):
                line_data = self.data["lines"][target_line_index]
                override = line_data.get("override", {})
                global_data = self.data["global"]
                for key, value in new_params.items():
                    if value != global_data.get(key): override[key] = value
                    else: 
                        if key in override: del override[key]
                self.data["lines"][target_line_index]["override"] = override

    def delete_line_at(self, index):
        if self.is_locked: return 
        if 0 <= index < len(self.data["lines"]):
            del self.data["lines"][index]
            self.data["global"]["nb_lines"] = float(len(self.data["lines"]))
            for i, line in enumerate(self.data["lines"]): line["id"] = i + 1

    def insert_lines_at(self, index, lines_to_insert):
        if self.is_locked: return 
        insert_pos = index + 1
        copies = []
        for line in lines_to_insert:
            import copy
            new_line = copy.deepcopy(line)
            new_line["id"] = 0
            copies.append(new_line)
        self.data["lines"][insert_pos:insert_pos] = copies
        self.data["global"]["nb_lines"] = float(len(self.data["lines"]))
        for i, line in enumerate(self.data["lines"]): line["id"] = i + 1

    @property
    def params(self): return self.data["global"]

    def on_rename_typing(self, event=None): 
        if self.is_locked: return 
        self.manager.notify_update(self)
        
    def change_color_manual(self, event=None):
        if self.is_locked: return 
        color = colorchooser.askcolor(title="Choisir une couleur", initialcolor=self.color)[1]
        if color:
            self.update_visuals(self.var_name.get(), color)
            self.manager.notify_update(self) 

    def update_visuals(self, name, color):
        self.color = color
        self.var_name.set(name)
        self.color_frame.config(bg=color)

    def toggle_visible(self):
        self.is_visible = not self.is_visible
        self.btn_eye.config(text="👁" if self.is_visible else "🚫", fg="#d4d4d4" if self.is_visible else "#666")
        self.manager.notify_change()

    def toggle_lock(self):
        self.is_locked = not self.is_locked
        self.update_lock_visuals()

    def set_lock(self, state):
        self.is_locked = state
        self.update_lock_visuals()

    def update_lock_visuals(self):
        self.btn_lock.config(text="🔒" if self.is_locked else "🔓", fg="#d4d4d4" if self.is_locked else "#969696")
        self.entry_name.config(state="disabled" if self.is_locked else "normal")

    def set_visible(self, state):
        self.is_visible = state
        self.btn_eye.config(text="👁" if self.is_visible else "🚫", fg="#d4d4d4" if self.is_visible else "#666")
        
    def select_me(self, event=None): self.manager.select_row(self)
    
    def set_selected_visual(self, is_selected):
        bg_color = "#007acc" if is_selected else "#2d2d30"
        fg_text = "white" if is_selected else "#d4d4d4"
        self.config(bg=bg_color)
        self.entry_name.config(bg=bg_color, fg=fg_text)
        self.btn_eye.config(bg=bg_color)
        self.btn_lock.config(bg=bg_color)

class CalquesPanel:
    def __init__(self, parent_frame, app_instance=None, on_select_callback=None):
        self.parent = parent_frame
        self.app = app_instance
        self.on_select_callback = on_select_callback
        self.rows = []
        self.selected_row = None
        self.palette = ["#e6194b", "#3cb44b", "#ffe119", "#4363d8", "#f58231", "#911eb4", "#46f0f0", "#f032e6", "#bcf60c", "#fabebe", "#008080", "#e6beff", "#9a6324", "#fffac8", "#800000", "#aaffc3", "#808000", "#ffd8b1", "#000075", "#808080"]
        self.color_index = 0
        self.toolbar = tk.Frame(self.parent, bg="#252526")
        self.toolbar.pack(side="top", fill="x", pady=(0, 5))
        
        self.buttons_config = [
            ("+", "z2_tt_add", self.action_add), 
            ("⎘", "z2_tt_dup", self.action_duplicate), 
            ("🗑️", "z2_tt_del", self.action_delete), 
            ("↑", "z2_tt_up", self.action_up), 
            ("↓", "z2_tt_down", self.action_down), 
            ("↔", "z2_tt_mir_h", self.action_mirror_h), 
            ("↕", "z2_tt_mir_v", self.action_mirror_v), 
            ("↻", "z2_tt_rot", self.action_rotate)
        ]
        
        for i, (text, tip_key, cmd) in enumerate(self.buttons_config):
            self.toolbar.columnconfigure(i, weight=1)
            btn = tk.Button(self.toolbar, text=text, command=cmd, bg="#333333", fg="white", bd=0, cursor="hand2", activebackground="#007acc", activeforeground="white")
            btn.grid(row=0, column=i, sticky="ew", padx=1)
            ToolTip(btn, lambda k=tip_key: self.t(k))

        self.list_container = tk.Frame(self.parent, bg="#252526")
        self.list_container.pack(fill="both", expand=True)
        self.action_add()

    def t(self, key):
        if self.app: return self.app.t(key)
        return key
        
    def refresh_ui(self): pass

    def notify_change(self):
        if self.app and hasattr(self.app, 'trigger_calculation'):
            self.app.trigger_calculation()

    def update_active_calque_data(self, name, color):
        if self.selected_row: self.selected_row.update_visuals(name, color)
    def notify_update(self, row):
        if self.selected_row == row and self.on_select_callback: self.on_select_callback(row.var_name.get(), row.color, row.data)
    def get_next_color(self):
        color = self.palette[self.color_index % len(self.palette)]
        self.color_index += 1
        return color
    def select_row(self, row_object):
        if self.selected_row and self.selected_row != row_object: self.selected_row.set_selected_visual(False)
        self.selected_row = row_object
        self.selected_row.set_selected_visual(True)
        if self.on_select_callback: self.on_select_callback(self.selected_row.var_name.get(), self.selected_row.color, self.selected_row.data)
    
    def add_calque_row(self, name, color=None, data=None):
        if color is None: color = self.get_next_color()
        row = CalqueRow(self.list_container, self, name, color, data)
        row.pack(fill="x", pady=1)
        self.rows.append(row)
        self.select_row(row)
        self.notify_change()
    
    def refresh_view(self):
        for row in self.rows: row.pack_forget()
        for row in self.rows: row.pack(fill="x", pady=1)
    
    def action_add(self):
        count = len(self.rows) + 1
        self.add_calque_row(f"Calque {count}")
    
    def action_delete(self):
        if self.selected_row:
            if self.selected_row.is_locked: return 
            self.selected_row.destroy()
            self.rows.remove(self.selected_row)
            self.selected_row = None 
        if self.rows: 
            self.select_row(self.rows[-1])
            self.notify_change()
        elif not self.rows: 
            self.action_add()
        
    def action_duplicate(self):
        if self.selected_row: 
            import copy
            new_data = copy.deepcopy(self.selected_row.data)
            self.add_calque_row(self.selected_row.var_name.get() + " (Copie)", data=new_data)
            
    def action_up(self):
        if self.selected_row and len(self.rows) > 1:
            idx = self.rows.index(self.selected_row)
            if idx > 0:
                self.rows[idx], self.rows[idx-1] = self.rows[idx-1], self.rows[idx]
                self.refresh_view()
                self.notify_change()
    def action_down(self):
        if self.selected_row and len(self.rows) > 1:
            idx = self.rows.index(self.selected_row)
            if idx < len(self.rows) - 1:
                self.rows[idx], self.rows[idx+1] = self.rows[idx+1], self.rows[idx]
                self.refresh_view()
                self.notify_change()
                
    # --- MIROIR HORIZONTAL (Basculement flag) ---
    def action_mirror_h(self): 
        if self.selected_row:
            if self.selected_row.is_locked: return 
            import copy
            new_data = copy.deepcopy(self.selected_row.data)
            
            # On inverse simplement le flag miroir H pour le nouveau calque
            val = new_data["global"].get("mirror_h", False)
            new_data["global"]["mirror_h"] = not val
            
            self.add_calque_row(f"{self.selected_row.var_name.get()} (Mir H)", data=new_data)

    # --- MIROIR VERTICAL (Basculement flag) ---
    def action_mirror_v(self):
        if self.selected_row:
            if self.selected_row.is_locked: return
            import copy
            new_data = copy.deepcopy(self.selected_row.data)
            
            # On inverse le flag miroir V
            val = new_data["global"].get("mirror_v", False)
            new_data["global"]["mirror_v"] = not val
            
            self.add_calque_row(f"{self.selected_row.var_name.get()} (Mir V)", data=new_data)

    def action_rotate(self):
        if self.selected_row: 
            if self.selected_row.is_locked: return 
            import copy
            new_data = copy.deepcopy(self.selected_row.data)
            current_rot = float(new_data["global"].get("rotation", 0.0))
            new_data["global"]["rotation"] = current_rot + 90.0
            self.add_calque_row(f"{self.selected_row.var_name.get()} (+90°)", data=new_data)

    def get_all_layers_state(self):
        state_list = []
        for row in self.rows:
            layer_state = {
                "name": row.var_name.get(),
                "color": row.color,
                "visible": row.is_visible,
                "locked": row.is_locked,
                "data": row.data 
            }
            state_list.append(layer_state)
        return state_list

    def load_all_layers_state(self, state_list):
        for row in self.rows: row.destroy()
        self.rows = []
        self.selected_row = None
        self.color_index = 0
        
        if not state_list:
            self.action_add()
            return

        for s in state_list:
            name = s.get("name", "Calque")
            color = s.get("color", "#ff0000")
            data = s.get("data", None)
            
            row = CalqueRow(self.list_container, self, name, color, data)
            row.set_visible(s.get("visible", True))
            row.set_lock(s.get("locked", False))
            
            row.pack(fill="x", pady=1)
            self.rows.append(row)
            
        if self.rows: self.select_row(self.rows[0])

    def get_selected_layer_state(self):
        if self.selected_row:
            import copy
            return {
                "type": "layer",
                "data": copy.deepcopy(self.selected_row.data),
                "name": self.selected_row.var_name.get(),
                "color": self.selected_row.color
            }
        return None
        
    def paste_layer_from_clipboard(self, clipboard_content):
        if clipboard_content.get("type") == "layer":
            import copy
            data = copy.deepcopy(clipboard_content["data"])
            name = clipboard_content["name"] + " (Copie)"
            self.add_calque_row(name, data=data)
