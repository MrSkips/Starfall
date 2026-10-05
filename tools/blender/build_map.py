"""
Starfall Forge - crater map (visual meshes), CON-01 "Sunlit Toy Foundry".
Run headless:  python3 build_map.py [--export] [--render]

Gameplay collision stays in Roblox as simple invisible parts built from the SAME numbers
(see SPEC below + ServerStorage.Tools.ApplyMap). These meshes are visual only, so they
must sit exactly on those surfaces:
  crater floor top z=0 (r<146) . ramp r=105->145 rising 0->12 . walkway r 145->147 at 13
  rim plateau top z=13 (r 146..264) . plot pads 56x56 top z=14 centred r=175 . boundary r~268
Object names: Map__<Name>__<MatKey>  (Roblox assigns Material+Color from MatKey; no baked textures).
Units: 1 Blender unit = 1 stud. Blender XY = Roblox XZ ground plane, Z = up.
"""
import bpy, bmesh, math, random, sys, os
from mathutils import Vector, Matrix

OUT = os.path.dirname(os.path.abspath(__file__))
SPEC = dict(PLOTS=8, PLOT_R=175, PLOT_SIZE=56, RIM_TOP=13, PAD_TOP=14, CRATER_R=146, RAMP_IN=105, RAMP_OUT=145,
            RAMP_W=20, RAMP_TOP=12, PLATEAU_OUT=264, PATH_R=218, PATH_W=8)
rng = random.Random(7)

PALETTE = {  # key: (hex, metallic, roughness, emission)
    "Grass": ("79C94A", 0, .8, 0), "GrassDark": ("5FA83B", 0, .8, 0), "Slate": ("687B91", 0, .75, 0),
    "SlateDark": ("55657A", 0, .75, 0), "Floor": ("7A8293", 0, .85, 0), "FloorDark": ("6A7180", 0, .85, 0),
    "Path": ("DB9856", 0, .8, 0), "Cream": ("FFF0CF", 0, .6, 0), "Wood": ("C98A4E", 0, .7, 0),
    "WoodDark": ("8A5A34", 0, .7, 0), "Leaf": ("6DBE45", 0, .7, 0), "LeafDark": ("4E9E35", 0, .7, 0),
    "Rock": ("8C96A3", 0, .8, 0), "Basalt": ("3B3540", 0, .7, 0), "Ember": ("FF6A1E", 0, .5, 8),
    "Steel": ("344658", .5, .4, 0), "LampGlow": ("FFE08A", 0, .4, 6), "FlowerY": ("FFD24A", 0, .6, 0),
    "FlowerP": ("F27B9B", 0, .6, 0), "Red": ("D95542", 0, .55, 0),
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

# ------------------------------------------------------------------ geometry accumulation
# Every piece is added to a bmesh bucket keyed by (object name, material). Buckets become one
# object each at the end -> few, big meshes (good for Roblox draw calls), split per sector.
BUCKETS = {}

def bucket(name, mat):
    k = (name, mat)
    if k not in BUCKETS:
        BUCKETS[k] = bmesh.new()
    return BUCKETS[k]

def add_mesh(name, mat, me_bm, matrix=Matrix.Identity(4)):
    tmp = bpy.data.meshes.new("tmp")
    me_bm.to_mesh(tmp)
    me_bm.free()
    tmp.transform(matrix)
    bucket(name, mat).from_mesh(tmp)
    bpy.data.meshes.remove(tmp)

def bevelled_box(size, bevel=0.2, seg=2):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    if bevel > 0:
        b = min(bevel, min(size) * 0.45)
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=b, segments=seg, affect="EDGES", profile=0.5)
    return bm

def box(name, mat, size, loc, rotz=0.0, bevel=0.2, seg=2, rotx=0.0, roty=0.0):
    m = Matrix.Translation(loc) @ Matrix.Rotation(rotz, 4, "Z") @ Matrix.Rotation(roty, 4, "Y") @ Matrix.Rotation(rotx, 4, "X")
    add_mesh(name, mat, bevelled_box(size, bevel, seg), m)

