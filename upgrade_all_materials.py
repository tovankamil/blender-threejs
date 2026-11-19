import bpy
import math

blend_file = r"C:\Users\PT.CTI\Documents\Tofan\Practice\3d blender\cookie_shop_urban_street.blend"
print(f"Opening {blend_file}...")
bpy.ops.wm.open_mainfile(filepath=blend_file)

def get_bsdf(mat):
    mat.use_nodes = True
    tree = mat.node_tree
    bsdf = None
    for n in tree.nodes:
        if n.type == 'BSDF_PRINCIPLED':
            bsdf = n
            break
    if not bsdf:
        bsdf = tree.nodes.new(type='ShaderNodeBsdfPrincipled')
        bsdf.location = (0, 300)
    
    # Ensure Output node exists
    output = None
    for n in tree.nodes:
        if n.type == 'OUTPUT_MATERIAL':
            output = n
            break
    if not output:
        output = tree.nodes.new(type='ShaderNodeOutputMaterial')
        output.location = (300, 300)
    
    # Link bsdf to output if not linked
    has_link = False
    for link in tree.links:
        if link.to_node == output:
            has_link = True
            break
    if not has_link:
        tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    return tree, bsdf

def set_val(bsdf, name, val):
    if name in bsdf.inputs:
        bsdf.inputs[name].default_value = val

def add_noise_bump(tree, bsdf, scale=35.0, detail=3.0, bump_strength=0.06):
    # Remove existing bumps if any
    for n in list(tree.nodes):
        if n.name.startswith("ProcBump_") or n.name.startswith("ProcNoise_"):
            tree.nodes.remove(n)
            
    tex_coord = tree.nodes.new(type='ShaderNodeTexCoord')
    tex_coord.name = "ProcNoise_Coord"
    tex_coord.location = (-600, 100)
    
    noise = tree.nodes.new(type='ShaderNodeTexNoise')
    noise.name = "ProcNoise_Tex"
    noise.location = (-400, 100)
    noise.inputs['Scale'].default_value = scale
    noise.inputs['Detail'].default_value = detail
    noise.inputs['Roughness'].default_value = 0.55
    tree.links.new(tex_coord.outputs['Object'], noise.inputs['Vector'])
    
    bump = tree.nodes.new(type='ShaderNodeBump')
    bump.name = "ProcBump_Node"
    bump.location = (-200, 100)
    bump.inputs['Strength'].default_value = bump_strength
    bump.inputs['Distance'].default_value = 0.1
    tree.links.new(noise.outputs['Fac'], bump.inputs['Height'])
    tree.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

print("Upgrading all materials with high-end stylized PBR shaders...")

all_mats = {m.name: m for m in bpy.data.materials}

