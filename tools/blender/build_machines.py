"""
Starfall Forge - machine models (Crusher, Smelter, Forge press, Star Anvil).
Run headless:  python3 build_machines.py  [--render] [--anim] [--export]

Art rules (docs/ART_BIBLE.md, CON-01 "Sunlit Toy Foundry"):
  chunky bevelled toy shapes, red enamel shells, cream trim, navy-steel working parts,
  emissive orange only where it glows. NO baked textures: every part is a separate object
  named  <Machine>__<Part>__<MatKey>  so Roblox can assign Material + Color per part
  (crisp at any distance, no stretched/blurry textures). Moving parts are separate objects
  with their pivot at the motion centre so Roblox scripts animate them.
Units: 1 Blender unit = 1 stud. Blender axes: X = width, -Y = front (faces the crater), Z = up.
"""
import bpy, bmesh, math, sys, os
from mathutils import Vector, Matrix

OUT = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- materials (preview only)
PALETTE = {  # sRGB hex -> used for previews; Roblox gets the same values via the part name
    "Red": ("D95542", 0.0, 0.55, 0), "Cream": ("FFF0CF", 0.0, 0.6, 0), "Steel": ("344658", 0.55, 0.38, 0),
    "SteelLight": ("6E7F93", 0.6, 0.32, 0), "Dark": ("1F2430", 0.2, 0.6, 0), "Yellow": ("FFC83D", 0.0, 0.5, 0),
    "Glow": ("FF9A3C", 0.0, 0.4, 7), "Gold": ("FFD24A", 0.3, 0.35, 5), "Ember": ("FF5A1E", 0.0, 0.5, 9),
    # pets v2 (T-04-02, build_pets_v2.py): hex codes from Astra's sheets in art/concepts/PETS/. Emission > 0 = Neon in Roblox
    "PebBody": ("8C8597", 0, .8, 0), "PebSpot": ("5E5868", 0, .8, 0), "PebCrystal": ("B9A8E0", 0, .3, 0),
    "CinderBody": ("4A3B44", 0, .75, 0), "CinderGlow": ("FF7A2A", 0, .4, 8),
    "RubBody": ("6E6585", 0, .8, 0), "RubSpike": ("C9B6A6", 0, .6, 0),
    "KitBody": ("5A2E2A", 0, .75, 0), "DarkRock": ("3B3540", 0, .75, 0), "MawJaw": ("6B6470", 0, .7, 0),
    "MawGlow": ("FFB13D", 0, .4, 7), "GoldGlow": ("FFE21B", 0, .4, 6),
    "FrostCrystal": ("BDEBFF", 0, .25, 0), "FrostGlow": ("BDEBFF", 0, .3, 5), "GlacioBeak": ("3D5C8A", 0, .6, 0),
    "AuroraBody": ("64DFD1", 0, .55, 0), "Cloud": ("FFE6F6", 0, .7, 0), "NebStar": ("B07CFF", 0, .5, 0),
    "WhaleBelly2": ("4C64B8", 0, .6, 0), "Magenta": ("FF4FD8", 0, .45, 0), "CoreRed": ("FF3B1F", 0, .4, 8),
    "CoreArmor": ("241E2C", 0, .7, 0), "Glass": ("BDEFFF", 0, .05, 0),
}

def srgb(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]

def material(key):
    if key in bpy.data.materials:
        return bpy.data.materials[key]
    h, metal, rough, emit = PALETTE[key]
    m = bpy.data.materials.new(key)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    col = srgb(h) + [1]
    b.inputs["Base Color"].default_value = col
    b.inputs["Metallic"].default_value = metal
    b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = col
        b.inputs["Emission Strength"].default_value = emit
    return m

# ---------------------------------------------------------------- mesh helpers
def _finish(obj, mat, bevel, seg, smooth=True):
    obj.data.materials.clear()
    obj.data.materials.append(material(mat))
    if smooth:
        for p in obj.data.polygons:
            p.use_smooth = True
    if bevel > 0:
        m = obj.modifiers.new("Bevel", "BEVEL")
        m.width = bevel
        m.segments = seg
        m.limit_method = "ANGLE"
        m.angle_limit = math.radians(35)
        m.harden_normals = True
    obj["mat"] = mat
    return obj

def box(size, loc, mat, bevel=0.15, seg=2, rot=(0, 0, 0), name="p"):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return _finish(o, mat, bevel, seg)

