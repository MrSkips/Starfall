# HANDOFF.md — the shared task board (Claude ⇄ ChatGPT/Codex ⇄ Astra ⇄ Zack)

**Every agent: read this file first, and update your own section before you stop.**
Last updated: 2026-10-06 by Claude (D-028 Zack playtest fixes: corner HUD, crusher path, pet sell + Pet Fuser, plateau retune).

## 1. Rules of the road
1. **One writer per target.** Only the owner listed in §3 edits a file or system. To change someone else's file, add a request to §5 instead.
2. **Status words** (use them exactly):
   - **planned:** written down, not made
   - **produced:** the file or design exists
   - **integrated:** it's in the Roblox place
   - **verified:** tested in Studio, with the evidence named
   Never claim more than you can show.
3. **Handoffs** live in `handoffs/T-<ver>-<nn>_<topic>.md`, and the reply goes in `..._RETURN.md`. The receiver checks the real files before marking anything done.
4. **Decisions** go in `docs/DECISIONS.md`. Anything marked **Needs Zack** is not decided, so don't build on it.
5. **Studio is the live code.** Only Claude has Studio access (Studio MCP). Other agents propose code changes as files under `handoffs/`, and Claude integrates them.
6. Commit with a message that says which agent did the work.

## 2. Where the game is right now
| Area | Status | Notes |
|---|---|---|
| Core loop: meteors, carry, deposit, machines, 6 upgrades, showers, Starheart | verified (solo) | 2-player Starheart and real phones are **not** verified |
| Map (Blender `SF_Map.fbx`) | verified | Visual meshes only; collision is the old invisible greybox parts |
| Models (`SF_Models.fbx`): 4 machines, Conveyor, Bellows, Boots, pads, sign, 5 meteors, Starheart | verified | Templates in `ServerStorage.Art`; tools `ApplyMap`, `ApplyModels` |
| UI in game (HUD, Forge panel, Collection, Settings) | verified | Asteroid layout in the **lime/cyan/red reference palette** with black text outlines (D-021) |
| Sound + VFX (`StarterPlayerScripts.FX`) | verified (PC) | Music, 9 SFX, landing/payout/build effects. Zack hasn't heard the sounds yet |
| Saving progress (DataStore) | integrated | Works only in the published game or with Studio API access on; Studio test showed the offline fallback |
| Supernova, quests + daily, streaks, tier-2 upgrades + gadgets | verified (solo, Studio) | D-023 |
| Personal/shared meteors, Meteor Chute, Core Breach event + Core Egg | verified (solo, Studio) | D-025. Needs a 2+ player test: hidden meteors, shared core HP, tier fairness |
| Tutorial | verified | Coach strip (Astra fixes) |
| Offline earnings | planned | Step 3 |
| Monetization plan | **planned** | Brief T-03-01 sent; no RETURN yet |
| Pets + Stardust eggs + loop perks | verified (solo, Studio) | D-024 perks. Blender pet meshes (`art/models/SF_Pets.fbx`) wait on Zack's import, then Claude runs `ApplyPets`. Robux eggs still wait on D-020 |
| `src/` script export | **missing** | Needs Zack to save `place/StarfallForge.rbxlx` |

## 3. Owners
| Who | Owns | Does not touch |
|---|---|---|
| **Claude** | Roblox Studio place (all scripts, models, UI implementation), Blender scripts `tools/blender/*`, `docs/*` except where noted, integration and testing, `PROJECT_STATE.md`, this file's §2 | Astra's Figma file (read-only) |
| **ChatGPT / Codex** | Design briefs and brainstorms (`handoffs/*_RETURN.md`), reviews, monetization design, Figma edits **only when Zack asks** | Studio and live scripts (propose changes instead) |
| **Astra** | Art direction, concept images, Figma UI file `YsaaA8w76ZIMNpBC2cGDIs` | Code |
| **Zack** | Approvals, saving and publishing the place, uploads, playtests, relaying handoffs | — |

## 4. Task queues
### Claude (now → next)
0. **Done (D-028, verified solo in Studio):** all items from Zack's 1-hour playtest (see docs/CHANGELOG.md). Follow-ups: Blender model for the Pet Fuser (currently part-built, Tools.ApplyFuser), real-phone check of the corner HUD, re-measure pacing after the retune.
1. **Waiting:** T-03-01 RETURN (the monetization brainstorm). When it arrives, follow `handoffs/T-03-01_CLAUDE_INTEGRATION.md`:
   - write `docs/MONETIZATION.md` with an accept / revise / reject table
   - build only the launch set, with server-side receipt handling
2. **Step 3 remaining:** first-minute tutorial, offline earnings. (Saving, Supernova, quests, pets and gadgets are in: D-023.)
   - Verify saving in the published game (needs Zack to publish).
   - 2-player check: other players' pets, drones and launch pads.
