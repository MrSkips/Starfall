"""
Starfall Forge - pets, eggs and gadget models in one FBX (SF_Pets.fbx).
Run headless:  python3 build_pets.py [--export] [--render]

Same rules as build_models.py: every part is its own object <Model>__<Part>__<MatKey>, no textures,
Roblox assigns Material + Color from MatKey (ServerStorage.Tools.ApplyPets). 1 unit = 1 stud,
-Y = the face / front, Z = up.
  pets    : Pet<Name> x16 (ids match ReplicatedStorage.Shared.Pets), ~2-3 studs tall, big glossy eyes
  eggs    : EggRock, EggEmber, EggFrost, EggCosmic (~3.4 studs tall)
  gadgets : ForgeDrone (Rotor1..4 pivots at the rotor hubs), LaunchPad (9 x 9, the import-scale reference)
"""
import bpy, bmesh, math, os, sys, random
from mathutils import Vector, Matrix, Euler

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_machines as BM
from build_machines import box, cyl, part, root
import build_models as MD
from build_models import mesh_obj, rock_bm, inset_patches, crystal, fib_dirs, torus

OUT = BM.OUT
BM.PALETTE.update({
    # shared
    "EyeBlack": ("16131C", 0, .15, 0), "EyeShine": ("FFFFFF", 0, .2, 6), "Blush": ("FF8FB0", 0, .6, 0),
    "White": ("F4F6FF", 0, .5, 0),
    # pet bodies
    "Pebble": ("8C8597", 0, .85, 0), "PebbleDark": ("5E5868", 0, .85, 0),
    "Rubble": ("6E6585", 0, .85, 0), "EmberFur": ("6A332C", 0, .7, 0), "Flare": ("FF8A2B", 0, .55, 0),
    "SunGold": ("FFB13D", 0, .45, 0), "Snow": ("DDEFFF", 0, .6, 0), "IceTeal": ("7FEAF2", 0, .1, 1.5),
    "Glacio": ("6FA8D8", 0, .55, 0), "Aurora": ("64DFD1", 0, .4, 0), "Pink": ("FF4FD8", 0, .4, 6),
    "Void": ("1F1A33", 0, .5, 0), "Cyan": ("19F0F5", 0, .4, 6), "Whale": ("2C3E8C", 0, .5, 0),
    "WhaleBelly": ("9FB3F0", 0, .5, 0), "Celest": ("FFD9F2", 0, .5, 0), "Wing": ("FFFFFF", 0, .4, 0),
    "WingGold": ("FFE9A0", 0, .4, 0), "Orange": ("FF9A3C", 0, .5, 0),
})
rng = random.Random(21)

# ---------------------------------------------------------------- helpers
def ell(radii, loc, mat, rot=(0, 0, 0), seg=20, rings=12, name="e", smooth=True):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=rings, radius=1, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = radii
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    return BM._finish(o, mat, 0, 1, smooth)

def cone(r1, r2, depth, loc, mat, rot=(0, 0, 0), verts=12, smooth=False, name="k"):
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r1, radius2=r2, depth=depth, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    return BM._finish(o, mat, 0, 1, smooth)

def cone_to(base, tip, r, mat, verts=10, r2=0.0):
    """cone whose base centre is `base`, pointing at `tip`"""
    base, tip = Vector(base), Vector(tip)
    d = tip - base
    q = d.to_track_quat("Z", "Y")
    mid = (base + tip) / 2
    return cone(r, r2, d.length, mid, mat, rot=q.to_euler(), verts=verts)

def surf(c, radii, d, k=0.96):
    """point on an ellipsoid (centre c, radii) in direction d"""
    d = Vector(d).normalized()
    return Vector(c) + Vector((radii[0] * d.x, radii[1] * d.y, radii[2] * d.z)) * k

def eyes(M, R, c, radii, spread=0.38, up=0.18, size=0.24, glow=None):
    """two big glossy eyes on the front of an ellipsoid head"""
    blacks, shines = [], []
    for s in (-1, 1):
        p = surf(c, radii, (s * spread, -1, up), 0.9)
        blacks.append(ell((size, size * 0.6, size * 1.15), p, glow or "EyeBlack", seg=16, rings=10))
        shines.append(ell((size * 0.36, size * 0.2, size * 0.36), p + Vector((s * -0.03 + 0.05, -size * 0.5, size * 0.38)), "EyeShine", seg=10, rings=6))
    part(M, "Eyes", blacks, R)
    part(M, "Shine", shines, R)

def blush(M, R, c, radii, spread=0.62, up=-0.08, size=0.13):
    part(M, "Blush", [ell((size, size * 0.4, size * 0.6), surf(c, radii, (s * spread, -1, up), 0.93), "Blush", seg=12, rings=6) for s in (-1, 1)], R)

def leg_set(xs, ys, z, r, h, mat):
    return [ell((r, r, h), (x, y, z), mat, seg=12, rings=8) for x in xs for y in ys]

def wing(loc, size, mat, yaw, tilt, roll=0):
    return ell((size[0], size[1], size[2]), loc, mat, rot=(math.radians(roll), math.radians(tilt), math.radians(yaw)), seg=16, rings=8)

