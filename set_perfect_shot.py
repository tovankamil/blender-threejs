"""
set_perfect_shot.py
Refines camera angles, lighting balance, and character pose.
"""

import bpy
import math
from mathutils import Vector, Euler

def setup():
    scene = bpy.context.scene

    # 1. Balanced Cozy Lighting (Prevent Overexposure, keep rich pastel tones)
    for lname in ["Light_DispLight", "Light_POSLight", "Light_BakingLight"]:
        lt = bpy.data.lights.get(f"Data_{lname}")
        if lt:
            lt.energy = 16.0
            lt.color = (1.0, 0.76, 0.48)
            lt.shadow_soft_size = 0.4

    disp_lt = bpy.data.lights.get("Data_Disp_Internal_Light")
    if disp_lt:
        disp_lt.energy = 12.0
        disp_lt.color = (1.0, 0.88, 0.60)

    oven_lt = bpy.data.lights.get("Data_Oven_Internal_Light")
    if oven_lt:
        oven_lt.energy = 25.0
        oven_lt.color = (1.0, 0.40, 0.05)

    # Fast clean EEVEE render settings
    if hasattr(scene, "eevee"):
        scene.eevee.fast_gi_method = 'AMBIENT_OCCLUSION_ONLY'
        scene.eevee.use_fast_gi = True
        scene.eevee.fast_gi_quality = 0.5
        scene.eevee.fast_gi_ray_count = 2
        scene.eevee.fast_gi_step_count = 6
        scene.eevee.taa_render_samples = 16

    scene.render.resolution_x = 1280
    scene.render.resolution_y = 960

    # 2. Camera_Interior Setup
    # Position: on the left side of the front customer area, looking across at the baker,
    # the counter, and framing the open front door looking out to the sidewalk!
    cam = bpy.data.objects.get("Camera_Interior")
    if cam:
        cam.data.lens = 22.0
        # Position at X = -1.75, Y = -0.55, Z = 1.35
        cam.location = (-1.75, -0.55, 1.35)
        # Aim toward baker & POS counter
        target = Vector((0.05, -1.85, 1.10))
        direction = target - cam.location
        rot_quat = direction.to_track_quat('-Z', 'Y')
        cam.rotation_euler = rot_quat.to_euler()

    # 3. Ensure Front Door is open ~20 degrees inward
    hinge = bpy.data.objects.get("Door_Hinge")
    if hinge:
        hinge.rotation_euler.z = -math.radians(22)

    # 4. Refine Baker Pose at Frame 150
    root = bpy.data.objects.get("Baker_Root")
    if root:
        root.location = (-0.35, -1.85, 0.20)
        root.rotation_euler = (0, 0, math.radians(-30)) # Turned 30 degrees toward front door & camera!
        root.keyframe_insert("location", frame=150)
        root.keyframe_insert("rotation_euler", frame=150)

    head = bpy.data.objects.get("Baker_Head")
    if head:
        head.rotation_euler = (math.radians(5), 0, math.radians(-10))
        head.keyframe_insert("rotation_euler", frame=150)

    arm_r = bpy.data.objects.get("Baker_Arm_R")
    forearm_r = bpy.data.objects.get("Baker_Forearm_R")
    if arm_r and forearm_r:
        arm_r.rotation_euler = (math.radians(135), math.radians(-25), 0)
        forearm_r.rotation_euler = (math.radians(-35), 0, math.radians(-30))
        arm_r.keyframe_insert("rotation_euler", frame=150)
        forearm_r.keyframe_insert("rotation_euler", frame=150)

    arm_l = bpy.data.objects.get("Baker_Arm_L")
    forearm_l = bpy.data.objects.get("Baker_Forearm_L")
    if arm_l and forearm_l:
        arm_l.rotation_euler = (math.radians(15), 0, math.radians(10))
        forearm_l.rotation_euler = (math.radians(-20), 0, 0)
        arm_l.keyframe_insert("rotation_euler", frame=150)
        forearm_l.keyframe_insert("rotation_euler", frame=150)

    print("Setup completed successfully!")

if __name__ == "__main__":
    setup()
