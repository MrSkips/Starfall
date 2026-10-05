# Roadmap, responsibilities, costs, risks

## Responsibilities
| Who | Owns |
|---|---|
| **Claude** | Research, roadmap, canonical docs, interface contracts, **all Studio integration** (only verified Studio access), server code, greybox and procedural map, AI mesh and material generation in Studio, profiling |
| **ChatGPT** | Concept mockups and art exploration, icons and thumbnail art, UI visual design (Figma if it works, otherwise images plus specs), independent reviews of consequential designs and code, bounded client/UI code tasks |
| **Zack** | Concept and art approval, references, saving and publishing the place, uploads that need your account, purchases (none planned), playtests on real devices, relaying handoffs |

Communication: **Mode B (manual relay).** Claude writes `handoffs/<task>.md` with a "SEND TO CHATGPT" block. Zack pastes it into ChatGPT with the listed attachments. ChatGPT replies with a RETURN block. Zack saves it as `handoffs/<task>_RETURN.md` (or pastes it to Claude). The integration owner checks the real files before marking anything integrated.

## Gates
| Version | Goal (player-facing) | Gate evidence | Effort (Claude sessions / Zack time) |
|---|---|---|---|
| v00 | Direction | This doc set plus Zack's approval | 1 / 15 min |
| v01 | **Is the meteor rush fun?** Greybox: plots, meteors, carry, deposit, machines, 6 purchase pads, 1 shower, on-plot A/B toggle | Studio playtest log, 2-client test, Zack plus 2–3 friends playtest notes | 1–2 / 1 h |
| v02 | Visual vertical slice: one plot and the crater in final style, real meshes, HUD and Shop UI, effects, sound | Screenshots vs concept, device sim, perf numbers | 2–4 / 1–2 h. ChatGPT: about 8–12 images |
| v03 | MVP systems: persistence, Supernova, mutations Codex, Starheart co-op, onboarding, offline earnings, settings | Persistence tests, full first-session funnel playtest | 3–5 / 2 h |
| v04 | Beta prep: security review, multi-device, analytics, passes, thumbnails, release checklist | Test-plan pass, private beta | 2–3 / 2–3 h |
| v05+ | Evidence-driven updates: weekly shower themes, second biome | Creator Analytics | ongoing |

## Costs ($0 plan)
Roblox Studio, publishing, image and mesh upload: free (audio uploads have a free monthly quota). Studio AI generation: no stated cost (unverified quotas). Figma: student plan; AI image credits limited (unverified). **Ads and sponsored placement: deferred until revenue, and only with Zack's approval.** ChatGPT and Claude usage: your existing subscriptions, the main constraint.

## Top risks and mitigations
| Risk | Mitigation |
|---|---|
| Rush loop feels tedious | v01 A/B with fallback F. Tune distance and speed in Config |
| Looks like a "Steal a ___" clone | No stealing, a distinct theme, an honest thumbnail |
| AI art inconsistency | Art bible, reference IDs, one base rock with material variants |
| Exploits (teleport-grab, autofarm) | Server range checks, carry state on the server, rate limits |
| Usage limits on both AIs | Bounded handoffs, one review pass, docs as memory |
| No organic discovery at launch | Polish the first 60 s, co-play hooks, private beta with friends to seed D1 |
