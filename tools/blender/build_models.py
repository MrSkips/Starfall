"""
Starfall Forge - ALL gameplay models in one FBX (machines + plot props + meteors).
Run headless:  python3 build_models.py [--export] [--render]

Reuses the helpers + the four machines from build_machines.py, then adds:
  plot props : Conveyor, Bellows, CarryBoots1, Pad (purchase pad), Sign (plot sign frame + posts)
  meteors    : MeteorNormal, MeteorMolten, MeteorFrozen, MeteorCharged, MeteorCosmic, Starheart
Same rules: every part is its own object <Model>__<Part>__<MatKey>; no textures; Roblox assigns
Material + Color from MatKey (tools/ApplyModels.luau). Units: 1 unit = 1 stud. -Y = model front.
"""
import bpy, bmesh, math, os, sys, random
from mathutils import Vector, Matrix

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_machines as BM
from build_machines import box, cyl, frustum, star4, part, root, apply_mods, boolean, srgb

OUT = BM.OUT
BM.PALETTE.update({
    "Leather": ("9B5B3A", 0, .7, 0), "Wood": ("C98A4E", 0, .7, 0), "WoodDark": ("8A5A34", 0, .7, 0),
    "Boot": ("4FA3FF", 0, .45, 0), "Teal": ("64DFD1", 0, .4, 5), "Green": ("50DC78", 0, .4, 4),
    "RockGrey": ("7D7A85", 0, .85, 0), "RockDark": ("4A4652", 0, .85, 0), "Basalt": ("3B3540", 0, .75, 0),
    "Lava": ("FF6A1E", 0, .5, 9), "IceRock": ("9FC9E0", 0, .5, 0), "Ice": ("BDEBFF", 0, .1, 1.2),
    "ChargedRock": ("3E4A66", 0, .7, 0), "Bolt": ("FFE14A", 0, .4, 7), "CosmicRock": ("3A2A5E", 0, .6, 0),
    "CosmicGlow": ("B07CFF", 0, .4, 7),
})
rng = random.Random(7)

# ---------------------------------------------------------------- extra mesh helpers
def mesh_obj(name, bm, mat, bevel=0.0, seg=1, smooth=False):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    return BM._finish(o, mat, bevel, seg, smooth)

def rock_bm(radius, subdiv=1, jitter=0.16, squash=0.85, seed=0):
    r = random.Random(seed)
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=radius)
    for v in bm.verts:
        v.co *= 1 + r.uniform(-jitter, jitter)
        v.co.z *= squash
    bm.normal_update()
    return bm

def inset_patches(src_bm, frac, seed, lift=0.03, shrink=0.7, pick=None):
    """copy a fraction of src faces as slightly raised, shrunken patches (glow veins, spots, frost)"""
    r = random.Random(seed)
    out = bmesh.new()
    for f in src_bm.faces:
        if (pick(f) if pick else r.random() < frac):
            c = f.calc_center_median()
            n = f.normal
            vs = [out.verts.new(c + (v.co - c) * shrink + n * lift) for v in f.verts]
            out.faces.new(vs)
    return out

def crystal(bm, base, direction, length, radius, sides=6):
    """pointed prism (crystal) from base along direction"""
    d = Vector(direction).normalized()
    q = d.to_track_quat("Z", "Y")
    M = Matrix.Translation(base) @ q.to_matrix().to_4x4()
    body = length * 0.7
    ring0, ring1 = [], []
    for i in range(sides):
        a = i * 2 * math.pi / sides
        p = Vector((math.cos(a) * radius, math.sin(a) * radius, 0))
        ring0.append(bm.verts.new(M @ (p * 0.85)))
        ring1.append(bm.verts.new(M @ (p + Vector((0, 0, body)))))
    tip = bm.verts.new(M @ Vector((0, 0, length)))
    bm.faces.new(ring0[::-1])
    for i in range(sides):
        j = (i + 1) % sides
        bm.faces.new((ring0[i], ring0[j], ring1[j], ring1[i]))
        bm.faces.new((ring1[i], ring1[j], tip))

def fib_dirs(n, seed):
    """n well-spread directions, biased away from straight down"""
    r = random.Random(seed)
    out = []
    off = r.uniform(0, 6.28)
    for i in range(n):
        z = 0.95 - 1.45 * (i + 0.5) / n
        rad = math.sqrt(max(0, 1 - z * z))
        a = off + i * 2.39996
        out.append(Vector((math.cos(a) * rad, math.sin(a) * rad, z)).normalized())
    return out

def torus(R, r, loc, mat, rot=(0, 0, 0), major=32, minor=8, name="t"):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, major_segments=major, minor_segments=minor, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    return BM._finish(o, mat, 0, 1)

