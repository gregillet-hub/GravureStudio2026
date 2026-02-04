# -*- coding: utf-8 -*-
import os
import math

class GuillochageIO:
    @staticmethod
    def rgb_to_dxf_color(hex_color):
        """Convertit HEX en ACI (AutoCAD Color Index) approximatif"""
        mapping = {
            "#000000": 7, "#ffffff": 7, "#ff0000": 1, "#ffff00": 2, 
            "#00ff00": 3, "#00ffff": 4, "#0000ff": 5, "#ff00ff": 6,
        }
        return mapping.get(hex_color.lower(), 7)

    @staticmethod
    def _write_dxf_polyline(f, points, color=7, layer="Guillochage", closed=False):
        if len(points) < 2: return
        f.write(f"0\nPOLYLINE\n8\n{layer}\n62\n{color}\n66\n1\n10\n0.0\n20\n0.0\n30\n0.0\n")
        if closed: f.write("70\n1\n") # Flag 1 = Closed
        for x, y in points:
            f.write(f"0\nVERTEX\n8\n{layer}\n10\n{x:.4f}\n20\n{y:.4f}\n30\n0.0\n")
        f.write("0\nSEQEND\n")

    @staticmethod
    def _get_rounded_rect_points(w, h, r):
        """Génère les points d'un rectangle arrondi pour le DXF"""
        pts = []
        steps = 8 # Résolution des arcs
        if r > min(w, h)/2: r = min(w, h)/2
        
        # 4 quadrants
        quadrants = [
            ((w/2 - r, h/2 - r), 0, math.pi/2),     # TR
            ((-w/2 + r, h/2 - r), math.pi/2, math.pi), # TL
            ((-w/2 + r, -h/2 + r), math.pi, 3*math.pi/2), # BL
            ((w/2 - r, -h/2 + r), 3*math.pi/2, 2*math.pi) # BR
        ]
        
        for center, start_ang, end_ang in quadrants:
            cx, cy = center
            for i in range(steps + 1):
                a = start_ang + (end_ang - start_ang) * i / steps
                pts.append((cx + r*math.cos(a), cy + r*math.sin(a)))
        return pts

    @staticmethod
    def export_dxf(filename, render_list, brut_data=None):
        """Export DXF standard avec Brut"""
        with open(filename, 'w', encoding='utf-8') as f:
            # Header
            f.write("0\nSECTION\n2\nHEADER\n9\n$ACADVER\n1\nAC1009\n0\nENDSEC\n")
            # Tables (Layers)
            f.write("0\nSECTION\n2\nTABLES\n0\nTABLE\n2\nLAYER\n70\n1\n")
            f.write("0\nLAYER\n2\nGuillochage\n70\n0\n62\n7\n6\nCONTINUOUS\n0\nENDTAB\n")
            # Layer Brut en ROUGE (1) et CONTINUOUS (Trait plein)
            f.write("0\nLAYER\n2\nBrut\n70\n0\n62\n1\n6\nCONTINUOUS\n0\nENDTAB\n0\nENDSEC\n")
            
            f.write("0\nSECTION\n2\nENTITIES\n")
            
            # --- 1. DESSIN DU BRUT ---
            if brut_data:
                try:
                    d1 = float(brut_data.get("dim1", 50))
                    d2 = float(brut_data.get("dim2", 50))
                    idx = brut_data.get("type_index", 0) # 0=Cercle, 1=Rect
                    
                    if idx == 0: # CERCLE
                        r = d1 / 2
                        f.write(f"0\nCIRCLE\n8\nBrut\n62\n1\n10\n0.0\n20\n0.0\n30\n0.0\n40\n{r:.4f}\n")
                    else: # RECTANGLE
                        r_corn = float(brut_data.get("radius", 0.0))
                        if r_corn > 0.1:
                            # Rectangle arrondi (discrétisé en polyligne)
                            pts = GuillochageIO._get_rounded_rect_points(d1, d2, r_corn)
                            GuillochageIO._write_dxf_polyline(f, pts, color=1, layer="Brut", closed=True)
                        else:
                            # Rectangle simple
                            w, h = d1, d2
                            pts = [(-w/2, -h/2), (w/2, -h/2), (w/2, h/2), (-w/2, h/2)]
                            GuillochageIO._write_dxf_polyline(f, pts, color=1, layer="Brut", closed=True)
                except Exception as e:
                    print(f"Err Brut DXF: {e}")

            # --- 2. DESSIN DU GUILLOCHAGE ---
            for item in render_list:
                pts = item.get("points", [])
                if len(pts) < 2: continue
                col = GuillochageIO.rgb_to_dxf_color(item.get("color", "#000000"))
                GuillochageIO._write_dxf_polyline(f, pts, color=col, layer="Guillochage")

            f.write("0\nENDSEC\n0\nEOF\n")

    @staticmethod
    def export_svg(filename, render_list, brut_data=None):
        """Export SVG vectoriel avec Brut"""
        try:
            bw = float(brut_data.get("dim1", 100))
            bh = float(brut_data.get("dim2", 100))
        except: bw, bh = 100, 100
        
        margin = 10
        width, height = bw + margin*2, bh + margin*2
        cx, cy = width/2, height/2

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}mm" height="{height}mm" viewBox="0 0 {width} {height}">\n')
            
            # --- 1. DESSIN DU BRUT ---
            if brut_data:
                try:
                    idx = brut_data.get("type_index", 0) # 0=Cercle, 1=Rect
                    # Style : Rouge, Fin, Pas de tirets (Solid)
                    style = 'fill="none" stroke="#ff0000" stroke-width="0.5"'
                    
                    if idx == 0: # CERCLE
                        r = bw / 2
                        f.write(f'<circle cx="{cx}" cy="{cy}" r="{r}" {style} />\n')
                    else: # RECTANGLE
                        r_corn = float(brut_data.get("radius", 0.0))
                        f.write(f'<rect x="{cx - bw/2}" y="{cy - bh/2}" width="{bw}" height="{bh}" rx="{r_corn}" ry="{r_corn}" {style} />\n')
                except: pass

            # --- 2. DESSIN DU GUILLOCHAGE ---
            for item in render_list:
                pts = item.get("points", [])
                if len(pts) < 2: continue
                col = item.get("color", "black")
                thk = item.get("thickness", 1.0)
                
                path_d = []
                for i, (x, y) in enumerate(pts):
                    # Inversion Y pour SVG et centrage
                    sx = cx + x
                    sy = cy - y
                    cmd = "M" if i == 0 else "L"
                    path_d.append(f"{cmd} {sx:.3f} {sy:.3f}")
                
                f.write(f'<path d="{" ".join(path_d)}" stroke="{col}" stroke-width="{thk}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>\n')
            
            f.write('</svg>')
