# -*- coding: utf-8 -*-
"""
Module CanvasPanel - Affichage central du guillochage
"""
import tkinter as tk
import math

class CanvasPanel:
    def __init__(self, parent_frame):
        self.parent = parent_frame
        
        # État de la vue
        self.zoom_level = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.show_grid = True
        self.auto_fit_mode = True
        
        # État 2.5D (Simulation Outil)
        self.render_mode_25d = False
        
        # Données sources
        self.brut_data = None
        self.calculated_lines = []
        
        # État de surbrillance (Selection Zone 5)
        self.highlight_layer = None
        self.highlight_index = None
        
        # Création du canvas
        self.canvas = tk.Canvas(self.parent, bg="#ffffff", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # Bindings
        self.canvas.bind("<ButtonPress-3>",   self.start_pan)
        self.canvas.bind("<B3-Motion>",       self.do_pan)
        self.canvas.bind("<MouseWheel>",      self.do_zoom)
        self.canvas.bind("<Button-4>",        lambda e: self.do_zoom(e, 1))
        self.canvas.bind("<Button-5>",        lambda e: self.do_zoom(e, -1))
        self.canvas.bind("<Configure>",       self.on_resize)

        # Overlay en haut à droite
        self.overlay_frame = tk.Frame(self.canvas, bg="#3e3e42", bd=1, relief="solid")
        self.overlay_frame.place(relx=1.0, x=-10, y=10, anchor="ne")
        
        btn_c = tk.Button(self.overlay_frame, text="⌂", command=self.reset_view_to_fit, bg="#2d2d30", fg="#d4d4d4", bd=0, width=3)
        btn_c.pack(side="left", padx=1)
        btn_g = tk.Button(self.overlay_frame, text="#", command=self.toggle_grid, bg="#007acc", fg="white", bd=0, width=3)
        btn_g.pack(side="left", padx=1)
        
        self.pan_start_x = 0
        self.pan_start_y = 0

    def set_brut_data(self, data):
        self.brut_data = data
        if self.auto_fit_mode: self.fit_to_brut()
        else: self.redraw()

    def set_calculated_lines(self, render_list):
        self.calculated_lines = render_list
        self.redraw()

    def set_highlight(self, layer_name, line_index):
        """Définit quelle ligne doit être mise en surbrillance"""
        self.highlight_layer = layer_name
        self.highlight_index = line_index
        self.redraw()

    def toggle_grid(self):
        self.show_grid = not self.show_grid
        self.redraw()
        
    def set_25d_mode(self, active):
        self.render_mode_25d = active
        bg_color = "#e0e0e0" if active else "#ffffff"
        self.canvas.config(bg=bg_color)
        self.redraw()

    def fit_to_brut(self):
        if not self.brut_data: return
        w_c = self.canvas.winfo_width()
        h_c = self.canvas.winfo_height()
        if w_c < 10:
            self.canvas.after(100, self.fit_to_brut)
            return
        try:
            d1 = float(self.brut_data.get('dim1', 50))
            d2 = float(self.brut_data.get('dim2', 50))
            if d1 > 0 and d2 > 0:
                self.zoom_level = min((w_c * 0.8) / d1, (h_c * 0.8) / d2)
                self.offset_x, self.offset_y = 0, 0
                self.auto_fit_mode = True
                self.redraw()
        except: pass

    def on_resize(self, event):
        if self.auto_fit_mode: self.fit_to_brut()
        else: self.redraw()

    def reset_view_to_fit(self):
        self.auto_fit_mode = True
        self.fit_to_brut()

    def start_pan(self, event):
        self.auto_fit_mode = False
        self.pan_start_x, self.pan_start_y = event.x, event.y

    def do_pan(self, event):
        self.auto_fit_mode = False
        self.offset_x += event.x - self.pan_start_x
        self.offset_y += event.y - self.pan_start_y
        self.pan_start_x, self.pan_start_y = event.x, event.y
        self.redraw()

    def do_zoom(self, event, factor=None):
        self.auto_fit_mode = False
        scale = 1.1 if (factor > 0 if factor else event.delta > 0) else 0.9
        self.zoom_level = max(0.01, min(500.0, self.zoom_level * scale))
        self.redraw()

    def to_screen_x(self, x):
        return self.canvas.winfo_width() / 2 + x * self.zoom_level + self.offset_x

    def to_screen_y(self, y):
        return self.canvas.winfo_height() / 2 - y * self.zoom_level + self.offset_y

    def _get_rounded_rect_points(self, cx, cy, w, h, r):
        pts = []
        r = min(r, w/2, h/2)
        if r <= 0: return [] 
        left, right = cx - w/2, cx + w/2
        top, bottom = cy - h/2, cy + h/2
        steps = 12 
        # TR, BR, BL, TL ...
        corners = [
            ((right-r, top+r), -math.pi/2, 0),
            ((right-r, bottom-r), 0, math.pi/2),
            ((left+r, bottom-r), math.pi/2, math.pi),
            ((left+r, top+r), math.pi, 3*math.pi/2)
        ]
        for c_pt, start, end in corners:
            for i in range(steps + 1):
                ang = start + (end - start) * i / steps
                pts.extend([c_pt[0] + r * math.cos(ang), c_pt[1] + r * math.sin(ang)])
        pts.extend([pts[0], pts[1]])
        return pts

    def redraw(self, event=None):
        self.canvas.delete("all")
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()

        if self.show_grid: self.draw_grid(w, h)
        if self.brut_data: self.draw_brut()

        for obj in self.calculated_lines:
            pts = obj.get("points", [])
            if len(pts) < 2: continue
            
            # Paramètres de base
            base_col = obj.get("color", "black")
            base_thick = float(obj.get("thickness", 1.0))
            
            # --- LOGIQUE SURBRILLANCE (Zone 5 -> Canvas) ---
            is_highlighted = False
            if self.highlight_layer is not None and self.highlight_index is not None:
                if obj.get("layer_name") == self.highlight_layer and obj.get("line_index") == self.highlight_index:
                    is_highlighted = True
            
            # Si surbrillance : Orange + plus large
            if is_highlighted:
                base_col = "#ffae00"  # Orange vif
                base_thick = max(2.5, base_thick + 2.0)

            scr_pts = []
            for px, py in pts:
                scr_pts.extend([self.to_screen_x(px), self.to_screen_y(py)])
            
            if self.render_mode_25d:
                # En mode 2.5D, on garde le gris pour les flancs, mais on peut colorer le fond
                flanc_width = max(2.0, base_thick * 4)
                self.canvas.create_line(scr_pts, fill="#888888", width=flanc_width, capstyle=tk.ROUND, joinstyle=tk.ROUND)
                
                fond_col = base_col # Le fond prend la couleur (Orange si sélectionné)
                self.canvas.create_line(scr_pts, fill=fond_col, width=1.0, capstyle=tk.ROUND, joinstyle=tk.ROUND)
            else:
                try:
                    self.canvas.create_line(scr_pts, fill=base_col, width=base_thick, capstyle=tk.ROUND, joinstyle=tk.ROUND)
                except: pass

    def draw_brut(self):
        cx, cy = self.to_screen_x(0), self.to_screen_y(0)
        try:
            d1 = float(self.brut_data.get('dim1', 50)) * self.zoom_level
            d2 = float(self.brut_data.get('dim2', 50)) * self.zoom_level
            style = {"fill": "", "outline": "#ff4444", "width": 2, "dash": (4, 4)}
            
            if "type_index" in self.brut_data:
                is_circle = (self.brut_data["type_index"] == 0)
            else:
                brut_type = str(self.brut_data.get('type', 'Cercle'))
                is_circle = ("Cercle" in brut_type) or ("Circle" in brut_type)

            if is_circle:
                self.canvas.create_oval(cx - d1/2, cy - d2/2, cx + d1/2, cy + d2/2, **style)
            else:
                radius = float(self.brut_data.get("radius", 0.0)) * self.zoom_level
                if radius > 0.5:
                    pts = self._get_rounded_rect_points(cx, cy, d1, d2, radius)
                    if pts: self.canvas.create_line(pts, fill="#ff4444", width=2, dash=(4, 4))
                    else: self.canvas.create_rectangle(cx - d1/2, cy - d2/2, cx + d1/2, cy + d2/2, **style)
                else:
                    self.canvas.create_rectangle(cx - d1/2, cy - d2/2, cx + d1/2, cy + d2/2, **style)
        except: pass

    def draw_grid(self, w, h):
        cx, cy = self.to_screen_x(0), self.to_screen_y(0)
        steps = [0.1, 0.5, 1.0, 5.0, 10.0, 50.0, 100.0]
        step_mm = steps[-1]
        for s in steps:
            if s * self.zoom_level >= 20:
                step_mm = s
                break
        px_step = step_mm * self.zoom_level

        start_k = math.floor((0 - cx) / px_step)
        end_k   = math.ceil((w - cx) / px_step)
        for k in range(start_k, end_k + 1):
            x = cx + k * px_step
            if k == 0: continue
            is_major = (abs(k) % 5 == 0) if step_mm >= 10 else (round(k * step_mm) % (step_mm * 5) == 0)
            self.canvas.create_line(x, 0, x, h, fill="#dddddd" if is_major else "#f5f5f5")

        start_k = math.floor((cy - h) / px_step)
        end_k   = math.ceil((cy - 0) / px_step)
        for k in range(start_k, end_k + 1):
            y = cy - k * px_step
            if k == 0: continue
            is_major = (abs(k) % 5 == 0) if step_mm >= 10 else (round(k * step_mm) % (step_mm * 5) == 0)
            self.canvas.create_line(0, y, w, y, fill="#dddddd" if is_major else "#f5f5f5")

        self.canvas.create_line(0, cy, w, cy, fill="#ffcccc", width=1)
        self.canvas.create_line(cx, 0, cx, h, fill="#ffcccc", width=1)
        self.canvas.create_line(0, cy, w, cy, fill="#cc0000", width=1, dash=(8, 4))
        self.canvas.create_line(cx, 0, cx, h, fill="#cc0000", width=1, dash=(8, 4))
