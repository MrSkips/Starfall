# Handoff T-00-01: art-direction exploration (Claude → ChatGPT)

**Zack: how to relay this.** Copy everything inside the SEND TO CHATGPT block into a new ChatGPT chat. Attach **all your art-style reference images** and name them REF-01, REF-02, and so on, in the order you attach them. When ChatGPT replies, save its images into `art/concepts/` and paste its RETURN text into `handoffs/T-00-01_RETURN.md` (or paste it to Claude).

````text
===== SEND TO CHATGPT =====
HANDOFF
Task ID: T-00-01
From / To: Claude (integration owner) → ChatGPT
Project / Version: Starfall Forge (working title), a Roblox tycoon / v00
Parent master-prompt revision: MP-r1
Baseline commit or snapshot: "v00 docs" (no game content yet)

Goal and player-facing outcome:
Produce 3 meaningfully different art-direction mockups so Zack can pick the game's visual style. Also give one short, critical sanity check on the concept.

Context and approved decisions:
- Game: players race across a shared crater to grab falling meteors, carry them home on their heads, and drop them into forge machines (Crusher → Smelter → Forge → Star Anvil) that turn them into "Stardust" cash. Meteors roll free mutations: Normal, Molten (orange flames), Frozen (icy blue crystals), Charged (yellow lightning), Cosmic (purple/teal galaxy swirl). Every 6 minutes there's a server-wide meteor shower, and huge "Starheart" meteors need 2 players to carry.
- Platform: Roblox, PC and mobile equally. All ages. Default Roblox blocky avatars, third-person camera about 15–25 studs behind and slightly above.
- All in-game assets will be AI-generated 3D (Roblox mesh generation plus procedural parts), so the style must be achievable with chunky, bevelled, low-to-mid detail shapes, solid or simple-gradient materials, and glow and particles. No photoreal or high-frequency texture detail.

Inputs and attachments:
REF-01… (Zack's style references). Base every direction on them. Don't copy any distinctive character, logo, or environment from them.

Owned files / nodes / assets: art/concepts/CON-01..CON-03 (new). Nothing else.
Allowed edits and excluded scope: Images and written analysis only. No code. Don't design UI screens yet.

Implementation requirements:
1. First, describe what you actually SEE in each reference (shape language, proportions, detail density, palette, contrast, lighting, materials, mood). Keep that separate from your interpretation.
2. Generate 3 images, each a different interpretation grounded in the references:
   CON-01, CON-02, CON-03: an IN-GAME gameplay view at the real camera angle (third-person behind a blocky Roblox-style avatar carrying a glowing meteor chunk overhead, walking up a ramp from a crater toward their plot with forge machines; other players and 2–3 meteors visible; one meteor streaking in). 16:9, 1536×864 or similar.
   For each, state: name of the direction, palette (5–7 hex codes), materials, lighting and time of day, how mutation rarity reads, what makes it feasible for AI 3D on mobile, and its risks.
3. Concept sanity check (≤ 150 words): the biggest weakness of this concept, one change you'd make, and whether anything reads as a clone of an existing Roblox hit.

Acceptance criteria:
- 3 images that differ clearly in direction (not just recolors), all at gameplay camera angle with the meteor and forge readable.
- Each traceable to specific REF IDs.
- Hex palettes provided. Everything labeled as concept reference, not a game asset.

Verification to perform: Look at each generated image before returning it, and say if anything came out wrong (text artifacts, non-Roblox avatars, unreadable meteor).
Known limitations / uncertainties: Perspective images don't define real dimensions. Claude will build measured geometry separately.

Return format and next recipient: Reply using this exact format, and Zack will relay it to Claude:
RETURN
Task ID / Version / Baseline: T-00-01 / v00 / v00 docs
Status: completed | partial | blocked | needs decision
Summary of actual result:
Reference observations (per REF):
Directions (CON-01..03: name, palette hex, materials, lighting, rarity readability, feasibility, risks):
Concept sanity check:
Validation performed and evidence:
Validation not performed:
Issues / assumptions / remaining work:
Next action and owner: Zack picks a direction (or a mix) → Claude writes ART_BIBLE.md
===== END =====
````
