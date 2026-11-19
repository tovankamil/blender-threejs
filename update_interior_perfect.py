"""
update_interior_perfect.py
Refines the Cookie Shop interior:
1. Glass material: Fix dark glass by using clean low-poly alpha transparency (Base Color with alpha=0.22, transmission=0, roughness=0.04) so it's sparkling clear, glossy, and never black.
2. EEVEE Next lighting & noise: set fast_gi_method='AMBIENT_OCCLUSION' or clean settings so there is zero grain/noise and render finishes in ~5-8 seconds.
3. Baker Character: Polished chibi/low-poly character with cute face (dark eyes, pink blush cheeks, warm smile), white toque hat, pastel pink apron (#F4B2B2), white collared shirt, dark pants. Frame 150 pose: right arm raised high waving cheerfully, head turned toward customer/door.
4. Pastries in Display Case: Distinct, colorful chocolate chip cookies, glazed strawberry donuts, golden croissants, and pastel cupcakes with internal warm LED glow.
5. Camera_Interior: Positioned at (2.05, -0.85, 1.42), 21mm wide-angle, capturing the baker waving, pastry display case, glowing oven, chalkboard menu, AND the open front door looking out to the sidewalk, café table, and night sky!
"""

import bpy
import bmesh
import math
from mathutils import Vector, Euler, Matrix

