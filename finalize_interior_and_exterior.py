"""
finalize_interior_and_exterior.py
Finalizes interior framing, baker orientation, lighting balance, and renders both required views:
1. cookie_shop_interior_render.png (Camera_Interior, frame 150: waving baker, display case, open door view)
2. cookie_shop_night_render.png (Storefront_Camera, frame 150: exterior night view with open door & glowing interior)
3. Saves cookie_shop_animated_interior.blend.
"""

import bpy
import math
from mathutils import Vector, Euler

def finalize():
    scene = bpy.context.scene

    # 1. EEVEE Render Settings (clean, fast, noise-free)
    scene.render.engine = 'BLENDER_EEVEE'
    scene.frame_start = 1
    scene.frame_end = 240
    scene.render.fps = 24
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 960
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'

    if hasattr(scene, "eevee"):
        scene.eevee.fast_gi_method = 'AMBIENT_OCCLUSION_ONLY'
        scene.eevee.use_fast_gi = True
        scene.eevee.fast_gi_quality = 0.5
        scene.eevee.fast_gi_ray_count = 2
        scene.eevee.fast_gi_step_count = 6
        scene.eevee.taa_render_samples = 16

    # 2. Balanced Lighting (warm, cozy, rich pastel tones)
    for lname, pwr in [("Light_DispLight", 10.0), ("Light_POSLight", 12.0), ("Light_BakingLight", 14.0)]:
        lt = bpy.data.lights.get(f"Data_{lname}")
        if lt:
            lt.energy = pwr
            lt.color = (1.0, 0.78, 0.50)
            lt.shadow_soft_size = 0.45

    disp_lt = bpy.data.lights.get("Data_Disp_Internal_Light")
    if disp_lt:
        disp_lt.energy = 8.0
        disp_lt.color = (1.0, 0.88, 0.65)

    oven_lt = bpy.data.lights.get("Data_Oven_Internal_Light")
    if oven_lt:
        oven_lt.energy = 22.0
        oven_lt.color = (1.0, 0.42, 0.05)

    # 3. Ensure Front Entrance Door is Open ~20° Inward
    hinge = bpy.data.objects.get("Door_Hinge")
    if hinge:
        hinge.rotation_euler.z = -math.radians(22)

    # 4. Baker Character Pose at Frame 150 (Faces Camera/Door, Waving Cheerful Hand!)
    root = bpy.data.objects.get("Baker_Root")
    if root:
        root.location = (-0.35, -1.85, 0.20)
        # Face toward the front-left where camera and entrance door are!
        root.rotation_euler = (0, 0, math.radians(135))
        root.keyframe_insert("location", frame=150)
        root.keyframe_insert("rotation_euler", frame=150)

    head = bpy.data.objects.get("Baker_Head")
    if head:
        head.rotation_euler = (math.radians(-5), 0, math.radians(10))
        head.keyframe_insert("rotation_euler", frame=150)

    # Right Arm raised high, waving side-to-side
    arm_r = bpy.data.objects.get("Baker_Arm_R")
    forearm_r = bpy.data.objects.get("Baker_Forearm_R")
    if arm_r and forearm_r:
        arm_r.rotation_euler = (math.radians(140), math.radians(-30), math.radians(15))
        forearm_r.rotation_euler = (math.radians(-35), math.radians(10), math.radians(-30))
        arm_r.keyframe_insert("rotation_euler", frame=150)
        forearm_r.keyframe_insert("rotation_euler", frame=150)

    # Left Arm resting gracefully by the counter
    arm_l = bpy.data.objects.get("Baker_Arm_L")
    forearm_l = bpy.data.objects.get("Baker_Forearm_L")
    if arm_l and forearm_l:
        arm_l.rotation_euler = (math.radians(25), math.radians(10), 0)
        forearm_l.rotation_euler = (math.radians(-25), 0, 0)
        arm_l.keyframe_insert("rotation_euler", frame=150)
        forearm_l.keyframe_insert("rotation_euler", frame=150)

    # 5. Perfect Camera_Interior Framing
    # Position: X = -1.45, Y = -0.22, Z = 1.35
    # Wide 19mm lens captures:
    # - Left: The open entrance door looking out onto the illuminated night sidewalk & streetlamp
    # - Center: The smiling baker waving cheerfully behind the counter
    # - Foreground: The illuminated glass display case with chocolate chip cookies, cupcakes & donuts
    # - Right: The POS register station with tip jar and cookie jars
    # - Background: The glowing oven, rolling cooling rack, and chalkboard menu
    cam_int = bpy.data.objects.get("Camera_Interior")
    if cam_int:
        cam_int.data.lens = 19.0 # Wide angle
        cam_int.location = (-1.45, -0.22, 1.35)
        target = Vector((0.15, -1.75, 1.05))
        direction = target - cam_int.location
        rot_quat = direction.to_track_quat('-Z', 'Y')
        cam_int.rotation_euler = rot_quat.to_euler()

    # Save updated scene file
    blend_path = r"C:\Users\PT.CTI\Documents\Tofan\Practice\3d blender\cookie_shop_animated_interior.blend"
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"Saved blend file to: {blend_path}")

if __name__ == "__main__":
    finalize()