def chain(points, r0, r1, mat):
    n = len(points)
    return [ell((r, r, r), p, mat, seg=10, rings=6) for p, r in zip(points, [r0 + (r1 - r0) * i / max(1, n - 1) for i in range(n)])]

# ---------------------------------------------------------------- pets (built at origin, feet at z=0)
def pebblit(R):
    M = "PetPebblit"
    c, rad = (0, 0, 1.0), (1.0, 0.95, 0.85)
    bm = rock_bm(1.0, 2, 0.07, 0.85, 3)
    bm.transform(Matrix.Translation(c))
    spots = inset_patches(bm, 0, 3, 0.02, 0.6, pick=lambda f: f.calc_center_median().y > 0.15 and f.calc_center_median().z > 1.2 and rng.random() < 0.3)
    part(M, "Body", [mesh_obj("b", bm, "Pebble")], R)
    part(M, "Spots", [mesh_obj("s", spots, "PebbleDark")], R)
    part(M, "Feet", leg_set((-0.45, 0.45), (-0.2,), 0.18, 0.32, 0.2, "PebbleDark"), R)
    sp = bmesh.new()
    crystal(sp, Vector((0.15, 0.1, 1.75)), Vector((0.25, 0.1, 1)), 0.55, 0.13)
    crystal(sp, Vector((-0.12, 0.15, 1.75)), Vector((-0.3, 0.2, 1)), 0.4, 0.1)
    part(M, "Sprout", [mesh_obj("sp", sp, "Teal")], R)
    eyes(M, R, c, rad, 0.36, 0.22, 0.22)
    blush(M, R, c, rad)

def cinderpup(R):
    M = "PetCinderpup"
    body_c, body_r = (0, 0.25, 0.95), (0.62, 0.85, 0.55)
    head_c, head_r = (0, -0.55, 1.55), (0.62, 0.56, 0.55)
    part(M, "Body", [ell(body_r, body_c, "Basalt"), ell(head_r, head_c, "Basalt"),
                     ell((0.3, 0.26, 0.22), (0, -1.05, 1.38), "Basalt")] + leg_set((-0.32, 0.32), (-0.2, 0.7), 0.32, 0.17, 0.34, "Basalt"), R)
    part(M, "Ears", [ell((0.16, 0.1, 0.42), (s * 0.5, -0.45, 1.88), "RockDark", rot=(0, math.radians(s * 50), 0)) for s in (-1, 1)], R)
    part(M, "Nose", [ell((0.11, 0.08, 0.08), (0, -1.3, 1.48), "EyeBlack", seg=10, rings=6)], R)
    part(M, "Tail", [cone_to((0, 1.0, 1.05), (0, 1.6, 1.3), 0.14, "Basalt")], R)
    part(M, "Embers", [ell((0.18, 0.24, 0.18), (0, 1.66, 1.33), "Lava")] +
         [ell((0.09, 0.32, 0.06), (x, 0.25 + y, 1.47), "Lava", rot=(0, 0, math.radians(a))) for x, y, a in ((-0.2, -0.1, 20), (0.18, 0.25, -15), (-0.05, 0.6, 5))], R)
    eyes(M, R, head_c, head_r, 0.4, 0.15, 0.17)
    blush(M, R, head_c, head_r, 0.68, -0.18, 0.1)

def glintmoth(R):
    M = "PetGlintmoth"
    body_c, body_r = (0, 0.1, 1.15), (0.42, 0.42, 0.62)
    head_c, head_r = (0, -0.15, 1.95), (0.5, 0.46, 0.46)
    part(M, "Body", [ell(body_r, body_c, "ChargedRock"), ell(head_r, head_c, "ChargedRock")] +
         leg_set((-0.18, 0.18), (-0.05,), 0.45, 0.1, 0.22, "ChargedRock"), R)
    part(M, "Collar", [torus(0.44, 0.15, (0, -0.05, 1.58), "Cream", major=20, minor=8)], R)
    part(M, "Wings", [wing((s * 0.85, 0.35, 1.55), (0.75, 0.05, 0.55), "WingGold", s * 20, s * -25) for s in (-1, 1)] +
         [wing((s * 0.65, 0.4, 0.95), (0.5, 0.05, 0.36), "WingGold", s * 25, s * 30) for s in (-1, 1)], R)
    part(M, "Spots", [ell((0.16, 0.06, 0.16), (s * 1.05, 0.35 - s * 0.06, 1.62), "Bolt", rot=(0, math.radians(s * -25), math.radians(s * 20)), seg=10, rings=6) for s in (-1, 1)], R)
    part(M, "Antennae", [cone_to((s * 0.15, -0.2, 2.35), (s * 0.45, -0.45, 2.85), 0.04, "ChargedRock", 6, 0.03) for s in (-1, 1)], R)
    part(M, "Tips", [ell((0.1, 0.1, 0.1), (s * 0.47, -0.47, 2.88), "Bolt", seg=10, rings=6) for s in (-1, 1)], R)
    eyes(M, R, head_c, head_r, 0.42, 0.05, 0.19)

