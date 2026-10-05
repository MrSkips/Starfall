# Game design, v00 (PROVISIONAL until Zack approves)

## 1. Concept comparison
Scale: 1 = poor, 3 = workable, 5 = strong. Weighted score = Σ(weight × score) / 5, so the maximum is 100. **These are comparative judgments, not predictions.**

| Criterion | Weight | A. Starfall Forge | B. Reef Keeper (aquarium) | C. Haunted Hotel | D. Sky Couriers | F. Classic Forge (fallback) |
|---|---|---|---|---|---|---|
| First-session appeal and clarity | 15 | 5 | 4 | 4 | 3 | 3 |
| Replay and retention potential | 15 | 4 | 4 | 4 | 4 | 2 |
| Distinctiveness and audience fit | 12 | 4 | 3 | 4 | 4 | 2 |
| AI asset feasibility and consistency | 12 | 5 | 3 | 2 | 4 | 5 |
| Code and multiplayer complexity (5 = simple) | 10 | 3 | 3 | 2 | 2 | 5 |
| Mobile usability and perf risk (5 = low risk) | 8 | 4 | 3 | 3 | 3 | 5 |
| Content and update burden (5 = light) | 10 | 4 | 3 | 2 | 3 | 4 |
| Monetization fit and fairness | 8 | 4 | 4 | 4 | 3 | 3 |
| Time to a convincing vertical slice | 10 | 4 | 3 | 2 | 2 | 5 |
| **Weighted total** | 100 | **83.4** | 67.6 | 61.6 | 63.8 | 72.6 |

- **A. Starfall Forge:** meteors crash into a shared crater. Players race out, haul glowing chunks home, and their forge machines turn them into cash. Mutations and server-wide meteor showers. *(Recommended.)*
- **B. Reef Keeper:** catch fish on a shared reef and display them in your aquarium for visitor income. Fishing is a heavily cloned theme, and creatures plus visitor NPCs cost more art.
- **C. Haunted Hotel:** monster guests with needs and rooms to build. Strong fantasy, but many rigged, animated creatures (the hardest AI asset type) and complex guest AI.
- **D. Sky Couriers:** build bridges and ziplines between floating islands for co-op deliveries. Very distinctive, but player-built physics networks are expensive and fragile.
- **F. Classic Forge Tycoon (fallback):** same theme as A, but meteors drop into *your own* plot like a classic dropper tycoon. No shared rush. It reuses every A asset, so falling back to it costs almost nothing.

**Why A wins:** it copies the *structure* that the hits share (personal base, contested shared resource, free random rarity) without copying their theme. "Starfall Forge" also explains itself, which helps play-through rate. Rocks, crystals, machines, and particle trails are the easiest AI assets to produce. The cost is moderate multiplayer code: carrying, contested pickups, and events.
**What could change this:** your art references point toward organic creatures (favors B or C), you want zero player-versus-player contact (A still works with bumping turned off), or the v01 playtest shows the rush is tedious (fall back to F).

## 2. Pitch
**"Catch falling stars. Haul them home. Forge a fortune before the next shower hits."**
- **Audience:** Roblox players aged about 9–16, plus casual older players. All-ages content. No combat.
- **Fantasy:** a cosmic prospector-blacksmith growing a tiny forge into a glowing star-foundry.
- **Hook:** the sky is **shared and live**. Everyone sees the same meteor streak in, everyone races for it, and rare mutated meteors cause stampedes. Big "Starheart" meteors need **two players to carry**, and both get paid (a co-play signal).

## 3. Loops
- **Core loop (about 20–40 s):** a meteor warning appears (marker plus countdown). Run to it. Grab a chunk (ProximityPrompt). Carry it home slowed down. Drop it in your Crusher. Cash ticks up as the machines process it.
- **Session loop (about 10–15 min):** buy machines and upgrades with the cash. Bigger forge, faster processing, more carry capacity. Catch at least one **Meteor Shower** (every 6 min, server-wide).
- **Progression loop:** the forge tiers up (Crusher, Smelter, Forge, Star Anvil). The final purchase unlocks **Supernova** (rebirth): reset the plot for a permanent multiplier and a new planet biome with new meteor types.
- **Return loop:** a free daily Comet Crate (fixed reward, not random paid), offline processing (capped), weekly shower themes and limited mutations, and unfinished rebirth goals.

## 4. First-time player timeline
- **0–30 s:** spawn on your assigned plot. A meteor is already falling 40 studs away: "Meteor landing in 5…". An arrow and beam point to it. Grab it, carry it to the glowing Crusher, deposit, and see "+$15" pop with a clink. *No menus before the first deposit.*
- **30 s–2 min:** two or three more meteors. The first purchase pad (Conveyor, $40) lights up when affordable. **A guaranteed Molten mutation** (×2, orange flames) appears by minute 2.
- **2–10 min:** 5–7 purchases. The first Meteor Shower arrives (15 rocks plus 1 Starheart). The goal tracker shows "Next: Smelter → Forge Tier 2".
- **Later sessions:** reach Supernova at about 45–60 min of play (to be tuned), the new biome, mutation collection log, and daily crate.

