# T-04-02 RETURN — pets v2, eggs, Pet Fuser (Blender, rigged + animated)

From: Claude (cloud session, no Studio access) · For: Zack / the next Studio session · Date: 2026-10-06

Status: **produced, not integrated.** Everything below exists as Blender files, FBX files and renders in this repo. Nothing has
been imported into Studio, so nothing here is integrated or verified in Roblox yet.

Inputs used: Astra's 18 sheets `art/concepts/PETS/PET-*.png` (+ `PET-Eggs.png`, `PET-LineupScale.png`), the brief text in
`handoffs/T-04-01_PROMPTS.md` (the brief file `handoffs/T-04-01_astra_pet_model_sheets.md` named in the task is not in the repo),
Codex's notes in `handoffs/T-04-01_RETURN.md`, the existing pipeline (`build_pets.py`, `build_models.py`, `build_machines.py`).
`tools/ApplyFuser.luau` (the part-built Pet Fuser) is not in the repo either; the Fuser contract below comes from the brief + D-028.

## What was built

| File | What |
|---|---|
| `tools/blender/build_pets_v2.py` | One re-runnable script (Blender 5.0, headless). `--export` builds, prints the budget table (exits non-zero if any budget is broken), saves the .blend and exports every FBX. `--verify` re-imports everything in a fresh scene and checks it. `--render` makes the previews/comparisons from the re-imported FBX. `--gifs` renders a preview GIF per clip. |
| `tools/blender/build_machines.py` | 23 new MatKeys in `PALETTE` (hex codes from Astra's sheets). Nothing else changed. |
| `art/models/SF_Pets_v2.fbx` + `.blend` | 18 rigged pets `Pet<Name>`, 5 rigged eggs `Egg<Fam>`, `PetFuser` (rigid plot machine), `FuserRig` (the same machine rigged, for the fusion reveal). No animation in this file. |
| `art/models/split/<Model>.fbx` | The same 25 models one per file (same names and positions). Fallback if the 3D Importer has trouble with 24 rigs in one file. |
| `art/models/anims/<Clip>.fbx` | 93 clips, each = that model's armature + one action (the format the Animation Editor's *Import from FBX* takes). `clips.json` lists rig, frames, seconds, loop and markers per clip. |
| `art/models/anims/preview/<Clip>.gif` | One preview GIF per clip (3/4 front camera; Carry clips show a grey stand-in meteor on the Carry bone). |
| `art/models/preview_pets_v2_sheet.png`, `preview_eggs_v2.png`, `preview_fuser_v2.png` | Renders of the re-imported FBX. |
| `art/models/compare/<Name>.png` | Astra's sheet (left) next to the re-imported FBX, front + side (right), one per pet. |
| `tools/ApplyPets.luau` | Updated import contract (see below). No other Luau changed. |

## Budget table (from `build_pets_v2.py --stats`)

Limits: pet ≤ 1,500 tris (Celestia ≤ 2,500), egg ≤ 800, Fuser ≤ 3,000, ≤ 25 parts per pet, ≤ 12 bones. All pass; the script fails the
run if one does not. Sizes are studs (X width × Y depth × Z height, Blender axes). 30 fps.

