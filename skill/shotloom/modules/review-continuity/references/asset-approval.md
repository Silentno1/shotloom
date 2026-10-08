# Asset discovery and approval

## Three operating levels

- **Concept:** broad exploration; no continuity authority required.
- **Continuity:** recurring identity/location/prop; focused references and approval required.
- **Formal production:** release-bound work; provenance, version, role, actual inspection and change control required.

Choose the lightest level that matches risk. Do not force formal-production paperwork onto concept tests.

Pass the selected level downstream as `production_level: concept | continuity | formal`. Concept may retain explicitly pending candidates. Continuity and formal generation require inspected, approved authorities for every recurring hard-continuity role; do not let a filename hint or pending candidate satisfy that gate.

## Asset state

`discovered -> inspected -> candidate -> approved -> retired`

Automatic search can only create `discovered`. File name, modification date, thumbnail or semantic similarity cannot approve an asset. Record actual path, version/hash, media type, assigned role, allowed transfer, forbidden transfer, inspection result and approver.

Use the smallest sufficient reference set. Missing exact authority is reported as missing; a vaguely related image cannot silently cover it.

For an approved generation manifest, assign each input one primary responsibility plus explicit priority and conflict handling. A reference may provide secondary evidence, but attachment alone never grants authority over all fields. When roles overlap without a declared priority, stop binding and resolve the authority conflict before generation.

## Derived images and selected candidates

For a grid-derived frame, identify the parent version/panel and whether it was cropped, resized, generated anew or repaired. Compare the actual derivative with its intended role and locks: framing, face/body, wardrobe, prop/contact, topology and new details as applicable. A generative extraction is a new candidate, not a lossless crop. Approval of a board's composition does not approve every panel as identity or continuity authority. Reuse prior evidence for unchanged pixels/roles only when sufficient; inspect changed content and cropping boundaries without automatically redoing unrelated checks.

Approval applies to the exact selected asset version, not merely a canvas node that can hold several candidates. Before an approved binding is handed onward, identify the selected candidate/content and slot. A new selection or replacement invalidates the affected binding check even if the node name and prompt label remain unchanged. Check role leakage (such as a composition image overriding face/clothes, or a whitebox motion reference dictating final materials) against the manifest. Lack of access to actual selected content is unverified, not approved.

When the assigned role includes shot composition, distinguish continuity approval from shot suitability using [shot-bearing references](../../visual-design/references/asset-and-spatial-systems.md#shot-bearing-references). Compare the actual image with the required relationship and visibility condition; correct faces and clothes alone are insufficient. An identity-only board need not pass this composition test. Report the specific lost/obscured relationship instead of an unexplained aesthetic score; reference-image approval still does not approve the resulting motion.
