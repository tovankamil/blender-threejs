"""
fix_doors_walls_cameras.py
1. Properly swings front door open 25 degrees inward around hinge pivot (-0.58, 0.04, 0).
2. Replaces solid/blocked front of Floor1_Walls with proper architectural framing
   (leaving doorway [-0.60, 0.60] and bay windows [-2.75, -0.95] and [0.95, 2.75] completely open!).
3. Positions Camera_Interior at eye level (~1.45m), 22mm, capturing the counter, pastry display case,
   animated baker waving, AND the exterior night view through the open door and window!
4. Renders cookie_shop_interior_render.png and cookie_shop_night_render.png.
5. Saves cookie_shop_animated_interior.blend.
"""

import bpy
import bmesh
import math
from mathutils import Vector, Euler, Matrix

def run_fix():
    scene = bpy.context.scene

    # -------------------------------------------------------------------------
    # 1. Door Hinge Swing: 25 degrees inward
    # -------------------------------------------------------------------------
    # Original unrotated positions of door parts (from create_stylized_cookie_shop.py):
    door_defaults = {
        "Door_Slab": ((0.0, 0.04, 1.30), Euler((0, 0, 0))),
        "Door_Glass_Pane": ((0.0, 0.08, 1.70), Euler((0, 0, 0))),
        "Door_Lower_Panel": ((0.0, 0.09, 0.65), Euler((0, 0, 0))),
        "Door_Mullion_H": ((0.0, 0.10, 1.70), Euler((0, 0, 0))),
        "Door_Mullion_V": ((0.0, 0.10, 1.70), Euler((0, 0, 0))),
        "Door_Brass_Handle": ((0.45, 0.13, 1.25), Euler((math.radians(90), 0, 0))),
        "Door_Brass_Kickplate": ((0.0, 0.09, 0.26), Euler((0, 0, 0))),
        "Door_Open_Sign_Board": ((0.0, 0.105, 1.62), Euler((0, 0, 0))),
        "Door_Open_Sign_Inner": ((0.0, 0.118, 1.62), Euler((0, 0, 0))),
        "Text_Open": ((0.0, 0.13, 1.57), Euler((math.radians(90), 0, math.radians(180)))),
    }

    # Hinge is at left edge of door: (-0.58, 0.04)
    pivot = Vector((-0.58, 0.04, 0.0))
    angle = math.radians(-25) # swing inward into shop (-Y)

    # Translation to origin, rotation, translation back
    T1 = Matrix.Translation(-pivot)
    R = Matrix.Rotation(angle, 4, 'Z')
    T2 = Matrix.Translation(pivot)
    M_swing = T2 @ R @ T1

    for name, (loc, rot) in door_defaults.items():
        obj = bpy.data.objects.get(name)
        if obj:
            obj.parent = None
            obj.location = Vector(loc)
            obj.rotation_euler = rot
            obj.scale = (1, 1, 1)
            # Apply hinge swing transform
            obj.matrix_world = M_swing @ obj.matrix_world

    print("Door swung 25 degrees open inward cleanly!")

    # -------------------------------------------------------------------------
    # 2. Re-architect Floor1_Walls so Doorway and Windows are completely open!
    # -------------------------------------------------------------------------
    mat_mint = bpy.data.materials.get("Mat_Mint")
    if not mat_mint:
        mat_mint = bpy.data.materials.get("Mat_Int_MintPanel")

    walls = bpy.data.objects.get("Floor1_Walls")
    if walls:
        bpy.data.objects.remove(walls, do_unlink=True)

    # Build clean hollow first-floor exterior shell with real openings
    # Back Wall: X in [-3.0, 3.0], Y = -3.35, Z in [0.35, 3.05]
    def make_wall_box(name, loc, size):
        mesh = bpy.data.meshes.new(name + "_Mesh")
        obj = bpy.data.objects.new(name, mesh)
        col = bpy.data.collections.get("Building")
        if col:
            col.objects.link(obj)
        else:
            scene.collection.objects.link(obj)

        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        for v in bm.verts:
            v.co.x *= size[0]
            v.co.y *= size[1]
            v.co.z *= size[2]
        bm.to_mesh(mesh)
        bm.free()
        obj.location = loc
        if mat_mint:
            obj.data.materials.append(mat_mint)
        return obj

    # Exterior Back Wall
    make_wall_box("F1_Wall_Back", (0.0, -3.35, 1.70), (6.00, 0.10, 2.70))
    # Exterior Left Wall
    make_wall_box("F1_Wall_Left", (-2.95, -1.70, 1.70), (0.10, 3.20, 2.70))
    # Exterior Right Wall
    make_wall_box("F1_Wall_Right", (2.95, -1.70, 1.70), (0.10, 3.20, 2.70))

    # Front Wall architectural piers (leaves door [-0.60, 0.60] and windows open!):
    # Left outer pier: X in [-3.0, -2.75]
    make_wall_box("F1_Pier_FarLeft",  (-2.875, 0.0, 1.70), (0.25, 0.10, 2.70))
    # Mid-left pier (between left window and door): X in [-0.95, -0.60]
    make_wall_box("F1_Pier_MidLeft",  (-0.775, 0.0, 1.70), (0.35, 0.10, 2.70))
    # Mid-right pier (between door and right window): X in [0.60, 0.95]
    make_wall_box("F1_Pier_MidRight", (0.775, 0.0, 1.70),  (0.35, 0.10, 2.70))
    # Right outer pier: X in [2.75, 3.0]
    make_wall_box("F1_Pier_FarRight", (2.875, 0.0, 1.70),  (0.25, 0.10, 2.70))
    # Header above doorway and windows: Z in [2.45, 3.05]
    make_wall_box("F1_Header_Top",    (0.0, 0.0, 2.75),    (6.00, 0.10, 0.60))

    print("Floor 1 architectural openings constructed cleanly!")

    # -------------------------------------------------------------------------
    # 3. Clean up any leftover glow planes
    # -------------------------------------------------------------------------
    for side in ["Left", "Right"]:
        gp = bpy.data.objects.get(f"Interior_GlowPlane_{side}")
        if gp:
            bpy.data.objects.remove(gp, do_unlink=True)

    # -------------------------------------------------------------------------
    # 4. Baker Character Pose at frame 150
    # -------------------------------------------------------------------------
    root = bpy.data.objects.get("Baker_Root")
    if root:
        root.location = (-0.35, -1.85, 0.20)
        # Face 3/4 towards camera and front entrance door
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

    # -------------------------------------------------------------------------
    # 5. Setup Camera_Interior (Cinematic eye-level ~1.45m wide-angle)
    # -------------------------------------------------------------------------
    # Camera at X = 1.60, Y = -2.65, Z = 1.45
    # Lens 21mm aimed at (-0.35, -0.70, 1.15)
    # View captures:
    # - Foreground / Midground: The baker waving cheerfully, pastry display case with cookies/cupcakes, POS register
    # - Background: The open front door and bay window, revealing the moonlit sidewalk,
    #   bistro café table & chairs, glowing vintage streetlamp, and starry night sky!
    cam_int = bpy.data.objects.get("Camera_Interior")
    if cam_int:
        cam_int.data.lens = 21.0
        cam_int.location = (1.60, -2.65, 1.45)
        target = Vector((-0.35, -0.70, 1.15))
        direction = target - cam_int.location
        rot_quat = direction.to_track_quat('-Z', 'Y')
        cam_int.rotation_euler = rot_quat.to_euler()

    # Save the updated .blend file
    blend_path = r"C:\Users\PT.CTI\Documents\Tofan\Practice\3d blender\cookie_shop_animated_interior.blend"
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"Saved blend file to: {blend_path}")

    # -------------------------------------------------------------------------
    # 6. Render View 1: cookie_shop_interior_render.png
    # -------------------------------------------------------------------------
    scene.camera = cam_int
    scene.frame_set(150)
    int_path = r"C:\Users\PT.CTI\Documents\Tofan\Practice\3d blender\cookie_shop_interior_render.png"
    scene.render.filepath = int_path
    print(f"Rendering Interior View to {int_path}...")
    bpy.ops.render.render(write_still=True)
    print("Interior render finished!")

    # -------------------------------------------------------------------------
    # 7. Render View 2: cookie_shop_night_render.png
    # -------------------------------------------------------------------------
    store_cam = bpy.data.objects.get("Storefront_Camera")
    if store_cam:
        scene.camera = store_cam
        scene.frame_set(150)
        ext_path = r"C:\Users\PT.CTI\Documents\Tofan\Practice\3d blender\cookie_shop_night_render.png"
        scene.render.filepath = ext_path
        print(f"Rendering Storefront Night View to {ext_path}...")
        bpy.ops.render.render(write_still=True)
        print("Storefront night render finished!")

if __name__ == "__main__":
    run_fix()
