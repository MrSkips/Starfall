# Starfall Forge (working title): AI-made Roblox tycoon

This is a Roblox tycoon built by Claude and ChatGPT. Zack owns the project and makes the creative calls. Every custom asset and every line of code is AI-made.

Start here: **PROJECT_STATE.md**, then the active `versions/vNN/MASTER_PROMPT.md`.

## Layout
| Path | Purpose |
|---|---|
| PROJECT_STATE.md | Current version, owners, blockers, next action, resume packet |
| docs/RESEARCH.md | Dated research with sources |
| docs/GAME_DESIGN.md | Concept matrix, recommendation, design doc, MVP boundary |
| docs/ART_BIBLE.md | Visual rules (fills in once references arrive) |
| docs/TECHNICAL_ARCHITECTURE.md | Code structure, interface contracts, asset pipeline, perf budgets |
| docs/DECISIONS.md | Decision log |
| docs/ASSET_MANIFEST.md | Every asset, its source, and its status |
| docs/TEST_PLAN.md | Tests plus analytics and metrics plan |
| docs/ROADMAP.md | Version gates, effort, costs, risks, and responsibility table |
| docs/CHANGELOG.md | What changed in each version |
| versions/vNN/ | Master prompt, tasks, and acceptance criteria for each version |
| handoffs/ | Handoffs between Claude and ChatGPT and the returns |
| src/ | Luau source of truth (from v01 on) |
| tools/ | Generation and sync scripts |
| art/ | Reference images (refs/) and concept mockups (concepts/) |

## Capability audit (verified 2026-10-05)
| Capability | Claude | ChatGPT | Notes |
|---|---|---|---|
| Web research and official docs | **Verified** | Unverified (likely) | Claude fetched Roblox Creator Hub pages |
| Shared project folder | **Verified** (read/write here) | **Unverified** | ChatGPT gets files only when Zack attaches them |
| Roblox Studio MCP: inspect, run Luau, edit scripts, playtest, screenshot | **Verified** (1 Studio, "Place1", Edit mode) | Unverified | Only Claude has a confirmed Studio connection |
| Studio AI generation: mesh, material, texture, procedural model | Available, **not yet tested** | n/a | Studio MCP tools (Roblox Cube) |
| Figma MCP | Connected. Account is on a student team with a **View** seat, so write access is **unverified** | Unverified | Test by creating a draft file in v02 |
| Image generation | Figma generate_image exists but uses Figma AI credits (unverified quota) | **Expected (ChatGPT image gen)**, relayed by hand | ChatGPT is the main mockup source |
| Blender scripting | Unavailable on your computer's shell. The cloud workspace may be able to install it (unverified) | Unverified | Not needed through v02 |
| Audio and music generation | Unavailable | Unverified | Use Roblox's licensed audio library or procedural SFX. Track rights |
| Asset upload and publishing | Studio uses your logged-in account. Claude can't publish | n/a | Publishing, purchases, and ID checks are **Zack-only** |
| Profiling | MicroProfiler and SceneAnalysis skills are available in Studio MCP (untested) | n/a | |
| Git on your computer | **Verified** (git, python3, node). No Rojo | n/a | Repo is the source of truth. Claude syncs to Studio through MCP |
| Assistant-to-assistant messaging | **Unavailable** | **Unavailable** | Mode B: Zack relays the handoff blocks |