def cyl(r, depth, loc, mat, axis="Z", verts=24, bevel=0.08, seg=2, r2=None, name="c"):
    rot = {"Z": (0, 0, 0), "X": (0, math.pi / 2, 0), "Y": (math.pi / 2, 0, 0)}[axis]
    if r2 is None:
        bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=depth, location=loc, rotation=rot)
    else:
        bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r, radius2=r2, depth=depth, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    return _finish(o, mat, bevel, seg)

def frustum(bottom, top, z0, z1, mat, thick=0.35, name="f"):
    """open-top/open-bottom square funnel (hopper)"""
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bw, bd = bottom
    tw, td = top
    vb = [bm.verts.new((x * bw / 2, y * bd / 2, z0)) for x, y in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    vt = [bm.verts.new((x * tw / 2, y * td / 2, z1)) for x, y in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new((vb[i], vb[j], vt[j], vt[i]))
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    s = o.modifiers.new("Solid", "SOLIDIFY")
    s.thickness = thick
    s.offset = -1
    return _finish(o, mat, 0.08, 2)

def star4(radius, inner, thick, loc, mat, name="star"):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    pts = []
    for i in range(8):
        a = i * math.pi / 4 + math.pi / 2
        r = radius if i % 2 == 0 else inner
        pts.append((math.cos(a) * r, 0, math.sin(a) * r))
    front = [bm.verts.new((x, -thick / 2, z)) for x, _, z in pts]
    back = [bm.verts.new((x, thick / 2, z)) for x, _, z in pts]
    bm.faces.new(front[::-1])
    bm.faces.new(back)
    for i in range(8):
        j = (i + 1) % 8
        bm.faces.new((front[i], front[j], back[j], back[i]))
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    o.location = loc
    return _finish(o, mat, 0.06, 2)

def apply_mods(o):
    dg = bpy.context.evaluated_depsgraph_get()
    ev = o.evaluated_get(dg)
    me = bpy.data.meshes.new_from_object(ev, preserve_all_data_layers=True, depsgraph=dg)
    o.modifiers.clear()
    old = o.data
    o.data = me
    bpy.data.meshes.remove(old)

def boolean(target, cutter, op="DIFFERENCE"):
    m = target.modifiers.new("Bool", "BOOLEAN")
    m.operation = op
    m.object = cutter
    m.solver = "EXACT"
    # boolean must run before bevel: move it to the top
    while target.modifiers.find("Bool") > 0:
        with bpy.context.temp_override(object=target):
            bpy.ops.object.modifier_move_up(modifier="Bool")
    apply_mods(target)
    bpy.data.objects.remove(cutter, do_unlink=True)

def part(machine, pname, objs, parent, pivot=None):
    """apply modifiers, join objs into one object named <machine>__<pname>__<mat>, origin at pivot"""
    for o in objs:
        apply_mods(o)
    if len(objs) > 1:
        with bpy.context.temp_override(active_object=objs[0], selected_editable_objects=objs, selected_objects=objs):
            bpy.ops.object.join()
    o = objs[0]
    mat = o["mat"]
    o.name = f"{machine}__{pname}__{mat}"
    o.data.name = o.name
    # bake the object's own transform into the mesh (rotated pieces!), so local == world
    o.data.transform(o.matrix_basis)
    o.matrix_basis = Matrix.Identity(4)
    # origin: pivot (motion centre) or bounding-box centre
    if pivot is None:
        pivot = sum((Vector(c) for c in o.bound_box), Vector()) / 8
    pv = Vector(pivot)
    o.data.transform(Matrix.Translation(-pv))
    o.location = pv
    o.parent = parent
    return o

def root(name, x):
    e = bpy.data.objects.new(name, None)
    e.empty_display_type = "PLAIN_AXES"
    e.location = (x, 0, 0)
    bpy.context.collection.objects.link(e)
    return e

# ---------------------------------------------------------------- machines (built at origin, then moved)
def crusher(R):
    M = "Crusher"
    part(M, "Base", [box((10.4, 9, 0.8), (0, 0, 0.4), "Steel", 0.2)], R)
    part(M, "Body", [box((9, 7.6, 5), (0, 0, 3.3), "Red", 0.35, 3)], R)
    trim = [box((9.3, 7.9, 0.5), (0, 0, 5.75), "Cream", 0.15),  # top band
            box((5.6, 0.3, 2.6), (0, -3.85, 3.2), "Cream", 0.12),  # front door panel
            box((1.2, 7.6, 2.9), (-3.95, 0, 7.4), "Cream", 0.25),  # roller cheeks
            box((1.2, 7.6, 2.9), (3.95, 0, 7.4), "Cream", 0.25),
            box((9.9, 8.3, 0.5), (0, 0, 11.15), "Cream", 0.15)]  # hopper rim
    # hollow out the rim
    cut = box((8.9, 7.3, 1.2), (0, 0, 11.15), "Cream", 0)
    boolean(trim[-1], cut)
    part(M, "Trim", trim, R)
    part(M, "Hopper", [frustum((6.7, 5.4), (9.5, 7.9), 8.6, 11.0, "Red", 0.35)], R)
    for side, y in (("Front", -1.15), ("Back", 1.15)):
        bits = [cyl(1.05, 6.6, (0, y, 7.1), "Steel", "X", 16, 0.06)]
        for k in range(4):
            for a in range(6):
                ang = a * math.pi / 3 + (k % 2) * math.pi / 6
                x = -2.4 + k * 1.6
                bits.append(box((0.6, 0.45, 0.45), (x, y + math.cos(ang) * 1.1, 7.1 + math.sin(ang) * 1.1), "Steel", 0.06, 1, rot=(ang, 0, 0)))
        part(M, f"Roller{side}", bits, R, pivot=(0, y, 7.1))
    for side, x in (("L", -4.75), ("R", 4.75)):
        bits = [cyl(1.25, 0.45, (x, -1.15, 7.1), "SteelLight", "X", 20, 0.05), cyl(0.45, 0.6, (x, -1.15, 7.1), "Steel", "X", 12, 0.05)]
        for t in range(10):
            ang = t * math.pi / 5
            bits.append(box((0.45, 0.42, 0.42), (x, -1.15 + math.cos(ang) * 1.38, 7.1 + math.sin(ang) * 1.38), "SteelLight", 0.06, 1, rot=(ang, 0, 0)))
        part(M, f"Gear{side}", bits, R, pivot=(x, -1.15, 7.1))
    chute = box((5, 2.4, 0.35), (0, -5.0, 1.2), "Steel", 0.1, rot=(math.radians(-18), 0, 0))
    lips = [box((0.3, 2.4, 0.7), (s * 2.4, -5.0, 1.45), "Steel", 0.08, rot=(math.radians(-18), 0, 0)) for s in (-1, 1)]
    part(M, "Chute", [chute] + lips, R)
    part(M, "Glow", [box((4.6, 0.25, 0.55), (0, -3.95, 1.55), "Glow", 0.1)], R)
    rivets = [cyl(0.18, 0.2, (x, -3.86, z), "Steel", "Y", 10, 0.04) for x in (-4.0, 4.0) for z in (1.6, 4.9)]
    part(M, "Rivets", rivets, R)

def smelter(R):
    M = "Smelter"
    part(M, "Base", [box((9.4, 9.4, 0.8), (0, 0, 0.4), "Steel", 0.2)], R)
    body = box((8, 8, 7), (0, 0, 4.3), "Red", 0.35, 3)
    # arched furnace mouth
    c1 = cyl(1.6, 3, (0, -3.6, 4.0), "Red", "Y", 32, 0)
    boolean(body, c1)
    c2 = box((3.2, 3, 2.4), (0, -3.6, 2.6), "Red", 0)
    boolean(body, c2)
    part(M, "Body", [body], R)
    frame = box((4.8, 0.7, 5.0), (0, -4.0, 3.3), "Cream", 0.18)
    f1 = cyl(1.6, 3, (0, -4.0, 4.0), "Cream", "Y", 32, 0)
    boolean(frame, f1)
    f2 = box((3.2, 3, 2.6), (0, -4.0, 2.5), "Cream", 0)
    boolean(frame, f2)
    part(M, "Trim", [frame, box((8.6, 8.6, 0.7), (0, 0, 8.15), "Cream", 0.18), box((6.4, 6.4, 0.5), (0, 0, 11.0), "Cream", 0.15)], R)
    part(M, "Upper", [box((6, 6, 2.6), (0, 0, 9.6), "Red", 0.3, 3)], R)
    part(M, "Chimney", [cyl(0.95, 4.2, (1.4, 1.4, 13.2), "Steel", "Z", 20, 0.08), cyl(1.25, 0.5, (1.4, 1.4, 15.3), "Steel", "Z", 20, 0.1)], R)
    part(M, "Fire", [box((3.0, 0.3, 3.4), (0, -2.0, 3.0), "Glow", 0.1), cyl(1.45, 0.3, (0, -2.0, 4.0), "Glow", "Y", 24, 0.05)], R)
    coals = [box((0.7, 0.6, 0.45), (x, -2.9 + (i % 2) * 0.4, 1.05), "Ember", 0.12, rot=(0, 0, 0.4 * i)) for i, x in enumerate((-1.1, -0.4, 0.3, 1.0))]
    part(M, "Coals", coals, R)
    vents = [box((0.15, 4.4, 0.35), (s * 4.02, 0, z), "Dark", 0.05) for s in (-1, 1) for z in (5.4, 6.2, 7.0)]
    part(M, "Vents", vents, R)
    part(M, "Tray", [box((4.4, 1.6, 0.35), (0, -5.0, 0.95), "Steel", 0.1)], R)

def forge(R):
    M = "Forge"
    part(M, "Base", [box((11.4, 7, 1), (0, 0, 0.5), "Steel", 0.2)], R)
    part(M, "Pillars", [box((1.8, 3.2, 12.4), (s * 4.4, 0, 7.2), "Red", 0.3, 3) for s in (-1, 1)] +
         [box((10.6, 3.6, 2.2), (0, 0, 14.4), "Red", 0.35, 3)], R)
    part(M, "Trim", [box((2.2, 3.6, 0.5), (s * 4.4, 0, 1.25), "Cream", 0.12) for s in (-1, 1)] +
         [box((11.0, 3.9, 0.45), (0, 0, 13.2), "Cream", 0.12), box((11.0, 3.9, 0.45), (0, 0, 15.6), "Cream", 0.12)], R)
    # hazard stripes on the pillar fronts: yellow plate + dark diagonal bars clipped to the plate
    plates, bars = [], []
    for s in (-1, 1):
        plates.append(box((1.5, 0.12, 4.2), (s * 4.4, -1.66, 8.5), "Yellow", 0.03, 1))
        for k in range(5):
            b = box((0.42, 0.14, 3.2), (s * 4.4, -1.73, 6.6 + k * 0.95), "Dark", 0.0, 1, rot=(0, math.radians(45), 0))
            clip = box((1.5, 0.5, 4.2), (s * 4.4, -1.7, 8.5), "Dark", 0)
            boolean(b, clip, "INTERSECT")
            bars.append(b)
    part(M, "StripesYellow", plates, R)
    part(M, "StripesDark", bars, R)
    part(M, "Bed", [box((5.2, 4.2, 1.6), (0, 0, 1.8), "Steel", 0.25), box((3.8, 3.2, 0.6), (0, 0, 2.9), "SteelLight", 0.15)], R)
    part(M, "Ingot", [box((2.4, 1.3, 0.6), (0, 0, 3.5), "Glow", 0.18)], R)
    part(M, "Sleeve", [cyl(0.85, 1.2, (0, 0, 12.7), "SteelLight", "Z", 20, 0.08)], R)
    # hammer (head + rod) moves on Z; pivot at head centre
    part(M, "Hammer", [box((3.6, 2.8, 2.4), (0, 0, 7.4), "Steel", 0.3, 3), box((3.9, 3.1, 0.35), (0, 0, 6.2), "SteelLight", 0.1),
                       cyl(0.5, 5.2, (0, 0, 11.0), "SteelLight", "Z", 16, 0.05)], R, pivot=(0, 0, 7.6))
    part(M, "Pipes", [cyl(0.28, 10.5, (s * 5.45, 0.9, 7.0), "SteelLight", "Z", 12, 0.04) for s in (-1, 1)], R)

def star_anvil(R):
    M = "StarAnvil"
    part(M, "Pedestal", [box((8.2, 5.6, 0.8), (0, 0, 0.4), "Cream", 0.2), box((5.2, 3.2, 0.5), (0, 0, 2.25), "Cream", 0.15)], R)
    part(M, "PedestalRed", [box((7.2, 4.6, 1.2), (0, 0, 1.4), "Red", 0.3, 3)], R)
    anvil = [box((2.4, 2.0, 1.5), (0, 0, 3.25), "Steel", 0.2),  # waist
             box((5.8, 2.6, 1.3), (-0.3, 0, 4.6), "Steel", 0.25, 3),  # face
             box((1.6, 2.2, 0.9), (-3.1, 0, 4.75), "Steel", 0.2),  # heel
             cyl(0.95, 2.6, (3.75, 0, 4.75), "Steel", "X", 20, 0.06, r2=0.12)]  # horn
    part(M, "Anvil", anvil, R)
    part(M, "Face", [box((5.0, 2.1, 0.12), (-0.3, 0, 5.28), "SteelLight", 0.03, 1)], R)
    part(M, "Star", [star4(1.6, 0.5, 0.55, (0, 0, 7.6), "Gold")], R, pivot=(0, 0, 7.6))

# ---------------------------------------------------------------- scene
def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    roots = {}
    for name, fn, x in (("Crusher", crusher, -21), ("Smelter", smelter, -7), ("Forge", forge, 7), ("StarAnvil", star_anvil, 21)):
        r = root(name, 0)
        fn(r)
        r.location.x = x
        roots[name] = r
    return roots

def stats():
    out = []
    for r in [o for o in bpy.data.objects if o.type == "EMPTY"]:
        tris = sum(sum(len(p.vertices) - 2 for p in c.data.polygons) for c in r.children)
        out.append(f"{r.name}: {len(r.children)} parts, {tris} tris")
    return out

def setup_render(w, h, samples):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Medium High Contrast"
    world = bpy.data.worlds.new("Sky")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = srgb("9FD3F0") + [1]
    world.node_tree.nodes["Background"].inputs[1].default_value = 0.9
    sc.world = world
    bpy.ops.object.light_add(type="SUN", rotation=(math.radians(50), math.radians(10), math.radians(-35)))
    bpy.context.object.data.energy = 3.2
    bpy.context.object.data.angle = math.radians(8)
    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, 0))
    g = bpy.context.object
    gm = bpy.data.materials.new("Ground")
    gm.use_nodes = True
    gm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = srgb("DB9856") + [1]
    gm.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.8
    g.data.materials.append(gm)
    bpy.ops.object.camera_add(location=(10, -62, 24))
    cam = bpy.context.object
    cam.data.lens = 38
    d = Vector((0, 0, 6)) - cam.location
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    sc.camera = cam

