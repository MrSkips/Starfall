# Changelog
## v00 (2026-10-05)
- Capability audit, research brief, concept matrix, provisional design doc, architecture, test and metrics plan, roadmap, v01 master prompt, ChatGPT handoff T-00-01. No game content yet.

## v01 (2026-10-05): Core-loop greybox
- New: seeded greybox map generator (ServerStorage.Tools.BuildGreybox), Config module, 6 server services (Plot, Economy, Machine, Purchase, Carry, Meteor), Main server script, ClientMain HUD.
- Gameplay: meteor warnings, falls, 5 mutations, pickup, carry, drop, and deposit, processing queue, 6 purchase pads, 120 s showers with a Starheart that needs 2 carriers, onboarding meteor, guaranteed Molten on 3rd deposit, DropOnPlot A/B.
- Tooling: [Metrics] logging, Studio-only DebugCall test hook, tools/export_scripts.py.
- Art: CON-01 approved; docs/ART_BIBLE.md rev 1.

## UI pass (2026-10-05)
- Figma: tokens, text and effect styles, 14 icons, 20+ components, 6 screens (HUD desktop and mobile, Shop desktop and mobile, Codex, Settings).
- Roblox: new UI.Kit and UI.Panels modules; ClientMain HUD rebuilt from Figma; Shop, Codex, and Settings panels; RequestPurchase remote; Found_/Owned_ attributes for UI state.
- Art (paused): 12 generated meshes in ServerStorage.Art; ServerStorage.Tools.BuildArt written but **not run**.

## UI rev 2: Astra UI-02 "Asteroid" (2026-10-05)
- Rebuilt UI.Kit (exact Figma tokens), UI.Panels (Collection, Your Forge, Settings), ClientMain (desktop 1440×810 and mobile 960×540 layouts, Forge Activity, notices, shower-active banner).
- 21 icons exported from Astra's Figma and uploaded. MachineService sends job/idle notices and drives Crusher ProcessFX.
- Place published privately (88630827996555).
