"""
Starfall Forge - production line + upgrade showpieces (SF_Line.fbx).   D-026
Run headless:  python3 build_line.py [--export] [--render] [--anim]

Zack 2026-10-06: "for any animations ensure blender and new models". Every moving piece is its own object with its
pivot at the motion centre, named <Model>__<Part>__<MatKey>, so the Roblox client (StarterPlayerScripts.LineAnimator)
drives exactly the motion previewed here with --anim.
  BeltStraight : 4-stud tileable belt; CLEATS slide along -Y (loop every 1 stud)
  BeltCorner   : 4x4 turntable; PLATE spins about Z
  Ore / Ingot / StarBar : the products that ride the belts (glow parts are tinted per mutation in Roblox)
  Silo         : Stardust silo at the end of the line; FILL is scaled up from its bottom pivot
  CrusherMk2   : grinder bolted beside the Crusher; DRUM spins about X
  CometBoots   : display stand; BOOTS bob + spin, FINS glow
  MagnetTower  : 18-stud lattice tower; DISH spins about Z, COIL pulses
  TwinRack     : cargo crane; ARM + HOOK swing about the mast top
  StarforgeCore: yard-centre reactor; STAR spins, RINGA / RINGB orbit on tilted axes
  MeteorChute  : ramp-foot launcher; BARREL recoils about its hinge
1 unit = 1 stud, -Y = front, Z = up.
"""
import bpy, bmesh, math, os, sys, random
from mathutils import Vector, Matrix

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_machines as BM
from build_machines import box, cyl, frustum, star4, part, root
import build_models as MD
from build_models import mesh_obj, rock_bm, torus, crystal, fib_dirs

OUT = BM.OUT
BM.PALETTE.update({
    "Glass": ("BFE9FF", 0, .05, 0), "StarFill": ("FFE21B", 0, .3, 6), "Lime": ("6FFF10", 0, .3, 5),
    "Cyan": ("19F0F5", 0, .3, 5), "BootPurple": ("8F5BFF", 0, .45, 0), "Teal": ("64DFD1", 0, .4, 5),
    "RockGrey": ("7D7A85", 0, .85, 0), "Leather": ("9B5B3A", 0, .7, 0),
})

# ---------------------------------------------------------------- belts
def belt_straight(R):
    M = "BeltStraight"
    L, W = 4.0, 3.0
    part(M, "Frame", [box((W + 0.4, L, 0.5), (0, 0, 0.75), "Steel", 0.08)], R)
    part(M, "Rails", [box((0.3, L, 0.55), (s * (W / 2 + 0.05), 0, 1.25), "Cream", 0.08) for s in (-1, 1)], R)
    part(M, "Belt", [box((W - 0.2, L, 0.2), (0, 0, 1.1), "Dark", 0.03)], R)
    part(M, "Legs", [box((0.4, 0.4, 0.6), (s * 1.3, 0, 0.3), "SteelLight", 0.06) for s in (-1, 1)], R)
    # cleats every 1 stud; the client slides them 0..1 stud along -Y and wraps (seamless)
    part(M, "Cleats", [box((W - 0.5, 0.18, 0.14), (0, -L / 2 + 0.5 + k, 1.27), "Yellow", 0.02, 1) for k in range(4)], R, pivot=(0, 0, 1.27))

def belt_corner(R):
    M = "BeltCorner"
    part(M, "Frame", [cyl(2.2, 0.5, (0, 0, 0.75), "Steel", "Z", 24, 0.08)], R)
    part(M, "Rails", [torus(2.15, 0.15, (0, 0, 1.25), "Cream", major=24, minor=6)], R)
    part(M, "Plate", [cyl(1.95, 0.2, (0, 0, 1.1), "Dark", "Z", 24, 0.03)], R, pivot=(0, 0, 1.1))
    part(M, "PlateCleats", [box((1.5, 0.18, 0.14), (math.cos(a) * 1.0, math.sin(a) * 1.0, 1.27), "Yellow", 0.02, 1, rot=(0, 0, a)) for a in [k * math.pi / 3 for k in range(6)]], R, pivot=(0, 0, 1.1))
    part(M, "Hub", [cyl(0.35, 0.2, (0, 0, 1.3), "SteelLight", "Z", 12, 0.03)], R, pivot=(0, 0, 1.1))

