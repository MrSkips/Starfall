# PROJECT_STATE: Starfall Forge (working title)

Last updated: 2026-10-05 by Claude (integration owner)
Master prompt revision: MP-r1 · Active version prompt: versions/v01/MASTER_PROMPT.md (v01-r1)

## Current version
**v02 visual slice: mostly done.** Blender map + models, Astra UI-02 in game, sound + VFX, all verified solo in Studio. **The live task board is HANDOFF.md** (owners, queues, open requests, decisions waiting on Zack).

## Next action
Claude: Step 3, starting with saving progress (DataStore). Then T-03-01 monetization integration once ChatGPT's RETURN arrives.
Zack: save `place/StarfallForge.rbxlx`, publish, send T-03-01 to ChatGPT, and decide the HANDOFF.md §6 items.

## Resume packet
> Project Starfall Forge. Read PROJECT_STATE.md, docs/DECISIONS.md, docs/ART_BIBLE.md, and versions/v01/* in the "Alpha Roblox Game" folder. Claude is the integration owner and the only one with Studio MCP access. Studio is the live code surface. src/ is exported from place/StarfallForge.rbxlx with tools/export_scripts.py. Automated server tests use the Studio-only hook ServerStorage.DebugCall (Invoke(service, fn, ...)).
