"""
Starfall Forge - pets v2 (T-04-02): 18 rigged + animated pets, 5 rigged eggs with hatch clips, the Pet Fuser.
Run headless (Blender 5.x as a Python module or `blender -b -P`):
  python3 build_pets_v2.py --export     build, budget table (fails on over-budget), save SF_Pets_v2.blend,
                                         export SF_Pets_v2.fbx (rigs, no animation) + art/models/anims/<Clip>.fbx
  python3 build_pets_v2.py --verify     re-import every exported FBX in a fresh scene: up axis, front, bounding
                                         boxes, bone counts, clip lengths, clip bone motion vs the .blend
  python3 build_pets_v2.py --render     renders from the re-imported FBX: preview_pets_v2_sheet.png,
                                         preview_eggs_v2.png, preview_fuser_v2.png, compare/<Name>.png
  python3 build_pets_v2.py --gifs [Name ...]  one preview GIF per clip into art/models/anims/preview/

Source of truth for shapes + colours: Astra's sheets art/concepts/PETS/PET-*.png (hex codes -> MatKeys in
build_machines.PALETTE). Same rules as build_pets.py: every part is its own object <Model>__<Part>__<MatKey>, no
textures, Roblox assigns Material + Color from MatKey (tools/ApplyPets.luau). 1 unit = 1 stud, Z up, -Y = face.
Pivot = bottom centre (Root bone at the origin of every rig).

Rigs: armature <Model>__Rig, every mesh 100 % weighted to one bone (rigid toy parts). All bones point straight up
with roll 180 deg, so after the export axis change every bone's rest orientation is the identity in Roblox and the
same clip means the same motion on every rig that has the bone. Clips are rotation + translation only (Roblox
Bone.Transform is a CFrame: no scale).

Export axes: axis_forward='Z', axis_up='Y', with the axis change baked into the data (see export_fbx). Blender's
"forward" is +Y, our models face -Y, so Blender +Y -> FBX +Z puts every face on FBX -Z = Roblox LookVector, and
Blender +Z -> FBX +Y = Roblox up. Every FBX node then has an identity rotation, so the importer has nothing to
apply twice or to drop (SF_Pets.fbx came in lying on its face).
"""
import bpy, bmesh, math, os, sys, random, re, json, time
from mathutils import Vector, Matrix, Euler, Quaternion

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
ART = os.path.join(REPO, "art", "models")
ANIM = os.path.join(ART, "anims")
PREV = os.path.join(ANIM, "preview")
CMP = os.path.join(ART, "compare")
SHEETS = os.path.join(REPO, "art", "concepts", "PETS")
FBX_MAIN = os.path.join(ART, "SF_Pets_v2.fbx")
BLEND = os.path.join(ART, "SF_Pets_v2.blend")
SPLIT = os.path.join(ART, "split")

sys.path.insert(0, HERE)
import build_machines as BM
import build_models as MD  # noqa: F401  (adds its MatKeys to BM.PALETTE)
import build_pets as P1     # noqa: F401  (v1 helpers + MatKeys: EyeBlack, EyeShine, Snow, Cyan, Pink, Void ...)
from build_machines import box, cyl, part as bm_part
from build_models import mesh_obj, crystal, torus
from build_pets import cone_to, surf

FPS = 30
LIMITS = {"pet_tris": 1500, "Celestia_tris": 2500, "egg_tris": 800, "fuser_tris": 3000, "pet_parts": 25, "bones": 12}
FETCH = {"Pebblit", "Cinderpup", "Voidling", "Celestia", "Coreling"}  # Shared.Pets perk FETCH (+ Coreling BREACH+FETCH)


# ======================================================================= geometry helpers
def frame(n, up=(0, 0, 1)):
    """3x3 basis whose local -Y points along n (outward) and local Z points as close to `up` as possible"""
    y = -Vector(n).normalized()
    u = Vector(up)
    z = u - y * u.dot(y)
    if z.length < 1e-4:
        z = Vector((0, 1, 0)) - y * y.y
    z.normalize()
    x = y.cross(z)
    return Matrix((x, y, z)).transposed()


def ell_normal(c, r, p):
    d = Vector(p) - Vector(c)
    return Vector((d.x / r[0] ** 2, d.y / r[1] ** 2, d.z / r[2] ** 2)).normalized()


def on(c, r, d, k=1.0):
    """point on ellipsoid (centre c, radii r) in direction d, and the surface normal there"""
    p = surf(c, r, d, k)
    return p, ell_normal(c, r, p)


def fac(radii, loc, mat, sub=2, keep=0.8, seed=0, jit=0.025, rot=(0, 0, 0), zcut=None):
    """faceted 'vinyl stone' ellipsoid: jittered icosphere, decimated, flat shaded (Astra's low-poly look)"""
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=1.0)
    r = random.Random(seed)
    for v in bm.verts:
        v.co *= 1 + r.uniform(-jit, jit)
    if zcut is not None:  # flatten the bottom (bells, domes)
        for v in bm.verts:
            v.co.z = max(v.co.z, zcut)
    bm.transform(Matrix.Translation(loc) @ Euler(rot).to_matrix().to_4x4() @ Matrix.Diagonal((*radii, 1)))
    o = mesh_obj("f", bm, mat, smooth=False)
    if keep < 1:
        d = o.modifiers.new("Dec", "DECIMATE")
        d.ratio = keep
    return o


def blob(radii, loc, mat, rot=(0, 0, 0), seed=0):
    """cheap faceted lump (20-80 tris): legs, paws, ears, spots"""
    return fac(radii, loc, mat, sub=1, keep=0.85, seed=seed, jit=0.03, rot=rot)


def spot(p, n, r, mat, depth=0.3):
    """flat low-poly chip lying on a surface (speckles, spots)"""
    F = frame(n)
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.0)
    bm.transform(Matrix.Translation(Vector(p) - Vector(n) * r * depth * 0.2) @ F.to_4x4() @ Matrix.Diagonal((r, r * depth, r * 0.85, 1)))
    o = mesh_obj("sp", bm, mat)
    d = o.modifiers.new("Dec", "DECIMATE")
    d.ratio = 0.35
    return o


def smooth_ell(radii, loc, mat, M3=None, seg=12, rings=8, front_only=False):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=rings, radius=1)
    if front_only:  # keep the outward half (local -Y)
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.y > 0.25], context="VERTS")
    T = Matrix.Translation(loc) @ (M3.to_4x4() if M3 is not None else Matrix.Identity(4)) @ Matrix.Diagonal((*radii, 1))
    bm.transform(T)
    return mesh_obj("e", bm, mat, smooth=True)


def eyes(c, r, spread=0.4, up=0.0, size=0.22, depth=0.42):
    """big glossy black eyes on an ellipsoid head + one white glint each (upper right, like the sheets)"""
    blacks, shines = [], []
    for s in (-1, 1):
        p, n = on(c, r, (s * spread, -1, up), 0.97)
        F = frame(n)
        blacks.append(smooth_ell((size, size * depth, size * 1.12), p, "EyeBlack", F, 12, 8, front_only=True))
        g = p + F @ Vector((size * 0.34, -size * depth * 0.9, size * 0.45))
        shines.append(smooth_ell((size * 0.2, size * 0.12, size * 0.2), g, "EyeShine", F, 6, 4))
    return blacks, shines


