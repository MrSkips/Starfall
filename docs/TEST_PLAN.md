# Test plan and metrics plan

## Risk-based tests (added as versions introduce the feature)
| Area | Checks | From |
|---|---|---|
| Join and first loop | Spawn on own plot; first meteor visible within 10 s; pickup, carry, deposit, and payout | v01 |
| Carry edge cases | Die or reset while carrying (chunk drops); leave while carrying (chunk freed); two players trigger one chunk in the same frame (one wins); deposit at someone else's plot (rejected) | v01 |
| Economy | Can't buy without funds; can't double-buy; purchase order requirements enforced; machine payouts match Config | v01 |
| Multiplayer | 2–4 client Studio test: plots unique, no cross-plot payouts, shower spawns count correctly, Starheart needs 2 carriers | v01 (2 clients) / v03 |
| Remote misuse | Spam, wrong types, out-of-range requests, other player's plot. Server rejects all | v02+ (when remotes exist) |
| Persistence | Save and rejoin; save failure retry; second-session lock; schema migration v1 to v2 | v03 |
| Devices | Phone, tablet, and PC layouts in Device Simulator; touch prompts reachable; HUD doesn't cover the meteor marker | v02 |
| Performance | Budgets in TECHNICAL_ARCHITECTURE §6 during a shower | v02 / v04 |
| Art | Compare against the selected concept; mutation readability; imported mesh orientation, collisions, missing textures | v02 |

Findings are sorted into **verified defect / usability observation / hypothesis / preference**, then prioritized by impact × frequency ÷ cost.

## Analytics (v03–v04; verify current AnalyticsService API before implementing)
Onboarding funnel: `join → first_pickup → first_deposit → first_purchase → first_mutation → first_shower → session_end`.
Other events: `purchase{itemId,cost}`, `supernova{count}`, `shower_participation{chunks}`, `starheart_coop{carriers}`, economy source and sink events.
Platform metrics (Creator Analytics): D1, D7, D28 retention; play-through rate; first-play bounce; play days per user; co-play rate. Cohort = new users by join day.

## Provisional goals (hypotheses, not benchmarks)
- Playtest (5–10 players Zack knows): **≥ 80% reach first purchase within 2 min**, and **≥ 50% voluntarily keep playing past 10 min**. Small biased sample, so treat this as directional only.
- After launch: watch D1 and first-play bounce weekly. No targets until we have real data.
