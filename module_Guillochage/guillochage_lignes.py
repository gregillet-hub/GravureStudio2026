# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk
from copy import deepcopy

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)
    def show_tip(self, event=None):
        if self.tip_window or not self.text: return
        try:
            if event is not None and getattr(event, 'x_root', None) is not None:
                x = event.x_root + 20
                y = event.y_root + 10
            else:
                try:
                    x, y, _, _ = self.widget.bbox("insert")
                    x = x + self.widget.winfo_rootx() + 25
                    y = y + self.widget.winfo_rooty() + 25
                except Exception:
                    x = self.widget.winfo_rootx() + 20
                    y = self.widget.winfo_rooty() + 20

            self.tip_window = tw = tk.Toplevel(self.widget)
            tw.wm_overrideredirect(True)
            tw.wm_geometry(f"+{x}+{y}")
            label = tk.Label(tw, text=self.text, justify=tk.LEFT, background="#ffffe0", relief=tk.SOLID, borderwidth=1, font=("Segoe UI", 8))
            label.pack(ipadx=1)
        except Exception:
            pass
    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

COL_CONFIG = [
    ("wave_type",  "z5_col_type",   3, str),
    ("invert",     "z5_col_inv",    1,  lambda x: "Oui" if x else "-"),
    ("amplitude",  "z5_col_ampl",   2,  "{:.2f}"),
    ("height",     "z5_col_height", 2,  "{:.1f}"),
    ("period",     "z5_col_period", 1,  "{:.1f}"),
    ("phase",      "z5_col_phase",  1,  "{:.0f}°"),
    ("rotation",   "z5_col_rot",    1,  "{:.0f}°"),
    ("resolution", "z5_col_res",    2,  str),
    ("thickness",  "z5_col_thick",  1,  "{:.1f}"),
    ("flambage",   "z5_col_flb",    1,  lambda x: "Oui" if x else "-")
]

