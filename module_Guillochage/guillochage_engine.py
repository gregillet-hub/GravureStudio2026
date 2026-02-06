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
            corner_radius = float(brut_data.get("radius", 0.0)) if not is_circle else 0.0
        except:
            brut_w, brut_h, is_circle, corner_radius = 50.0, 50.0, True, 0.0

        diag = math.hypot(brut_w, brut_h)
        # Marge de génération pour éviter les bords coupés
        gen_len = diag * 1.5 
        max_dim = max(brut_w, brut_h)
        start_offset_mm = (gen_len - max_dim) / 2

        for layer in layers_state:
            if not layer.get("visible", True): continue
            
            layer_name = layer.get("name", "")
            data = layer.get("data", {})
            global_params = data.get("global", {})
            layer_color = layer.get("color", "black")
            
            lines_list = data.get("lines", [])
            
            # Gestion cas legacy ou liste vide
            nb_global = int(float(global_params.get("nb_lines", 10.0)))
            if not lines_list and nb_global > 0:
                 lines_list = [{"id": i+1, "is_active": True, "is_deleted": False, "override": {}} for i in range(nb_global)]

            # Nb total (incluant les supprimées) pour conserver l'équidistance
            nb_total = len(lines_list)
            if nb_total < 1: continue

            marge_user = float(global_params.get("margin_in", 0.0))
            h_eff = brut_h - (marge_user * 2)
            min_y_axis = -h_eff / 2
            max_y_axis = h_eff / 2
            dist_axis = max_y_axis - min_y_axis
            
            step = dist_axis / (nb_total - 1) if nb_total > 1 else 0
            if nb_total == 1: min_y_axis = 0; step = 0

            # --- BOUCLE PRINCIPALE DES LIGNES ---
            for i, line_data in enumerate(lines_list):
                
                # 1. SI LA LIGNE EST MARQUÉE SUPPRIMÉE (CORBEILLE) -> ON NE DESSINE PAS
                # Mais on est dans une boucle enumerate, donc 'i' incrémente quand même.
                # Cela crée un "trou" visuel mais garde l'espacement des autres.
                if line_data.get("is_deleted", False):
                    continue

                # 2. SI LA LIGNE EST DÉSACTIVÉE (CHECKBOX) -> ON NE DESSINE PAS
                if not line_data.get("is_active", True):
                    continue

                # --- PRÉPARATION PARAMÈTRES ---
                current_params = global_params.copy()
                current_params.update(line_data.get("override", {}))
                
                current_params["line_index"] = i
                current_params["total_lines"] = nb_total
                current_params["y_base"] = min_y_axis + i * step
                current_params["radius_offset"] = marge_user + i * (brut_w/2 / nb_total) if nb_total > 0 else 0
                current_params["gen_len"] = gen_len 
                current_params["brut_w"] = brut_w
                current_params["brut_h"] = brut_h

                traj_name = current_params.get("traj_type", "ligne_droite")
                traj_func = self._get_trajectory_func(traj_name)
                if not traj_func: traj_func = lambda t, p: (((t-0.5)*p.get("gen_len", 100), 0), (0, 1))

                wave_name = current_params.get("wave_type", "sinus")
                is_flambage = current_params.get("flambage", False)
                amp_global = float(current_params.get("amplitude", 2.0))
                amp_start = float(current_params.get("amp_start", 1.0))
                amp_end = float(current_params.get("amp_end", 3.0))
                thickness = float(current_params.get("thickness", 1.0))
                is_mir_h = current_params.get("mirror_h", False)
                is_mir_v = current_params.get("mirror_v", False)
                rot_deg = float(current_params.get("rotation", 0.0))
                rad_rot = math.radians(rot_deg)
                cr, sr = math.cos(rad_rot), math.sin(rad_rot)
                pos_x = float(current_params.get("pos_x", 0.0))
                pos_y = float(current_params.get("pos_y", 0.0))

                # Résolution
                res_key = str(current_params.get("resolution", "Moyenne"))
                if "Faible" in res_key: steps = 200
                elif "Haute" in res_key: steps = 2000
                elif "Ultra" in res_key: steps = 10000
                else: steps = 800 

                nb_cycles_user = float(current_params.get("period", 10.0))
                phase_user = float(current_params.get("phase", 0.0))
                cycles_per_mm = nb_cycles_user / max_dim

                pts = []
                
                # --- CALCUL DES POINTS ---
                for j in range(steps + 1):
                    t = j / steps
                    (tx, ty), (nx, ny) = traj_func(t, current_params)
                    
                    if "ligne" in traj_name.lower() or "straight" in traj_name.lower():
                        ty = current_params["y_base"]
                    
                    dist_mm = t * gen_len
                    dist_relative_to_brut = dist_mm - start_offset_mm
                    angle_wave = dist_relative_to_brut * cycles_per_mm * 2 * math.pi
                    angle_wave += phase_user * 2 * math.pi
                    
                    offset_val = self._eval_wave(wave_name, angle_wave)
                    
                    if is_flambage: current_amp = amp_start + (amp_end - amp_start) * t
                    else: current_amp = amp_global
                    
                    fx = tx + nx * offset_val * current_amp
                    fy = ty + ny * offset_val * current_amp
                    
                    # Rotation et Position
                    rx = fx * cr - fy * sr 
                    ry = fx * sr + fy * cr
                    final_x = rx + pos_x
                    final_y = ry + pos_y
                    
                    if is_mir_h: final_x = -final_x
                    if is_mir_v: final_y = -final_y
                    
                    pts.append((final_x, final_y))
                
                # Clipping (Découpe selon la forme brut)
                clipped_segments = self._clip_polyline(pts, is_circle, brut_w, brut_h, corner_radius)
                
                for seg in clipped_segments:
                    if len(seg) > 1:
                        render_list.append({
                            "type": "polyline",
                            "points": seg,
                            "color": layer_color,
                            "thickness": thickness,
                            "layer_name": layer_name,
                            "line_index": i
                        })

        return render_list

    def _clip_polyline(self, points, is_circle, w, h, r_corner):
        segments = []
        current_segment = []
        
        rx = w / 2
        ry = h / 2
        rx_sq = rx**2
        ry_sq = ry**2

        def is_inside(p):
            px, py = p
            if is_circle:
                if rx_sq > 0 and ry_sq > 0:
                    return (px*px)/rx_sq + (py*py)/ry_sq <= 1.00001
                return False
            
            if not (-rx <= px <= rx and -ry <= py <= ry):
                return False
            
            if r_corner <= 0: return True
            
            ax, ay = abs(px), abs(py)
            cx = rx - r_corner
            cy = ry - r_corner
            
            if ax > cx and ay > cy:
                dx = ax - cx
                dy = ay - cy
                return (dx*dx + dy*dy) <= (r_corner * r_corner)
            return True

        def get_intersection(p1, p2):
            in_p, out_p = p1, p2
            if not is_inside(p1): in_p, out_p = p2, p1
            for _ in range(12): 
                mid_x = (in_p[0] + out_p[0]) / 2
                mid_y = (in_p[1] + out_p[1]) / 2
                mid = (mid_x, mid_y)
                if is_inside(mid): in_p = mid
                else: out_p = mid
            return in_p

        if not points: return []
        
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
            
        if current_segment: segments.append(current_segment)
        return segments
