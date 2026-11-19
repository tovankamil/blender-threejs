import bpy
import bmesh
import math
from mathutils import Vector, Euler, Matrix
import random

def hex_to_linear(hex_str, alpha=1.0):
    hex_str = hex_str.lstrip('#')
    r, g, b = [int(hex_str[i:i+2], 16) / 255.0 for i in (0, 2, 4)]
    def srgb_to_lin(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return (srgb_to_lin(r), srgb_to_lin(g), srgb_to_lin(b), alpha)

def perfect_night_scene():
    scene = bpy.context.scene

    def link_to(obj, c_name):
        c = bpy.data.collections.get(c_name)
        if not c:
            c = bpy.data.collections.new(c_name)
            scene.collection.children.link(c)
        for existing_c in list(obj.users_collection):
            existing_c.objects.unlink(obj)
        c.objects.link(obj)
        return obj

    def box(name, coll_name, loc, size, mat=None):
        bpy.ops.mesh.primitive_cube_add(location=loc)
        obj = bpy.context.active_object
        obj.name = name
        obj.scale = (size[0]/2, size[1]/2, size[2]/2)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        if mat:
            obj.data.materials.append(mat)
        return link_to(obj, coll_name)

    def cyl(name, coll_name, loc, r, h, segs=16, mat=None, rot=(0,0,0)):
        bpy.ops.mesh.primitive_cylinder_add(vertices=segs, radius=r, depth=h, location=loc, rotation=rot)
        obj = bpy.context.active_object
        obj.name = name
        if mat:
            obj.data.materials.append(mat)
        return link_to(obj, coll_name)

    def sphere(name, coll_name, loc, r, segs=12, rings=8, mat=None):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=segs, ring_count=rings, radius=r, location=loc)
        obj = bpy.context.active_object
        obj.name = name
        if mat:
            obj.data.materials.append(mat)
        return link_to(obj, coll_name)

    def icosphere(name, coll_name, loc, r, subdiv=1, mat=None):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdiv, radius=r, location=loc)
        obj = bpy.context.active_object
        obj.name = name
        if mat:
            obj.data.materials.append(mat)
        return link_to(obj, coll_name)

    # Clean existing items from Night_Sky, Backyard, Front_Seating to ensure zero duplicates
    for c_name in ["Night_Sky", "Backyard", "Front_Seating"]:
        c = bpy.data.collections.get(c_name)
        if c:
            for obj in list(c.objects):
                bpy.data.objects.remove(obj, do_unlink=True)

    # -------------------------------------------------------------------------
    # Materials
    # -------------------------------------------------------------------------
    def get_or_make_mat(name, color_rgba, roughness=0.7, metallic=0.0, emission=None, emission_strength=1.0, transmission=0.0, alpha=1.0):
        mat = bpy.data.materials.get(name)
        if not mat:
            mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        nodes.clear()
        
        node_out = nodes.new(type='ShaderNodeOutputMaterial')
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        
        bsdf.inputs['Base Color'].default_value = color_rgba
        bsdf.inputs['Roughness'].default_value = roughness
        bsdf.inputs['Metallic'].default_value = metallic
        
        if 'Transmission Weight' in bsdf.inputs:
            bsdf.inputs['Transmission Weight'].default_value = transmission
        elif 'Transmission' in bsdf.inputs:
            bsdf.inputs['Transmission'].default_value = transmission
            
        if 'Alpha' in bsdf.inputs:
            bsdf.inputs['Alpha'].default_value = alpha
            
        if emission:
            if 'Emission Color' in bsdf.inputs:
                bsdf.inputs['Emission Color'].default_value = emission
                bsdf.inputs['Emission Strength'].default_value = emission_strength
            elif 'Emission' in bsdf.inputs:
                bsdf.inputs['Emission'].default_value = emission
                if 'Emission Strength' in bsdf.inputs:
                    bsdf.inputs['Emission Strength'].default_value = emission_strength
                    
        mat.node_tree.links.new(bsdf.outputs['BSDF'], node_out.inputs['Surface'])
        return mat

    # Materials
    mat_backyard_grass = get_or_make_mat("Mat_BackyardGrass", hex_to_linear("#4A7C59"), roughness=0.85)
    mat_fence = get_or_make_mat("Mat_FenceWood", hex_to_linear("#C68B59"), roughness=0.75)
    mat_stepping_stone = get_or_make_mat("Mat_SteppingStone", hex_to_linear("#A6A19C"), roughness=0.88)
    mat_chair_wood = get_or_make_mat("Mat_ChairWood", hex_to_linear("#D49B6A"), roughness=0.65)
    mat_chair_cushion = get_or_make_mat("Mat_ChairCushion", hex_to_linear("#7ECBC0"), roughness=0.55)
    mat_table_top = get_or_make_mat("Mat_TableTop", hex_to_linear("#EEDCC8"), roughness=0.60)
    mat_cottage_wall = get_or_make_mat("Mat_CottageWall", hex_to_linear("#F8C5A8"), roughness=0.65)
    mat_cottage_roof = get_or_make_mat("Mat_CottageRoof", hex_to_linear("#C96F4B"), roughness=0.70)
    mat_fairy_bulb = get_or_make_mat("Mat_FairyBulb", (1.0, 0.90, 0.60, 1.0), roughness=0.2, emission=(1.0, 0.90, 0.60, 1.0), emission_strength=8.0)
    mat_moon = get_or_make_mat("Mat_Moon", hex_to_linear("#FFF4C2"), roughness=0.3, emission=hex_to_linear("#FFF4C2"), emission_strength=5.5)
    
    # Warm glowing window pane material (matches reference image's warm lit windows!)
    c_warm_lit = hex_to_linear("#FFE8A8")
    mat_window_glow = get_or_make_mat("Mat_WindowLitGlow", c_warm_lit, roughness=0.4, emission=c_warm_lit, emission_strength=3.2)
    c_warm_f2 = hex_to_linear("#FFF0C8")
    mat_f2_glow = get_or_make_mat("Mat_F2LitGlow", c_warm_f2, roughness=0.4, emission=c_warm_f2, emission_strength=2.8)

    mat_choc = bpy.data.materials.get("Mat_DarkChocolate")
    mat_cookie = bpy.data.materials.get("Mat_CookieBrown")
    mat_cream = bpy.data.materials.get("Mat_WarmCream")
    mat_pink = bpy.data.materials.get("Mat_SoftPink")
    mat_foliage_1 = bpy.data.materials.get("Mat_Foliage1")
    mat_flower_pink = bpy.data.materials.get("Mat_FlowerPink")
    mat_flower_yellow = bpy.data.materials.get("Mat_FlowerYellow")

    # =========================================================================
    # 1. NIGHTTIME ATMOSPHERE & BALANCED LIGHTING
    # =========================================================================
    world = scene.world
    if not world:
        world = bpy.data.worlds.new("Night_World")
        scene.world = world
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs['Color'].default_value = (0.006, 0.009, 0.032, 1.0)
        bg_node.inputs['Strength'].default_value = 0.28

    # Moonlight Key (Cool pale-blue directional light)
    sun = bpy.data.objects.get("Sun_Key")
    if sun and sun.data:
        sun.data.energy = 1.10
        sun.data.color = hex_to_linear("#9BB8FF")[:3]
        sun.data.angle = math.radians(16)

    # Soft Ambient Sky Fill
    sky = bpy.data.objects.get("Sky_Fill")
    if sky and sky.data:
        sky.data.energy = 0.55
        sky.data.color = (0.15, 0.22, 0.45)

    # Soft Warm Front Fill Light (Ensures pastel storefront is clearly readable and beautiful!)
    fill_lt_obj = bpy.data.objects.get("Light_Front_Fill")
    if not fill_lt_obj:
        fill_lt_data = bpy.data.lights.new("Light_Front_Fill", 'SUN')
        fill_lt_data.energy = 0.75
        fill_lt_data.color = (1.0, 0.95, 0.88)
        fill_lt_data.angle = math.radians(35)
        fill_lt_obj = bpy.data.objects.new("Light_Front_Fill", fill_lt_data)
        fill_lt_obj.location = (4.0, 8.0, 6.0)
        fill_lt_obj.rotation_euler = (math.radians(-35), math.radians(15), math.radians(-25))
        link_to(fill_lt_obj, "Lighting")

    # Warm Window Backdrops & Lights (Floor 1 Display Windows & Floor 2 Windows)
    # Assign glowing material to Floor 2 windows so they glow warm light into the night!
    for wi in [0, 1, 2]:
        w_glass = bpy.data.objects.get(f"F2_Glass_{wi}")
        if w_glass:
            w_glass.data.materials.clear()
            w_glass.data.materials.append(mat_f2_glow)

    # Floor 1 Display Windows - glowing warm backdrop planes right behind shelves
    for side, xc in [("Left", -1.85), ("Right", 1.85)]:
        glow_p = bpy.data.objects.get(f"Interior_GlowPlane_{side}")
        if glow_p:
            glow_p.location = (xc, 0.05, 1.60)
            glow_p.data.materials.clear()
            glow_p.data.materials.append(mat_window_glow)

        # Warm point lights right inside window display casting warm light outward
        in_lt = bpy.data.lights.get(f"Light_Interior_{side[0]}")
        if in_lt:
            in_lt.energy = 220.0
            in_lt.color = (1.0, 0.78, 0.38)
            bpy.data.objects[f"Light_Interior_{side[0]}"].location = (xc, 0.30, 1.70)

    # Door Window Glass - warm glowing
    door_glass = bpy.data.objects.get("Door_Glass_Pane")
    if door_glass:
        door_glass.data.materials.clear()
        door_glass.data.materials.append(mat_window_glow)

    # Door lantern
    door_lt = bpy.data.lights.get("Light_Door_Lantern")
    if door_lt:
        door_lt.energy = 90.0
        door_lt.color = (1.0, 0.82, 0.45)

    # Spotlights on Giant Cookie (bright and clear)
    for s_name in ["Spot_Cookie_-0.85", "Spot_Cookie_0.85"]:
        sp = bpy.data.lights.get(s_name)
        if sp:
            sp.energy = 85.0
            sp.color = (1.0, 0.92, 0.75)

    # "Cookie Shop" Sign text emission
    mat_sign = bpy.data.materials.get("Mat_GoldSignText")
    if mat_sign and mat_sign.use_nodes:
        bsdf = mat_sign.node_tree.nodes.get("Principled BSDF")
        if bsdf and 'Emission Strength' in bsdf.inputs:
            bsdf.inputs['Emission Strength'].default_value = 3.2

    # Wet reflective road asphalt
    mat_road = bpy.data.materials.get("Mat_Road")
    if mat_road and mat_road.use_nodes:
        bsdf = mat_road.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs['Roughness'].default_value = 0.28
            if 'Specular IOR Level' in bsdf.inputs:
                bsdf.inputs['Specular IOR Level'].default_value = 0.85
            elif 'Specular' in bsdf.inputs:
                bsdf.inputs['Specular'].default_value = 0.85

    # -------------------------------------------------------------------------
    # Streetlamp, Bench, and Props Positioning (Matching Reference Image!)
    # -------------------------------------------------------------------------
    # Streetlamp on the RIGHT side of sidewalk: X = -2.7, Y = 2.4
    lamp_objs = [o for o in bpy.data.objects if o.name.startswith("Lamp_")]
    for l_obj in lamp_objs:
        l_obj.location.x = -abs(l_obj.location.x)
        l_obj.location.y = 2.4

    # Lantern glass on streetlamp emits bright warm light
    l_glass = bpy.data.objects.get("Lamp_Lantern_Glass")
    if l_glass:
        l_glass.data.materials.clear()
        l_glass.data.materials.append(mat_fairy_bulb)

    lamp_lt_obj = bpy.data.objects.get("Light_Streetlamp")
    if lamp_lt_obj:
        lamp_lt_obj.location = (-2.7, 2.4, 2.95)
        lamp_lt_obj.data.energy = 160.0
        lamp_lt_obj.data.color = (1.0, 0.86, 0.50)
        lamp_lt_obj.data.shadow_soft_size = 0.35

    # Pool light underneath streetlamp
    pool_lt = bpy.data.objects.get("Light_Streetlamp_Pool")
    if not pool_lt:
        pool_lt_data = bpy.data.lights.new("Light_Streetlamp_Pool", 'POINT')
        pool_lt_data.energy = 95.0
        pool_lt_data.color = (1.0, 0.80, 0.40)
        pool_lt_data.shadow_soft_size = 0.6
        pool_lt = bpy.data.objects.new("Light_Streetlamp_Pool", pool_lt_data)
        link_to(pool_lt, "Lighting")
    pool_lt.location = (-2.7, 2.4, 2.65)

    # Bench on the LEFT side of sidewalk: X = 2.8, Y = 1.6
    for b_slat in [o for o in bpy.data.objects if o.name.startswith("Bench_")]:
        b_slat.location.x = abs(b_slat.location.x)

    # Planter next to bench: X = 3.8
    p_box = bpy.data.objects.get("Bench_Planter_Box")
    if p_box:
        p_diff = 3.8 - p_box.location.x
        for p_elem in [o for o in bpy.data.objects if "Bench_Planter" in o.name or "Bench_Flower" in o.name]:
            p_elem.location.x += p_diff

    # Chalkboard Menu Sign on LEFT of entrance: X = 1.35
    for chalk_o in [o for o in bpy.data.objects if o.name.startswith("Chalk_")]:
        chalk_o.location.x = abs(chalk_o.location.x)

    # Bicycle tucked neatly on far left: X = 4.3, Y = 1.8
    bike_lead = bpy.data.objects.get("Bike_Frame_Bottom")
    if bike_lead:
        b_diff = 4.3 - bike_lead.location.x
        for bike_o in [o for o in bpy.data.objects if o.name.startswith("Bike_")]:
            bike_o.location.x += b_diff

    # =========================================================================
    # 2. NIGHT SKY WITH CRESCENT MOON & TWINKLING STARS ("Night_Sky")
    # =========================================================================
    # Stylized Low-Poly Crescent Moon (Positioned high on the UPPER-RIGHT behind shop!)
    # Exactly matching reference image: floating above right chimney/roofline
    moon_x, moon_y, moon_z = -3.8, -7.5, 7.3
    me_moon = bpy.data.meshes.new("Mesh_Crescent_Moon")
    bm_moon = bmesh.new()

    outer_pts = []
    for i in range(18):
        th = math.radians(-110 + i * (220 / 17))
        outer_pts.append((1.45 * math.cos(th), 1.45 * math.sin(th)))

    inner_pts = []
    for i in range(16):
        th = math.radians(110 - i * (220 / 15))
        inner_pts.append((-0.55 + 1.15 * math.cos(th), 0.18 + 1.15 * math.sin(th)))

    poly_pts = outer_pts + inner_pts
    thick = 0.28
    v_front = [bm_moon.verts.new((px, thick/2, pz)) for px, pz in poly_pts]
    v_back = [bm_moon.verts.new((px, -thick/2, pz)) for px, pz in poly_pts]

    n_pts = len(poly_pts)
    for i in range(n_pts):
        next_i = (i + 1) % n_pts
        bm_moon.faces.new([v_front[i], v_front[next_i], v_back[next_i], v_back[i]])

    bm_moon.faces.new(v_front)
    bm_moon.faces.new(list(reversed(v_back)))

    bm_moon.to_mesh(me_moon)
    bm_moon.free()

    moon_obj = bpy.data.objects.new("Crescent_Moon", me_moon)
    moon_obj.location = (moon_x, moon_y, moon_z)
    moon_obj.scale = (1.25, 1.25, 1.25)
    moon_obj.rotation_euler = (0, 0, math.radians(20))
    moon_obj.data.materials.append(mat_moon)
    link_to(moon_obj, "Night_Sky")

    # Moon ambient backlight
    m_lt = bpy.data.objects.get("Light_Moon_Glow")
    if not m_lt:
        m_lt_data = bpy.data.lights.new("Light_Moon_Glow", 'POINT')
        m_lt_data.energy = 110.0
        m_lt_data.color = hex_to_linear("#FFF4C2")[:3]
        m_lt_data.shadow_soft_size = 0.9
        m_lt = bpy.data.objects.new("Light_Moon_Glow", m_lt_data)
        link_to(m_lt, "Lighting")
    m_lt.location = (moon_x, moon_y + 0.8, moon_z)

    # 4 Animated Star Materials
    star_mats = []
    for s_idx, s_hex in enumerate(["#FFFFFF", "#FFF6D6", "#FFFBF0", "#FFEAC2"]):
        s_mat = get_or_make_mat(f"Mat_Star_{s_idx+1}", hex_to_linear(s_hex), roughness=0.2, emission=hex_to_linear(s_hex), emission_strength=1.5)
        star_mats.append(s_mat)

    phases = [0.0, math.pi * 0.5, math.pi * 1.0, math.pi * 1.5]
    for m_i, s_mat in enumerate(star_mats):
        bsdf = s_mat.node_tree.nodes.get("Principled BSDF")
        phase = phases[m_i]
        for f in range(1, 241, 15):
            angle = (f / 240.0) * math.pi * 4.0 + phase
            val = 1.95 + 1.55 * math.sin(angle)
            bsdf.inputs['Emission Strength'].default_value = val
            bsdf.inputs['Emission Strength'].keyframe_insert("default_value", frame=f)

    scene.frame_start = 1
    scene.frame_end = 240
    scene.render.fps = 24

    # 52 Small Low-Poly Stars (Diamond Sparkles & Dots)
    random.seed(202)
    me_diamond = bpy.data.meshes.new("Mesh_DiamondStar")
    bm_d = bmesh.new()
    r_l, r_s, thk = 0.20, 0.11, 0.04
    v_cf = bm_d.verts.new((0, thk, 0))
    v_cb = bm_d.verts.new((0, -thk, 0))
    v_n = bm_d.verts.new((0, 0, r_l))
    v_s = bm_d.verts.new((0, 0, -r_l))
    v_e = bm_d.verts.new((r_s, 0, 0))
    v_w = bm_d.verts.new((-r_s, 0, 0))
    bm_d.faces.new([v_cf, v_n, v_e])
    bm_d.faces.new([v_cf, v_e, v_s])
    bm_d.faces.new([v_cf, v_s, v_w])
    bm_d.faces.new([v_cf, v_w, v_n])
    bm_d.faces.new([v_cb, v_e, v_n])
    bm_d.faces.new([v_cb, v_s, v_e])
    bm_d.faces.new([v_cb, v_w, v_s])
    bm_d.faces.new([v_cb, v_n, v_w])
    bm_d.to_mesh(me_diamond)
    bm_d.free()

    star_coords = []
    while len(star_coords) < 54:
        sx = random.uniform(-9.5, 9.5)
        sz = random.uniform(4.0, 10.5)
        sy = random.uniform(-8.5, -13.0)
        if -2.6 < sx < 2.6 and sz < 6.4:
            continue
        if (sx - moon_x)**2 + (sz - moon_z)**2 < 1.8:
            continue
        star_coords.append((sx, sy, sz))

    for st_i, (sx, sy, sz) in enumerate(star_coords):
        s_mat = star_mats[st_i % 4]
        if st_i % 2 == 0:
            st_obj = bpy.data.objects.new(f"Star_Diamond_{st_i}", me_diamond)
            st_obj.location = (sx, sy, sz)
            scale_fac = random.uniform(0.65, 1.25)
            st_obj.scale = (scale_fac, scale_fac, scale_fac)
            st_obj.rotation_euler = (0, 0, math.radians(random.uniform(-15, 15)))
            st_obj.data.materials.append(s_mat)
            link_to(st_obj, "Night_Sky")
        else:
            r_val = random.uniform(0.06, 0.12)
            icosphere(f"Star_Ico_{st_i}", "Night_Sky", (sx, sy, sz), r=r_val, subdiv=1, mat=s_mat)

    # =========================================================================
    # 3. BACKYARD AREA ("Backyard")
    # =========================================================================
    # Green Grass Lawn
    box("Backyard_Lawn", "Backyard", (0, -4.0, 0.08), (16.0, 8.0, 0.16), mat_backyard_grass)

    # Picket Fence
    me_picket = bpy.data.meshes.new("Mesh_Picket")
    bm_p = bmesh.new()
    pw, pt, ph = 0.12, 0.03, 0.85
    v1 = bm_p.verts.new((-pw/2, -pt/2, 0))
    v2 = bm_p.verts.new((pw/2, -pt/2, 0))
    v3 = bm_p.verts.new((pw/2, -pt/2, ph - pw/2))
    v4 = bm_p.verts.new((0, -pt/2, ph))
    v5 = bm_p.verts.new((-pw/2, -pt/2, ph - pw/2))
    v1b = bm_p.verts.new((-pw/2, pt/2, 0))
    v2b = bm_p.verts.new((pw/2, pt/2, 0))
    v3b = bm_p.verts.new((pw/2, pt/2, ph - pw/2))
    v4b = bm_p.verts.new((0, pt/2, ph))
    v5b = bm_p.verts.new((-pw/2, pt/2, ph - pw/2))
    bm_p.faces.new([v1, v2, v3, v4, v5])
    bm_p.faces.new([v5b, v4b, v3b, v2b, v1b])
    bm_p.faces.new([v1, v1b, v2b, v2])
    bm_p.faces.new([v2, v2b, v3b, v3])
    bm_p.faces.new([v3, v3b, v4b, v4])
    bm_p.faces.new([v4, v4b, v5b, v5])
    bm_p.faces.new([v5, v5b, v1b, v1])
    bm_p.to_mesh(me_picket)
    bm_p.free()

    def make_fence_line(name_prefix, start_pos, end_pos, num_pickets):
        p1 = Vector(start_pos)
        p2 = Vector(end_pos)
        diff = p2 - p1
        dist = diff.length
        rot_z = math.atan2(diff.y, diff.x)
        
        mid = (p1 + p2) * 0.5
        rail1 = box(f"{name_prefix}_Rail1", "Backyard", (mid.x, mid.y, p1.z + 0.25), (dist, 0.04, 0.06), mat_fence)
        rail1.rotation_euler = (0, 0, rot_z)
        rail2 = box(f"{name_prefix}_Rail2", "Backyard", (mid.x, mid.y, p1.z + 0.60), (dist, 0.04, 0.06), mat_fence)
        rail2.rotation_euler = (0, 0, rot_z)

        for pi in range(num_pickets):
            frac = (pi + 0.5) / num_pickets
            px = p1.x + diff.x * frac
            py = p1.y + diff.y * frac
            p_obj = bpy.data.objects.new(f"{name_prefix}_Picket_{pi}", me_picket)
            p_obj.location = (px, py, p1.z)
            p_obj.rotation_euler = (0, 0, rot_z)
            p_obj.data.materials.append(mat_fence)
            link_to(p_obj, "Backyard")

    make_fence_line("Fence_L_Front", (6.8, 0.0, 0.16), (6.8, -3.5, 0.16), 14)
    make_fence_line("Fence_L_Back", (6.8, -3.5, 0.16), (6.8, -7.0, 0.16), 14)
    make_fence_line("Fence_L_Conn", (3.05, -1.8, 0.16), (6.8, -1.8, 0.16), 15)

    make_fence_line("Fence_Back_1", (6.8, -7.0, 0.16), (0.0, -7.0, 0.16), 25)
    make_fence_line("Fence_Back_2", (0.0, -7.0, 0.16), (-6.8, -7.0, 0.16), 25)

    make_fence_line("Fence_R_Front", (-6.8, 0.0, 0.16), (-6.8, -3.5, 0.16), 14)
    make_fence_line("Fence_R_Back", (-6.8, -3.5, 0.16), (-6.8, -7.0, 0.16), 14)

    # Backyard Cottage (Located on the RIGHT side, visible between shop and right tree)
    cottage_x, cottage_y, cottage_z = -3.6, -2.4, 1.45
    box("Backyard_Cottage_Wall", "Backyard", (cottage_x, cottage_y, cottage_z), (2.2, 2.6, 2.6), mat_cottage_wall)
    cottage_roof = box("Backyard_Cottage_Roof", "Backyard", (cottage_x, cottage_y, cottage_z + 1.45), (2.5, 2.9, 0.16), mat_cottage_roof)
    cottage_roof.rotation_euler = (0, math.radians(12), 0)

    # Cottage Back Door (facing front towards sidewalk)
    box("Backyard_Door_Frame", "Backyard", (-2.6, -1.1, 1.05), (0.75, 0.08, 1.65), mat_cream)
    box("Backyard_Door_Slab", "Backyard", (-2.6, -1.08, 1.05), (0.65, 0.04, 1.55), mat_fence)
    box("Backyard_Door_Glass", "Backyard", (-2.6, -1.06, 1.45), (0.45, 0.02, 0.55), mat_window_glow)

    # Porch Lamp above Back Door
    cyl("Backyard_Porch_Fixture", "Backyard", (-2.6, -1.02, 2.0), r=0.05, h=0.04, segs=8, mat=mat_fence, rot=(math.radians(90), 0, 0))
    cyl("Backyard_Porch_Shade", "Backyard", (-2.6, -0.96, 1.95), r=0.10, h=0.08, segs=8, mat=mat_fence)
    sphere("Backyard_Porch_Bulb", "Backyard", (-2.6, -0.96, 1.90), r=0.04, segs=8, rings=6, mat=mat_fairy_bulb)

    porch_lt_obj = bpy.data.objects.get("Light_Porch_Lamp")
    if not porch_lt_obj:
        porch_lt_data = bpy.data.lights.new("Light_Porch_Lamp", 'POINT')
        porch_lt_data.energy = 65.0
        porch_lt_data.color = (1.0, 0.82, 0.45)
        porch_lt_data.shadow_soft_size = 0.3
        porch_lt_obj = bpy.data.objects.new("Light_Porch_Lamp", porch_lt_data)
        link_to(porch_lt_obj, "Lighting")
    porch_lt_obj.location = (-2.6, -0.95, 1.88)

    # Stepping Stone Path on the right grass
    stone_coords = [
        (-3.0, 0.2, 0.17),
        (-3.0, -0.2, 0.17),
        (-2.9, -0.6, 0.17),
        (-2.7, -1.0, 0.17),
    ]
    for s_i, (sx, sy, sz) in enumerate(stone_coords):
        cyl(f"SteppingStone_{s_i}", "Backyard", (sx, sy, sz), r=0.22, h=0.04, segs=7, mat=mat_stepping_stone)

    # Bushes and Flower Bed in Backyard
    icosphere("Backyard_Bush_R1", "Backyard", (-3.2, -0.2, 0.50), r=0.35, subdiv=1, mat=mat_foliage_1)
    box("Backyard_Flower_Bed", "Backyard", (-4.8, -1.0, 0.30), (1.4, 0.6, 0.20), mat_fence)
    for fi, (fx, fy, f_mat) in enumerate([(-0.4, 0.0, mat_flower_pink), (0.0, 0.1, mat_flower_yellow), (0.4, -0.1, mat_flower_pink)]):
        sphere(f"Backyard_Bed_Flower_{fi}", "Backyard", (-4.8 + fx, -1.0 + fy, 0.46), r=0.07, segs=8, rings=6, mat=f_mat)

    # Warm String Lights (Fairy Lights) on Right Side (Shop corner to Cottage)
    start_wire = Vector((-3.05, 0.0, 2.7))
    end_wire = Vector((-4.6, -2.2, 2.5))
    num_bulbs = 10
    for bi in range(num_bulbs):
        frac = (bi + 0.5) / num_bulbs
        dip = 0.32 * math.sin(frac * math.pi)
        pos = start_wire + (end_wire - start_wire) * frac
        pos.z -= dip
        sphere(f"FairyBulb_{bi}", "Backyard", (pos.x, pos.y, pos.z), r=0.045, segs=8, rings=6, mat=mat_fairy_bulb)

    str_lt_obj = bpy.data.objects.get("Light_StringLights")
    if not str_lt_obj:
        str_lt_data = bpy.data.lights.new("Light_StringLights", 'POINT')
        str_lt_data.energy = 55.0
        str_lt_data.color = (1.0, 0.82, 0.45)
        str_lt_data.shadow_soft_size = 0.4
        str_lt_obj = bpy.data.objects.new("Light_StringLights", str_lt_data)
        link_to(str_lt_obj, "Lighting")
    str_lt_obj.location = (-3.8, -1.1, 2.3)

    # =========================================================================
    # 4. FRONT OUTDOOR SEATING ("Front_Seating")
    # =========================================================================
    # Table & 2 Chairs on RIGHT side of entrance (X = -1.90, Y = 1.70)
    tab_x, tab_y, tab_z = -1.90, 1.70, 0.205

    # Round Café Table
    cyl("Cafe_Table_Top", "Front_Seating", (tab_x, tab_y, tab_z + 0.54), r=0.38, h=0.04, segs=18, mat=mat_table_top)
    cyl("Cafe_Table_Rim", "Front_Seating", (tab_x, tab_y, tab_z + 0.53), r=0.40, h=0.02, segs=18, mat=mat_chair_wood)
    cyl("Cafe_Table_Pedestal", "Front_Seating", (tab_x, tab_y, tab_z + 0.26), r=0.035, h=0.50, segs=8, mat=mat_fence)
    cyl("Cafe_Table_Base", "Front_Seating", (tab_x, tab_y, tab_z + 0.02), r=0.22, h=0.03, segs=12, mat=mat_fence)

    def make_oriented_chair(name, loc, rot_rad):
        for lx, ly in [(-0.16, -0.16), (0.16, -0.16), (-0.16, 0.16), (0.16, 0.16)]:
            rx = lx * math.cos(rot_rad) - ly * math.sin(rot_rad)
            ry = lx * math.sin(rot_rad) + ly * math.cos(rot_rad)
            cyl(f"{name}_Leg_{lx}_{ly}", "Front_Seating", (loc[0] + rx, loc[1] + ry, loc[2] + 0.20), r=0.025, h=0.40, segs=6, mat=mat_chair_wood)
        
        s_frame = box(f"{name}_SeatFrame", "Front_Seating", (loc[0], loc[1], loc[2] + 0.40), (0.38, 0.38, 0.03), mat_chair_wood)
        s_frame.rotation_euler = (0, 0, rot_rad)
        s_cush = box(f"{name}_Cushion", "Front_Seating", (loc[0], loc[1], loc[2] + 0.435), (0.35, 0.35, 0.045), mat_chair_cushion)
        s_cush.rotation_euler = (0, 0, rot_rad)

        for bx_l in [-0.15, 0.15]:
            rx = bx_l * math.cos(rot_rad) - (-0.15) * math.sin(rot_rad)
            ry = bx_l * math.sin(rot_rad) + (-0.15) * math.cos(rot_rad)
            cyl(f"{name}_BackUp_{bx_l}", "Front_Seating", (loc[0] + rx, loc[1] + ry, loc[2] + 0.62), r=0.02, h=0.44, segs=6, mat=mat_chair_wood)

        for bz, bw in [(0.68, 0.05), (0.80, 0.06)]:
            rx = 0.0 * math.cos(rot_rad) - (-0.15) * math.sin(rot_rad)
            ry = 0.0 * math.sin(rot_rad) + (-0.15) * math.cos(rot_rad)
            slat = box(f"{name}_BackSlat_{bz}", "Front_Seating", (loc[0] + rx, loc[1] + ry, loc[2] + bz), (0.32, 0.025, bw), mat_chair_wood)
            slat.rotation_euler = (0, 0, rot_rad)

    make_oriented_chair("Cafe_Chair_Left", (tab_x + 0.48, tab_y, tab_z), math.radians(-90))
    make_oriented_chair("Cafe_Chair_Right", (tab_x - 0.48, tab_y, tab_z), math.radians(90))

    # Tableware
    cyl("Cafe_Saucer_1", "Front_Seating", (tab_x - 0.12, tab_y - 0.08, tab_z + 0.57), r=0.09, h=0.015, segs=12, mat=mat_cream)
    cyl("Cafe_Cup_1", "Front_Seating", (tab_x - 0.12, tab_y - 0.08, tab_z + 0.62), r=0.06, h=0.08, segs=12, mat=mat_pink)
    cyl("Cafe_Coffee_1", "Front_Seating", (tab_x - 0.12, tab_y - 0.08, tab_z + 0.65), r=0.05, h=0.015, segs=8, mat=mat_choc)

    cyl("Cafe_Saucer_2", "Front_Seating", (tab_x + 0.12, tab_y + 0.08, tab_z + 0.57), r=0.09, h=0.015, segs=12, mat=mat_cream)
    cyl("Cafe_Cup_2", "Front_Seating", (tab_x + 0.12, tab_y + 0.08, tab_z + 0.62), r=0.06, h=0.08, segs=12, mat=mat_cream)
    cyl("Cafe_Coffee_2", "Front_Seating", (tab_x + 0.12, tab_y + 0.08, tab_z + 0.65), r=0.05, h=0.015, segs=8, mat=mat_choc)

    cyl("Cafe_Plate", "Front_Seating", (tab_x + 0.04, tab_y - 0.06, tab_z + 0.57), r=0.12, h=0.015, segs=14, mat=mat_cream)
    cyl("Cafe_Cookie", "Front_Seating", (tab_x + 0.04, tab_y - 0.06, tab_z + 0.59), r=0.065, h=0.018, segs=10, mat=mat_cookie)
    cyl("Cafe_Chip1", "Front_Seating", (tab_x + 0.02, tab_y - 0.05, tab_z + 0.602), r=0.02, h=0.01, segs=5, mat=mat_choc)
    cyl("Cafe_Chip2", "Front_Seating", (tab_x + 0.06, tab_y - 0.07, tab_z + 0.602), r=0.016, h=0.01, segs=5, mat=mat_choc)

    print("Perfect night scene alignment executed!")
    return "Perfect night scene alignment completed."

perfect_night_scene()
