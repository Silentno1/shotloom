# Chronology-safe continuity ledger

The ledger stores immutable take records and derives canon only from active, dependency-valid accepted takes sorted by `sequence_index`.

## Invariants

- Candidate/rejected records may be stored but cannot apply `canon_patch` or `registry_patch`.
- Only an accepted take with `canon_effect: update` changes derived canon.
- `one-shot-exception` and `no-change` do not propagate state.
- Accepting a replacement changes only the shot's active-take pointer; it does not mutate the earlier take record.
- Every accepted take records the entering registry/state hashes against which it was reviewed. The default is a conservative full baseline. When review can name exact dependencies, `depends_on` may list `state.*` or `registry.*` paths so unrelated upstream changes do not force unnecessary re-review. A changed baseline makes the later take `stale` and stops its canon contribution; use the resolution policy below.
- `last_accepted_shot` means the highest dependency-valid active accepted sequence index, not the most recently reviewed file; stale takes are excluded.
- Shot sequence index is stable during take updates. Authorized story-order revisions use the separate `revise` operation; presentation-order changes do not resequence canon. See [narrative-contexts.md](narrative-contexts.md) for contexts, selected-cut reconciliation, withdrawal and migration.

## Update shape

```json
{
  "shot_id": "S010",
  "sequence_index": 10,
  "take_id": "take-03",
  "status": "accepted",
  "canon_effect": "update",
  "canon_patch": {"props": {"key": {"owner": "B"}}},
  "registry_patch": {},
  "next_requirements": {},
  "exceptions": []
}
```

`canon_patch` describes the accepted observed endpoint delta, not the intended prompt. `accepted_against` is calculated by the ledger rather than supplied as a creative claim. The script writes atomically and validates after recomputation. Check `stale_takes` before generating or editing later material.

For continuous performance, retain only material observed carryover: attention target, posture/contact, an unfinished gesture, visible breath activity or persistent wetness when needed by the next shot. Use existing project state paths and dependency rules; do not create a universal emotion schema or store an inferred hidden feeling as observed fact. A cut does not automatically reset the body or expression, but a motivated time jump or changed stimulus may alter them.

Legacy accepted records without `accepted_against` are reported stale rather than silently trusted. Re-review or replace them to establish a new baseline; do not fabricate hashes merely to clear the warning.

## Dependency resolution and exact-baseline restoration

New downstream acceptance cannot skip unresolved earlier active takes and treat the shortened derived state as complete. Resolve the stale predecessors in story order, then accept the dependent take. Candidate/rejected records may still be stored. Reviewing the stale shot itself is allowed when its own predecessors are resolved.

For genuinely independent downstream work, explicit `depends_on` paths plus `stale_dependency_review: {"shot_ids": ["S002"], "source": "actual scoped review record"}` may record the reviewed exception. List every earlier stale active shot exactly. The checker conservatively blocks paths overlapping those shots' state/registry write domains; it leaves those stale takes unresolved. Do not manufacture narrow dependencies to bypass relevant facts. A structurally disjoint path does not prove creative independence.

If the entering baseline returns **exactly** to the immutable take's original baseline, recomputation restores structural dependency validity. Reuse its old acceptance only when the actual source/hash, selected range, director/appearance locks and review criteria are unchanged and the original acceptance remains applicable. This is reuse, not a new media inspection. Otherwise re-review/rebind a new record. Explicit chronology invalidation from `revise` does not clear merely because state values happen to match; it requires actual re-review. Missing evidence stays unverified. Never edit an old baseline to force a match.

New path baselines use `encoding: presence-v2`: path existence is hashed separately from its value, so a missing path cannot equal a real `{"__missing__": true}` value. Old path baselines with no encoding remain immutable and compare in their old format when unambiguous. If a legacy comparison encounters a missing path or that sentinel-shaped actual value, it is ambiguous and requires real re-review, not a fabricated migration. This affects only relevant ledger checks; do not batch-rewrite project history when installing the skill.

## Source version and range

When supplied, `usable_range` is finite `[in,out)`, with `0 <= in < out` seconds in the declared source time origin. New accepted records that name `source_file` must also retain its lowercase `source_sha256`; the ledger validates and preserves the declaration, not the file bytes. Bind it to the actual reviewed preflight/source. A valid digest alone is no proof of acceptance.

Old records remain unchanged; absent hashes are unbound evidence, not automatically approved for reuse. A source-less logical/state test record may remain unbound and is not media-quality approval. `source_binding_status: declared_hash_bound` means only that the declared binding is present. Reject malformed/reversed ranges rather than guessing or swapping them. This ledger is single-context: do not pass an ignored `context_id` into updates; choose the proper separate ledger under [narrative-contexts.md](narrative-contexts.md).
