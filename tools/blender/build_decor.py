"""
Starfall Forge - better crystal clusters + tiled plot floor (SF_Decor.fbx).
Run headless:  python3 build_decor.py [--export] [--render]

Zack 2026-10-06: the crystals looked like flat glowing paper (they were scaled-up meteor shards in solid Neon)
and the plot floor was one flat orange slab. Same rules as the other scripts: every part is its own object
<Model>__<Part>__<MatKey>, no textures, Roblox assigns Material + Color (ServerStorage.Tools.ApplyDecor).
  CrystalA/B/C : hexagonal crystals with faceted tips, a glassy SHELL (Roblox Glass, tinted per cluster) around a
                 thin glowing CORE (Neon), growing out of a chunky rock BASE.  ~10 studs tall, pivot = base centre.
  PlotFloor    : 56 x 56 stone-tile yard (8 x 8 bevelled tiles in two tones + a few cracked ones, dark grout bed,
                 raised border). Top at z = 0, pivot = top centre.
"""
import bpy, bmesh, math, os, sys, random
from mathutils import Vector, Matrix

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_machines as BM
from build_machines import box, part, root
import build_models as MD
from build_models import mesh_obj, rock_bm

OUT = BM.OUT
BM.PALETTE.update({
    "CrystalShell": ("B07CFF", 0, .05, 0.6), "CrystalCore": ("E9D9FF", 0, .2, 8),
    "CrystalRock": ("2E2838", 0, .85, 0), "CrystalRockLight": ("4A4256", 0, .85, 0),
    "TileA": ("D9A86C", 0, .8, 0), "TileB": ("C69155", 0, .8, 0), "TileC": ("E6BE86", 0, .8, 0), "TileCrack": ("B07E49", 0, .85, 0),
    "Grout": ("5B4636", 0, .9, 0), "Border": ("8C6A4E", 0, .8, 0),
})

# ---------------------------------------------------------------- crystal
def crystal_bm(bm, base, direction, length, radius, sides=6, tip=0.32, twist=0.0, lean_tip=0.0):
    """hexagonal prism with a faceted, slightly off-centre tip; bottom sunk into the rock"""
    d = Vector(direction).normalized()
    q = d.to_track_quat("Z", "Y")
    M = Matrix.Translation(base) @ q.to_matrix().to_4x4() @ Matrix.Rotation(twist, 4, "Z")
    body = length * (1 - tip)
    r0, r1 = [], []
    for i in range(sides):
        a = i * 2 * math.pi / sides
        p = Vector((math.cos(a) * radius, math.sin(a) * radius, 0))
        r0.append(bm.verts.new(M @ (p * 0.9 + Vector((0, 0, -radius * 1.2)))))
        r1.append(bm.verts.new(M @ (p * 1.04 + Vector((0, 0, body)))))
    tipv = bm.verts.new(M @ Vector((radius * lean_tip, radius * lean_tip * 0.5, length)))
    bm.faces.new(r0[::-1])
    for i in range(sides):
        j = (i + 1) % sides
        bm.faces.new((r0[i], r0[j], r1[j], r1[i]))
        bm.faces.new((r1[i], r1[j], tipv))

def cluster(R, name, seed, n, spread, h0, h1):
    rng = random.Random(seed)
    shell, core = bmesh.new(), bmesh.new()
    # one tall hero crystal + a ring of shorter ones leaning out
    specs = [(Vector((0, 0, 0)), Vector((rng.uniform(-.1, .1), rng.uniform(-.1, .1), 1)), h1, h1 * 0.17)]
    for k in range(n - 1):
        a = k / (n - 1) * 2 * math.pi + rng.uniform(-0.3, 0.3)
        r = spread * rng.uniform(0.45, 1.0)
        lean = rng.uniform(0.35, 0.8)
        L = rng.uniform(h0, h1 * 0.8)
        specs.append((Vector((math.cos(a) * r, math.sin(a) * r, 0)), Vector((math.cos(a) * lean, math.sin(a) * lean, 1)), L, L * rng.uniform(0.15, 0.21)))
    for base, d, L, rad in specs:
        tw = rng.uniform(0, 1)
        lt = rng.uniform(-0.35, 0.35)
        crystal_bm(shell, base + Vector((0, 0, 0.3)), d, L, rad, 6, rng.uniform(0.25, 0.38), tw, lt)
        crystal_bm(core, base + Vector((0, 0, 0.3)), d, L * 0.82, rad * 0.42, 6, 0.3, tw, lt * 0.5)
    part(name, "Shell", [mesh_obj("sh", shell, "CrystalShell")], R, pivot=(0, 0, 0))
    part(name, "Core", [mesh_obj("co", core, "CrystalCore")], R, pivot=(0, 0, 0))
    # chunky rock base hugging the roots + a few pebbles
    rocks = []
    for k in range(4):
        a = k * math.pi / 2 + rng.uniform(-0.4, 0.4)
        bm = rock_bm(spread * rng.uniform(0.75, 0.95), 1, 0.2, 0.6, seed * 10 + k)
        o = mesh_obj("rb", bm, "CrystalRock")
        o.location = (math.cos(a) * spread * 0.45, math.sin(a) * spread * 0.45, 0.1)
        rocks.append(o)
    part(name, "Base", rocks, R, pivot=(0, 0, 0))
    peb = []
    for k in range(5):
        a = rng.uniform(0, 2 * math.pi)
        bm = rock_bm(rng.uniform(0.25, 0.5), 1, 0.25, 0.7, seed * 20 + k)
        o = mesh_obj("pb", bm, "CrystalRockLight")
        o.location = (math.cos(a) * spread * 1.25, math.sin(a) * spread * 1.25, 0.1)
        peb.append(o)
    part(name, "Pebbles", peb, R, pivot=(0, 0, 0))

