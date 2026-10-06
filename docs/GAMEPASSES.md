# Starfall Forge – Game passes (D-027 proposal, 2026-10-06)

Rules these follow (T-03-01 brief + D-006/D-020):
- No paid random items: no egg sold for Robux, and no Robux-bought currency that can buy eggs. **That rules out Stardust packs**, because Stardust buys eggs.
- No paid power over other players. Every pass boosts your own loop or is cosmetic.
- The free path still reaches Supernova and every pet.
- Prices are whole Robux. Roblox keeps 30%, so you net about 70%.

## Passes (one-time purchase)

| # | Pass | R$ | What it does in game | Code hook |
|---|------|----|----------------------|-----------|
| 1 | **2x Stardust** | 399 | Every payout ×2. Stacks with VIP, pets, streaks and Supernova. | MachineService payout multiplier |
| 2 | **VIP** | 199 | +10% payouts, gold [VIP] chat tag, a gold VIP star on your plot sign | MachineService, TextChatService tag, plot SignVisual |
| 3 | **+2 Pet Slots** | 299 | Base slots 3 → 5. The Supernova cap rises 6 → 8. | PetService slots(), PetFollow SLOTS (add 2 positions) |
| 4 | **Triple Hatch** | 249 | Hatch 3 Stardust eggs at once (you still pay 3× the Stardust); you can skip the animation. Odds unchanged. | PetService Hatch(count), Panels egg button |
| 5 | **Comet Sneakers** | 149 | +25% walk speed, +3 carry speed | PurchaseService.GetCarrySpeed, Humanoid.WalkSpeed |
| 6 | **Supernova Head Start** | 199 | After each Supernova you keep Conveyor, Smelter, Meteor Chute and Carry Boots | Supernova handler in Main |
| 7 | **Plot Themes** (cosmetic) | 99 | 4 colour sets for belts, floor trim and silo (Ember, Frost, Nebula, Gold) | ApplyLine colour swap on your plot |
| 8 | **Lucky Sky** *(needs a check, see note)* | 349 | Your personal meteors roll a mutation 1.5× as often. The odds table in the Codex shows both rates. | MeteorService personal spawn roll |

Note on Lucky Sky: it boosts the odds of free drops, so it is not a paid random item. Still, list both odds openly and confirm against current Roblox policy before shipping. Drop it if in doubt.

## Developer product (repeatable)
| Product | R$ | Effect |
|---------|----|--------|
| **Summon Meteor Shower** | 49 | Starts a shower for the whole server right away (if none is running and no Core Breach is active). Everyone can race for it, and the buyer is named in the banner. 10-minute server cooldown. |

## Not doing
- Stardust packs: they buy eggs, which breaks the "no Robux-bought currency for eggs" rule.
- Robux eggs: D-020 is still open. Under the brief they need odds shown, a PolicyService region gate, and every pet obtainable for free.
- Anything that lowers other players' meteors or core damage.

## Icons
- Figma (editable components): https://www.figma.com/design/vQOPtmDmT77EdE0azufoCv
- 512×512 PNGs ready to upload: `art/gamepass_icons/` (01_2x_Stardust … 09_Summon_Meteor_Shower). Roblox shows pass icons circle-cropped, so the key art sits in the centre.
- `10_Shop_Button.png`: in-game HUD button that opens the store. Generic bag + star, no Roblox logo. Claude uploads it with the store UI.

## Creating them (Creator Hub)
1. Go to create.roblox.com → Creations → Starfall Forge → **Monetization → Passes → Create a Pass**.
2. Upload a 512×512 icon, then add the name and the description below. Click **Create Pass**.
3. Open the pass → **Sales** → turn on "Item for Sale" → enter the price → Save.
4. Copy each pass ID (the number in the URL) into `Config.GamePasses` (Claude wires them).
5. For the developer product, go to Monetization → **Developer Products** → Create, then copy its ID.

## Store descriptions (copy-paste)
- 2x Stardust: "Double every Stardust payout from your forge, forever."
- VIP: "+10% Stardust, a gold VIP chat tag and a VIP star on your plot."
- +2 Pet Slots: "Bring 2 more pets along. Raises the max to 8 after Supernova."
- Triple Hatch: "Open 3 eggs at once (Stardust cost x3). Same odds as single hatches."
- Comet Sneakers: "Run 25% faster and carry meteors quicker."
- Supernova Head Start: "Keep your Conveyor, Smelter, Meteor Chute and Carry Boots after every Supernova."
- Plot Themes: "Recolour your production line: Ember, Frost, Nebula or Gold."
- Summon Meteor Shower: "Call a meteor shower for the whole server right now!"


## Live IDs + status (D-029, 2026-10-06)
Wired in `Config.GamePasses` (MonetizationService). Ownership is checked on join and granted instantly after an in-game purchase. Verified in Studio (the place owner owns every pass automatically, so each effect was checked with that).
| Pass | ID | Price now | Notes |
|---|---|---|---|
| 2x Stardust | 2006391828 | 399 | payout x2 |
| VIP | 2006619881 | 199 | +10% payout, [VIP] chat tag (ChatTags), star over the plot sign |
| 2 Additional Pets | 2008934412 | **29** | plan said 299; check this price |
| Triple Hatch | 2007039848 | 349 | "x3" button on each egg (opens the Shop without the pass) |
| Comet Sneakers | 2004921816 | 149 | walk x1.25, +3 carry speed |
| Supernova Head Start | 2006727844 | 199 | keeps Conveyor, Smelter, Meteor Chute, Carry Boots |
| Special Plot Themes | 2006355827 | 99 | picker in the Shop card (Default/Ember/Frost/Nebula/Gold), saved in the profile |
| Lucky Sky | 2006961749 | 349 | non-Normal weights x1.5 on your personal rolls; both odds tables shown on the card |
Managed pricing is on, so the shop reads prices live from Roblox. Summon Meteor Shower (developer product) is not created yet; send its ID to wire it.