def rubblord(R):
    M = "PetRubblord"
    c, rad = (0, 0, 1.3), (1.05, 0.95, 1.0)
    bm = rock_bm(1.0, 2, 0.1, 1.0, 9)
    bm.transform(Matrix.Translation(c) @ Matrix.Diagonal((1.05, 0.95, 1.0, 1)))
    part(M, "Body", [mesh_obj("b", bm, "Rubble")], R)
    limbs = []
    for s in (-1, 1):
        a = rock_bm(0.36, 1, 0.15, 1.2, 20 + s)
        a.transform(Matrix.Translation((s * 1.15, -0.1, 1.0)))
        limbs.append(mesh_obj("a", a, "RockDark"))
        f = rock_bm(0.34, 1, 0.12, 0.7, 30 + s)
        f.transform(Matrix.Translation((s * 0.5, -0.1, 0.24)))
        limbs.append(mesh_obj("f", f, "RockDark"))
    part(M, "Limbs", limbs, R)
    cr = bmesh.new()
    for i, (x, h) in enumerate(((-0.5, 0.45), (-0.25, 0.62), (0, 0.8), (0.25, 0.62), (0.5, 0.45))):
        crystal(cr, Vector((x, 0.05, 2.15 - abs(x) * 0.35)), Vector((x * 0.6, 0, 1)), h, 0.11, sides=5)
    part(M, "Crown", [mesh_obj("cr", cr, "Gold")], R)
    eyes(M, R, c, rad, 0.34, 0.28, 0.2)

def emberkit(R):
    M = "PetEmberkit"
    body_c, body_r = (0, 0.25, 0.82), (0.58, 0.78, 0.52)
    head_c, head_r = (0, -0.5, 1.45), (0.66, 0.56, 0.56)
    part(M, "Body", [ell(body_r, body_c, "EmberFur"), ell(head_r, head_c, "EmberFur")] +
         leg_set((-0.3, 0.3), (-0.15, 0.65), 0.25, 0.15, 0.28, "EmberFur"), R)
    part(M, "Ears", [cone_to((s * 0.4, -0.45, 1.85), (s * 0.58, -0.5, 2.38), 0.24, "EmberFur", 4) for s in (-1, 1)], R)
    part(M, "Muzzle", [ell((0.28, 0.16, 0.18), (0, -1.0, 1.3), "Cream")] + leg_set((-0.3, 0.3), (-0.2,), 0.08, 0.15, 0.08, "Cream"), R)
    flame = [cone_to((0, 0.9, 0.9), (0, 1.45, 1.2), 0.2, "Lava", 8), cone_to((0, 1.4, 1.15), (0.08, 1.85, 1.45), 0.15, "Lava", 8),
             ell((0.11, 0.11, 0.11), (0.08, 1.87, 1.46), "Lava", seg=8, rings=6)]
    flame += [cone_to((s * 0.42, -0.52, 1.92), (s * 0.55, -0.6, 2.22), 0.11, "Lava", 4) for s in (-1, 1)]  # inner ears
    part(M, "Flame", flame, R)
    eyes(M, R, head_c, head_r, 0.4, 0.12, 0.18)
    blush(M, R, head_c, head_r, 0.66, -0.2, 0.1)

def magmaw(R):
    M = "PetMagmaw"
    c, rad = (0, 0, 0.92), (1.0, 0.92, 0.82)
    part(M, "Body", [ell(rad, c, "Basalt", seg=24, rings=14)] + leg_set((-0.55, 0.55), (-0.2, 0.4), 0.14, 0.2, 0.16, "RockDark"), R)
    part(M, "Mouth", [ell((0.55, 0.12, 0.26), surf(c, rad, (0, -1, -0.15), 0.93), "Lava")], R)
    teeth = [cone_to(surf(c, rad, (x, -1, 0.05), 0.92) + Vector((0, -0.08, 0)), surf(c, rad, (x, -1, 0.05), 0.92) + Vector((0, -0.12, -0.2)), 0.08, "Cream", 4) for x in (-0.25, 0.25)]
    part(M, "Teeth", teeth, R)
    bm = rock_bm(1.0, 2, 0.0, 1.0, 1)
    bm.transform(Matrix.Translation(c) @ Matrix.Diagonal((rad[0], rad[1], rad[2], 1)))
    cracks = inset_patches(bm, 0, 5, 0.02, 0.55, pick=lambda f: f.calc_center_median().y > -0.2 and rng.random() < 0.35)
    bm.free()
    part(M, "Cracks", [mesh_obj("cr", cracks, "Lava")], R)
    part(M, "Horns", [cone_to((s * 0.42, -0.1, 1.62), (s * 0.62, -0.1, 2.05), 0.13, "RockDark", 6) for s in (-1, 1)], R)
    eyes(M, R, c, rad, 0.4, 0.45, 0.19)

