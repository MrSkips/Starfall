# Astra progression playtest (2026-10-06): what Claude changed

Source: Astra's 16-minute blind playtest notes (relayed by Zack). Status words per HANDOFF §1.

| # | Astra saw | Root cause | Fix | Status |
|---|---|---|---|---|
| 1 | Spawn with 0 Stardust, no obvious first action; "Ready for a meteor" and the shower countdown read as "wait" | No onboarding | New `Coach` LocalScript: 3-step strip under the shower timer (1 grab a meteor, 2 bring it to your Crusher, 3 buy your first upgrade), hides after the first purchase. Forge Activity now says "Bring a meteor here" | verified (Studio: steps advance 1→2→3→hidden) |
| 2 | Clicking / touching / E on a meteor gave no clear response | Prompt needed a 0.15 s hold; no click support | Pickup prompt is instant; clicking or tapping the meteor picks it up (ClickDetector) | verified (ClickDetector present, hold 0) |
| 3 | Depositing at the Crusher felt like guesswork | Prompt sits high on the intake | Walk-in deposit: carrying a meteor within 10 studs of YOUR Crusher drops it in | verified (Deliveries 0→1 on walk-in) |
| 4 | Sky/moon visible through a hole in the crater wall beside the ramp | Blender wall skips blocks within 13 studs of each ramp centre; the ramp is only 10.6 wide, so a ~3-stud gap per side shows the empty space under the rim grass | `Tools.BuildCliffCollision`: solid slate buttress + grass cap filling both gaps on all 8 ramps | integrated (not visually re-checked: Studio's 3D capture was blank this session) |
| 5 | Stuck against the wall at the stair edge, camera inside the avatar | Same gap: a pocket between the tall ramp side and the wall | Gap filled (above) + invisible rails along both sides of every ramp | integrated |
| 6 | Guide beam points straight at the Crusher, through the wall | Beam always aimed at the target | Beam routes via your ramp: in the crater → ramp foot; on the ramp → top/bottom; on your plot heading down → ramp top | verified (beam went to the ramp foot while carrying in the crater) |
| 7 | Pet auto-fills hands while hunting a rarer meteor | Fetch handed meteors to the player | Fetch pets now fly the meteor straight into your Crusher; hands stay free (D-024 text updated) | verified (fetch ran, hands stayed empty) |
| 8 | Pale untextured debris at the crater edge | "Rock" rubble was pale 8C96A3 SmoothPlastic | Rubble is now dark slate 5C5868 (ApplyMap palette updated too) | integrated |
| 9 | Yellow (Charged) meteor vanished before she reached it | 60 s despawn for everything | Frozen / Charged / Cosmic / Starheart last 120 s | integrated |
| 10 | Earned 42 from two deliveries vs a 250/450 next step | Base value 15 | Base meteor value 25 (first delivery now pays 25) | verified |
| 11 | Launch Pad / Supernova hidden behind menu browsing | No goal surfacing | "Next goal" chip bottom-left after the tutorial: cheapest available upgrade + what it does + progress bar, "READY - TAP TO BUY" opens it in Forge; ends on Supernova | verified |
| 12 | Reduced effects didn't tone down the bright crystals | Setting only touched meteor particles | Also cuts Bloom to 30% and turns off sun rays | integrated |
| 13 | Upgrades priced in dollars | Pad labels and a toast said "$" | Pads read "40 Stardust"; toast says "Need N Stardust" | integrated |

Not changed: competition/social (needs a 2-player test), frame rate and sound (needs a real device).
