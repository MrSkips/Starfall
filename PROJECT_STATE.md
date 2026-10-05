# PROJECT_STATE — Starfall Forge (working title)

Last updated: 2026-10-05 by Claude (integration owner, v00)
Master prompt revision: MP-r1 (Zack's "Claude Master Prompt — Research and Build an AI-Made Roblox Game with ChatGPT")

## Current version
v00 — Research and direction. Status: **deliverables complete, waiting on Zack's concept approval + art references.**

## Baseline
- Repo: this folder (`Alpha Roblox Game`). Git initialized 2026-10-05. Baseline = first commit "v00 docs".
- Studio: one open place, "Place1", **unsaved and unpublished** (PlaceId 0). It's an empty baseplate. No game content yet.

## Approved decisions (from Zack, 2026-10-05)
- Genre: tycoon, with a distinctive twist (research picks the twist).
- Devices: PC and mobile equally.
- Budget: $0 now. Ads are possible later if the game earns revenue.
- Partner AI: ChatGPT. Zack will provide art-style references.

## Provisional (needs Zack's approval)
- Concept: **Starfall Forge**: shared meteor rush plus forge tycoon. Fallback: Classic Forge Tycoon (same theme, single-player dropper). See docs/GAME_DESIGN.md §1.
- Art direction: wait for references (docs/ART_BIBLE.md is a placeholder).

## Completed (v00)
- Capability audit (README.md §Capabilities)
- Research brief (docs/RESEARCH.md)
- Concept matrix, recommendation, and design doc (docs/GAME_DESIGN.md)
- Architecture, interface contracts, and asset pipeline (docs/TECHNICAL_ARCHITECTURE.md)
- Test and metrics plan (docs/TEST_PLAN.md)
- Roadmap (docs/ROADMAP.md)
- v01 master prompt (versions/v01/MASTER_PROMPT.md)
- First ChatGPT handoff (handoffs/T-00-01_chatgpt_art_exploration.md)

## Active owners
- v00 and v01 integration owner: Claude
- Art exploration T-00-01: ChatGPT (waiting on Zack to relay it with the reference images)

## Blockers / decisions needed from Zack
1. Approve Starfall Forge, choose the fallback, or reject both.
2. Attach the art references to the ChatGPT handoff T-00-01.
3. Save the Studio place: File > Save to File As > `Alpha Roblox Game/place/StarfallForge.rbxl`. Before v03 you also need to publish it privately so DataStores work.

## Latest verified build
None.

## Next action
Zack approves the concept. Claude then runs versions/v01/MASTER_PROMPT.md: greybox core loop, built directly in Studio through MCP.

## Resume packet (paste into a new session)
> Project Starfall Forge. Read PROJECT_STATE.md, docs/DECISIONS.md, and the active versions/vNN/MASTER_PROMPT.md in the "Alpha Roblox Game" folder before acting. Claude is the integration owner. ChatGPT handles art and review through manual relay (Mode B). Studio MCP is available to Claude only.