# ---------------------------------------------------------------- plot props
def conveyor(R):
    M = "Conveyor"
    L, W = 11.0, 4.0
    part(M, "Legs", [box((0.5, 0.5, 1.0), (sx * 1.7, sy * 4.4, 0.5), "Steel", 0.08) for sx in (-1, 1) for sy in (-1, 0, 1)], R)
    part(M, "Frame", [box((0.45, L, 0.9), (sx * 2.05, 0, 1.45), "Cream", 0.15) for sx in (-1, 1)], R)
    part(M, "Belt", [box((3.5, L - 1.2, 0.35), (0, 0, 1.65), "Dark", 0.08)], R)
    chev = []
    for k in range(6):
        y = -4.1 + k * 1.65
        for s in (-1, 1):
            chev.append(box((1.35, 0.32, 0.08), (s * 0.55, y + 0.25, 1.86), "Yellow", 0.02, 1, rot=(0, 0, s * math.radians(35))))
    part(M, "Chevrons", chev, R)
    for side, y in (("Front", -(L / 2 - 0.55)), ("Back", L / 2 - 0.55)):
        bits = [cyl(0.55, 3.6, (0, y, 1.4), "SteelLight", "X", 16, 0.05)]
        bits += [box((3.62, 0.18, 0.18), (0, y + math.cos(a) * 0.55, 1.4 + math.sin(a) * 0.55), "SteelLight", 0.0, 1) for a in (0, math.pi / 2, math.pi, 1.5 * math.pi)]
        part(M, f"Roller{side}", bits, R, pivot=(0, y, 1.4))
    # intake bin at the crater end (front marker)
    part(M, "Bin", [frustum((3.2, 1.6), (4.2, 2.6), 1.9, 3.3, "Red", 0.25)], R, )
    bpy.data.objects[f"{M}__Bin__Red"].location.y -= L / 2 - 1.2
    part(M, "Bolts", [cyl(0.16, 0.12, (sx * 2.3, sy, 1.45), "Steel", "X", 8, 0.02) for sx in (-1, 1) for sy in (-4, -1.3, 1.3, 4)], R)

def bellows(R):
    M = "Bellows"
    part(M, "Base", [box((5.0, 3.6, 0.5), (0, 0, 0.25), "WoodDark", 0.12)], R)
    part(M, "BoardBottom", [box((4.4, 3.0, 0.35), (0, 0, 0.7), "Wood", 0.1)], R)
    # accordion bag: stacked rounded slabs, pivot at its bottom so Roblox can pump it (Size.Y)
    folds = []
    for k in range(4):
        w = 3.9 - (k % 2) * 0.5
        folds.append(box((w, 2.6 - (k % 2) * 0.4, 0.45), (0, 0, 1.1 + k * 0.42), "Leather", 0.16, 2))
    part(M, "Bag", folds, R, pivot=(0, 0, 0.88))
    # top board hinged at the back edge (+Y), with handle
    part(M, "BoardTop", [box((4.4, 3.0, 0.35), (0, 0, 2.95), "Wood", 0.1)], R, pivot=(0, 1.5, 2.95))
    part(M, "Handle", [box((0.35, 0.35, 1.3), (s * 1.2, 1.2, 3.75), "WoodDark", 0.06) for s in (-1, 1)] +
         [cyl(0.22, 2.8, (0, 1.2, 4.35), "WoodDark", "X", 10, 0.04)], R, pivot=(0, 1.5, 2.95))
    # nozzle to the smelter: along -X
    part(M, "Nozzle", [cyl(0.55, 1.6, (-2.9, -0.2, 1.5), "Steel", "X", 14, 0.06, r2=0.3),
                       cyl(0.32, 2.4, (-4.7, -0.2, 1.5), "Steel", "X", 12, 0.04)], R)
    part(M, "Bands", [cyl(0.62, 0.25, (-2.3, -0.2, 1.5), "Cream", "X", 14, 0.04), cyl(0.4, 0.22, (-5.6, -0.2, 1.5), "Cream", "X", 12, 0.03)], R)

