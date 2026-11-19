import bpy
import os

blend_file = r"C:\Users\PT.CTI\Documents\Tofan\Practice\3d blender\cookie_shop_urban_street.blend"
out_glb = r"C:\Users\PT.CTI\Documents\Tofan\Practice\3d blender\cookie_shop_scene.glb"

print(f"Loading {blend_file}...")
bpy.ops.wm.open_mainfile(filepath=blend_file)

print("Exporting GLB cleanly (no punctual lights, no cameras)...")
bpy.ops.export_scene.gltf(
    filepath=out_glb,
    export_format='GLB',
    use_selection=False,
    export_lights=False,
    export_cameras=False,
    export_materials='EXPORT',
    export_animations=True,
    export_apply=True
)

file_size = os.path.getsize(out_glb)
print(f"Successfully exported clean GLB: {out_glb} ({file_size} bytes)")