def flarefly(R):
    M = "PetFlarefly"
    head_c, head_r = (0, -0.35, 1.55), (0.55, 0.5, 0.5)
    part(M, "Body", [ell(head_r, head_c, "Flare"), ell((0.38, 0.42, 0.38), (0, 0.2, 1.4), "Flare")], R)
    part(M, "Glow", [ell((0.4, 0.55, 0.4), (0, 0.75, 1.25), "Glow")], R)
    part(M, "Wings", [wing((s * 0.55, 0.2, 2.0), (0.55, 0.05, 0.3), "Wing", s * 35, s * -40) for s in (-1, 1)] +
         [wing((s * 0.5, 0.45, 1.85), (0.42, 0.05, 0.24), "Wing", s * 60, s * -30) for s in (-1, 1)], R)
    part(M, "Antennae", [cone_to((s * 0.15, -0.45, 1.98), (s * 0.4, -0.7, 2.45), 0.04, "EmberFur", 6, 0.03) for s in (-1, 1)], R)
    part(M, "Tips", [ell((0.09, 0.09, 0.09), (s * 0.42, -0.72, 2.48), "Bolt", seg=8, rings=6) for s in (-1, 1)], R)
    part(M, "Legs", [cone_to((x, y, 1.1), (x * 1.4, y - 0.05, 0.82), 0.05, "EmberFur", 6, 0.03) for x in (-0.2, 0.2) for y in (-0.1, 0.25)], R)
    eyes(M, R, head_c, head_r, 0.42, 0.1, 0.18)
    blush(M, R, head_c, head_r, 0.68, -0.2, 0.09)

def solarix(R):
    M = "PetSolarix"
    c, rad = (0, 0, 1.55), (0.85, 0.8, 0.85)
    part(M, "Body", [ell(rad, c, "SunGold", seg=24, rings=14)], R)
    rays = []
    for i in range(12):
        a = i * math.pi / 6
        d = Vector((math.cos(a), 0.15, math.sin(a)))
        b = Vector(c) + d * 0.78
        rays.append(cone_to(b, Vector(c) + d * (1.45 if i % 2 == 0 else 1.2), 0.2, "Gold", 6))
    part(M, "Rays", rays, R)
    part(M, "Halo", [torus(0.55, 0.06, (0, 0.1, 2.7), "Gold", major=28, minor=6)], R)
    part(M, "Wisp", [cone_to((0, 0.2, 0.85), (0, 0.4, 0.2), 0.38, "SunGold", 12)], R)
    eyes(M, R, c, rad, 0.36, 0.12, 0.2)
    blush(M, R, c, rad, 0.62, -0.15, 0.12)

def frostling(R):
    M = "PetFrostling"
    c, rad = (0, 0, 1.05), (0.68, 0.62, 0.92)
    part(M, "Body", [ell(rad, c, "IceRock", seg=22, rings=14)], R)
    part(M, "Belly", [ell((0.5, 0.2, 0.62), (0, -0.48, 0.92), "Snow")], R)
    part(M, "Flippers", [ell((0.12, 0.25, 0.48), (s * 0.68, -0.05, 0.95), "IceRock", rot=(0, math.radians(s * 25), 0)) for s in (-1, 1)], R)
    part(M, "Feet", [ell((0.2, 0.28, 0.08), (s * 0.28, -0.25, 0.08), "Orange", seg=12, rings=6) for s in (-1, 1)] +
         [cone_to((0, -0.62, 1.3), (0, -0.88, 1.25), 0.1, "Orange", 6)], R)
    cr = bmesh.new()
    for x, h, t in ((-0.22, 0.45, -0.35), (0, 0.65, 0), (0.22, 0.45, 0.35)):
        crystal(cr, Vector((x, 0.05, 1.85)), Vector((t, 0.1, 1)), h, 0.12, sides=6)
    part(M, "Crystals", [mesh_obj("cr", cr, "Ice")], R)
    eyes(M, R, c, rad, 0.36, 0.35, 0.18)
    blush(M, R, c, rad, 0.62, 0.15, 0.1)

def shardbun(R):
    M = "PetShardbun"
    body_c, body_r = (0, 0.25, 0.75), (0.62, 0.7, 0.58)
    head_c, head_r = (0, -0.35, 1.38), (0.58, 0.52, 0.52)
    part(M, "Body", [ell(body_r, body_c, "Snow"), ell(head_r, head_c, "Snow")] +
         [ell((0.2, 0.36, 0.12), (s * 0.35, -0.25, 0.12), "Snow", seg=12, rings=8) for s in (-1, 1)], R)
    part(M, "Tail", [ell((0.24, 0.24, 0.24), (0, 0.95, 0.85), "White", seg=12, rings=8)], R)
    ears = bmesh.new()
    for s in (-1, 1):
        crystal(ears, Vector((s * 0.22, -0.25, 1.75)), Vector((s * 0.35, 0.15, 1)), 1.15, 0.16, sides=5)
    part(M, "Ears", [mesh_obj("ea", ears, "IceTeal")], R)
    part(M, "Nose", [ell((0.07, 0.05, 0.05), (0, -0.87, 1.33), "Blush", seg=8, rings=6)], R)
    eyes(M, R, head_c, head_r, 0.4, 0.15, 0.17)
    blush(M, R, head_c, head_r, 0.66, -0.15, 0.1)