def carry_boots(R):
    M = "CarryBoots1"
    part(M, "Pedestal", [box((3.4, 3.4, 0.5), (0, 0, 0.25), "Cream", 0.15), box((2.6, 2.6, 0.35), (0, 0, 2.2), "Cream", 0.12)], R)
    part(M, "PedestalRed", [box((2.8, 2.8, 1.5), (0, 0, 1.25), "Red", 0.25, 2)], R)
    part(M, "Ring", [torus(1.45, 0.12, (0, 0, 2.45), "Teal", major=28, minor=6)], R)
    boots, soles, wings = [], [], []
    for s in (-1, 1):
        x = s * 0.55
        boots.append(box((0.8, 0.85, 1.1), (x, 0.15, 3.35), "Boot", 0.2, 2))      # shaft
        boots.append(box((0.8, 1.45, 0.55), (x, -0.15, 2.95), "Boot", 0.22, 2))   # foot
        soles.append(box((0.88, 1.55, 0.2), (x, -0.15, 2.62), "Cream", 0.07))
        soles.append(box((0.86, 0.95, 0.18), (x, 0.15, 3.9), "Cream", 0.06))       # cuff
        w = star4(0.42, 0.14, 0.12, (x + s * 0.48, 0.2, 3.45), "Gold")
        w.rotation_euler = (0, 0, math.pi / 2)
        wings.append(w)
    piv = (0, 0, 3.2)
    part(M, "Boots", boots, R, pivot=piv)
    part(M, "Soles", soles, R, pivot=piv)
    part(M, "Wings", wings, R, pivot=piv)

def pad(R):
    M = "Pad"
    part(M, "Base", [box((7, 7, 0.45), (0, 0, 0.225), "Steel", 0.15)], R)
    rim = box((6.6, 6.6, 0.25), (0, 0, 0.55), "Cream", 0.08)
    boolean(rim, box((5.6, 5.6, 1), (0, 0, 0.55), "Cream", 0))
    part(M, "Rim", [rim], R)
    part(M, "Top", [box((5.5, 5.5, 0.2), (0, 0, 0.52), "Green", 0.06)], R)
    s = star4(1.7, 0.6, 0.18, (0, 0, 0.7), "Cream")
    s.rotation_euler = (math.pi / 2, 0, math.pi / 4)
    part(M, "Star", [s], R)

def sign(R):
    M = "Sign"
    # board centre at z=9 (matches the greybox Sign part 14x4x1, which stays as the text surface)
    frame = box((15.4, 1.6, 5.4), (0, 0, 9), "Red", 0.3, 2)
    boolean(frame, box((14.05, 3, 4.05), (0, 0, 9), "Red", 0))
    part(M, "Frame", [frame], R)
    part(M, "Posts", [box((1.0, 1.0, 9.6), (s * 6.0, 0.35, 4.8), "WoodDark", 0.15) for s in (-1, 1)], R)
    part(M, "Feet", [box((1.8, 1.8, 0.5), (s * 6.0, 0.35, 0.25), "Steel", 0.12) for s in (-1, 1)], R)
    part(M, "Cap", [box((16.2, 2.2, 0.6), (0, 0, 12.0), "Cream", 0.2)], R)
    part(M, "Star", [star4(1.3, 0.45, 0.45, (0, 0, 13.6), "Gold")], R)

# ---------------------------------------------------------------- meteors (pivot = centre, ~diameter 2)
def meteor(R, name, rock, accent, seed):
    bm = rock_bm(1.0, 2, 0.12, 0.86, seed)
    if accent == "spots":
        a = inset_patches(bm, 0.18, seed, 0.02, 0.62)
        part(name, "Spots", [mesh_obj("s", a, "RockDark")], R, pivot=(0, 0, 0))
    elif accent == "lava":
        a = inset_patches(bm, 0.38, seed, 0.03, 0.74)
        part(name, "Veins", [mesh_obj("v", a, "Lava")], R, pivot=(0, 0, 0))
    elif accent == "ice":
        c = bmesh.new()
        r = random.Random(seed)
        for d in fib_dirs(7, seed):
            crystal(c, d * 0.72, d + Vector((r.uniform(-.3, .3), r.uniform(-.3, .3), 0.2)), r.uniform(0.65, 1.0), r.uniform(0.16, 0.24))
        part(name, "Crystals", [mesh_obj("c", c, "Ice")], R, pivot=(0, 0, 0))
        a = inset_patches(bm, 0.3, seed + 1, 0.02, 0.7)
        part(name, "Frost", [mesh_obj("f", a, "Cream")], R, pivot=(0, 0, 0))
    elif accent == "bolt":
        c = bmesh.new()
        r = random.Random(seed)
        for d in fib_dirs(6, seed):
            crystal(c, d * 0.75, d, r.uniform(0.55, 0.85), r.uniform(0.13, 0.19), sides=4)
        part(name, "Shards", [mesh_obj("c", c, "Bolt")], R, pivot=(0, 0, 0))
        a = inset_patches(bm, 0.22, seed + 2, 0.03, 0.55)
        part(name, "Sparks", [mesh_obj("p", a, "Bolt")], R, pivot=(0, 0, 0))
    elif accent == "cosmic":
        a = inset_patches(bm, 0.35, seed, 0.03, 0.7)
        part(name, "Glow", [mesh_obj("g", a, "CosmicGlow")], R, pivot=(0, 0, 0))
        part(name, "Ring", [torus(1.45, 0.07, (0, 0, 0), "Teal", rot=(math.radians(68), math.radians(18), 0), major=36, minor=5)], R, pivot=(0, 0, 0))
    part(name, "Rock", [mesh_obj("r", bm, rock)], R, pivot=(0, 0, 0))

