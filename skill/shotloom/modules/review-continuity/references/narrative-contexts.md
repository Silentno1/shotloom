# Narrative contexts and selected-cut continuity

Use for nonlinear/subjective material or when the edit changes which source events are retained. A simple continuous shot can retain the existing ledger unchanged. Director owns [narrative-time intent](../../director/references/narrative-time.md); review owns observed evidence and accepted state, not new plot decisions.

## Separate state layers without changing existing ledgers silently

`continuity_state.py` remains a single-context ledger ordered by story sequence, not display order. For material nonlinear work, use separate authorized ledger files per context (e.g. objective story, a specific dream/account or an unresolved version). Record context identity, story-time interval, fact/subjective/uncertain status and entry baseline source in the existing project event map. Never send a dream's damage/ownership patch to objective current state.

A factual flashback belongs at its actual story position in the objective ledger when that chronology is established; its presentation order is separate. If the same event is shown again, map both presentations to one event instead of applying the state change twice. Character knowledge and audience knowledge are separate fields/maps: revealing an event later does not mean it happened later or that every character learned it.

Do not copy current present-day state backwards as a flashback baseline. Establish an authoritative earlier baseline, or mark it unresolved. Each independent context records its own approved base state/registry and provenance. Cross-context promotion needs explicit story authority and evidence review; no automatic merge of alternative histories. This workflow uses existing schema-2 files, not an undocumented multi-timeline capability. Old records stay in place until a specifically authorized migration is reviewed.

## Accepted source versus selected edit

Source acceptance says which take/range is eligible. A cut manifest says what was selected. Reconcile material story events separately from pixel inclusion:

- Bind cut version/hash, fragment ID, source hash/take ID, actual source in/out, presentation position and any retime to stable event/context IDs.
- For each affected event, state `shown`, `implied`, `omitted_but_retained`, `removed_by_approved_story_change` or `unresolved`, with observed support and authority. These are semantic findings, not automatically derived by overlap arithmetic.
- If a prop transfer is cut away but approved before/after evidence still establishes it, retain the event with its ellipsis basis. If the only evidence is lost and the result no longer communicates what is needed, mark the edit unresolved; do not blindly keep the full-source endpoint or automatically undo the transfer.
- Reordering presentation does not resequence objective chronology. Repeated footage does not repeat the event. Splitting one source into fragments does not apply its full endpoint to every fragment.

The editor proposes affected events, retained evidence, changed endpoints and dependencies. Review inspects the actual selected cut, obtains/reuses version-specific acceptance and applies any authorized continuity change. Retained events with unchanged valid evidence need no redundant take rewrite. Changed endpoints use a new accepted take/selection record with source/cut provenance; acceptance of the original full clip alone is insufficient.

Use `scripts/selection_manifest_check.py` for deterministic manifest structure and change detection. It hashes the normalized selection snapshot, checks evidence/status partitions and names changed event claims; it cannot determine whether an implication is artistically clear or validate source media/authority authenticity. `unresolved` is non-passing. Bind re-review to its fingerprint and actual cut, never merely to a mutable filename. Preserve the manifest/EDL in the authorized edit location; maintenance handoffs still follow the user-selected storage policy.

The checker accepts `cut_version`, `cut_file`, `cut_sha256`, `time_origin`, `fragments` and `events`. Each fragment has `id`, `take_id`, `source_file`, `source_sha256`, `source_in/out`, `timeline_in/out` (finite seconds, out exclusive) and `time_mapping` (normal speed or a reference to the actual retime map). Each event has `id`, `context_id`, `story_position`, `status`, `fragment_ids`, `evidence`, `authority_source`, and `approval_source` for approved removal. Shown events need selected fragment evidence; inferred/retained events need their actual supporting basis, not fabricated fragment IDs. `--previous` compares a prior manifest and identifies changed event claims or their bound fragments, not semantic truth.

For an accepted endpoint changed by selection, the new ledger update adds `selection_provenance` with `cut_sha256`, `selection_fingerprint`, `event_ids` and `acceptance_source`. These fields bind the review to the chosen edit; the script checks shape, not the authenticity or completeness of that review. Existing full-source take records need no forced backfill. A new selection record is required only when the accepted state/evidence actually changes.

Timing has an explicit contract: `time_mapping: "normal"` (or `{"kind":"normal"}`) requires equal source/timeline duration within one microsecond. Constant retiming uses `{"kind":"constant","speed":2}` for twice-speed playback and requires source duration / speed = timeline duration. A ramp, freeze or reverse uses `{"kind":"map","reference":"retime-map-file","sha256":"<actual 64-hex hash>","source_range":[4,8],"timeline_range":[0,6]}` with ranges matching that fragment. Its actual mapping must still be inspected. Arbitrary legacy retime text returns `unverified_timing`, not a passing timing claim; unresolved story events remain separately listed. Never label a four-second source stretched to forty seconds as normal speed.

## Withdrawal, changed chronology and split/merge

Rejecting a new candidate does not withdraw an older accepted take. Use the ledger's explicit `revise` command with approval evidence and reason to deactivate an accepted shot or change story sequence indices. It preserves immutable take records, logs the edit and recomputes validity; dependent takes with changed entering state become stale. Presentation-only reordering belongs in the cut manifest, not this operation.

The revision packet includes `expected_state_hash` from `fingerprint`, `reason`, `approval_source`, optional `deactivate_shots`, and optional `sequence_indices`. The latter maps existing shot IDs to final nonnegative integer positions; final positions must be unique. A move never rewrites an accepted take's original sequence/baseline or asserts a new review. Reactivation/re-review requires a new take record; do not erase history or fake new baseline hashes to clear stale warnings.

For an authorized story-event split/merge, prepare a versioned copy of the ledger, deactivate the superseded shot IDs, then apply genuinely reviewed new event/take IDs in story order. Validate the completed copy and affected cut before atomically promoting it under the project's write authority. Keep the old version as rollback; do not expose a partially migrated ledger as current. Report stale dependencies and stop propagation until reviewed. No project data is migrated merely because this skill was upgraded.
