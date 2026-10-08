# Seedream 5.0 adapter

`last_verified: 2026-08-20`

`supported_variants: Seedream 5.0 Pro and limited family-level Seedream 5.0 Lite guidance`

`capability_evidence: historical first-party snapshot; current validity must be checked when consequential`

This retained profile was not freshly verified during the 2026-10-04 public conversion. Its detailed advice targets Pro; Lite remains limited. Use the current [generation workflow](../../modules/generation/WORKFLOW.md) for authority, open appearance, reference approval and sound/media boundaries.

`workflow_evidence: production-method unless explicitly labeled otherwise`

## Sources

- [Seedream 5.0 Pro official launch](https://seed.bytedance.com/en/blog/beyond-generation-it-understands-design-introducing-seedream-5-0-pro)
- [Seedream 5.0 Lite official introduction](https://seed.bytedance.com/en/blog/deeper-thinking-more-accurate-generation-introducing-seedream-5-0-lite)

## Scope and variant gate

Use this adapter for Seedream 5.0 family image planning. Ask for the exact variant when capability details matter.

- Detailed production guidance below targets **Seedream 5.0 Pro**.
- For **Seedream 5.0 Lite**, use only family-level generation, reasoning, reference, and editing guidance supported by its own source. Do not claim Pro-only precision editing, layer separation, or production behavior for Lite.

This adapter covers character and environment assets, props, style frames, first frames, multi-image composition, and bounded image edits. It does not cover video generation.

## Verified Pro capabilities

The official Pro launch highlights:

- complex information visualization;
- interactive precision editing using point, lasso, box, sketch, color, and material controls;
- multi-image fusion;
- layer separation;
- improved realistic imagery, materials, lighting, and portrait texture;
- native multilingual input and rendering across many languages.

The same source states that finer text rendering and pixel-level editing consistency still have room to improve. Improved text capability is not deterministic accuracy.

## Decide the image job

Name one production job:

- reusable identity or wardrobe asset;
- environment or prop asset;
- look-development frame;
- exact first frame for one camera setup;
- local correction to an accepted image;
- composite layout or information image.

Do not ask one image to serve incompatible reusable-asset and shot-specific composition roles without stating the compromise.

## Compilation order

1. exact variant and image job;
2. reference map and exclusions;
3. subject count, identity, pose, blocking, and prop ownership;
4. physical camera position, direction, angle, lens behavior, and framing;
5. environment geometry and two or three validating landmarks;
6. motivated light, exposure, palette, and material behavior;
7. output-specific requirements such as clean margins, motion room, or editable surface;
8. continuity locks;
9. exclusions and review criteria.

## First frames

Create a dedicated first frame when the shot changes physical camera position, viewing direction, blocking, or required background. Hands and props must be ready for the first video action. Leave motion room in the intended direction.

A reverse angle is not "the same image from the other side." State where the camera moves and which complementary wall, opening, furniture cluster, or landmark must appear.

## Multi-image fusion

Give each input one role. State which dimensions it must not transfer. If identity, wardrobe, and environment come from different sources, keep those responsibilities separate and identify the composition owner.

For a recurring subject, separate a stable passport—approved identity views, proportions, canonical wardrobe, and prohibited redesigns—from shot-state references such as fatigue, wetness, injury, or one temporary expression.

For spatially sensitive recurring locations, use the smallest sufficient anchor set: layout or blockout, necessary fixed-asset views, useful room directions, and camera positions. These assets prove geometry; no fixed count is universal.

## Local edit

When most of an image is accepted:

1. mark the exact region using a control the active surface exposes;
2. name one change in that region;
3. preserve composition, identity, geometry, light, and unaffected pixels outside it;
4. review the edit boundary and surrounding continuity.

If the same placement or donor leakage survives two materially different prompts, change the reference set, marked region, layout source, or model instead of adding prose.

## Exact text and interfaces

Use prepared assets or post-production compositing for legal wording, prices, names, totals, UI state, and continuity-critical typography. For ordinary decorative text, inspect spelling, reading direction, hierarchy, and omissions after generation.

## Common failure diagnosis

| Symptom | First diagnostic change |
|---|---|
| identity image overwrites shot background | restrict identity to face/body and make the composition owner explicit |
| reverse angle looks mirrored | describe physical camera position and complementary landmarks |
| exact text is wrong | use a prepared insert or clean compositing surface |
| local edit changes the whole image | tighten the region and preservation list |
| crowded multi-person frame swaps people | reduce subjects, provide layout ownership, or generate controlled layers |
| wardrobe logo or print deforms | use a detail reference and local repair or replace it in post |

## Review gates

Check person count, identity, wardrobe, prop ownership, camera side, background landmarks, hands, text, lighting direction, edit boundaries, motion room, and readiness for the next video action.

## Version isolation

Do not present Pro capabilities as universal Seedream 5.0 family behavior. Do not transfer video duration, audio, extension, or reference ceilings from Seedance adapters into image work.