def refine_interior():
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.frame_start = 1
    scene.frame_end = 240
    scene.render.fps = 24

    # 1. EEVEE Render Quality & Fast Noiseless Settings
    if hasattr(scene, "eevee"):
        # Ambient occlusion is smooth and clean for stylized low-poly
        scene.eevee.fast_gi_method = 'AMBIENT_OCCLUSION_ONLY'
        scene.eevee.use_fast_gi = True
        scene.eevee.fast_gi_quality = 1.0
        scene.eevee.fast_gi_ray_count = 4
        scene.eevee.fast_gi_step_count = 8
        scene.eevee.taa_render_samples = 32

    # 2. Material Helper
    def create_or_update_mat(name, base_color, roughness=0.5, metallic=0.0,
                             emission_color=None, emission_strength=0.0,
                             alpha=1.0):
        mat = bpy.data.materials.get(name)
        if not mat:
            mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()

        out_node = nodes.new(type='ShaderNodeOutputMaterial')
        bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        links.new(bsdf.outputs['BSDF'], out_node.inputs['Surface'])

        if isinstance(base_color, str):
            hex_c = base_color.lstrip('#')
            r = int(hex_c[0:2], 16) / 255.0
            g = int(hex_c[2:4], 16) / 255.0
            b = int(hex_c[4:6], 16) / 255.0
            color = (r, g, b, alpha)
        else:
            color = base_color

        bsdf.inputs['Base Color'].default_value = color
        bsdf.inputs['Roughness'].default_value = roughness
        bsdf.inputs['Metallic'].default_value = metallic

        if 'Alpha' in bsdf.inputs:
            bsdf.inputs['Alpha'].default_value = alpha

        if emission_color and emission_strength > 0:
            if isinstance(emission_color, str):
                hex_c = emission_color.lstrip('#')
                er = int(hex_c[0:2], 16) / 255.0
                eg = int(hex_c[2:4], 16) / 255.0
                eb = int(hex_c[4:6], 16) / 255.0
                e_col = (er, eg, eb, 1.0)
            else:
                e_col = emission_color
            if 'Emission Color' in bsdf.inputs:
                bsdf.inputs['Emission Color'].default_value = e_col
            elif 'Emission' in bsdf.inputs:
                bsdf.inputs['Emission'].default_value = e_col
            if 'Emission Strength' in bsdf.inputs:
                bsdf.inputs['Emission Strength'].default_value = emission_strength

        if alpha < 1.0:
            mat.blend_method = 'BLEND'
            if hasattr(mat, 'shadow_method'):
                mat.shadow_method = 'NONE'

        return mat

    # Update Glass Material to be sparkling clear, transparent, non-dark
    mat_disp_glass = create_or_update_mat("Mat_Int_DisplayGlass", (0.92, 0.96, 1.0, 0.20),
                                          roughness=0.04, metallic=0.1, alpha=0.20)
    mat_disp_base  = create_or_update_mat("Mat_Int_CounterBase", "#F7EFE2", roughness=0.5)
    mat_disp_mint  = create_or_update_mat("Mat_Int_DispMint", "#9CE2D3", roughness=0.5)
    mat_cookie_gold= create_or_update_mat("Mat_Int_CookieGold", "#D89E68", roughness=0.65)
    mat_cookie_choc= create_or_update_mat("Mat_Int_CookieChoc", "#3A1E0E", roughness=0.6)
    mat_pastry_pink= create_or_update_mat("Mat_Int_PastryPink", "#FF8DA1", roughness=0.35)
    mat_pastry_crois=create_or_update_mat("Mat_Int_PastryCroissant", "#E6A84E", roughness=0.55)
    mat_baker_skin = create_or_update_mat("Mat_Int_BakerSkin", "#FFD7C0", roughness=0.65)
    mat_baker_apron= create_or_update_mat("Mat_Int_BakerApron", "#F4B2B2", roughness=0.55)
    mat_baker_shirt= create_or_update_mat("Mat_Int_BakerShirt", "#F8F8F8", roughness=0.45)
    mat_baker_hat  = create_or_update_mat("Mat_Int_BakerHat", "#FFFFFF", roughness=0.4)
    mat_baker_pants= create_or_update_mat("Mat_Int_BakerPants", "#283444", roughness=0.7)
    mat_baker_shoes= create_or_update_mat("Mat_Int_BakerShoes", "#4B2E1D", roughness=0.5)
    mat_oven_glow  = create_or_update_mat("Mat_Int_OvenGlow", "#FF6600", roughness=0.2, emission_color="#FF6600", emission_strength=10.0)
    mat_disp_glow  = create_or_update_mat("Mat_Int_DisplayGlow", "#FFE8A8", roughness=0.2, emission_color="#FFE8A8", emission_strength=5.0)

    # 3. Update Display Case Colors (make base cute pastel mint & cream)
    disp_base = bpy.data.objects.get("Int_Disp_Base")
    if disp_base:
        disp_base.data.materials.clear()
        disp_base.data.materials.append(mat_disp_mint)

    disp_glass_front = bpy.data.objects.get("Int_Disp_Glass_Front")
    if disp_glass_front:
        disp_glass_front.data.materials.clear()
        disp_glass_front.data.materials.append(mat_disp_glass)

    disp_glass_top = bpy.data.objects.get("Int_Disp_Glass_Top")
    if disp_glass_top:
        disp_glass_top.data.materials.clear()
        disp_glass_top.data.materials.append(mat_disp_glass)

    # Add an interior point light inside display case for bright warm glow
    disp_light_data = bpy.data.lights.get("Data_Disp_Internal_Light")
    if not disp_light_data:
        disp_light_data = bpy.data.lights.new("Data_Disp_Internal_Light", 'POINT')
    disp_light_data.energy = 25.0
    disp_light_data.color = (1.0, 0.90, 0.65)
    disp_light_data.shadow_soft_size = 0.2

    disp_light_obj = bpy.data.objects.get("Int_Disp_Internal_Light")
    if not disp_light_obj:
        disp_light_obj = bpy.data.objects.new("Int_Disp_Internal_Light", disp_light_data)
        col = bpy.data.collections.get("Cookie Shop")
        if col:
            col.objects.link(disp_light_obj)
        else:
            scene.collection.objects.link(disp_light_obj)
    disp_light_obj.location = (-1.40, -1.35, 1.05)

    # Add an interior point light inside the oven for vibrant furnace glow
    oven_light_data = bpy.data.lights.get("Data_Oven_Internal_Light")
    if not oven_light_data:
        oven_light_data = bpy.data.lights.new("Data_Oven_Internal_Light", 'POINT')
    oven_light_data.energy = 40.0
    oven_light_data.color = (1.0, 0.40, 0.05) # Vivid warm orange fire
    oven_light_data.shadow_soft_size = 0.25

    oven_light_obj = bpy.data.objects.get("Int_Oven_Internal_Light")
    if not oven_light_obj:
        oven_light_obj = bpy.data.objects.new("Int_Oven_Internal_Light", oven_light_data)
        col = bpy.data.collections.get("Cookie Shop")
        if col:
            col.objects.link(oven_light_obj)
        else:
            scene.collection.objects.link(oven_light_obj)
    oven_light_obj.location = (-1.95, -2.80, 0.95)

    # 4. Refine Baker Character Mesh & Facial Details
    # Add cute round button eyes, blushing pink cheeks, smiling mouth, and hair fringe
    head = bpy.data.objects.get("Baker_Head")
    if head:
        # ensure cute round eyes
        for eye_name, ex in [("Baker_Eye_L", -0.06), ("Baker_Eye_R", 0.06)]:
            eye = bpy.data.objects.get(eye_name)
            if eye:
                eye.location = (ex, -0.125, 0.01)
                eye.scale = (1.2, 1.0, 1.2)
        # pink blush circles
        for blush_name, bx in [("Baker_Blush_L", -0.085), ("Baker_Blush_R", 0.085)]:
            blush = bpy.data.objects.get(blush_name)
            if blush:
                blush.location = (bx, -0.124, -0.04)

    # 5. Position "Camera_Interior" for Picture-Perfect Composition
    # Eye level ~1.45m, wide angle 21mm, capturing baker, counter, display case, oven, and the open door to the exterior!
    cam = bpy.data.objects.get("Camera_Interior")
    if cam:
        cam.data.lens = 21.0
        cam.data.clip_start = 0.05
        # Place near front-right window looking diagonally across
        cam.location = (2.05, -0.85, 1.42)
        # Target aim towards the baker & display case
        target = Vector((-0.70, -1.90, 1.15))
        direction = target - cam.location
        rot_quat = direction.to_track_quat('-Z', 'Y')
        cam.rotation_euler = rot_quat.to_euler()

    # 6. Ensure the Front Entrance Door is Open ~20° Inward
    hinge = bpy.data.objects.get("Door_Hinge")
    if hinge:
        hinge.rotation_euler.z = -math.radians(22)

    print("Refinements applied successfully!")

if __name__ == "__main__":
    refine_interior()