class LigneRow(tk.Frame):
    def __init__(self, parent, manager, index, line_dict, global_params, calque_color):
        super().__init__(parent, bg="#2d2d30", pady=2)
        self.manager = manager
        self.index = index
        self.line_dict = line_dict
        
        self.is_deleted = line_dict.get("is_deleted", False)

        self.final_params = global_params.copy()
        self.final_params.update(line_dict.get("override", {}))
        
        self.has_override = bool(line_dict.get("override"))
        
        if self.is_deleted:
            self.default_fg = "#666666" 
            self.bg_color = "#222222"
        else:
            self.default_fg = "#ffae00" if self.has_override else "#d4d4d4"
            self.bg_color = "#2d2d30"

        self.config(bg=self.bg_color)
        
        self.elements = []
        
        self.var_active = tk.BooleanVar(value=line_dict.get("is_active", True))
        self.chk = tk.Checkbutton(self, variable=self.var_active, bg=self.bg_color, activebackground=self.bg_color, selectcolor="#2d2d30", bd=0, command=self.on_toggle_active)
        self.chk.grid(row=0, column=0, sticky="w", padx=(5, 2))
        if self.is_deleted: self.chk.config(state="disabled")
        self.elements.append(self.chk)

        font_style = ("Segoe UI", 9, "bold" if self.has_override else "normal")
        if self.is_deleted: font_style = ("Segoe UI", 9, "overstrike")
        
        self.lbl_idx = tk.Label(self, text=f"{index + 1:02d}", fg=self.default_fg, bg=self.bg_color, width=3, font=font_style)
        self.lbl_idx.grid(row=0, column=1, sticky="w")
        self.elements.append(self.lbl_idx)

        self.canvas_color = tk.Canvas(self, width=14, height=14, bg=self.bg_color, highlightthickness=0)
        if not self.is_deleted:
            self.canvas_color.create_rectangle(1, 1, 13, 13, fill=calque_color, outline="#555")
        self.canvas_color.grid(row=0, column=2, padx=5)
        self.elements.append(self.canvas_color)

        current_col = 3
        for key, title_key, weight, fmt in COL_CONFIG:
            raw_val = self.final_params.get(key, 0)
            if callable(fmt): val_str = fmt(raw_val)
            elif isinstance(fmt, str): val_str = fmt.format(float(raw_val)) if isinstance(raw_val, (int, float)) else str(raw_val)
            else: val_str = str(raw_val)
            
            if key == "wave_type" or key == "traj_type":
                base_name = str(raw_val).replace(".py", "")
                if base_name.startswith("traj_"): base_name = base_name[5:]
                if base_name.startswith("onde_"): base_name = base_name[5:]
                trans_key = "file_" + base_name.lower()
                translated = self.manager.t(trans_key)
                if translated != trans_key: val_str = translated
                else: val_str = base_name.replace("_", " ").title()
            
            if key == "resolution":
                res_map = {
                    "Faible (Rapide)": "z4_val_res_low", "Moyenne": "z4_val_res_med",
                    "Haute": "z4_val_res_high", "Ultra (Export)": "z4_val_res_ultra"
                }
                if val_str in res_map: val_str = self.manager.t(res_map[val_str])

            if self.is_deleted: val_str = "---"

            l = tk.Label(self, text=val_str, fg="#666" if self.is_deleted else="#969696", bg=self.bg_color, anchor="c", font=("Segoe UI", 9))
            l.grid(row=0, column=current_col, sticky="ew", padx=1)
            self.columnconfigure(current_col, weight=weight)
            self.elements.append(l)
            l.bind("<Button-1>", self.on_simple_click)
            current_col += 1

        self.frame_actions = tk.Frame(self, bg=self.bg_color)
        self.frame_actions.grid(row=0, column=99, sticky="e", padx=(5, 10))
        self.columnconfigure(99, weight=0)
        self.elements.append(self.frame_actions)
        
        btn_edit = tk.Button(self.frame_actions, text="✎", command=self.on_edit_click, bg="#3e3e42", fg="white", bd=0, width=3, cursor="hand2")
        btn_edit.pack(side="left", padx=2)
        if self.is_deleted: btn_edit.config(state="disabled", bg="#222")
        ToolTip(btn_edit, self.manager.t("z5_act_edit"))
        
        can_reset = self.has_override or self.is_deleted
        state_reset = "normal" if can_reset else "disabled"
        fg_reset = "white" if can_reset else "#555"
        
        self.btn_reset = tk.Button(self.frame_actions, text="⟲", command=self.on_reset, state=state_reset, bg="#3e3e42", fg=fg_reset, bd=0, width=3, cursor="hand2")
        self.btn_reset.pack(side="left", padx=2)
        ToolTip(self.btn_reset, self.manager.t("z5_act_reset"))

        icon_del = "♻" if self.is_deleted else "🗑️"
        fg_del = "#4CAF50" if self.is_deleted else "#f48771"
        tooltip_del = "Restaurer" if self.is_deleted else self.manager.t("z5_act_del")
        
        btn_del = tk.Button(self.frame_actions, text=icon_del, command=self.on_toggle_delete, bg="#3e3e42", fg=fg_del, bd=0, width=3, cursor="hand2")
        btn_del.pack(side="left", padx=2)
        ToolTip(btn_del, tooltip_del)

        all_widgets = [self, self.lbl_idx, self.canvas_color, self.frame_actions] + self.elements
        for w in all_widgets:
            if isinstance(w, (tk.Button, tk.Checkbutton)): continue
            w.bind("<Button-1>", self.on_simple_click, add="+")
            w.bind("<Control-Button-1>", self.on_multi_select, add="+")
            w.bind("<Button-3>", self.on_right_click, add="+")
            
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        for el in self.elements:
            if isinstance(el, tk.Label):
                el.bind("<Enter>", self.on_enter)
                el.bind("<Leave>", self.on_leave)

    def on_enter(self, event=None):
        if self.index not in self.manager.selected_indices and self.index != self.manager.editing_index:
            self.configure_bg("#353538" if not self.is_deleted else "#2a2a2a")

    def on_leave(self, event=None):
        if self.index not in self.manager.selected_indices and self.index != self.manager.editing_index:
            self.configure_bg(self.bg_color)

    def configure_bg(self, color):
        self.config(bg=color)
        for w in self.elements:
            if isinstance(w, tk.Label): w.config(bg=color)
            elif isinstance(w, tk.Checkbutton): w.config(bg=color, activebackground=color)
            elif isinstance(w, tk.Frame) or isinstance(w, tk.Canvas): w.config(bg=color)

    def on_simple_click(self, event=None): 
        self.manager.highlight_row_only(self.index)
        
    def on_edit_click(self): 
        if self.is_deleted: return
        self.manager.select_row_for_editing(self.index)
        
    def on_multi_select(self, event=None): self.manager.toggle_selection(self.index)
        
    def on_right_click(self, event=None):
        if self.index not in self.manager.selected_indices:
            self.manager.highlight_row_only(self.index)
        self.manager.show_context_menu(event)

    def on_reset(self):
        self.line_dict["override"] = {}
        self.line_dict["is_deleted"] = False
        self.is_deleted = False
        try:
            self.chk.config(state="normal")
        except Exception:
            pass
        self.manager.refresh_needed()
        self.manager.trigger_redraw()

    def on_toggle_delete(self): 
        new_val = not self.line_dict.get("is_deleted", False)
        self.line_dict["is_deleted"] = new_val
        self.is_deleted = new_val
        try:
            if self.is_deleted:
                self.chk.config(state="disabled")
            else:
                self.chk.config(state="normal")
        except Exception:
            pass
        self.manager.refresh_needed()
        self.manager.trigger_redraw()

    def on_toggle_active(self): 
        self.line_dict["is_active"] = self.var_active.get()
        self.manager.trigger_redraw()

    def set_selected(self, state, is_editing_mode=False):
        if is_editing_mode: bg = "#007acc"
        elif state: bg = "#444444"
        else: bg = self.bg_color
        
        fg_normal = "white" if state else ("#666" if self.is_deleted else "#969696")
        fg_special = "white" if state else self.default_fg
        
        self.config(bg=bg)
        for w in self.elements:
            if isinstance(w, tk.Label):
                is_idx = (w == self.lbl_idx)
                w.config(bg=bg, fg=fg_special if is_idx else fg_normal)
            elif isinstance(w, tk.Checkbutton): w.config(bg=bg, activebackground=bg, selectcolor="#2d2d30")
            elif isinstance(w, tk.Frame) or isinstance(w, tk.Canvas): w.config(bg=bg)

