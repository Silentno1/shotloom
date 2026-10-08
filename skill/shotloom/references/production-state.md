# Production state

## File-backed mode

Use the user's authorized project location and existing conventions under [environment](environment.md). Keep one current authority, stable IDs and versioned records. Do not duplicate source-of-truth files across five modules. The optional [continuity ledger](../modules/review-continuity/references/continuity-ledger.md) implements immutable take records and dependency-aware recomputation.

## Conversation-only mode

Carry the same facts in copyable Markdown: project/work/script version, method ID/version, appearance version, assets/roles, shots and active takes, observed entering/ending state, evidence, pending dependencies and next task. State that persistence depends on retaining and returning the record. Manually compare dependencies; without tools do not claim calculated hashes or durable saves.

## Stable identifiers

Use stable project, scene, shot, take, asset, event and task IDs. A new file or repair version receives a new take/evidence binding; a mutable filename is not content identity. Keep story order separate from presentation order and separate subjective contexts when needed.

## State transition rules

Separate these dimensions; do not use a repair instruction as a take lifecycle state:

- Take lifecycle: candidate, accepted or rejected. A previous accepted record may be superseded by the active pointer without erasing its history.
- Review recommendation: retain, repair then review, regenerate affected unit or unverified.
- Dependency validity: current or stale, derived from the entering baseline and affected locks.
- Canon effect: update, one-shot-exception or no-change.
- Edit selection: eligible source, selected fragments, and actual cut/version/event dispositions.

A retain recommendation is not user acceptance. A repaired file stays candidate until reviewed and explicitly accepted. Only an active, accepted, dependency-valid take with update effect propagates its observed endpoint. Rejected/candidate media and local exceptions never become reference authority.

Replacing an earlier accepted take recomputes story state and marks affected later takes stale. Do not accept a dependent take against an incomplete baseline. Re-review, replace, or reuse the unchanged old acceptance only after exact-baseline restoration and the ledger's evidence conditions. Narrow dependencies require real scoped review, not a bypass.

Withdrawal, story-order changes, dreams/flashbacks and selected-cut changes follow [narrative contexts](../modules/review-continuity/references/narrative-contexts.md). Editing proposes a state/event delta; review and user acceptance authorize it. An omitted depiction does not automatically erase the event.

## Existing records

The former alpha's keep/re-roll/local-edit words were decisions, not equivalent lifecycle states. Preserve those historical notes and source evidence. Map only with explicit review and authorization; do not automatically turn an old keep note into an accepted, hash-bound ledger record. Imported examples remain fictional demonstrations, not real production evidence.
