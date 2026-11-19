import bpy
import bmesh
import math
import mathutils
from mathutils import Vector, Euler, Matrix
import random

def hex_to_linear(hex_str, alpha=1.0):
    hex_str = hex_str.lstrip('#')
    r, g, b = [int(hex_str[i:i+2], 16) / 255.0 for i in (0, 2, 4)]
    def srgb_to_lin(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return (srgb_to_lin(r), srgb_to_lin(g), srgb_to_lin(b), alpha)

def apply_night_expansion():
    scene = bpy.context.scene

    # -------------------------------------------------------------------------
    # 1. Collections Setup ("Night_Sky", "Backyard", "Front_Seating")
    # -------------------------------------------------------------------------
    def link_to(obj, c_name):
        c = bpy.data.collections.get(c_name)
        if not c:
            c = bpy.data.collections.new(c_name)
            scene.collection.children.link(c)
        for existing_c in list(obj.users_collection):
            existing_c.objects.unlink(obj)
        c.objects.link(obj)
        return obj


    # -------------------------------------------------------------------------
    # Helper Modeling Functions
    # -------------------------------------------------------------------------
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

    # Materials for additions
    mat_backyard_grass = get_or_make_mat("Mat_BackyardGrass", hex_to_linear("#4A7C59"), roughness=0.85)
    mat_fence = get_or_make_mat("Mat_FenceWood", hex_to_linear("#C68B59"), roughness=0.75)
    mat_stepping_stone = get_or_make_mat("Mat_SteppingStone", hex_to_linear("#A6A19C"), roughness=0.88)
    mat_chair_wood = get_or_make_mat("Mat_ChairWood", hex_to_linear("#D49B6A"), roughness=0.65)
    mat_chair_cushion = get_or_make_mat("Mat_ChairCushion", hex_to_linear("#7ECBC0"), roughness=0.55)
    mat_table_top = get_or_make_mat("Mat_TableTop", hex_to_linear("#EEDCC8"), roughness=0.60)
    mat_cottage_wall = get_or_make_mat("Mat_CottageWall", hex_to_linear("#F8C5A8"), roughness=0.65)
    mat_cottage_roof = get_or_make_mat("Mat_CottageRoof", hex_to_linear("#C96F4B"), roughness=0.70)
    mat_fairy_bulb = get_or_make_mat("Mat_FairyBulb", (1.0, 0.82, 0.45, 1.0), roughness=0.2, emission=(1.0, 0.82, 0.45, 1.0), emission_strength=5.0)
    mat_moon = get_or_make_mat("Mat_Moon", hex_to_linear("#FFF4C2"), roughness=0.3, emission=hex_to_linear("#FFF4C2"), emission_strength=4.5)
    mat_choc = bpy.data.materials.get("Mat_DarkChocolate") or get_or_make_mat("Mat_DarkChocolate", hex_to_linear("#4A2C18"))
    mat_cookie = bpy.data.materials.get("Mat_CookieBrown") or get_or_make_mat("Mat_CookieBrown", hex_to_linear("#D49B6A"))
    mat_cream = bpy.data.materials.get("Mat_WarmCream") or get_or_make_mat("Mat_WarmCream", hex_to_linear("#F9F3EB"))
    mat_pink = bpy.data.materials.get("Mat_SoftPink") or get_or_make_mat("Mat_SoftPink", hex_to_linear("#F4B2B2"))
    mat_foliage_1 = bpy.data.materials.get("Mat_Foliage1") or get_or_make_mat("Mat_Foliage1", hex_to_linear("#68B058"))
    mat_flower_pink = bpy.data.materials.get("Mat_FlowerPink") or get_or_make_mat("Mat_FlowerPink", hex_to_linear("#FF7B90"))
    mat_flower_yellow = bpy.data.materials.get("Mat_FlowerYellow") or get_or_make_mat("Mat_FlowerYellow", hex_to_linear("#FFDA44"))

    # =========================================================================
    # 2. NIGHTTIME ATMOSPHERE & LIGHTING UPDATES
    # =========================================================================
    # Deep Stylized Night Sky World Background (#0B1026, strength ~0.20)
    world = scene.world
    if not world:
        world = bpy.data.worlds.new("Night_World")
        scene.world = world
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs['Color'].default_value = (0.003, 0.005, 0.022, 1.0)
        bg_node.inputs['Strength'].default_value = 0.20

    # Pale-Blue Moonlight (replacing bright sun)
    sun = bpy.data.objects.get("Sun_Key")
    if sun and sun.data:
        sun.data.energy = 0.65
        sun.data.color = hex_to_linear("#9BB8FF")[:3]
        sun.data.angle = math.radians(22)

    # Ambient deep midnight sky fill
    sky = bpy.data.objects.get("Sky_Fill")
    if sky and sky.data:
        sky.data.energy = 0.25
        sky.data.color = (0.05, 0.08, 0.25)

    # Boost Warm Golden Interior Window Glow (#FFAE52, energy 280.0)
    c_warm_gold = hex_to_linear("#FFAE52")[:3]
    for side in ["L", "R"]:
        in_lt = bpy.data.lights.get(f"Light_Interior_{side}")
        if in_lt:
            in_lt.energy = 280.0
            in_lt.color = c_warm_gold
            in_lt.shadow_soft_size = 0.40

    door_lt = bpy.data.lights.get("Light_Door_Lantern")
    if door_lt:
        door_lt.energy = 90.0
        door_lt.color = (1.0, 0.75, 0.30)

    # Interior Glow Planes Material
    mat_glow = bpy.data.materials.get("Mat_InteriorGlow")
    if mat_glow and mat_glow.use_nodes:
        bsdf = mat_glow.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            if 'Emission Color' in bsdf.inputs:
                bsdf.inputs['Emission Color'].default_value = (1.0, 0.75, 0.32, 1.0)
                bsdf.inputs['Emission Strength'].default_value = 5.0

    # Streetlamp Lantern Warm Glow & Point Light
    lamp_lt = bpy.data.lights.get("Light_Streetlamp")
    if lamp_lt:
        lamp_lt.energy = 130.0
        lamp_lt.color = (1.0, 0.80, 0.38)
        lamp_lt.shadow_soft_size = 0.30
    
    # Downward Streetlamp Pool Light
    if not bpy.data.objects.get("Light_Streetlamp_Pool"):
        pool_lt_data = bpy.data.lights.new("Light_Streetlamp_Pool", 'POINT')
        pool_lt_data.energy = 85.0
        pool_lt_data.color = (1.0, 0.78, 0.35)
        pool_lt_data.shadow_soft_size = 0.50
        pool_lt_obj = bpy.data.objects.new("Light_Streetlamp_Pool", pool_lt_data)
        pool_lt_obj.location = (2.68, 2.3, 2.65)
        link_to(pool_lt_obj, "Lighting")

    # Spotlights on Giant Cookie & Store Sign
    for s_name in ["Spot_Cookie_-0.85", "Spot_Cookie_0.85"]:
        sp = bpy.data.lights.get(s_name)
        if sp:
            sp.energy = 65.0
            sp.color = (1.0, 0.90, 0.70)

    mat_sign = bpy.data.materials.get("Mat_GoldSignText")
    if mat_sign and mat_sign.use_nodes:
        bsdf = mat_sign.node_tree.nodes.get("Principled BSDF")
        if bsdf and 'Emission Strength' in bsdf.inputs:
            bsdf.inputs['Emission Strength'].default_value = 2.2

    # Wet / Glossy Night Asphalt Reflection
    mat_road = bpy.data.materials.get("Mat_Road")
    if mat_road and mat_road.use_nodes:
        bsdf = mat_road.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs['Roughness'].default_value = 0.35
            if 'Specular IOR Level' in bsdf.inputs:
                bsdf.inputs['Specular IOR Level'].default_value = 0.75
            elif 'Specular' in bsdf.inputs:
                bsdf.inputs['Specular'].default_value = 0.75

    # =========================================================================
    # 3. SKY WITH MOON & SLOWLY TWINKLING STARS ("Night_Sky")
    # =========================================================================
    # Low-Poly Crescent Moon (Positioned high on upper-right behind shop)
    moon_x, moon_y, moon_z = 2.4, -7.5, 6.8
    me_moon = bpy.data.meshes.new("Mesh_Crescent_Moon")
    bm_moon = bmesh.new()

    outer_pts = []
    for i in range(18):
        th = math.radians(-110 + i * (220 / 17))
        outer_pts.append((1.35 * math.cos(th), 1.35 * math.sin(th)))

    inner_pts = []
    for i in range(16):
        th = math.radians(110 - i * (220 / 15))
        inner_pts.append((0.50 + 1.05 * math.cos(th), 0.15 + 1.05 * math.sin(th)))

    poly_pts = outer_pts + inner_pts
    thick = 0.24
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
    moon_obj.rotation_euler = (0, 0, math.radians(-15))
    moon_obj.data.materials.append(mat_moon)
    link_to(moon_obj, "Night_Sky")

    # Moonlight point light behind building
    if not bpy.data.objects.get("Light_Moon_Glow"):
        m_lt_data = bpy.data.lights.new("Light_Moon_Glow", 'POINT')
        m_lt_data.energy = 90.0
        m_lt_data.color = hex_to_linear("#FFF4C2")[:3]
        m_lt_data.shadow_soft_size = 0.8
        m_lt_obj = bpy.data.objects.new("Light_Moon_Glow", m_lt_data)
        m_lt_obj.location = (moon_x, moon_y + 0.8, moon_z)
        link_to(m_lt_obj, "Lighting")

    # 4 Emissive Star Materials with Animated Twinkling
    star_mats = []
    for s_idx, s_hex in enumerate(["#FFFFFF", "#FFF6D6", "#FFFBF0", "#FFEAC2"]):
        s_mat = get_or_make_mat(f"Mat_Star_{s_idx+1}", hex_to_linear(s_hex), roughness=0.2, emission=hex_to_linear(s_hex), emission_strength=1.5)
        star_mats.append(s_mat)

    # Animate Emission Strength for each star material (1 to 240 frames)
    # Staggered smooth sinusoidal oscillation between 0.4 and 3.5
    phases = [0.0, math.pi * 0.5, math.pi * 1.0, math.pi * 1.5]
    for m_i, s_mat in enumerate(star_mats):
        bsdf = s_mat.node_tree.nodes.get("Principled BSDF")
        phase = phases[m_i]
        for f in range(1, 241, 15):
            angle = (f / 240.0) * math.pi * 4.0 + phase
            # Sine wave oscillating smoothly between 0.4 and 3.5
            val = 1.95 + 1.55 * math.sin(angle)
            bsdf.inputs['Emission Strength'].default_value = val
            bsdf.inputs['Emission Strength'].keyframe_insert("default_value", frame=f)

    # Set frame range
    scene.frame_start = 1
    scene.frame_end = 240
    scene.render.fps = 24

    # Generate 50 Small Low-Poly Stars (Diamond Stars and Tiny Icospheres)
    random.seed(42)
    star_coords = []
    # Avoid center box of the building (X: -3 to 3, Z: 0 to 6.3)
    while len(star_coords) < 52:
        sx = random.uniform(-8.8, 8.8)
        sz = random.uniform(3.8, 9.8)
        sy = random.uniform(-8.5, -12.5)
        # Filter out stars hidden behind the shop
        if -2.8 < sx < 2.8 and sz < 6.2:
            continue
        # Avoid moon center
        if (sx - moon_x)**2 + (sz - moon_z)**2 < 1.4:
            continue
        star_coords.append((sx, sy, sz))

    # Helper for 4-point diamond star mesh
    def create_diamond_mesh(r_l, r_s, thk):
        me = bpy.data.meshes.new("Mesh_DiamondStar")
        bm = bmesh.new()
        v_cf = bm.verts.new((0, thk, 0))
        v_cb = bm.verts.new((0, -thk, 0))
        v_n = bm.verts.new((0, 0, r_l))
        v_s = bm.verts.new((0, 0, -r_l))
        v_e = bm.verts.new((r_s, 0, 0))
        v_w = bm.verts.new((-r_s, 0, 0))
        bm.faces.new([v_cf, v_n, v_e])
        bm.faces.new([v_cf, v_e, v_s])
        bm.faces.new([v_cf, v_s, v_w])
        bm.faces.new([v_cf, v_w, v_n])
        bm.faces.new([v_cb, v_e, v_n])
        bm.faces.new([v_cb, v_s, v_e])
        bm.faces.new([v_cb, v_w, v_s])
        bm.faces.new([v_cb, v_n, v_w])
        bm.to_mesh(me)
        bm.free()
        return me

    me_diamond = create_diamond_mesh(r_l=0.22, r_s=0.12, thk=0.04)

    for st_i, (sx, sy, sz) in enumerate(star_coords):
        s_mat = star_mats[st_i % 4]
        if st_i % 2 == 0:
            # 4-point Diamond Star
            st_obj = bpy.data.objects.new(f"Star_Diamond_{st_i}", me_diamond)
            st_obj.location = (sx, sy, sz)
            scale_fac = random.uniform(0.65, 1.25)
            st_obj.scale = (scale_fac, scale_fac, scale_fac)
            st_obj.rotation_euler = (0, 0, math.radians(random.uniform(-15, 15)))
            st_obj.data.materials.append(s_mat)
            link_to(st_obj, "Night_Sky")
        else:
            # Tiny Icosphere Star
            r_val = random.uniform(0.06, 0.12)
            st_obj = icosphere(f"Star_Ico_{st_i}", "Night_Sky", (sx, sy, sz), r=r_val, subdiv=1, mat=s_mat)

    # =========================================================================
    # 4. BACKYARD AREA ("Backyard")
    # =========================================================================
    # Green Grass Ground Lawn (Directly behind Cookie Shop and Sidewalk)
    # Spans X: -8.0 to +8.0, Y: 0.0 to -8.0, Z: 0.08
    box("Backyard_Lawn", "Backyard", (0, -4.0, 0.08), (16.0, 8.0, 0.16), mat_backyard_grass)

    # Low-Poly Wooden Picket Fence along perimeter
    # Picket helper
    me_picket = bpy.data.meshes.new("Mesh_Picket")
    bm_p = bmesh.new()
    pw, pt, ph = 0.12, 0.03, 0.85
    # Vertices of a picket with pointed triangle top
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
        
        # Horizontal cross rails
        mid = (p1 + p2) * 0.5
        rail1 = box(f"{name_prefix}_Rail1", "Backyard", (mid.x, mid.y, p1.z + 0.25), (dist, 0.04, 0.06), mat_fence)
        rail1.rotation_euler = (0, 0, rot_z)
        rail2 = box(f"{name_prefix}_Rail2", "Backyard", (mid.x, mid.y, p1.z + 0.60), (dist, 0.04, 0.06), mat_fence)
        rail2.rotation_euler = (0, 0, rot_z)

        # Repeating vertical pickets
        for pi in range(num_pickets):
            frac = (pi + 0.5) / num_pickets
            px = p1.x + diff.x * frac
            py = p1.y + diff.y * frac
            p_obj = bpy.data.objects.new(f"{name_prefix}_Picket_{pi}", me_picket)
            p_obj.location = (px, py, p1.z)
            p_obj.rotation_euler = (0, 0, rot_z)
            p_obj.data.materials.append(mat_fence)
            link_to(p_obj, "Backyard")

    # Left fence lines
    make_fence_line("Fence_Left_Front", (-6.8, 0.0, 0.16), (-6.8, -3.5, 0.16), 14)
    make_fence_line("Fence_Left_Mid", (-6.8, -3.5, 0.16), (-6.8, -7.0, 0.16), 14)
    make_fence_line("Fence_Left_Connector", (-3.05, -1.8, 0.16), (-6.8, -1.8, 0.16), 15)

    # Back fence line
    make_fence_line("Fence_Back_L", (-6.8, -7.0, 0.16), (0.0, -7.0, 0.16), 25)
    make_fence_line("Fence_Back_R", (0.0, -7.0, 0.16), (6.8, -7.0, 0.16), 25)

    # Right fence line
    make_fence_line("Fence_Right_Front", (6.8, 0.0, 0.16), (6.8, -3.5, 0.16), 14)
    make_fence_line("Fence_Right_Mid", (6.8, -3.5, 0.16), (6.8, -7.0, 0.16), 14)

    # Right Backyard Cottage / Extension (as seen in reference image)
    cottage_x, cottage_y, cottage_z = 3.6, -2.4, 1.45
    box("Backyard_Cottage_Wall", "Backyard", (cottage_x, cottage_y, cottage_z), (2.2, 2.6, 2.6), mat_cottage_wall)
    
    # Slanted roof on cottage
    cottage_roof = box("Backyard_Cottage_Roof", "Backyard", (cottage_x, cottage_y, cottage_z + 1.45), (2.5, 2.9, 0.16), mat_cottage_roof)
    cottage_roof.rotation_euler = (0, math.radians(-12), 0)

    # Back Door on Cottage (facing front/sidewalk)
    box("Backyard_Door_Frame", "Backyard", (2.6, -1.1, 1.05), (0.75, 0.08, 1.65), mat_cream)
    box("Backyard_Door_Slab", "Backyard", (2.6, -1.08, 1.05), (0.65, 0.04, 1.55), mat_fence)
    box("Backyard_Door_Glass", "Backyard", (2.6, -1.06, 1.45), (0.45, 0.02, 0.55), mat_glow)

    # Porch Lamp above Cottage Back Door
    cyl("Backyard_Porch_Fixture", "Backyard", (2.6, -1.02, 2.0), r=0.05, h=0.04, segs=8, mat=mat_fence, rot=(math.radians(90), 0, 0))
    cyl("Backyard_Porch_Shade", "Backyard", (2.6, -0.96, 1.95), r=0.10, h=0.08, segs=8, mat=mat_fence)
    sphere("Backyard_Porch_Bulb", "Backyard", (2.6, -0.96, 1.90), r=0.04, segs=8, rings=6, mat=mat_fairy_bulb)

    porch_lt_data = bpy.data.lights.new("Light_Porch_Lamp", 'POINT')
    porch_lt_data.energy = 45.0
    porch_lt_data.color = (1.0, 0.82, 0.45)
    porch_lt_data.shadow_soft_size = 0.3
    porch_lt_obj = bpy.data.objects.new("Light_Porch_Lamp", porch_lt_data)
    porch_lt_obj.location = (2.6, -0.95, 1.88)
    link_to(porch_lt_obj, "Lighting")

    # Stepping Stone Path (curving from sidewalk edge to back door)
    stone_coords = [
        (3.0, 0.2, 0.17),
        (3.0, -0.2, 0.17),
        (2.9, -0.6, 0.17),
        (2.7, -1.0, 0.17),
    ]
    for s_i, (sx, sy, sz) in enumerate(stone_coords):
        cyl(f"SteppingStone_{s_i}", "Backyard", (sx, sy, sz), r=0.22, h=0.04, segs=7, mat=mat_stepping_stone)

    # Low-poly Bushes & Planter Beds on Backyard Grass
    icosphere("Backyard_Bush_L1", "Backyard", (-3.8, -2.5, 0.55), r=0.45, subdiv=1, mat=mat_foliage_1)
    icosphere("Backyard_Bush_L2", "Backyard", (-5.2, -3.2, 0.50), r=0.38, subdiv=1, mat=mat_foliage_1)
    icosphere("Backyard_Bush_R1", "Backyard", (3.2, -0.2, 0.50), r=0.35, subdiv=1, mat=mat_foliage_1)

    # Backyard Flower Bed on Right Grass
    box("Backyard_Flower_Bed", "Backyard", (4.8, -1.0, 0.30), (1.4, 0.6, 0.20), mat_fence)
    for fi, (fx, fy, f_mat) in enumerate([(-0.4, 0.0, mat_flower_pink), (0.0, 0.1, mat_flower_yellow), (0.4, -0.1, mat_flower_pink)]):
        sphere(f"Backyard_Bed_Flower_{fi}", "Backyard", (4.8 + fx, -1.0 + fy, 0.46), r=0.07, segs=8, rings=6, mat=f_mat)

    # Cozy Warm String Lights (Fairy Lights)
    # Strung between main shop corner and cottage roof
    start_wire = Vector((3.05, 0.0, 2.7))
    end_wire = Vector((4.6, -2.2, 2.5))
    num_bulbs = 10
    
    for bi in range(num_bulbs):
        frac = (bi + 0.5) / num_bulbs
        # Catenary dip
        dip = 0.32 * math.sin(frac * math.pi)
        pos = start_wire + (end_wire - start_wire) * frac
        pos.z -= dip
        # Little bulb sphere
        sphere(f"FairyBulb_{bi}", "Backyard", (pos.x, pos.y, pos.z), r=0.045, segs=8, rings=6, mat=mat_fairy_bulb)

    # Soft ambient point light along string
    if not bpy.data.objects.get("Light_StringLights"):
        str_lt_data = bpy.data.lights.new("Light_StringLights", 'POINT')
        str_lt_data.energy = 35.0
        str_lt_data.color = (1.0, 0.80, 0.42)
        str_lt_data.shadow_soft_size = 0.4
        str_lt_obj = bpy.data.objects.new("Light_StringLights", str_lt_data)
        str_lt_obj.location = (3.8, -1.1, 2.3)
        link_to(str_lt_obj, "Lighting")

    # =========================================================================
    # 5. FRONT OUTDOOR SEATING ("Front_Seating")
    # =========================================================================
    # 1 Round Café Table + 2 Facing Chairs
    # Position: on the front sidewalk, on the right side of entrance
    # Placed at X: 1.95, Y: 1.70, Z: 0.205 (open space between potted plant at 1.05 and streetlamp at 2.68)
    tab_x, tab_y, tab_z = 1.95, 1.70, 0.205

    # Round Café Table
    cyl("Cafe_Table_Top", "Front_Seating", (tab_x, tab_y, tab_z + 0.54), r=0.38, h=0.04, segs=18, mat=mat_table_top)
    cyl("Cafe_Table_Rim", "Front_Seating", (tab_x, tab_y, tab_z + 0.53), r=0.40, h=0.02, segs=18, mat=mat_chair_wood)
    cyl("Cafe_Table_Pedestal", "Front_Seating", (tab_x, tab_y, tab_z + 0.26), r=0.035, h=0.50, segs=8, mat=mat_fence)
    cyl("Cafe_Table_Base", "Front_Seating", (tab_x, tab_y, tab_z + 0.02), r=0.22, h=0.03, segs=12, mat=mat_fence)

    # 2 Facing Chairs (Chair 1 on Left facing +X, Chair 2 on Right facing -X)
    def make_cafe_chair(name_prefix, pos, rot_z):
        # 4 Wooden legs
        for lx, ly in [(-0.16, -0.16), (0.16, -0.16), (-0.16, 0.16), (0.16, 0.16)]:
            cyl(f"{name_prefix}_Leg_{lx}_{ly}", "Front_Seating", (pos.x + lx, pos.y + ly, pos.z + 0.20), r=0.025, h=0.40, segs=6, mat=mat_chair_wood)
        
        # Wooden seat frame
        box(f"{name_prefix}_SeatFrame", "Front_Seating", (pos.x, pos.y, pos.z + 0.40), (0.38, 0.38, 0.03), mat_chair_wood)
        # Soft padded cushion (Pastel Mint/Cyan #7ECBC0)
        box(f"{name_prefix}_Cushion", "Front_Seating", (pos.x, pos.y, pos.z + 0.435), (0.35, 0.35, 0.045), mat_chair_cushion)

        # Backrest uprights & horizontal slats (local -Y is back when unrotated)
        # We build backrest at local -X or -Y depending on orientation
        up1 = cyl(f"{name_prefix}_BackUp1", "Front_Seating", (pos.x - 0.15, pos.y - 0.15, pos.z + 0.62), r=0.02, h=0.44, segs=6, mat=mat_chair_wood)
        up2 = cyl(f"{name_prefix}_BackUp2", "Front_Seating", (pos.x + 0.15, pos.y - 0.15, pos.z + 0.62), r=0.02, h=0.44, segs=6, mat=mat_chair_wood)
        slat1 = box(f"{name_prefix}_BackSlat1", "Front_Seating", (pos.x, pos.y - 0.15, pos.z + 0.68), (0.32, 0.02, 0.05), mat_chair_wood)
        slat2 = box(f"{name_prefix}_BackSlat2", "Front_Seating", (pos.x, pos.y - 0.15, pos.z + 0.80), (0.34, 0.025, 0.06), mat_chair_wood)

    # Chair 1: At X = 1.45, facing table (+X direction)
    # Chair 2: At X = 2.45, facing table (-X direction)
    # Let's create chairs with proper local rotation:
    def make_oriented_chair(name, loc, rot_rad):
        # Create an empty parent or position parts rotated around loc
        for lx, ly in [(-0.16, -0.16), (0.16, -0.16), (-0.16, 0.16), (0.16, 0.16)]:
            rx = lx * math.cos(rot_rad) - ly * math.sin(rot_rad)
            ry = lx * math.sin(rot_rad) + ly * math.cos(rot_rad)
            cyl(f"{name}_Leg_{lx}_{ly}", "Front_Seating", (loc[0] + rx, loc[1] + ry, loc[2] + 0.20), r=0.025, h=0.40, segs=6, mat=mat_chair_wood)
        
        # Seat frame & cushion
        s_frame = box(f"{name}_SeatFrame", "Front_Seating", (loc[0], loc[1], loc[2] + 0.40), (0.38, 0.38, 0.03), mat_chair_wood)
        s_frame.rotation_euler = (0, 0, rot_rad)
        s_cush = box(f"{name}_Cushion", "Front_Seating", (loc[0], loc[1], loc[2] + 0.435), (0.35, 0.35, 0.045), mat_chair_cushion)
        s_cush.rotation_euler = (0, 0, rot_rad)

        # Backrest (at back of chair: local -Y)
        for bx_l in [-0.15, 0.15]:
            rx = bx_l * math.cos(rot_rad) - (-0.15) * math.sin(rot_rad)
            ry = bx_l * math.sin(rot_rad) + (-0.15) * math.cos(rot_rad)
            cyl(f"{name}_BackUp_{bx_l}", "Front_Seating", (loc[0] + rx, loc[1] + ry, loc[2] + 0.62), r=0.02, h=0.44, segs=6, mat=mat_chair_wood)

        for bz, bw in [(0.68, 0.05), (0.80, 0.06)]:
            rx = 0.0 * math.cos(rot_rad) - (-0.15) * math.sin(rot_rad)
            ry = 0.0 * math.sin(rot_rad) + (-0.15) * math.cos(rot_rad)
            slat = box(f"{name}_BackSlat_{bz}", "Front_Seating", (loc[0] + rx, loc[1] + ry, loc[2] + bz), (0.32, 0.025, bw), mat_chair_wood)
            slat.rotation_euler = (0, 0, rot_rad)

    # Chair 1 on left of table (faces +X, so back is at -X -> rot = -90 deg)
    make_oriented_chair("Cafe_Chair_Left", (1.46, tab_y, tab_z), math.radians(-90))
    # Chair 2 on right of table (faces -X, so back is at +X -> rot = +90 deg)
    make_oriented_chair("Cafe_Chair_Right", (2.44, tab_y, tab_z), math.radians(90))

    # Tableware (2 Coffee Cups with saucers + 1 Plate with cookie)
    # Cup 1
    cyl("Cafe_Saucer_1", "Front_Seating", (tab_x - 0.12, tab_y - 0.08, tab_z + 0.57), r=0.09, h=0.015, segs=12, mat=mat_cream)
    cyl("Cafe_Cup_1", "Front_Seating", (tab_x - 0.12, tab_y - 0.08, tab_z + 0.62), r=0.06, h=0.08, segs=12, mat=mat_pink)
    cyl("Cafe_Coffee_1", "Front_Seating", (tab_x - 0.12, tab_y - 0.08, tab_z + 0.65), r=0.05, h=0.015, segs=8, mat=mat_choc)

    # Cup 2
    cyl("Cafe_Saucer_2", "Front_Seating", (tab_x + 0.12, tab_y + 0.08, tab_z + 0.57), r=0.09, h=0.015, segs=12, mat=mat_cream)
    cyl("Cafe_Cup_2", "Front_Seating", (tab_x + 0.12, tab_y + 0.08, tab_z + 0.62), r=0.06, h=0.08, segs=12, mat=mat_cream)
    cyl("Cafe_Coffee_2", "Front_Seating", (tab_x + 0.12, tab_y + 0.08, tab_z + 0.65), r=0.05, h=0.015, segs=8, mat=mat_choc)

    # Cookie Plate in Center
    cyl("Cafe_Plate", "Front_Seating", (tab_x + 0.04, tab_y - 0.06, tab_z + 0.57), r=0.12, h=0.015, segs=14, mat=mat_cream)
    cyl("Cafe_Cookie", "Front_Seating", (tab_x + 0.04, tab_y - 0.06, tab_z + 0.59), r=0.065, h=0.018, segs=10, mat=mat_cookie)
    cyl("Cafe_Chip1", "Front_Seating", (tab_x + 0.02, tab_y - 0.05, tab_z + 0.602), r=0.02, h=0.01, segs=5, mat=mat_choc)
    cyl("Cafe_Chip2", "Front_Seating", (tab_x + 0.06, tab_y - 0.07, tab_z + 0.602), r=0.016, h=0.01, segs=5, mat=mat_choc)

    print("Night atmosphere & scene expansion completed successfully!")
    return "Night atmosphere & expansion applied."

apply_night_expansion()