| Model | Parts | Tris | Size (studs) | Bones | Clips |
|---|---:|---:|---|---:|---|
| PetPebblit | 19 | 850 | 2.29 x 2.36 x 2.29 | 11 | Idle 2.00 s loop, Move 0.60 s loop, Cast 0.70 s, Carry 1.00 s loop, Reveal 1.20 s |
| PetCinderpup | 17 | 832 | 2.31 x 3.07 x 2.93 | 11 | Idle 2.00 s loop, Move 0.60 s loop, Cast 0.70 s, Carry 1.00 s loop, Reveal 1.20 s |
| PetGlintmoth | 15 | 600 | 3.13 x 1.49 x 3.23 | 9 | Idle 2.00 s loop, Move 0.60 s loop, Cast 0.70 s, Reveal 1.20 s |
| PetRubblord | 10 | 834 | 3.56 x 2.02 x 3.04 | 6 | Idle 2.00 s loop, Move 0.60 s loop, Cast 0.70 s, Reveal 1.20 s |
| PetEmberkit | 18 | 594 | 2.12 x 2.68 x 2.61 | 11 | Idle 2.00 s loop, Move 0.60 s loop, Cast 0.70 s, Reveal 1.20 s |
| PetMagmaw | 13 | 632 | 1.97 x 1.92 x 2.33 | 7 | Idle 2.00 s loop, Move 0.60 s loop, Cast 0.70 s, Reveal 1.20 s |
| PetFlarefly | 13 | 624 | 1.80 x 1.66 x 2.97 | 8 | Idle 2.00 s loop, Move 0.60 s loop, Cast 0.70 s, Reveal 1.20 s |
| PetSolarix | 15 | 940 | 2.16 x 2.28 x 3.25 | 9 | Idle 2.00 s loop, Move 0.60 s loop, Cast 0.70 s, Reveal 1.20 s |
| PetFrostling | 18 | 694 | 2.06 x 2.88 x 2.68 | 11 | Idle 2.00 s loop, Move 0.60 s loop, Cast 0.70 s, Reveal 1.20 s |
| PetShardbun | 16 | 624 | 2.19 x 2.06 x 3.04 | 10 | Idle 2.00 s loop, Move 0.60 s loop, Cast 0.70 s, Reveal 1.20 s |
| PetGlacio | 11 | 516 | 2.15 x 1.77 x 2.74 | 6 | Idle 2.00 s loop, Move 0.60 s loop, Cast 0.70 s, Reveal 1.20 s |
| PetAurorabe | 15 | 850 | 2.13 x 1.84 x 3.46 | 7 | Idle 2.00 s loop, Move 0.60 s loop, Cast 0.70 s, Reveal 1.20 s |
| PetNebulynx | 21 | 792 | 1.97 x 2.34 x 3.02 | 10 | Idle 2.00 s loop, Move 0.60 s loop, Cast 0.70 s, Reveal 1.20 s |
| PetVoidling | 10 | 636 | 2.82 x 2.13 x 2.38 | 6 | Idle 2.00 s loop, Move 0.60 s loop, Cast 0.70 s, Carry 1.00 s loop, Reveal 1.20 s |
| PetStarwhale | 10 | 718 | 2.64 x 2.22 x 2.77 | 6 | Idle 2.00 s loop, Move 0.60 s loop, Cast 0.70 s, Reveal 1.20 s |
| PetCelestia | 18 | 798 | 3.08 x 2.53 x 3.35 | 12 | Idle 2.00 s loop, Move 0.60 s loop, Cast 0.70 s, Carry 1.00 s loop, Reveal 1.20 s |
| PetCoreling | 14 | 714 | 1.93 x 2.90 x 2.04 | 9 | Idle 2.00 s loop, Move 0.60 s loop, Cast 0.70 s, Carry 1.00 s loop, Reveal 1.20 s |
| PetMagmacore | 14 | 694 | 2.38 x 2.45 x 2.49 | 7 | Idle 2.00 s loop, Move 0.60 s loop, Cast 0.70 s, Reveal 1.20 s |
| EggRock | 16 | 726 | 2.60 x 2.17 x 3.52 | 8 | Idle 2.00 s loop, Hatch 2.40 s, HatchFast 0.90 s |
| EggEmber | 15 | 670 | 2.25 x 2.17 x 3.60 | 8 | Idle 2.00 s loop, Hatch 2.40 s, HatchFast 0.90 s |
| EggFrost | 14 | 766 | 2.45 x 2.44 x 3.53 | 8 | Idle 2.00 s loop, Hatch 2.40 s, HatchFast 0.90 s |
| EggCosmic | 16 | 780 | 3.03 x 2.94 x 3.06 | 8 | Idle 2.00 s loop, Hatch 2.40 s, HatchFast 0.90 s |
| EggCore | 17 | 710 | 2.65 x 2.17 x 3.81 | 8 | Idle 2.00 s loop, Hatch 2.40 s, HatchFast 0.90 s |
| PetFuser | 20 | 2094 | 7.00 x 7.00 x 7.44 | 0 | — (rigid, code-animated) |
| FuserRig | 20 | 2094 | 7.00 x 7.00 x 7.44 | 10 | Fuse 2.00 s |

## Export axis settings (why the old pets lay on their face)

`axis_forward='Z'`, `axis_up='Y'`, with the axis change **applied to the data before export** (`use_space_transform=False`,
`bake_space_transform=False`; the script rotates every top-level object by Blender (x, y, z) → (−x, z, y) and applies it).

- Blender calls +Y "forward" and our models face −Y, so mapping Blender +Y to FBX +Z puts every face on FBX −Z, which is Roblox's
  LookVector. Blender +Z (up) becomes FBX +Y = Roblox up.
- The old export (`axis_forward='-Z'`, `axis_up='Y'`) did the axis change as a −90° rotation on the root nodes and left the vertex
  data Z-up. If an importer drops or re-applies that root rotation, the model lies down — that is what happened to `SF_Pets.fbx`.
  Now the vertex and bone data is already Y-up and every non-bone node in the file has an identity rotation (checked by `--verify`
  straight from the raw FBX), so there is nothing to apply twice or to lose.
