# Appearance-family routing

An appearance family selects the visual contract branch; it is not an upload category, model choice or automatic recommendation. Choose it from the user's explicit decision or an approved visual bible. If the evidence is insufficient, keep it `pending` and do not default to three-render-two.

## Maintained validation branches, not a style allowlist

- `photographic` — live-action or photographically simulated work; inspect capture behavior, anatomy/performance, physical light and materials.
- `hand_drawn_2d` — drawn or painterly 2D; inspect line/shape language, layer and paint behavior, limited-animation intent and deformation.
- `standard_3d` — 3D-led rendering without a required 2D-appearance contract; inspect volume, rig/deformation, physical or stylized material response and light.
- `three_render_two` — 3D volume rendered toward a controlled 2D appearance; load [three-render-two.md](three-render-two.md).
- `stop_motion` — physical or simulated material animation; inspect material persistence, replacement cadence, contact and scale.
- `motion_graphics` — graphic information and type-led motion; inspect hierarchy, typography, interpolation, timing and legibility.
- `mixed_media` — multiple owned layers or controlled sublooks; inspect layer ownership, boundaries, retained anchors and return rules.
- `other` — an explicit project-specific contract that does not fit the maintained branches.

These are schema routing keys, not the complete set of permitted visual styles. Preserve a custom style's actual name, visible rules and approved references in `final_appearance` and `family_specific_contract` under `other`; do not rename the aesthetic to an existing house style just to pass validation. A style can also use a maintained branch when its observable contract genuinely fits. No model is guaranteed to reproduce every style merely because the contract can represent it.

Do not infer production technique, the correct branch or a model from a style name alone. Watercolor, ink wash, pixel art, collage, clay, flat vector or an unnamed custom look are examples, not extra mandatory branches. Specific approved descriptions can resolve the branch without another question; ask only when a missing distinction materially changes the work. An unknown label with a clear contract is different from an unspecified look.

## Open appearance contract

Reuse the relevant decisions in the existing visual bible or local brief; do not introduce another compulsory form. Define only what matters:

- visible shape/edge/line treatment, including an explicit absence of contours when intended;
- surface/paint/material and light behavior, including approved flatness, abstraction or nonphysical relationships;
- spatial representation and the camera/layer behavior it permits;
- cadence, deformation and performance language, including authorized holds, stepping, smears or shape replacement;
- what must persist, what may vary, forbidden drift and how the actual sequence will be judged.

Required family fields describe decisions, not compulsory effects: `line_language` may specify no fixed outline, `space_and_perspective` may specify flat overlap without lens parallax, and a valid cadence may be deliberately stepped. Preserve them as meaningful descriptions rather than empty values. Visual style does not invent story physics, change character identity, remove a required contact/response or replace the director's intent.

For mixed media, assign look and motion rules to actual layers/subjects or bounded intervals, with ownership, interfaces/occlusion, retained anchors and transitions/return when applicable. Do not average all looks or demand a return from a permanent composite. If an explicitly approved local contract is three-render-two, its rules stay scoped there: the whole-work family remains `mixed_media`, and the top-level specialized payload must not leak to other layers. The [compiler](../../generation/references/three-render-two-compilation.md) may supply owner-specific clauses inside the same operation; no production split or extra generation is required merely to activate local rules. A separately justified and authorized sub-operation may instead use its own approved family. Nested/layer semantics require review; the current structural validator does not validate every nested contract.

This is the shared activation authority for visual guidance and every image/video adapter: whole-operation `three_render_two` activates the whole-work branch; explicitly approved local three-render-two within `mixed_media` activates only that named layer/subject/interval. Adapters change syntax, not this scope. A request to diagnose an existing result may load relevant guidance without approving its look for future production. Explicit user selection is sufficient authority for a proposed design; formal production still requires the existing locks and permissions.

`anime`, `animation`, `cinematic`, `stylized`, `cyberpunk`, `2D` and `3D` alone are too broad to choose a family. Ask or preserve `pending` when the distinction materially affects design; do not silently route `anime` to three-render-two.

## Isolation rule

Family-specific fields are conditional:

- photographic work is not forced to use contour, cel-shadow or impact-drawing rules;
- hand-drawn 2D is not forced to maintain 3D parallax, rig behavior or 3D materials;
- standard 3D is not automatically cel-shaded;
- stop-motion and motion graphics keep their own material and timing contracts;
- mixed media states which layer owns each behavior instead of averaging all branches.

Controlled sublooks may activate a different family for a bounded segment only when entry, retained anchors, ownership and return logic are explicit.

Style changes invalidate only affected appearance assumptions and evidence reuse. Whether the model should change is a separate [task-based selection](../../generation/references/video-model-selection.md) decision, not a consequence of changing a style label. Carry these appearance decisions through the source lock to model-native compilation and actual-media review.
