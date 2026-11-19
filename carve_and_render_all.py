"""
carve_and_render_all.py
1. Carves doorway and bay window openings cleanly through Floor1_Walls.
2. Adjusts Door_Hinge rotation to 25 degrees inward.
3. Configures Camera_Interior and baker pose.
4. Renders cookie_shop_interior_render.png.
5. Renders cookie_shop_night_render.png.
6. Saves cookie_shop_animated_interior.blend.
"""

import bpy
import bmesh
import math
from mathutils import Vector, Euler

def run():
    scene = bpy.context.scene

    # 1. Carve openings in Floor1_Walls
    walls = bpy.data.objects.get("Floor1_Walls")
    if walls:
        bm = bmesh.new()

        # Door cutter: X in [-0.65, 0.65], Y in [-0.5, 0.5], Z in [0.22, 2.50]
        c1 = bmesh.ops.create_cube(bm, size=1.0)
        for v in c1['verts']:
            v.co.x *= 1.30
            v.co.y *= 1.00
            v.co.z *= 2.30
            v.co.x += 0.0
            v.co.y += 0.0
            v.co.z += 1.35

        # Left Window cutter: X in [-2.80, -0.90], Y in [-0.5, 0.5], Z in [0.75, 2.50]
        c2 = bmesh.ops.create_cube(bm, size=1.0)
        for v in c2['verts']:
            v.co.x *= 1.90
            v.co.y *= 1.00
            v.co.z *= 1.75
            v.co.x += -1.85
            v.co.y += 0.0
            v.co.z += 1.625

        # Right Window cutter: X in [0.90, 2.80], Y in [-0.5, 0.5], Z in [0.75, 2.50]
        c3 = bmesh.ops.create_cube(bm, size=1.0)
        for v in c3['verts']:
            v.co.x *= 1.90
            v.co.y *= 1.00
            v.co.z *= 1.75
            v.co.x += 1.85
            v.co.y += 0.0
            v.co.z += 1.625

        cutter_mesh = bpy.data.meshes.new("Temp_Wall_Cutter")
        bm.to_mesh(cutter_mesh)
        bm.free()

        cutter_obj = bpy.data.objects.new("Wall_Cutter", cutter_mesh)
        scene.collection.objects.link(cutter_obj)

        mod = walls.modifiers.new(name="Carve_Openings", type='BOOLEAN')
        mod.operation = 'DIFFERENCE'
        mod.object = cutter_obj
        mod.solver = 'EXACT'

        bpy.context.view_layer.objects.active = walls
        bpy.ops.object.modifier_apply(modifier=mod.name)

        bpy.data.objects.remove(cutter_obj, do_unlink=True)
        bpy.data.meshes.remove(cutter_mesh)
        print(f"Floor1_Walls openings carved! Verts: {len(walls.data.vertices)}, Polys: {len(walls.data.polygons)}")

    # 2. Ensure door swings open inward
    hinge = bpy.data.objects.get("Door_Hinge")
    if hinge:
        hinge.rotation_euler.z = -math.radians(26)

    # 3. Baker Character Pose at frame 150
    root = bpy.data.objects.get("Baker_Root")
    if root:
        root.location = (-0.35, -1.85, 0.20)
        root.rotation_euler = (0, 0, math.radians(40))
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

    # 4. Camera_Interior Setup
    cam_int = bpy.data.objects.get("Camera_Interior")
    if cam_int:
        cam_int.data.lens = 22.0
        cam_int.location = (1.65, -2.75, 1.45)
        target = Vector((-0.30, -0.70, 1.15))
        direction = target - cam_int.location
        rot_quat = direction.to_track_quat('-Z', 'Y')
        cam_int.rotation_euler = rot_quat.to_euler()

    # Save the updated .blend file
    blend_path = r"C:\Users\PT.CTI\Documents\Tofan\Practice\3d blender\cookie_shop_animated_interior.blend"
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"Saved blend file to: {blend_path}")

    # 5. Render View 1: cookie_shop_interior_render.png
    scene.camera = cam_int
    scene.frame_set(150)
    int_path = r"C:\Users\PT.CTI\Documents\Tofan\Practice\3d blender\cookie_shop_interior_render.png"
    scene.render.filepath = int_path
    print(f"Rendering interior to {int_path}...")
    bpy.ops.render.render(write_still=True)
    print("Interior render finished!")

    # 6. Render View 2: cookie_shop_night_render.png
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
    run()