- Blender's own "Apply Transform" (`bake_space_transform`) does the same thing for meshes but is documented as broken for
  armatures, so the script does it by hand.
- Bones are made vertical with roll 180°, so after the axis change every bone's rest orientation is the identity in Roblox
  (bone axes = model axes). The same clip therefore means the same motion on every rig that has the bone.
- Units are unchanged from the old pipeline (`FBX_SCALE_ALL`). `ApplyPets` normalises the import from the PetFuser base, which is
  modelled exactly 7.000 studs wide, and prints the factor.

## Rigs and clips

- Every pet has `Pet<Name>__Rig`, 6–12 bones, rooted at `Root` (bottom centre). Each mesh is weighted 100 % to one bone (rigid toy
  parts; checked from the raw FBX for all 365 skinned meshes). Shared names: `Root`, `Body`, `Head`, `Ear_L/R`, `Tail_1/2`,
  `Leg_FL/FR/BL/BR` (quadrupeds), `Leg_L/R` + `Arm_L/R` (Rubblord, Glacio, Celestia, and the flyers' legs), `Wing_L/R`,
  `Antenna`/`Antenna_L/R`, `Fin_L/R`, `Tent_1..4` (Aurorabe), `Hand_L/R` + `Ring` (Voidling), `Halo` (Solarix), `Star_L/R`
  (Celestia), `Jaw` (Magmaw), `Drill` (Coreling), `Crown` (Aurorabe).
- **`Carry` bone** on the FETCH pets (Pebblit: in the basket, Cinderpup: in the tail scoop, Voidling: between the hands above the
  head, Celestia: above the head, Coreling: above the head). The integration session should weld or move the carried meteor to
  `Rig.Carry.WorldCFrame` while `<Pet>_Carry` plays.
- Clips per pet: `<Pet>_Idle` (2.0 s loop), `<Pet>_Move` (0.6 s loop: hop for walkers, waddle for bipeds, wing flap for flyers,
  bob/swim for floaters), `<Pet>_Cast` (0.7 s: crouch, jump + 360° spin, land, ends at rest), `<Pet>_Carry` (1.0 s loop, FETCH pets
  only), `<Pet>_Reveal` (1.2 s: crouched → pop + twirl → ta-da pose, held). Rotation + translation only: Roblox bones have no scale.
- Eggs: `ShellBottom`, `ShellTop`, `Shard_1..5` (+ matching accent parts) cut from one shell along a zig-zag crack, so the intact
  egg is seamless. Bones `Root`, `Bottom`, `Top`, `Shard_1..5`. Clips `Egg<Fam>_Idle` (2.0 s loop), `Egg<Fam>_Hatch` (2.4 s),
  `Egg<Fam>_HatchFast` (0.9 s). Rock tips over in chunks, Ember bursts upward, Frost shatters far and spins, Cosmic's shards carry
  the ring pieces round in an orbit before flying out, Core launches its drill top high.
- `Fuser_Fuse` (2.0 s) on `FuserRig`: orbs spin up, lift and pull in, the chamber shakes, the core pulses and jumps, the tips jab in.
- **Markers** (Blender pose markers on the actions; FBX cannot carry them, so add them as Animation Events in Studio):
  | Clip | `PetOut` frame (30 fps) | Other |
  |---|---|---|
  | `Egg<Fam>_Hatch` | **51** (1.70 s) | `Crack` 48 |
  | `Egg<Fam>_HatchFast` | **17** (0.57 s) | `Crack` 15 |
  | `Fuser_Fuse` | **44** (1.47 s) | `Flash` 40 |
- Skipped: blinking. Roblox bone animation cannot scale, so a blink would need eyelid parts on another bone; not worth the parts
  budget. The chamber "flash" is motion only in the clip; the light itself (a Highlight, PointLight or neon colour pulse) belongs in
  code at the `Flash` marker.

## Where I deviated from Astra's sheets, and why

All pets (shared choices):
- **Faceted toy look**: bodies are faceted low-poly shells (decimated icospheres, flat shaded) to match the sheets' broad facets.
  Eyes are smooth glossy domes with one white glint (`EyeBlack` / `EyeShine`).
- **No mouth lines.** The sheets draw thin black smiles; those are thinner than the 0.15-stud rule and vanish on phones. Most pets
  keep the small dark nose.
- **Sparkle points** (Solarix, Starwhale, Magmacore, Aurorabe's crown) are left to runtime effects as Codex suggested, except
  where they are a big readable shape (Celestia's two star shards, Solarix's halo spikes, Aurorabe's crown gem).
- Glow colours are Neon only where the sheet shows a glow; matte crystals use SmoothPlastic in the accent colour.

| Pet | Deviation | Why |
|---|---|---|
| Pebblit | Crystal bits reduced to 2 cheek crystals + the basket cluster; spots only on head, body and front paws | Common silhouette, part budget (Codex note) |
| Cinderpup | Lava cracks simplified to ~10 short glowing streaks; scoop keeps glowing embers (sheet) | Readable at phone size |
| Glintmoth | One thick faceted wing per side (big upper kite + small lower kite) with glowing inlays through both faces | Codex note; no thin wings |
| Rubblord | Spikes reduced to 7 on head/back + 4 per arm; shoulder and fist boulders are separate rigid pieces on the arm bone | Budget, animation |
| Emberkit | As sheet (cheek gems kept) | — |
| Magmaw | Crest kept as 1 big + 2 small crystals (Codex suggested removing it, but every sheet view shows it); back seams reduced to 4 glow patches; jaw is a separate part on a `Jaw` bone | Sheet is the source of truth; budget |
| Flarefly | Antenna stem thickened to 0.17 studs and hooked to the front-right | No thin parts |
| Solarix | Mane = 7 thick plates + 2 cheek wedges; halo tube 0.18 studs thick; walks on 4 legs (Hover 0) | Phone readability (Codex), sheet shows a standing cub |
| Frostling | Tail crystal segments touch instead of floating apart; forehead + chest gems kept small, glowing | Codex note (no gaps) |
| Shardbun | As sheet | — |
| Glacio | Ice core is opaque Neon; crest = 1 large + 2 small crystals | Codex note (opaque ice) |
| Aurorabe | Exactly 4 thick tentacles (the sheet varies between views) with the pink stripe as a neon strip on the front face; all opaque | Codex note; cube footprint |
| Nebulynx | 4 matte violet body stars (sheet has more, smaller ones); chest gem kept | Codex note (sparse, matte) |
| Voidling | Kept the 2 top crystals (all four views show them); dropped the chest diamond (the orbit ring passes over it) | Sheet vs Codex note; clutter |
| Starwhale | Lighter navy belly (`WhaleBelly2` #4C64B8 sampled from the sheet, not a listed swatch); 5 big gold stars, tiny speckles dropped | Phone readability |
| Celestia | No wings and no halo (the old model had both; the sheet has neither); walks on 2 legs (Hover 0) | Sheet |
| Coreling | Drill = 3 stepped cones with 2 glowing bands; armour seams as glowing strips | Codex note (no fine threads) |
| Magmacore | Hammer horn = one fixed stem + head (Codex's correction); crown of 5 crystals | Codex note |

Eggs: shells are faceted tiles in staggered rows (Rock: grey plates with dark grooves; Ember and Core: dark plates whose gaps show the
glowing shell underneath). Cosmic's orbit ring is lavender like the sheet (the old egg's ring was teal) and is split into 5 arcs that
fly off with the shards. Frost has 12 ice crystals plus a crown, Rock a lavender crystal cluster on the top and the side, Ember a flame
crest, and Core a stepped drill crest plus 2 side fins.

Pet Fuser (no sheet): toy machine per the art bible. 7 × 7 steel base, cream trim, three red pillars with cream caps (back,
front-left, front-right), red plinths with yellow rims, a glass `Chamber`, gold neon `Core`, teal neon `Orb1-3` orbiting at
radius 2.15, teal `Tip1-3` crystals on the pillars pointing at the chamber, a steel dome with a teal beacon, and a front console with
three yellow buttons. 7.44 studs tall.

## Studio steps for the next session

**1. Models**
1. Open the place, then *File → Import 3D* → `art/models/SF_Pets_v2.fbx`. Keep the defaults and import it into the Workspace.
   If the importer shows a scale-unit option, use the one that makes the PetFuser base 7 studs wide. `ApplyPets` prints the factor
   and warns when it is not 1.000.
   - If the combined file imports badly (a pet with no Bones, bones on the wrong pet, parts flying off when previewing), delete it
     and import all files in `art/models/split/` instead (multi-select in the Import 3D dialog). Names and positions are identical.
2. Command bar: `require(game.ServerStorage.Tools.ApplyPets)()`. It
   - fills `ReplicatedStorage.Assets.PetMeshes` (18 pets incl. **Coreling** and **Magmacore**, which used procedural models until
     now), `EggMeshes` (adds **CoreEgg**), `ReplicatedStorage.Assets.FuserRig`, and `ServerStorage.Art.Machines.PetFuser`;
   - re-parents each rig's bones under the template's PrimaryPart and adds `AnimationController` + `Animator`;
   - replaces `Visual` under every plot's `Items.PetFuser` (placed or still in `ServerStorage.PlotItems`): same position, plot-facing
     like the other machines, `FusePrompt` moved onto `Base`, the `Collider` and any lights/emitters/attachments on same-named old
     parts carried over, attributes copied, `ItemId = PetFuser`, `Machine = PetFuser`, hidden if the old one was hidden;
   - only replaces templates that are in the import (the old version emptied the whole PetMeshes/EggMeshes/Gadgets folders, which
     would now have deleted the Forge Drone and Launch Pad).
   It still accepts the old `SF_Pets.fbx`.
3. Command bar: `require(game.ServerStorage.Tools.OptimizeParts)()`.
4. Playtest: hatch each egg, equip pets (PetFollow), open the Pets panel, buy/use the Pet Fuser (check the orbit animation still runs
   on Orb1-3 / Core / Tips, and the FusePrompt), Core Breach with Coreling/Magmacore. Save the place.

**2. Animations**
1. Drag a template (e.g. `PetMeshes.Pebblit`) into the Workspace and select it in the Animation Editor (it has an
   `AnimationController`, so the editor accepts it as a rig).
2. *⋯ → Import → From FBX Animation* → `art/models/anims/Pebblit_Idle.fbx`. Set looping for the clips marked loop in `clips.json`
   (Idle, Move, Carry, Egg Idle); add the `PetOut` / `Crack` / `Flash` events at the frames above.
3. *Publish to Roblox* and note the AnimationId. Repeat for each clip on its own rig (eggs on `EggMeshes.<Fam>Egg`, `Fuser_Fuse` on
   `Assets.FuserRig`). 93 clips in all.
4. Collect the ids in a new `Config.PetAnims` table, e.g.
   `PetAnims = { Pebblit = { Idle = "rbxassetid://…", Move = …, Cast = …, Carry = …, Reveal = … }, RockEgg = { Idle = …, Hatch = …, HatchFast = … }, Fuser = { Fuse = … } }`.
5. Integration (not done here; no scripts were changed): PetFollow swaps its code-driven hop and perk spin for
   `Animator:LoadAnimation` (Move while following, Idle when still, Cast on perk fire, Carry while fetching with the meteor on the
   `Carry` bone); the hatch reveal plays `Hatch`/`HatchFast` (Triple Hatch) and shows the pet on `PetOut`, then plays its `Reveal`;
   the fusion reveal plays `Fuser_Fuse` on a clone of `Assets.FuserRig`. Animated rigs in a ViewportFrame need a `WorldModel`.

## Verification done here (Blender only)

- Budget table above; the script exits with an error if any limit is broken.
- `--verify` re-imports `SF_Pets_v2.fbx` into an empty scene: every model's bounding box, bottom at z = 0, eyes on the −Y face and in
  the upper half (pets), ShellTop above ShellBottom (eggs), PetFuser base 7.000 wide. Raw FBX check: no non-bone node has a
  rotation; every one of the 365 skinned meshes has one skin cluster holding all its vertices at weight 1.0 on a bone of its own rig.
  Each `split/*.fbx` re-imports bound, with the same bounding box. All 93 clip FBX files re-import with 0.0000-stud bone error
  against the .blend at four sampled frames.
- Every clip GIF was reviewed frame by frame (contact sheets) for parts drifting off, interpenetration and loop seams.
- `tools/ApplyPets.luau` compiles with the Luau compiler (`luau-compile`). It has **not** run in Studio.
- Blender's FBX importer drops some skin bindings when one file holds 24 rigs (it re-parents meshes while looping over them). The
  file data is correct (see the raw check). This is why the `split/` files exist.

## Not verified / open questions

- How the Roblox 3D Importer handles 24 rigs with the same bone names in one FBX (use `split/` if it struggles), and where it parents
  the Bones (ApplyPets finds each rig's `Root` bone by position, so the hierarchy doesn't matter).
- Bone animation on anchored templates and on `Model:ScaleTo` (ApplyPets scales after re-parenting the bones). Roblox documents both
  as supported; untested here.
- The old `ApplyFuser` Visual structure (prompt location, collider, extra children) is inferred. ApplyPets carries over what it finds
  and prints how many plot fusers it replaced.
- Hover heights: Solarix and Celestia now stand on legs in Astra's sheets, so `ApplyPets` sets their `Hover` to 0 (was 1.2 / 0.8).