class LignesPanel:
    def __init__(self, parent_frame, app_instance=None, on_line_select_callback=None, on_delete_callback=None, on_paste_callback=None):
        self.parent = parent_frame
        self.app = app_instance
        self.on_line_select_callback = on_line_select_callback
        self.on_delete_callback = on_delete_callback
        self.on_paste_callback = on_paste_callback
        
        self.rows = []
        self.current_calque_global = {}
        self.current_calque_lines = []
        self.current_calque_color = "#ffffff"
        self.selected_indices = set()
        self.editing_index = None

        self.header = tk.Frame(self.parent, bg="#333333", height=30)
        self.header.pack(fill="x", side="top")
        
        self.header_labels = [] 

        tk.Label(self.header, text="✓", bg="#333333", fg="#d4d4d4", width=3, font=("Segoe UI", 9, "bold")).grid(row=0, column=0, padx=2)
        tk.Label(self.header, text="ID", bg="#333333", fg="#d4d4d4", width=3, font=("Segoe UI", 9, "bold")).grid(row=0, column=1)
        tk.Label(self.header, text="Col", bg="#333333", fg="#d4d4d4", width=3, font=("Segoe UI", 9, "bold")).grid(row=0, column=2)
        
        col_idx = 3
        for _, title_key, weight, _ in COL_CONFIG:
            txt = self.t(title_key)
            lbl = tk.Label(self.header, text=txt, bg="#333333", fg="#d4d4d4", font=("Segoe UI", 9, "bold"), anchor="c")
            lbl.grid(row=0, column=col_idx, sticky="ew", padx=1)
            self.header.columnconfigure(col_idx, weight=weight)
            self.header_labels.append((lbl, title_key))
            col_idx += 1
            
        self.btn_back_calque = tk.Button(self.header, text="Retour Calque", command=self.deselect_all, bg="#444", fg="white", bd=0, font=("Segoe UI", 8), padx=5)
        self.btn_back_calque.grid(row=0, column=98, sticky="e", padx=5)

        self.lbl_actions = tk.Label(self.header, text=self.t("z5_col_actions"), bg="#333333", fg="#007acc", width=12, font=("Segoe UI", 9, "bold"), anchor="e")
        self.lbl_actions.grid(row=0, column=99, sticky="e", padx=10)
        self.header.columnconfigure(99, weight=0)

        self.canvas = tk.Canvas(self.parent, bg="#252526", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.parent, orient="vertical", command=self.canvas.yview)
        self.list_frame = tk.Frame(self.canvas, bg="#252526")
        
        self.window_id = self.canvas.create_window((0, 0), window=self.list_frame, anchor="nw")
        