def glacio(R):
    M = "PetGlacio"
    body_c, body_r = (0, 0.35, 0.62), (0.7, 1.05, 0.55)
    head_c, head_r = (0, -0.6, 1.2), (0.6, 0.55, 0.52)
    part(M, "Body", [ell(body_r, body_c, "Glacio"), ell(head_r, head_c, "Glacio"), ell((0.45, 0.35, 0.4), (0, -0.25, 0.85), "Glacio")], R)
    part(M, "Flippers", [ell((0.42, 0.18, 0.06), (s * 0.68, -0.15, 0.25), "Glacio", rot=(0, 0, math.radians(s * 30))) for s in (-1, 1)] +
         [ell((0.36, 0.14, 0.05), (s * 0.25, 1.38, 0.32), "Glacio", rot=(0, 0, math.radians(s * 50))) for s in (-1, 1)], R)
    part(M, "Muzzle", [ell((0.3, 0.16, 0.18), (0, -1.08, 1.04), "Snow")], R)
    part(M, "Tusks", [cone_to((s * 0.12, -1.15, 0.95), (s * 0.15, -1.2, 0.55), 0.06, "White", 6) for s in (-1, 1)], R)
    cr = bmesh.new()
    for d in ((0, 0.2, 1), (-0.3, 0.6, 1), (0.3, 0.6, 1), (0, 1.0, 1)):
        crystal(cr, Vector((d[0] * 0.8, d[1], 1.08 - abs(d[0]) * 0.3 - (d[1] - 0.2) * 0.2)), Vector((d[0], 0.15, 1)), 0.5, 0.11, sides=6)
    part(M, "Crystals", [mesh_obj("cr", cr, "IceTeal")], R)
    eyes(M, R, head_c, head_r, 0.42, 0.25, 0.17)

def aurorabe(R):
    M = "PetAurorabe"
    c, rad = (0, 0, 1.75), (0.95, 0.9, 0.7)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=14, radius=1)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < -0.25], context="VERTS")
    bm.transform(Matrix.Translation(c) @ Matrix.Diagonal((rad[0], rad[1], rad[2], 1)))
    o = mesh_obj("bell", bm, "Aurora", smooth=True)
    s = o.modifiers.new("Solid", "SOLIDIFY")
    s.thickness = 0.12
    part(M, "Bell", [o], R)
    part(M, "Rim", [torus(0.9, 0.08, (0, 0, 1.58), "Pink", major=32, minor=6)], R)
    tend = []
    for i in range(6):
        a = i * math.pi / 3 + 0.3
        pts = [Vector((math.cos(a) * (0.55 - k * 0.04) + math.sin(k * 1.3 + i) * 0.1, math.sin(a) * (0.55 - k * 0.04), 1.45 - k * 0.22)) for k in range(6)]
        tend += chain(pts, 0.11, 0.05, "Pink" if i % 2 else "Cyan")
    part(M, "Tendrils", tend, R)
    part(M, "Spots", [ell((0.12, 0.06, 0.12), surf(c, rad, d, 0.98), "Pink", seg=8, rings=6) for d in ((0.6, 0.3, 0.8), (-0.6, 0.3, 0.8), (0, 0.6, 0.9), (0.2, -0.2, 1))], R)
    eyes(M, R, c, rad, 0.36, -0.05, 0.2)
    blush(M, R, c, rad, 0.62, -0.25, 0.11)

def nebulynx(R):
    M = "PetNebulynx"
    body_c, body_r = (0, 0.25, 0.85), (0.6, 0.8, 0.55)
    head_c, head_r = (0, -0.5, 1.5), (0.68, 0.58, 0.58)
    part(M, "Body", [ell(body_r, body_c, "CosmicRock"), ell(head_r, head_c, "CosmicRock")] +
         leg_set((-0.32, 0.32), (-0.15, 0.65), 0.27, 0.16, 0.3, "CosmicRock") +
         [cone_to((s * 0.42, -0.45, 1.9), (s * 0.6, -0.5, 2.45), 0.25, "CosmicRock", 4) for s in (-1, 1)] +
         [ell((0.12, 0.12, 0.55), (0, 1.15, 1.25), "CosmicRock", rot=(math.radians(-35), 0, 0))], R)
    part(M, "Tufts", [cone_to((s * 0.6, -0.5, 2.42), (s * 0.66, -0.52, 2.78), 0.06, "CosmicGlow", 4) for s in (-1, 1)] +
         [ell((0.15, 0.15, 0.18), (0, 1.45, 1.7), "CosmicGlow", seg=10, rings=6)], R)
    part(M, "Stars", [ell((0.09, 0.09, 0.05), surf(body_c, body_r, d, 1.0), "CosmicGlow", seg=8, rings=6)
                      for d in ((0.5, 0.2, 0.8), (-0.4, 0.5, 0.8), (0.1, 0.9, 0.6), (-0.6, -0.1, 0.6), (0.7, 0.6, 0.3))], R)
    part(M, "Muzzle", [ell((0.26, 0.14, 0.16), (0, -1.03, 1.35), "Snow")], R)
    eyes(M, R, head_c, head_r, 0.42, 0.12, 0.19, glow=None)

