from guillochage_io import GuillochageIO
# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sys
import os
import json
import time

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try: from guillochage_forme import FormePanel
except ImportError as e: print(f"Err Forme: {e}")
try: from guillochage_calques import CalquesPanel
except ImportError as e: print(f"Err Calques: {e}")
try: from guillochage_canvas import CanvasPanel
except ImportError as e: print(f"Err Canvas: {e}")
try: from guillochage_courbes import CourbesPanel
except ImportError as e: print(f"Err Courbes: {e}")
try: from guillochage_lignes import LignesPanel
except ImportError as e: print(f"Err Lignes: {e}")
try: from guillochage_menu import GuillochageMenu
except ImportError as e: print(f"Err Menu: {e}")
try: from guillochage_engine import GuillochageEngine
except ImportError as e: print(f"Err Engine: {e}")

class TranslationManager:
    def __init__(self, lang_dir, default_lang="fr"):
        self.lang_dir = lang_dir
        self.current_lang = default_lang
        self.translations = {}
        self.load_language(default_lang)
    def load_language(self, lang_code):
        path = os.path.join(self.lang_dir, f"{lang_code}.json")
        if not os.path.exists(path): return False
        try:
            with open(path, "r", encoding="utf-8-sig") as f:
                self.translations = json.load(f)
            self.current_lang = lang_code
            return True
        except Exception as e:
            print(f"Err JSON {lang_code}: {e}")
            return False
    def get(self, key):
        return self.translations.get(key, key)