# ---------------------------------------------------------------- products
def ore(R):
    M = "Ore"
    rocks, glow = [], []
    for k, (x, y, z, r) in enumerate(((0, 0, 0.45, 0.45), (0.45, 0.15, 0.32, 0.32), (-0.35, 0.25, 0.3, 0.3))):
        bm = rock_bm(r, 1, 0.2, 0.85, 70 + k)
        o = mesh_obj("o", bm, "RockGrey")
        o.location = (x, y, z)
        rocks.append(o)
    c = bmesh.new()
    for d in fib_dirs(4, 3):
        crystal(c, d * 0.3 + Vector((0, 0, 0.45)), d, 0.45, 0.09, 4)
    part(M, "Rock", rocks, R, pivot=(0, 0, 0))
    part(M, "Glow", [mesh_obj("g", c, "Glow")], R, pivot=(0, 0, 0))

def ingot_bm(L=1.5, W=0.7, H=0.45, taper=0.18):
    bm = bmesh.new()
    lo = [(-L / 2, -W / 2, 0), (L / 2, -W / 2, 0), (L / 2, W / 2, 0), (-L / 2, W / 2, 0)]
    hi = [(-L / 2 + taper, -W / 2 + taper, H), (L / 2 - taper, -W / 2 + taper, H), (L / 2 - taper, W / 2 - taper, H), (-L / 2 + taper, W / 2 - taper, H)]
    a = [bm.verts.new(p) for p in lo]
    b = [bm.verts.new(p) for p in hi]
    bm.faces.new(a[::-1])
    bm.faces.new(b)
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new((a[i], a[j], b[j], b[i]))
    return bm

def ingot(R):
    part("Ingot", "Bar", [mesh_obj("i", ingot_bm(), "Glow", smooth=False)], R, pivot=(0, 0, 0))

def star_bar(R):
    M = "StarBar"
    part(M, "Bar", [mesh_obj("i", ingot_bm(1.7, 0.8, 0.5), "Gold", smooth=False)], R, pivot=(0, 0, 0))
    s = star4(0.28, 0.1, 0.08, (0, 0, 0.55), "Cream")
    s.rotation_euler = (math.pi / 2, 0, 0)
    part(M, "Stamp", [s], R, pivot=(0, 0, 0))

# ---------------------------------------------------------------- silo
def silo(R):
    M = "Silo"
    part(M, "Base", [cyl(3.8, 0.8, (0, 0, 0.4), "Steel", "Z", 8, 0.15)], R)
    part(M, "Legs", [box((0.6, 0.6, 2.2), (math.cos(a) * 2.6, math.sin(a) * 2.6, 1.9), "SteelLight", 0.08) for a in [k * math.pi / 2 + math.pi / 4 for k in range(4)]], R)
    part(M, "Floor", [cyl(3.0, 0.5, (0, 0, 3.15), "Red", "Z", 24, 0.1)], R)
    tank = cyl(2.8, 7.0, (0, 0, 6.9), "Glass", "Z", 24, 0.0)
    part(M, "Tank", [tank], R)
    part(M, "Fill", [cyl(2.6, 6.8, (0, 0, 3.4 + 3.4), "StarFill", "Z", 24, 0.0)], R, pivot=(0, 0, 3.4))  # pivot = bottom: scale Z
    part(M, "Bands", [torus(2.85, 0.2, (0, 0, z), "Red", major=28, minor=6) for z in (3.6, 6.9, 10.2)], R)
    part(M, "Cap", [cyl(3.0, 0.6, (0, 0, 10.7), "Red", "Z", 24, 0.12), cyl(2.6, 1.4, (0, 0, 11.7), "Red", "Z", 24, 0.12, r2=1.0)], R)
    part(M, "Funnel", [cyl(1.0, 1.2, (0, 0, 12.9), "Steel", "Z", 16, 0.06, r2=1.4)], R)
    part(M, "Star", [star4(1.0, 0.36, 0.3, (0, 0, 14.6), "Gold")], R, pivot=(0, 0, 14.6))
    part(M, "Chute", [box((1.2, 3.4, 0.25), (0, -3.4, 3.7), "Steel", 0.05, rot=(math.radians(20), 0, 0))], R)

