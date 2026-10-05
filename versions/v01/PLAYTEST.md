# v01 playtest script (Zack plus 2–3 friends)

## Setup (Zack)
1. Open the place in Studio. **Test tab → Clients and Servers → 2 (or 3) players → Start.** Each test window is one player.
2. For a real-device check, publish privately and play on your phone with a friend (optional for v01).
3. Play for **10 minutes without explaining anything.** Just watch where people hesitate.
4. To try the fallback mode: in `ReplicatedStorage.Shared.Config`, set `Debug.DropOnPlot = true`, play 5 more minutes, then set it back.

Controls: **E** (or tap) to pick up and deposit · **Q** (or the Drop button) to drop · walk onto green pads to buy.

## Things to check (two-player only, couldn't be automated)
- [ ] Both players spawn on different plots
- [ ] Two players reaching one meteor at the same time: only one gets it
- [ ] Starheart (gold, appears in each shower): one player can't move it; two players holding it makes it follow them; depositing pays **both** players
- [ ] Nobody can deposit at someone else's Crusher

## Questions (write the answers in versions/v01/PLAYTEST_RESULTS.md, or just paste them to Claude)
1. In the first minute, did you know what to do without being told? What confused you?
2. When did you first feel bored (minute mark), and what were you doing?
3. Running into the crater vs meteors landing on your plot (DropOnPlot): which felt better, 1–10 each?
4. Did the meteor shower feel exciting, or just like "more of the same"?
5. Would you come back tomorrow to finish the Star Anvil? What would make you?

## Numbers Claude will pull from the Output window ([Metrics] lines)
Time from join to first deposit, trip time per meteor, purchase timings, and starheart_coop events. In Studio, copy the Output window into the results file.
