# Asset manifest
Status values: planned · concept only · generated · imported · verified · rejected. Roblox asset IDs are recorded only once the platform returns them.

| Asset ID | Family | Description | Pipeline / source | Prompt / script | Seed | Owner | Status | Destination |
|---|---|---|---|---|---|---|---|---|
| A-MAP-001 | Map | Greybox crater plus 8 plots | ServerStorage.Tools.BuildGreybox | script | 1 | Claude | **imported (greybox)** | Workspace/Map |
| A-MET-001 | Meteor | Meteor chunk (greybox: ball Part plus light/particles per mutation) | procedural, MeteorService.makeChunk | code | n/a | Claude | **imported (greybox)** | runtime |
| A-MCH-001..006 | Machine | Crusher, Conveyor, Smelter, Bellows, Forge, Star Anvil, Boots stand (greybox blocks) | BuildGreybox | script | n/a | Claude | **imported (greybox)** | Plot.Items / ServerStorage.PlotItems |
| CON-01 | Concept | Sunlit Toy Foundry gameplay mockup | Astra image_gen | art/concepts/CON-01/PROMPT.md | n/a | Astra | **concept only (APPROVED)** | art/concepts/CON-01 |
| CON-02, CON-03 | Concept | Orbital Workshop, Prism Starworks | Astra image_gen | PROMPT.md each | n/a | Astra | rejected (kept for reference) | art/concepts/ |
| UI-01, UI-02 | Concept | Desktop and mobile HUD mockups | Astra image_gen | art/concepts/CON-01/UI/NOTES-AND-PROMPTS.md | n/a | Astra | concept only | art/concepts/CON-01/UI |
| ART-MESH-01..12 | Mesh | Crusher, Smelter, Forge, StarAnvil, MeteorRock, Tree, Meteorite (landmark), Boulders, Fence, Lamp, Crates, Bush | Roblox Studio generate_mesh (Cube) | prompts in session log (CON-01 palette) | n/a | Claude | **generated (not placed)** | ServerStorage.Art |
| UI-FIGMA-01 | UI | Figma design system and screens | Figma MCP use_figma | docs/UI.md | n/a | Claude | **generated** | figma.com/design/epTn2brL2LP9N8DjjV7YNk |
| UI-ICON-01..21 | Icon | 21 UI icons (star, gear, book, forge ×3, lock, chevron, arrow, mut_* ×5, meteor_* ×6) | Astra Figma SVG → cairosvg PNG 256px | art/ui-icons/svg | n/a | Astra (design), Claude (export) | **imported (rbxassetid in UI.Icons)** | StarterPlayerScripts.UI.Icons |

## Blender models (2026-10-05): produced, not yet imported/verified in Studio
| File | Contents | Source script | Studio tool |
|---|---|---|---|
| art/models/SF_Models.fbx | Crusher, Smelter, Forge, StarAnvil, Conveyor, Bellows, CarryBoots1, Pad, Sign, 5 mutation meteors, Starheart | tools/blender/build_models.py | ServerStorage.Tools.ApplyModels |
| art/models/SF_Map.fbx | Crater floor + meteorite, cliffs, 8 ramps, plot pads, fences, path ring, lamps, trees, outer mesas (visual only) | tools/blender/build_map.py | ServerStorage.Tools.ApplyMap |
| art/models/SF_Machines.fbx | Superseded by SF_Models.fbx (machines only) | tools/blender/build_machines.py | (ApplyMachineModels now forwards to ApplyModels) |
Runtime hooks: MeteorService welds Art.Meteors[mutation] onto the hitbox ball; PurchaseService toggles pad Visual; MachineAnimator animates Conveyor rollers, Bellows pump, Boots bob/spin.

## Audio (2026-10-05): integrated + verified loading in Studio playtest (StarterPlayerScripts.FX)
Free Creator Store audio; licensed-library uploads (ProSoundEffects, APMOfficial, DistrokidOfficial) preferred. Not yet heard by Zack — swap any that sound wrong.
| Key | Asset ID | Source / creator | Used for |
|---|---|---|---|
| Impact | 92921472425972 | "Rock Slam Crater SFX" / GleonoffG | meteor landing |
| Whoosh | 9114428742 | "Fireball Burning Whoosh By 1" / ProSoundEffects | meteor falling |
| Pickup | 120136323399242 | "Rock Hit" / Canned_Beans9669 | pickup |
| Deposit | 115881287161374 | "Rock Impact" / GleonoffG | meteor into crusher |
| Coins | 73185454281235 | "Collect coins" / Nu World | payout |
| Build | 9048749902 | "Daily Affirmation - Mnemonic1" / APMOfficial | upgrade built |
| Alarm | 9125709757 | "Neutral Zone Alarm…" / ProSoundEffects | meteor shower start (first 3 s) |
| Click | 74354585591493 | "Default Button Sound - 1" / Val_DaMage | UI buttons |
| Hammer | 106200935745005 | "Hammer Hit 2" / Lixue_Cromwell | forge slam |
| Music 1 | 100333487341753 | "Retro Radiance" / DistrokidOfficial (63 s) | background playlist |
| Music 2 | 132921711367845 | "Ahead" / DistrokidOfficial (71 s) | background playlist |
