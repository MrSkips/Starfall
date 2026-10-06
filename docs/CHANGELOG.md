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

## 2026-10-05
- Blender map (SF_Map.fbx) + all gameplay models (SF_Models.fbx): props, purchase pads, sign, mutation meteors, Starheart. Studio tools ApplyMap / ApplyModels written; awaiting import.
- Map + models imported and applied in Studio; meteor meshes, pads, signs, upgrades verified in playtest; lighting toned down (was washed out).
- Step 2 visual slice: StarterPlayerScripts.FX (sounds, music playlist, landing dust/shockwave/chips/sparks + camera shake, falling trails, warning pulse, pickup puff, deposit crunch, payout "+N" popup + coin burst, build poof + scale pop, shower alarm, UI clicks). Settings gained Music + Sound effects toggles. Server Explosion removed (client FX replaces it). Hammer clang synced to forge slam. Bellows moved behind the Smelter (nozzle into its back). Crater floor darkened; Starheart light softened; shadows off on 143 small decor meshes.
- UI palette switched to lime/cyan/red reference colors with black text outlines (D-021). Drop buttons red, stage strip/shower banner/guide beam lime. Collection locked cards narrowed to fit the panel.
- Fixed Codex playtest bugs 01–05 (prompt priority while carrying, CameraGuard + camera proxies, landscape lock + modal refit, phone tap targets, Collection search). Added pickup hop + arms-overhead carry pose (IKControl).
- "10,000x cooler": Tools.BuildSpace (sunset lighting, persistent sky model, 33 neon crystal clusters, 11 floating rocks, energy pillar, embers) + Ambience LocalScript (rock bob/spin, pillar pulse, shooting stars, camera-relative planet/moon so they render). Boxy UI + button/panel/balance/toast/banner animations.
- Loop depth + pets (D-023):
  - Server: DataService (DataStore StarfallForge_v1, autosave 90 s, save on leave/close, offline fallback), GadgetService (Launch Pad, Forge Drone), QuestService (3 quests + 20 h daily with a free Rock Egg), PetService (eggs, odds roll, auto-equip, equip/unequip/equip best, bonuses, pet models), Supernova handler in Main; EconomyService.Set; new remotes QuestAction, PetAction, HatchEgg, RequestSupernova.
  - Streaks, Twin Rack stacking and Meteor Magnet in CarryService; streak/pet/Supernova/lucky payout in MachineService; rare-meteor beam + "INCOMING!" label in MeteorService; 7 tier-2 items in Config.
  - Client: Pets panel (eggs with odds, pet grid with 3D previews, Equip best), hatch reveal animation, Quests panel, Forge gained Starforge Core / gadget / SUPERNOVA tabs, streak badge, Pets/Quests nav + quest-ready dot, PetFollow, Gadgets (launch + drone animation), Twin Rack prompts, LUCKY/STREAK payout popups, dark text no longer gets a black outline.
- 2026-10-06 Pet perks (D-024): Shared.Pets.Perks + PerkTag/PerkText; PetService perk loop (fetch with the pet riding the meteor, beacon), Pop popups; CarryService infuse / pet streak window + cap / supercharge / Strong Starheart carrier; MeteorService.SpawnAround + Aurorabe shower extras; PetFollow fetch/lift/cast animations; perk pills on pet tiles, perk on egg odds and hatch reveal; streak bar uses the per-player window. Blender pets (SF_Pets.fbx) + tools/ApplyPets.luau committed, awaiting import.
