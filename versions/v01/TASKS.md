# v01 tasks (owner: Claude unless noted). Evidence from Studio MCP sessions on 2026-10-05.
| ID | Task | Status | Evidence |
|---|---|---|---|
| T1 | ServerStorage.Tools.BuildGreybox: crater, 40-segment rim, 8 plots, ramps, 3 landmark spires, plot items, pads | **done** | Built 8 plots. Raycast check: ramp rises 0.9 → 6.0 → 11.1 studs across r=108/125/142, plot surface at y=14. Navigation from crater (r=60) up the ramp to the Crusher succeeded |
| T2 | Config, PlotService, EconomyService | **done** | Player assigned Plot1 and spawned on it (y=17) |
| T3 | MeteorService plus CarryService | **done** | Onboarding meteor landed near the ramp ~6 s after join. **Real E-key pickup worked** (speed 16→11, jump 0). Far pickup rejected, double pickup rejected, deposit at another plot rejected, deposit from far rejected, deposit at own Crusher accepted, +15 Stardust after processing |
| T4 | MachineService plus PurchaseService (6 pads) | **done** | Too-poor purchase rejected. Star Anvil before Forge rejected. All 6 bought, total spent 2140 (matches Config). Value ×4.5, process 1.33 s, carry speed 13. Items appear in the world, pads hide |
| T5 | Shower plus Starheart co-op | **done (solo-verified)** | Shower spawned 20 meteors including 1 Starheart and toggled ShowerActive. Solo Starheart: lifted (speed 9), didn't move with 1 carrier, solo deposit rejected, walking away released it to the ground. **2-player carry and payout NOT verified** |
| T6 | Client HUD, guide beam, Drop (Q/B/touch), payout pop, toasts | **done** | HUD visible in a play-mode screenshot (Stardust pill, shower timer, carry card) |
| T7 | Tests, measurements, docs, commit, playtest script | **done** | No errors in Output. Estimated round trip ~19 s (path ~120 studs at 16 out / 11 back). Measured join → first deposit = 19 s (scripted, so a real player will be slower). versions/v01/PLAYTEST.md written |
| Z1 | (Zack) Save place as place/StarfallForge.rbxlx | **waiting** | |
| Z2 | (Zack) 2–3 player playtest plus answers | **waiting** | |

Known issue: Studio's 3D viewport rendered black in every MCP screenshot (HUD only). Proximity prompts stopped appearing once rendering stalled, so later interaction tests went through the Studio-only DebugCall hook (the same server code paths the prompts call).
