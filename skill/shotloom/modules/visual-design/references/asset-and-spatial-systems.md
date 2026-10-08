# Asset and spatial authority

## Asset levels

- **Concept:** exploration only; cannot silently control identity or continuity.
- **Continuity candidate:** plausible and role-specific, awaiting actual inspection and approval.
- **Approved authority:** inspected, explicitly accepted and assigned one responsibility.
- **Retired/rejected:** discovery only; never auto-bound.

Discovery is not approval.

## Character package

Separate face identity, body proportions, wardrobe details and temporary visible state. A board or collage is for human overview; model inputs should be the smallest sufficient focused set. Voice identity and current voice state belong to the director/sound contract; visual design may cross-reference an approved voice asset identifier but may not redefine it.

## Reference responsibility manifest

For every approved visual reference used by generation, record source/version, approval state, one primary responsibility, optional secondary evidence, priority, allowed transfer, forbidden transfer and conflict rule. Useful responsibilities include face identity, body proportion, wardrobe construction, prop identity, location topology, composition, light, material or motion. Audio and voice references use the sound contract and the same approval discipline, not visual authority.

A reference does not control every visible field merely because it is attached. When two references compete, follow the explicit priority and owning authority; do not let a broad style or full-body board defeat a focused identity, wardrobe, topology or current-state source.

## Grid to single-shot reference

Use a multi-panel board to compare coverage, appearance or staging; it is not automatically a sequence of continuous moments or an approved identity/space authority. Each selected panel needs a declared purpose and its own continuity comparison.

Choose the operation explicitly:

- **Pixel-preserving crop:** isolate existing pixels without generation, resampling or retouching. Record the source version/hash, row/column and crop bounds. Re-encoding lossily is not lossless extraction; resizing is a separate derivative step. A crop cannot recover detail that was never present.
- **Generative extraction/recreation:** asking a model to “generate panel row X, column Y alone” creates a new candidate, even if it resembles a crop. Record parent/panel, locks and allowed changes; inspect face, costume, props, topology, framing and any new detail again. The parent board's approval does not approve invented pixels.
- **Local repair:** name the defect and change region, protect successful areas and preserve locked pose, angle, scale and contact. It is not permission to redesign the entire image.

Trace the selected single-shot version back to its parent and operation. Approval is role-specific: a board approved for composition does not confer face identity authority on its derivative. A faithful crop may reuse applicable prior evidence only when the relevant content, role and review baseline are unchanged; still verify bounds, no neighboring-panel/gutter leakage, resolution and the operation's input limits. Changed or invented content needs renewed review. Never bind an unreviewed regenerated panel as a formal reference merely because its parent was accepted.

Before generation, reconcile the selected derivative and responsibility manifest with the actual reference slots/candidates in `generation/references/operation-reconciliation.md`. A correct label in prose is not proof of a correct attachment.

## Shot-bearing references

When a reference is meant to carry a shot's composition rather than only identity/topology, evaluate the actual selected image for the director's required relationship: attention hierarchy, subject scale, access/occlusion, usable action space and relevant light/color separation. Identity correctness does not establish shot suitability. A beautiful portrait can be a poor source for a two-person handoff; a plain identity board can remain entirely valid in its identity-only role.

Distinguish what is established in the image from what must change in motion. A start frame can establish geometry but cannot prove a later reveal, reaction or camera path. If the creative carrier is absent, contradictory or unreadable, improve the scoped composition/control plan before treating it as a shot authority. Do not redesign accepted faces, clothes or locations to make it more attractive.

Choose controls by the relationship at risk: a focused composition image, sequential keyframes, a path annotation, spatial/depth or motion reference, or text-only direction where sufficient. These are alternatives, not a compulsory bundle; verify support in the selected interface. An annotation's geometry may transfer while its arrows/text must not appear in the result; a depth reference's movement may transfer without its grayscale surface. Multiple keyframes may contradict each other or overconstrain motion, so preserve explicit priorities and temporal roles. Do not assume more references improve execution.

## Scene package

For repeated or spatially sensitive locations, record local coordinates, shell, doors/windows, fixed anchors, paths, light/sound directions, axes and candidate cameras. Build only the views required by the story. A new angle must be derivable from the approved package or use a focused approved reference.

## Props and text

Record owner, count, support/contact, orientation, state, readable text and allowed changes. Precision interfaces and text receive dedicated authority and direct review.