def animate(frames):
    """preview motion = the same motion the Roblox scripts play (rollers spin, gears, hammer slam, star bob)"""
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = 1, frames
    O = bpy.data.objects
    for n, sign in (("Crusher__RollerFront__Steel", 1), ("Crusher__RollerBack__Steel", -1), ("Crusher__GearL__SteelLight", 1), ("Crusher__GearR__SteelLight", 1)):
        o = O[n]
        for f in (1, frames + 1):
            o.rotation_euler[0] = sign * (f - 1) / frames * 2 * math.pi
            o.keyframe_insert("rotation_euler", index=0, frame=f)
    h = O["Forge__Hammer__Steel"]
    z0 = h.location.z
    for f, dz in ((1, 0), (int(frames * 0.45), 0.6), (int(frames * 0.6), -3.2), (int(frames * 0.7), -3.2), (frames, 0)):
        h.location.z = z0 + dz
        h.keyframe_insert("location", index=2, frame=f)
    s = O["StarAnvil__Star__Gold"]
    sz = s.location.z
    for f in range(1, frames + 1, max(1, frames // 4)):
        s.location.z = sz + 0.5 * math.sin((f - 1) / frames * 2 * math.pi)
        s.rotation_euler[2] = (f - 1) / frames * 2 * math.pi
        s.keyframe_insert("location", index=2, frame=f)
        s.keyframe_insert("rotation_euler", index=2, frame=f)
    for fc in [fc for a in bpy.data.actions for fc in getattr(a, "fcurves", [])]:
        for k in fc.keyframe_points:
            k.interpolation = "LINEAR"

def export_fbx(path):
    for o in bpy.data.objects:
        o.select_set(o.type in ("MESH", "EMPTY") and not o.name.startswith("Plane"))
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, apply_unit_scale=True, apply_scale_options="FBX_SCALE_ALL",
                             axis_forward="-Z", axis_up="Y", object_types={"MESH", "EMPTY"}, use_mesh_modifiers=True,
                             mesh_smooth_type="FACE", bake_anim=False, add_leaf_bones=False)

if __name__ == "__main__":
    args = sys.argv
    build()
    print("\n".join(stats()))
    if "--export" in args:
        export_fbx(os.path.join(OUT, "SF_Machines.fbx"))
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "SF_Machines.blend"))
        print("exported")
    if "--render" in args:
        setup_render(1100, 520, 24)
        bpy.context.scene.render.filepath = os.path.join(OUT, "preview_lineup.png")
        bpy.ops.render.render(write_still=True)
        print("rendered")
    if "--anim" in args:
        setup_render(640, 320, 12)
        n = 16
        animate(n)
        bpy.context.scene.render.filepath = os.path.join(OUT, "anim_")
        bpy.context.scene.render.image_settings.file_format = "PNG"
        bpy.ops.render.render(animation=True)
        print("anim rendered")