# ---------------------------------------------------------------- tier-2 showpieces
def crusher_mk2(R):
    M = "CrusherMk2"
    part(M, "Base", [box((5.2, 6.0, 0.6), (0, 0, 0.3), "Steel", 0.15)], R)
    part(M, "Housing", [box((4.6, 5.2, 3.4), (0, 0, 2.3), "Red", 0.3, 2)], R)
    part(M, "Hopper", [frustum((3.6, 4.2), (4.8, 5.4), 4.0, 5.6, "Cream", 0.25)], R)
    teeth = [cyl(1.0, 3.8, (0, 0, 4.4), "SteelLight", "X", 16, 0.05)]
    for k in range(10):
        a = k * math.pi / 5
        teeth.append(box((3.8, 0.35, 0.35), (0, math.cos(a) * 1.05, 4.4 + math.sin(a) * 1.05), "SteelLight", 0.04, 1, rot=(a, 0, 0)))
    part(M, "Drum", teeth, R, pivot=(0, 0, 4.4))
    part(M, "Glow", [box((3.0, 0.2, 0.6), (0, -2.62, 1.6), "Glow", 0.08)], R)
    part(M, "Badge", [box((1.6, 0.15, 0.8), (0, -2.62, 3.2), "Cream", 0.05)], R)

def comet_boots(R):
    M = "CometBoots"
    part(M, "Pedestal", [cyl(1.9, 0.6, (0, 0, 0.3), "Cream", "Z", 24, 0.1), cyl(1.8, 0.4, (0, 0, 2.6), "Cream", "Z", 24, 0.1)], R)
    part(M, "Column", [cyl(1.5, 1.8, (0, 0, 1.5), "BootPurple", "Z", 24, 0.15)], R)
    part(M, "Ring", [torus(1.75, 0.12, (0, 0, 2.85), "Cyan", major=28, minor=6)], R)
    boots, fins, soles = [], [], []
    for s in (-1, 1):
        x = s * 0.6
        boots.append(box((0.85, 0.9, 1.2), (x, 0.15, 4.0), "BootPurple", 0.22, 2))
        boots.append(box((0.85, 1.5, 0.6), (x, -0.15, 3.55), "BootPurple", 0.24, 2))
        soles.append(box((0.92, 1.6, 0.2), (x, -0.15, 3.2), "Cream", 0.07))
        f = star4(0.5, 0.16, 0.12, (x + s * 0.5, 0.35, 4.1), "Cyan")
        f.rotation_euler = (0, 0, math.pi / 2)
        fins.append(f)
        fins.append(cyl(0.18, 1.0, (x, 0.75, 3.3), "Cyan", "Y", 8, 0.02, r2=0.02))  # comet tail
    piv = (0, 0, 3.8)
    part(M, "Boots", boots, R, pivot=piv)
    part(M, "Soles", soles, R, pivot=piv)
    part(M, "Fins", fins, R, pivot=piv)

def magnet_tower(R):
    M = "MagnetTower"
    H = 15.0
    legs, braces = [], []
    for sx in (-1, 1):
        for sy in (-1, 1):
            legs.append(box((0.45, 0.45, H), (sx * 1.6, sy * 1.6, H / 2), "Steel", 0.06))
    for k in range(5):
        z = 1.5 + k * 3.0
        for (a, b) in (((-1.6, -1.6), (1.6, -1.6)), ((1.6, -1.6), (1.6, 1.6)), ((1.6, 1.6), (-1.6, 1.6)), ((-1.6, 1.6), (-1.6, -1.6))):
            mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, z + 1.5)
            length = math.hypot(b[0] - a[0], b[1] - a[1])
            yaw = math.atan2(b[1] - a[1], b[0] - a[0])
            braces.append(box((math.hypot(length, 3.0), 0.22, 0.22), mid, "SteelLight", 0.03, 1, rot=(0, -math.atan2(3.0, length), yaw)))
    part(M, "Legs", legs, R)
    part(M, "Braces", braces, R)
    part(M, "Base", [box((4.6, 4.6, 0.6), (0, 0, 0.3), "Steel", 0.15)], R)
    part(M, "Platform", [box((4.4, 4.4, 0.5), (0, 0, H + 0.25), "Red", 0.15)], R)
    part(M, "Coil", [torus(0.9, 0.3, (0, 0, H + 0.8 + k * 0.35), "Glow", major=18, minor=6) for k in range(3)], R)
    # horseshoe magnet: U from three boxes + cream tips, spinning about Z
    dish = [box((0.9, 0.9, 2.6), (s * 1.3, 0, H + 3.3), "Red", 0.25, 2) for s in (-1, 1)]
    dish.append(box((3.5, 0.9, 0.9), (0, 0, H + 2.2), "Red", 0.25, 2))
    tips = [box((0.95, 0.95, 0.8), (s * 1.3, 0, H + 5.0), "Cream", 0.2, 2) for s in (-1, 1)]
    part(M, "Dish", dish, R, pivot=(0, 0, H + 2.2))
    part(M, "Tips", tips, R, pivot=(0, 0, H + 2.2))

