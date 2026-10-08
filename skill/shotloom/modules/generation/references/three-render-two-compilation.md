# Conditional three-render-two compilation

## Activation

Load this reference only when the approved source lock records either whole-operation `appearance_family: three_render_two`, or an explicitly approved three-render-two layer/subject/interval within a `mixed_media` operation. In the mixed case, keep the root `mixed_media`, preserve other layers' contracts, and scope all clauses to the named owner. The local contract can be compiled inside the same operation and prompt; activation does not require splitting or an extra generation. Do not activate it from `anime`, `animation`, `cinematic`, `stylized`, `cyberpunk`, `2D`, `3D`, outlines or 2D effects alone.

The visual-design contract remains authoritative. Generation compiles its stable base lock plus the current shot delta; it may not redesign the look.

## Eight-dimension handoff

Account for:

1. `volume_perspective` — coherent 3D volume, foreshortening, contact and parallax;
2. `contours` — outer/interior line behavior, thickness and disappearance;
3. `shadow_bands` — banding/gradient policy, terminators, face shadows and highlights;
4. `materials` — roughness, specular policy and surface separation;
5. `texture_adhesion` — painted detail remains attached through turn, deformation and camera motion;
6. `two_d_effects` — hand-drawn/graphic/screen-space/volumetric ownership and depth/contact behavior;
7. `cadence` — holds, stepped motion, selective smoothness and camera cadence;
8. `deformation` — squash/stretch, smears, impact drawings and silhouette breaks.

For each dimension, record one internal destination: `prompt`, `reference`, `not_applicable`, `unsupported`, or `review_required`, with a short reason. Use `scripts/appearance_coverage_check.py` to catch silent loss. This coverage map stays outside prompt-only output.

For an owned layer inside mixed media, the map accounts for that local contract only. When using the checker, validate a separate local map with `appearance_family: three_render_two`, while the whole-operation packet stays `mixed_media` without a top-level `three_render_two_dimensions` payload. The map is internal accounting, not a second generation/source-lock submission; it does not alter the operation count. The existing checkers do not recursively establish layer ownership or semantic consistency, so compare the local clauses and shared boundaries back to the approved mixed contract.

## Minimum sufficient prompt

Order only the dimensions relevant to the operation:

`grounded scene/action → volume and space → line/shape → light/shadow → materials/texture → cadence/deformation → 2D-effect depth/contact → forbidden drift`

- Quiet performance prioritizes facial volume, stable contour/shadow behavior, material/texture stability and restrained cadence.
- Spatial or moving-camera work prioritizes parallax, environment shape separation and texture adhesion through motion.
- Action prioritizes readable pose/contact, timing contrast, deformation/silhouette break, effect depth and the resulting state.
- Static image generation carries static dimensions. Cadence/deformation appear only when the image is an approved animation design or keyframe authority.

Do not repeat all eight dimensions in every prompt. Do not compress the base lock into a single `three-render-two anime style` label.

## Adapter placement

### H3

- Base modes: place the stable appearance clauses near the beginning of `integrated_multimodal_description`; place action-specific cadence, deformation and effects inside the relevant shot event.
- Ref2VA: follow the [H3 adapter](minimax-h3.md): `summary` identifies the task and briefly names the appearance goal; `retention_analysis` assigns reference-owned scope. The actual stable appearance constraints occur once in the one-or-two-sentence opening of `detailed_description`, before `[Shot 1]`, followed by shot deltas in playback order. The short summary is not a second copy of the full look contract and does not replace that required opening.
- These are writing placements inside the verified H3 schema, not guarantees of style fidelity.

### Seedance

State the stable appearance lock once before the continuous timeline. Put only triggered cadence, deformation, contour/effect changes and return state inside the relevant time interval. Do not repeat the entire look at every timestamp or import H3 labels.

### Still-image platforms

Compile volume, contours, shadow, material, texture and static effect ownership. Mark cadence/deformation `not_applicable` unless the result is intentionally an animation design/keyframe authority. Use the exact image-model adapter and reference system; do not claim a static image proves motion stability.

## Transcode and repair

Every model compiles independently from the same eight-dimension base lock and shot delta. A local retry changes one principal failed dimension and preserves the other observed successes. Structural failure in volume, topology, base appearance or required action returns upstream instead of accumulating style adjectives.
