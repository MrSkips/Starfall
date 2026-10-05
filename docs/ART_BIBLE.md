# Art bible: Starfall Forge (rev 1, 2026-10-05)

Status: **approved direction = CON-01 "Sunlit Toy Foundry"** (Zack chose it in the Astra session; see handoffs/T-00-01_RETURN.md).
Primary reference: `art/concepts/CON-01/CON-01-concept-reference.png`. UI reference: `art/concepts/CON-01/UI/*-hud-concept.png`.
Source-video frames REF-01..05 (`art/concepts/CON-01/REF-*.jpg`) are style **evidence only**. They come from another Roblox game, so never copy its ants, mounts, signage, layout, or "Starfall Event" branding.

## Style statement
A bright, cheerful toy-construction world: chunky bevelled blocks, broad flat color fields, red-and-cream "toy machine" forges, and glowing meteors as the only strongly emissive objects. It should read like a clean Roblox screenshot, never a cinematic render.

## Priorities (in order)
1. **The carried meteor and its mutation read instantly**, even at phone size.
2. Machines are readable as four distinct silhouettes from the crater.
3. Routes (ramp and paths) are obvious: orange paths on green and slate.
4. Everything is cheap: mobile-friendly part counts and few particles.

## Palette (CON-01)
| Token | Hex | Use |
|---|---|---|
| grass | #79C94A | terrace tops, rim caps |
| path | #DB9856 | ramps, plot floors, walkways |
| slate | #687B91 | cliffs, crater walls, spires |
| cream | #FFF0CF | machine trim, signage, UI panels |
| machine red | #D95542 | machine shells (forge identity color) |
| sky | #86D6F4 | sky and ambient |
| steel | #344658 | rollers, hammers, anvil, dark trim |
| UI navy | #26384D | UI outlines and text |
| UI orange | #F2A348 | primary UI accent |
| UI teal | #46BFB2 | success accent only |

## Materials
Smooth matte plastic (SmoothPlastic or a simple MaterialVariant). Slate only on cliffs and the crater floor. **No stud textures, no photoreal textures, no high-frequency detail.** Neon only on meteor accents, furnace mouths, the anvil star, and purchase pads.

## Shape and proportion
- Blocky, axis-aligned masses with one large bevel. Terraces step in ~6-stud increments.
- Machines: squat rectangular "toy" bodies about 8–12 studs, a thick cream trim band, and steel working parts.
  - Crusher: paired rollers plus hopper
  - Smelter: furnace mouth plus stubby chimney
  - Forge: gantry plus hammer
  - Star Anvil: wide anvil plus small star
- Avatars are default Roblox. Props may be oversized relative to the avatar (toy scale).

## Mutation visual language (shape *and* motion *and* color, so it's colorblind-safe)
| Mutation | Body | Cue |
|---|---|---|
| Normal | plain gray faceted rock | no aura |
| Molten | dark brown rock | orange glowing cracks plus short flame tongues |
| Frozen | blue-gray rock | large icy-blue crystal spikes |
| Charged | dark rock | yellow **zigzag arcs** (never just yellow cracks, or it reads as Molten) |
| Cosmic | purple body | one thick teal orbit ribbon |
| Starheart | big gold-cream glowing core | star sparkles, 2× meteor size |
Reserve the brightest glow for carried and ground meteors. Scenery never uses neon purple or teal.

## Lighting and atmosphere
Late-morning daylight, blue ambient fill, short soft shadows, light distance haze. No depth of field (remove the default DepthOfFieldEffect in v02). Bloom stays subtle.

## UI rules (from Astra's HUD concepts)
Cream rounded-rect panels, thick navy outline, small offset navy shadow, bold rounded font (FredokaOne for now). Orange is the primary accent. Teal is used only for success.
Layout: Stardust pill top-left (below the Roblox top bar), shower capsule top-center, settings top-right, Forge and Collection buttons left-middle, carry card bottom-center below the avatar, and Drop button bottom-right above the jump button on mobile.
Keep the center of the screen clear. No sales banners, no extra currencies.

## Allowed variation and drift
- Allowed: color variation within ±10% lightness per token; prop scale variation; per-biome palettes later (a new biome swaps grass, path, and sky only).
- **Drift, reject it:** pickaxes or mining tools (players carry meteors by hand), stud textures, glossy or photoreal surfaces, purple or teal scenery that competes with Cosmic, cluttered rubble carpets.

## Technical constraints (provisional, measured in v02)
Meteor mesh ≤ 2k triangles, machine ≤ 6k triangles each, and a fully built plot ≤ 15k. Separate simple collision boxes from decorative meshes. ≤ 2 particle emitters per meteor.

## Reference IDs
REF-01..05 (source video frames, evidence only) · CON-01 (approved) · CON-02, CON-03 (rejected alternatives, keep for reference) · UI-01 desktop HUD, UI-02 mobile HUD (art/concepts/CON-01/UI/)
