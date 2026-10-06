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
- 2026-10-06 Astra progression playtest fixes (handoffs/PLAYTEST_2026-10-06_ASTRA_FIXES.md): Coach tutorial + next-goal chip, instant/click pickup, walk-in deposit, ramp gap fills + rails (Tools.BuildCliffCollision), beam routed via the ramp, fetch pets deliver to the Crusher, dark rubble, rare meteors last 120 s, base value 25, Reduced effects cuts bloom, no more "$".
- 2026-10-06 Blender art applied: SF_Pets.fbx (16 pets, 4 eggs, Forge Drone, Launch Pad) via Tools.ApplyPets and SF_Decor.fbx (glass crystal clusters x39, stone-tile floor on 8 plots) via Tools.ApplyDecor. Note: the pets FBX came in lying on its face (Blender up on -Z) and was rotated upright by hand; template pivots are set through PrimaryPart.PivotOffset (bottom centre, face -Z). PetModels/egg previews/GadgetService use the meshes; PetFollow puts pet feet on the owner's ground level; drone rotors spin about the model pivot. Mobile next-goal chip moved right of the nav column.
- 2026-10-06 D-025: personal + shared meteors (PersonalMeteors client hides others'), Meteor Chute shortcut, Core Breach event (CoreService + CoreUI: countdown chip, event panel with core HP + personal tier bar, HP bar over the Meteorite, red pulse, damage numbers, result card; pets circle and dive at the core), Core Shards + Core Egg (Coreling, Magmacore - procedural models until Blender versions exist). Guide beam turns red and points at the core while you carry during the event.
- 2026-10-06 D-026 production-line plots: SF_Line.fbx imported; Tools.ApplyLine re-laid all 8 plots (machines, pads, spawn, belts as the Conveyor item, showpieces as plot items, Silo fixture); PurchaseService ghosts (next-buyable only, Neon hologram); MachineService JobMut/JobN plot attributes; LineAnimator (belts, products, silo fill, showpiece motion, chute recoil, streaming-safe registration); GadgetService uses Line spots + Blender chute.

## 2026-10-06: Performance + game passes (D-027)
- Tools.OptimizeParts (re-run after every Apply* import): Box collision on 1715 non-colliding meshes, 934 fewer shadow casters, CanQuery/CanTouch off on decor.
- Client Perf module: distance culling in LineAnimator, MachineAnimator and PetFollow; product cap; HUD throttling. Phones default to Reduced effects, which now also disables Depth of Field, Sun Rays and remote pet sparkles.
- Fix: MachineAnimator streaming bug (machines that streamed in never animated).
- docs/GAMEPASSES.md: 8 passes + 1 developer product with prices, effects and Creator Hub steps.

## 2026-10-06: Zack's 1-hour playtest fixes (D-028)
- HUD: Forge Activity panel + centre notices replaced by one corner column (desktop bottom-right, phones top-right): message feed (payouts merge, fades after ~3 s), compact Forge status card (tap to open Forge), PET PERKS card with FETCH/BEACON cooldown bars. Core Breach result goes to the feed too (HUD.FeedPush).
- Eggs/pets no longer cut off in the Pets panel and hatch reveal (Panels.frameModel aims at the bounding-box centre).
- Pets follow the real floor under them and stay on the owner's side of walls (PetFollow raycasts); fixes clipping through the bridge/props.
- Forge panel: every item has a plain Desc, payout items show "a Normal meteor pays X now, Y after", locked items say what is missing + where and the button becomes "Go to <item>"; locked tabs are grey. Pad + ghost labels show a short effect line.
- Crusher with no Conveyor crunches + sells on the spot (burst, BaseProcessSec 3 -> 1.5). With the Conveyor, products only ride up to the last machine you have built and sell there (no more invisible path over empty gaps). Every machine plays its animation + a burst when a product enters it (Visual PulseAt).
- Fetch pets skip the meteor your guide beam points at, meteors you are walking toward, and meteors next to other players. Pet models carry PerkReadyAt/PerkCd for the HUD.
- Core Breach: events are keyed by round (an early-broken core's timer could end the next event), CoreDamage reset at the end of every event.
- Pets: Sell (Stardust by rarity x egg price; equipped pets can't be sold), Pet Fuser plot item (1,000, needs Smelter; Tools.ApplyFuser part-built model with orbit animation + FusePrompt): 3 same pets -> Gold (x2.5 stats, cooldowns x0.8), 3 Gold -> Diamond (x6, x0.6). Tier aura + sparkles on models, GOLD/DIAMOND ribbon on tiles, fusion reveal.
- Plateau retune: Crusher Mk II 2,500 and +1 payout, Comet Boots 3,500, Forge Drone 5,000, Twin Rack 7,500, Starforge Core 12,000, Frost Egg 15,000, Cosmic Egg 75,000.

## 2026-10-06: Robux game passes (D-029)
- Config.GamePasses (8 IDs) + Config.Pass tuning. New server MonetizationService (UserOwnsGamePassAsync on join with retries, PromptGamePassPurchaseFinished grants live, Pass_<key> player attributes, VIP plot star, Plot Themes recolour of belts + silo, PassAction remote).
- Hooks: MachineService payout x PayoutMult, PetService slots +2 / cap 8, HatchEgg count 3, CarryService walk/carry speed, MeteorService Lucky Sky roll, Main Supernova keep list.
- Client: Shop panel (live icons + prices, Owned state, theme picker, Lucky Sky odds), Shop button (desktop rail, phones next to the gear), x3 hatch button, faster queued hatch reveals, ChatTags LocalScript, PetFollow slots 7-8.
