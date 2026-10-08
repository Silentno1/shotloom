# Production method and final appearance

## Production method

Describe the actual or simulated pipeline, for example:

- live-action/photographic generation;
- hand-drawn or painterly 2D animation;
- vector, cut-out, motion-graphic or collage animation;
- 3D character/environment animation with PBR, NPR or cel shading;
- stop-motion or material simulation;
- mixed pipeline with explicit ownership by layer.

Do not compress these into a platform menu. The method controls spatial volume, deformation, materials, camera freedom, animation cadence and revision cost.

## Final visual appearance

Record an explicit `appearance_family` using [appearance-family-routing.md](appearance-family-routing.md). The family selects conditional validation; it does not choose a generation model or distribution category.

Lock what the audience sees:

```text
silhouette and proportions
line language
shape simplification
color hierarchy
light and shadow structure
material response
surface texture behavior
space and perspective
motion cadence and holds
deformation/smear language
VFX and compositing ownership
text/UI language
forbidden drift
```

The list above is a design inventory, not a demand that every medium use the same fields. Apply only the common fields and the selected family's contract. Keep unknown items open rather than borrowing requirements from another family.

For a serialized contract, set `media_type` to `image` or `video`; omitted legacy contracts retain video requirements. A static image does not require motion cadence, animation replacement/interpolation timing, deformation/rig motion or VFX compositing fields merely to pass. If the still explicitly uses VFX, set `vfx_present: true` and describe compositing ownership; otherwise omit irrelevant fields. An animation-design reference may voluntarily retain motion intentions but cannot validate their execution.

## Upload category

Inspect the actual current platform. Select only among the displayed categories. Record the category and date separately from production method and appearance. Do not hard-code “photoreal/2D/3D” as a universal platform taxonomy.

When `upload_category` is included in the visual contract, record `upload_platform`, `category_options_observed` and `category_verification_source` with dated interface/source evidence. Independently established method and category labels may be identical; differing strings alone are not evidence of independent decisions. Omit distribution fields when distribution is not in scope.

## Cyberpunk boundary

Cyberpunk requires systemic content such as high technology under unequal living conditions, commodified identity/body/memory, corporate or algorithmic power, surveillance, labor and social consequences. It can be rendered as 2D, 3D, photoreal, collage or mixed media.