def starheart(R):
    name = "Starheart"
    core = bmesh.new()
    bmesh.ops.create_icosphere(core, subdivisions=1, radius=0.62)
    part(name, "Core", [mesh_obj("core", core, "Gold")], R, pivot=(0, 0, 0))
    sp = bmesh.new()
    for d in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
        crystal(sp, Vector(d) * 0.3, d, 1.15, 0.26, sides=4)
    for d in ((1, 1, 1), (-1, 1, 1), (1, -1, 1), (-1, -1, 1), (1, 1, -1), (-1, 1, -1), (1, -1, -1), (-1, -1, -1)):
        v = Vector(d).normalized()
        crystal(sp, v * 0.35, v, 0.8, 0.16, sides=4)
    part(name, "Spikes", [mesh_obj("sp", sp, "Gold")], R, pivot=(0, 0, 0))
    # cracked rock shell chunks hugging the core
    shell = []
    r = random.Random(11)
    for k in range(6):
        a = k * math.pi / 3 + 0.3
        bm = rock_bm(0.42, 1, 0.2, 0.8, 30 + k)
        o = mesh_obj("sh", bm, "RockDark")
        o.location = (math.cos(a) * 0.62, math.sin(a) * 0.62, r.uniform(-0.45, 0.2))
        shell.append(o)
    part(name, "Shell", shell, R, pivot=(0, 0, 0))
    part(name, "Ring", [torus(1.55, 0.08, (0, 0, 0), "Cream", rot=(math.radians(75), 0, 0), major=36, minor=5)], R, pivot=(0, 0, 0))

PROPS = [("Conveyor", conveyor), ("Bellows", bellows), ("CarryBoots1", carry_boots), ("Pad", pad), ("Sign", sign)]
METEORS = [("MeteorNormal", "RockGrey", "spots"), ("MeteorMolten", "Basalt", "lava"), ("MeteorFrozen", "IceRock", "ice"),
           ("MeteorCharged", "ChargedRock", "bolt"), ("MeteorCosmic", "CosmicRock", "cosmic")]

def build_all():
    BM.build()  # machines at x = -21..21, y = 0
    for k, (n, fn) in enumerate(PROPS):
        r = root(n, 0)
        fn(r)
        r.location = (-24 + k * 12, 22, 0)
    for k, (n, rock, acc) in enumerate(METEORS):
        r = root(n, 0)
        meteor(r, n, rock, acc, 100 + k)
        r.location = (-12 + k * 5, -14, 1.6)
    r = root("Starheart", 0)
    starheart(r)
    r.location = (16, -14, 2.2)

def heights():
    out = {}
    for r in [o for o in bpy.data.objects if o.type == "EMPTY"]:
        zs = []
        tris = 0
        for c in r.children:
            for v in c.data.vertices:
                zs.append((c.matrix_world @ v.co).z)
            tris += sum(len(p.vertices) - 2 for p in c.data.polygons)
        out[r.name] = (round(max(zs) - min(zs), 3), len(r.children), tris)
    return out

if __name__ == "__main__":
    build_all()
    bpy.context.view_layer.update()
    for k, v in heights().items():
        print(f"{k}: height {v[0]}  parts {v[1]}  tris {v[2]}")
    if "--export" in sys.argv:
        BM.export_fbx(os.path.join(OUT, "SF_Models.fbx"))
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "SF_Models.blend"))
        print("exported")
    if "--render" in sys.argv:
        BM.setup_render(1200, 600, 20)
        cam = bpy.context.scene.camera
        groups = {
            "machines": ["Crusher", "Smelter", "Forge", "StarAnvil"],
            "props": [n for n, _ in PROPS],
            "meteors": [n for n, _, _ in METEORS] + ["Starheart"],
        }
        def shot(key, loc, target, lens, fname):
            for r in [o for o in bpy.data.objects if o.type == "EMPTY"]:
                for c in r.children:
                    c.hide_render = r.name not in groups[key]
            cam.location = loc
            cam.data.lens = lens
            cam.rotation_euler = (Vector(target) - cam.location).to_track_quat("-Z", "Y").to_euler()
            bpy.context.scene.render.filepath = os.path.join(OUT, fname)
            bpy.ops.render.render(write_still=True)
        pass
        shot("props", (0, -30, 30), (0, 22, 3), 28, "preview_props.png")
        shot("meteors", (2, -48, 12), (2, -14, 1.8), 30, "preview_meteors.png")
        print("rendered")
