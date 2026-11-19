"""
render_urban_city.py
Sets Camera_City_Street and renders cookie_shop_urban_render.png at frame 150.
Also renders cookie_shop_interior_render.png.
Saves cookie_shop_urban_street.blend.
"""

import bpy

def main():
    scene = bpy.context.scene

    # Render City View
    cam_city = bpy.data.objects.get("Camera_City_Street")
    if cam_city:
        scene.camera = cam_city
        scene.frame_set(150)
        city_path = r"C:\Users\PT.CTI\Documents\Tofan\Practice\3d blender\cookie_shop_urban_render.png"
        scene.render.filepath = city_path
        print(f"Rendering Urban City View to {city_path}...")
        bpy.ops.render.render(write_still=True)
        print("Urban City render complete!")

    # Render Interior View
    cam_int = bpy.data.objects.get("Camera_Interior")
    if cam_int:
        scene.camera = cam_int
        scene.frame_set(150)
        int_path = r"C:\Users\PT.CTI\Documents\Tofan\Practice\3d blender\cookie_shop_interior_render.png"
        scene.render.filepath = int_path
        print(f"Rendering Interior View to {int_path}...")
        bpy.ops.render.render(write_still=True)
        print("Interior render complete!")

    blend_path = r"C:\Users\PT.CTI\Documents\Tofan\Practice\3d blender\cookie_shop_urban_street.blend"
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print("Saved blend file successfully!")

if __name__ == "__main__":
    main()
