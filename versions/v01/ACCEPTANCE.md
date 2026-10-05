# v01 acceptance criteria
1. A fresh solo join spawns on an owned plot. The first meteor warning appears within 10 s.
2. Pickup works on PC (E) and through the touch prompt (Device Simulator). The carry slows the player to Config speed.
3. Depositing at your own Crusher pays out within `ProcessSec` × queue. Depositing at another plot is rejected.
4. All 6 purchase pads work, respect order and funds, and can't be bought twice.
5. A shower spawns `Count` chunks plus 1 Starheart. A single player can't move the Starheart. Two can, and both get paid.
6. Death or leaving while carrying drops or frees the chunk. Chunks despawn after `DespawnSec`.
7. Two-client test passes with no errors in the server or client console.
8. Toggling `DropOnPlot` switches the mode without code edits.
9. Carrying trip time and time to first deposit are measured and recorded.
