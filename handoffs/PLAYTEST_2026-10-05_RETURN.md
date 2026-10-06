# Starfall Forge — hour playtest RETURN

Owner: Codex. Requested by Zack: play for about an hour and find bugs.
Date: 2026-10-05 (America/New_York). Place: **88630827996555**.
Build: live Studio visual slice described as v02 in PROJECT_STATE.md; server banner still says v01 greybox. This was not a published-client test.
Status: **completed QA session; fixes not implemented**.
Session window: approximately **20:17–21:18 EDT on October 5** (**00:17–01:18 UTC on October 6**), about 61 minutes across three Studio play sessions. This includes gameplay, UI inspection, supplemental checks, and tool recovery; it is not 61 minutes of uninterrupted human-style play.
Evidence totals: **34 logged player deposits** (17 first desktop, 15 phone simulation, 2 final desktop), plus the separate four-job queue check. Console evidence is saved in `PLAYTEST_2026-10-05_LOG.md`; no game script error appeared in the captured logs. This does not prove the build is error-free.
End state: **Play stopped; device simulation reset to default.** Temporary test funds, meteor spawns, observers, and character changes were discarded. No source or place asset changes were saved.

## Confirmed findings

### BUG-01 — Nearby pickup prompts can intercept delivery (P2, gameplay)

**Reproduction:** Put several ground meteors within pickup range of your crusher. Pick up one, then press E to deposit while another ground meteor remains nearby. In this test the avatar was approximately `(200, 17, 17)`, the crusher intake was `(191, 23.25, 18)`, and other chunks were around `(203, 15.5, 20)` and `(203, 15.5, 24)`.

**Expected:** While carrying and at your crusher, E delivers the held meteor.

**Actual:** E targets a different ground meteor's pickup prompt. The server refuses another pickup because the player is already carrying, and delivery does nothing. Repeated E attempts retained the held Normal chunk and the same 1,131-Stardust balance. The intake was enabled, on screen, and 10.92 studs away, inside its 14-stud prompt range. Moving away from the ground chunks allowed delivery and increased the balance to 1,199.

**Evidence:** Temporary client prompt tracing recorded `Workspace.Meteors.Meteor_Normal.ProximityPrompt` for the successful pickup, then `Workspace.Meteors.Meteor_Molten.ProximityPrompt` for the attempted delivery. No deposit occurred until repositioning. The pile was created using Studio's existing Meteor test hook; the interactions used keyboard input. Ground chunks near a crusher can also arise from dropping carried chunks, but that natural pile-building sequence was not separately tested.

**Suggested fix:** Suppress ordinary pickup prompts locally while carrying, and give the owned crusher's deposit interaction priority. Preserve the server's existing ownership, distance, and carry validation. Handle Starheart joining separately.

### BUG-02 — Camera can enter visible meshes and obscure play (P2, visuals/navigation)

**Reproduction:** Approach Plot1's crusher from the crater side near `(183.3, 17, 17.6)` at the default camera distance. Also walk outward from the plot toward the outer cliff near `(267.6, 16, -8.6)`. A similar obstruction occurred near a solo-held Starheart beside the central crater prop.

**Actual:** The crusher rollers, cliff, or central prop fill much of the screen and hide the avatar or carried meteor. At the first crusher occurrence the camera was around `(195.39, 21.75, 17.58)`. The outer-cliff screen was almost entirely blue mesh. Other ordinary tree occlusion was observed during the phone session.

**Evidence:** Screenshots `Crusher_Delivery`, `Mobile_Boundary_Fall`, `Mobile_Boundary_Respawn`, and `Android_Starheart_Active`, inspected directly in this chat. All 240 parts under `Workspace.Map.Visual` had both CanQuery and CanCollide false. Eleven of the crusher's 15 parts were also non-queryable/non-collidable. Invisible greybox parts remain its physical proxies.

**Suggested fix:** Review camera obstruction against the visible meshes and align the proxy volumes with them. Test a camera-specific obstruction solution or suitable queryable proxies; changing every visual's query/collision settings blindly could affect meteor ground raycasts and navigation. Validate at both normal camera distances and all eight plots.

### BUG-03 — Portrait HUD overlaps (P2, mobile)

**Reproduction:** Start play on iPhone 17 Pro in landscape, then rotate to portrait. StarterGui.ScreenOrientation is Sensor, so the place currently permits this orientation.

**Actual:** The shower banner overlaps the balance area, and the settings button covers part of the banner text. A toast occupies much of the remaining upper view. The measured viewport was `401 × 778`, HUD scale `1.4407`, and the banner about `389 × 72`.

**Evidence:** `iPhone17_Portrait_HUD` and `iPhone17_Portrait_Forge`. ClientMain chooses MOBILE once at startup and rescales primarily by viewport height. Its open modal also does not refit immediately on a viewport change; desktop-to-phone simulation showed an oversized panel until reopening.

**Suggested fix:** Either explicitly support portrait with a responsive layout and viewport-change refitting, or choose a landscape-only orientation if that is Zack's intended product behavior. Do not silently treat portrait as supported without testing it.

### BUG-04 — Phone modal controls shrink excessively (P2, usability)

**Reproduction:** Open Forge or Settings on the phone presets. Rotate to portrait for the smallest Forge controls.

