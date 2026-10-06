# T-04-01 RETURN — pet model reference sheets

From: Codex · For: Claude / Zack · Date: 2026-10-06

Status: **produced**. Zack requested Codex to execute the Astra brief in this chat. Created 18 individual pet sheets and the three optional sheets using the built-in imagegen tool. These are concept references for Blender reconstruction; no meshes or Studio integration were produced.

## Deliverables and inspection

All files are in `art/concepts/PETS/`. The 18 individual sheets were visually inspected in the generation output: four labeled views (front, 3/4 front, left-facing side, back), three labeled swatches, full silhouettes, and broad faceted forms. Exact names, rarities and requested body/accent hex values are retained in the prompt set.

**Resolution exception:** all individual sheets, TierExamples and Eggs are **1672 × 941**. The built-in generator returned this native size despite requests for at least 2048 px wide, including the targeted Magmacore correction. The brief's minimum resolution is not met for these 20 files. They have not been artificially upscaled. LineupScale is **2172 × 724**.

Rendered materials include studio shading and glow, so the hex codes in the brief are the source of truth for Blender materials, not sampled pixel colors. Soft contact shadows remain in the sheets. The four views are conceptual, not mechanically exact orthographic drawings; reconcile minor changes as noted below. Triangle counts and phone readability require mesh/Studio testing. All accents should use the prescribed color only; baked yellow/white highlights are lighting, not extra emissive colors.

## Per-pet notes

| File | Body / accent | Changes or uncertainties for rebuild |
|---|---|---|
| `PET-Pebblit.png` | #8C8597 / #5E5868 | Added crystals in basket; treat them as optional cargo and simplify surface pebble spots. Keep the Common silhouette simple. |
| `PET-Cinderpup.png` | #4A3B44 / #FF7A2A | Scoop tail and ember ears read clearly; simplify crack geometry and empty the scoop for a neutral model. |
| `PET-Glintmoth.png` | #3E4A66 / #FFE14A | Wings render as two paired lobes per side; merge each side into one thick wing piece. Added chest glow is optional; antenna tips define BEACON. |
| `PET-Rubblord.png` | #6E6585 / #C9B6A6 | Strong shoulders read clearly; reduce cream spikes to a few large back spikes and keep cream stone matte. |
| `PET-Emberkit.png` | #5A2E2A / #FF5A1E | Furnace window reads clearly; remove optional cheek gems for the simplest Common silhouette. Flame tail must remain thick. |
| `PET-Magmaw.png` | #3B3540 / #FFB13D | Wide molten mouth and solid drips read clearly; generator added a crystal crest and many seams. Remove crest and reduce seams to preserve Uncommon simplicity. |
| `PET-Flarefly.png` | #FF8A2B / #FFE14A | Beacon bulb and lantern abdomen read clearly; thicken antenna stem and keep wings solid. |
| `PET-Solarix.png` | #FFB13D / #FFE21B | Sun halo reads clearly; make halo thick enough for phones, reduce mane to a small set of shared wedges. Use runtime sparkle effects. |
| `PET-Frostling.png` | #9FC9E0 / #BDEBFF | Three-segment tail is shown with gaps; connect segments with thick joints. Remove extra forehead/chest gems and simplify Common silhouette. |
| `PET-Shardbun.png` | #DDEFFF / #19F0F5 | Crystal ears and swept cheek fins read clearly; keep ears solid and limit optional belly gem. |
| `PET-Glacio.png` | #6FA8D8 / #BDEBFF | Belly core reads clearly; keep crest to one large crystal plus two small wedges. Render ice opaque. |
| `PET-Aurorabe.png` | #64DFD1 / #FF4FD8 | Cloud crown reads clearly; tentacle count varies across views. Rebuild exactly four thick opaque tentacles and size total footprint into a cube. |
| `PET-Nebulynx.png` | #3A2A5E / #B07CFF | Violet antenna ears read clearly; reduce scattered stars and remove optional chest core to keep Uncommon identity. Sparse star markings can be matte. |
| `PET-Voidling.png` | #1F1A33 / #19F0F5 | Orbit ring and hand orbs read clearly; generator added head crystals and belly gem. Omit those extras; place exactly two hand orbs symmetrically. |
| `PET-Starwhale.png` | #2C3E8C / #FFE21B | Tail ring and chunky fins read clearly; raised tail counts toward cube bounds. Sparse star markings should use exact accent; optional emissive. |
| `PET-Celestia.png` | #FFD9F2 / #FF4FD8 | Two orbiting stars and strong arms read clearly; ensure exactly one eye highlight per eye. Reduce spine gems as needed to meet triangle budget. |
| `PET-Coreling.png` | #3B3540 / #FF3B1F | Drill nose and claws read clearly; use broad conical drill steps instead of fine threads. Simplify seams. |
| `PET-Magmacore.png` | #241E2C / #FF6A1E | Corrected pointed rhino horn into a broad bevelled hammer head. Side view slightly tilts the hammer; rebuild it as one fixed stem/head assembly. Keep heavy armor and visible core. |

## Optional sheets

- `PET-TierExamples.png`: Normal / Gold / Diamond with same base Pebblit geometry, recolored crystal trim, foot aura rings and more Diamond sparkle points. Gold ring is shown slightly larger than Diamond; use game code for the intended larger Diamond aura. Sparkles/aura belong in effects, not the mesh.
- `PET-Eggs.png`: Rock, Ember, Frost, Cosmic, Core from left to right, front row above and 3/4 row below. Generator omitted requested family/view labels. Families are identified by order; simplify repeated crystal ornamentation.
- `PET-LineupScale.png`: all 18 pets in brief order beside an avatar silhouette. **Rough guide only:** Rubblord/Magmacore are oversized relative to knee-to-hip target; some names have spelling errors, and some creatures differ from individual sheets. Use individual sheets for design, and set mesh heights to about 0.30–0.45 avatar height (measure knee-to-hip against the actual game avatar). Do not trace lineup labels or use lineup geometry as authoritative.

## Prompt record and integration

`handoffs/T-04-01_PROMPTS.md` preserves the global prompt, per-pet briefs, optional prompts and the Magmacore correction. Built-in tool used; no API/CLI fallback.

Claude's next step: rebuild from the individual sheets with 10–25 simple pieces, approximately 1,500 triangles per pet, bottom-centre pivot and face toward -Z. Prioritize perk silhouette; remove optional detail where noted. Import and apply through Claude's existing pipeline, then test scale, opaque materials and mobile readability. Recheck these files before marking integration or Studio verification.