def twin_rack(R):
    M = "TwinRack"
    H = 17.0
    part(M, "Base", [box((5.0, 5.0, 0.8), (0, 0, 0.4), "Steel", 0.15)], R)
    part(M, "Plinth", [box((3.2, 3.2, 1.6), (0, 0, 1.6), "Red", 0.2)], R)
    mast = [box((0.4, 0.4, H), (sx * 0.9, sy * 0.9, H / 2 + 1.5), "Yellow", 0.05) for sx in (-1, 1) for sy in (-1, 1)]
    for k in range(int(H // 2)):
        z = 2.5 + k * 2.0
        mast.append(box((2.2, 0.18, 0.18), (0, -0.9, z), "Yellow", 0.02, 1, rot=(0, math.radians(40), 0)))
        mast.append(box((2.2, 0.18, 0.18), (0, 0.9, z), "Yellow", 0.02, 1, rot=(0, math.radians(-40), 0)))
    part(M, "Mast", mast, R)
    top = H + 1.5
    pv = (0, 0, top)
    part(M, "Arm", [box((0.6, 13.0, 0.8), (0, -4.0, top + 0.6), "Yellow", 0.1)], R, pivot=pv)
    part(M, "ArmWeight", [box((1.6, 1.6, 1.6), (0, 3.4, top + 0.2), "Steel", 0.15)], R, pivot=pv)
    part(M, "ArmCab", [box((1.6, 1.8, 1.4), (0, 0, top + 1.6), "Red", 0.2)], R, pivot=pv)
    part(M, "ArmCable", [cyl(0.06, 5.0, (0, -9.6, top - 2.0), "Dark", "Z", 6, 0.0)], R, pivot=pv)
    part(M, "ArmHook", [box((0.9, 0.9, 0.5), (0, -9.6, top - 4.7), "SteelLight", 0.1),
                        torus(0.4, 0.1, (0, -9.6, top - 5.3), "SteelLight", rot=(math.pi / 2, 0, 0), major=14, minor=5)], R, pivot=pv)

def starforge_core(R):
    M = "StarforgeCore"
    part(M, "Base", [cyl(5.0, 1.0, (0, 0, 0.5), "Steel", "Z", 8, 0.2)], R)
    part(M, "Deck", [cyl(4.4, 0.5, (0, 0, 1.25), "Cream", "Z", 32, 0.1)], R)
    part(M, "Pillars", [box((0.8, 0.8, 9.0), (math.cos(a) * 3.9, math.sin(a) * 3.9, 5.5), "Steel", 0.15) for a in [k * math.pi / 2 + math.pi / 4 for k in range(4)]], R)
    part(M, "Crown", [torus(3.9, 0.4, (0, 0, 10.2), "Red", major=32, minor=8)], R)
    part(M, "Vents", [box((1.2, 0.2, 0.5), (math.cos(a) * 4.45, math.sin(a) * 4.45, 1.25), "Glow", 0.05, 1, rot=(0, 0, a + math.pi / 2)) for a in [k * math.pi / 4 for k in range(8)]], R)
    shell = bmesh.new()
    bmesh.ops.create_icosphere(shell, subdivisions=3, radius=3.0)
    shell.transform(Matrix.Translation((0, 0, 5.8)))
    part(M, "Shell", [mesh_obj("sh", shell, "Glass", smooth=True)], R, pivot=(0, 0, 5.8))
    st = bmesh.new()
    bmesh.ops.create_icosphere(st, subdivisions=1, radius=0.9)
    for d in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
        crystal(st, Vector(d) * 0.5, Vector(d), 1.4, 0.3, 4)
    st.transform(Matrix.Translation((0, 0, 5.8)))
    part(M, "Star", [mesh_obj("st", st, "StarFill")], R, pivot=(0, 0, 5.8))
    part(M, "RingA", [torus(2.2, 0.1, (0, 0, 5.8), "Cyan", rot=(math.radians(65), 0, 0), major=32, minor=6)], R, pivot=(0, 0, 5.8))
    part(M, "RingB", [torus(2.5, 0.1, (0, 0, 5.8), "Teal", rot=(0, math.radians(70), 0), major=32, minor=6)], R, pivot=(0, 0, 5.8))

def meteor_chute(R):
    M = "MeteorChute"
    part(M, "Base", [box((6.0, 6.0, 1.0), (0, 0, 0.5), "Steel", 0.2)], R)
    part(M, "Mount", [box((0.8, 2.4, 2.6), (s * 2.0, 0.8, 2.3), "Steel", 0.12) for s in (-1, 1)], R)
    hinge = (0, 0.8, 3.2)
    barrel = cyl(1.7, 5.6, (0, 0, 0), "Red", "Z", 20, 0.2, r2=1.5)
    barrel.location = (0, 0.8 + 2.0, 3.2 + 2.8)
    barrel.rotation_euler = (math.radians(-35), 0, 0)
    band = cyl(1.85, 0.6, (0, 0, 0), "Cream", "Z", 20, 0.08)
    band.location = (0, 0.8 + 1.0, 3.2 + 1.4)
    band.rotation_euler = (math.radians(-35), 0, 0)
    part(M, "Barrel", [barrel], R, pivot=hinge)
    part(M, "Band", [band], R, pivot=hinge)
    part(M, "Rim", [cyl(2.6, 0.5, (0, -3.4, 1.05), "Dark", "Z", 24, 0.1)], R)
    part(M, "Mouth", [cyl(2.2, 0.25, (0, -3.4, 1.35), "Lime", "Z", 24, 0.04)], R)
    part(M, "Arrows", [box((0.9, 0.25, 0.1), (s * 0.35, -3.4 + k * 0.7 - 0.4, 1.52), "Cream", 0.02, 1, rot=(0, 0, s * math.radians(40))) for k in range(2) for s in (-1, 1)], R)

MODELS = [("BeltStraight", belt_straight), ("BeltCorner", belt_corner), ("Ore", ore), ("Ingot", ingot), ("StarBar", star_bar),
          ("Silo", silo), ("CrusherMk2", crusher_mk2), ("CometBoots", comet_boots), ("MagnetTower", magnet_tower),
          ("TwinRack", twin_rack), ("StarforgeCore", starforge_core), ("MeteorChute", meteor_chute)]

def build_all():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    xs = {"BeltStraight": (-30, 0), "BeltCorner": (-25, 0), "Ore": (-21, -2), "Ingot": (-18.5, -2), "StarBar": (-16, -2), "Silo": (-10, 0),
          "CrusherMk2": (-2, 0), "CometBoots": (4, 0), "MagnetTower": (10, 0), "TwinRack": (17, 4), "StarforgeCore": (28, 0), "MeteorChute": (38, 0)}
    for n, fn in MODELS:
        r = root(n, 0)
        fn(r)
        r.location = (xs[n][0], xs[n][1], 0)

def animate(frames):
    """the exact client motion (LineAnimator), for the preview GIF"""
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = 1, frames
    O = bpy.data.objects
    def key(o, path, idx, vals):
        for f, v in vals:
            getattr(o, path)[idx] = v
            o.keyframe_insert(path, index=idx, frame=f)
    t = lambda k: 1 + round(k * frames)
    c = O["BeltStraight__Cleats__Yellow"]
    key(c, "location", 1, [(1, c.location.y), (frames + 1, c.location.y - 1.0)])
    key(O["BeltCorner__Plate__Dark"], "rotation_euler", 2, [(1, 0), (frames + 1, -math.pi / 3)])
    key(O["BeltCorner__PlateCleats__Yellow"], "rotation_euler", 2, [(1, 0), (frames + 1, -math.pi / 3)])
    key(O["BeltCorner__Hub__SteelLight"], "rotation_euler", 2, [(1, 0), (frames + 1, -math.pi / 3)])
    key(O["CrusherMk2__Drum__SteelLight"], "rotation_euler", 0, [(1, 0), (frames + 1, 2 * math.pi)])
    for n in ("CometBoots__Boots__BootPurple", "CometBoots__Soles__Cream", "CometBoots__Fins__Cyan"):
        o = O[n]
        z = o.location.z
        key(o, "rotation_euler", 2, [(1, 0), (frames + 1, 2 * math.pi)])
        key(o, "location", 2, [(1, z), (t(0.5), z + 0.5), (frames + 1, z)])
    for n in ("MagnetTower__Dish__Red", "MagnetTower__Tips__Cream"):
        key(O[n], "rotation_euler", 2, [(1, 0), (frames + 1, 2 * math.pi)])
    for n in ("TwinRack__Arm__Yellow", "TwinRack__ArmWeight__Steel", "TwinRack__ArmCab__Red", "TwinRack__ArmCable__Dark", "TwinRack__ArmHook__SteelLight"):
        if n in O:
            key(O[n], "rotation_euler", 2, [(1, -0.6), (t(0.5), 0.6), (frames + 1, -0.6)])
    for n, axis, amt in (("StarforgeCore__Star__StarFill", 2, 2 * math.pi), ("StarforgeCore__RingA__Cyan", 1, 2 * math.pi), ("StarforgeCore__RingB__Teal", 0, -2 * math.pi)):
        key(O[n], "rotation_euler", axis, [(1, 0), (frames + 1, amt)])
    for n in ("MeteorChute__Barrel__Red", "MeteorChute__Band__Cream"):
        key(O[n], "rotation_euler", 0, [(1, 0), (t(0.15), math.radians(10)), (t(0.45), 0), (frames + 1, 0)])
    fill = O["Silo__Fill__StarFill"]
    key(fill, "scale", 2, [(1, 0.35), (t(0.5), 0.75), (frames + 1, 0.35)])
    for fc in [fc for a in bpy.data.actions for fc in getattr(a, "fcurves", [])]:
        for k in fc.keyframe_points:
            k.interpolation = "LINEAR"

if __name__ == "__main__":
    build_all()
    bpy.context.view_layer.update()
    for k, v in MD.heights().items():
        print(f"{k}: height {v[0]}  parts {v[1]}  tris {v[2]}")
    if "--export" in sys.argv:
        BM.export_fbx(os.path.join(OUT, "SF_Line.fbx"))
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "SF_Line.blend"))
        print("exported")
    if "--render" in sys.argv or "--anim" in sys.argv:
        BM.setup_render(1600, 600, 16)
        m = bpy.data.materials["Glass"].node_tree.nodes["Principled BSDF"]
        m.inputs["Transmission Weight"].default_value = 0.9
        cam = bpy.context.scene.camera
        cam.location = (4, -58, 22)
        cam.data.lens = 30
        cam.rotation_euler = (Vector((4, 0, 6)) - cam.location).to_track_quat("-Z", "Y").to_euler()
        if "--render" in sys.argv:
            bpy.context.scene.render.filepath = os.path.join(OUT, "preview_line.png")
            bpy.ops.render.render(write_still=True)
            print("rendered")
        if "--anim" in sys.argv:
            n = 16
            animate(n)
            sc = bpy.context.scene
            sc.render.resolution_x, sc.render.resolution_y = 960, 360
            sc.cycles.samples = 8
            sc.render.filepath = os.path.join(OUT, "line_anim_")
            sc.render.image_settings.file_format = "PNG"
            bpy.ops.render.render(animation=True)
            print("anim rendered")