def prism(name, mat, sides, r, h, loc, rotz=0.0):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=sides, radius1=r, radius2=r, depth=h)
    add_mesh(name, mat, bm, Matrix.Translation(loc) @ Matrix.Rotation(rotz, 4, "Z"))

def rock(name, mat, r, loc, squash=0.75, jitter=0.28, subd=1):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subd, radius=r)
    for v in bm.verts:
        v.co *= 1 + rng.uniform(-jitter, jitter)
        v.co.z *= squash
    add_mesh(name, mat, bm, Matrix.Translation(loc) @ Matrix.Rotation(rng.uniform(0, 6.28), 4, "Z"))

def annulus(name, mat, r0, r1, a0, a1, z0, z1, seg=None):
    n = seg or max(4, int((a1 - a0) * r1 / 6))
    bm = bmesh.new()
    ti, to, bi, bo = [], [], [], []
    for i in range(n + 1):
        a = a0 + (a1 - a0) * i / n
        c, s = math.cos(a), math.sin(a)
        ti.append(bm.verts.new((c * r0, s * r0, z1))); to.append(bm.verts.new((c * r1, s * r1, z1)))
        bi.append(bm.verts.new((c * r0, s * r0, z0))); bo.append(bm.verts.new((c * r1, s * r1, z0)))
    for i in range(n):
        bm.faces.new((ti[i], to[i], to[i + 1], ti[i + 1]))
        bm.faces.new((bi[i + 1], bo[i + 1], bo[i], bi[i]))
        bm.faces.new((to[i], bo[i], bo[i + 1], to[i + 1]))
        bm.faces.new((ti[i + 1], bi[i + 1], bi[i], ti[i]))
    bm.faces.new((ti[0], bi[0], bo[0], to[0]))
    bm.faces.new((to[n], bo[n], bi[n], ti[n]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    add_mesh(name, mat, bm)

def polar(r, a, z=0.0):
    return Vector((math.cos(a) * r, math.sin(a) * r, z))

# ------------------------------------------------------------------ map pieces
def plot_angle(i):
    return i * 2 * math.pi / SPEC["PLOTS"]

def ang_dist(a, b):
    return abs(math.atan2(math.sin(a - b), math.cos(a - b)))

def build_floor():
    S = SPEC
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=96, radius1=S["CRATER_R"] + 2, radius2=S["CRATER_R"] + 2, depth=4)
    add_mesh("Floor", "Floor", bm, Matrix.Translation((0, 0, -2)))
    # stone plates
    for _ in range(90):
        r, a = rng.uniform(34, 138), rng.uniform(0, 6.28)
        if min(ang_dist(a, plot_angle(i)) * r for i in range(S["PLOTS"])) < 13 and r > 100:
            continue
        prism("FloorPlates", rng.choice(["FloorDark", "FloorDark", "SlateDark"]), 6, rng.uniform(2.2, 5.5), 0.16, polar(r, a, 0.06), rng.uniform(0, 1))
    # impact scar + lava cracks around the central meteorite
    prism("Scorch", "Basalt", 40, 28, 0.12, (0, 0, 0.06))
    for k in range(12):
        a = k * math.pi / 6 + rng.uniform(-0.2, 0.2)
        L = rng.uniform(6, 16)
        box("LavaCracks", "Ember", (L, 0.7, 0.14), polar(24 + L / 2 - 4, a, 0.1), a, 0.05, 1)
    # meteorite: faceted rock with glowing inset patches
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=2, radius=11)
    for v in bm.verts:
        v.co *= 1 + rng.uniform(-0.14, 0.14)
        v.co.z *= 0.82
    bm.normal_update()
    ember = bmesh.new()
    for f in list(bm.faces):
        if rng.random() < 0.13:
            c = f.calc_center_median()
            n = f.normal
            vs = [ember.verts.new(c + (v.co - c) * 0.72 + n * 0.12) for v in f.verts]
            ember.faces.new(vs)
    M = Matrix.Translation((0, 0, 5.5)) @ Matrix.Rotation(0.4, 4, "Z")
    add_mesh("Meteorite", "Basalt", bm, M)
    add_mesh("MeteoriteLava", "Ember", ember, M)
    for _ in range(12):
        r, a = rng.uniform(13, 27), rng.uniform(0, 6.28)
        rock("Debris", rng.choice(["Basalt", "Rock"]), rng.uniform(1.2, 3.0), polar(r, a, 0.6))
    for _ in range(26):
        r, a = rng.uniform(34, 132), rng.uniform(0, 6.28)
        if min(ang_dist(a, plot_angle(i)) * r for i in range(S["PLOTS"])) < 14 and r > 95:
            continue
        rock("CraterRocks", "Rock", rng.uniform(1.2, 3.2), polar(r, a, 0.7))