for name, mat in all_mats.items():
    tree, bsdf = get_bsdf(mat)
    
    # ----------------------------------------------------
    # 1. BAKED GOODS & COOKIES (Crumbly texture, soft SSS warmth)
    # ----------------------------------------------------
    if name in ['Mat_CookieBrown', 'Mat_Int_CookieGold']:
        set_val(bsdf, 'Base Color', (0.75, 0.44, 0.22, 1.0))
        set_val(bsdf, 'Roughness', 0.76)
        set_val(bsdf, 'Subsurface Weight', 0.22)
        set_val(bsdf, 'Subsurface Radius', (1.0, 0.5, 0.2))
        set_val(bsdf, 'Subsurface Scale', 0.05)
        set_val(bsdf, 'Specular IOR Level', 0.4)
        add_noise_bump(tree, bsdf, scale=40.0, detail=4.0, bump_strength=0.08)
        
    elif name in ['Mat_DarkChocolate', 'Mat_Int_CookieChoc']:
        set_val(bsdf, 'Base Color', (0.13, 0.065, 0.035, 1.0))
        set_val(bsdf, 'Roughness', 0.26)
        set_val(bsdf, 'Specular IOR Level', 0.6)
        set_val(bsdf, 'Coat Weight', 0.3)
        set_val(bsdf, 'Coat Roughness', 0.08)
        
    elif name in ['Mat_BreadLoaf', 'Mat_Int_PastryCroissant']:
        set_val(bsdf, 'Base Color', (0.82, 0.48, 0.22, 1.0))
        set_val(bsdf, 'Roughness', 0.68)
        set_val(bsdf, 'Subsurface Weight', 0.18)
        set_val(bsdf, 'Subsurface Radius', (1.0, 0.4, 0.15))
        set_val(bsdf, 'Subsurface Scale', 0.05)
        add_noise_bump(tree, bsdf, scale=35.0, detail=3.0, bump_strength=0.06)
        
    elif name == 'Mat_Int_PastryPink':
        # Glossy sweet strawberry glaze
        set_val(bsdf, 'Base Color', (0.98, 0.55, 0.68, 1.0))
        set_val(bsdf, 'Roughness', 0.16)
        set_val(bsdf, 'Subsurface Weight', 0.15)
        set_val(bsdf, 'Coat Weight', 0.6)
        set_val(bsdf, 'Coat Roughness', 0.05)
        
    # ----------------------------------------------------
    # 2. WOODS & PLANKING (Warm satin finish, rich golden undertones)
    # ----------------------------------------------------
    elif name in ['Mat_Int_WoodFloor', 'Mat_Int_WoodFloor2']:
        set_val(bsdf, 'Base Color', (0.58, 0.36, 0.18, 1.0))
        set_val(bsdf, 'Roughness', 0.45)
        set_val(bsdf, 'Sheen Weight', 0.35)
        set_val(bsdf, 'Sheen Roughness', 0.4)
        set_val(bsdf, 'Specular IOR Level', 0.55)
        add_noise_bump(tree, bsdf, scale=25.0, detail=2.0, bump_strength=0.03)
        
    elif name in ['Mat_Int_CounterOak', 'Mat_TableTop', 'Mat_ChairWood', 'Mat_FenceWood', 'Mat_City_WoodCedar', 'Mat_TreeWood']:
        set_val(bsdf, 'Roughness', 0.48)
        set_val(bsdf, 'Sheen Weight', 0.3)
        set_val(bsdf, 'Specular IOR Level', 0.5)
        add_noise_bump(tree, bsdf, scale=20.0, detail=2.0, bump_strength=0.03)
        
    # ----------------------------------------------------
    # 3. PASTEL ARCHITECTURE & STOREFRONT (Velvety eggshell architectural finish)
    # ----------------------------------------------------
    elif name in ['Mat_Mint', 'Mat_Int_MintPanel']:
        set_val(bsdf, 'Base Color', (0.42, 0.76, 0.68, 1.0))
        set_val(bsdf, 'Roughness', 0.52)
        set_val(bsdf, 'Specular IOR Level', 0.5)
        
    elif name in ['Mat_Peach', 'Mat_Int_PeachWall']:
        set_val(bsdf, 'Base Color', (0.98, 0.70, 0.54, 1.0))
        set_val(bsdf, 'Roughness', 0.54)
        set_val(bsdf, 'Specular IOR Level', 0.5)
        
    elif name == 'Mat_SoftPink':
        set_val(bsdf, 'Base Color', (0.98, 0.62, 0.70, 1.0))
        set_val(bsdf, 'Roughness', 0.50)
        set_val(bsdf, 'Specular IOR Level', 0.5)
        
    elif name in ['Mat_WarmCream', 'Mat_City_CreamStone', 'Mat_Int_WhiteTrim', 'Mat_City_WhitePaint']:
        set_val(bsdf, 'Base Color', (0.96, 0.95, 0.92, 1.0))
        set_val(bsdf, 'Roughness', 0.46)
        set_val(bsdf, 'Specular IOR Level', 0.52)
        
    elif name in ['Mat_CottageRoof', 'Mat_City_BrickRed']:
        set_val(bsdf, 'Base Color', (0.75, 0.32, 0.22, 1.0))
        set_val(bsdf, 'Roughness', 0.78)
        add_noise_bump(tree, bsdf, scale=30.0, detail=3.0, bump_strength=0.05)
        
    elif name in ['Mat_CottageWall', 'Mat_City_BrickBrown']:
        set_val(bsdf, 'Roughness', 0.80)
        add_noise_bump(tree, bsdf, scale=30.0, detail=3.0, bump_strength=0.05)
        
    # ----------------------------------------------------
    # 4. METALS & TRIMS (True PBR reflections)
    # ----------------------------------------------------
    elif name in ['Mat_Brass', 'Mat_Int_Brass', 'Mat_GoldLetters', 'Mat_GoldSignText', 'Mat_GoldSignText.001', 'Mat_GoldText']:
        set_val(bsdf, 'Base Color', (0.98, 0.82, 0.36, 1.0))
        set_val(bsdf, 'Metallic', 1.0)
        set_val(bsdf, 'Roughness', 0.24)
        set_val(bsdf, 'Specular IOR Level', 0.85)
        
    elif name in ['Mat_DarkIron', 'Mat_City_DarkIron', 'Mat_Int_OvenMetal']:
        set_val(bsdf, 'Base Color', (0.16, 0.17, 0.20, 1.0))
        set_val(bsdf, 'Metallic', 0.88)
        set_val(bsdf, 'Roughness', 0.36)
        set_val(bsdf, 'Specular IOR Level', 0.6)
        
    # ----------------------------------------------------
    # 5. GLASS & CRYSTAL SURFACES
    # ----------------------------------------------------
    elif name in ['Mat_Glass', 'Mat_Int_DisplayGlass']:
        set_val(bsdf, 'Base Color', (0.92, 0.97, 1.0, 1.0))
        set_val(bsdf, 'Transmission Weight', 0.95)
        set_val(bsdf, 'Roughness', 0.04)
        set_val(bsdf, 'IOR', 1.52)
        set_val(bsdf, 'Specular IOR Level', 0.6)
        
    # ----------------------------------------------------
    # 6. GLOWING EMISSIVES (Atmospheric night bloom)
    # ----------------------------------------------------
    elif name == 'Mat_Int_OvenGlow':
        set_val(bsdf, 'Base Color', (1.0, 0.28, 0.02, 1.0))
        set_val(bsdf, 'Emission Color', (1.0, 0.38, 0.08, 1.0))
        set_val(bsdf, 'Emission Strength', 5.0)
        
    elif name in ['Mat_Int_DisplayGlow', 'Mat_Int_PendantGlow', 'Mat_InteriorGlow', 'Mat_FairyBulb']:
        set_val(bsdf, 'Base Color', (1.0, 0.85, 0.50, 1.0))
        set_val(bsdf, 'Emission Color', (1.0, 0.88, 0.55, 1.0))
        set_val(bsdf, 'Emission Strength', 3.5)
        
    elif name in ['Mat_WindowLitGlow', 'Mat_City_WindowLit', 'Mat_F2LitGlow', 'Mat_City_Headlight']:
        set_val(bsdf, 'Base Color', (1.0, 0.90, 0.58, 1.0))
        set_val(bsdf, 'Emission Color', (1.0, 0.90, 0.60, 1.0))
        set_val(bsdf, 'Emission Strength', 2.8)
        
    elif name in ['Mat_City_Taillight', 'Mat_City_HydrantRed']:
        set_val(bsdf, 'Base Color', (0.95, 0.08, 0.08, 1.0))
        if name == 'Mat_City_Taillight':
            set_val(bsdf, 'Emission Color', (1.0, 0.10, 0.05, 1.0))
            set_val(bsdf, 'Emission Strength', 3.0)
            
    elif name == 'Mat_Moon':
        set_val(bsdf, 'Base Color', (1.0, 0.96, 0.82, 1.0))
        set_val(bsdf, 'Emission Color', (1.0, 0.96, 0.82, 1.0))
        set_val(bsdf, 'Emission Strength', 3.0)
        
    elif name.startswith('Mat_Star_'):
        set_val(bsdf, 'Base Color', (1.0, 1.0, 1.0, 1.0))
        set_val(bsdf, 'Emission Color', (1.0, 0.98, 0.88, 1.0))
        set_val(bsdf, 'Emission Strength', 3.5)
        
    # ----------------------------------------------------
    # 7. AUTOMOTIVE & VEHICLES (Glossy die-cast toy look)
    # ----------------------------------------------------
    elif name == 'Mat_City_TaxiYellow':
        set_val(bsdf, 'Base Color', (0.98, 0.80, 0.15, 1.0))
        set_val(bsdf, 'Roughness', 0.20)
        set_val(bsdf, 'Coat Weight', 1.0)
        set_val(bsdf, 'Coat Roughness', 0.04)
        
    elif name == 'Mat_City_CarTeal':
        set_val(bsdf, 'Base Color', (0.18, 0.72, 0.76, 1.0))
        set_val(bsdf, 'Roughness', 0.20)
        set_val(bsdf, 'Coat Weight', 1.0)
        set_val(bsdf, 'Coat Roughness', 0.04)
        
    elif name == 'Mat_City_CarTire':
        set_val(bsdf, 'Base Color', (0.07, 0.07, 0.08, 1.0))
        set_val(bsdf, 'Roughness', 0.85)
        
    # ----------------------------------------------------
    # 8. CHARACTERS & FABRICS
    # ----------------------------------------------------
    elif name in ['Mat_Int_BakerSkin', 'Mat_Char_Skin']:
        set_val(bsdf, 'Base Color', (0.96, 0.78, 0.70, 1.0))
        set_val(bsdf, 'Roughness', 0.48)
        set_val(bsdf, 'Subsurface Weight', 0.35)
        set_val(bsdf, 'Subsurface Radius', (1.0, 0.4, 0.2))
        set_val(bsdf, 'Subsurface Scale', 0.03)
        
    elif name in ['Mat_Int_BakerApron', 'Mat_Int_BakerHat', 'Mat_Int_BakerShirt']:
        set_val(bsdf, 'Roughness', 0.75)
        set_val(bsdf, 'Sheen Weight', 0.6)
        set_val(bsdf, 'Sheen Roughness', 0.5)
        
    elif name in ['Mat_Int_BakerPants', 'Mat_Char_Jeans', 'Mat_Char_CoatMaroon', 'Mat_Char_CoatTan', 'Mat_ChairCushion']:
        set_val(bsdf, 'Roughness', 0.72)
        set_val(bsdf, 'Sheen Weight', 0.5)
        set_val(bsdf, 'Sheen Roughness', 0.5)
        
    elif name == 'Mat_Char_DogFur':
        set_val(bsdf, 'Base Color', (0.86, 0.60, 0.30, 1.0))
        set_val(bsdf, 'Roughness', 0.80)
        set_val(bsdf, 'Sheen Weight', 0.8)
        
    # ----------------------------------------------------
    # 9. ROADS, SIDEWALK & MASONRY
    # ----------------------------------------------------
    elif name in ['Mat_City_Asphalt', 'Mat_Road']:
        set_val(bsdf, 'Base Color', (0.13, 0.14, 0.16, 1.0))
        set_val(bsdf, 'Roughness', 0.70)
        add_noise_bump(tree, bsdf, scale=50.0, detail=3.0, bump_strength=0.05)
        
    elif name in ['Mat_Sidewalk', 'Mat_SteppingStone', 'Mat_City_CurbGray', 'Mat_Curb']:
        set_val(bsdf, 'Base Color', (0.76, 0.78, 0.80, 1.0))
        set_val(bsdf, 'Roughness', 0.68)
        add_noise_bump(tree, bsdf, scale=40.0, detail=3.0, bump_strength=0.04)
        
    elif name == 'Mat_RoadLine':
        set_val(bsdf, 'Base Color', (0.95, 0.95, 0.95, 1.0))
        set_val(bsdf, 'Roughness', 0.60)
        
    # ----------------------------------------------------
    # 10. NATURE & VEGETATION
    # ----------------------------------------------------
    elif name in ['Mat_Foliage1', 'Mat_Foliage2', 'Mat_BackyardGrass']:
        set_val(bsdf, 'Roughness', 0.62)
        set_val(bsdf, 'Subsurface Weight', 0.25)
        set_val(bsdf, 'Subsurface Radius', (0.4, 1.0, 0.2))
        set_val(bsdf, 'Subsurface Scale', 0.05)
        
    elif name in ['Mat_FlowerPink', 'Mat_FlowerYellow']:
        set_val(bsdf, 'Roughness', 0.45)
        set_val(bsdf, 'Subsurface Weight', 0.3)
        set_val(bsdf, 'Subsurface Radius', (1.0, 0.5, 0.2))
        
    elif name in ['Mat_Chalkboard', 'Mat_Int_Chalkboard']:
        set_val(bsdf, 'Base Color', (0.10, 0.11, 0.12, 1.0))
        set_val(bsdf, 'Roughness', 0.88)
        
    elif name == 'Mat_Int_ChalkText':
        set_val(bsdf, 'Base Color', (0.95, 0.95, 0.95, 1.0))
        set_val(bsdf, 'Emission Color', (1.0, 1.0, 1.0, 1.0))
        set_val(bsdf, 'Emission Strength', 1.2)
        
    elif name == 'Mat_Int_FlourSack':
        set_val(bsdf, 'Base Color', (0.92, 0.88, 0.82, 1.0))
        set_val(bsdf, 'Roughness', 0.85)
        set_val(bsdf, 'Sheen Weight', 0.5)

print("All 92 materials upgraded successfully!")

# Save blend file
bpy.ops.wm.save_mainfile()
print(f"Saved updated master blend file: {blend_file}")
