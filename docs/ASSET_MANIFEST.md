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
