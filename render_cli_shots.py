"""
render_cli_shots.py
Runs via Blender CLI to:
1. Finalize Camera_Interior framing & lighting
2. Render cookie_shop_interior_render.png (frame 150)
3. Render cookie_shop_night_render.png (Storefront_Camera, frame 150)
4. Save cookie_shop_animated_interior.blend
"""

import bpy
import math
from mathutils import Vector, Euler

def main():
    scene = bpy.context.scene

    # 1. EEVEE Next Render Settings
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

    # 2. Lighting Balance
    for lname, pwr in [("Light_DispLight", 14.0), ("Light_POSLight", 16.0), ("Light_BakingLight", 16.0)]:
        lt = bpy.data.lights.get(f"Data_{lname}")
        if lt:
            lt.energy = pwr
            lt.color = (1.0, 0.80, 0.52)
            lt.shadow_soft_size = 0.45

    disp_lt = bpy.data.lights.get("Data_Disp_Internal_Light")
    if disp_lt:
        disp_lt.energy = 10.0
        disp_lt.color = (1.0, 0.88, 0.65)

    oven_lt = bpy.data.lights.get("Data_Oven_Internal_Light")
    if oven_lt:
        oven_lt.energy = 25.0
        oven_lt.color = (1.0, 0.42, 0.05)

    # 3. Ensure Front Entrance Door is Open ~22° Inward
    hinge = bpy.data.objects.get("Door_Hinge")
    if hinge:
        hinge.rotation_euler.z = -math.radians(22)

    # 4. Baker Character Pose at Frame 150:
    # Waving right arm cheerfully, friendly smiling expression!
    root = bpy.data.objects.get("Baker_Root")
    if root:
        root.location = (-0.35, -1.85, 0.20)
        # Angle toward door and camera
        root.rotation_euler = (0, 0, math.radians(45))
        root.keyframe_insert("location", frame=150)
        root.keyframe_insert("rotation_euler", frame=150)

    head = bpy.data.objects.get("Baker_Head")
    if head:
        head.rotation_euler = (math.radians(-5), 0, math.radians(-15))
        head.keyframe_insert("rotation_euler", frame=150)

    arm_r = bpy.data.objects.get("Baker_Arm_R")
    forearm_r = bpy.data.objects.get("Baker_Forearm_R")
    if arm_r and forearm_r:
        arm_r.rotation_euler = (math.radians(135), math.radians(-25), 0)
        forearm_r.rotation_euler = (math.radians(-40), 0, math.radians(-35))
        arm_r.keyframe_insert("rotation_euler", frame=150)
        forearm_r.keyframe_insert("rotation_euler", frame=150)

    arm_l = bpy.data.objects.get("Baker_Arm_L")
    forearm_l = bpy.data.objects.get("Baker_Forearm_L")
    if arm_l and forearm_l:
        arm_l.rotation_euler = (math.radians(20), 0, math.radians(10))
        forearm_l.rotation_euler = (math.radians(-25), 0, 0)
        arm_l.keyframe_insert("rotation_euler", frame=150)
        forearm_l.keyframe_insert("rotation_euler", frame=150)

    # 5. Position Camera_Interior
    # Position: inside the bakery at X = 1.70, Y = -2.75, Z = 1.45
    # Wide 22mm lens aimed across the counter, baker, and through the open front door:
    cam_int = bpy.data.objects.get("Camera_Interior")
    if cam_int:
        cam_int.data.lens = 22.0
        cam_int.location = (1.70, -2.75, 1.45)
        target = Vector((-0.30, -0.70, 1.15))
        direction = target - cam_int.location
        rot_quat = direction.to_track_quat('-Z', 'Y')
        cam_int.rotation_euler = rot_quat.to_euler()

    # Save blend file
    blend_path = r"C:\Users\PT.CTI\Documents\Tofan\Practice\3d blender\cookie_shop_animated_interior.blend"
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print("Saved blend file successfully!")

    # 6. Render View 1: cookie_shop_interior_render.png
    scene.camera = cam_int
    scene.frame_set(150)
    int_render_path = r"C:\Users\PT.CTI\Documents\Tofan\Practice\3d blender\cookie_shop_interior_render.png"
    scene.render.filepath = int_render_path
    print(f"Rendering Interior View to {int_render_path}...")
    bpy.ops.render.render(write_still=True)
    print("Interior render finished!")

    # 7. Render View 2: cookie_shop_night_render.png
    store_cam = bpy.data.objects.get("Storefront_Camera")
    if store_cam:
        scene.camera = store_cam
        scene.frame_set(150)
        ext_render_path = r"C:\Users\PT.CTI\Documents\Tofan\Practice\3d blender\cookie_shop_night_render.png"
        scene.render.filepath = ext_render_path
        print(f"Rendering Storefront Night View to {ext_render_path}...")
        bpy.ops.render.render(write_still=True)
        print("Storefront render finished!")

if __name__ == "__main__":
    main()