**Measured results:** iPhone 17 Pro landscape Forge category and Close buttons were about **29 pixels high** after fitting. Portrait Forge category buttons were about **62 × 19 pixels**. On Galaxy A06 landscape, Settings toggle hit targets were about **38 × 21 pixels**. Labels also become very small.

**Evidence:** `iPhone17_Forge_Actual`, `iPhone17_Portrait_Forge`, `Galaxy_A06_Settings`, and live AbsoluteSize queries. These are simulator measurements, not physical touch testing.

**Suggested fix:** Use a phone-specific modal composition with scrolling or stacked sections, larger hit regions, and readable type instead of shrinking the entire desktop composition to fit. Keep the approved lime/cyan/red palette and outlined white button labels.

### BUG-05 — Collection search leaves an empty column (P3, UI)

**Reproduction:** Discover at least one mutation, then search for an undiscovered mutation (e.g. Cosmic) or an unmatched string (`zzzz`).

**Actual:** A narrow empty bordered Discovered group remains. An unmatched query has no clear no-results message; the footer still lists the overall discovery state.

**Evidence:** `Collection_Search`, `Galaxy_A06_Collection_No_Match`, and Panels.RefreshCollection. Group visibility uses the total known count instead of the count of visible matching known cards.

**Suggested fix:** Hide that group when no discovered cards match the query, and show a clear empty-search state when neither group has matches.

## Checks that passed

- Pick up, overhead carry, Q drop, GUI Drop, and re-pickup. Ordinary carry speed was 11; Boots increased it to 13; dropping restored 16.
- Normal, Molten, Frozen, and Charged were collected from naturally spawned meteors. Cosmic was exercised with a QA-spawned meteor, so its natural rarity was not validated.
- Base examples: Frozen paid 45; Molten paid 30. With Smelter: Normal paid 23, Frozen 68, Charged 113. Full upgrade multiplier: Normal paid 68, Molten 135, Cosmic 810.
- Purchases charged their configured amounts; the six upgrade costs totalled 2,140. Prerequisite/insufficient-funds states and repeat/max-level clicks did not produce a second charge in the tested cases.
- Another plot's crusher rejected delivery and retained the held meteor.
- A carried chunk survived a **118.9-second** rim circuit and paid correctly afterward. Ground expiry did not destroy that held chunk.
- Single-holder Starheart stayed stationary. Walking outside its hold radius with keyboard input released it and restored client/server speed to 16. **Two-player carry and payout remain untested.**
- Supplemental death test: after setting the test avatar's Health to zero while carrying, it respawned at `(181, 17, 0)` with Health 100, speed 16, jump power 50, and no stuck carried chunk. Balance remained unchanged. The native Reset menu was inaccessible to the automation tool.
- Music/SFX groups muted and restored correctly; settings persisted when reopening the panel within the same session. Listening quality was not assessed.
- Multiple natural showers, banners, warnings, falling meteors, pickup after landing, and ground expiry were observed. The current test interval is 120 seconds, not the design's 360 seconds.
- All five Collection icons eventually loaded. Initial blank icons were loading delays and are **not** reported as broken assets.
- The completed desktop activity panel displayed Crusher, Smelter, Forge, and Star Anvil rows.
- Supplemental queue test: four jobs (base values 15, 30, 75, 180) paid **68, 135, 338, 810**, in order, once each. Balance changed **1,199 → 2,550**, exactly +1,351, and Processing returned false. This used Machine.Enqueue through DebugCall, not rapid player deposits.

## Known release gap, not a newly discovered bug

Progress saving is already marked planned in HANDOFF.md. The inspected live server starts balances at zero and has no saving service in its initialization path. Studio restarts reset test progress, but that alone is not a published-server persistence test. Claude should finish saving before release or monetization and verify real leave/rejoin behavior separately.

## Test method and limitations

Used Studio character navigation, keyboard/mouse input, screenshots, console logs, and read-only state/source inspection. No game scripts, meshes, configuration, or published place were edited. Temporary setup consisted of test currency, QA meteor spawns, queued jobs, one induced avatar death, and short prompt/notification observers. Stopping play discards this session state.

Desktop control helper failed to initialize (`failed to write kernel assets`), including after reset. Roblox's purpose-built tools remained available. Native Escape/Reset input was blocked by VirtualInput. Phone clicks needed correction for device safe-area offsets. Navigation sometimes returned success without arriving, or failed when a target expired; final character coordinates were checked and these tool failures were not counted as game bugs. A stale client speed after tool-driven Starheart navigation was excluded; keyboard movement produced the correct reset.

No real second client, physical phone, published-client reconnect, Robux purchase, receipt processing, full-server contention, or real-device performance test was performed. Editor memory samples are not a reliable mobile memory benchmark. Pacing to all upgrades is not measured: inspections interrupted play, and late-machine setup used temporary currency.

Screenshots were inspected inline via Studio; the capture IDs above identify the chat evidence. They were not exported as image files.

The final additional screenshot request stalled and was cancelled. Its image is not counted as evidence; Studio state and console retrieval still worked afterward, and play was stopped successfully. All findings above use earlier completed captures and state/log checks.

## Next owner

Claude: prioritize BUG-01 and BUG-02, then mobile layout/control sizes, then Collection filtering. Integrate fixes in Studio and re-run the listed reproductions. Zack: physical-phone and two-player playtest after those fixes. This report proposes fixes; it does not claim they are implemented.