def on_canvas_configure(event):
                self.canvas.itemconfig(self.window_id, width=event.width)
                self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            self.canvas.bind("<Configure>", on_canvas_configure)
            self.list_frame.bind("<Configure", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
            self.canvas.configure(yscrollcommand=self.scrollbar.set)
            
            self.list_frame.bind("<Button-1>", self.deselect_all)
            self.canvas.bind("<Button-1>", self.deselect_all)
            
            self.canvas.pack(side="left", fill="both", expand=True)
            self.scrollbar.pack(side="right", fill="y")

            self.context_menu = tk.Menu(self.parent, tearoff=0, bg="#2d2d30", fg="white")
            self.context_menu.add_command(label=self.t("z5_ctx_copy"), command=self.action_copy)
            self.context_menu.add_command(label=self.t("z5_ctx_paste"), command=self.action_paste)
            self.clipboard = []

    def t(self, key):
        if self.app: return self.app.t(key)
        return key

    def refresh_ui(self):
        for lbl, key in self.header_labels:
            lbl.config(text=self.t(key))
        self.lbl_actions.config(text=self.t("z5_col_actions"))
        try:
            self.context_menu.entryconfigure(0, label=self.t("z5_ctx_copy"))
            self.context_menu.entryconfigure(1, label=self.t("z5_ctx_paste"))
        except: pass
        self.refresh_table()

    def load_data(self, calque_data, color):
        if not calque_data: return
        self.current_calque_global = calque_data.get("global", {})
        self.current_calque_lines = calque_data.get("lines", [])
        self.current_calque_color = color
        self.refresh_table()

    def refresh_table(self):
        for row in self.rows: row.destroy()
        self.rows = []
        if not self.current_calque_lines: return
        max_idx = len(self.current_calque_lines) - 1
        self.selected_indices = {i for i in self.selected_indices if i <= max_idx}
        
        for i, line_dict in enumerate(self.current_calque_lines):
            row = LigneRow(self.list_frame, self, i, line_dict, self.current_calque_global, self.current_calque_color)
            row.pack(fill="x", pady=0)
            self.rows.append(row)
            is_selected = (i in self.selected_indices)
            is_editing = (i == self.editing_index)
            row.set_selected(is_selected or is_editing, is_editing_mode=is_editing)

    def trigger_redraw(self):
        if self.app and hasattr(self.app, 'trigger_calculation'):
            self.app.trigger_calculation()

    def highlight_row_only(self, index):
        if not isinstance(index, int):
            return
        if index < 0 or index >= len(self.current_calque_lines):
            return
        self.selected_indices = {index}
        self.editing_index = None
        self.update_visual_selection()
        if self.on_line_select_callback:
            line_data = self.current_calque_lines[index]
            merged = self.current_calque_global.copy()
            merged.update(line_data.get("override", {}))
            self.on_line_select_callback(index, merged)

    def select_row_for_editing(self, index):
        if not isinstance(index, int):
            return
        if index < 0 or index >= len(self.current_calque_lines):
            return
        self.selected_indices = {index}
        self.editing_index = index
        self.update_visual_selection()
        self.notify_main_edit()

    def toggle_selection(self, index):
        if index in self.selected_indices: self.selected_indices.remove(index)
        else: self.selected_indices.add(index)
        self.update_visual_selection()
        
    def deselect_all(self, event=None):
        self.selected_indices = set()
        self.editing_index = None
        self.update_visual_selection()
        if self.on_line_select_callback: self.on_line_select_callback(None, self.current_calque_global)

    def update_visual_selection(self):
        for row in self.rows:
            is_sel = row.index in self.selected_indices
            is_edit = row.index == self.editing_index
            row.set_selected(is_sel or is_edit, is_editing_mode=is_edit)
            if not is_sel and not is_edit:
                row.on_leave()

    def notify_main_edit(self):
        if self.editing_index is not None and self.on_line_select_callback:
            if self.editing_index < 0 or self.editing_index >= len(self.current_calque_lines):
                return
            line_data = self.current_calque_lines[self.editing_index]
            merged = self.current_calque_global.copy()
            merged.update(line_data.get("override", {}))
            self.on_line_select_callback(self.editing_index, merged)
            
    def show_context_menu(self, event):
        state = "normal" if self.clipboard else "disabled"
        try: self.context_menu.entryconfigure(1, state=state)
        except: pass
        self.context_menu.tk_popup(event.x_root, event.y_root)

    def action_copy(self):
        self.clipboard = []
        for idx in sorted(list(self.selected_indices)):
            try:
                self.clipboard.append(deepcopy(self.current_calque_lines[idx]))
            except Exception:
                pass
                
    def action_paste(self):
        if not self.clipboard: return
        if self.selected_indices:
            insert_after = max(self.selected_indices)
        else:
            insert_after = len(self.current_calque_lines) - 1 if self.current_calque_lines else -1
        if self.on_paste_callback: self.on_paste_callback(insert_after, self.clipboard)
        
    def delete_line(self, index):
        if self.on_delete_callback: self.on_delete_callback(index)

    def refresh_needed(self):
        self.refresh_table()
        if self.editing_index is not None: self.notify_main_edit()