def build_sector(i):
    S = SPEC
    pa = plot_angle(i)
    a0, a1 = pa - math.pi / S["PLOTS"], pa + math.pi / S["PLOTS"]
    sid = str(i + 1)
    top = S["RIM_TOP"]
    # rim plateau (grass) + dirt path ring + spoke to the plot back edge
    annulus("Grass" + sid, "Grass", S["CRATER_R"], S["PLATEAU_OUT"] + 8, a0, a1, top - 3, top)
    annulus("Path" + sid, "Path", S["PATH_R"] - S["PATH_W"] / 2, S["PATH_R"] + S["PATH_W"] / 2, a0, a1, top, top + 0.08)
    back = S["PLOT_R"] + S["PLOT_SIZE"] / 2
    box("Path" + sid, "Path", (S["PATH_R"] - back - S["PATH_W"] / 2 + 0.5, S["PATH_W"], 0.14), polar((back + S["PATH_R"] - S["PATH_W"] / 2) / 2, pa, top + 0.05), pa, 0.04, 1)

    # crater wall: stacked slate blocks along r=145, gap for the ramp
    arc = (a1 - a0) * S["CRATER_R"]
    t = 0.0
    while t < arc:
        w = rng.uniform(5, 9)
        a = a0 + (t + w / 2) / S["CRATER_R"]
        t += w
        if ang_dist(a, pa) * S["CRATER_R"] < S["RAMP_W"] / 2 + 3:
            continue
        d1 = rng.uniform(4, 7)
        h1 = rng.uniform(4.5, 7.5)
        box("Cliff" + sid, rng.choice(["Slate", "Slate", "SlateDark"]), (w + 0.6, d1, h1), polar(S["RAMP_OUT"] - 0.3 + d1 / 2, a, h1 / 2), a, 0.45, 2)
        h2 = top - h1 + rng.uniform(0.3, 1.6)
        d2 = rng.uniform(4, 8)
        box("Cliff" + sid, rng.choice(["Slate", "SlateDark", "Slate"]), (w + 0.4, d2, h2), polar(S["RAMP_OUT"] + 0.4 + d2 / 2, a + rng.uniform(-0.004, 0.004), h1 + h2 / 2), a, 0.45, 2)
        box("CliffGrass" + sid, "Grass", (w + 0.8, d2 + 0.8, 0.7), polar(S["RAMP_OUT"] + 0.4 + d2 / 2, a, h1 + h2 + 0.2), a, 0.25, 2)
        if rng.random() < 0.35:  # little boulder at the foot
            rock("Cliff" + sid, "Rock", rng.uniform(1.0, 2.0), polar(S["RAMP_OUT"] - 1.2, a + rng.uniform(-0.01, 0.01), 0.6))

    # ramp: slate wedge body + plank deck + rails, walkway onto the rim
    L = S["RAMP_OUT"] - S["RAMP_IN"]
    slope = math.atan2(S["RAMP_TOP"], L)
    bm = bmesh.new()
    hw = S["RAMP_W"] / 2 + 0.6
    P = [(0, -hw, 0), (L, -hw, 0), (L, -hw, S["RAMP_TOP"]), (0, hw, 0), (L, hw, 0), (L, hw, S["RAMP_TOP"])]
    v = [bm.verts.new(p) for p in P]
    for f in ((0, 1, 2), (3, 5, 4), (0, 3, 4, 1), (1, 4, 5, 2), (0, 2, 5, 3)):
        bm.faces.new([v[k] for k in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    rampM = Matrix.Translation(polar(S["RAMP_IN"], pa)) @ Matrix.Rotation(pa, 4, "Z")
    add_mesh("RampBase" + sid, "SlateDark", bm, rampM @ Matrix.Translation((0, 0, -0.35)))
    n = 18
    for k in range(n):
        u = (k + 0.5) / n * L
        box("RampDeck" + sid, "Wood" if k % 2 == 0 else "WoodDark", (L / n * 0.96, S["RAMP_W"], 0.45),
            (rampM @ Vector((u, 0, u * math.tan(slope) + 0.05))), pa, 0.08, 1, roty=-slope)
    for side in (-1, 1):
        for k in range(6):
            u = k / 5 * L
            box("RampRails" + sid, "WoodDark", (0.7, 0.7, 3.2), rampM @ Vector((u, side * (S["RAMP_W"] / 2 + 0.2), u * math.tan(slope) + 1.6)), pa, 0.12, 1)
        mid = rampM @ Vector((L / 2, side * (S["RAMP_W"] / 2 + 0.2), L / 2 * math.tan(slope) + 2.8))
        box("RampRails" + sid, "Wood", (L / math.cos(slope) + 0.6, 0.45, 0.45), mid, pa, 0.1, 1, roty=-slope)
    box("RampDeck" + sid, "Wood", (2.6, S["RAMP_W"], 0.5), polar(S["RAMP_OUT"] + 1.0, pa, top - 0.2), pa, 0.08, 1)

    # plot pad (56x56, top z=14): path deck, cream border, corner posts
    pc = polar(S["PLOT_R"], pa)
    box("PlotPad" + sid, "Path", (S["PLOT_SIZE"], S["PLOT_SIZE"], 1.4), pc + Vector((0, 0, S["PAD_TOP"] - 0.7)), pa, 0.35, 2)
    hs = S["PLOT_SIZE"] / 2
    R = Matrix.Rotation(pa, 4, "Z")
    for (x, y, sx, sy) in ((0, -hs + 0.5, S["PLOT_SIZE"], 1.0), (0, hs - 0.5, S["PLOT_SIZE"], 1.0), (-hs + 0.5, 0, 1.0, S["PLOT_SIZE"]), (hs - 0.5, 0, 1.0, S["PLOT_SIZE"])):
        box("PlotTrim" + sid, "Cream", (sx, sy, 0.35), pc + R @ Vector((x, y, 0)) + Vector((0, 0, S["PAD_TOP"] + 0.12)), pa, 0.12, 1)
    for x in (-hs + 0.8, hs - 0.8):
        for y in (-hs + 0.8, hs - 0.8):
            box("PlotTrim" + sid, "Cream", (1.6, 1.6, 2.4), pc + R @ Vector((x, y, 0)) + Vector((0, 0, S["PAD_TOP"] + 1.1)), pa, 0.3, 2)
    # fence along the back (gap for the path) and the sides (open towards the crater)
    def fence_run(p0, p1, gap_mid=None, gap=0.0):
        seg = (p1 - p0)
        length = seg.length
        dirv = seg.normalized()
        ang = math.atan2(dirv.y, dirv.x)
        k = 0.0
        while k <= length + 0.01:
            pos = p0 + dirv * k
            if gap_mid is None or (pos - gap_mid).length > gap:
                box("Fence" + sid, "WoodDark", (0.6, 0.6, 2.6), pos + Vector((0, 0, S["PAD_TOP"] + 1.3)), ang, 0.1, 1)
                if k + 6.9 <= length + 0.01:
                    nxt = p0 + dirv * (k + 7)
                    if gap_mid is None or (nxt - gap_mid).length > gap:
                        for zz in (0.9, 1.9):
                            box("Fence" + sid, "Wood", (7, 0.3, 0.35), (pos + nxt) / 2 + Vector((0, 0, S["PAD_TOP"] + zz)), ang, 0.05, 1)
            k += 7
    c = lambda x, y: pc + R @ Vector((x, y, 0))
    fence_run(c(hs - 1.5, -hs + 1.5), c(hs - 1.5, hs - 1.5), gap_mid=c(hs - 1.5, 0), gap=5)
    fence_run(c(-hs + 8, -hs + 1.5), c(hs - 1.5, -hs + 1.5))
    fence_run(c(-hs + 8, hs - 1.5), c(hs - 1.5, hs - 1.5))

    # lamps on the path ring (2 per sector)
    for off in (-0.35, 0.35):
        a = pa + off
        p = polar(S["PATH_R"] + S["PATH_W"] / 2 + 1.5, a)
        box("Lamps" + sid, "Steel", (0.7, 0.7, 7), p + Vector((0, 0, top + 3.5)), a, 0.15, 1)
        box("LampGlow" + sid, "LampGlow", (1.6, 1.6, 1.6), p + Vector((0, 0, top + 7.6)), a, 0.3, 2)
        box("Lamps" + sid, "Steel", (2.0, 2.0, 0.4), p + Vector((0, 0, top + 8.6)), a, 0.1, 1)

    # trees / bushes / rocks / flowers on the plateau (keep off plots, paths, ramp mouths)
    def free(r, a, pad=4):
        local = Matrix.Rotation(-pa, 4, "Z") @ (polar(r, a) - pc)
        if abs(local.x) < hs + pad and abs(local.y) < hs + pad:
            return False
        if abs(r - S["PATH_R"]) < S["PATH_W"] / 2 + 3:
            return False
        if ang_dist(a, pa) * r < S["PATH_W"] / 2 + 3 and back - 2 < r < S["PATH_R"]:
            return False
        return r > S["CRATER_R"] + 6
    placed = 0
    tries = 0
    while placed < 9 and tries < 200:
        tries += 1
        r, a = rng.uniform(150, S["PLATEAU_OUT"] - 4), rng.uniform(a0 + 0.02, a1 - 0.02)
        if not free(r, a):
            continue
        p = polar(r, a, top)
        h = rng.uniform(4, 6.5)
        box("Trunks" + sid, "WoodDark", (1.4, 1.4, h), p + Vector((0, 0, h / 2)), rng.uniform(0, 1), 0.2, 1)
        leaf = "Leaf" if rng.random() < 0.6 else "LeafDark"
        s1 = rng.uniform(6, 7.5)
        box("Leaves" + sid, leaf, (s1, s1, s1 * 0.8), p + Vector((0, 0, h + s1 * 0.3)), rng.uniform(0, 1.5), 0.9, 2)
        s2 = s1 * rng.uniform(0.6, 0.72)
        box("Leaves" + sid, leaf, (s2, s2, s2 * 0.85), p + Vector((rng.uniform(-.6, .6), rng.uniform(-.6, .6), h + s1 * 0.75 + s2 * 0.3)), rng.uniform(0, 1.5), 0.7, 2)
        placed += 1
    for _ in range(7):
        r, a = rng.uniform(150, S["PLATEAU_OUT"]), rng.uniform(a0, a1)
        if free(r, a, 2):
            s = rng.uniform(2.2, 3.4)
            box("Bushes" + sid, rng.choice(["Leaf", "LeafDark"]), (s, s, s * 0.8), polar(r, a, top + s * 0.35), rng.uniform(0, 1.5), 0.8, 2)
            if rng.random() < 0.7:
                for _ in range(3):
                    box("Flowers" + sid, rng.choice(["FlowerY", "FlowerP"]), (0.6, 0.6, 0.6), polar(r, a, top + s * 0.7) + Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(0, .4))), 0, 0.2, 1)
    for _ in range(4):
        r, a = rng.uniform(150, S["PLATEAU_OUT"]), rng.uniform(a0, a1)
        if free(r, a, 2):
            rock("PlateauRocks" + sid, "Rock", rng.uniform(1.3, 2.6), polar(r, a, top + 0.5))

    # outer mesas: stepped blocky cliffs with grass caps (skyline, CON-01)
    t = 0.0
    arcm = (a1 - a0) * 290
    while t < arcm:
        w = rng.uniform(22, 40)
        a = a0 + (t + w / 2) / 290
        t += w * 0.8
        r = rng.uniform(268, 282)
        z = top - 1
        tiers = rng.randint(2, 4)
        d = rng.uniform(22, 34)
        for k in range(tiers):
            h = rng.uniform(8, 16) if k == 0 else rng.uniform(7, 14)
            ww, dd = w * (1 - 0.18 * k), d * (1 - 0.15 * k)
            rr = r + k * rng.uniform(3, 7)
            box("Mesa" + sid, rng.choice(["Slate", "SlateDark"]), (ww, dd, h), polar(rr + dd / 2, a, z + h / 2), a + math.pi / 2 + rng.uniform(-0.05, 0.05), 0.8, 2)
            z += h
            box("MesaGrass" + sid, "GrassDark" if k % 2 else "Grass", (ww + 0.6, dd + 0.6, 1.0), polar(rr + dd / 2, a, z + 0.3), a + math.pi / 2, 0.4, 2)
            if rng.random() < 0.4:  # a tree on top
                tp = polar(rr + dd / 2 + rng.uniform(-3, 3), a + rng.uniform(-0.01, 0.01), z + 0.8)
                box("Trunks" + sid, "WoodDark", (1.4, 1.4, 4), tp + Vector((0, 0, 2)), 0, 0.2, 1)
                box("Leaves" + sid, "LeafDark", (6, 6, 5), tp + Vector((0, 0, 6)), rng.uniform(0, 1.5), 0.9, 2)

