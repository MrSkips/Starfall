# v01 MASTER PROMPT: Core-loop greybox ("Is the meteor rush fun?")
Project: Starfall Forge · Parent master prompt: MP-r1 · Version: v01 · Revision: v01-r1 (2026-10-05)
Baseline: git commit "v00 docs" in the `Alpha Roblox Game` folder. Studio place must be saved as `place/StarfallForge.rbxl` before starting.
**Start condition:** Zack has approved D-005 (Starfall Forge). If he chose the fallback instead, set `Config.Debug.DropOnPlot=true` as the default and skip the crater rush tasks.

## 1. Context (read first)
PROJECT_STATE.md · docs/GAME_DESIGN.md §2–8 and §15 · docs/TECHNICAL_ARCHITECTURE.md §1–4 · docs/DECISIONS.md.

## 2. Player-facing objective
A player can join, find their plot, race to a falling meteor, carry it home, deposit it, watch it turn into Stardust, buy upgrades, and join a meteor shower. **Everything is greybox.** The point is to find out whether the loop is fun.

## 3. Included
1. `tools/build_greybox.luau`: seeded crater (Parts or Terrain), 8 plots (60×60) on the rim with ramps, 3 landmark spires, spawn on own plot.
2. Shared modules: `Config`, `Strings`, `Types`.
3. Services: PlotService, EconomyService (leaderstats "Stardust"), MeteorService (schedule, warning marker plus countdown, falling tween plus impact, mutation roll, despawn), CarryService (prompt pickup, overhead attach, speed and jump change, drop on death or leave), MachineService (queue, 1 Hz tick, payout), PurchaseService (6 pads: Conveyor, Smelter, Carry Boots I, Processing Speed I, Forge, Star Anvil).
4. Meteor Shower every `Config.Shower.IntervalSec` (set to 120 s for testing) plus 1 Starheart needing 2 carriers.
5. Minimal client: Stardust label, "next meteor" timer, beam or arrow to nearest live chunk, deposit "+$" popup.
6. A/B: `Config.Debug.DropOnPlot` makes meteors land inside the player's own plot.
7. Guaranteed Molten mutation on a player's 4th meteor (onboarding beat).

## 4. Excluded
Persistence, rebirth, real art and meshes, Figma UI, sounds beyond placeholder, monetization, analytics, Bump, offline earnings.

## 5. Owners
Integration owner and sole writer for `src/`, `tools/`, and the Studio place: **Claude**. ChatGPT: none in v01 (art task T-00-01 runs in parallel and touches only `art/` and `handoffs/`). Zack: save the place, playtest, and give feedback.

## 6. Contracts
Follow TECHNICAL_ARCHITECTURE §4 exactly. Any change gets a DECISIONS entry first. All gameplay validation happens on the server. No client-to-server remotes in v01.

## 7. Implementation sequence
T1 greybox script, then T2 Config/Plot/Economy, then T3 Meteor plus Carry, then T4 Machine plus Purchase, then T5 Shower plus Starheart, then T6 client HUD, then T7 tests. Write files in `src/` first, sync to Studio, then run a playtest after each of T3, T4, and T5.

## 8. Tests and evidence required
- Studio play solo: screenshot of carry, deposit, payout, and purchase. Console free of errors.
- Studio 2-client local server: unique plots, contested pickup (one winner), Starheart needs both players, and no cross-plot payout.
- Edge cases from TEST_PLAN "Carry edge cases".
- Measured: trip time plot → center → plot while carrying (target 15–25 s), and time from join to first deposit.

## 9. Acceptance
See versions/v01/ACCEPTANCE.md. Runtime claims need screenshots or console evidence. Anything untested is labeled "unverified".

## 10. Stopping condition and outputs
Stop when acceptance passes, or report what's blocked. Update PROJECT_STATE, CHANGELOG, and ASSET_MANIFEST, commit "v01", and give Zack a **playtest script**: 5 questions such as "When did you first feel bored?", "Did the rush or the forge feel better?", and "Rate on-plot drops vs crater rush."

## 11. Completeness checklist
☐ All tasks done or explicitly blocked ☐ Evidence attached ☐ Docs updated ☐ Commit made ☐ Playtest script delivered ☐ v02 recommendation written
