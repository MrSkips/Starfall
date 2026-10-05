# UI: Astra UI-02 "Asteroid" → Roblox (rev 2, 2026-10-05)

**Source of truth:** Astra's Figma file **Starfall Forge / Asteroid UI**, https://www.figma.com/design/YsaaA8w76ZIMNpBC2cGDIs (pages "01 — Asteroid UI" and "03 — UI components"), plus `art/concepts/UI-02/` (18 video-pattern crops, final exports, REFERENCE-INDEX.md).
Rev 1 (the cream "toy" UI in Claude's file epTn2brL2LP9N8DjjV7YNk) is **superseded** and kept for history only.

## Tokens (read directly from Figma variables → `UI.Kit`)
space #141d2d · panel #26354a · inset #1b283b · border #53657c · cream #fff0cf · muted #b8c5d4 · orange #f5a15d · teal #64dfd1 · purple #b89bff · red #f17779 · gold #ffd671 · gap 12 · pad 20 · radius 16 · border 2px
Text: title Fredoka Bold 32 · label Fredoka Bold 22 · body Nunito Bold 16 · small Nunito Bold 13 (Roblox: FredokaOne + Nunito Bold).
Effect "Panel depth": rgba(5,10,20,0.6), y+5, no blur (Kit.panel builds it as a "Depth" frame).
Button tones: Primary orange/#141d2d text · Secondary panel/cream · Danger red · Disabled inset/muted.

## Screens → code (design units; UIScale = viewportHeight / 810 desktop or / 540 mobile)
| Figma screen / component | Roblox | Notes |
|---|---|---|
| 06 Stardust balance 193×100 @24,72 | ClientMain `Balance` | Moves below the Roblox top bar when needed; widens for big numbers |
| 11 Shower countdown 253×100 (top-centre) | `Shower` | Switches to **08 Shower active** (orange, "New meteors are landing!") during showers |
| Gear 56×52 | `IconButton_gear` → Settings | |
| 05 Navigation rail 170×139 | `NavRail` (ForgeButton, CollectionButton) | Mobile: 58×54 icon buttons (forge_cream, book_cream) |
| 17 Processing queue "FORGE ACTIVITY" 287×321 | `ForgeActivity` | One row per built stage (Crusher always). Animated from server `Notify{kind="job", startedAt, duration}`. The job's time is split across built stages. Desktop only (not in the mobile design) |
| 09 Carry and drop 335×145 | `Carry` | Icon tinted per mutation. "Drop meteor" (Q / gamepad B also work). Mobile: 300×81 card plus a separate 170×54 Drop above Jump |
| DELIVER HERE 180×63 | BillboardGui over your Crusher | |
| 18 Completion notice 287×100 | `Notice` | Payouts ("Meteor processed! +N Stardust added") and server messages |
| 03 Collection (01 Mutation cards, 02 Unknown mutation, 03 browser) | `Panels` Collection | Search box filters live. Discovery = player attribute `Found_<Mutation>` |
| 04 Forge (14 categories, 07 upgrade detail, 06 balance, 13 stages) | `Panels` Forge | Machine levels map onto Config items (below). Upgrade → `RequestPurchase` (server-validated) |
| Settings | `Panels` Settings | Not in UI-02. Built in the same language (guide beam, reduced effects) |

### Forge panel ↔ economy mapping
Crusher = Lv1 base, + Conveyor (Lv2), + Bellows (Lv3), stat = process time · Smelter / Forge / Star Anvil = build, stat = payout × · **Carry Boots added as a 5th category** (not in UI-02; it's the only upgrade that isn't a machine) · the stage strip highlights the furthest built machine.

## Deviations from 1:1 (deliberate)
1. Forge panel has a 5th category (Carry Boots).
2. Progress-bar track uses #141d2d instead of #1b283b so the bar is visible inside the #1b283b rows.
3. Charged and Cosmic mutation icons, and the per-mutation meteor tints, were drawn by Claude in Astra's style (not in UI-02).
4. Mobile joystick and jump are Roblox's native controls (the Figma circles were placeholders).
5. Panels auto-shrink to fit very short screens.

## Icons
Exported as SVG from Astra's file, rendered to 256 px PNG (`art/ui-icons/`, sources in `art/ui-icons/svg/`), bulk-uploaded by Zack, wired in `UI.Icons` (21 rbxassetid ids).

## Verified (Studio, 2026-10-05, real mouse clicks)
- **Desktop (1440×810 emulated device):** HUD, Forge panel (live Crusher Lv2, 2 → 1.3 sec, Upgrade • 250), Collection (3/5 discovered, Charged and Cosmic locked).
- **Mobile layout (small viewport):** HUD and carry card.
- No console errors. Purchases go through the validated remote.

**Not verified:** a real phone, a gamepad, and the Forge Activity animation mid-job (verified idle state only).