# ---------------------------------------------------------------- plot floor
def plot_floor(R):
    M = "PlotFloor"
    rng = random.Random(5)
    S, N = 56.0, 8
    border = 1.6
    inner = S - 2 * border
    t = inner / N
    gap = 0.22
    groups = {"TileA": [], "TileB": [], "TileC": [], "TileCrack": []}
    # running-bond flagstones: rows of pavers in mixed lengths, random shade per stone (not a checkerboard)
    for j in range(N):
        y = -inner / 2 + (j + 0.5) * t
        x0 = -inner / 2
        widths = []
        x = x0 - (t * 0.5 if j % 2 else 0)
        while x < inner / 2:
            w = t * rng.choice((1.0, 1.0, 1.5, 2.0))
            a0, a1 = max(x, x0), min(x + w, inner / 2)
            if a1 - a0 > 0.8:
                widths.append((a0, a1))
            x += w
        for (a0, a1) in widths:
            key = rng.choice(("TileA", "TileA", "TileB", "TileB", "TileC"))
            if rng.random() < 0.07:
                key = "TileCrack"
            h = 0.5 + rng.uniform(-0.04, 0.04)
            cx = (a0 + a1) / 2
            o = box((a1 - a0 - gap, t - gap, h), (cx, y, -h / 2 + rng.uniform(-0.03, 0.03)), key, 0.14, 2, rot=(0, 0, rng.uniform(-0.006, 0.006)))
            groups[key].append(o)
            if key == "TileCrack":
                o2 = box(((a1 - a0) * 0.7, 0.12, 0.08), (cx, y + rng.uniform(-1, 1), 0.0), "Grout", 0.02, 1, rot=(0, 0, rng.uniform(-0.5, 0.5)))
                groups.setdefault("Cracks", []).append(o2)
    for key, objs in groups.items():
        if objs:
            part(M, key if key != "Cracks" else "Cracks", objs, R, pivot=(0, 0, 0))
    part(M, "Grout", [box((inner + 0.1, inner + 0.1, 1.2), (0, 0, -0.75), "Grout", 0.05, 1)], R, pivot=(0, 0, 0))
    edges = []
    for (x, y, sx, sy) in ((0, -S / 2 + border / 2, S, border), (0, S / 2 - border / 2, S, border),
                           (-S / 2 + border / 2, 0, border, S - 2 * border), (S / 2 - border / 2, 0, border, S - 2 * border)):
        edges.append(box((sx, sy, 1.4), (x, y, -0.6), "Border", 0.25, 2))
    part(M, "Border", edges, R, pivot=(0, 0, 0))

# ---------------------------------------------------------------- build
def build_all():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for k, (n, seed, cnt, spread, h0, h1) in enumerate((("CrystalA", 1, 7, 1.6, 3.2, 8.5), ("CrystalB", 2, 5, 1.3, 2.6, 6.5), ("CrystalC", 3, 9, 2.0, 2.4, 7.0))):
        r = root(n, 0)
        cluster(r, n, seed, cnt, spread, h0, h1)
        r.location = (-14 + k * 9, -20, 0)
    r = root("PlotFloor", 0)
    plot_floor(r)
    r.location = (0, 30, 1.5)

if __name__ == "__main__":
    build_all()
    bpy.context.view_layer.update()
    for k, v in MD.heights().items():
        print(f"{k}: height {v[0]}  parts {v[1]}  tris {v[2]}")
    if "--export" in sys.argv:
        BM.export_fbx(os.path.join(OUT, "SF_Decor.fbx"))
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "SF_Decor.blend"))
        print("exported")
    if "--render" in sys.argv:
        BM.setup_render(1400, 640, 24)
        sc = bpy.context.scene
        # dusk sky so the cores read as glowing
        sc.world.node_tree.nodes["Background"].inputs[0].default_value = BM.srgb("2B2350") + [1]
        sc.world.node_tree.nodes["Background"].inputs[1].default_value = 0.6
        for o in bpy.data.objects:
            if o.type == "LIGHT":
                o.data.energy = 1.6
        # glass look for the shells in the preview (Roblox uses Glass material)
        m = bpy.data.materials["CrystalShell"]
        b = m.node_tree.nodes["Principled BSDF"]
        b.inputs["Transmission Weight"].default_value = 0.85
        b.inputs["Roughness"].default_value = 0.08
        b.inputs["IOR"].default_value = 1.35
        cam = sc.camera
        def shot(names, loc, target, lens, fname):
            for rr in [o for o in bpy.data.objects if o.type == "EMPTY"]:
                for c in rr.children:
                    c.hide_render = rr.name not in names
            cam.location = loc
            cam.data.lens = lens
            cam.rotation_euler = (Vector(target) - cam.location).to_track_quat("-Z", "Y").to_euler()
            sc.render.filepath = os.path.join(OUT, fname)
            bpy.ops.render.render(write_still=True)
        shot(["CrystalA", "CrystalB", "CrystalC"], (-5, -50, 12), (-5, -20, 3.5), 38, "preview_crystals.png")
        sc.world.node_tree.nodes["Background"].inputs[0].default_value = BM.srgb("9FD3F0") + [1]
        for o in bpy.data.objects:
            if o.type == "LIGHT":
                o.data.energy = 3.2
        shot(["PlotFloor"], (22, -12, 34), (0, 30, 0), 32, "preview_plotfloor.png")
        print("rendered")
