# Fixes for PLAYTEST_2026-10-05_RETURN (Claude)

Status: **integrated and verified in Studio** (desktop + iPhone 17 Pro + Galaxy A06 simulation). Not yet verified on a physical phone or with 2 real players.

| Bug | Fix | Re-test evidence |
|---|---|---|
| BUG-01 pickup prompts steal E at the crusher | `StarterPlayerScripts.FX`: while you carry (player attribute `Carrying`), every meteor pickup prompt is disabled locally; re-enabled from each meteor's `State` when you stop carrying. Server checks unchanged. | Exact repro: held Molten at (200,17,17), ground Molten + Normal at (203,·,20)/(203,·,24). Pressing E delivered (+30 Stardust, Carrying cleared). Ground prompts re-enabled afterwards. |
| BUG-02 camera inside crusher / cliffs / mesas | New `StarterPlayerScripts.CameraGuard`: after the camera updates, sphere-cast focus→camera against `Map.Plots` (machine visuals + greybox shells), new invisible `Map.CameraProxies` (96-segment crater-wall ring with ramp gaps, 64-segment mesa ring) and the meteorite collider; the camera is pulled in front of any hit. Boundary wall moved from r≈268 to r≈261 (in front of the mesas). Visual meshes stay non-solid; collision groups `Visual` / `Players` / `GroundRay` keep ground raycasts off the visuals. | Crusher repro: the camera is now in front of the crusher instead of inside it. Outer edge: walking outward stops at r 261.2; camera looking back sits at r 269 (no mesa fill). Meteors still land on the crater floor (y 1.5) and drops land on the plot (y 15.5). |
| BUG-03 portrait HUD overlap | `StarterGui.ScreenOrientation = LandscapeSensor` (landscape only). Open modals refit when the viewport changes (`Panels.Refit`). | PlayerGui reports LandscapeSensor. |
| BUG-04 tiny phone controls | Compact (phone) layout: Forge categories in a 2-column grid, balance + stage strip hidden on phones, buttons 68 design px, whole Settings row toggles, HUD Forge/Collection/gear buttons 66 px. | iPhone 17 Pro: every Forge/Close/Upgrade button 45 px (was 29), Settings rows 385×44, HUD icons 44. Galaxy A06 (smallest): 40–43 px (was 19–21). |
| BUG-05 Collection empty column | Discovered group hidden when none of its cards match; "No mutation matches …" message when nothing matches. | Galaxy A06: Normal+Molten found, search "cos" → only Cosmic card, no empty column. "zzzz" → no-results message. |

Also added (Zack's request): **pickup animation**. On pickup the rock hops from the ground to the head in a 0.32 s arc with spin and squash, and both arms lift into an overhead hold (IKControl on the arm chains, so legs keep their walk animation; blends in 0.25 s, out 0.2 s). Visible to every player. Measured: hand rises from 1.9 below the head to 0.9 above it within ~0.2 s.

Other: server banner now says v02 visual slice.