def voidling(R):
    M = "PetVoidling"
    c, rad = (0, 0, 1.55), (0.72, 0.68, 0.78)
    part(M, "Body", [ell(rad, c, "Void", seg=22, rings=14), cone_to((0, 0.1, 1.0), (0.25, 0.55, 0.25), 0.55, "Void", 14),
                     ell((0.14, 0.14, 0.26), (-0.72, -0.1, 1.35), "Void", rot=(0, math.radians(-30), 0)),
                     ell((0.14, 0.14, 0.26), (0.72, -0.1, 1.35), "Void", rot=(0, math.radians(30), 0))], R)
    part(M, "Ring", [torus(1.05, 0.06, (0, 0.05, 1.55), "Cyan", rot=(math.radians(72), math.radians(15), 0), major=32, minor=6)], R)
    part(M, "Wisp", [ell((0.1, 0.1, 0.1), (0.27, 0.58, 0.2), "Cyan", seg=8, rings=6)], R)
    eyes(M, R, c, rad, 0.36, 0.12, 0.2, glow="Cyan")

def starwhale(R):
    M = "PetStarwhale"
    c, rad = (0, 0.1, 1.2), (0.82, 1.15, 0.75)
    part(M, "Body", [ell(rad, c, "Whale", seg=24, rings=14),
                     ell((0.18, 0.4, 0.06), (0, 1.55, 1.45), "Whale", rot=(math.radians(25), 0, 0)),
                     ell((0.5, 0.22, 0.05), (-0.32, 1.85, 1.62), "Whale", rot=(math.radians(20), 0, math.radians(-20))),
                     ell((0.5, 0.22, 0.05), (0.32, 1.85, 1.62), "Whale", rot=(math.radians(20), 0, math.radians(20)))] +
         [ell((0.4, 0.18, 0.05), (s * 0.82, -0.05, 0.85), "Whale", rot=(math.radians(-10), math.radians(s * 35), math.radians(s * 20))) for s in (-1, 1)], R)
    part(M, "Belly", [ell((0.62, 0.95, 0.4), (0, -0.05, 0.85), "WhaleBelly")], R)
    st = bmesh.new()
    pts = []
    for i in range(10):
        a = i * math.pi / 5 + math.pi / 2
        r = 0.36 if i % 2 == 0 else 0.15
        pts.append((math.cos(a) * r, math.sin(a) * r))
    top = [st.verts.new((x, y, 0.07)) for x, y in pts]
    bot = [st.verts.new((x, y, -0.07)) for x, y in pts]
    st.faces.new(top)
    st.faces.new(bot[::-1])
    for i in range(10):
        j = (i + 1) % 10
        st.faces.new((bot[i], bot[j], top[j], top[i]))
    st.transform(Matrix.Translation((0, -0.15, 2.0)) @ Matrix.Rotation(math.radians(-80), 4, "X"))
    part(M, "Star", [mesh_obj("st", st, "Gold")], R)
    part(M, "Freckles", [ell((0.06, 0.03, 0.06), surf(c, rad, d, 1.0), "Gold", seg=8, rings=6)
                         for d in ((0.6, 0.1, 0.7), (-0.6, 0.3, 0.7), (0.2, 0.5, 0.9), (-0.25, 0.75, 0.6))], R)
    part(M, "Spout", chain([Vector((0, -0.1, 2.15 + k * 0.22)) for k in range(3)], 0.1, 0.06, "Cyan"), R)
    eyes(M, R, c, rad, 0.45, 0.3, 0.22)
    blush(M, R, c, rad, 0.7, 0.02, 0.1)

def celestia(R):
    M = "PetCelestia"
    body_c, body_r = (0, 0.25, 1.05), (0.55, 0.72, 0.55)
    head_c, head_r = (0, -0.45, 1.75), (0.66, 0.6, 0.6)
    part(M, "Body", [ell(body_r, body_c, "Celest"), ell(head_r, head_c, "Celest")] +
         leg_set((-0.28, 0.28), (-0.05, 0.6), 0.45, 0.14, 0.3, "Celest") +
         [cone_to((s * 0.42, -0.35, 2.15), (s * 0.62, -0.35, 2.6), 0.2, "Celest", 6) for s in (-1, 1)], R)
    feathers = []
    for s in (-1, 1):
        for k, (l, a) in enumerate(((0.8, 30), (0.65, 10), (0.5, -10))):
            feathers.append(wing((s * (0.55 + l * 0.6), 0.45 + k * 0.08, 1.55 + k * 0.1 + l * 0.25), (l, 0.06, 0.2), "Wing", s * -10, s * -a))
    part(M, "Wings", feathers, R)
    part(M, "Horn", [cone_to((0, -0.85, 2.18), (0, -1.05, 2.75), 0.12, "Gold", 8)], R)
    part(M, "Halo", [torus(0.42, 0.05, (0, -0.35, 2.65), "Pink", major=28, minor=6)], R)
    part(M, "Tail", [ell((0.1, 0.1, 0.45), (0, 1.0, 1.25), "Celest", rot=(math.radians(-40), 0, 0)),
                     ell((0.2, 0.2, 0.2), (0, 1.3, 1.58), "Pink", seg=10, rings=6)], R)
    part(M, "Mane", [ell((0.18, 0.18, 0.18), (0, -0.2 + k * 0.22, 2.3 - k * 0.12), "Pink", seg=10, rings=6) for k in range(4)], R)
    eyes(M, R, head_c, head_r, 0.4, 0.12, 0.19)
    blush(M, R, head_c, head_r, 0.66, -0.18, 0.11)