3. Measure free-player pacing for real: time to buy everything and Stardust per minute. This replaces the 15–25 min guess.
4. Done: lime/cyan/red palette is applied in the game (D-021).

### ChatGPT / Codex
0. **Produced (2026-10-06, Zack requested Codex execute T-04-01):** 18 pet reference sheets + TierExamples, LineupScale, Eggs in `art/concepts/PETS/`. Notes: `handoffs/T-04-01_RETURN.md`; prompts: `handoffs/T-04-01_PROMPTS.md`. Individual sheets are 1672 × 941 (below the brief's 2048 minimum); lineup is a rough guide. No mesh/Studio integration or verification.
1. **Produce the T-03-01 RETURN.** Use the brief in `handoffs/T-03-01_chatgpt_monetization.md`, including section L (pets + eggs), and save it as `handoffs/T-03-01_RETURN.md`. The brainstorm itself has not been done yet. Only the integration brief exists.
2. Figma: keep the screens in sync with the in-game palette (D-021). Button labels are white with a black outline.
3. **Produced / verified QA evidence (2026-10-05):** Zack requested an hour playtest. About 61 minutes of Studio QA, 34 logged deposits, desktop plus iPhone/Galaxy simulation. Five confirmed findings and explicit limitations are in `handoffs/PLAYTEST_2026-10-05_RETURN.md`; console evidence is in `handoffs/PLAYTEST_2026-10-05_LOG.md`. Fixes are proposed, not integrated. Play stopped and default viewport restored; game source unchanged.

### Astra
- **T-04-01 (new):** pet model reference sheets for the 18 pets (+ tier examples, scale lineup, eggs). Brief: `handoffs/T-04-01_astra_pet_model_sheets.md`. Return images to `art/concepts/PETS/`.
- Nothing assigned. Possible next: game thumbnail and icon once the name is picked (D-013), and pet concept art after T-03-01 returns.

### Zack
- **Passes are wired (D-029).** Check the "2 Additional Pets" price (29 vs planned 299). Create the Summon Meteor Shower developer product if you want it and send the ID.
0. **Save the place now (Ctrl+S / publish):** the D-028 changes live only in the open Studio session. Then replay: Core Breach twice in one session, Pet Fuser (Forge > Pet Fuser), Sell mode in Pets.
1. Save the place to `place/StarfallForge.rbxlx` (File → Save to File As), then publish. To test saving inside Studio, turn on Game Settings → Security → Enable Studio Access to API Services.
2. Send the T-03-01 brief to ChatGPT and save its RETURN.
3. Decide the open items in §6.
4. Run the friend playtest (`versions/v01/PLAYTEST.md`) on PC and phones.

## 5. Open requests between agents
| ID | From → To | Request | Status |
|---|---|---|---|
| R-1 | Codex → Claude | Apply the lime/cyan/red palette in the game | **Done** (D-021, Zack approved) |
| R-2 | Claude → ChatGPT/Codex | In the lime/cyan palette, white button text on lime #6FFF10 (≈1.3:1 contrast) and cyan #19F0F5 (≈1.4:1) is unreadable on phones without the outline. Use near-black text #080809 on lime/cyan (≈15:1), and keep white text for red and grey | **Closed:** Zack chose white text with a black outline |
| R-3 | Claude → ChatGPT/Codex | Don't copy a specific hit game's palette 1:1. "Steal an Egg" colors make us look like a clone (ROADMAP top risk). Shift the hues so they're clearly our own (e.g. star-gold + teal + ember instead of lime + cyan + red) | **Closed:** Zack says copying the palette is fine |
| R-4 | Codex → Claude | Fix the 5 playtest bugs (handoffs/PLAYTEST_2026-10-05_RETURN.md) | **Done** (2026-10-05): all 5 fixed and re-run in Studio; see `handoffs/PLAYTEST_2026-10-05_FIXES.md`. Physical phone + 2-player still needed (Zack) |

## 6. Decisions waiting on Zack
- **D-020:** Robux eggs, yes or no. Stardust eggs are fine either way.
- **D-013:** the final game name, needed before the thumbnail, store page and launch.
- Whether the "Claude outputs/" folder should stay. It duplicates files in `art/models/`. Claude suggests ignoring it in git.

## 7. Key facts every agent should know
- **Place and Studio:** placeId 88630827996555, published privately. Studio test hook: `ServerStorage.DebugCall:Invoke(service, fn, ...)`.
- **Economy (Config):**
  - meteor base value 15 Stardust; mutations Normal ×1 / Molten ×2 / Frozen ×3 / Charged ×5 / Cosmic ×12
  - upgrades: Conveyor 40, Boots 80, Smelter 120, Bellows 250, Forge 450, Star Anvil 1,200 (total 2,140)
  - a meteor every 12 s; shower every 120 s (testing value, design is 360)
- **Hard rules for any money feature:**
  - no paid power against other players
  - paid random items only with the odds shown and a region gate
  - no dark patterns aimed at kids
  - the free path must reach Supernova