def gem(p, n, w, h, d, mat, up=(0, 0, 1), back=0.35):
    """octahedron gem sitting on a surface (diamonds on chests/foreheads, veins when long + thin)"""
    F = frame(n, up)
    bm = bmesh.new()
    vs = [bm.verts.new(Vector(p) + F @ Vector(q)) for q in ((w, 0, 0), (0, 0, h), (-w, 0, 0), (0, 0, -h), (0, -d, 0), (0, d * back, 0))]
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new((vs[i], vs[j], vs[4]))
        bm.faces.new((vs[j], vs[i], vs[5]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return mesh_obj("g", bm, mat)


def star(p, n, R, r, t, mat, points=4, up=(0, 0, 1)):
    """flat n-point star prism lying on a surface (star speckles, star shards)"""
    F = frame(n, up)
    bm = bmesh.new()
    pts = []
    for i in range(points * 2):
        a = i * math.pi / points + math.pi / 2
        rr = R if i % 2 == 0 else r
        pts.append(Vector((math.cos(a) * rr, 0, math.sin(a) * rr)))
    front = [bm.verts.new(Vector(p) + F @ (q + Vector((0, -t / 2, 0)))) for q in pts]
    back = [bm.verts.new(Vector(p) + F @ (q + Vector((0, t / 2, 0)))) for q in pts]
    bm.faces.new(front)
    bm.faces.new(back[::-1])
    k = len(pts)
    for i in range(k):
        j = (i + 1) % k
        bm.faces.new((front[j], front[i], back[i], back[j]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return mesh_obj("s", bm, mat)


def crystals(spec, mat, sides=5):
    """spec: [(base, direction, length, radius)] -> one object of pointed prisms"""
    bm = bmesh.new()
    for base, d, L, rad in spec:
        crystal(bm, Vector(base), Vector(d), L, rad, sides=sides)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return mesh_obj("c", bm, mat)


def pyramid(base, tip, r, mat, sides=4, twist=0.0):
    """faceted cone/pyramid from base centre to tip (ears, spikes, mane plates)"""
    return P1.cone(r, 0, (Vector(tip) - Vector(base)).length, (Vector(base) + Vector(tip)) / 2, mat,
                   rot=((Vector(tip) - Vector(base)).to_track_quat("Z", "Y") @ Quaternion((0, 0, 1), twist)).to_euler(), verts=sides)


def seg(a, b, r1, r2, mat, sides=6):
    """faceted tapered limb segment from a to b"""
    return cone_to(a, b, r1, mat, sides, r2)


# ======================================================================= model + rig
class Model:
    def __init__(self, name, kind="pet"):
        self.name, self.kind = name, kind
        self.parts = []  # (object, bone)
        self.bones = []  # (name, head, parent)
        self.arch = None
        self.arm = None
        self.root = None
        self.clips = {}  # clip -> (frames, loop, markers)

    def add(self, pname, objs, bone):
        """join objs into <Model>__<pname>__<MatKey> weighted to `bone`; a second material becomes <pname><MatKey>"""
        objs = objs if isinstance(objs, list) else [objs]
        by = {}
        for o in objs:
            by.setdefault(o["mat"], []).append(o)
        first = None
        for i, (mat, group) in enumerate(by.items()):
            o = bm_part(self.name, pname if i == 0 else pname + mat, group, None)
            self.parts.append((o, bone))
            first = first or o
        return first

    def bone(self, name, head, parent="Root"):
        self.bones.append((name, Vector(head), parent))


def make_rig(M):
    ad = bpy.data.armatures.new(M.name + "__Rig")
    arm = bpy.data.objects.new(M.name + "__Rig", ad)
    bpy.context.scene.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="EDIT")
    for n, head, par in [("Root", Vector((0, 0, 0)), None)] + M.bones:
        b = ad.edit_bones.new(n)
        b.head = head
        b.tail = head + Vector((0, 0, 0.25))
        b.roll = math.pi  # bone X = Blender -X -> identity rest orientation in Roblox after the axis change
        if par:
            b.parent = ad.edit_bones[par]
    bpy.ops.object.mode_set(mode="OBJECT")
    names = {b.name for b in ad.bones}
    assert len(names) <= LIMITS["bones"], f"{M.name}: {len(names)} bones"
    for o, bn in M.parts:
        assert bn in names, f"{M.name}: part {o.name} uses missing bone {bn}"
        o.parent = arm
        vg = o.vertex_groups.new(name=bn)
        vg.add([v.index for v in o.data.vertices], 1.0, "REPLACE")
        mod = o.modifiers.new("Armature", "ARMATURE")
        mod.object = arm
    for pb in arm.pose.bones:
        pb.rotation_mode = "QUATERNION"
    M.arm = arm
    return arm


def make_static(M):
    e = bpy.data.objects.new(M.name, None)
    e.empty_display_type = "PLAIN_AXES"
    bpy.context.scene.collection.objects.link(e)
    for o, _ in M.parts:
        o.parent = e
    M.root = e
    return e


# ======================================================================= animation
def _R0():
    return Matrix(((-1, 0, 0), (0, 0, 1), (0, 1, 0))).transposed()  # columns = bone rest axes (X=-X, Y=+Z, Z=+Y)


R0 = _R0()
R0i = R0.inverted()
D = math.radians


def sm(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def seg01(t, a, b):
    return min(1.0, max(0.0, (t - a) / (b - a)))


def bump(t, a, b):
    """0 -> 1 -> 0 over [a, b] (sin arch)"""
    u = seg01(t, a, b)
    return math.sin(math.pi * u)


def key_clip(M, clip, frames, fn, loop=False, markers=None):
    """fn(t, f) -> {bone: ((dx,dy,dz) world-axes offset, (rx,ry,rz) world-axes euler)}; keys every frame 0..frames"""
    arm = M.arm
    name = f"{'Fuser' if M.name == 'FuserRig' else M.name[3:] if M.name.startswith('Pet') else M.name}_{clip}"
    act = bpy.data.actions.new(name)
    act.use_fake_user = True
    arm.animation_data_create()
    arm.animation_data.action = act
    prev = {}
    for f in range(frames + 1):
        t = f / frames
        P = fn(t, f) if not (loop and f == frames) else fn(0.0, 0)
        for pb in arm.pose.bones:
            loc, rot = P.get(pb.name, ((0, 0, 0), (0, 0, 0)))
            pb.location = R0i @ Vector(loc)
            q = (R0i @ Euler(rot).to_matrix() @ R0).to_quaternion()
            if pb.name in prev and prev[pb.name].dot(q) < 0:
                q.negate()
            prev[pb.name] = q.copy()
            pb.rotation_quaternion = q
            pb.keyframe_insert("location", frame=f)
            pb.keyframe_insert("rotation_quaternion", frame=f)
    act.frame_range = (0, frames)
    act.use_frame_range = True
    act["loop"] = int(loop)
    for mk, fr in (markers or {}).items():
        pm = act.pose_markers.new(mk)
        pm.frame = fr
    M.clips[name] = (frames, loop, markers or {})
    arm.animation_data.action = None
    for pb in arm.pose.bones:
        pb.location = (0, 0, 0)
        pb.rotation_quaternion = (1, 0, 0, 0)
    return act


def has(M, b):
    return any(n == b for n, _, _ in M.bones)


def pet_clips(M, opt):
    """Idle / Move / Cast / Reveal (+ Carry for FETCH pets) from the pet's archetype + bones"""
    A = M.arch
    hop = opt.get("hop", 0.32)
    S = lambda x: math.sin(2 * math.pi * x)  # noqa: E731
    C = lambda x: math.cos(2 * math.pi * x)  # noqa: E731
    sideL = {"Ear_L": -1, "Ear_R": 1, "Wing_L": -1, "Wing_R": 1, "Arm_L": -1, "Arm_R": 1, "Antenna_L": -1, "Antenna_R": 1,
             "Fin_L": -1, "Fin_R": 1, "Hand_L": -1, "Hand_R": 1, "Star_L": -1, "Star_R": 1}

    def ears(P, out, back=0.0):
        """out > 0 tilts both ears outward (deg), back > 0 folds them back"""
        for b in ("Ear_L", "Ear_R"):
            if has(M, b):
                P[b] = ((0, 0, 0), (D(-back), D(out) * sideL[b], 0))

    def wings(P, up):
        for b in ("Wing_L", "Wing_R", "Fin_L", "Fin_R"):
            if has(M, b):
                P[b] = ((0, 0, 0), (0, -D(up) * sideL[b], 0))

    def arms(P, out=0.0, fwd=0.0):
        for b in ("Arm_L", "Arm_R"):
            if has(M, b):
                P[b] = ((0, 0, 0), (D(-fwd), -D(out) * sideL[b], 0))

    def tents(P, t, amp, base=0.0):
        for i in range(1, 5):
            b = f"Tent_{i}"
            if has(M, b):
                ph = i * 1.3
                P[b] = ((0, 0, 0), (D(base + amp * math.sin(2 * math.pi * t + ph)), D(amp * 0.6 * math.cos(2 * math.pi * t + ph)), 0))

    def tail(P, yaw, pitch=0.0):
        if has(M, "Tail_1"):
            P["Tail_1"] = ((0, 0, 0), (D(pitch), 0, D(yaw)))
        if has(M, "Tail_2"):
            P["Tail_2"] = ((0, 0, 0), (D(pitch * 0.6), 0, D(yaw * 0.8)))

    def legs4(P, front, backl, alt=False):
        if alt:  # trot: diagonal pairs
            for b, s in (("Leg_FL", 1), ("Leg_BR", 1), ("Leg_FR", -1), ("Leg_BL", -1)):
                if has(M, b):
                    P[b] = ((0, 0, 0), (D(front * s), 0, 0))
            return
        for b in ("Leg_FL", "Leg_FR"):
            if has(M, b):
                P[b] = ((0, 0, 0), (D(-front), 0, 0))
        for b in ("Leg_BL", "Leg_BR"):
            if has(M, b):
                P[b] = ((0, 0, 0), (D(backl), 0, 0))
        for b, s in (("Leg_L", 1), ("Leg_R", -1)):
            if has(M, b) and A == "fly":
                P[b] = ((0, 0, 0), (D(backl * 0.5), 0, 0))

    def extras(P, t, speed=1.0):
        """always-on motion for orbiting / spinning bits"""
        if has(M, "Ring"):
            P["Ring"] = ((0, 0, 0), (0, 0, 2 * math.pi * t * speed))
        if has(M, "Halo"):
            P["Halo"] = ((0, 0, 0), (0, D(8) * S(t), 0))
        for b in ("Star_L", "Star_R"):
            if has(M, b):
                s = sideL[b]
                P[b] = ((0, 0.25 * s * S(t), 0.12 * C(t)), (0, D(20) * S(t), D(25) * S(t) * s))
        for b in ("Hand_L", "Hand_R"):
            if has(M, b):
                s = sideL[b]
                P.setdefault(b, ((0, 0, 0.1 * S(t + (0.25 if s > 0 else 0))), (0, 0, 0)))
        if has(M, "Drill"):
            P["Drill"] = ((0, 0, 0), (0, 0, 0))
        if has(M, "Crown"):
            P["Crown"] = ((0, 0, 0.04 * S(t)), (0, 0, D(10) * S(t)))

    # ---------------------------------------------------------------- Idle (loop, 2 s): breathe, look, ears, tail
    def idle(t, f):
        P = {}
        br = 0.5 - 0.5 * C(t)
        if A in ("walk4", "biped"):
            P["Body"] = ((0, 0, 0.035 * br), (D(1.5) * S(t), 0, 0))
            P["Head"] = ((0, 0, 0), (D(-3) * S(t + 0.15), D(2.5) * S(t), D(6) * S(t + 0.3)))
            ears(P, 6 * S(2 * t), 4 * br)
            tail(P, 16 * S(2 * t), 4 * S(t))
            arms(P, 4 * br, 3 * S(t))
        elif A == "fly":
            P["Body"] = ((0, 0, 0.05 * br), (D(2) * S(t), 0, 0))
            P["Head"] = ((0, 0, 0), (D(-3) * S(t + 0.2), 0, D(5) * S(t)))
            wings(P, 12 * S(2 * t))
            for b in ("Antenna", "Antenna_L", "Antenna_R"):
                if has(M, b):
                    P[b] = ((0, 0, 0), (D(6) * S(t + 0.4), D(5) * S(t) * sideL.get(b, 1), 0))
        else:  # floaters
            P["Body"] = ((0, 0, 0.09 * br), (D(2.5) * S(t), D(2) * S(t + 0.25), 0))
            tents(P, t, 9)
            ears(P, 5 * S(t))
            wings(P, 14 * S(t))
            tail(P, 0, 10 * S(t + 0.2))
        extras(P, t, 1)
        return P

    # ---------------------------------------------------------------- Move (loop, 0.6 s): hop / waddle / flap / swim
    def move(t, f):
        P = {}
        if A == "walk4":
            h = math.sin(math.pi * t)
            P["Root"] = ((0, 0, hop * h), (0, 0, 0))
            P["Body"] = ((0, 0, 0), (D(-5) * S(t), 0, 0))
            P["Head"] = ((0, 0, 0), (D(4) * S(t), 0, 0))
            legs4(P, 24 * h, 24 * h)
            ears(P, 4, 16 * h)
            tail(P, 10 * S(t), -14 * h)
        elif A == "biped":
            P["Root"] = ((0, 0, hop * 0.45 * abs(S(t))), (0, 0, D(4) * S(t)))
            P["Body"] = ((0, 0, 0), (D(3), D(7) * S(t), 0))
            P["Head"] = ((0, 0, 0), (0, D(-4) * S(t), 0))
            for b, s in (("Leg_L", 1), ("Leg_R", -1)):
                if has(M, b):
                    P[b] = ((0, 0, 0), (D(24) * S(t) * s, 0, 0))
            for b, s in (("Arm_L", -1), ("Arm_R", 1)):
                if has(M, b):
                    P[b] = ((0, 0, 0), (D(22) * S(t) * s, -D(10 + 6 * abs(S(t))) * sideL[b], 0))
            ears(P, 5 * S(t), 6)
            tail(P, 18 * S(t), -6)
        elif A == "fly":
            P["Root"] = ((0, 0, 0.12 * S(t)), (0, 0, 0))
            P["Body"] = ((0, 0, 0), (D(10), 0, 0))
            P["Head"] = ((0, 0, 0), (D(-6), 0, 0))
            wings(P, 8 + 34 * S(3 * t))
            legs4(P, 0, 18)
            for b in ("Antenna", "Antenna_L", "Antenna_R"):
                if has(M, b):
                    P[b] = ((0, 0, 0), (D(-14 + 6 * S(t)), 0, 0))
        else:
            P["Body"] = ((0, 0, 0.14 * (0.5 - 0.5 * C(t))), (D(7) + D(4) * S(t), 0, 0))
            tents(P, t, 10, base=-18)
            wings(P, 26 * S(t))
            tail(P, 0, 20 * S(t - 0.15))
            ears(P, 8 * S(t), 8)
            for b in ("Hand_L", "Hand_R"):
                if has(M, b):
                    s = sideL[b]
                    P[b] = ((0, 0.12 * S(t), 0.14 * C(t) * s), (D(15) * S(t), 0, 0))
        extras(P, t, 1)
        return P

    # ---------------------------------------------------------------- Cast (0.7 s): crouch, jump + spin, land
    def cast(t, f):
        P = {}
        u = seg01(t, 0.18, 0.82)
        crouch = bump(t, 0.0, 0.36) * (1 - seg01(t, 0.18, 0.2))
        air = 4 * u * (1 - u)
        land = bump(t, 0.82, 1.0)
        P["Root"] = ((0, 0, 1.0 * air), (0, 0, 2 * math.pi * sm(u)))
        P["Body"] = ((0, 0, -0.1 * crouch - 0.07 * land), (D(-8) * air, 0, 0))
        P["Head"] = ((0, 0, 0), (D(-12) * air, 0, 0))
        ears(P, 18 * air, -10 * air)
        legs4(P, 26 * air, 26 * air)
        for b, s in (("Leg_L", 1), ("Leg_R", -1)):
            if has(M, b) and A == "biped":
                P[b] = ((0, 0, 0), (D(-20) * air * s, 0, 0))
        arms(P, 75 * air, 20 * air)
        wings(P, 10 + 40 * math.sin(10 * math.pi * t) * air)
        tents(P, t, 6, base=-25 * air)
        tail(P, 0, -25 * air)
        extras(P, t, 2)
        return P

    # ---------------------------------------------------------------- Reveal (1.2 s): crouched -> pop + twirl -> ta-da pose
    def reveal(t, f):
        P = {}
        crouch = 1 - sm(seg01(t, 0.18, 0.3))
        u = seg01(t, 0.25, 0.58)
        air = 4 * u * (1 - u)
        dip = bump(t, 0.58, 0.72)
        tada = sm(seg01(t, 0.6, 0.8))
        wig = math.sin(t * 2 * math.pi * 4) * (1 - seg01(t, 0, 0.25)) * crouch
        P["Root"] = ((0, 0, 0.75 * air), (0, 0, 2 * math.pi * sm(u) + D(8) * wig))
        P["Body"] = ((0, 0, -0.16 * crouch - 0.08 * dip), (D(10) * crouch - D(6) * tada, 0, 0))
        P["Head"] = ((0, 0, 0), (D(14) * crouch - D(12) * tada, D(8) * tada, 0))
        ears(P, 22 * tada, 24 * crouch)
        tail(P, 22 * tada * math.sin(t * 2 * math.pi * 3), -30 * tada)
        if A == "walk4":
            legs4(P, 18 * air, 18 * air)
            if has(M, "Leg_FR"):
                P["Leg_FR"] = ((0, 0, 0.12 * tada), (D(-55) * tada - D(18) * air, 0, 0))
        if A == "biped":
            arms(P, 20 + 100 * tada, 20 * tada)
        wings(P, 40 * tada + 30 * air * math.sin(t * 2 * math.pi * 6))
        tents(P, t, 6, base=-30 * tada)
        for b in ("Hand_L", "Hand_R"):
            if has(M, b):
                s = sideL[b]
                P[b] = ((0.25 * s * tada, 0, 0.55 * tada), (0, 0, 0))
        extras(P, t, 1.5)
        return P

    # ---------------------------------------------------------------- Carry (loop, 1 s): FETCH pets hold a meteor at the Carry bone
    def carry(t, f):
        P = {}
        if A == "walk4":
            P["Root"] = ((0, 0, 0.07 * abs(S(t))), (0, 0, 0))
            P["Body"] = ((0, 0, 0), (D(-2), 0, 0))
            legs4(P, 16 * S(t), 0, alt=True)
            ears(P, 6, 10)
        elif A == "biped":
            P["Root"] = ((0, 0, 0.05 * abs(S(t))), (0, 0, 0))
            P["Body"] = ((0, 0, 0), (D(-4), D(4) * S(t), 0))
            for b, s in (("Leg_L", 1), ("Leg_R", -1)):
                if has(M, b):
                    P[b] = ((0, 0, 0), (D(16) * S(t) * s, 0, 0))
        else:
            P["Body"] = ((0, 0, 0.06 * S(t)), (0, 0, 0))
        opt.get("carry", lambda P, t: None)(P, t)
        extras(P, t, 1)
        return P

    key_clip(M, "Idle", 60, idle, loop=True)
    key_clip(M, "Move", 18, move, loop=True)
    key_clip(M, "Cast", 21, cast)
    if M.name[3:] in FETCH:
        key_clip(M, "Carry", 30, carry, loop=True)
    key_clip(M, "Reveal", 36, reveal)


# ======================================================================= pets (built at the origin, feet on z = 0)
def head_set(M, c, r, spread=0.4, up=-0.02, size=0.24, nose=True, bone="Head"):
    b, s = eyes(c, r, spread, up, size)
    M.add("Eyes", b, bone)
    M.add("Shine", s, bone)
    if nose:
        p, n = on(c, r, (0, -1, up - 0.25), 1.0)
        M.add("Nose", gem(p, n, 0.08, 0.06, 0.07, "EyeBlack", back=0.6), bone)


def legs4_geo(M, mat, xs, yf, yb, z, rf, rb, seed=0, front_bone=True):
    for nm, x, y, rr in (("LegFL", -xs, yf, rf), ("LegFR", xs, yf, rf), ("LegBL", -xs, yb, rb), ("LegBR", xs, yb, rb)):
        M.add(nm, blob(rr, (x, y, z), mat, seed=seed + int(x * 10) + int(y * 10)), "Leg_" + nm[3:])


def leg_bones(M, xs, yf, yb, z):
    for b, x, y in (("Leg_FL", -xs, yf), ("Leg_FR", xs, yf), ("Leg_BL", -xs, yb), ("Leg_BR", xs, yb)):
        M.bone(b, (x, y, z), "Body")


def pebblit():
    M = Model("PetPebblit")
    M.arch = "walk4"
    hc, hr = (0, -0.36, 1.5), (0.86, 0.72, 0.64)
    bc, br = (0, 0.22, 0.74), (0.62, 0.8, 0.52)
    M.bone("Body", (0, 0.25, 0.7))
    M.bone("Head", (0, -0.2, 1.1), "Body")
    M.bone("Ear_L", (-0.66, -0.34, 1.86), "Head")
    M.bone("Ear_R", (0.66, -0.34, 1.86), "Head")
    M.bone("Tail_1", (0, 0.95, 0.9), "Body")
    leg_bones(M, 0.34, -0.26, 0.68, 0.5)
    M.bone("Carry", (0, 0.62, 1.95), "Body")
    M.add("Body", fac(br, bc, "PebBody", seed=1), "Body")
    M.add("Head", fac(hr, hc, "PebBody", seed=2, keep=0.85), "Head")
    M.add("HeadSpots", [spot(*on(hc, hr, d), w, "PebSpot") for d, w in (((0.1, -0.45, 1), 0.17), ((-0.62, -0.55, 0.5), 0.13), ((0.66, 0.1, 0.62), 0.14))], "Head")
    M.add("BodySpots", [spot(*on(bc, br, d), w, "PebSpot") for d, w in (((0.78, 0.25, 0.5), 0.18), ((-0.75, 0.45, 0.55), 0.16), ((0.6, 0.85, 0.2), 0.14),
                                                                        ((-0.6, -0.15, 0.25), 0.13), ((0, 1, 0.1), 0.2))], "Body")
    head_set(M, hc, hr, 0.4, -0.04, 0.24)
    for s_, nm in ((-1, "EarL"), (1, "EarR")):
        M.add(nm, fac((0.18, 0.36, 0.5), (s_ * 0.9, -0.3, 1.36), "PebBody", sub=2, keep=0.6, seed=5 + s_, rot=(D(-6), D(-s_ * 24), 0)), "Ear_" + nm[3])
    M.add("Tail", blob((0.21, 0.21, 0.21), (0, 1.0, 0.9), "PebSpot", seed=9), "Tail_1")
    for nm, x, y, rr in (("LegFL", -0.34, -0.3, (0.26, 0.3, 0.3)), ("LegFR", 0.34, -0.3, (0.26, 0.3, 0.3)),
                         ("LegBL", -0.34, 0.68, (0.23, 0.25, 0.29)), ("LegBR", 0.34, 0.68, (0.23, 0.25, 0.29))):
        M.add(nm, [blob(rr, (x, y, 0.28), "PebBody", seed=3 + int(x * 10 + y * 10))] +
              ([spot((x, y - rr[1] * 0.9, 0.3), (0, -1, 0.1), 0.11, "PebSpot")] if nm in ("LegFL", "LegFR") else []), "Leg_" + nm[3:])
    M.add("Basket", [P1.cone(0.34, 0.52, 0.44, (0, 0.62, 1.46), "PebSpot", verts=8),
                     torus(0.52, 0.1, (0, 0.62, 1.68), "PebSpot", major=10, minor=4)], "Body")
    M.add("Crystals", crystals([((0, 0.62, 1.56), (0.05, 0, 1), 0.72, 0.19), ((0.24, 0.52, 1.58), (0.5, -0.2, 1), 0.42, 0.13),
                                ((-0.24, 0.72, 1.58), (-0.5, 0.2, 1), 0.4, 0.12), ((0.08, 0.88, 1.58), (0.1, 0.6, 1), 0.34, 0.11),
                                ((-0.14, 0.4, 1.58), (-0.2, -0.6, 1), 0.3, 0.1)], "PebCrystal"), "Body")
    M.add("Bits", crystals([((s_ * 0.74, -0.62, 1.22), (s_ * 1, -0.4, 0.3), 0.22, 0.09) for s_ in (-1, 1)], "PebCrystal", 4), "Head")
    return M, {"hop": 0.32, "carry": lambda P, t: P.update({"Head": ((0, 0, 0), (D(-6), 0, 0))})}


def cinderpup():
    M = Model("PetCinderpup")
    M.arch = "walk4"
    hc, hr = (0, -0.36, 1.6), (0.8, 0.7, 0.72)
    bc, br = (0, 0.28, 0.76), (0.55, 0.72, 0.5)
    M.bone("Body", (0, 0.28, 0.72))
    M.bone("Head", (0, -0.2, 1.12), "Body")
    M.bone("Ear_L", (-0.52, -0.3, 2.0), "Head")
    M.bone("Ear_R", (0.52, -0.3, 2.0), "Head")
    M.bone("Tail_1", (0, 0.96, 0.9), "Body")
    leg_bones(M, 0.32, -0.25, 0.7, 0.5)
    M.bone("Carry", (0, 1.44, 1.72), "Tail_1")
    M.add("Body", fac(br, bc, "CinderBody", seed=11), "Body")
    M.add("Head", fac(hr, hc, "CinderBody", seed=12, keep=0.85), "Head")
    veins = [gem(*on(hc, hr, d), 0.06, 0.26, 0.035, "CinderGlow", up=u) for d, u in (((-0.66, -0.55, 0.0), (0.4, 0, 1)), ((0.66, -0.5, -0.1), (-0.5, 0, 1)),
                                                                                    ((0.25, -0.45, 0.85), (1, 0, 0.6)), ((-0.6, 0.4, 0.5), (0, 1, 0.8)),
                                                                                    ((0.15, 0.7, 0.6), (0.3, 0, 1)))]
    M.add("HeadVeins", veins, "Head")
    bv = [gem(*on(bc, br, (0, -1, 0.15)), 0.16, 0.22, 0.1, "CinderGlow")]
    bv += [gem(*on(bc, br, d), 0.06, 0.24, 0.035, "CinderGlow", up=u) for d, u in (((0.8, 0.1, 0.4), (0, 1, 0.5)), ((-0.8, 0.5, 0.3), (0, 1, -0.4)),
                                                                                   ((0.4, 0.9, 0.6), (1, 0, 1)), ((-0.5, -0.4, -0.2), (0, 0.4, 1)))]
    M.add("BodyVeins", bv, "Body")
    head_set(M, hc, hr, 0.4, -0.04, 0.25)
    for s_, nm in ((-1, "L"), (1, "R")):
        base = Vector((s_ * 0.55, -0.3, 1.98))
        M.add("Ear" + nm, fac((0.32, 0.26, 0.32), base + Vector((s_ * 0.04, 0, 0.1)), "CinderBody", sub=1, keep=0.9, seed=14 + s_), "Ear_" + nm)
        M.add("Flame" + nm, crystals([(base + Vector((s_ * 0.02, -0.04, 0.22)), (s_ * 0.2, -0.1, 1), 0.72, 0.2),
                                      (base + Vector((s_ * 0.24, 0.0, 0.16)), (s_ * 0.9, 0, 1), 0.52, 0.17),
                                      (base + Vector((-s_ * 0.16, 0.04, 0.2)), (-s_ * 0.3, 0.1, 1), 0.5, 0.16),
                                      (base + Vector((s_ * 0.1, 0.14, 0.2)), (s_ * 0.3, 0.6, 1), 0.42, 0.15)], "CinderGlow"), "Ear_" + nm)
    M.add("Tail", [seg((0, 0.9, 0.86), (0, 1.32, 1.3), 0.17, 0.14, "CinderBody"),
                   P1.cone(0.22, 0.46, 0.36, (0, 1.44, 1.5), "CinderBody", rot=(D(-20), 0, 0), verts=8)], "Tail_1")
    M.add("Embers", crystals([((0, 1.46, 1.58), (0, -0.2, 1), 0.32, 0.14), ((0.17, 1.38, 1.58), (0.4, 0, 1), 0.26, 0.11),
                              ((-0.16, 1.52, 1.58), (-0.4, 0.2, 1), 0.26, 0.11), ((0.02, 1.62, 1.58), (0, 0.5, 1), 0.22, 0.1)], "CinderGlow"), "Tail_1")
    for nm, x, y in (("LegFL", -0.32, -0.25), ("LegFR", 0.32, -0.25), ("LegBL", -0.32, 0.7), ("LegBR", 0.32, 0.7)):
        M.add(nm, blob((0.22, 0.25, 0.3), (x, y, 0.28), "CinderBody", seed=13 + int(x * 10 + y * 10)), "Leg_" + nm[3:])
    return M, {"hop": 0.34, "carry": lambda P, t: P.update({"Tail_1": ((0, 0, 0), (D(42), 0, 0))})}


def glintmoth():
    M = Model("PetGlintmoth")
    M.arch = "fly"
    hc, hr = (0, -0.16, 1.74), (0.74, 0.64, 0.66)
    bc, br = (0, 0.1, 0.84), (0.54, 0.5, 0.56)
    M.bone("Body", (0, 0.1, 0.7))
    M.bone("Head", (0, -0.1, 1.22), "Body")
    M.bone("Wing_L", (-0.42, 0.32, 1.2), "Body")
    M.bone("Wing_R", (0.42, 0.32, 1.2), "Body")
    M.bone("Antenna_L", (-0.24, -0.2, 2.32), "Head")
    M.bone("Antenna_R", (0.24, -0.2, 2.32), "Head")
    M.bone("Leg_L", (-0.24, 0.0, 0.42), "Body")
    M.bone("Leg_R", (0.24, 0.0, 0.42), "Body")
    M.add("Body", fac(br, bc, "ChargedRock", seed=21), "Body")
    M.add("ChestGem", gem(*on(bc, br, (0, -1, 0.1)), 0.17, 0.26, 0.12, "Bolt"), "Body")
    M.add("Head", fac(hr, hc, "ChargedRock", seed=22, keep=0.85), "Head")
    head_set(M, hc, hr, 0.42, -0.02, 0.25, nose=False)
    for s_, nm in ((-1, "L"), (1, "R")):
        # one thick faceted wing per side: big upper kite + smaller lower kite, glowing inlays through both faces
        up = gem((s_ * 1.0, 0.36, 1.55), (0, -1, 0), 0.62, 0.7, 0.16, "ChargedRock", up=(s_ * 0.45, 0, 1), back=1.0)
        lo = gem((s_ * 0.82, 0.36, 0.86), (0, -1, 0), 0.45, 0.48, 0.15, "ChargedRock", up=(-s_ * 0.6, 0, 1), back=1.0)
        M.add("Wing" + nm, [up, lo], "Wing_" + nm)
        M.add("WingGlow" + nm, [gem((s_ * 1.08, 0.36, 1.6), (0, -1, 0), 0.36, 0.52, 0.18, "Bolt", up=(s_ * 0.45, 0, 1), back=1.0),
                                gem((s_ * 0.87, 0.36, 0.84), (0, -1, 0), 0.26, 0.34, 0.17, "Bolt", up=(-s_ * 0.6, 0, 1), back=1.0)], "Wing_" + nm)
        a0 = Vector((s_ * 0.24, -0.2, 2.28))
        a1 = Vector((s_ * 0.34, -0.26, 2.6))
        a2 = Vector((s_ * 0.5, -0.3, 2.8))
        M.add("Antenna" + nm, [seg(a0, a1, 0.1, 0.09, "ChargedRock"), seg(a1, a2, 0.09, 0.085, "ChargedRock")], "Antenna_" + nm)
        M.add("Tip" + nm, crystals([(a2 - Vector((s_ * 0.03, 0, 0.06)), (s_ * 0.45, -0.15, 1), 0.52, 0.19)], "Bolt"), "Antenna_" + nm)
        M.add("Leg" + nm, blob((0.2, 0.22, 0.27), (s_ * 0.24, 0.0, 0.25), "ChargedRock", seed=27 + s_), "Leg_" + nm)
    return M, {}


def rubblord():
    M = Model("PetRubblord")
    M.arch = "biped"
    bc, br = (0, 0, 1.42), (0.84, 0.74, 0.92)
    M.bone("Body", (0, 0, 0.75))
    M.bone("Arm_L", (-0.95, 0.05, 1.8), "Body")
    M.bone("Arm_R", (0.95, 0.05, 1.8), "Body")
    M.bone("Leg_L", (-0.42, 0.0, 0.66), "Body")
    M.bone("Leg_R", (0.42, 0.0, 0.66), "Body")
    M.add("Body", fac(br, bc, "RubBody", seed=31, keep=0.85), "Body")
    head_set(M, bc, br, 0.32, 0.25, 0.21, nose=False, bone="Body")
    sp = [((0, -0.05, 2.12), (0, -0.1, 1), 0.9, 0.24), ((-0.42, 0.0, 2.02), (-0.45, 0, 1), 0.55, 0.17), ((0.42, 0.0, 2.02), (0.45, 0, 1), 0.55, 0.17),
          ((0, 0.62, 1.9), (0, 0.8, 0.7), 0.6, 0.2), ((0, 0.74, 1.4), (0, 1, 0.4), 0.5, 0.18), ((-0.38, 0.62, 1.66), (-0.3, 0.9, 0.5), 0.42, 0.15),
          ((0.38, 0.62, 1.66), (0.3, 0.9, 0.5), 0.42, 0.15)]
    M.add("Spikes", [crystals(sp, "RubSpike"), gem(*on(bc, br, (0, -1, -0.42)), 0.22, 0.3, 0.14, "RubSpike")], "Body")
    for s_, nm in ((-1, "L"), (1, "R")):
        sh = fac((0.56, 0.56, 0.56), (s_ * 0.92, 0.04, 1.74), "RubBody", sub=2, keep=0.55, seed=33 + s_)
        ua = fac((0.38, 0.38, 0.44), (s_ * 1.06, -0.02, 1.2), "RubBody", sub=1, keep=0.9, seed=35 + s_)
        fi = fac((0.46, 0.45, 0.48), (s_ * 1.1, -0.1, 0.6), "RubBody", sub=2, keep=0.5, seed=37 + s_)
        M.add("Arm" + nm, [sh, ua, fi], "Arm_" + nm)
        M.add("ArmSpike" + nm, crystals([((s_ * 1.06, 0.05, 2.16), (s_ * 0.6, 0, 1), 0.58, 0.19), ((s_ * 1.3, 0.05, 1.98), (s_ * 0.8, 0, 0.7), 0.4, 0.15),
                                         ((s_ * 1.5, -0.1, 0.76), (s_ * 1, -0.3, 0.2), 0.3, 0.13), ((s_ * 1.28, -0.48, 0.9), (s_ * 0.4, -1, 0.3), 0.26, 0.12)], "RubSpike"), "Arm_" + nm)
        M.add("Leg" + nm, fac((0.34, 0.36, 0.4), (s_ * 0.38, 0.0, 0.38), "RubBody", sub=1, keep=0.9, seed=39 + s_), "Leg_" + nm)
    return M, {"hop": 0.3}


def emberkit():
    M = Model("PetEmberkit")
    M.arch = "walk4"
    hc, hr = (0, -0.32, 1.48), (0.84, 0.72, 0.72)
    bc, br = (0, 0.24, 0.7), (0.52, 0.62, 0.45)
    M.bone("Body", (0, 0.24, 0.66))
    M.bone("Head", (0, -0.2, 1.02), "Body")
    M.bone("Ear_L", (-0.5, -0.3, 2.0), "Head")
    M.bone("Ear_R", (0.5, -0.3, 2.0), "Head")
    M.bone("Tail_1", (0, 0.8, 0.72), "Body")
    M.bone("Tail_2", (0, 1.18, 0.88), "Tail_1")
    leg_bones(M, 0.3, -0.2, 0.62, 0.46)
    M.add("Body", fac(br, bc, "KitBody", seed=41), "Body")
    p, n = on(bc, br, (0, -1, 0.1))
    M.add("Furnace", P1.cone(0.24, 0.24, 0.16, p, "Ember", rot=n.to_track_quat("Z", "Y").to_euler(), verts=6), "Body")
    M.add("Head", [fac(hr, hc, "KitBody", seed=42, keep=0.6)] +
          [pyramid((s * 0.78, -0.42, 1.3), (s * 1.06, -0.45, 1.22), 0.14, "KitBody", 4) for s in (-1, 1)], "Head")
    M.add("Cheeks", [gem(*on(hc, hr, (s * 0.78, -0.6, -0.2)), 0.13, 0.14, 0.08, "Ember") for s in (-1, 1)], "Head")
    head_set(M, hc, hr, 0.4, 0.0, 0.27)
    for s, nm in ((-1, "L"), (1, "R")):
        M.add("Ear" + nm, pyramid((s * 0.5, -0.28, 1.86), (s * 0.72, -0.34, 2.6), 0.32, "KitBody", 4, D(45)), "Ear_" + nm)
        M.add("EarGlow" + nm, pyramid((s * 0.5, -0.44, 1.9), (s * 0.69, -0.49, 2.46), 0.19, "Ember", 4, D(45)), "Ear_" + nm)
    M.add("Tail1", seg((0, 0.78, 0.7), (0, 1.2, 0.86), 0.13, 0.12, "KitBody"), "Tail_1")
    M.add("Tail2", seg((0, 1.18, 0.84), (0, 1.34, 1.26), 0.12, 0.11, "KitBody"), "Tail_2")
    M.add("Flame", [fac((0.2, 0.2, 0.3), (0, 1.38, 1.46), "Ember", sub=1, keep=0.7, seed=48)] +
          crystals_list([((0, 1.38, 1.58), (0, 0.1, 1), 0.42, 0.13), ((0.12, 1.36, 1.48), (0.6, 0, 1), 0.3, 0.1)], "Ember"), "Tail_2")
    legs4_geo(M, "KitBody", 0.3, -0.2, 0.62, 0.26, (0.21, 0.23, 0.27), (0.2, 0.22, 0.26), seed=43)
    return M, {"hop": 0.34}


def crystals_list(spec, mat, sides=5):
    return [crystals(spec, mat, sides)]


def magmaw():
    M = Model("PetMagmaw")
    M.arch = "walk4"
    c, r = (0, 0.05, 0.98), (1.0, 0.9, 0.82)
    M.bone("Body", (0, 0.05, 0.5))
    M.bone("Jaw", (0, -0.35, 0.66), "Body")
    leg_bones(M, 0.6, -0.42, 0.45, 0.36)
    M.add("Body", [fac(r, c, "DarkRock", seed=51, keep=0.6)] +
          [blob((0.3, 0.3, 0.28), (s * 0.44, -0.42, 1.48), "DarkRock", seed=52 + s) for s in (-1, 1)], "Body")
    glow = [fac((0.8, 0.3, 0.22), (0, -0.62, 0.84), "MawGlow", sub=2, keep=0.6, seed=54)]
    glow += [fac((0.1, 0.1, 0.2), (s * 0.66, -0.66, 0.6), "MawGlow", sub=1, keep=0.6, seed=55 + s) for s in (-1, 1)]
    glow += [crystals([((0, -0.1, 1.68), (0, -0.1, 1), 0.62, 0.2), ((-0.35, 0.05, 1.62), (-0.3, 0, 1), 0.36, 0.12), ((0.35, 0.05, 1.62), (0.3, 0, 1), 0.36, 0.12)], "MawGlow")]
    glow += [gem(*on(c, r, d), 0.12, 0.17, 0.09, "MawGlow") for d in ((0.85, 0.4, 0.35), (-0.85, 0.5, 0.3), (0.3, 0.9, 0.5), (-0.25, 0.95, 0.15))]
    M.add("Glow", glow, "Body")
    M.add("Jaw", fac((0.7, 0.32, 0.2), (0, -0.56, 0.58), "MawJaw", sub=1, keep=0.9, seed=57), "Jaw")
    hs, hsh = eyes((0, -0.42, 1.48), (0.62, 0.42, 0.3), 0.72, 0.15, 0.26)
    M.add("Eyes", hs, "Body")
    M.add("Shine", hsh, "Body")
    for nm, x, y, rr in (("FL", -0.6, -0.42, (0.27, 0.3, 0.2)), ("FR", 0.6, -0.42, (0.27, 0.3, 0.2)), ("BL", -0.68, 0.45, (0.31, 0.32, 0.22)), ("BR", 0.68, 0.45, (0.31, 0.32, 0.22))):
        M.add("Leg" + nm, blob(rr, (x, y, 0.19), "DarkRock", seed=58 + int(x * 5)), "Leg_" + nm)
        M.add("Toe" + nm, [gem((x + dx, y - rr[1] * 0.85, 0.1), (0, -1, 0.2), 0.07, 0.08, 0.1, "MawGlow") for dx in (-0.1, 0.1)], "Leg_" + nm)
    return M, {"hop": 0.28}


def flarefly():
    M = Model("PetFlarefly")
    M.arch = "fly"
    hc, hr = (0, -0.18, 1.74), (0.76, 0.64, 0.62)
    M.bone("Body", (0, 0.05, 0.7))
    M.bone("Head", (0, -0.12, 1.25), "Body")
    M.bone("Wing_L", (-0.36, 0.25, 1.38), "Body")
    M.bone("Wing_R", (0.36, 0.25, 1.38), "Body")
    M.bone("Antenna", (0, -0.12, 2.4), "Head")
    M.bone("Leg_L", (-0.24, 0.05, 0.4), "Body")
    M.bone("Leg_R", (0.24, 0.05, 0.4), "Body")
    M.add("Body", [fac((0.48, 0.44, 0.42), (0, 0.15, 1.1), "Flare", sub=1, keep=0.8, seed=61)] +
          [fac((0.13, 0.14, 0.24), (s * 0.3, -0.42, 1.02), "Flare", sub=1, keep=0.6, seed=62 + s, rot=(0, D(s * 15), 0)) for s in (-1, 1)], "Body")
    M.add("Lantern", fac((0.56, 0.5, 0.52), (0, -0.12, 0.8), "Bolt", seed=63, keep=0.6), "Body")
    M.add("Head", [fac(hr, hc, "Flare", seed=64, keep=0.85), blob((0.14, 0.14, 0.12), (0, -0.12, 2.34), "Flare", seed=65)], "Head")
    head_set(M, hc, hr, 0.44, 0.02, 0.25, nose=False)
    for s, nm in ((-1, "L"), (1, "R")):
        M.add("Wing" + nm, fac((0.27, 0.56, 0.68), (s * 0.58, 0.22, 0.98), "Flare", sub=2, keep=0.5, seed=66 + s, rot=(D(-12), D(s * 16), 0)), "Wing_" + nm)
        M.add("WingGlow" + nm, gem((s * 0.8, 0.12, 0.94), (s, -0.2, 0), 0.36, 0.5, 0.1, "Bolt", up=(0, -0.2, 1), back=0.2), "Wing_" + nm)
        M.add("Leg" + nm, blob((0.16, 0.17, 0.22), (s * 0.24, 0.05, 0.2), "Flare", seed=68 + s), "Leg_" + nm)
    pts = [Vector(p) for p in ((0, -0.12, 2.32), (0.04, -0.14, 2.66), (0.24, -0.22, 2.86), (0.46, -0.3, 2.82))]
    M.add("Antenna", [seg(pts[i], pts[i + 1], 0.085, 0.08, "Flare") for i in range(3)], "Antenna")
    M.add("Bulb", fac((0.21, 0.21, 0.21), (0.54, -0.33, 2.66), "Bolt", sub=1, keep=0.8, seed=69), "Antenna")
    return M, {}


def solarix():
    M = Model("PetSolarix")
    M.arch = "walk4"
    hc, hr = (0, -0.3, 1.66), (0.7, 0.62, 0.64)
    bc, br = (0, 0.3, 0.8), (0.52, 0.7, 0.5)
    M.bone("Body", (0, 0.3, 0.74))
    M.bone("Head", (0, -0.18, 1.2), "Body")
    M.bone("Halo", (0, 0.32, 2.1), "Head")
    M.bone("Tail_1", (0, 0.95, 0.9), "Body")
    leg_bones(M, 0.3, -0.24, 0.72, 0.5)
    M.add("Body", fac(br, bc, "SunGold", seed=71), "Body")
    M.add("ChestGem", [gem(*on(bc, br, (0, -1, 0.2)), 0.16, 0.24, 0.12, "GoldGlow"),
                       gem(*on(bc, br, (-0.35, -1, 0.0)), 0.1, 0.15, 0.09, "GoldGlow"), gem(*on(bc, br, (0.35, -1, 0.0)), 0.1, 0.15, 0.09, "GoldGlow")], "Body")
    M.add("Head", fac(hr, hc, "SunGold", seed=72, keep=0.6), "Head")
    mane, glow = [], []
    for i in range(10):
        a = math.radians(-60 + i * 30) if i < 9 else math.radians(-90)
        if i == 9:
            continue
        d = Vector((math.sin(a), 0, math.cos(a)))
        base = Vector(hc) + Vector((d.x * 0.5, 0.18, d.z * 0.5))
        L = 0.52 if i % 2 == 0 else 0.42
        mane.append(pyramid(base, base + d * L + Vector((0, 0.12, 0)), 0.34, "SunGold", 4, D(45)))
        glow.append(gem(base + d * (L * 0.45) + Vector((0, -0.12, 0)), (d.x * 0.2, -1, d.z * 0.2), 0.08, 0.13, 0.06, "GoldGlow", up=d))
    for s in (-1, 1):
        mane.append(pyramid((s * 0.62, -0.1, 1.3), (s * 1.08, 0.0, 1.12), 0.24, "SunGold", 4, D(45)))
    M.add("Mane", mane, "Head")
    glow.append(gem(*on(hc, hr, (0, -0.7, 0.75)), 0.1, 0.17, 0.08, "GoldGlow"))
    M.add("ManeGlow", glow, "Head")
    M.add("Halo", [torus(0.74, 0.09, (0, 0.4, 2.1), "GoldGlow", rot=(D(90), 0, 0), major=20, minor=6)] +
          crystals_list([((0, 0.4, 2.82), (0, 0, 1), 0.4, 0.13), ((-0.74, 0.4, 2.1), (-1, 0, 0), 0.3, 0.11), ((0.74, 0.4, 2.1), (1, 0, 0), 0.3, 0.11),
                         ((-0.52, 0.4, 2.62), (-0.7, 0, 0.7), 0.24, 0.09), ((0.52, 0.4, 2.62), (0.7, 0, 0.7), 0.24, 0.09)], "GoldGlow", 4), "Halo")
    head_set(M, hc, hr, 0.4, -0.04, 0.24)
    M.add("Tail", [seg((0, 0.92, 0.86), (0, 1.12, 0.92), 0.12, 0.1, "SunGold"), gem((0, 1.16, 0.94), (0, 1, 0.2), 0.12, 0.16, 0.12, "GoldGlow", back=1.0)], "Tail_1")
    legs4_geo(M, "SunGold", 0.3, -0.24, 0.72, 0.24, (0.21, 0.23, 0.26), (0.2, 0.22, 0.25), seed=73)
    return M, {"hop": 0.32}


def frostling():
    M = Model("PetFrostling")
    M.arch = "walk4"
    hc, hr = (0, -0.3, 1.55), (0.74, 0.64, 0.64)
    bc, br = (0, 0.26, 0.76), (0.48, 0.66, 0.45)
    M.bone("Body", (0, 0.26, 0.7))
    M.bone("Head", (0, -0.2, 1.12), "Body")
    M.bone("Ear_L", (-0.42, -0.26, 1.98), "Head")
    M.bone("Ear_R", (0.42, -0.26, 1.98), "Head")
    M.bone("Tail_1", (0, 0.86, 0.86), "Body")
    M.bone("Tail_2", (0, 1.3, 1.34), "Tail_1")
    leg_bones(M, 0.27, -0.22, 0.66, 0.48)
    M.add("Body", fac(br, bc, "IceRock", seed=81), "Body")
    col = [pyramid((math.sin(a) * 0.36, -0.3 + math.cos(a) * 0.28 - 0.05, 1.08), (math.sin(a) * 0.62, -0.3 + math.cos(a) * 0.45 - 0.1, 0.9), 0.16, "FrostCrystal", 4)
           for a in [D(x) for x in (120, 150, 180, 210, 240)]]
    col.append(gem(*on(bc, br, (0, -1, 0.05)), 0.12, 0.2, 0.1, "FrostGlow"))
    M.add("Collar", col, "Body")
    M.add("Head", [fac(hr, hc, "IceRock", seed=82, keep=0.6)] +
          [pyramid((s * 0.62, -0.42, 1.36), (s * 0.95, -0.42, 1.22), 0.15, "IceRock", 4) for s in (-1, 1)] +
          [pyramid((s * 0.58, -0.3, 1.18), (s * 0.82, -0.3, 0.98), 0.13, "IceRock", 4) for s in (-1, 1)], "Head")
    M.add("Forehead", gem(*on(hc, hr, (0, -0.65, 0.8)), 0.1, 0.2, 0.08, "FrostGlow"), "Head")
    head_set(M, hc, hr, 0.42, 0.0, 0.24)
    for s, nm in ((-1, "L"), (1, "R")):
        M.add("Ear" + nm, pyramid((s * 0.42, -0.24, 1.86), (s * 0.66, -0.26, 2.62), 0.28, "IceRock", 4, D(45)), "Ear_" + nm)
        M.add("EarIce" + nm, crystals([((s * 0.56, -0.2, 2.1), (s * 0.6, 0.1, 1), 0.66, 0.14), ((s * 0.64, -0.32, 2.0), (s * 1.0, -0.1, 0.8), 0.5, 0.12),
                                       ((s * 0.5, -0.12, 2.25), (s * 0.3, 0.3, 1), 0.44, 0.11)], "FrostGlow"), "Ear_" + nm)
    M.add("Tail1", crystals([((0, 0.84, 0.84), (0, 1, 0.65), 0.62, 0.18), ((0, 1.18, 1.12), (0, 1, 0.9), 0.4, 0.13)], "FrostGlow"), "Tail_1")
    M.add("Tail2", crystals([((0, 1.3, 1.36), (0, 0.8, 1), 0.58, 0.17), ((0, 1.56, 1.72), (0, 0.6, 1), 0.5, 0.15)], "FrostGlow"), "Tail_2")
    legs4_geo(M, "IceRock", 0.27, -0.22, 0.66, 0.24, (0.19, 0.21, 0.26), (0.18, 0.2, 0.25), seed=83)
    return M, {"hop": 0.34}


def shardbun():
    M = Model("PetShardbun")
    M.arch = "walk4"
    hc, hr = (0, -0.22, 1.3), (0.7, 0.62, 0.6)
    bc, br = (0, 0.22, 0.64), (0.5, 0.6, 0.44)
    M.bone("Body", (0, 0.22, 0.6))
    M.bone("Head", (0, -0.15, 0.95), "Body")
    M.bone("Ear_L", (-0.28, -0.12, 1.8), "Head")
    M.bone("Ear_R", (0.28, -0.12, 1.8), "Head")
    M.bone("Tail_1", (0, 0.78, 0.6), "Body")
    leg_bones(M, 0.28, -0.2, 0.55, 0.4)
    M.add("Body", fac(br, bc, "Snow", seed=91), "Body")
    M.add("ChestGem", gem(*on(bc, br, (0, -1, 0.15)), 0.13, 0.2, 0.13, "Cyan"), "Body")
    M.add("Head", fac(hr, hc, "Snow", seed=92, keep=0.6), "Head")
    fins = []
    for s in (-1, 1):
        b0 = Vector((s * 0.62, -0.32, 1.12))
        fins.append(crystals([(b0, (s * 1, -0.1, 0.55), 0.5, 0.12), (b0, (s * 1, -0.1, 0.1), 0.48, 0.12), (b0, (s * 1, -0.1, -0.35), 0.38, 0.1)], "Cyan", 4))
    M.add("Fins", fins, "Head")
    head_set(M, hc, hr, 0.42, -0.02, 0.24, nose=False)
    for s, nm in ((-1, "L"), (1, "R")):
        M.add("Ear" + nm, seg((s * 0.26, -0.12, 1.7), (s * 0.36, -0.12, 2.25), 0.22, 0.25, "Snow", 6), "Ear_" + nm)
        M.add("EarGem" + nm, crystals([((s * 0.36, -0.12, 2.22), (s * 0.15, 0, 1), 0.8, 0.25)], "Cyan", 6), "Ear_" + nm)
    M.add("Tail", blob((0.24, 0.22, 0.24), (0, 0.84, 0.62), "Snow", seed=95), "Tail_1")
    M.add("TailGem", gem((0, 1.04, 0.64), (0, 1, 0.2), 0.12, 0.14, 0.1, "Cyan", back=0.6), "Tail_1")
    legs4_geo(M, "Snow", 0.28, -0.2, 0.55, 0.18, (0.19, 0.22, 0.2), (0.2, 0.26, 0.2), seed=93)
    return M, {"hop": 0.38}


def glacio():
    M = Model("PetGlacio")
    M.arch = "biped"
    c, r = (0, 0, 1.18), (0.82, 0.74, 1.0)
    M.bone("Body", (0, 0, 0.5))
    M.bone("Arm_L", (-0.74, 0.0, 1.5), "Body")
    M.bone("Arm_R", (0.74, 0.0, 1.5), "Body")
    M.bone("Leg_L", (-0.32, -0.1, 0.22), "Body")
    M.bone("Leg_R", (0.32, -0.1, 0.22), "Body")
    M.add("Body", fac(r, c, "Glacio", seed=101, keep=0.6), "Body")
    M.add("Mask", [fac((0.62, 0.3, 0.44), (0, -0.52, 1.6), "Snow", sub=1, keep=0.9, seed=102),
                   fac((0.62, 0.32, 0.6), (0, -0.46, 0.82), "Snow", sub=1, keep=0.9, seed=103),
                   blob((0.2, 0.18, 0.16), (0, 0.5, 0.34), "Snow", seed=104)], "Body")
    M.add("Beak", pyramid((0, -0.72, 1.48), (0, -1.04, 1.42), 0.16, "GlacioBeak", 4, D(45)), "Body")
    M.add("Crest", crystals([((0, -0.05, 2.08), (0, -0.05, 1), 0.68, 0.17), ((-0.24, -0.02, 2.0), (-0.5, 0, 1), 0.4, 0.12), ((0.24, -0.02, 2.0), (0.5, 0, 1), 0.4, 0.12),
                             ((-0.34, -0.74, 0.86), (-1, -0.3, 0.8), 0.36, 0.12), ((0.34, -0.74, 0.86), (1, -0.3, 0.8), 0.36, 0.12)], "FrostCrystal"), "Body")
    M.add("Core", gem((0, -0.8, 0.95), (0, -1, 0), 0.3, 0.4, 0.22, "FrostGlow"), "Body")
    b, s = eyes((0, -0.4, 1.62), (0.6, 0.42, 0.42), 0.6, 0.05, 0.2)
    M.add("Eyes", b, "Body")
    M.add("Shine", s, "Body")
    for sd, nm in ((-1, "L"), (1, "R")):
        M.add("Flipper" + nm, fac((0.15, 0.3, 0.5), (sd * 0.88, 0.0, 1.08), "Glacio", sub=1, keep=0.8, seed=105 + sd, rot=(0, D(sd * 22), 0)), "Arm_" + nm)
        M.add("Foot" + nm, fac((0.25, 0.32, 0.1), (sd * 0.32, -0.28, 0.1), "Glacio", sub=1, keep=0.8, seed=107 + sd), "Leg_" + nm)
    return M, {"hop": 0.3}


def aurorabe():
    M = Model("PetAurorabe")
    M.arch = "float"
    c, r = (0, 0, 2.05), (1.0, 0.88, 0.8)
    M.bone("Body", (0, 0, 1.6))
    M.bone("Crown", (0, 0.05, 2.78), "Body")
    tps = [(-0.44, -0.26), (0.44, -0.26), (-0.4, 0.32), (0.4, 0.32)]
    for i, (x, y) in enumerate(tps):
        M.bone(f"Tent_{i + 1}", (x, y, 1.74), "Body")
    M.add("Body", [fac(r, c, "AuroraBody", seed=111, keep=0.75, zcut=-0.45)] +
          [fac((0.32, 0.18, 0.32), (s_ * 0.78, 0.02, 2.66), "AuroraBody", sub=1, keep=0.9, seed=112 + s_) for s_ in (-1, 1)], "Body")
    acc = [gem((s_ * 0.78, -0.17, 2.66), (0, -1, 0), 0.17, 0.17, 0.06, "Pink") for s_ in (-1, 1)]
    acc += [gem(*on(c, r, (s_ * 0.82, -0.62, -0.05)), 0.1, 0.16, 0.07, "Pink") for s_ in (-1, 1)]
    M.add("Accents", acc, "Body")
    M.add("Crown", [blob((0.26, 0.21, 0.18), (x, 0.08, 2.86), "Cloud", seed=114 + i) for i, x in enumerate((-0.3, 0, 0.3))], "Crown")
    M.add("CrownGem", crystals([((0, 0.02, 2.96), (0, 0, 1), 0.5, 0.15), ((-0.42, 0.02, 2.95), (-0.5, 0, 1), 0.22, 0.07),
                                ((0.42, 0.02, 2.95), (0.5, 0, 1), 0.22, 0.07)], "Pink", 4), "Crown")
    head_set(M, c, r, 0.4, 0.12, 0.27, bone="Body")
    for i, (x, y) in enumerate(tps):
        out = Vector((x, y, 0)).normalized()
        p0 = Vector((x, y, 1.78))
        p1 = Vector((x, y, 0)) + out * 0.36 + Vector((0, 0, 1.0))
        p2 = Vector((x, y, 0)) + out * 0.12 + Vector((0, 0, 0.42))
        M.add(f"Tent{i + 1}", [seg(p0, p1, 0.25, 0.21, "AuroraBody", 6), seg(p1, p2, 0.21, 0.17, "AuroraBody", 6)], f"Tent_{i + 1}")
        f = Vector((0, -0.17 if y < 0 else 0.17, 0))
        M.add(f"TentGlow{i + 1}", [seg(p0 + f, p1 + f, 0.12, 0.11, "Pink", 5), seg(p1 + f, p2 + f * 0.8, 0.11, 0.1, "Pink", 5)] +
              crystals_list([(p2 + Vector((0, 0, 0.14)), (0, 0, -1), 0.56, 0.2)], "Pink", 6), f"Tent_{i + 1}")
    return M, {}


def nebulynx():
    M = Model("PetNebulynx")
    M.arch = "walk4"
    hc, hr = (0, -0.3, 1.55), (0.76, 0.66, 0.66)
    bc, br = (0, 0.26, 0.78), (0.5, 0.68, 0.48)
    M.bone("Body", (0, 0.26, 0.72))
    M.bone("Head", (0, -0.2, 1.12), "Body")
    M.bone("Ear_L", (-0.44, -0.28, 2.0), "Head")
    M.bone("Ear_R", (0.44, -0.28, 2.0), "Head")
    M.bone("Tail_1", (0, 0.9, 0.86), "Body")
    leg_bones(M, 0.28, -0.22, 0.68, 0.5)
    M.add("Body", fac(br, bc, "CosmicRock", seed=121), "Body")
    M.add("BodyStars", [star(*on(bc, br, d), 0.14, 0.05, 0.1, "NebStar") for d in ((0.8, 0.2, 0.5), (-0.8, 0.5, 0.4), (0.4, 0.8, 0.6), (-0.3, 0.1, 1))], "Body")
    M.add("ChestGem", gem(*on(bc, br, (0, -1, 0.15)), 0.15, 0.22, 0.12, "CosmicGlow"), "Body")
    M.add("Head", fac(hr, hc, "CosmicRock", seed=122, keep=0.6), "Head")
    M.add("HeadStar", star(*on(hc, hr, (0, -0.7, 0.8)), 0.2, 0.06, 0.1, "CosmicGlow"), "Head")
    M.add("Ruff", [crystals([((s * 0.66, -0.4, 1.32), (s * 1, -0.3, -0.1), 0.34, 0.12), ((s * 0.6, -0.32, 1.12), (s * 1, -0.1, -0.6), 0.3, 0.11)], "NebStar", 4) for s in (-1, 1)], "Head")
    head_set(M, hc, hr, 0.42, -0.02, 0.25)
    for s, nm in ((-1, "L"), (1, "R")):
        M.add("Ear" + nm, pyramid((s * 0.44, -0.26, 1.86), (s * 0.64, -0.3, 2.6), 0.3, "CosmicRock", 4, D(45)), "Ear_" + nm)
        M.add("EarIn" + nm, pyramid((s * 0.44, -0.4, 1.9), (s * 0.6, -0.43, 2.4), 0.17, "NebStar", 4, D(45)), "Ear_" + nm)
        M.add("Tuft" + nm, crystals([((s * 0.64, -0.3, 2.5), (s * 0.15, 0, 1), 0.5, 0.13), ((s * 0.56, -0.26, 2.42), (-s * 0.4, 0.1, 1), 0.36, 0.1),
                                     ((s * 0.74, -0.3, 2.42), (s * 0.8, 0, 1), 0.34, 0.1)], "CosmicGlow"), "Ear_" + nm)
    M.add("Tail", [blob((0.22, 0.24, 0.22), (0, 1.0, 0.92), "CosmicRock", seed=125), gem((0, 1.2, 0.95), (0, 1, 0.2), 0.11, 0.15, 0.1, "NebStar", back=0.5)], "Tail_1")
    legs4_geo(M, "CosmicRock", 0.28, -0.22, 0.68, 0.24, (0.2, 0.22, 0.26), (0.19, 0.21, 0.25), seed=123)
    return M, {"hop": 0.34}


def fix_tail_mats(M):
    pass


def voidling():
    M = Model("PetVoidling")
    M.arch = "float"
    c, r = (0, 0, 1.08), (0.8, 0.76, 0.8)
    M.bone("Body", (0, 0, 0.6))
    M.bone("Ring", (0, 0, 1.08), "Body")
    M.bone("Hand_L", (-1.18, -0.12, 0.86))
    M.bone("Hand_R", (1.18, -0.12, 0.86))
    M.bone("Carry", (0, -0.1, 2.75), "Body")
    M.add("Body", [fac(r, c, "Void", seed=131, keep=0.6), P1.cone(0.3, 0.0, 0.32, (0, 0, 0.18), "Void", rot=(math.pi, 0, 0), verts=5)], "Body")
    M.add("Crystals", crystals([((0.05, 0.0, 1.78), (0.1, 0, 1), 0.62, 0.17), ((0.36, 0.05, 1.7), (0.5, 0, 1), 0.4, 0.12)], "Void", 4), "Body")
    M.add("CrystalGlow", [gem((0.06, -0.12, 2.08), (0, -1, 0), 0.06, 0.16, 0.06, "Cyan"), gem((0.42, -0.08, 1.88), (0.3, -1, 0), 0.05, 0.1, 0.06, "Cyan")], "Body")
    M.add("Ring", torus(1.0, 0.1, c, "Cyan", rot=(D(14), D(-9), 0), major=24, minor=5), "Ring")
    head_set(M, c, r, 0.42, 0.06, 0.27, nose=False, bone="Body")
    for s, nm in ((-1, "L"), (1, "R")):
        M.add("Hand" + nm, fac((0.28, 0.28, 0.28), (s * 1.18, -0.12, 0.86), "Void", sub=1, keep=0.8, seed=133 + s), "Hand_" + nm)
        M.add("HandGlow" + nm, gem((s * 1.18, -0.38, 0.86), (0, -1, 0), 0.12, 0.13, 0.08, "Cyan", back=0.4), "Hand_" + nm)

    def carry(P, t):
        for b, s in (("Hand_L", -1), ("Hand_R", 1)):
            P[b] = ((-s * 0.72, 0.02, 1.62 + 0.04 * math.sin(2 * math.pi * t)), (0, 0, 0))
    return M, {"carry": carry}


def starwhale():
    M = Model("PetStarwhale")
    M.arch = "float"
    c, r = (0, 0.1, 0.95), (0.86, 1.0, 0.88)
    M.bone("Body", (0, 0.1, 0.5))
    M.bone("Tail_1", (0, 0.72, 1.45), "Body")
    M.bone("Tail_2", (0, 0.9, 2.34), "Tail_1")
    M.bone("Fin_L", (-0.72, -0.2, 0.62), "Body")
    M.bone("Fin_R", (0.72, -0.2, 0.62), "Body")
    M.add("Body", fac(r, c, "Whale", seed=141, keep=0.6), "Body")
    M.add("Belly", fac((0.74, 0.62, 0.48), (0, -0.28, 0.6), "WhaleBelly2", sub=1, keep=0.9, seed=142), "Body")
    M.add("Stars", [star(*on(c, r, d), R, R * 0.35, 0.1, "GoldGlow") for d, R in (((0.35, -0.5, 0.75), 0.17), ((-0.7, 0.2, 0.6), 0.15), ((0.75, 0.45, 0.45), 0.13),
                                                                                 ((-0.2, 0.75, 0.6), 0.12), ((0.1, 0.95, 0.15), 0.15))], "Body")
    head_set(M, c, r, 0.44, -0.05, 0.26, nose=False, bone="Body")
    M.add("Tail", [seg((0, 0.7, 1.45), (0, 0.86, 2.0), 0.32, 0.24, "Whale", 6), seg((0, 0.86, 2.0), (0, 0.92, 2.42), 0.24, 0.17, "Whale", 6)], "Tail_1")
    M.add("Ring", torus(0.32, 0.09, (0, 0.86, 2.02), "GoldGlow", rot=(D(-12), 0, 0), major=16, minor=5), "Tail_1")
    M.add("Fluke", [fac((0.4, 0.17, 0.24), (s * 0.34, 0.95, 2.58), "Whale", sub=1, keep=0.8, seed=143 + s, rot=(0, D(-s * 30), 0)) for s in (-1, 1)], "Tail_2")
    for s, nm in ((-1, "L"), (1, "R")):
        M.add("Fin" + nm, fac((0.44, 0.22, 0.13), (s * 0.98, -0.2, 0.42), "Whale", sub=1, keep=0.8, seed=145 + s, rot=(D(-10), D(s * 28), D(-s * 20))), "Fin_" + nm)
    return M, {}


def celestia():
    M = Model("PetCelestia")
    M.arch = "biped"
    hc, hr = (0, -0.22, 2.02), (0.72, 0.62, 0.64)
    bc, br = (0, 0.05, 1.12), (0.55, 0.5, 0.6)
    M.bone("Body", (0, 0.05, 0.62))
    M.bone("Head", (0, -0.12, 1.6), "Body")
    M.bone("Arm_L", (-0.55, -0.05, 1.5), "Body")
    M.bone("Arm_R", (0.55, -0.05, 1.5), "Body")
    M.bone("Leg_L", (-0.3, 0.0, 0.55), "Body")
    M.bone("Leg_R", (0.3, 0.0, 0.55), "Body")
    M.bone("Tail_1", (0, 0.45, 0.72), "Body")
    M.bone("Tail_2", (0, 0.98, 0.6), "Tail_1")
    M.bone("Star_L", (-1.2, -0.1, 1.55))
    M.bone("Star_R", (1.2, -0.1, 1.55))
    M.bone("Carry", (0, -0.55, 3.15), "Body")
    M.add("Body", fac(br, bc, "Celest", seed=151), "Body")
    gems = [gem(*on(bc, br, (0, -1, 0.1)), 0.17, 0.28, 0.13, "Pink")]
    gems += [gem(*on(bc, br, (0, 1, z)), 0.1, 0.16, 0.08, "Pink") for z in (0.55, 0.05)]
    M.add("Gems", gems, "Body")
    M.add("Head", [fac(hr, hc, "Celest", seed=152, keep=0.6)] + [pyramid((s * 0.62, -0.2, 2.2), (s * 1.02, -0.18, 2.4), 0.2, "Celest", 4, D(45)) for s in (-1, 1)], "Head")
    M.add("HeadGem", [gem(*on(hc, hr, (0, -0.7, 0.75)), 0.1, 0.17, 0.08, "Pink"), gem(*on(hc, hr, (0, 0.7, 0.7)), 0.1, 0.16, 0.08, "Pink")], "Head")
    horns = []
    for s in (-1, 1):
        a, b, cc = Vector((s * 0.36, -0.15, 2.5)), Vector((s * 0.5, -0.1, 2.92)), Vector((s * 0.72, -0.02, 3.34))
        horns += [seg(a, b, 0.2, 0.15, "Magenta", 5), cone_to(b, cc, 0.15, "Magenta", 5, 0.0)]
        horns.append(pyramid((s * 0.68, -0.24, 2.22), (s * 0.92, -0.24, 2.34), 0.11, "Magenta", 4))
    M.add("Horns", horns, "Head")
    head_set(M, hc, hr, 0.42, -0.04, 0.25, nose=False)
    for s, nm in ((-1, "L"), (1, "R")):
        M.add("Arm" + nm, [seg((s * 0.55, -0.05, 1.45), (s * 0.68, -0.14, 1.0), 0.17, 0.16, "Celest"), blob((0.2, 0.2, 0.2), (s * 0.7, -0.16, 0.9), "Celest", seed=153 + s)], "Arm_" + nm)
        M.add("Claw" + nm, crystals([((s * 0.7, -0.3, 0.86), (s * 0.2, -1, -0.6), 0.28, 0.08), ((s * 0.82, -0.24, 0.86), (s * 0.7, -0.7, -0.6), 0.26, 0.08),
                                     ((s * 0.6, -0.26, 0.82), (-s * 0.3, -0.8, -0.7), 0.24, 0.08)], "Magenta", 4), "Arm_" + nm)
        M.add("Leg" + nm, blob((0.25, 0.28, 0.36), (s * 0.3, -0.02, 0.35), "Celest", seed=155 + s), "Leg_" + nm)
        M.add("Star" + nm, star((s * 1.2, -0.1, 1.55), (0, -1, 0), 0.34, 0.1, 0.16, "Pink"), "Star_" + nm)
    M.add("Tail1", seg((0, 0.45, 0.72), (0, 1.0, 0.56), 0.2, 0.15, "Celest"), "Tail_1")
    M.add("Tail2", seg((0, 0.98, 0.56), (0, 1.36, 0.92), 0.15, 0.1, "Celest"), "Tail_2")
    M.add("TailSpikes", crystals([((0, 1.08, 0.7), (0, 0.2, 1), 0.28, 0.09), ((0, 1.24, 0.86), (0, 0.4, 1), 0.26, 0.08), ((0, 1.38, 0.98), (0, 0.6, 0.9), 0.36, 0.1)], "Magenta", 4), "Tail_2")

    def carry(P, t):
        for b in ("Arm_L", "Arm_R"):
            s = -1 if b == "Arm_L" else 1
            P[b] = ((0, 0, 0), (D(-150), D(12) * s, 0))
        P["Head"] = ((0, 0, 0), (D(-8), 0, 0))
    return M, {"hop": 0.3, "carry": carry}


def coreling():
    M = Model("PetCoreling")
    M.arch = "walk4"
    bc, br = (0, 0.32, 1.0), (0.86, 0.86, 0.84)
    hc, hr = (0, -0.4, 1.28), (0.7, 0.58, 0.64)
    M.bone("Body", (0, 0.3, 0.5))
    M.bone("Head", (0, -0.25, 1.0), "Body")
    M.bone("Drill", (0, -0.86, 1.08), "Head")
    M.bone("Leg_FL", (-0.6, -0.42, 0.7), "Body")
    M.bone("Leg_FR", (0.6, -0.42, 0.7), "Body")
    M.bone("Leg_BL", (-0.56, 0.7, 0.42), "Body")
    M.bone("Leg_BR", (0.56, 0.7, 0.42), "Body")
    M.bone("Carry", (0, -0.3, 2.62), "Body")
    M.add("Body", fac(br, bc, "DarkRock", seed=161, keep=0.6), "Body")
    seams = [gem(*on(bc, br, d), 0.055, 0.32, 0.05, "CoreRed", up=u) for d, u in (((0.5, 0.6, 0.6), (0, 1, -0.6)), ((-0.5, 0.6, 0.6), (0, 1, -0.6)),
                                                                                  ((0.8, 0.2, 0.4), (0.2, 1, 0.3)), ((-0.8, 0.2, 0.4), (-0.2, 1, 0.3)),
                                                                                  ((0, 0.75, 0.65), (1, 0, 0)), ((0, 0.95, 0.1), (0, 0, 1)), ((0.3, 0.2, 1), (1, 0.4, 0)))]
    M.add("Seams", seams, "Body")
    M.add("Head", fac(hr, hc, "DarkRock", seed=162, keep=0.7), "Head")
    M.add("HeadGlow", [gem(*on(hc, hr, (0, -0.3, 1)), 0.17, 0.26, 0.16, "CoreRed", up=(0, -1, 0.3)),
                       gem(*on(hc, hr, (0.7, -0.4, 0.4)), 0.05, 0.24, 0.05, "CoreRed", up=(0, 1, 1)),
                       gem(*on(hc, hr, (-0.7, -0.4, 0.4)), 0.05, 0.24, 0.05, "CoreRed", up=(0, 1, 1))], "Head")
    dr = [P1.cone(0.4, 0.31, 0.26, (0, -0.94, 1.08), "DarkRock", rot=(D(90), 0, 0), verts=8),
          P1.cone(0.29, 0.18, 0.3, (0, -1.18, 1.08), "DarkRock", rot=(D(90), 0, 0), verts=8),
          P1.cone(0.17, 0.0, 0.36, (0, -1.5, 1.08), "DarkRock", rot=(D(90), 0, 0), verts=8)]
    M.add("Drill", dr, "Drill")
    M.add("DrillGlow", [P1.cone(0.33, 0.33, 0.08, (0, -1.06, 1.08), "CoreRed", rot=(D(90), 0, 0), verts=8),
                        P1.cone(0.2, 0.2, 0.08, (0, -1.34, 1.08), "CoreRed", rot=(D(90), 0, 0), verts=8)], "Drill")
    b, s_ = eyes(hc, hr, 0.5, 0.32, 0.22)
    M.add("Eyes", b, "Head")
    M.add("Shine", s_, "Head")
    for sd, nm in ((-1, "L"), (1, "R")):
        M.add("LegF" + nm, fac((0.33, 0.38, 0.32), (sd * 0.66, -0.52, 0.34), "DarkRock", sub=1, keep=0.9, seed=163 + sd), "Leg_F" + nm)
        M.add("ClawF" + nm, crystals([((sd * 0.66 + dx, -0.76, 0.3), (dx * 0.6, -1, -0.6), 0.44, 0.11) for dx in (-0.17, 0.0, 0.17)], "CoreRed", 4), "Leg_F" + nm)
        M.add("LegB" + nm, fac((0.27, 0.3, 0.24), (sd * 0.56, 0.74, 0.22), "DarkRock", sub=1, keep=0.9, seed=165 + sd), "Leg_B" + nm)

    def carry(P, t):
        for b_ in ("Leg_FL", "Leg_FR"):
            sg = -1 if b_ == "Leg_FL" else 1
            P[b_] = ((0, 0, 0.12), (D(-118), D(10) * sg, 0))
        P["Body"] = ((0, 0, 0), (D(-6), 0, 0))
    return M, {"hop": 0.26, "carry": carry}


def magmacore():
    M = Model("PetMagmacore")
    M.arch = "walk4"
    c, r = (0, 0.28, 1.08), (0.92, 1.0, 0.84)
    hc, hr = (0, -0.5, 1.12), (0.66, 0.52, 0.58)
    M.bone("Body", (0, 0.22, 0.55))
    M.bone("Head", (0, -0.36, 0.95), "Body")
    leg_bones(M, 0.56, -0.32, 0.8, 0.48)
    M.add("Body", fac(r, c, "CoreArmor", seed=171, keep=0.6), "Body")
    sm_ = [crystals([((0, 0.12, 1.84), (0, 0, 1), 0.6, 0.18), ((-0.32, 0.14, 1.8), (-0.4, 0, 1), 0.42, 0.14), ((0.32, 0.14, 1.8), (0.4, 0, 1), 0.42, 0.14),
                     ((-0.6, 0.2, 1.68), (-0.7, 0, 1), 0.3, 0.11), ((0.6, 0.2, 1.68), (0.7, 0, 1), 0.3, 0.11),
                     ((-0.82, 0.55, 1.28), (-1, 0.2, 0.6), 0.44, 0.16), ((0.82, 0.55, 1.28), (1, 0.2, 0.6), 0.44, 0.16)], "Lava")]
    sm_ += [gem(*on(c, r, d), 0.055, 0.34, 0.05, "Lava", up=u) for d, u in (((0.45, 0.7, 0.55), (0, 1, -0.5)), ((-0.45, 0.7, 0.55), (0, 1, -0.5)),
                                                                            ((0.85, -0.1, 0.25), (0, 1, 0.4)), ((-0.85, -0.1, 0.25), (0, 1, 0.4)), ((0, 1, 0.1), (0, 0, 1)))]
    sm_.append(gem((0, -0.76, 0.5), (0, -1, -0.1), 0.26, 0.24, 0.12, "Lava"))
    M.add("Glow", sm_, "Body")
    M.add("Head", [fac(hr, hc, "CoreArmor", seed=172, keep=0.8), seg((0, -0.86, 1.36), (0, -0.92, 1.66), 0.17, 0.16, "CoreArmor", 6)], "Head")
    M.add("Hammer", box((0.96, 0.38, 0.38), (0, -0.94, 1.8), "Lava", 0.08, 1), "Head")
    b, s_ = eyes(hc, hr, 0.6, 0.0, 0.2)
    M.add("Eyes", b, "Head")
    M.add("Shine", s_, "Head")
    for nm, x, y in (("FL", -0.56, -0.32), ("FR", 0.56, -0.32), ("BL", -0.56, 0.8), ("BR", 0.56, 0.8)):
        M.add("Leg" + nm, blob((0.3, 0.3, 0.3), (x, y, 0.26), "CoreArmor", seed=173 + int(x * 7 + y * 3)), "Leg_" + nm)
        M.add("Toe" + nm, gem((x, y - 0.26, 0.12), (0, -1, 0.2), 0.12, 0.08, 0.1, "Lava"), "Leg_" + nm)
    return M, {"hop": 0.24}


PETS = [("Pebblit", pebblit), ("Cinderpup", cinderpup), ("Glintmoth", glintmoth), ("Rubblord", rubblord),
        ("Emberkit", emberkit), ("Magmaw", magmaw), ("Flarefly", flarefly), ("Solarix", solarix),
        ("Frostling", frostling), ("Shardbun", shardbun), ("Glacio", glacio), ("Aurorabe", aurorabe),
        ("Nebulynx", nebulynx), ("Voidling", voidling), ("Starwhale", starwhale), ("Celestia", celestia),
        ("Coreling", coreling), ("Magmacore", magmacore)]


# ======================================================================= eggs: one shell split along a zig-zag crack
EGG_S, EGG_R = 10, 9          # segments, rings (pole to pole)
EGG_H, EGG_W = 3.4, 2.5
CRACK_LO, CRACK_HI = 4, 6     # ring indices of the lower / upper zig-zag crack
N_SHARDS = 5
EGG_SCALE = 0.9


def egg_vert(k, s):
    th = math.pi * k / EGG_R
    z = (1 - math.cos(th)) / 2 * EGG_H
    rad = math.sin(th) * EGG_W / 2 * (1.12 - 0.26 * z / EGG_H)
    a = 2 * math.pi * (s + 0.5 * (k % 2)) / EGG_S  # staggered rows -> brick / hex-like plates
    if k in (CRACK_LO, CRACK_HI):
        z += 0.13 * (1 if (s + k) % 2 == 0 else -1)  # zig-zag crack line
    return Vector((math.cos(a) * rad, math.sin(a) * rad, z))


def egg_region(k, s):
    """face row k (between ring k and k+1), segment s -> piece name"""
    if k < CRACK_LO:
        return "Bottom"
    if k >= CRACK_HI:
        return "Top"
    row = k - CRACK_LO
    return f"Shard_{((s + row) // 2) % N_SHARDS + 1}"


def egg_pieces(lift=0.025, shrink=0.84, plates=True, thick=0.12):
    """-> {piece: (shell bmesh, plate bmesh, centroid)} ; plates = raised shrunken face copies (stone plates / seams)"""
    pieces = {}
    for k in range(EGG_R):
        for s in range(EGG_S):
            pn = egg_region(k, s)
            s1 = (s + 1) % EGG_S
            if k == 0:
                q = [Vector((0, 0, 0)), egg_vert(1, s1), egg_vert(1, s)]
            elif k == EGG_R - 1:
                q = [egg_vert(k, s), egg_vert(k, s1), Vector((0, 0, EGG_H))]
            else:
                q = [egg_vert(k, s), egg_vert(k, s1), egg_vert(k + 1, s1), egg_vert(k + 1, s)]
            pieces.setdefault(pn, []).append((q, k))
    out = {}
    for pn, faces in pieces.items():
        bm = bmesh.new()
        cache = {}

        def V(p):
            key = tuple(round(x, 5) for x in p)
            if key not in cache:
                cache[key] = bm.verts.new(p)
            return cache[key]
        pl = bmesh.new()
        cen = Vector()
        for q, k in faces:
            bm.faces.new([V(p) for p in q])
            c = sum(q, Vector()) / len(q)
            cen += c
            if plates and 0 < k < EGG_R - 1:
                n = (q[1] - q[0]).cross(q[2] - q[0]).normalized()
                pl.faces.new([pl.verts.new(c + (p - c) * shrink + n * lift) for p in q])
        out[pn] = (bm, pl, cen / len(faces))
    return out


def shell_obj(bm, mat, thick=0.12):
    o = mesh_obj("sh", bm, mat)
    m = o.modifiers.new("Solid", "SOLIDIFY")
    m.thickness = thick
    m.offset = -1
    m.use_rim = True
    return o


EGGS = [("Rock", "PebSpot", "PebBody"), ("Ember", "CinderGlow", "CinderBody"), ("Frost", "IceRock", None),
        ("Cosmic", "CosmicRock", None), ("Core", "Lava", "CoreArmor")]


def egg_model(name, shell, plate):
    M = Model("Egg" + name, "egg")
    pcs = egg_pieces(plates=plate is not None)
    M.bone("Bottom", (0, 0, 0))
    M.bone("Top", (0, 0, egg_vert(CRACK_HI, 0).z))
    for i in range(1, N_SHARDS + 1):
        M.bone(f"Shard_{i}", pcs[f"Shard_{i}"][2])
    rnd = random.Random(hash(name) % 1000)

    def acc_piece(pn):
        return "Bottom" if pn == "Bottom" else ("Top" if pn == "Top" else pn)
    pmap = {"Bottom": "Bottom", "Top": "Top"}
    pmap.update({f"Shard_{i}": f"Shard_{i}" for i in range(1, N_SHARDS + 1)})
    extra = {pn: [] for pn in pmap}  # piece -> accent objects (same MatKey per call)
    for pn, (bm, pl, cen) in pcs.items():
        nm = {"Bottom": "ShellBottom", "Top": "ShellTop"}.get(pn, pn)
        M.add(nm, shell_obj(bm, shell), pn)
        if plate:
            M.add({"Bottom": "PlatesBottom", "Top": "PlatesTop"}.get(pn, "Plates" + pn[5:]), mesh_obj("pl", pl, plate), pn)
        else:
            pl.free()

    def ring_angle_piece(a):
        s = int((a % (2 * math.pi)) / (2 * math.pi) * EGG_S)
        return f"Shard_{((s + 0) // 2) % N_SHARDS + 1}"
    zt = egg_vert(CRACK_HI, 0).z
    if name == "Rock":
        M.add("Crest", crystals([((0.1, 0.0, 3.2), (0.2, 0, 1), 0.72, 0.2), ((0.42, 0.2, 2.98), (0.8, 0.3, 1), 0.6, 0.18),
                                 ((-0.3, 0.32, 3.02), (-0.6, 0.5, 1), 0.5, 0.16), ((0.35, -0.3, 2.95), (0.6, -0.6, 1), 0.46, 0.15),
                                 ((-0.36, -0.28, 2.98), (-0.6, -0.5, 1), 0.4, 0.13)], "PebCrystal"), "Top")
        a = 0.3
        p = Vector((math.cos(a) * 1.3, math.sin(a) * 1.3, 2.0))
        sp = ring_angle_piece(a)
        M.add("SideCrystals", crystals([(p, (1, 0.3, 0.6), 0.48, 0.15), (p + Vector((0, 0.2, -0.25)), (1, 0.4, 0.2), 0.36, 0.12)], "PebCrystal"), sp)
    elif name == "Ember":
        M.add("Crest", crystals([((0, 0, 3.15), (0, 0, 1), 0.85, 0.24), ((0.3, 0.1, 3.0), (0.5, 0.1, 1), 0.6, 0.18), ((-0.3, -0.1, 3.0), (-0.5, -0.1, 1), 0.6, 0.18),
                                 ((0.05, 0.32, 3.0), (0.1, 0.6, 1), 0.5, 0.16), ((0.0, -0.34, 3.0), (0, -0.6, 1), 0.5, 0.16)], "CinderGlow", 4), "Top")
    elif name == "Frost":
        by = {}
        for i in range(12):
            a = 2 * math.pi * (i / 12) + rnd.uniform(-0.15, 0.15)
            kz = [0.6, 1.1, 1.7, 2.3][i % 4]
            k = 1 + int(math.acos(1 - 2 * kz / EGG_H) / math.pi * EGG_R)
            th = math.pi * (math.acos(1 - 2 * kz / EGG_H) / math.pi)
            rad = math.sin(th) * EGG_W / 2 * (1.12 - 0.26 * kz / EGG_H)
            base = Vector((math.cos(a) * rad * 0.92, math.sin(a) * rad * 0.92, kz))
            s = int((a % (2 * math.pi)) / (2 * math.pi) * EGG_S)
            pn = egg_region(min(k - 1, EGG_R - 1), s)
            by.setdefault(pn, []).append((base, (math.cos(a) * 0.5, math.sin(a) * 0.5, 1), 0.55 + 0.2 * (i % 3), 0.15))
        for pn, spec in by.items():
            M.add("Ice" + ({"Bottom": "Bottom", "Top": "Top"}.get(pn, pn[5:])), crystals(spec, "FrostCrystal"), pn)
        M.add("Crest", crystals([((0, 0, 3.2), (0, 0, 1), 0.72, 0.2), ((0.3, 0, 3.05), (0.6, 0, 1), 0.5, 0.15), ((-0.3, 0, 3.05), (-0.6, 0, 1), 0.5, 0.15),
                                 ((0, 0.3, 3.05), (0, 0.6, 1), 0.45, 0.14), ((0, -0.3, 3.05), (0, -0.6, 1), 0.45, 0.14)], "FrostCrystal"), "Top")
    elif name == "Cosmic":
        sts = {}
        for d, z in (((1, -0.4, 0), 1.0), ((-0.6, -0.8, 0), 2.1), ((-0.5, 0.9, 0), 0.8), ((0.7, 0.7, 0), 2.6), ((-1, 0.1, 0), 1.7)):
            a = math.atan2(d[1], d[0])
            th = math.acos(1 - 2 * z / EGG_H)
            rad = math.sin(th) * EGG_W / 2 * (1.12 - 0.26 * z / EGG_H)
            p = Vector((math.cos(a) * rad, math.sin(a) * rad, z))
            k = min(EGG_R - 1, int(th / math.pi * EGG_R))
            s = int((a % (2 * math.pi)) / (2 * math.pi) * EGG_S)
            sts.setdefault(egg_region(k, s), []).append(star(p, Vector((math.cos(a), math.sin(a), 0.2)), 0.32, 0.1, 0.12, "CosmicGlow"))
        for pn, objs in sts.items():
            M.add("Stars" + ({"Bottom": "Bottom", "Top": "Top"}.get(pn, pn[5:])), objs, pn)
        # thick orbit ring split into arcs that ride the shards (the portal pieces)
        arcs = {}
        Rr, rr, nseg = 1.62, 0.12, 15
        tilt = Matrix.Translation((0, 0, 1.75)) @ Euler((D(-20), D(12), 0)).to_matrix().to_4x4()
        for i in range(nseg):
            a0, a1 = 2 * math.pi * i / nseg, 2 * math.pi * (i + 1) / nseg
            pn = f"Shard_{(i * N_SHARDS) // nseg + 1}"
            arcs.setdefault(pn, []).append((a0, a1))
        for pn, segs in arcs.items():
            bm = bmesh.new()
            for a0, a1 in segs:
                rings = []
                for a in (a0, a1):
                    ring = []
                    for j in range(4):
                        b = 2 * math.pi * j / 4 + math.pi / 4
                        p = Vector((math.cos(a) * (Rr + math.cos(b) * rr), math.sin(a) * (Rr + math.cos(b) * rr), math.sin(b) * rr * 1.3))
                        ring.append(bm.verts.new(tilt @ p))
                    rings.append(ring)
                for j in range(4):
                    j1 = (j + 1) % 4
                    bm.faces.new((rings[0][j], rings[0][j1], rings[1][j1], rings[1][j]))
                bm.faces.new(rings[0][::-1])
                bm.faces.new(rings[1])
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
            M.add("Ring" + pn[5:], mesh_obj("r", bm, "NebStar"), pn)
    elif name == "Core":
        M.add("Crest", [P1.cone(0.5, 0.36, 0.3, (0, 0, 3.32), "CoreArmor", verts=6), P1.cone(0.34, 0.2, 0.3, (0, 0, 3.66), "CoreArmor", verts=6),
                        P1.cone(0.19, 0.0, 0.42, (0, 0, 4.02), "CoreArmor", verts=6)], "Top")
        M.add("CrestGlow", [P1.cone(0.42, 0.42, 0.08, (0, 0, 3.5), "Lava", verts=6), P1.cone(0.26, 0.26, 0.08, (0, 0, 3.84), "Lava", verts=6)], "Top")
        fins = {}
        for s in (-1, 1):
            a = 0 if s > 0 else math.pi
            p = Vector((math.cos(a) * 1.35, math.sin(a) * 1.35, 1.0))
            fins.setdefault("Bottom", []).append(fac((0.22, 0.42, 0.6), p, "CoreArmor", sub=1, keep=0.5, seed=190 + s))
        M.add("Fins", fins["Bottom"], "Bottom")
    # scale the finished egg so shell + crest stand ~3.4 studs (shell modelled 3.4 tall)
    k = EGG_SCALE
    for o, _ in M.parts:
        o.data.transform(Matrix.Scale(k, 4))
        o.location *= k
    M.bones = [(n, h * k, par) for n, h, par in M.bones]
    M.arch = name
    return M


def egg_clips(M):
    name = M.arch
    pcs = [(f"Shard_{i}", next(h for n, h, _ in M.bones if n == f"Shard_{i}")) for i in range(1, N_SHARDS + 1)]
    zt = next(h for n, h, _ in M.bones if n == "Top").z
    F = {"Rock": dict(top=1.1, side=0.9, spin=1.0, out=1.3, up=0.7, shake=1.0),
         "Ember": dict(top=2.4, side=0.5, spin=2.5, out=1.9, up=1.6, shake=1.2),
         "Frost": dict(top=1.5, side=1.1, spin=3.0, out=2.5, up=1.0, shake=1.0),
         "Cosmic": dict(top=1.8, side=0.2, spin=1.5, out=2.2, up=0.9, shake=0.7, orbit=1.0),
         "Core": dict(top=3.4, side=0.3, spin=3.5, out=2.0, up=2.2, shake=1.6)}[name]

    def idle(t, f):
        return {"Root": ((0, 0, 0), (D(2.2) * math.sin(2 * math.pi * t), D(3) * math.sin(2 * math.pi * t + 1.1), 0))}

    def hatch_fn(T_crack, T_end):
        def fn(t, f):
            P = {}
            tt = t * T_end  # seconds
            # wobble that speeds up
            w = min(1.0, tt / T_crack)
            ph = 2 * math.pi * (1.2 * tt + 2.6 * tt * tt / T_crack) * (1.6 / T_crack) ** 0.5
            amp = D(3 + 11 * w * w) * F["shake"] * (1 - sm(seg01(tt, T_crack, T_crack + 0.25)))
            hopz = 0.06 * max(0, math.sin(ph * 2)) * w * w * F["shake"]
            P["Root"] = ((0, 0, hopz), (amp * math.sin(ph), amp * 0.7 * math.cos(ph * 0.9), 0))
            # crack: pieces separate after T_crack
            u = max(0.0, tt - T_crack) / (T_end - T_crack)  # 0..1
            if u > 0:
                g = 1 - (1 - u) ** 2
                # top pops up, tumbles, lands beside the egg
                side = F["side"]
                up = F["top"] * 4 * min(u, 1) * (1 - min(u, 1)) * 1.0
                fall = -zt * sm(seg01(u, 0.55, 1.0)) + 0.35 * sm(seg01(u, 0.55, 1.0))
                tx = side * 1.2 * g
                P["Top"] = ((tx, side * 0.6 * g, up + fall), (D(100) * side * g + D(20) * g, D(F["spin"] * 120) * g * (0.3 if name == "Rock" else 1), D(F["spin"] * 60) * g))
                for i, (pn, h) in enumerate(pcs):
                    a = math.atan2(h.y, h.x)
                    out = Vector((math.cos(a), math.sin(a), 0))
                    if F.get("orbit"):
                        ang = D(160) * sm(u) * (1 - 0.3 * u)
                        rot_h = Matrix.Rotation(ang, 3, "Z") @ h
                        d = (rot_h - h) + out * F["out"] * sm(seg01(u, 0.35, 1.0)) * 1.0
                        z = F["up"] * 4 * u * (1 - u) - (h.z - 0.25) * sm(seg01(u, 0.6, 1.0))
                        P[pn] = ((d.x, d.y, z), (D(30) * g, D(F["spin"] * 50) * g, ang + D(90) * g))
                    else:
                        d = out * F["out"] * g * (0.85 + 0.15 * (i % 2))
                        z = F["up"] * 4 * u * (1 - u) * (0.8 + 0.2 * (i % 3)) - (h.z - 0.22) * sm(seg01(u, 0.45, 1.0))
                        tilt = D(70 + 20 * (i % 2)) * g
                        P[pn] = ((d.x, d.y, z), (-tilt * math.sin(a), tilt * math.cos(a), D(F["spin"] * 40) * g * (1 if i % 2 else -1)))
            elif tt > T_crack - 0.18:  # crack forming: shards jitter
                j = (tt - (T_crack - 0.18)) / 0.18
                for i, (pn, h) in enumerate(pcs):
                    a = math.atan2(h.y, h.x)
                    P[pn] = ((math.cos(a) * 0.03 * j, math.sin(a) * 0.03 * j, 0.01 * j * ((-1) ** i)), (0, 0, 0))
                P["Top"] = ((0, 0, 0.04 * j), (0, 0, 0))
            return P
        return fn
    key_clip(M, "Idle", 60, idle, loop=True)
    key_clip(M, "Hatch", 72, hatch_fn(1.6, 2.4), markers={"Crack": 48, "PetOut": 51})
    key_clip(M, "HatchFast", 27, hatch_fn(0.5, 0.9), markers={"Crack": 15, "PetOut": 17})


# ======================================================================= Pet Fuser (plot machine, 7 x 7 footprint, ~7.5 tall)
FUSER_W = 7.0
FUSER_ORB_R, FUSER_ORB_Z = 2.15, 3.35
FUSER_PILLARS = (D(90), D(210), D(330))  # back + front-left + front-right
FUSER_TIP_Z = 4.62


def fuser(M):
    """rigid parts with the names the existing orbit animation uses (Base, Orb1-3, Core, Chamber, Tip1-3)"""
    half = FUSER_W / 2
    base = box((FUSER_W, FUSER_W, 0.8), (0, 0, 0.4), "Steel", 0.25, 2)
    M.add("Base", base, "Root")
    M.add("Trim", [box((6.5, 6.5, 0.32), (0, 0, 0.94), "Cream", 0.12, 1), box((3.6, 0.55, 0.9), (0, -2.85, 1.45), "Cream", 0.12, 1)], "Root")
    M.add("Plinth", [cyl(2.0, 1.0, (0, 0, 1.6), "Red", "Z", 12, 0.12, 1), cyl(1.95, 0.9, (0, 0, 5.4), "Red", "Z", 12, 0.12, 1)], "Root")
    M.add("Rims", [cyl(1.78, 0.22, (0, 0, 2.18), "Yellow", "Z", 12, 0.05, 1), cyl(1.78, 0.22, (0, 0, 4.86), "Yellow", "Z", 12, 0.05, 1)], "Root")
    M.add("Chamber", cyl(1.55, 2.6, (0, 0, 3.52), "Glass", "Z", 12, 0.0, 1), "Chamber")
    M.add("Core", fac((0.55, 0.55, 0.55), (0, 0, 3.4), "Gold", sub=1, keep=1.0, seed=201, jit=0.08), "Core")
    M.add("CoreStand", [cyl(0.42, 0.5, (0, 0, 2.45), "SteelLight", "Z", 8, 0.05, 1)], "Root")
    M.add("Dome", [cyl(1.5, 0.7, (0, 0, 6.2), "Steel", "Z", 12, 0.12, 1, r2=0.85), cyl(0.5, 0.35, (0, 0, 6.72), "SteelLight", "Z", 8, 0.06, 1)], "Root")
    M.add("Beacon", fac((0.32, 0.32, 0.32), (0, 0, 7.12), "Teal", sub=1, keep=1.0, seed=202), "Root")
    pillars, caps = [], []
    for i, a in enumerate(FUSER_PILLARS):
        d = Vector((math.cos(a), math.sin(a), 0))
        foot = d * 3.0
        pillars.append(box((0.7, 0.7, 5.2), (foot.x, foot.y, 3.4), "Red", 0.18, 2, rot=(0, 0, a)))
        pillars.append(box((0.5, 0.5, 0.5), (d.x * 2.62, d.y * 2.62, FUSER_TIP_Z), "Steel", 0.1, 1, rot=(0, 0, a)))
        caps.append(box((0.9, 0.9, 0.32), (foot.x, foot.y, 1.0), "Cream", 0.1, 1, rot=(0, 0, a)))
        caps.append(box((0.9, 0.9, 0.36), (foot.x, foot.y, 6.1), "Cream", 0.1, 1, rot=(0, 0, a)))
        tip = crystals([(d * 2.5 + Vector((0, 0, FUSER_TIP_Z)), (-d.x, -d.y, -0.12), 0.55, 0.19)], "Teal", 4)
        M.add(f"Tip{i + 1}", tip, f"Tip{i + 1}")
    M.add("Pillars", pillars, "Root")
    M.add("Caps", caps, "Root")
    for i, a in enumerate((D(30), D(150), D(270))):
        p = Vector((math.cos(a) * FUSER_ORB_R, math.sin(a) * FUSER_ORB_R, FUSER_ORB_Z))
        M.add(f"Orb{i + 1}", fac((0.32, 0.32, 0.32), p, "Teal", sub=1, keep=1.0, seed=210 + i), f"Orb{i + 1}")
    M.add("Buttons", [cyl(0.24, 0.24, (x, -3.15, 1.65), "Yellow", "Y", 10, 0.04, 1) for x in (-1.0, 0.0, 1.0)], "Root")


def fuser_bones(M):
    M.bone("Chamber", (0, 0, 2.2))
    M.bone("Core", (0, 0, 3.4))
    M.bone("Orbs", (0, 0, FUSER_ORB_Z))
    for i, a in enumerate((D(30), D(150), D(270))):
        M.bone(f"Orb{i + 1}", (math.cos(a) * FUSER_ORB_R, math.sin(a) * FUSER_ORB_R, FUSER_ORB_Z), "Orbs")
    for i, a in enumerate(FUSER_PILLARS):
        d = Vector((math.cos(a), math.sin(a), 0))
        M.bone(f"Tip{i + 1}", d * 2.5 + Vector((0, 0, FUSER_TIP_Z)))


def fuser_clips(M):
    def fuse(t, f):
        P = {}
        T = t * 2.0
        spin = 2 * math.pi * (0.6 * T * T * 1.3 if T < 1.35 else (0.6 * 1.35 ** 2 * 1.3 + 3.5 * (T - 1.35) - 2.2 * (T - 1.35) ** 2))
        lift = 0.55 * sm(seg01(T, 0.1, 1.2)) * (1 - sm(seg01(T, 1.5, 2.0)))
        pull = sm(seg01(T, 0.6, 1.3)) * (1 - sm(seg01(T, 1.45, 1.9)))
        P["Orbs"] = ((0, 0, lift), (0, 0, spin))
        for i, a in enumerate((D(30), D(150), D(270))):
            d = Vector((math.cos(a), math.sin(a), 0))
            P[f"Orb{i + 1}"] = ((-d.x * 0.75 * pull, -d.y * 0.75 * pull, 0.12 * math.sin(T * 9 + i)), (0, 0, 0))
        flash = bump(T, 1.3, 1.5)
        pulse = 0.12 * math.sin(T * 2 * math.pi * 2.5) * sm(seg01(T, 0.2, 1.3)) * (1 - seg01(T, 1.6, 2.0))
        P["Core"] = ((0, 0, pulse + 0.35 * flash), (D(30) * flash, 0, spin * 0.5))
        P["Chamber"] = ((0.04 * math.sin(T * 70) * flash, 0.04 * math.cos(T * 63) * flash, 0.05 * flash), (0, 0, 0))
        for i, a in enumerate(FUSER_PILLARS):
            d = Vector((math.cos(a), math.sin(a), 0))
            jab = 0.35 * bump(T, 1.2, 1.55)
            P[f"Tip{i + 1}"] = ((-d.x * jab, -d.y * jab, -0.2 * jab), (0, 0, 0))
        return P
    key_clip(M, "Fuse", 60, fuse, markers={"Flash": 40, "PetOut": 44})


# ======================================================================= build + stats
def tris_of(o):
    return sum(len(p.vertices) - 2 for p in o.data.polygons)


def world_bbox(objs):
    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return mn, mx


MODELS = []


def build_all(only=None):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    MODELS.clear()
    for n, fn in PETS:
        if only and n not in only:
            continue
        M, opt = fn()
        make_rig(M)
        pet_clips(M, opt)
        MODELS.append(M)
    for n, shell, plate in EGGS:
        if only and "Egg" + n not in only:
            continue
        M = egg_model(n, shell, plate)
        make_rig(M)
        egg_clips(M)
        MODELS.append(M)
    if not only or "PetFuser" in only:
        M = Model("PetFuser", "fuser")
        fuser(M)
        make_static(M)
        MODELS.append(M)
        M = Model("FuserRig", "fuser")
        fuser(M)
        fuser_bones(M)
        make_rig(M)
        fuser_clips(M)
        MODELS.append(M)
    # layout (rows of 6); every model keeps its pivot at its own origin
    for k, M in enumerate(MODELS):
        top = M.arm or M.root
        top.location = ((k % 6) * 5.0 - 12.5, (k // 6) * 6.0, 0) if M.kind != "fuser" else ((k % 6) * 9.0 - 20, 30, 0)
    bpy.context.view_layer.update()
    return MODELS


def stats(Ms):
    rows, bad = [], []
    for M in Ms:
        objs = [o for o, _ in M.parts]
        tris = sum(tris_of(o) for o in objs)
        top = M.arm or M.root
        mn, mx = world_bbox(objs)
        size = mx - mn
        nb = len(M.arm.data.bones) if M.arm else 0
        lim = LIMITS["Celestia_tris"] if M.name == "PetCelestia" else LIMITS["pet_tris"] if M.kind == "pet" else LIMITS["egg_tris"] if M.kind == "egg" else LIMITS["fuser_tris"]
        if tris > lim:
            bad.append(f"{M.name}: {tris} tris > {lim}")
        if M.kind == "pet" and len(objs) > LIMITS["pet_parts"]:
            bad.append(f"{M.name}: {len(objs)} parts > {LIMITS['pet_parts']}")
        if nb > LIMITS["bones"]:
            bad.append(f"{M.name}: {nb} bones")
        if M.kind == "pet" and not (2.0 <= size.z <= 3.5):
            bad.append(f"{M.name}: height {size.z:.2f}")
        if abs((mn.z - top.location.z)) > 0.06 and M.kind != "pet":
            bad.append(f"{M.name}: bottom at {mn.z - top.location.z:.2f}, pivot must be the bottom")
        clips = " ".join(f"{c.split('_', 1)[1]}:{fr / FPS:.2f}s{'L' if lp else ''}" for c, (fr, lp, _) in M.clips.items())
        rows.append((M.name, len(objs), tris, f"{size.x:.2f} x {size.y:.2f} x {size.z:.2f}", nb, clips))
    return rows, bad


def print_table(rows):
    print(f"{'model':16s} {'parts':>5s} {'tris':>5s}  {'bbox X x Y x Z (studs)':24s} {'bones':>5s}  clips (L = loop)")
    for r in rows:
        print(f"{r[0]:16s} {r[1]:5d} {r[2]:5d}  {r[3]:24s} {r[4]:5d}  {r[5]}")


# ======================================================================= export
EXPORT_ROT = Matrix(((-1, 0, 0, 0), (0, 0, 1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))  # Blender (x,y,z) -> FBX (-x, z, y)
FBX_KW = dict(apply_unit_scale=True, apply_scale_options="FBX_SCALE_ALL", axis_forward="Z", axis_up="Y",
              use_space_transform=False, bake_space_transform=False, use_mesh_modifiers=False, mesh_smooth_type="FACE",
              add_leaf_bones=False, primary_bone_axis="Y", secondary_bone_axis="X", armature_nodetype="NULL",
              use_armature_deform_only=False)


def bake_axes():
    """apply the FBX axis change to the scene data itself (rotation of every top-level object, then applied),
    so the file carries Y-up / -Z-front vertex + bone data and identity node rotations. Blender's own
    bake_space_transform is documented as broken with armatures, so this does the same thing by hand."""
    tops = [o for o in bpy.data.objects if o.parent is None and o.type in ("ARMATURE", "EMPTY")]
    for o in tops:
        o.matrix_world = EXPORT_ROT @ o.matrix_world
    bpy.context.view_layer.update()
    for o in bpy.data.objects:
        o.select_set(o.type in ("ARMATURE", "EMPTY", "MESH"))
    bpy.context.view_layer.objects.active = tops[0]
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)


def rest_pose(arm):
    if arm.animation_data:
        arm.animation_data.action = None
    for pb in arm.pose.bones:
        pb.location = (0, 0, 0)
        pb.rotation_quaternion = (1, 0, 0, 0)


def export_all(Ms):
    os.makedirs(ANIM, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)
    bake_axes()
    for M in Ms:
        if M.arm:
            rest_pose(M.arm)
    for o in bpy.data.objects:
        o.select_set(o.type in ("ARMATURE", "EMPTY", "MESH"))
    bpy.ops.export_scene.fbx(filepath=FBX_MAIN, use_selection=True, object_types={"ARMATURE", "EMPTY", "MESH"}, bake_anim=False, **FBX_KW)
    # the same models one per file (fallback if an importer struggles with 24 rigs in one file; same names + positions)
    os.makedirs(SPLIT, exist_ok=True)
    for M in Ms:
        top = M.arm or M.root
        for o in bpy.data.objects:
            o.select_set(o == top or o.parent == top)
        bpy.ops.export_scene.fbx(filepath=os.path.join(SPLIT, M.name + ".fbx"), use_selection=True,
                                 object_types={"ARMATURE", "EMPTY", "MESH"}, bake_anim=False, **FBX_KW)
    sc = bpy.context.scene
    n = 0
    for M in Ms:
        if not M.arm:
            continue
        for clip, (frames, loop, markers) in M.clips.items():
            act = bpy.data.actions[clip]
            for o in bpy.data.objects:
                o.select_set(o == M.arm)
            bpy.context.view_layer.objects.active = M.arm
            M.arm.animation_data.action = act
            if act.slots:
                M.arm.animation_data.action_slot = act.slots[0]
            sc.frame_start, sc.frame_end = 0, frames
            sc.render.fps = FPS
            sc.name = clip
            bpy.ops.export_scene.fbx(filepath=os.path.join(ANIM, clip + ".fbx"), use_selection=True, object_types={"ARMATURE"},
                                     bake_anim=True, bake_anim_use_all_bones=True, bake_anim_use_nla_strips=False,
                                     bake_anim_use_all_actions=False, bake_anim_force_startend_keying=True,
                                     bake_anim_step=1.0, bake_anim_simplify_factor=0.0, **FBX_KW)
            n += 1
            rest_pose(M.arm)
    meta = {clip: {"model": M.name, "rig": M.arm.name, "frames": fr, "seconds": round(fr / FPS, 3), "loop": bool(lp), "markers": mk}
            for M in Ms if M.arm for clip, (fr, lp, mk) in M.clips.items()}
    with open(os.path.join(ANIM, "clips.json"), "w") as fh:
        json.dump(meta, fh, indent=1, sort_keys=True)
    print(f"exported {FBX_MAIN} and {n} clip FBX files")


# ======================================================================= verification (fresh scene, re-imported FBX)
def mat_key(name):
    m = re.match(r"^(\w+?)__(.+?)__([A-Za-z0-9]+)", name)
    return (m.group(1), m.group(2), m.group(3)) if m else (None, None, None)


def preview_materials():
    for o in bpy.data.objects:
        if o.type != "MESH":
            continue
        model, pname, key = mat_key(o.name)
        if key in BM.PALETTE:
            o.data.materials.clear()
            m = BM.material(key)
            if key == "Glass" and not m.get("glass"):
                b = m.node_tree.nodes["Principled BSDF"]
                b.inputs["Alpha"].default_value = 0.35
                m["glass"] = 1
            if BM.PALETTE[key][3] and not m.get("tamed"):
                m.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 1.0
                m["tamed"] = 1
            o.data.materials.append(m)


def import_fbx(path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=path, automatic_bone_orientation=False)
    bpy.context.view_layer.update()


def models_in_scene():
    out = {}
    for o in bpy.data.objects:
        if o.type == "MESH":
            model, pname, key = mat_key(o.name)
            if model:
                out.setdefault(model, []).append(o)
    return out


def verify():
    import_fbx(FBX_MAIN)
    groups = models_in_scene()
    fails = []
    print("\nRe-import of SF_Pets_v2.fbx (Blender reads the file's Y-up axis settings and converts back to Z-up):")
    print(f"{'model':16s} {'bbox X x Y x Z':24s} {'bottom z':>8s}  up/front check")
    for model in sorted(groups):
        objs = groups[model]
        mn, mx = world_bbox(objs)
        size = mx - mn
        eyes = [o for o in objs if "__Eyes__" in o.name or "__Nose__" in o.name]
        front = "-"
        if eyes:
            emn, emx = world_bbox(eyes)
            cy = (emn.y + emx.y) / 2 - (mn.y + mx.y) / 2
            cz = (emn.z + emx.z) / 2 - mn.z
            front = "ok (eyes at -Y, upper half)" if cy < 0 and cz > size.z * 0.3 else "WRONG"
            if front == "WRONG":
                fails.append(f"{model}: eyes not on the front/top ({cy:.2f}, {cz:.2f})")
        if model.startswith("Egg"):
            top = [o for o in objs if "__ShellTop__" in o.name]
            tmn, tmx = world_bbox(top)
            front = "ok (ShellTop above)" if tmn.z > mn.z + size.z * 0.5 else "WRONG"
            if front == "WRONG":
                fails.append(f"{model}: ShellTop not on top")
        if model in ("PetFuser", "FuserRig"):
            base = [o for o in objs if "__Base__" in o.name]
            bmn, bmx = world_bbox(base)
            w = bmx.x - bmn.x
            front = f"Base {w:.3f} wide, at the bottom" if bmn.z - mn.z < 0.01 else "WRONG"
            if abs(w - FUSER_W) > 0.02:
                fails.append(f"{model}: Base width {w:.3f} != {FUSER_W}")
        print(f"{model:16s} {size.x:5.2f} x {size.y:5.2f} x {size.z:5.2f}      {mn.z:8.2f}  {front}")
        if size.z > size.x * 3 or size.z < 0.5:
            fails.append(f"{model}: suspicious proportions {size}")
    arms = [o for o in bpy.data.objects if o.type == "ARMATURE"]
    print(f"armatures: {len(arms)}; bones per rig: " + ", ".join(f"{a.name.split('__')[0]}={len(a.data.bones)}" for a in sorted(arms, key=lambda a: a.name)))
    # raw node check: every node rotation in the file is the identity (nothing for an importer to apply twice)
    raw = raw_node_rotations(FBX_MAIN)
    nonid = [(n, r) for n, kind, r in raw if kind != "LimbNode" and r and any(abs(x) > 1e-3 for x in r)]
    print(f"raw FBX: {len(raw)} model nodes, {len(nonid)} non-bone nodes with a rotation" + (f": {nonid[:4]}" if nonid else ""))
    if nonid:
        fails.append("non-identity node rotations in the FBX")
    # skinning straight from the file data (Blender's importer drops some bindings in a 24-rig file: it re-parents
    # meshes while iterating the root's children in collect_armature_meshes, so it cannot be the judge here)
    for path in [FBX_MAIN] + sorted(os.path.join(SPLIT, f) for f in os.listdir(SPLIT)):
        n, bad = raw_skin_check(path)
        if path == FBX_MAIN:
            print(f"raw skin check: {n} skinned meshes, each 100% on one bone of its own <Model>__Rig" + (f"; {len(bad)} BAD" if bad else ""))
        fails += [f"{os.path.basename(path)}: {b}" for b in bad]
    # split files: each re-imports as one bound rig with the same bounding box as in the combined file
    ref_bb = {m: world_bbox(o) for m, o in groups.items()}
    split_bad = []
    for f in sorted(os.listdir(SPLIT)):
        import_fbx(os.path.join(SPLIT, f))
        g = models_in_scene()
        for m, objs in g.items():
            unbound = [o.name for o in objs if m != "PetFuser" and not any(md.type == "ARMATURE" for md in o.modifiers)]
            mn, mx = world_bbox(objs)
            d = max((mn - ref_bb[m][0]).length, (mx - ref_bb[m][1]).length)
            if unbound or d > 0.01 or len(objs) != len(groups[m]):
                split_bad.append(f"{f}: {len(unbound)} unbound, bbox diff {d:.3f}, parts {len(objs)}/{len(groups[m])}")
    print(f"split files: {len(os.listdir(SPLIT))} re-imported one by one, all meshes bound to their rig, bboxes match the combined file" if not split_bad else "split files BAD")
    fails += split_bad
    # clips: re-import each clip FBX, compare bone world positions against the .blend at a few frames
    meta = json.load(open(os.path.join(ANIM, "clips.json")))
    errs = verify_clips(meta)
    worst = max(errs.values()) if errs else 0
    print(f"clips: {len(errs)} re-imported, worst bone position error vs .blend {worst:.4f} studs")
    for c, e in errs.items():
        if e > 0.02:
            fails.append(f"clip {c}: bone error {e:.3f}")
    if fails:
        print("VERIFY FAILED:\n  " + "\n  ".join(fails))
        sys.exit(1)
    print("verify ok")


def raw_skin_check(path):
    """-> (skinned mesh count, problems): every mesh of a rigged model has one Skin whose only non-empty Cluster
    holds all of its vertices at weight 1.0, on a bone that belongs to the same model's <Model>__Rig"""
    from io_scene_fbx import parse_fbx
    root, _ = parse_fbx.parse(path)
    objs = [e for e in root.elems if e.id == b"Objects"][0]
    node = {}
    for e in objs.elems:
        node[e.props[0]] = e
    parent, children = {}, {}
    for c in [e for e in root.elems if e.id == b"Connections"][0].elems:
        if c.props[0] == b"OO":
            parent.setdefault(c.props[1], []).append(c.props[2])
            children.setdefault(c.props[2], []).append(c.props[1])
    nm = lambda e: e.props[1].split(b"\x00")[0].decode()  # noqa: E731

    def first(e, key):
        for c in e.elems:
            if c.id == key:
                return c.props[0]
        return None
    rigs = {nm(e)[:-5] for e in objs.elems if e.id == b"Model" and nm(e).endswith("__Rig")}
    bad, n = [], 0
    for e in objs.elems:
        if e.id != b"Geometry" or e.props[2] != b"Mesh":
            continue
        model = nm(e).split("__")[0]
        if model not in rigs:
            continue
        n += 1
        nverts = len(first(e, b"Vertices")) // 3
        skins = [node[u] for u in children.get(e.props[0], []) if node.get(u) is not None and node[u].props[2] == b"Skin"]
        if len(skins) != 1:
            bad.append(f"{nm(e)}: {len(skins)} skins")
            continue
        used = []
        for cu in children.get(skins[0].props[0], []):
            cl = node.get(cu)
            if cl is None or cl.props[2] != b"Cluster":
                continue
            idx = first(cl, b"Indexes")
            if idx is not None and len(idx):
                used.append((cl, idx, first(cl, b"Weights")))
        if len(used) != 1:
            bad.append(f"{nm(e)}: weighted to {len(used)} bones")
            continue
        cl, idx, w = used[0]
        if len(set(idx)) != nverts or min(w) < 0.999:
            bad.append(f"{nm(e)}: cluster covers {len(set(idx))}/{nverts} verts, min weight {min(w):.3f}")
        bone = [node[u] for u in children.get(cl.props[0], []) if node.get(u) is not None and node[u].id == b"Model"]
        u = bone[0].props[0] if bone else None
        while u is not None and not nm(node[u]).endswith("__Rig"):
            u = next((p for p in parent.get(u, []) if p in node and node[p].id == b"Model"), None)
        if u is None or nm(node[u]) != model + "__Rig":
            bad.append(f"{nm(e)}: bone not in {model}__Rig")
    return n, bad


def raw_node_rotations(path):
    from io_scene_fbx import parse_fbx  # loaded by the import operator
    root, _ = parse_fbx.parse(path)
    objs = [e for e in root.elems if e.id == b"Objects"][0]
    out = []
    for m in objs.elems:
        if m.id != b"Model":
            continue
        name = m.props[1].split(b"\x00")[0].decode()
        rot = None
        for c in m.elems:
            if c.id == b"Properties70":
                for p in c.elems:
                    if p.props[0] == b"Lcl Rotation":
                        rot = list(p.props[4:])
        out.append((name, m.props[2].decode(), rot))
    return out


def bone_world(arm, frame):
    bpy.context.scene.frame_set(frame)
    bpy.context.view_layer.update()
    return {pb.name: arm.matrix_world @ pb.head for pb in arm.pose.bones}


def verify_clips(meta):
    """the same clip from the .blend and from its exported FBX must put every bone in the same place"""
    bpy.ops.wm.open_mainfile(filepath=BLEND)
    ref = {}
    for clip, m in meta.items():
        arm = bpy.data.objects[m["rig"]]
        arm.animation_data_create()
        arm.animation_data.action = bpy.data.actions[clip]
        if bpy.data.actions[clip].slots:
            arm.animation_data.action_slot = bpy.data.actions[clip].slots[0]
        frames = sorted({0, m["frames"] // 3, m["frames"] // 2, m["frames"]})
        base = arm.matrix_world.translation.copy()
        ref[clip] = {f: {k: v - base for k, v in bone_world(arm, f).items()} for f in frames}
        arm.animation_data.action = None
    errs = {}
    for clip, m in meta.items():
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.fbx(filepath=os.path.join(ANIM, clip + ".fbx"), automatic_bone_orientation=False)
        arm = [o for o in bpy.data.objects if o.type == "ARMATURE"][0]
        # Blender's importer 'connects' a child bone that sits on its parent's axis and then ignores its
        # translation keys (Roblox has no such concept); disconnect so the check measures the file's data
        bpy.context.view_layer.objects.active = arm
        bpy.ops.object.mode_set(mode="EDIT")
        for eb in arm.data.edit_bones:
            eb.use_connect = False
        bpy.ops.object.mode_set(mode="OBJECT")
        sc = bpy.context.scene
        act = arm.animation_data.action if arm.animation_data else None
        start = int(act.frame_range[0]) if act else 0
        base_rest = None
        e = 0.0
        for f, bones in ref[clip].items():
            got = bone_world(arm, start + f)
            if base_rest is None:
                base_rest = arm.matrix_world.translation.copy()
            for k, v in bones.items():
                if k in got:
                    e = max(e, ((got[k] - base_rest) - v).length)
                else:
                    e = max(e, 99)
        errs[clip] = e
    return errs


# ======================================================================= rendering
def studio(w, h, samples=24, bg="D9DCE3"):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.render.film_transparent = False
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    world = bpy.data.worlds.new("Studio")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = BM.srgb(bg) + [1]
    world.node_tree.nodes["Background"].inputs[1].default_value = 0.75
    sc.world = world
    bpy.ops.object.light_add(type="SUN", rotation=(D(42), D(12), D(-28)))
    bpy.context.object.data.energy = 2.0
    bpy.context.object.data.angle = D(10)
    bpy.ops.object.light_add(type="AREA", location=(0, -12, 8))
    l = bpy.context.object
    l.data.energy = 380
    l.data.size = 10
    l.rotation_euler = (Vector((0, 0, 1)) - l.location).to_track_quat("-Z", "Y").to_euler()
    bpy.ops.mesh.primitive_plane_add(size=400, location=(0, 0, 0))
    g = bpy.context.object
    g.name = "Ground"
    gm = bpy.data.materials.new("GroundMat")
    gm.use_nodes = True
    gm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = BM.srgb(bg) + [1]
    gm.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.9
    g.data.materials.append(gm)
    bpy.ops.object.camera_add()
    sc.camera = bpy.context.object
    return sc.camera


def aim(cam, target, yaw, pitch, dist, lens=60, ortho=None):
    t = Vector(target)
    d = Vector((math.sin(yaw) * math.cos(pitch), -math.cos(yaw) * math.cos(pitch), math.sin(pitch)))
    cam.location = t + d * dist
    cam.rotation_euler = (t - cam.location).to_track_quat("-Z", "Y").to_euler()
    if ortho:
        cam.data.type = "ORTHO"
        cam.data.ortho_scale = ortho
    else:
        cam.data.type = "PERSP"
        cam.data.lens = lens


def show_only(groups, names):
    for model, objs in groups.items():
        for o in objs:
            o.hide_render = model not in names


def render_to(path):
    bpy.context.scene.render.filepath = path
    bpy.ops.render.render(write_still=True)


def model_tops(groups):
    """top-level objects of each re-imported model. Blender's FBX importer leaves some skinned meshes unparented
    (see raw_skin_check), so a model can have its armature plus loose meshes as separate tops"""
    out = {}
    for model, objs in groups.items():
        tops = []
        for o in objs:
            while o.parent:
                o = o.parent
            if o not in tops:
                tops.append(o)
        out[model] = tops
    return out


def place_model(groups, tops, model, loc):
    """move a re-imported model so its bottom centre sits at loc"""
    mn, mx = world_bbox(groups[model])
    off = Vector(loc) - Vector(((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, mn.z))
    for top in tops[model]:
        top.location += off
    bpy.context.view_layer.update()


def render_all():
    from PIL import Image, ImageDraw
    os.makedirs(CMP, exist_ok=True)
    import_fbx(FBX_MAIN)
    preview_materials()
    groups = models_in_scene()
    tops = model_tops(groups)
    cam = studio(1800, 1250, 32)
    pets = ["Pet" + n for n, _ in PETS]
    # pets sheet: 6 x 3 grid, front 3/4
    show_only(groups, pets)
    for k, m in enumerate(pets):
        place_model(groups, tops, m, ((k % 6) * 3.6 - 9.0, (k // 6) * 4.2, 0))
    aim(cam, (0, 4.2, 1.2), D(-22), D(16), 44, lens=50)
    render_to(os.path.join(ART, "preview_pets_v2_sheet.png"))
    # eggs
    eggs = ["Egg" + n for n, _, _ in EGGS]
    show_only(groups, eggs)
    for k, m in enumerate(eggs):
        place_model(groups, tops, m, ((k - 2) * 3.4, 0, 0))
    bpy.context.scene.render.resolution_x, bpy.context.scene.render.resolution_y = 1700, 700
    aim(cam, (0, 0, 1.8), D(-18), D(10), 30, lens=55)
    render_to(os.path.join(ART, "preview_eggs_v2.png"))
    # fuser (rigid plot model)
    show_only(groups, ["PetFuser"])
    place_model(groups, tops, "PetFuser", (0, 0, 0))
    bpy.context.scene.render.resolution_x, bpy.context.scene.render.resolution_y = 1000, 1000
    aim(cam, (0, 0, 3.4), D(-30), D(18), 24, lens=50)
    render_to(os.path.join(ART, "preview_fuser_v2.png"))
    # per-pet comparison: sheet left, FBX render (front + side) right
    bpy.context.scene.render.resolution_x, bpy.context.scene.render.resolution_y = 560, 640
    bpy.context.scene.cycles.samples = 24
    for n, _ in PETS:
        m = "Pet" + n
        show_only(groups, [m])
        place_model(groups, tops, m, (0, 0, 0))
        mn, mx = world_bbox(groups[m])
        h = mx.z - mn.z
        shots = []
        for tag, yaw in (("front", 0.0), ("side", D(-90))):
            aim(cam, (0, 0, h * 0.5), yaw, D(4), 30, ortho=max(h, mx.x - mn.x, mx.y - mn.y) * 1.25)
            p = os.path.join(CMP, f"_{n}_{tag}.png")
            render_to(p)
            shots.append(p)
        sheet = Image.open(os.path.join(SHEETS, f"PET-{n}.png")).convert("RGB")
        H = 640
        sheet = sheet.resize((int(sheet.width * H / sheet.height), H))
        out = Image.new("RGB", (sheet.width + 2 * 560 + 20, H + 40), (240, 241, 245))
        out.paste(sheet, (0, 40))
        for i, p in enumerate(shots):
            out.paste(Image.open(p).convert("RGB"), (sheet.width + 20 + i * 560, 40))
            os.remove(p)
        d = ImageDraw.Draw(out)
        d.text((10, 12), f"{n}: Astra sheet (left)  |  SF_Pets_v2.fbx re-imported (front, side facing left)", fill=(30, 30, 40))
        out.save(os.path.join(CMP, f"{n}.png"))
        place_model(groups, tops, m, (0, 60, 0))
    print("rendered")


# ======================================================================= clip preview GIFs (rendered from the .blend actions)
def render_gifs(only=None):
    from PIL import Image
    os.makedirs(PREV, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=BLEND)
    preview_materials()
    meta = json.load(open(os.path.join(ANIM, "clips.json")))
    arms = {o.name: o for o in bpy.data.objects if o.type == "ARMATURE"}
    statics = [o for o in bpy.data.objects if o.type == "EMPTY"]
    cam = studio(256, 256, 10)
    sc = bpy.context.scene
    sc.render.fps = FPS
    for e in statics:
        for c in e.children:
            c.hide_render = True
    for clip, m in sorted(meta.items()):
        model = m["model"]
        short = model[3:] if model.startswith("Pet") else model
        if only and short not in only and model not in only and clip not in only:
            continue
        arm = arms[m["rig"]]
        for a in arms.values():
            for c in a.children:
                c.hide_render = a != arm
        act = bpy.data.actions[clip]
        arm.animation_data_create()
        arm.animation_data.action = act
        if act.slots:
            arm.animation_data.action_slot = act.slots[0]
        rock = None
        if clip.endswith("_Carry"):  # preview only: a meteor riding the Carry bone (the game welds the real one there)
            bm = bmesh.new()
            bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.42)
            rock = mesh_obj("PreviewMeteor", bm, "RockGrey")
            rock.data.materials.clear()
            rock.data.materials.append(BM.material("RockGrey"))
            con = rock.constraints.new("CHILD_OF")
            con.target = arm
            con.subtarget = "Carry"
            con.inverse_matrix = Matrix.Identity(4)
            rock.location = (0, 0, 0)
            rock.matrix_parent_inverse = Matrix.Identity(4)
        # frame the whole clip: union of deformed bboxes over sampled frames
        meshes = list(arm.children) + ([rock] if rock else [])
        mn = Vector((1e9, 1e9, 1e9))
        mx = -mn
        for f in range(0, m["frames"] + 1, 3):
            sc.frame_set(f)
            dg = bpy.context.evaluated_depsgraph_get()
            for o in meshes:
                ev = o.evaluated_get(dg)
                me = ev.to_mesh()
                for v in me.vertices:
                    p = o.matrix_world @ v.co
                    mn = Vector((min(mn.x, p.x), min(mn.y, p.y), min(mn.z, p.z)))
                    mx = Vector((max(mx.x, p.x), max(mx.y, p.y), max(mx.z, p.z)))
                ev.to_mesh_clear()
        c = (mn + mx) / 2
        size = max((mx - mn).x, (mx - mn).y, (mx - mn).z)
        aim(cam, (c.x, c.y, (mn.z + mx.z) / 2), D(-32), D(14), 40, ortho=size * 1.25)
        frames = []
        step = 2 if m["frames"] <= 36 else 3
        for f in range(0, m["frames"] + (0 if m["loop"] else 1), step):
            sc.frame_set(f)
            p = os.path.join(PREV, f"_f{f:03d}.png")
            render_to(p)
            frames.append(Image.open(p).convert("RGB").quantize(colors=96, method=Image.Quantize.MEDIANCUT))
            os.remove(p)
        hold = [] if m["loop"] else [frames[-1]] * int(0.6 * FPS / step)
        out = os.path.join(PREV, f"{clip}.gif")
        frames[0].save(out, save_all=True, append_images=frames[1:] + hold, duration=int(1000 * step / FPS), loop=0, optimize=True)
        arm.animation_data.action = None
        if rock:
            bpy.data.objects.remove(rock, do_unlink=True)
        print("gif", clip, len(frames))


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    only = [a for a in argv if not a.startswith("--")]
    if "--export" in argv or "--stats" in argv:
        t0 = time.time()
        Ms = build_all(only or None)
        rows, bad = stats(Ms)
        print_table(rows)
        if bad:
            print("BUDGET FAILED:\n  " + "\n  ".join(bad))
            sys.exit(1)
        print(f"budgets ok ({time.time() - t0:.1f}s)")
        if "--export" in argv:
            export_all(Ms)
    if "--verify" in argv:
        verify()
    if "--render" in argv:
        render_all()
    if "--gifs" in argv:
        render_gifs(only or None)