PETS = [("Pebblit", pebblit), ("Cinderpup", cinderpup), ("Glintmoth", glintmoth), ("Rubblord", rubblord),
        ("Emberkit", emberkit), ("Magmaw", magmaw), ("Flarefly", flarefly), ("Solarix", solarix),
        ("Frostling", frostling), ("Shardbun", shardbun), ("Glacio", glacio), ("Aurorabe", aurorabe),
        ("Nebulynx", nebulynx), ("Voidling", voidling), ("Starwhale", starwhale), ("Celestia", celestia)]

# ---------------------------------------------------------------- eggs (pivot = bottom centre)
def egg_bm(h=3.4, w=2.5, seed=0, jitter=0.0):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=3, radius=1)
    r = random.Random(seed)
    for v in bm.verts:
        z = v.co.z
        k = 1 - 0.18 * z  # narrower top
        v.co.x *= w / 2 * k
        v.co.y *= w / 2 * k
        v.co.z = (z + 1) / 2 * h
        if jitter:
            v.co *= 1 + r.uniform(-jitter, jitter)
    return bm

def egg(R, name, shell, accent, seed):
    M = "Egg" + name
    bm = egg_bm(seed=seed)
    if accent == "spots":
        a = inset_patches(bm, 0, seed, 0.03, 0.75, pick=lambda f: rng.random() < 0.16)
        part(M, "Spots", [mesh_obj("a", a, "PebbleDark")], R)
    elif accent == "lava":
        a = inset_patches(bm, 0, seed, 0.03, 0.8, pick=lambda f: abs(math.sin(f.calc_center_median().z * 2.3 + math.atan2(f.calc_center_median().y, f.calc_center_median().x) * 2)) < 0.22)
        part(M, "Cracks", [mesh_obj("a", a, "Lava")], R)
    elif accent == "ice":
        cr = bmesh.new()
        for i in range(10):
            a = i * 2 * math.pi / 10
            base = Vector((math.cos(a) * 1.05, math.sin(a) * 1.05, 0.35 + (i % 2) * 0.15))
            crystal(cr, base, Vector((math.cos(a) * 0.45, math.sin(a) * 0.45, 1)), 0.7 + (i % 3) * 0.25, 0.17, sides=6)
        part(M, "Crystals", [mesh_obj("cr", cr, "Ice")], R)
        a = inset_patches(bm, 0, seed, 0.02, 0.8, pick=lambda f: f.calc_center_median().z > 2.75 or rng.random() < 0.06)
        part(M, "Frost", [mesh_obj("f", a, "Snow")], R)
    elif accent == "cosmic":
        a = inset_patches(bm, 0, seed, 0.03, 0.55, pick=lambda f: rng.random() < 0.1)
        part(M, "Stars", [mesh_obj("a", a, "CosmicGlow")], R)
        part(M, "Ring", [torus(1.65, 0.09, (0, 0, 1.6), "Teal", rot=(math.radians(70), math.radians(12), 0), major=40, minor=6)], R)
    part(M, "Shell", [mesh_obj("s", bm, shell, smooth=True)], R)

EGGS = [("Rock", "Pebble", "spots"), ("Ember", "Basalt", "lava"), ("Frost", "IceRock", "ice"), ("Cosmic", "CosmicRock", "cosmic")]

# ---------------------------------------------------------------- gadgets
def forge_drone(R):
    M = "ForgeDrone"
    part(M, "Body", [ell((1.3, 1.3, 1.0), (0, 0, 0), "Red", seg=24, rings=14)], R, pivot=(0, 0, 0))
    part(M, "Band", [torus(1.32, 0.18, (0, 0, -0.05), "Cream", major=32, minor=8)], R, pivot=(0, 0, 0))
    part(M, "Eye", [ell((0.5, 0.25, 0.5), (0, -1.12, 0.1), "Teal", seg=16, rings=10)], R)
    part(M, "Visor", [torus(0.55, 0.08, (0, -1.15, 0.1), "Dark", rot=(math.radians(90), 0, 0), major=24, minor=6)], R)
    arms = []
    for i in range(4):
        a = i * math.pi / 2 + math.pi / 4
        hub = Vector((math.cos(a) * 2.3, math.sin(a) * 2.3, 0.75))
        arms.append(cone_to(Vector((math.cos(a) * 1.0, math.sin(a) * 1.0, 0.3)), hub, 0.18, "Steel", 8, 0.14))
        arms.append(cyl(0.42, 0.35, hub, "Steel", "Z", 16, 0.05))
        blades = [box((2.2, 0.32, 0.08), hub + Vector((0, 0, 0.3)), "SteelLight", 0.03, 1, rot=(0, 0, a)),
                  box((2.2, 0.32, 0.08), hub + Vector((0, 0, 0.3)), "SteelLight", 0.03, 1, rot=(0, 0, a + math.pi / 2)),
                  cyl(0.15, 0.25, hub + Vector((0, 0, 0.3)), "Yellow", "Z", 10, 0.03)]
        part(M, f"Rotor{i + 1}", blades, R, pivot=tuple(hub + Vector((0, 0, 0.3))))
    part(M, "Arms", arms, R)
    part(M, "Claw", [cyl(0.22, 0.8, (0, 0, -1.25), "Steel", "Z", 12, 0.04)] +
         [cone_to((math.cos(a) * 0.2, math.sin(a) * 0.2, -1.6), (math.cos(a) * 0.55, math.sin(a) * 0.55, -2.2), 0.1, "Yellow", 6, 0.06) for a in (0, 2.09, 4.19)], R)
    part(M, "Lights", [ell((0.12, 0.12, 0.12), (math.cos(a) * 1.25, math.sin(a) * 1.25, 0.35), "Green", seg=8, rings=6) for a in (0.6, 2.5, 3.8, 5.6)], R)