class ModuleApp:
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.root = self.parent.winfo_toplevel()
        self.selected_line_index = None
        self.is_zone3_full = False 
        
        self.current_file_path = None
        self.is_dirty = False 
        self.undo_stack = []
        self.redo_stack = []
        self.clipboard_data = None 
        self.is_snapshotting = False 
        
        self._calc_job = None
        
        lang_path = os.path.join(os.path.dirname(__file__), "lang")
        self.trans_mgr = TranslationManager(lang_path, default_lang="fr")
        
        self.engine = GuillochageEngine() if 'GuillochageEngine' in globals() else None
        
        self.menu = GuillochageMenu(self.parent, self)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.main_paned = tk.PanedWindow(self.parent, orient=tk.VERTICAL, bg="#1e1e1e", sashwidth=4, sashrelief="flat")
        self.main_paned.pack(fill="both", expand=True)
        self.top_paned = tk.PanedWindow(self.main_paned, orient=tk.HORIZONTAL, bg="#1e1e1e", sashwidth=4, sashrelief="flat")
        self.main_paned.add(self.top_paned, stretch="always", minsize=300) 
        self.left_paned = tk.PanedWindow(self.top_paned, orient=tk.VERTICAL, bg="#1e1e1e", sashwidth=4, sashrelief="flat")
        self.top_paned.add(self.left_paned, minsize=200, width=250)

        self.frame_visu = tk.Frame(self.top_paned, bg="#1e1e1e")
        self.panneau_canvas = CanvasPanel(self.frame_visu)
        self.top_paned.add(self.frame_visu, minsize=400, stretch="always")

        self.frame_forme, self.scroll_forme = self.create_scrollable_zone(self.left_paned, "#252526")
        self.lbl_z1_title = tk.Label(self.scroll_forme, text=self.t("z1_title"), fg="#007acc", bg="#252526", font=("Segoe UI", 10, "bold"))
        self.lbl_z1_title.pack(pady=10, anchor="w", padx=10)
        self.panneau_forme = FormePanel(self.scroll_forme, app_instance=self, on_change_callback=self.on_forme_changed)
        self.left_paned.add(self.frame_forme, minsize=100, height=200)

        self.frame_params_container = tk.Frame(self.top_paned, bg="#252526")
        self.z4_header = tk.Frame(self.frame_params_container, bg="#333333", height=35)
        self.z4_header.pack(fill="x", side="top")
        self.lbl_z4_title = tk.Label(self.z4_header, text=self.t("z4_title_global"), fg="white", bg="#333333", font=("Segoe UI", 9, "bold"))
        self.lbl_z4_title.pack(side="left", padx=10)
        
        self.is_zone5_visible = False
        self.btn_toggle = tk.Button(self.z4_header, text="≣", command=self.toggle_zone5, bg="#333333", fg="#969696", activeforeground="#007acc", bd=0, cursor="hand2", font=("Segoe UI", 12))
        self.btn_toggle.pack(side="right", padx=5)
        self.btn_25d = tk.Button(self.z4_header, text="2.5D", command=self.toggle_25d, bg="#333333", fg="#969696", activeforeground="#007acc", bd=0, cursor="hand2", font=("Segoe UI", 9, "bold"))
        self.btn_25d.pack(side="right", padx=5)
        
        self.z4_body_frame, self.z4_scroll_content = self.create_scrollable_zone(self.frame_params_container, "#252526")
        self.z4_body_frame.pack(fill="both", expand=True)
        self.panneau_courbes = CourbesPanel(self.z4_scroll_content, app_instance=self, on_change_callback=self.on_param_change_from_zone4, on_calque_modified_callback=self.on_calque_modified_from_zone4)
        self.top_paned.add(self.frame_params_container, minsize=250, width=300)

        self.frame_zone5 = tk.Frame(self.main_paned, bg="#252526", height=150)
        self.z5_header = tk.Frame(self.frame_zone5, bg="#333333", height=30)
        self.z5_header.pack(fill="x", side="top")
        self.lbl_z5_title = tk.Label(self.z5_header, text=self.t("z5_title"), fg="#007acc", bg="#333333", font=("Segoe UI", 10, "bold"))
        self.lbl_z5_title.pack(side="left", padx=10)
        
        self.panneau_lignes = LignesPanel(self.frame_zone5, app_instance=self, on_line_select_callback=self.on_line_selected_in_zone5, on_delete_callback=self.on_delete_line_action, on_paste_callback=self.on_paste_lines_action)

        self.frame_calques, self.scroll_calques = self.create_scrollable_zone(self.left_paned, "#252526")
        self.lbl_z2_title = tk.Label(self.scroll_calques, text=self.t("z2_title"), fg="#007acc", bg="#252526", font=("Segoe UI", 10, "bold"))
        self.lbl_z2_title.pack(pady=10, anchor="w", padx=10)
        self.panneau_calques = CalquesPanel(self.scroll_calques, app_instance=self, on_select_callback=self.on_calque_click)
        self.left_paned.add(self.frame_calques, minsize=100, stretch="always")
        
        self.update_title()
        if hasattr(self, 'panneau_canvas') and hasattr(self, 'panneau_forme'): self.update_brut_on_canvas()
        
        self.take_snapshot()
        self.is_dirty = False
        self.update_title()
        
        self.start_autosave_timer()
        
        # Zone 5 masquée par défaut
        # self.toggle_zone5()
        
        # Premier calcul
        self._perform_calculation()

    def trigger_calculation(self):
        if self._calc_job:
            try: self.root.after_cancel(self._calc_job)
            except: pass
        self._calc_job = self.root.after(50, self._perform_calculation)

    def _perform_calculation(self):
        self._calc_job = None
        if not self.engine or not hasattr(self, 'panneau_calques'): return
        try:
            layers_state = self.panneau_calques.get_all_layers_state()
            brut_data = self.panneau_forme.get_shape_data()
            render_data = self.engine.calculate_geometry(layers_state, self.panneau_forme.get_shape_data())
            
            if hasattr(self, 'panneau_canvas'):
                if hasattr(self.panneau_canvas, 'set_calculated_lines'):
                    self.panneau_canvas.set_calculated_lines(render_data)
        except Exception as e:
            print(f"Erreur calcul: {e}")

    def get_project_state(self):
        return {
            "version": "1.0",
            "forme": self.panneau_forme.get_shape_data(),
            "calques": self.panneau_calques.get_all_layers_state(),
        }

    def load_project_state(self, state):
        if not state: return
        self.is_snapshotting = True 
        try:
            if "forme" in state:
                self.panneau_forme.set_shape_data(state["forme"])
                self.update_brut_on_canvas()
            
            if "calques" in state:
                self.panneau_calques.load_all_layers_state(state["calques"])
            
            self.trigger_calculation()
            
        except Exception as e:
            print(f"Erreur chargement état: {e}")
        finally:
            self.is_snapshotting = False

    def take_snapshot(self):
        if self.is_snapshotting: return
        state = self.get_project_state()
        if self.undo_stack:
            last = self.undo_stack[-1]
            if json.dumps(last, sort_keys=True) == json.dumps(state, sort_keys=True):
                return
        self.undo_stack.append(state)
        if len(self.undo_stack) > 50: self.undo_stack.pop(0)
        self.redo_stack.clear() 
        self.is_dirty = True
        self.update_title()
        self.trigger_calculation()

    def undo(self):
        if len(self.undo_stack) <= 1: return 
        current = self.undo_stack.pop()
        self.redo_stack.append(current)
        previous = self.undo_stack[-1]
        self.load_project_state(previous)
        self.is_dirty = True
        self.update_title()

    def redo(self):
        if not self.redo_stack: return
        next_state = self.redo_stack.pop()
        self.undo_stack.append(next_state)
        self.load_project_state(next_state)
        self.is_dirty = True
        self.update_title()

    def action_new(self):
        if self.is_dirty:
            if not messagebox.askyesno(self.t("m_new"), self.t("msg_save_changes")): return
        self.current_file_path = None
        self.panneau_calques.load_all_layers_state([]) 
        self.undo_stack = []
        self.redo_stack = []
        self.take_snapshot()
        self.is_dirty = False
        self.update_title()

    def action_save(self):
        if self.current_file_path: self._save_to_file(self.current_file_path)
        else: self.action_save_as()

    def action_save_as(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".guillo", filetypes=[("Projet Guillochage", "*.guillo"), ("JSON", "*.json"), ("Tous", "*.*")])
        if file_path:
            self.current_file_path = file_path
            self._save_to_file(file_path)

    def _save_to_file(self, path):
        try:
            state = self.get_project_state()
            with open(path, "w", encoding="utf-8") as f: json.dump(state, f, indent=4)
            self.is_dirty = False
            self.update_title()
        except Exception as e: messagebox.showerror(self.t("msg_error"), f"Erreur sauvegarde : {e}")

    def action_open(self):
        if self.is_dirty:
            if not messagebox.askyesno(self.t("m_new"), self.t("msg_save_changes")): return
        file_path = filedialog.askopenfilename(filetypes=[("Projet Guillochage", "*.guillo"), ("JSON", "*.json"), ("Tous", "*.*")])
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f: state = json.load(f)
                self.load_project_state(state)
                self.current_file_path = file_path
                self.undo_stack = [state]
                self.redo_stack = []
                self.is_dirty = False
                self.update_title()
            except Exception as e: messagebox.showerror(self.t("msg_error"), f"Erreur ouverture : {e}")

    def action_copy(self):
        if hasattr(self, 'panneau_lignes') and self.panneau_lignes.selected_indices:
            self.panneau_lignes.action_copy()
            return
        if hasattr(self, 'panneau_calques') and self.panneau_calques.selected_row:
            state = self.panneau_calques.get_selected_layer_state()
            if state: self.clipboard_data = state

    def action_paste(self):
        if hasattr(self, 'panneau_lignes') and self.panneau_lignes.clipboard:
             self.panneau_lignes.action_paste()
             self.take_snapshot()
             return
        if self.clipboard_data and self.clipboard_data.get("type") == "layer":
            self.panneau_calques.paste_layer_from_clipboard(self.clipboard_data)
            self.take_snapshot()

    def start_autosave_timer(self):
        if hasattr(self.menu, 'var_autosave') and self.menu.var_autosave.get(): self.do_autosave()
        self.root.after(300000, self.start_autosave_timer)

    def do_autosave(self):
        if self.is_dirty:
            try:
                with open("autosave.guillo", "w", encoding="utf-8") as f: json.dump(self.get_project_state(), f)
            except: pass

    def on_closing(self):
        if self.is_dirty:
            resp = messagebox.askyesnocancel(self.t("msg_quit_title"), self.t("msg_save_changes"))
            if resp is None: return 
            if resp: self.action_save() 
        self.root.destroy()

    def on_forme_changed(self, data=None):
        if not hasattr(self, 'panneau_forme'): return
        self.update_brut_on_canvas()
        self.take_snapshot()
        self.trigger_calculation()

    def on_param_change_from_zone4(self):
        if hasattr(self, 'panneau_calques') and hasattr(self, 'panneau_courbes'):
            new_data = self.panneau_courbes.get_current_params()
            if self.panneau_calques.selected_row:
                self.panneau_calques.selected_row.update_params_from_zone4(new_data, target_line_index=self.selected_line_index)
                self.refresh_all_zones()
                self.trigger_calculation()

    def on_calque_modified_from_zone4(self, new_name, new_color):
        self.panneau_calques.update_active_calque_data(new_name, new_color)
        if self.panneau_calques.selected_row:
             data = self.panneau_calques.selected_row.data
             self.panneau_lignes.load_data(data, new_color)
        self.take_snapshot() 

    def on_delete_line_action(self, index):
        if self.panneau_calques.selected_row:
            self.panneau_calques.selected_row.delete_line_at(index)
            self.refresh_all_zones()
            self.take_snapshot()

    def on_paste_lines_action(self, insert_after_index, lines_list):
        if self.panneau_calques.selected_row:
            self.panneau_calques.selected_row.insert_lines_at(insert_after_index, lines_list)
            self.refresh_all_zones()
            self.take_snapshot()

    def refresh_all_zones(self):
        full_data = self.panneau_calques.selected_row.data
        color = self.panneau_calques.selected_row.color
        if hasattr(self, 'panneau_lignes'): 
            self.panneau_lignes.load_data(full_data, color)
        if hasattr(self, 'panneau_courbes'):
            if self.selected_line_index is not None and self.selected_line_index < len(full_data["lines"]):
                global_p = full_data["global"]
                line_p = full_data["lines"][self.selected_line_index]
                merged = global_p.copy()
                merged.update(line_p.get("override", {}))
                self.panneau_courbes.set_params(merged)
            else:
                self.panneau_courbes.set_params(full_data["global"])

    def update_brut_on_canvas(self): self.panneau_canvas.set_brut_data(self.panneau_forme.get_shape_data())

    def t(self, key): return self.trans_mgr.get(key)
    
    def update_title(self):
        base = self.t("app_title")
        file = os.path.basename(self.current_file_path) if self.current_file_path else "Sans Titre"
        dirty = "*" if self.is_dirty else ""
        try: self.root.title(f"{base} - {file}{dirty}")
        except: pass

    def change_language(self, lang_code):
        if self.trans_mgr.load_language(lang_code):
            self.update_title()
            if hasattr(self.menu, 'rebuild_menu'): self.menu.rebuild_menu()
            
            if hasattr(self, 'lbl_z1_title'): self.lbl_z1_title.config(text=self.t("z1_title"))
            if hasattr(self, 'lbl_z2_title'): self.lbl_z2_title.config(text=self.t("z2_title"))
            if hasattr(self, 'lbl_z5_title'): self.lbl_z5_title.config(text=self.t("z5_title"))
            
            if self.selected_line_index is not None:
                txt = self.t("z4_title_line").format(index=self.selected_line_index + 1)
                self.lbl_z4_title.config(text=txt)
            else:
                self.lbl_z4_title.config(text=self.t("z4_title_global"))
            
            if hasattr(self.panneau_forme, 'refresh_ui'): self.panneau_forme.refresh_ui()
            if hasattr(self.panneau_courbes, 'refresh_ui'): self.panneau_courbes.refresh_ui()
            if hasattr(self.panneau_lignes, 'refresh_ui'): self.panneau_lignes.refresh_ui()
            if hasattr(self.panneau_calques, 'refresh_ui'): self.panneau_calques.refresh_ui()

    def create_scrollable_zone(self, parent, bg_color):
        container = tk.Frame(parent, bg=bg_color)
        canvas = tk.Canvas(container, bg=bg_color, highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=bg_color)
        canvas_frame = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_frame, width=e.width))
        def _on_mousewheel(event): canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        container.bind('<Enter>', lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        container.bind('<Leave>', lambda e: canvas.unbind_all("<MouseWheel>"))
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        return container, scrollable_frame

    def toggle_zone3_fullscreen(self):
        if self.is_zone3_full:
            self.top_paned.add(self.left_paned, before=self.frame_visu, minsize=200, width=250)
            self.top_paned.add(self.frame_params_container, after=self.frame_visu, minsize=250, width=300)
            self.is_zone3_full = False
        else:
            self.top_paned.remove(self.left_paned)
            self.top_paned.remove(self.frame_params_container)
            if self.is_zone5_visible: self.toggle_zone5()
            self.is_zone3_full = True

    def toggle_zone5(self):
        if self.is_zone5_visible:
            self.main_paned.remove(self.frame_zone5)
            self.is_zone5_visible = False
            self.btn_toggle.config(fg="#969696")
        else:
            self.main_paned.add(self.frame_zone5, minsize=100, height=150)
            self.is_zone5_visible = True
            self.btn_toggle.config(fg="#007acc")

    def toggle_25d(self): pass

    def on_calque_click(self, nom_calque, couleur_calque, full_calque_data):
        self.selected_line_index = None 
        self.lbl_z4_title.config(text=self.t("z4_title_global"), fg="white")
        self.panneau_courbes.update_active_layer(nom_calque, couleur_calque)
        self.panneau_courbes.set_params(full_calque_data["global"])
        if hasattr(self, 'panneau_lignes'):
            self.panneau_lignes.selected_index = None
            self.panneau_lignes.load_data(full_calque_data, couleur_calque)

    def on_line_selected_in_zone5(self, line_index, merged_params):
        self.selected_line_index = line_index
        if line_index is not None:
            txt = self.t("z4_title_line").format(index=line_index + 1)
            self.lbl_z4_title.config(text=txt, fg="#ffae00")
            self.panneau_courbes.set_params(merged_params)
        else:
            self.lbl_z4_title.config(text=self.t("z4_title_global"), fg="white")
            self.panneau_courbes.set_params(merged_params)

if __name__ == "__main__":
    root = tk.Tk()
    app = ModuleApp(root)
    root.mainloop()



    def action_export_file(self, format_type="svg"):
        try:
            # Récupération des données fraîches
            layers_state = self.panneau_calques.get_all_layers_state()
            # Sécurisation si panneau_forme plante ou est vide
            try: brut_data = self.panneau_forme.get_shape_data()
            except: brut_data = {"dim1": 50, "dim2": 50}
            
            # Calcul de la géométrie
            render_list = self.engine.calculate_geometry(layers_state, brut_data)
            
            # Dialogue d'enregistrement
            ext = f".{format_type}"
            path = filedialog.asksaveasfilename(defaultextension=ext, filetypes=[(format_type.upper(), ext)])
            
            if path:
                if format_type == "svg":
                    GuillochageIO.export_svg(path, render_list, brut_data)
                else:
                    GuillochageIO.export_dxf(path, render_list)
                messagebox.showinfo("Export", f"Fichier sauvegardé :\n{path}")
        except Exception as e:
            messagebox.showerror("Erreur Export", str(e))
