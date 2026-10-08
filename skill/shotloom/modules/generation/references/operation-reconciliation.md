# Reconcile the intended operation with what will actually run

Use to prepare the user's verification before external submission, and after a consequential plan change. Shotloom never generates, uploads, charges credits or modifies a remote workspace. Check only available evidence; a prompt-only task delivers intended settings with unresolved bindings labeled. Do not connect to a platform to fill this checklist.

## Time and settings

Compare three separate sources when available: the source-locked plan, the final prompt and independently supplied operation readback. Verify relevant model/version/mode, duration, ratio and controls. Record whether evidence was directly observed or user-reported; do not copy planned values into an observed object. An echoed parameter is not independent readback. If access is unavailable, retain unverified status and let the user confirm their setup.

- If the prompt explicitly promises 8.4 seconds but the operation is set to 6, resolve the conflict before submitting; do not silently squeeze required action into 6 seconds.
- Normalize timestamped beats onto the **generation** time axis. The last event must fit the operation; non-overlapping shot durations must fit in total. Concurrent action, camera and sound tracks may overlap and must not be summed as sequential shots. Declare deliberate same-track overlap; do not use overlap to disguise an overlong plan.
- A 20-second sequence cannot be sent as one 15-second operation without an approved replanning decision. Conversely, an edit may use 1.5 seconds from a 5-second generation: selected edit duration is not a conflicting output setting. Keep pre/post handles explicit, and do not stretch one hit to fill the generation duration.
- Numeric fit does not prove physical/acting feasibility. Read the density, causal sequence, essential contact/response and tail state; exact fractions in prose do not guarantee precise model timing. Do not add excessive timestamps to otherwise adequate relative choreography.
- Recheck actual produced duration and content after generation; planned/saved settings are not proof of delivered media.

## Reference binding

For each platform-native label or slot, reconcile the smallest relevant manifest with the actual input: source node/file, selected candidate, immutable content version/hash when available, order/slot, primary role, allowed/forbidden transfer and approval for this production level. In a single-output source, use an explicit single-candidate identifier plus an immutable content identity, not a guessed multi-candidate index. A node name or file path alone cannot identify content that has been replaced.

Inspect the selected content, not only graph edges. Bindings may change when a node's selected image changes even if its connection and display name stay the same. A board, its selected panel and a generated recreation are different assets. Regenerated content does not inherit approval. Do not assume `image1` syntax or candidate numbering transfers between interfaces; use the active adapter's evidenced mapping.

Keep responsibilities separate: an identity image does not dictate the composition; a composition image does not supply the protagonist's face or wardrobe; whitebox motion/topology evidence does not dictate final materials. Conflicts return to the relevant authority instead of letting the latest attachment win. Missing access to the selected candidate/version is an unresolved binding, not permission to pretend it matches.

If a platform lacks a field or readback, mark it unknown and describe an available manual verification path. Do not invent APIs, manufacture a version ID or silently treat a thumbnail as full content inspection. A manual check should identify the actual screen/input/version and what was checked. Existing user authorization determines whether to pause or seek a changed control method; missing evidence never becomes a passing check.

## Semantic contradiction pass

Read the entire final prompt against its locks, including repeated multilingual/style boilerplate. Check local versus global hair/clothes, identities/counts, prop state/contact, spatial anchors, camera mechanisms, sound ownership and endpoint. Resolve an old clause that says dark hair when the approved local shot says gold hair, or fixed position plus physical dolly zoom. Do not treat every difference as a conflict: approved shot deltas, sequential phases and simultaneous independent tracks are valid. Structured checks cannot perform this interpretation.

## Optional deterministic helper

`python3 scripts/operation_reconciliation_check.py packet.json` compares a compact **video-operation** packet. Use it when a structured timing/binding plan is already useful; a simple operation may use the same checks directly without manufacturing extra files. It neither parses prose nor calls a platform. Validate source approval, platform evidence, input geometry, sound and adapter syntax with their existing gates as applicable.

Packet fields:

- `planned_settings`: object with positive numeric `duration_s`; include other consequential settings such as `model`, `mode`, `aspect_ratio` using the active adapter's normalized values. `observed_settings` is independent readback. Every planned key is compared; extra observed keys are not automatically errors.
- `readback_evidence`: nonempty trace to the actual readback, with operation identity/version or capture time. Evidence freshness/authenticity requires operator review; a nonempty string is not proof.
- Optional `prompt_duration_s`: the duration explicitly stated in the **final prompt**, or omit if none. Do not fill it merely from the plan. It must match generation duration, not the desired edit extract.
- Optional `segments`: generation-axis objects `{id, track, start_s, end_s}`. Same-track intervals cannot overlap unless both share a nonempty `overlap_group` describing an intentional overlap. Different tracks may overlap. Gaps/unused tail are allowed for holds/handles; the checker does not demand full coverage.
- `planned_references` and `observed_references`: arrays, empty when none. Each item has `label`, `slot` (positive integer), `source_id`, `candidate_id`, `content_version`. The planned item also has `primary_role`. Labels/slots are unique within each array; one content asset may intentionally fill distinct roles. Both lists describe only inputs actually sent, not every node linked for human organization. Obtain the mapping from actual platform evidence.

The helper returns `matched_structurally`, `blocked` or `unverified`; only the first means the **supplied structured fields** match. It explicitly leaves semantic correctness, approval, readback authenticity/freshness and media quality unchecked. Missing actual readback is `unverified`, not a pass. Fix a conflict in the underlying operation, re-read it, then rerun the affected checks; do not edit evidence to match the plan.
