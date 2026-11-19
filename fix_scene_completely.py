"""
fix_scene_completely.py
1. Fixes door parts world transforms so door is physically 25° open inward at ground level Z=1.30.
2. Removes old exterior Counter_Left/Right that obstructed the interior floor.
3. Adds warm key/fill light above baker & counter so character and interior glow warmly.
4. Positions Camera_Interior at (-0.85, -0.75, 1.40) looking at baker, display case, POS, and background.
5. Renders cookie_shop_interior_render.png and cookie_shop_night_render.png.
6. Saves cookie_shop_animated_interior.blend.
"""

import bpy
import math
from mathutils import Vector, Euler

def fix_all():
    scene = bpy.context.scene

    # 1. Door Hinge Swing: 25° open inward at ground level
    # Pivot at hinge: (-0.58, 0.04)
    # At 25° open inward (-Y):
    # X = -0.58 + 0.58*cos(-25°) = -0.055
    # Y = 0.04 + 0.58*sin(-25°) = -0.205
    door_transforms = {
        "Door_Slab": ((-0.055, -0.205, 1.30), Euler((0, 0, math.radians(-25)))),
        "Door_Glass_Pane": ((-0.055, -0.165, 1.70), Euler((0, 0, math.radians(-25)))),
        "Door_Lower_Panel": ((-0.055, -0.155, 0.65), Euler((0, 0, math.radians(-25)))),
        "Door_Brass_Kickplate": ((-0.055, -0.155, 0.26), Euler((0, 0, math.radians(-25)))),
        "Door_Brass_Handle": ((0.375, -0.405, 1.25), Euler((math.radians(90), 0, math.radians(-25)))),
        "Door_Open_Sign_Board": ((-0.055, -0.145, 1.62), Euler((0, 0, math.radians(-25)))),
        "Door_Open_Sign_Inner": ((-0.055, -0.132, 1.62), Euler((0, 0, math.radians(-25)))),
        "Text_Open": ((-0.055, -0.120, 1.57), Euler((math.radians(90), 0, math.radians(155)))),
    }

    for name, (loc, rot) in door_transforms.items():
        obj = bpy.data.objects.get(name)
        if obj:
            obj.parent = None
            obj.location = Vector(loc)
            obj.rotation_euler = rot
            obj.scale = (1, 1, 1)

    print("Door parts placed at exact open positions!")

    # 2. Remove old exterior Counter_Left/Right if present
    for side in ["Left", "Right"]:
        for cname in [f"Counter_{side}", f"Counter_Top_{side}"]:
            old_c = bpy.data.objects.get(cname)
            if old_c:
                bpy.data.objects.remove(old_c, do_unlink=True)

    # 3. Add warm key/fill light above baker & counter
    baker_light_data = bpy.data.lights.get("Data_Baker_KeyLight")
    if not baker_light_data:
        baker_light_data = bpy.data.lights.new("Data_Baker_KeyLight", 'POINT')
    baker_light_data.energy = 40.0
    baker_light_data.color = (1.0, 0.85, 0.60) # Warm golden
    baker_light_data.shadow_soft_size = 0.5

    baker_light_obj = bpy.data.objects.get("Light_Baker_Key")
    if not baker_light_obj:
        baker_light_obj = bpy.data.objects.new("Light_Baker_Key", baker_light_data)
        col = bpy.data.collections.get("Cookie Shop")
        if col:
            col.objects.link(baker_light_obj)
        else:
            scene.collection.objects.link(baker_light_obj)
    baker_light_obj.location = (-0.35, -1.55, 2.20)

    # 4. Baker Character Pose at frame 150
    root = bpy.data.objects.get("Baker_Root")
    if root:
        root.location = (-0.35, -1.85, 0.20)
        # Face toward front counter and camera (Z-rotation = 0 to 15 deg)
        root.rotation_euler = (0, 0, math.radians(15))
        root.keyframe_insert("location", frame=150)
        root.keyframe_insert("rotation_euler", frame=150)

    head = bpy.data.objects.get("Baker_Head")
    if head:
        head.rotation_euler = (math.radians(-5), 0, math.radians(-10))
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

    # 5. Position Camera_Interior: Eye-level (Z=1.40m), 22mm wide-angle
    # Customer-eye view looking across the counter at the smiling waving baker,
    # the illuminated glass pastry case, POS station, glowing oven, and chalkboard menu!
    cam_int = bpy.data.objects.get("Camera_Interior")
    if cam_int:
        cam_int.data.lens = 22.0
        cam_int.location = (-0.85, -0.75, 1.40)
        target = Vector((0.10, -1.90, 1.15))
        direction = target - cam_int.location
        rot_quat = direction.to_track_quat('-Z', 'Y')
        cam_int.rotation_euler = rot_quat.to_euler()

    # Re-save blend file
    blend_path = r"C:\Users\PT.CTI\Documents\Tofan\Practice\3d blender\cookie_shop_animated_interior.blend"
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print("Saved updated blend file!")

    # 6. Render View 1: cookie_shop_interior_render.png
    scene.camera = cam_int
    scene.frame_set(150)
    int_path = r"C:\Users\PT.CTI\Documents\Tofan\Practice\3d blender\cookie_shop_interior_render.png"
    scene.render.filepath = int_path
    print(f"Rendering interior to {int_path}...")
    bpy.ops.render.render(write_still=True)
    print("Interior render finished!")

    # 7. Render View 2: cookie_shop_night_render.png
    store_cam = bpy.data.objects.get("Storefront_Camera")
    if store_cam:
        scene.camera = store_cam
        scene.frame_set(150)
        ext_path = r"C:\Users\PT.CTI\Documents\Tofan\Practice\3d blender\cookie_shop_night_render.png"
        scene.render.filepath = ext_path
        print(f"Rendering storefront night view to {ext_path}...")
        bpy.ops.render.render(write_still=True)
        print("Storefront night render finished!")

if __name__ == "__main__":
    fix_all()
