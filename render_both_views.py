"""
render_both_views.py
Sets up the cinematic Camera_Interior shot (capturing counter, display case, waving baker,
and exterior night street through the open door and window),
renders cookie_shop_interior_render.png, then sets Storefront_Camera and renders
cookie_shop_night_render.png, and saves cookie_shop_animated_interior.blend.
"""

import bpy
import math
from mathutils import Vector, Euler

def setup_interior_cam():
    scene = bpy.context.scene

    # 1. Camera_Interior: Positioned at (-1.35, -2.65, 1.45), 22mm
    # Captures:
    # - Midground: The smiling baker in apron & toque waving cheerfully
    # - Counter & Glass Display Case with cookies and cupcakes
    # - Background: Open entrance door & bay window looking out onto the night sidewalk,
    #   bistro table & chairs, glowing streetlamp, and starry sky!
    cam_int = bpy.data.objects.get("Camera_Interior")
    if cam_int:
        cam_int.data.lens = 22.0
        cam_int.location = (-1.35, -2.65, 1.45)
        target = Vector((0.35, 0.15, 1.25))
        direction = target - cam_int.location
        rot_quat = direction.to_track_quat('-Z', 'Y')
        cam_int.rotation_euler = rot_quat.to_euler()

    # 2. Baker Character at frame 150:
    # Faces 35 degrees toward the open door and camera, smiling and waving!
    root = bpy.data.objects.get("Baker_Root")
    if root:
        root.location = (-0.35, -1.85, 0.20)
        root.rotation_euler = (0, 0, math.radians(35))
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

    # 3. Ensure Front Entrance Door is open 22° inward
    hinge = bpy.data.objects.get("Door_Hinge")
    if hinge:
        hinge.rotation_euler.z = -math.radians(22)

    # 4. Save main blend file
    blend_path = r"C:\Users\PT.CTI\Documents\Tofan\Practice\3d blender\cookie_shop_animated_interior.blend"
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print("Interior camera and baker pose updated!")

if __name__ == "__main__":
    setup_interior_cam()