def finalize():
    root = bpy.data.objects.new("Map", None)
    bpy.context.collection.objects.link(root)
    for (name, mat), bm in BUCKETS.items():
        me = bpy.data.meshes.new(f"Map__{name}__{mat}")
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
        bm.to_mesh(me)
        bm.free()
        o = bpy.data.objects.new(me.name, me)
        bpy.context.collection.objects.link(o)
        me.materials.append(material(mat))
        # smooth shading with sharp edges kept (bevels read as soft highlights)
        for p in me.polygons:
            p.use_smooth = True
        try:
            me.set_sharp_from_angle(angle=math.radians(40))
        except Exception:
            pass
        # origin at bbox centre (Roblox pivots/streaming behave better)
        bb = [Vector(c) for c in o.bound_box]
        ctr = sum(bb, Vector()) / 8
        me.transform(Matrix.Translation(-ctr))
        o.location = ctr
        o.parent = root
    # alignment markers for the Roblox importer (deleted after alignment)
    for nm, loc in (("Marker0", (0, 0, 20)), ("Marker1", (SPEC["PLOT_R"], 0, 20))):
        bpy.ops.mesh.primitive_cube_add(size=2, location=loc)
        mk = bpy.context.object
        mk.name = f"Map__{nm}__Red"
        mk.data.materials.append(material("Red"))
        mk.parent = root
    return root