def launch_pad(R):
    M = "LaunchPad"
    oct8 = cyl(4.5 / math.cos(math.pi / 8), 0.8, (0, 0, 0.4), "Steel", "Z", 8, 0.12)
    oct8.rotation_euler.z = math.pi / 8
    part(M, "Base", [oct8], R)
    rim = cyl(4.2 / math.cos(math.pi / 8), 0.3, (0, 0, 0.95), "Yellow", "Z", 8, 0.06)
    rim.rotation_euler.z = math.pi / 8
    part(M, "Rim", [rim], R)
    top = cyl(3.5, 0.25, (0, 0, 1.05), "Teal", "Z", 32, 0.04)
    part(M, "Top", [top], R)
    chev = []
    for k in range(3):
        y = 1.6 - k * 1.6
        for s in (-1, 1):
            chev.append(box((1.6, 0.42, 0.18), (s * 0.55, y, 1.25), "Cream", 0.04, 1, rot=(0, 0, math.radians(s * 35))))
    part(M, "Chevrons", chev, R)
    springs = []
    for a in (0.4, 2.0, 3.6, 5.2):
        p = Vector((math.cos(a) * 3.9, math.sin(a) * 3.9, 0))
        for z in (0.95, 1.2, 1.45):
            springs.append(torus(0.32, 0.07, (p.x, p.y, z), "SteelLight", major=16, minor=6))
        springs.append(cyl(0.38, 0.12, (p.x, p.y, 1.6), "Red", "Z", 12, 0.03))
    part(M, "Springs", springs, R)

# ---------------------------------------------------------------- build
def build_all():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for k, (n, fn) in enumerate(PETS):
        r = root("Pet" + n, 0)
        fn(r)
        r.location = (-21 + (k % 8) * 6, -6 + (k // 8) * 8, 0)
    for k, (n, shell, acc) in enumerate(EGGS):
        r = root("Egg" + n, 0)
        egg(r, n, shell, acc, 40 + k)
        r.location = (-9 + k * 6, 12, 0)
    r = root("ForgeDrone", 0)
    forge_drone(r)
    r.location = (18, 12, 3)
    r = root("LaunchPad", 0)
    launch_pad(r)
    r.location = (-24, 14, 0)

if __name__ == "__main__":
    build_all()
    bpy.context.view_layer.update()
    for k, v in MD.heights().items():
        print(f"{k}: height {v[0]}  parts {v[1]}  tris {v[2]}")
    if "--export" in sys.argv:
        BM.export_fbx(os.path.join(OUT, "SF_Pets.fbx"))
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "SF_Pets.blend"))
        print("exported")
    if "--render" in sys.argv:
        BM.setup_render(1400, 520, 20)
        cam = bpy.context.scene.camera
        roots = {o.name: o for o in bpy.data.objects if o.type == "EMPTY"}
        def shot(names, spacing, z, dist, lens, fname, lift=0):
            for n, r in roots.items():
                for c in r.children:
                    c.hide_render = n not in names
            for k, n in enumerate(names):
                roots[n].location = ((k - (len(names) - 1) / 2) * spacing, 0, lift if n == "ForgeDrone" else 0)
            cam.location = (0, -dist, z + dist * 0.28)
            cam.data.lens = lens
            cam.rotation_euler = (Vector((0, 0, z)) - cam.location).to_track_quat("-Z", "Y").to_euler()
            bpy.context.scene.render.filepath = os.path.join(OUT, fname)
            bpy.ops.render.render(write_still=True)
        pets = ["Pet" + n for n, _ in PETS]
        for g in range(4):
            shot(pets[g * 4:g * 4 + 4], 3.4, 1.3, 17, 50, f"preview_pets_{g + 1}.png")
        shot(["Egg" + n for n, _, _ in EGGS], 3.6, 1.7, 19, 50, "preview_eggs.png")
        shot(["LaunchPad", "ForgeDrone"], 10, 2.5, 26, 40, "preview_gadgets.png", lift=4)
        print("rendered")
