# Gameplay HUD concepts

Concept references only; not implemented UI or game assets. Created with built-in image_gen, grounded in the approved CON-01 sunny toy-foundry direction.

Desktop: desktop-hud-concept.png
Mobile landscape: mobile-hud-concept.png

Both images were visually inspected. Main labels are legible and correctly spelled, overhead meteor and four machines remain readable, and the unintended pickaxe has been removed. Desktop carrying card overlaps the avatar's feet slightly. Mobile carrying card is more compact; touch control positions are illustrative and have not been tested on a device. Platform safe areas, minimum touch sizes, narrow aspect ratios and localization require implementation checks. Currency and timer values are examples. Forge and Collection buttons propose navigation entry points; their screens are not designed here. My Plot should mean navigation guidance unless teleportation is separately approved. Forge processing progress belongs in a later processing-state concept; this image shows carrying.

Palette: cream #FFF0CF, navy #26384D, orange #F2A348, teal #46BFB2 (reserved success accent).

## Exact desktop prompt

Use case: ui-mockup. Create a polished IN-GAME HUD concept for the Roblox game Starfall Forge, using the provided sunny toy-foundry gameplay image as the background edit target. Output a single 16:9 landscape image approximately 1920x1080. Concept reference only. Preserve its chunky Roblox block avatar carrying a molten meteor overhead, green cliff terraces, broad orange ramp, red and cream Crusher, Smelter, Forge and Star Anvil machines, other players and meteor streak. Remove the other player's pickaxe, their activity should be carrying meteors. Keep the gameplay scene sharp and dominant, do not blur it. This is a clean actual gameplay screen with a thoughtfully restrained HUD, not a design board, not a menu, not a promotional poster. No device frame.

UI visual language: toy-like bevelled rounded rectangular panels, warm cream faces #FFF0CF, thick deep navy #26384D outlines, small clean offset navy shadows, orange #F2A348 primary accents and teal #46BFB2 success accents. Friendly bold rounded sans-serif lettering, legible white or navy text. Simple chunky illustrated icons. Premium consistent spacing, not a crowded simulator screen. Avoid microtext, excessive gradients, rainbow buttons, sales banners or Robux prompts. Text must be crisp, spelled exactly as supplied.

Layout:
Keep upper leftmost 180x70 pixels clear for Roblox system controls.
Below that top-left safe area: compact cream currency pill, gold four-point sparkle icon, large navy "12,450" and smaller "STARDUST". No other currencies.
Top center: a modest navy outlined cream event capsule with a small meteor icon, label "METEOR SHOWER" and separate orange timer segment "02:34". It should occupy less than 25 percent screen width. Do not cover the meteor streak.
Top right: two small cream rounded square icon buttons, speaker and gear. No labels.
Left middle edge: exactly two stacked compact cream buttons, chunky forge icon labelled "Forge" and meteor book icon labelled "Collection". Leave plenty of space around them and avoid obscuring other players.
Bottom center: one compact dark navy carrying card, width approx 28 percent screen. Small orange meteor icon at left, white "MOLTEN METEOR" and cream secondary instruction "Carry to your Crusher". Small orange mutation chip labelled "Molten". The panel sits below the avatar feet, not across the torso or meteor. No inventory hotbar.
Lower right, above bottom edge: compact contextual pale cream button labelled "Drop", with a small desktop "Q" keycap. It means drop the carried meteor, not process it. Keep it secondary and smaller than the carrying card. Beside it a separate unobtrusive Home icon button labelled "My Plot". No joystick or touch jump in this desktop variant; button sizes and margins should translate to touch later.
One small world-space cream marker at the Crusher intake says "DELIVER HERE" with a simple down arrow. Marker must not hide the roller machine. No other floating text. 
Very small discreet lower-left footer "UI CONCEPT • NOT IMPLEMENTED".
Make all HUD elements consistent in corners, border thickness, icon scale and typography. Crucially preserve a large unobstructed view of the ramp, meteor and machines. Do not invent game mechanics, XP, quests, pets, energy or extra currencies.

## Exact mobile prompt

Use case: ui-mockup. Edit the supplied Starfall Forge desktop gameplay HUD concept into its MOBILE LANDSCAPE companion, single 16:9 screenshot, no device frame. Keep same chunky sunny Roblox world, overhead molten meteor, avatar, four red/cream machines, sky meteor, and cream/navy/orange HUD aesthetic. Concept reference, not implementation. Keep UI readable and intentionally sparse. Preserve exact words as follows. Top-left currency pill smaller: gold sparkle icon, "12,450", "STARDUST", leave small clear uppermost strip for platform system controls. Top-center compact "METEOR SHOWER" capsule and orange "02:34". Top-right just one small gear settings button. Left-middle two small cream buttons "Forge" and "Collection", well above movement area. Lower-left reserve a generous thumb zone with a translucent neutral circular movement joystick only; no cards in this zone. Lower-right separate translucent circular Jump button with white up arrow, placed near bottom right, and a clearly separated cream/orange pill "Drop" above and left of jump so they cannot be confused. No Q keycap anywhere. No My Plot button. Bottom-center shrink carrying status into a compact navy two-line card about 30 percent screen width: small molten meteor icon, bold "MOLTEN", smaller "Carry to Crusher". Card must sit below the avatar feet and between the thumb zones, not obscure the avatar; if needed move avatar slightly higher or expand clear ground below feet. World-space compact "DELIVER HERE" arrow above Crusher, clear of other UI. Plenty of empty central gameplay space. No microtext, no shop ads, no inventory hotbar, no extra currencies or quests. A tiny top-center secondary footer "MOBILE UI CONCEPT" may be placed below event timer. Match icon style, border thickness, bevels and rounded bold font from input. All visible text spelled correctly. Touch controls should look like functional Roblox mobile controls and fit the visual language. Keep screenshot bright, not cinematic.

