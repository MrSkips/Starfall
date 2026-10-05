# T-03-01 — Claude's monetization integration brief

From: Zack + Codex
To: Claude, integration owner
Project: Starfall Forge / v04 planning
Companion input: handoffs/T-03-01_chatgpt_monetization.md
Expected brainstorm result: handoffs/T-03-01_RETURN.md

## Purpose

When the monetization brainstorm arrives, turn it into a small, measurable launch implementation. Treat its prices, conversion estimates, benefits, and UI proposals as hypotheses. Compare them with the live game before building. This brief does not claim that the brainstorm, product IDs, or policy checks are already complete.

## 1. Reconcile the real game first

Read PROJECT_STATE.md, docs/DECISIONS.md, docs/GAME_DESIGN.md, docs/TECHNICAL_ARCHITECTURE.md, docs/UI.md, the active version prompt, and the actual Studio scripts. The repository currently describes v01, while the monetization handoff plans v04 and lists several future systems. Record what exists, what is planned, and what each paid benefit depends on. Check that the place is saved and exported before making changes.

Measure free-player completion time, Stardust income, machine throughput, queue occupancy, meteor pickup contention, and time to the first Supernova. Do not use the handoff's 15–25 minute estimate as a measured baseline.

## 2. Review every proposed item

Create docs/MONETIZATION.md with a decision table:

Item | Proposed price | Exact benefit | Required system | Accept / Revise / Reject / Defer | Reason | Test

Use the brainstorm's ordered launch set as the starting point. Prioritize cosmetics, visible plot personalization, and benefits confined to the player's own forge. Defer products whose delivery depends on unbuilt persistence, Supernova, subscriptions, advertising, or gifting infrastructure.

Resolve these specific conflicts before implementation:

- **Paid carry speed:** faster trips can improve access to shared meteors. Evaluate the whole collection loop, not just walking while loaded. Replace with a cosmetic boot effect or a benefit confined to the forge if it harms free players.
- **Rare-meteor radar:** paid information can confer a shared-crater advantage. A safer version is free warning information for everyone, with paid cosmetic marker styling.
- **Paid luck:** a permanent luck purchase can still affect subsequent random rewards. Calling the purchase deterministic does not settle either fairness or paid-random-item policy. Prefer a fixed, disclosed reward or cosmetic alternative; verify the actual mechanics against current official rules.
- **Plot drone:** define its collection boundary and resource source. It must not reach into the shared crater or create an indirect pickup advantage.
- **Starter currency:** 2,000 Stardust nearly covers the listed 2,140-Stardust upgrade path. Tune against the measured economy so it does not erase the first session's progression.
- **Summoned events:** define cooldowns, live-meteor limits, queueing and reward access. Do not charge for an event that cannot actually run.
- **Multipliers:** specify how pass, VIP, potion and Supernova bonuses combine. Test the combined result and free-versus-paid pacing.

Check relevant current Roblox documentation before labeling any item compliant. Keep unresolved policy, availability and eligibility questions marked VERIFY. If a launch item fails a hard rule in T-03-01, revise or exclude it.

## 3. Build a concrete launch specification

For each selected item, record its platform product ID, type, whole-Robux price, benefit, duration, stacking rule, persistence, rebirth behavior, store placement and delivery path. Missing IDs should leave that purchase disabled and clearly pending configuration.

Keep gameplay unchanged by client-side price or entitlement edits. Grant paid benefits on the server using authoritative ownership or purchase records. Repeatable purchases need durable receipt tracking and idempotent delivery: replaying the same transaction must not grant the reward twice. Persist successful fulfillment before acknowledging completion. Follow the current official API contract for retries and unavailable data.

Do not grant a repeatable purchase solely because the client reports that a purchase prompt closed successfully. Restore permanent entitlements on rejoin. Keep cosmetic selections separate from ownership. Calculate displayed currency-pack rewards on the server and disclose the amount before purchase; ensure delivery matches that amount.

Specify potion behavior across disconnects, server changes and Supernova. A product should not silently expire or lose value because these cases were left undefined.

## 4. Implement the store and offer timing

Use the game's current approved Figma direction. The latest UI revision matches the reference video's lime-green, cyan, red, dark-gray and white palette. Confirm docs/UI.md reflects that revision before translating the store.

Show the exact Robux price, permanent or temporary status, and a short concrete benefit. Use a player tap to open a native purchase prompt. Make close/back controls obvious on mobile. Keep unsolicited offers out of meteor carrying and cooperative Starheart interactions.

Use the brainstorm's frequency caps, plus a dismissal cooldown. Cosmetic previews and useful forge upgrades should lead the store. Avoid fake urgency, paid random rewards, confusing currency conversions and pressure copy. Any planned first-purchase offer needs explicit eligibility and persistent one-time enforcement.

## 5. Test and measure before launch

Add cases to docs/TEST_PLAN.md for purchase success, cancellation, platform failure, duplicate receipts, persistence failure, disconnect during fulfillment, rejoin restoration, potion stacking, rebirth, and invalid client requests. Verify every selected item on both PC and mobile.

Run a free-versus-paid multiplayer check: no paid item should claim, reveal preferentially, remove, or monopolize shared resources in a way that worsens the free player's experience. Confirm a free player can reach Supernova.

Log offer shown, store opened, item viewed, purchase prompt requested, authoritative purchase fulfilled, delivery failed/retried, and benefit used. Keep currency payouts and transaction fulfillment distinct. Start price tests only after delivery works reliably and enough data exists; do not report assumption-based revenue as measured performance.

## Claude's return to Zack

Return: selected launch catalog and exact effects; revised/rejected ideas with reasons; implementation files and configured/missing product IDs; test evidence; measured free/paid pacing; remaining VERIFY items; and the next concrete action. Update PROJECT_STATE.md and docs/CHANGELOG.md to match the work actually completed.

Do not implement the whole brainstorm at once. Finish the selected launch set, then use real retention and purchase data to choose the next additions.
