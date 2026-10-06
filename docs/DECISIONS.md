# Decision log
| ID | Date | Decision | Status | Basis |
|---|---|---|---|---|
| D-001 | 2026-10-05 | Genre is tycoon with a distinctive twist | Approved by Zack | Zack's answer |
| D-002 | 2026-10-05 | PC and mobile equal priority. ProximityPrompt-based interactions | Approved / design | Zack's answer |
| D-003 | 2026-10-05 | $0 budget until revenue. No paid tools or ads without approval | Approved | Zack's answer |
| D-004 | 2026-10-05 | ChatGPT is the partner AI. Mode B manual relay | Approved / verified | No shared messaging tool exists |
| D-005 | 2026-10-05 | Concept: Starfall Forge (fallback: Classic Forge, kept as the DropOnPlot toggle) | Approved by Zack ("you're up") | GAME_DESIGN §1 |
| D-006 | 2026-10-05 | No paid random items, no base stealing, no feed/scroll rewards in the MVP | Proposed | Roblox policy (RESEARCH §D, §A4) |
| D-007 | 2026-10-05 | ~~src/ canonical~~ **Revised:** Studio (saved as place/StarfallForge.rbxlx) is the live code surface; tools/export_scripts.py mirrors scripts into src/ for git | Approved (rev 2) | Avoids writing every script twice through two tools |
| D-008 | 2026-10-05 | Claude is the integration owner for v00–v01 | Proposed | Only Claude has verified Studio access |
| D-009 | 2026-10-05 | Astra takes T-00-01 (art exploration from Zack's style video). ChatGPT stays available for later tasks | Approved by Zack | Zack's request |
| D-010 | 2026-10-05 | Art direction: CON-01 Sunlit Toy Foundry. CON-02/03 rejected | Approved by Zack | Astra T-00-01 |
| D-011 | 2026-10-05 | Astra makes concept and HUD *images*; Claude is the only writer in Figma and builds native Roblox UI; Astra reviews | Approved | Single writer per target |
| D-012 | 2026-10-05 | A meteor is claimed by whoever picks it up first. You compete on the way *to* it, never take it from a carrier (no Bump in the MVP) | Adopted | Astra concept check, design §6 |
| D-013 | 2026-10-05 | "Starfall Forge" stays a working title: the style reference video advertises a "Starfall Event". Rename before publishing | Open | Astra concept check |
| D-014 | 2026-10-05 | Shower interval is 120 s for v01 testing (design target 360 s) | Temporary | Faster playtests |
| D-015 | 2026-10-05 | Zack: the greybox looks too blocky. Pulled an art pass forward: 12 AI meshes generated into ServerStorage.Art and a BuildArt tool written (terrain crater, mesas, lighting, plot dressing). **Paused before running at Zack's request ("focus on UI")** | Paused | Zack |
| D-016 | 2026-10-05 | UI built in Figma (tokens, 20+ components, 6 screens), then as native Roblox UI (Kit, Panels, ClientMain). Shop purchases go through a validated RequestPurchase remote | Done | docs/UI.md |
| D-017 | 2026-10-05 | UI direction = Astra UI-02 "Asteroid" (charcoal panels, copper actions, teal progress), copied 1:1 into Roblox. Supersedes the rev-1 cream UI (D-016) | Approved by Zack ("copy 1:1") | docs/UI.md |
| D-018 | 2026-10-05 | Figma ownership: Astra owns the UI-02 design file; Claude owns the Roblox implementation and reads Astra's file (read-only) | Adopted | Single writer per target |
| D-019 | 2026-10-05 | Place published privately to Roblox (placeId 88630827996555) so the Asset Manager and DataStores work | Done (Zack) | |
| D-020 | 2026-10-05 | Add Pets + Eggs (Stardust eggs always available). Robux eggs only if Roblox paid-random-item rules are met (odds shown before purchase, PolicyService region gate, every pet also obtainable free). Supersedes the egg part of D-006 | **Needs Zack: Robux eggs yes/no after T-03-01 return** | Zack request |
| D-021 | 2026-10-05 | UI palette = reference-video colors (lime #6FFF10 primary, cyan #19F0F5 secondary, red #E70002 drop, panels #32333E, outline #080809, gold #FFE21B, purple #9A15E8). White text with a black outline on buttons and headings. Copying the palette is accepted. Layout stays Astra UI-02. Supersedes the D-017 palette | Approved by Zack | art/concepts/UI-02/REFERENCE-COLORS.md |
| D-022 | 2026-10-05 | Map look = "epic space crater" (sunset sky, ringed planet + moon, glowing crystal clusters, floating rocks, energy pillar, embers, shooting stars). UI = boxy (6px corners, 3px black borders, hard drop shadows) + juice (hover/press bounce, shine on primary buttons, count-up balance, panel slide-in, toast pop, shower banner throb) | Approved by Zack | Tools.BuildSpace, StarterPlayerScripts.Ambience, UI.Kit |
