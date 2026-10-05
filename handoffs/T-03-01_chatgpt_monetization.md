# Handoff T-03-01: monetization brainstorm (Claude → ChatGPT)

**Zack: how to relay this.** Copy everything inside the SEND TO CHATGPT block into a new ChatGPT chat. Attach 2–3 screenshots of the game if you have them; they're optional. When ChatGPT replies, paste its RETURN block to Claude or save it as `handoffs/T-03-01_RETURN.md`. Claude checks every idea against the real code, then builds the chosen ones in v04.

````text
===== SEND TO CHATGPT =====
HANDOFF
Task ID: T-03-01
From / To: Claude (integration owner) → ChatGPT (monetization design)
Project / Version: Starfall Forge (working title), a Roblox tycoon / planning for v04 (beta)
Owner: Zack (solo dev, $0 budget, wants Robux income)

GOAL
Design the complete monetization plan for this game. It should earn as much Robux as possible while staying fun for free players and fully compliant with Roblox rules. I want two layers:
  1. OVERT: a clear store with game passes, developer products, and bundles that players knowingly shop for.
  2. SUBTLE: placement, timing, social visibility, and the economy itself, so buying feels natural at the right moments. No dark patterns (rules below).
Give concrete Robux prices for everything, and justify every price.

THE GAME (what exists today; this is the real implemented state)
- Pitch: "Catch falling stars. Haul them home. Forge a fortune before the next shower hits."
- Audience: Roblox players aged about 9–16 plus casual older players. PC and mobile equally. Up to 8 players per server, each with a personal plot around a shared crater.
- Core loop (20–40 s): a meteor warning appears in the crater → run to it → pick it up (it sits on your head and slows you down) → carry it up a ramp to your plot → drop it in your Crusher → machines process it → you earn Stardust (the soft currency).
- Meteor mutations (free random roll, not purchasable today):
    Normal 70% ×1 · Molten 18% ×2 · Frozen 8% ×3 · Charged 3.5% ×5 · Cosmic 0.5% ×12
  Base meteor value is 15 Stardust × mutation multiplier. A meteor spawns about every 12 s (max 12 live, shared by the whole server).
- Meteor Shower: server-wide event (15 meteors over about 6 s; design target every 6 min).
- Starheart: a giant meteor during showers that needs 2 players to carry. Worth ×10, and both carriers get paid (a co-op hook).
- Plot upgrades (one-time Stardust purchases, built on pads):
    Conveyor 40 (×1.5 process speed) · Carry Boots 80 (+2 carry walk speed) · Smelter 120 · Bellows 250 · Forge 450 · Star Anvil 1,200
  Total is about 2,140 Stardust. A free player finishes all of it in roughly 15–25 minutes (estimate, not yet measured).
- Machines visibly animate. The plot has a sign with the owner's name, and other players can see your plot and what you carry.
- UI: Stardust balance, shower timer, Forge (upgrade shop) panel, Collection panel (mutations discovered), Settings.
- Planned (not built yet; you can design around them): saved progress, a first-minute tutorial, a mutation Codex, offline earnings (capped), a free daily Comet Crate (fixed reward), and **Supernova**, a rebirth that resets the plot for a permanent multiplier plus a new biome.
- Visual style: chunky toy-like "Sunlit Toy Foundry", with red enamel machines, cream trim, navy steel, and orange/teal glows.

HARD RULES (non-negotiable; each idea must pass all of them)
1. Follow Roblox's current Terms of Use, Community Standards, and monetization/advertising policies. Where a policy matters (for example paid random items, ads to under-13s, or experience subscriptions), say what you believe the current rule is, and mark it "VERIFY" if you're not certain. Don't invent policy.
2. No paid random items (no loot boxes, eggs, or gacha bought with Robux, directly or through a Robux-bought currency). Free random rolls are fine.
3. No pay-to-win against other players. Nothing paid may take meteors away from others, block them, slow them, or out-compete them in the shared crater in a way that makes free players' experience worse. Paid boosts to YOUR OWN plot and income are fine.
4. No dark patterns aimed at kids:
   - no fake countdown timers or fake scarcity
   - no "your progress will be lost" scare prompts
   - no confusing currency math
   - no pop-ups that cover gameplay or are hard to close
   - no guilt or shaming copy
   - no auto-opening of the purchase prompt without a player tap
   Real limited-time items with real end dates are allowed.
5. The game must stay fully fun and completable with no payment. A free player must be able to reach Supernova.
6. Use only Roblox-native systems: game passes, developer products, Premium Payouts / Premium benefits, private servers, experience subscriptions (VERIFY availability), and Roblox's rewarded video ads (VERIFY eligibility). No off-platform payments or links.
7. Be realistic for a $0, solo, AI-built game. Each item needs a simple implementation (no trading systems, no UGC catalog items).