def stats():
    tot = 0
    worst = (0, "")
    for o in bpy.data.objects:
        if o.type == "MESH" and o.name.startswith("Map__"):
            t = sum(len(p.vertices) - 2 for p in o.data.polygons)
            tot += t
            worst = max(worst, (t, o.name))
    n = len([o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("Map__")])
    return f"{n} meshes, {tot} tris total, largest {worst[1]} = {worst[0]} tris"

def setup_render(w, h, samples, cam_loc, target, lens=32):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Medium High Contrast"
    if not sc.world:
        world = bpy.data.worlds.new("Sky")
        world.use_nodes = True
        world.node_tree.nodes["Background"].inputs[0].default_value = srgb("9FD3F0") + [1]
        world.node_tree.nodes["Background"].inputs[1].default_value = 1.0
        sc.world = world
        bpy.ops.object.light_add(type="SUN", rotation=(math.radians(48), math.radians(8), math.radians(-30)))
        bpy.context.object.data.energy = 3.4
        bpy.context.object.data.angle = math.radians(6)
        sc.view_settings.exposure = 0.0
    cam = sc.camera
    if cam is None:
        bpy.ops.object.camera_add()
        cam = bpy.context.object
        sc.camera = cam
    cam.location = cam_loc
    cam.data.lens = lens
    cam.data.clip_end = 3000
    d = Vector(target) - cam.location
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()

