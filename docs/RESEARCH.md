# Research brief, v00
Research date: **2026-10-05**. Researcher: Claude. Sources are listed at the bottom.
Labels: **[Official]** = Roblox source. **[3P]** = third-party or press. **[Inferred]** = my reasoning, not observed.

## A. How Roblox decides what to recommend
1. **[Official]** The "Recommended For You" algorithm was widened from a 7-day view to a **28-day view of long-term retention**. It splits retention into day 1, days 2–7, and days 8–28. Play-through, session quality, and spend are now separate signals. Roblox says it rewards games where "players come back to a game over time, bring their friends, and spend money." (Roblox newsroom, June 2026)
2. **[Official]** The most important home signals are **play-through rate** (impression to play), **first-play bounce rate** (leaving after a short first session), **play days per user**, and **playtime per user**. Next come **co-play with friends**, qualified play sessions, and spend days and Robux per user. All are per-user averages, so a small game isn't penalized for being small. (Creator Hub: Discovery)
3. **[Official]** Discovery downranks giveaway or money-reward metadata, metadata that doesn't match gameplay, and **"non-unique games resembling existing titles."** Thumbnails must reflect real gameplay. (Creator Hub: Discovery)
4. **[Official / 3P]** As of 2026-08-29, games that reward users for consuming a continuous content feed with no natural stopping points are restricted for younger accounts. This followed the viral *Steal An Egg*. (MassivelyOP, citing the Roblox DevForum)

**What this means for us [Inferred]:** the first 60 seconds (bounce rate), a reason to come back on day 2 and again around day 8–28, and doing things *with* other players all matter more than raw session length. A clone of a top game gets suppressed.

## B. What's working in the genre right now (observed through public trackers and press)
| Experience | What was observed | Takeaway |
|---|---|---|
| Steal a Brainrot (May 2025) | Buy characters off a shared conveyor. They earn passive income at your base. Other players can steal them; temporary base shield; rebirth. Peak 25.4M CCU (Oct 2025). Criticized for pay-to-win admin powers and exploiters. | A **shared, contested source** of value in the open area, plus a personal base, creates stories. Paid power over other players causes backlash |
| Steal An Egg (2026) | Steal eggs, hatch pets, earn, upgrade the base. About 15-min sessions. All-time peak around 9.9M. Removed after its feed-reward treadmill mechanic triggered the new policy. | "The name explains the game." Short sessions work. Stay away from feed/scroll reward mechanics |
| Grow a Garden (Mar 2025) | Plant crops, wait for growth, mutations, weekly updates, server-wide co-op events (Summer Harvest donation tiers). 21.3M peak (Jun 2025). | **Mutations** plus **weekly events** plus **cooperative server goals** drove record peaks |
| Sell Lemons (2026) | Buy, earn, invest, reset. Workers and managers automate income. Rebirth, Evolution, and Ascension layers. NPC phone deals. About 135k CCU (Jun 2026). | Layered prestige and automation still work when the theme is fresh |
| Kick a Lucky Block | RNG clicker with meteor-shower events. About 107k (Jun 2026). | Server-wide timed events are a common retention beat |
| Build An Ant Empire / Build the Pyramid | Base-building and construction sims. About 20k each (Oct 2026 tracker, undated) | Building-up fantasies still pull mid-sized audiences |
| Retail / Restaurant / Theme Park Tycoon 2 | Long-lived "build a business" tycoons | Evergreen fantasy, but heavy content and building tools |
| Fish It!, Fisch | Fishing sims, "one of Roblox's most-cloned genres" | A saturated theme. Avoid making fishing the core |

Not observed: revenue, retention, or conversion for any of these games. Peak CCU numbers measure virality, not *why* a game works.