PRICE ANCHORS TO START FROM (critique and adjust them; don't just accept them)
Game passes (one-time):
- 2× Stardust: 349 R$
- VIP (+10% Stardust, VIP chat tag, golden plot sign, VIP-only cosmetic trail): 249 R$
- Swift Boots (permanent +3 carry walk speed): 149 R$
- Forge Drone (a small drone on your plot that auto-collects one meteor from INSIDE your plot area every N s, never from the shared crater): 499 R$
- Meteor Radar (beam to the rarest live meteor + mutation shown on the warning marker): 199 R$
- Lucky Charm (permanent ×1.5 mutation luck on meteors YOU pick up; deterministic boost, not a random purchase): 299 R$
- Bigger Queue (machines hold +3 queued meteors): 99 R$
- Cosmetic forge skins (Neon, Gold, Candy, Galaxy): 149–399 R$ each, plus a bundle
Developer products (repeatable):
- Stardust packs scaled to the player's current income: small 49 / medium 149 / large 399 / mega 899 R$ (you decide the scaling formula, e.g. "N minutes of current income")
- 30-minute 2× Stardust potion: 79 R$
- 15-minute 2× Luck potion: 49 R$
- Instant process (finish the current machine queue now): 25 R$
- Summon Meteor Shower for the WHOLE server (a social gift; the buyer gets a shout-out banner): 199 R$
- Summon a Starheart next to your plot: 99 R$
- Starter Pack (one-time per player, high value: 2,000 Stardust + 30-min 2× potion + exclusive trail): 99 R$
Other: private servers (suggest a monthly price), Premium player perks (e.g. +10% Stardust), and a possible experience subscription ("Star Club", suggest a monthly price and perks).

WHAT TO PRODUCE
A. Monetization strategy (≤200 words): the overall philosophy, the whale / dolphin / minnow mix you're targeting, and why this game's loop suits it.
B. Full catalog table, one row per item. Columns:
   Name | Type (Game Pass / Dev Product / Bundle / Subscription / Premium / Ads / Private Server) | Price R$ | Exact effect (numbers) | Overt or Subtle | Where and when it is offered in-game | Why players buy it | Free-player impact | Policy check (pass / VERIFY + reason) | Build effort (S/M/L) | Priority (Launch / Later)
   Include the anchors above (revised) plus at least 10 NEW ideas of your own. At least 4 should be cosmetic or social-status items that other players can SEE (carry auras, meteor trail colors, plot banners, name effects, Starheart emotes, and so on).
C. Price ladder: list every price point from cheapest to most expensive. Explain the decoy/anchor logic and how the Starter Pack and the first-purchase offer lead into bigger purchases. Use Roblox-typical price points.
D. Subtle layer: 10–15 specific in-game moments and techniques, each with:
   - the trigger (e.g. "first Cosmic meteor caught", "Star Anvil just bought", "player waited 20 s for the machine queue", "shower starts", "player sees another player's golden trail")
   - what appears, and its exact UI copy (short, friendly, kid-appropriate, no pressure)
   - why it converts
   - how it respects rule 4
   Include economy tuning levers (e.g. where a natural "wait" or "grind" plateau sits that a pass relieves) without making the free path miserable.
E. First-session and first-week timeline: the minute or day each offer first appears, and the maximum number of offer impressions per session (a frequency cap).
F. Social and server-wide spending: gifting, server-wide boosts, shout-outs, and leaderboards (a "Top Supporters" board is OK only if it's opt-in and not shaming).
G. Supernova / rebirth tie-ins: what carries over, and which passes keep value across rebirths (so buying early feels safe).
H. Revenue model: a rough estimate with stated assumptions (DAU, payer conversion %, ARPPU) for 3 scenarios: 100, 1,000, and 10,000 DAU. Label it clearly as an assumption-based estimate. Mention Premium Payouts and the Robux→USD DevEx rate only if you're confident; otherwise mark it VERIFY.
I. Analytics: the 8–10 events Claude should log to measure monetization (funnel: offer shown → opened → purchased), plus the A/B tests worth running first (e.g. 2× Stardust at 299 vs 349).
J. DO-NOT list: tempting ideas you rejected, and which rule each one breaks.
K. Your top 8 "launch set" items to build first, in order, with one-line reasons.

CONSTRAINTS ON YOUR ANSWER
- Prices in Robux only (R$). Use whole numbers.
- Write all player-facing copy short enough for a phone screen (≤40 characters for buttons, ≤90 for descriptions).
- Don't claim anything is verified or measured. Separate facts about the game (given above) from your assumptions.
- If something in this brief seems like a bad idea, say so and propose the better version.

RETURN FORMAT (reply exactly in this structure; Zack will relay it to Claude):
RETURN
Task ID / Version: T-03-01 / v04 planning
Status: completed | partial | needs decision
A. Strategy:
B. Catalog table:
C. Price ladder:
D. Subtle layer:
E. Timeline + frequency caps:
F. Social spending:
G. Supernova tie-ins:
H. Revenue estimate (assumptions labeled):
I. Analytics events + A/B tests:
J. DO-NOT list:
K. Launch set (top 8, ordered):
Policy items marked VERIFY:
Open questions for Zack:
===== END =====
````