def append_machines(plot_index=2):
    """preview only: drop the machine set onto one plot"""
    path = os.path.join(OUT, "SF_Machines.blend")
    if not os.path.exists(path):
        return
    with bpy.data.libraries.load(path) as (src, dst):
        dst.objects = [n for n in src.objects]
    pa = plot_angle(plot_index)
    pc = polar(SPEC["PLOT_R"], pa, SPEC["PAD_TOP"])
    spots = {"Crusher": -18, "Smelter": -6, "Forge": 6, "StarAnvil": 18}
    for o in dst.objects:
        if o is None:
            continue
        bpy.context.collection.objects.link(o)
    for o in dst.objects:
        if o and o.type == "EMPTY" and o.name in spots:
            # plot-local: x along the plot's tangent, machines 16 studs behind centre, fronts face the crater
            R = Matrix.Rotation(pa, 4, "Z")
            local = Vector((16, spots[o.name], 0))
            o.location = pc + R @ local
            o.rotation_euler = (0, 0, pa - math.pi / 2)

if __name__ == "__main__":
    bpy.ops.wm.read_factory_settings(use_empty=True)
    build_floor()
    for i in range(SPEC["PLOTS"]):
        build_sector(i)
    finalize()
    print(stats())
    if "--export" in sys.argv:
        for o in bpy.data.objects:
            o.select_set(o.name.startswith("Map"))
        bpy.ops.export_scene.fbx(filepath=os.path.join(OUT, "SF_Map.fbx"), use_selection=True, apply_unit_scale=True,
                                 apply_scale_options="FBX_SCALE_ALL", axis_forward="-Z", axis_up="Y",
                                 object_types={"MESH", "EMPTY"}, mesh_smooth_type="FACE", add_leaf_bones=False, bake_anim=False)
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "SF_Map.blend"))
        print("exported")
    if "--render" in sys.argv:
        append_machines(2)
        for o in bpy.data.objects:
            if "Marker" in o.name:
                o.hide_render = True
        pa = plot_angle(2)
        setup_render(1100, 560, 20, (430, -430, 330), (0, 0, 0), 30)
        bpy.context.scene.render.filepath = os.path.join(OUT, "map_aerial.png")
        bpy.ops.render.render(write_still=True)
        # gameplay-ish view: standing on the ramp of plot 3 looking up at its machines
        eye = polar(92, pa, 24) + polar(10, pa + math.pi / 2)
        setup_render(1100, 560, 20, eye, polar(SPEC["PLOT_R"], pa, 14), 24)
        bpy.context.scene.render.filepath = os.path.join(OUT, "map_ground.png")
        bpy.ops.render.render(write_still=True)
        print("rendered")
