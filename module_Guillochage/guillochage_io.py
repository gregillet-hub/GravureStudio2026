# -*- coding: utf-8 -*-
import os

class GuillochageIO:
    @staticmethod
    def rgb_to_dxf_color(hex_color):
        """Convertit HEX en ACI (AutoCAD Color Index)"""
        mapping = {
            "#000000": 7, "#ffffff": 7, "#ff0000": 1, "#ffff00": 2, 
            "#00ff00": 3, "#00ffff": 4, "#0000ff": 5, "#ff00ff": 6,
        }
        return mapping.get(hex_color.lower(), 7)

    @staticmethod
    def export_dxf(filename, render_list):
        """Export DXF standard"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("0\nSECTION\n2\nHEADER\n9\n$ACADVER\n1\nAC1009\n0\nENDSEC\n")
            f.write("0\nSECTION\n2\nTABLES\n0\nTABLE\n2\nLAYER\n70\n1\n")
            f.write("0\nLAYER\n2\nGuillochage\n70\n0\n62\n7\n6\nCONTINUOUS\n0\nENDTAB\n0\nENDSEC\n")
            f.write("0\nSECTION\n2\nENTITIES\n")
            
            for item in render_list:
                pts = item.get("points", [])
                if len(pts) < 2: continue
                col = GuillochageIO.rgb_to_dxf_color(item.get("color", "#000000"))
                f.write("0\nPOLYLINE\n8\nGuillochage\n62\n{}\n66\n1\n10\n0.0\n20\n0.0\n30\n0.0\n".format(col))
                for x, y in pts:
                    f.write(f"0\nVERTEX\n8\nGuillochage\n10\n{x:.4f}\n20\n{y:.4f}\n30\n0.0\n")
                f.write("0\nSEQEND\n")
            f.write("0\nENDSEC\n0\nEOF\n")

    @staticmethod
    def export_svg(filename, render_list, brut_data=None):
        """Export SVG vectoriel"""
        try:
            bw = float(brut_data.get("dim1", 100))
            bh = float(brut_data.get("dim2", 100))
        except: bw, bh = 100, 100
        
        margin = 10
        width, height = bw + margin*2, bh + margin*2
        cx, cy = width/2, height/2

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}mm" height="{height}mm" viewBox="0 0 {width} {height}">\n')
            
            # Brut (cadre)
            if brut_data:
                f.write(f'<rect x="{cx-bw/2}" y="{cy-bh/2}" width="{bw}" height="{bh}" fill="none" stroke="#ddd" stroke-dasharray="2,2"/>\n')

            # Courbes
            for item in render_list:
                pts = item.get("points", [])
                if len(pts) < 2: continue
                col = item.get("color", "black")
                thk = item.get("thickness", 1.0)
                path_d = []
                for i, (x, y) in enumerate(pts):
                    cmd = "M" if i == 0 else "L"
                    path_d.append(f"{cmd} {cx+x:.3f} {cy-y:.3f}")
                f.write(f'<path d="{" ".join(path_d)}" stroke="{col}" stroke-width="{thk}" fill="none"/>\n')
            f.write('</svg>')