## C. Design lessons
- **[3P]** Classic room-and-button tycoons get monotonous. They need goals, events, and new mechanical layers that unlock gradually. Juice (sounds, bounces, coins popping) affects retention. "No events, no game." Avoid "fast food" design that collapses by day 7. (AppQuantum, Oct 2025)
- **[Inferred]** The hits combine three things: (1) a **personal base that earns while you do other things**, (2) a **shared open space with a contested or cooperative resource**, and (3) **random rarity layers** (mutations) that make every pickup a small lottery *without* charging money for the roll.

## D. Monetization and policy constraints
- **[Official]** Paid random items (loot boxes, paid wheels, paid luck boosts, pity systems) require all outcomes with exact odds summing to 100%. Players where `PolicyService.ArePaidRandomItemsRestricted` is true must get a free path, a fixed sequence, a direct purchase, or no access. **Decision: no paid random items in the MVP.**
- **[3P]** DevEx is about **$0.0035 per Robux** (mid-2026). Roblox keeps 30% on passes and products. Example from the source: 500k Robux a month nets about $800 after the cut and taxes. Revenue needs a real audience. Nothing here is a promise.

## E. AI production feasibility
- **[Official]** Studio MCP exposes `generate_mesh`, `generate_material`, `generate_procedural_model`, texture generation, `execute_luau`, playtest control, and screen capture. Claude has these **connected and verified** (generation not yet tested). The Cube foundation model is moving toward "4D" functional objects (Feb 2026).
- **[Inferred]** Rocks, crystals, glowing ores, and chunky machines are among the easiest subjects for AI mesh generation and procedural parts. Organic characters needing rigs and animation are the hardest. **Prefer a theme built from props and effects.**

## F. Risks for a tycoon
Clone suppression · monotony after day 1 · exploiters (server authority required) · pay-to-win backlash · feed-reward policy · mobile performance from particle-heavy effects · AI art drifting between assets.

## Sources
- [Roblox newsroom: Optimizing discovery (Jun 2026)](https://about.roblox.com/newsroom/2026/06/optimizing-discovery-great-games-reach-millions-players-roblox)
- [Creator Hub: Discovery](https://create.roblox.com/docs/production/promotion/discovery)
- [Creator Hub: Paid random items](https://create.roblox.com/docs/production/monetization/paid-random-items)
- [Creator Hub: Studio MCP](https://create.roblox.com/docs/en-us/studio/mcp.md)
- [Roblox newsroom: Cube foundation model (Feb 2026)](https://about.roblox.com/newsroom/2026/02/accelerating-creation-powered-roblox-cube-foundation-model)
- [Wikipedia: Steal a Brainrot](https://en.wikipedia.org/wiki/Steal_a_Brainrot)
- [Player.One: Steal An Egg](https://www.player.one/robloxs-steal-egg-beating-some-platforms-biggest-games-164086)
- [MassivelyOP: Roblox clamps down on feed games (2026-08-29)](https://massivelyop.com/2026/08/29/roblox-clamps-down-on-gen-ai-brainrot-scrolling-games-after-steal-an-egg-goes-viral/)
- [Insider Gaming: Grow a Garden record](https://insider-gaming.com/roblox-grow-a-garden-shatters-all-time-player-record-for-second-week-in-a-row/)
- [RoWatcher: Most popular games (Jun 2026)](https://rowatcher.com/news/the-most-popular-roblox-games-right-now-ranked-by-live-players)
- [RoWatcher: Simulation genre](https://rowatcher.com/genres/Simulation)
- [RoWatcher: DevEx math 2026](https://rowatcher.com/news/roblox-devex-math-what-you-actually-take-home-in-2026)
- [Beebom: Sell Lemons wiki](https://beebom.com/sell-lemons-wiki/amp/)
- [AppQuantum: How to make tycoons in 2025](https://appquantum.com/news/october-2025/once-again-on-how-to-make-tycoons-in-2025-with-links-and-examples.html)
- [creation.dev: Tycoon genre](https://www.creation.dev/genres/tycoon)
