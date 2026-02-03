# -*- coding: utf-8 -*-
"""
Module CanvasPanel - Affichage central du guillochage
----------------------------------------------------
Gère le canvas Tkinter principal où sont dessinés :
- La grille de référence
- La forme brute (cercle ou rectangle arrondi) en pointillés rouges
- Les lignes calculées du guillochage (polylignes colorées)
"""

import tkinter as tk
import math

class CanvasPanel:
    def __init__(self, parent_frame):
        """
        Initialise le panneau canvas avec ses contrôles et bindings.
        """
        self.parent = parent_frame
        
        # État de la vue
        self.zoom_level = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.show_grid = True
        self.auto_fit_mode = True
        
        # Données sources
        self.brut_data = None           # Dict {dim1, dim2, type_index, radius}
        self.calculated_lines = []      # Liste des objets à dessiner
        
        # Création du canvas
        self.canvas = tk.Canvas(
            self.parent,
            bg="#ffffff",
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)
        
        # Bindings souris
        self.canvas.bind("<ButtonPress-3>",   self.start_pan)
        self.canvas.bind("<B3-Motion>",       self.do_pan)
        self.canvas.bind("<MouseWheel>",      self.do_zoom)
        self.canvas.bind("<Button-4>",        lambda e: self.do_zoom(e, 1))   # Linux zoom up
        self.canvas.bind("<Button-5>",        lambda e: self.do_zoom(e, -1))  # Linux zoom down
        self.canvas.bind("<Configure>",       self.on_resize)

        # Overlay en haut à droite (reset + grille)
        self.overlay_frame = tk.Frame(self.canvas, bg="#3e3e42", bd=1, relief="solid")
        self.overlay_frame.place(relx=1.0, x=-10, y=10, anchor="ne")
        
        # Bouton reset vue
        btn_c = tk.Button(self.overlay_frame, text="⌂", command=self.reset_view_to_fit,
                          bg="#2d2d30", fg="#d4d4d4", bd=0, width=3)
        btn_c.pack(side="left", padx=1)
        
        # Bouton toggle grille
        btn_g = tk.Button(self.overlay_frame, text="#", command=self.toggle_grid,
                          bg="#007acc", fg="white", bd=0, width=3)
        btn_g.pack(side="left", padx=1)
        
        # Variables pour le drag (pan)
        self.pan_start_x = 0
        self.pan_start_y = 0

    def set_brut_data(self, data):
        """Reçoit les informations de la forme brute"""
        self.brut_data = data
        if self.auto_fit_mode:
            self.fit_to_brut()
        else:
            self.redraw()

    def set_calculated_lines(self, render_list):
        """Reçoit la liste des lignes à dessiner"""
        self.calculated_lines = render_list
        self.redraw()

    def toggle_grid(self):
        """Inverse l'affichage de la grille"""
        self.show_grid = not self.show_grid
        self.redraw()

    def fit_to_brut(self):
        """Adapte automatiquement le zoom"""
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
        except Exception: pass

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
        """Génère les coordonnées d'un rectangle arrondi pour create_line"""
        pts = []
        # Limiter le rayon à la moitié du plus petit côté
        r = min(r, w/2, h/2)
        if r <= 0: return [] # Devrait être géré avant

        left, right = cx - w/2, cx + w/2
        top, bottom = cy - h/2, cy + h/2
        steps = 12 # Qualité de l'arc

        # 4 coins avec trigonométrie pour l'approximation des arcs
        # Attention: Axe Y vers le bas en écran (Top < Bottom)
        
        # 1. Top-Right Corner (Arc de -90° à 0°)
        tr_c = (right - r, top + r)
        for i in range(steps + 1):
            ang = -math.pi/2 + (math.pi/2 * i / steps)
            pts.extend([tr_c[0] + r * math.cos(ang), tr_c[1] + r * math.sin(ang)])
            
        # 2. Bottom-Right Corner (Arc de 0° à 90°)
        br_c = (right - r, bottom - r)
        for i in range(steps + 1):
            ang = 0 + (math.pi/2 * i / steps)
            pts.extend([br_c[0] + r * math.cos(ang), br_c[1] + r * math.sin(ang)])

        # 3. Bottom-Left Corner (Arc de 90° à 180°)
        bl_c = (left + r, bottom - r)
        for i in range(steps + 1):
            ang = math.pi/2 + (math.pi/2 * i / steps)
            pts.extend([bl_c[0] + r * math.cos(ang), bl_c[1] + r * math.sin(ang)])

        # 4. Top-Left Corner (Arc de 180° à 270°)
        tl_c = (left + r, top + r)
        for i in range(steps + 1):
            ang = math.pi + (math.pi/2 * i / steps)
            pts.extend([tl_c[0] + r * math.cos(ang), tl_c[1] + r * math.sin(ang)])
            
        # Fermeture de la boucle
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
            col = obj.get("color", "black")
            thick = float(obj.get("thickness", 1.0))
            scr_pts = []
            for px, py in pts:
                scr_pts.extend([self.to_screen_x(px), self.to_screen_y(py)])
            try:
                self.canvas.create_line(scr_pts, fill=col, width=thick, capstyle=tk.ROUND, joinstyle=tk.ROUND)
            except: pass

    def draw_brut(self):
        """Dessine la forme brute (Cercle ou Rectangle +/- Arrondi)"""
        cx, cy = self.to_screen_x(0), self.to_screen_y(0)
        
        try:
            d1 = float(self.brut_data.get('dim1', 50)) * self.zoom_level
            d2 = float(self.brut_data.get('dim2', 50)) * self.zoom_level
            
            style = {"fill": "", "outline": "#ff4444", "width": 2, "dash": (4, 4)}
            
            # Détection fiable du type
            if "type_index" in self.brut_data:
                is_circle = (self.brut_data["type_index"] == 0)
            else:
                brut_type = str(self.brut_data.get('type', 'Cercle'))
                is_circle = ("Cercle" in brut_type) or ("Circle" in brut_type)

            if is_circle:
                self.canvas.create_oval(cx - d1/2, cy - d2/2, cx + d1/2, cy + d2/2, **style)
            else:
                # Rectangle
                radius = float(self.brut_data.get("radius", 0.0)) * self.zoom_level
                
                if radius > 0.5: # Si rayon visible
                    pts = self._get_rounded_rect_points(cx, cy, d1, d2, radius)
                    if pts:
                        # On utilise create_line pour préserver le style pointillé (dash) proprement
                        self.canvas.create_line(pts, fill="#ff4444", width=2, dash=(4, 4))
                    else:
                        # Fallback si calcul échoue
                        self.canvas.create_rectangle(cx - d1/2, cy - d2/2, cx + d1/2, cy + d2/2, **style)
                else:
                    # Rectangle Standard
                    self.canvas.create_rectangle(cx - d1/2, cy - d2/2, cx + d1/2, cy + d2/2, **style)
                
        except Exception as e:
            print(f"[Canvas] Erreur dessin brut : {e}")

    def draw_grid(self, w, h):
        cx, cy = self.to_screen_x(0), self.to_screen_y(0)
        steps = [0.1, 0.5, 1.0, 5.0, 10.0, 50.0, 100.0]
        step_mm = steps[-1]
        for s in steps:
            if s * self.zoom_level >= 20:
                step_mm = s
                break
        px_step = step_mm * self.zoom_level

        # Verticales
        start_k = math.floor((0 - cx) / px_step)
        end_k   = math.ceil((w - cx) / px_step)
        for k in range(start_k, end_k + 1):
            x = cx + k * px_step
            if k == 0: continue
            is_major = (abs(k) % 5 == 0) if step_mm >= 10 else (round(k * step_mm) % (step_mm * 5) == 0)
            self.canvas.create_line(x, 0, x, h, fill="#dddddd" if is_major else "#f5f5f5")

        # Horizontales
        start_k = math.floor((cy - h) / px_step)
        end_k   = math.ceil((cy - 0) / px_step)
        for k in range(start_k, end_k + 1):
            y = cy - k * px_step
            if k == 0: continue
            is_major = (abs(k) % 5 == 0) if step_mm >= 10 else (round(k * step_mm) % (step_mm * 5) == 0)
            self.canvas.create_line(0, y, w, y, fill="#dddddd" if is_major else "#f5f5f5")

        # Axes
        self.canvas.create_line(0, cy, w, cy, fill="#ffcccc", width=1)
        self.canvas.create_line(cx, 0, cx, h, fill="#ffcccc", width=1)
        self.canvas.create_line(0, cy, w, cy, fill="#cc0000", width=1, dash=(8, 4))
        self.canvas.create_line(cx, 0, cx, h, fill="#cc0000", width=1, dash=(8, 4))