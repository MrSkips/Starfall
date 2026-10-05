# PROJECT_STATE: Starfall Forge (working title)

Last updated: 2026-10-05 by Claude (integration owner, v01)
Master prompt revision: MP-r1 · Active version prompt: versions/v01/MASTER_PROMPT.md (v01-r1)

## Current version
**v01: Core-loop greybox.** Status: **built and server-verified. Waiting on Zack's multiplayer playtest and saving the place.**

## Baseline
- Repo: `Alpha Roblox Game` (git). The v01 commit follows "v00 docs".
- Studio: "Place1" holds the full v01 build. **It is NOT saved to disk yet.** Zack: File > Save to File As > `place/StarfallForge.rbxlx` (use the **.rbxlx** format), then run `python3 tools/export_scripts.py` (or ask Claude) to copy the scripts into src/.

## Approved decisions
Tycoon with a twist · PC and mobile equal · $0 budget · Starfall Forge concept (D-005) · Art direction CON-01 Sunlit Toy Foundry (D-010) · Astra on art, ChatGPT available · Claude builds the Figma UI later (D-011).

## Completed in v01 (evidence in versions/v01/TASKS.md)
Greybox map (seeded generator) · plots and spawn · meteor schedule, warning, fall, and mutations · carry, drop, and deposit · processing queue · 6 purchase pads with requirement order · showers plus Starheart co-op carry · HUD (Stardust, shower timer, carry card, guide beam, payout pop, toasts) · [Metrics] logging · DropOnPlot A/B toggle.

## Not verified yet
2-player behavior (Starheart co-op payout, contested pickup with two real players) · real touch/mobile input · Studio's 3D viewport didn't render during Claude's session (screenshots were black), so there's no visual check of the greybox yet.

## Blockers / needs Zack
1. Save the place as `place/StarfallForge.rbxlx` (otherwise the v01 work exists only in the open Studio window).
2. Run the playtest in versions/v01/PLAYTEST.md and send the answers.
3. If Studio's 3D view is black for you too, tell Claude (a graphics setting issue).

## Next action
Zack: save, then playtest. Claude: read the results, tune Config, then write the v02 master prompt (visual vertical slice: CON-01 meshes, real HUD from Figma, sound, perf numbers).

## Resume packet
> Project Starfall Forge. Read PROJECT_STATE.md, docs/DECISIONS.md, docs/ART_BIBLE.md, and versions/v01/* in the "Alpha Roblox Game" folder. Claude is the integration owner and the only one with Studio MCP access. Studio is the live code surface. src/ is exported from place/StarfallForge.rbxlx with tools/export_scripts.py. Automated server tests use the Studio-only hook ServerStorage.DebugCall (Invoke(service, fn, ...)).
