# -*- coding: utf-8 -*-
import math
import os
import importlib.util

class GuillochageEngine:
    def __init__(self):
        self.traj_cache = {}
        self.wave_cache = {}

    def _get_trajectory_func(self, traj_name):
        clean = str(traj_name).lower().replace(" ", "_").replace(".py", "")
        if clean in self.traj_cache: return self.traj_cache[clean]
        path = os.path.join(os.path.dirname(__file__), "lib_courbes", "Trajectoires", f"{clean}.py")
        if os.path.exists(path):
            try:
                spec = importlib.util.spec_from_file_location(f"dyn_traj_{clean}", path)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                if hasattr(mod, "get_trajectoire"):
                    self.traj_cache[clean] = mod.get_trajectoire
                    return mod.get_trajectoire
            except: pass
        return None

    def _eval_wave(self, wave_name, t):
        clean = str(wave_name).lower().replace(" ", "_").replace(".py", "")
        if clean == "sinus": return math.sin(t)
        if clean == "triangle": return 2 * abs(2 * (t/(2*math.pi) - math.floor(t/(2*math.pi) + 0.5))) - 1
        if clean == "carre": return 1.0 if math.sin(t) >= 0 else -1.0
        
        if clean in self.wave_cache: return self.wave_cache[clean](t, {})
        
        path = os.path.join(os.path.dirname(__file__), "lib_courbes", "Ondes", f"{clean}.py")
        if os.path.exists(path):
            try:
                spec = importlib.util.spec_from_file_location(f"dyn_wave_{clean}", path)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                if hasattr(mod, "get_offset"):
                    self.wave_cache[clean] = mod.get_offset
                    return mod.get_offset(t, {})
            except: pass
        return math.sin(t)

    def calculate_geometry(self, layers_state, brut_data):
        render_list = []
        try:
            brut_w = float(brut_data.get("dim1", 50.0))
            brut_h = float(brut_data.get("dim2", 50.0))
            idx = brut_data.get("type_index", 0)
            is_circle = (idx == 0)
            # Récupération du rayon des coins (0 si cercle ou si non défini)
            corner_radius = float(brut_data.get("radius", 0.0)) if not is_circle else 0.0
        except:
            brut_w, brut_h, is_circle, corner_radius = 50.0, 50.0, True, 0.0

        # Diagonale pour rotation
        diag = math.hypot(brut_w, brut_h)
        gen_len = diag * 1.2 
        max_dim = max(brut_w, brut_h)
        start_offset_mm = (gen_len - max_dim) / 2

        for layer in layers_state:
            if not layer.get("visible", True): continue
            
            data = layer.get("data", {})
            params = data.get("global", {})
            color = layer.get("color", "black")
            thickness = float(params.get("thickness", 1.0))
            
            traj_name = params.get("traj_type", "ligne_droite")
            traj_func = self._get_trajectory_func(traj_name)
            
            if not traj_func: 
                traj_func = lambda t, p: (((t-0.5)*p.get("gen_len", 100), 0), (0, 1))

            nb = int(float(params.get("nb_lines", 10.0)))
            if nb < 1: nb = 1
            
            wave_name = params.get("wave_type", "sinus")
            marge_user = float(params.get("margin_in", 0.0))
            
            amp_global = float(params.get("amplitude", 2.0))
            is_flambage = params.get("flambage", False)
            amp_start = float(params.get("amp_start", 1.0))
            amp_end = float(params.get("amp_end", 3.0))

            # Repartition Verticale (Plein Cadre)
            h_eff = brut_h - (marge_user * 2)
            min_y_axis = -h_eff / 2
            max_y_axis = h_eff / 2
            dist_axis = max_y_axis - min_y_axis
            
            step = dist_axis / (nb - 1) if nb > 1 else 0
            if nb == 1: min_y_axis = 0; step = 0

            rot_deg = float(params.get("rotation", 0.0))
            rad_rot = math.radians(rot_deg)
            cr, sr = math.cos(rad_rot), math.sin(rad_rot)
            pos_x = float(params.get("pos_x", 0.0))
            pos_y = float(params.get("pos_y", 0.0))

            raw_polylines = []
            
            for i in range(nb):
                current_params = params.copy()
                current_params["line_index"] = i
                current_params["total_lines"] = nb
                current_params["y_base"] = min_y_axis + i * step
                current_params["radius_offset"] = marge_user + i * (brut_w/2 / nb)
                current_params["gen_len"] = gen_len 
                current_params["brut_w"] = brut_w
                current_params["brut_h"] = brut_h

                pts = []
                
                # Résolution
                res_key = str(params.get("resolution", "Moyenne"))
                if "Faible" in res_key: steps = 200
                elif "Haute" in res_key: steps = 2000
                elif "Ultra" in res_key: steps = 10000
                else: steps = 800 

                nb_cycles_user = float(params.get("period", 10.0))
                phase_user = float(params.get("phase", 0.0))
                cycles_per_mm = nb_cycles_user / max_dim
                
                for j in range(steps + 1):
                    t = j / steps
                    
                    # 1. Trajectoire
                    (tx, ty), (nx, ny) = traj_func(t, current_params)
                    
                    if "ligne" in traj_name.lower() or "straight" in traj_name.lower():
                        ty = current_params["y_base"]
                    
                    # 2. Onde
                    dist_mm = t * gen_len
                    dist_relative_to_brut = dist_mm - start_offset_mm
                    angle_wave = dist_relative_to_brut * cycles_per_mm * 2 * math.pi
                    angle_wave += phase_user * 2 * math.pi
                    
                    offset_val = self._eval_wave(wave_name, angle_wave)
                    
                    # Flambage
                    if is_flambage:
                        current_amp = amp_start + (amp_end - amp_start) * t
                    else:
                        current_amp = amp_global
                    
                    fx = tx + nx * offset_val * current_amp
                    fy = ty + ny * offset_val * current_amp
                    
                    # 3. Rotation
                    rx = fx * cr - fy * sr 
                    ry = fx * sr + fy * cr
                    
                    # 4. Position
                    final_x = rx + pos_x
                    final_y = ry + pos_y
                    
                    pts.append((final_x, final_y))
                
                raw_polylines.append(pts)

            # Clipping avec Rayons de coins
            for poly in raw_polylines:
                clipped = self._clip_polyline(poly, is_circle, brut_w, brut_h, corner_radius)
                for seg in clipped:
                    if len(seg) > 1:
                        render_list.append({
                            "type": "polyline",
                            "points": seg,
                            "color": color,
                            "thickness": thickness
                        })

        return render_list

    def _clip_polyline(self, points, is_circle, w, h, r_corner):
        """
        Découpe intelligente prenant en compte les coins arrondis.
        """
        segments = []
        current_segment = []
        
        # Dimensions brutes (bords)
        rx = w / 2
        ry = h / 2
        rx_sq = rx**2
        ry_sq = ry**2

        # Fonction locale pour tester si un point est dedans
        def is_inside(p):
            px, py = p
            # 1. Cas CERCLE
            if is_circle:
                if rx_sq > 0 and ry_sq > 0:
                    return (px*px)/rx_sq + (py*py)/ry_sq <= 1.00001
                return False
            
            # 2. Cas RECTANGLE
            # D'abord, on vérifie la boîte englobante globale
            if not (-rx <= px <= rx and -ry <= py <= ry):
                return False
            
            # Si pas de rayon, c'est bon (car on est dans la boîte)
            if r_corner <= 0:
                return True
            
            # 3. Gestion des Coins Arrondis
            # On travaille en valeur absolue pour traiter les 4 coins d'un coup
            ax, ay = abs(px), abs(py)
            
            # Limites des centres des cercles de coins
            cx = rx - r_corner
            cy = ry - r_corner
            
            # Si on est dans la zone d'un coin (extérieur à la croix centrale)
            if ax > cx and ay > cy:
                # On vérifie la distance par rapport au centre du coin
                dx = ax - cx
                dy = ay - cy
                # Pythagore : est-ce qu'on est dans le rayon ?
                return (dx*dx + dy*dy) <= (r_corner * r_corner)
            
            # Si on n'est pas dans la zone des coins, on est dans la croix centrale -> Dedans
            return True

        # Fonction locale Dichotomie (ne change pas, elle utilise is_inside mis à jour)
        def get_intersection(p1, p2):
            in_p, out_p = p1, p2
            if not is_inside(p1): in_p, out_p = p2, p1
            
            for _ in range(12): # Un peu plus de précision pour les arrondis
                mid_x = (in_p[0] + out_p[0]) / 2
                mid_y = (in_p[1] + out_p[1]) / 2
                mid = (mid_x, mid_y)
                if is_inside(mid):
                    in_p = mid
                else:
                    out_p = mid
            return in_p

        if not points: return []
        
        # Boucle principale de découpe
        p_prev = points[0]
        prev_inside = is_inside(p_prev)
        if prev_inside:
            current_segment.append(p_prev)
            
        for i in range(1, len(points)):
            p_curr = points[i]
            curr_inside = is_inside(p_curr)
            
            if prev_inside and curr_inside:
                current_segment.append(p_curr)
            
            elif prev_inside and not curr_inside:
                inter = get_intersection(p_prev, p_curr)
                current_segment.append(inter)
                segments.append(current_segment)
                current_segment = []
                
            elif not prev_inside and curr_inside:
                inter = get_intersection(p_curr, p_prev)
                current_segment = [inter, p_curr]
            
            p_prev = p_curr
            prev_inside = curr_inside
            
        if current_segment:
            segments.append(current_segment)
            
        return segments