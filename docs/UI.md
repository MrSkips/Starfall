# UI: Figma → Roblox mapping (rev 1, 2026-10-05)

Figma file: **Starfall Forge – UI**, https://www.figma.com/design/epTn2brL2LP9N8DjjV7YNk (owner: Claude is the only writer; Astra reviews screenshots).
Pages: Foundations (variables and styles) · Components · Screens (HUD Desktop 1920×1080, HUD Mobile 844×390, Shop Desktop, Shop Mobile, Codex, Settings).
Note: the Figma backdrops are a hand-drawn stand-in. Uploading the CON-01 image is blocked by the network proxy, so drag `art/concepts/CON-01/CON-01-concept-reference.png` onto the "Backdrop" layers by hand if wanted.

## Tokens (Figma variables → `StarterPlayerScripts.UI.Kit`)
| Figma | Roblox (Kit) |
|---|---|
| SF Color/surface/cream #FFF0CF, navy #26384D, accent/orange #F2A348, gold #FFC83D, state/success #46BFB2, disabled #B9B3A6, mutation/* | `Kit.C.*`, `Kit.Mutation.*` |
| radius sm/md/lg 10/14/20 · stroke/ui 3 | `Kit.R.*` · `Kit.STROKE` (UIStroke, Border mode) |
| Text: Display/L Fredoka One 32, Title 24, Label 18, Body Nunito ExtraBold 16, Caption Nunito Bold 13 | `Kit.T.*` (FredokaOne and Nunito FontFace; Label/Body/Caption are +2px in-game for phone readability) |
| Effect "Toy shadow" (navy, y+4, no blur) | `Kit.shadowed()`: navy copy frame offset 4px (Disabled buttons have 0 offset) |

## Components
| Figma component | Roblox builder | Behavior |
|---|---|---|
| CurrencyPill | ClientMain `Currency` | Under the Roblox top bar (uses `GuiService.TopbarInset`). Bumps and pops "+$N" on payout |
| EventCapsule (Countdown/Active) | ClientMain `Shower` | Reads `ReplicatedStorage` attributes ShowerAt and ShowerActive |
| IconButton | `Kit.iconButton` | Settings (top-right), panel close (44px) |
| SideButton | `Kit.sideButton` | Shop and Codex, left-middle (clear of the mobile thumbstick) |
| CarryCard (by mutation) | ClientMain `CarryCard` | Visible while the player attribute `Carrying` is set |
| DropButton (Desktop/Touch) | ClientMain `Drop` | Visible while carrying. Q / gamepad B. Touch layout sits above-left of Jump |
| Toast | ClientMain `Toast` | Notify `{kind="toast"}`, 2.5 s |
| WorldMarker | BillboardGui `DeliverMarker` | Over your Crusher intake while carrying |
| Button (Primary/Secondary/Disabled) | `Kit.button`, `Kit.setButtonVariant` | Pressed state drops onto its shadow |
| Toggle | `Kit.toggle` | Settings rows |
| PanelHeader, ShopCard, CodexRow, SettingRow | `UI.Panels` | One modal at a time. Dim backdrop or X closes it |

## Screens → behavior
- **Shop:** mirrors the purchase pads. States: Owned / Locked (shows the requirement) / Affordable (Primary) / Too expensive (Disabled). The buy button fires `Remotes.RequestPurchase(itemId)`. The server validates type, existence, rate (≤ 4/s), ownership, requirement, and funds through the same `tryBuy` path as the pads. Owned items replicate as plot attributes `Owned_<id>`.
- **Codex:** odds are computed from Config weights and always shown. Discovery = player attribute `Found_<Mutation>`, set by the server on pickup.
- **Settings (client-only):** guide beam, reduced effects (turns off meteor particles and fire), keyboard hints. Music and SFX rows come with audio.
- **Responsive:** `UIScale = clamp(viewportY/820, 0.72, 1)`. Viewport height under 600 px = compact (Shop becomes a horizontal scrolling strip).

## Verified in Studio (2026-10-05, real mouse clicks through Studio MCP)
HUD renders. The pill clears the top bar. Shop opens and shows live Owned/Locked states. A real `RequestPurchase` bought the Conveyor. A locked Star Anvil and a malformed request were both rejected. Codex shows 3 of 5 discovered with correct odds. Settings toggle flips and the panel stays open. No console errors.
**Not verified:** real phone touch, gamepad, 2-player.

## Known gaps / next
Icons are emoji placeholders; next step is replacing them with the Figma icon set uploaded as images. No open and close sounds yet. No Supernova/daily-crate screens (v03).