## 5. Controls, camera, and feedback
- Default Roblox movement and camera, which works on PC, mobile, and controller. Interactions use **ProximityPrompt** (tap, E, or button X), so touch and controller come for free.
- Carrying: the chunk sits above your head, walk speed drops 16 to 11 (configurable), and you can't jump while carrying (configurable). Drop it anytime with the same prompt.
- Feedback: impact shake plus dust on landing, a glow pulse that is stronger for rarer meteors, a coin-burst number on deposit, machine animations, and a purchase "build-in" tween.
- Failure and recovery: nothing is ever lost from your base. The worst case is another player grabbing the meteor first. Dropped chunks despawn after 60 s.

## 6. Multiplayer
- **Server size hypothesis:** 8 players, with 8 plots ringed around a central crater field.
- **Contested but fair:** anyone can pick up a ground chunk. **No stealing from bases.** Optional *Bump* (v03 experiment, off by default): a short-cooldown shove makes a carrier drop their chunk.
- **Co-op:** Starheart meteors need 2 carriers (speed scales with carriers), and every carrier's base gets the full value. The server shower goal is "Collect 30 chunks together → everyone gets a Shooting Star boost".

## 7. Map (greybox targets, to be measured in v01)
- Central crater field about 260 × 260 studs with gentle dunes and 3 landmark rock spires for orientation.
- 8 plots of 60 × 60 studs on the rim, each with a ramp into the crater. **Target trip plot → center → plot: 15–25 s while carrying.**
- Meteors land in weighted zones. Rare ones favor the center (contest point). Each landing is guaranteed at least 25 studs from any plot.

## 8. Economy (all values live in `Config.luau`)
- **Currency:** Stardust ($). One soft currency in the MVP.
- **Sources:** processed chunks (base value × mutation multiplier × machine multiplier × rebirth multiplier), shower bonuses, daily crate.
- **Sinks:** machines, upgrades (processing speed, carry speed, capacity), cosmetics later.
- **Mutations (free, rolled at spawn):** Normal 70% ×1 · Molten 18% ×2 · Frozen 8% ×3 · Charged 3.5% ×5 · Cosmic 0.5% ×12. The odds are shown in an in-game Codex for transparency even though they aren't paid.
- **Offline processing (v03):** up to 2 h at 50%.

## 9. Onboarding
Contextual only: arrows, highlights, and one-line prompts, with no text walls. Steps: grab, deposit, buy first pad, catch shower. Skippable, and it never repeats once done (saved).

## 10. UI inventory (MVP)
HUD (Stardust, next meteor or shower timer, goal tracker) · Purchase pads (in-world) · Shop panel (upgrades, v02) · Codex (mutations and odds, v03) · Settings (music/SFX, reduced effects) · Supernova confirm · Daily crate · Store (passes, v04) · Loading, error, and "data failed to load" states (v03).

## 11. Audio, animation, and effects
Meteor whistle and impact, pickup grunt-free "chime", deposit clink (pitch rises by rarity), machine hum loops, purchase thunk, shower siren, ambient space-wind music bed. Effects: Beam trails, ParticleEmitters with per-device "reduced effects" settings. No custom character animations in the MVP (Roblox default plus carry pose via simple Motor6D tween).

## 12. Monetization (v04, ethical)
Enjoyable with no payment. Game passes: 2× Stardust, Swift Boots (+carry speed), Collector Drone (auto-grabs small chunks inside your plot), cosmetic forge skins. Private servers. **No paid random items. No paid power against other players.**

## 13. Accessibility and localization
Color *and* shape or particle cues for mutation rarity (colorblind-safe), reduced-effects toggle, minimum touch target 44 px, all strings in a `Strings` module ready for localization, captions for siren cues.

## 14. MVP boundary
**In:** one biome, 8 plots, meteor rush, 5 mutations, showers, Starheart co-op carry, 4 machine tiers plus about 15 purchases, Supernova ×1 biome, persistence, onboarding, HUD/Shop/Codex/Settings, 3–4 passes, analytics funnel.
**Deferred:** Bump PvP, second biome, trading, pets/drones beyond the pass, leaderboards, seasonal events, localization translations.
**Excluded:** paid random items, base stealing, feed/scroll rewards.

## 15. Biggest unproven assumption
**"Running out, grabbing a meteor, and hauling it home is fun to repeat for 10+ minutes, and better than meteors landing in your plot."** v01 tests this directly with configurable carry speed, spawn rate, and distance, plus an A/B toggle that drops meteors on-plot (the fallback F).
