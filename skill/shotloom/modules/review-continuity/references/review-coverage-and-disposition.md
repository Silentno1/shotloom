# Video review coverage and disposition

Use for full take, selected-range, sequence or final-render review, especially when deciding whether material needs repair or regeneration. Targeted defect questions stay targeted; do not turn a single-frame question into full acceptance. This is a method for reducing blind spots, not a promise of zero missed defects.

## 1. Establish the review target

Bind the actual file/hash/version, intended selected interval, time origin, applicable project acceptance baseline and modalities. Separate **whole file**, **selected source range**, **edited sequence** and **final render**. A source take passing does not approve the assembled edit. A picture-only conclusion does not approve sound. Reuse existing evidence only for unchanged content, ranges and criteria.

Read the current project's tolerance and exact locks when available. Discovery and tolerance are separate: first determine what is observed, then decide whether it matters under that baseline. Do not import another project's permissive examples or stricter appearance criteria. An already accepted version is not reopened merely because this skill changed.

## 2. Cover the interval, then inspect events and objects

For full video review, normal-speed viewing must cover the entire claimed interval at the intended display size; it may be done in contiguous chunks. Record the actually reviewed ranges. Listen separately when sound is in scope. Tool availability, file decoding, image extraction, transcripts and thumbnails do not establish that playback/listening occurred. If the environment cannot inspect playback, report the temporal dimensions as unverified and still provide the supported picture findings.

Use a shot/event map from both the actual clip and the approved beat. A scene-change detector can suggest locations but may miss soft transitions or confuse flashes with cuts. Do not rely only on evenly spaced overview tiles or only on anomalies noticed during the first pass. For long material, work through scenes/contiguous ranges rather than stretching the same 16-frame overview across an episode.

Select independent inspection triggers from the material: handoffs, contact/impact and separation, occlusion/reappearance, turns, entrances/exits, prop use, moving camera against static geometry, state changes and edit boundaries. Inspect the relevant before/change/after states even when the first viewing seemed fine. Low-risk static intervals do not need the same density as a fast contact. If a short interval's relevant transition remains ambiguous, use every decoded source frame, then return to normal playback to judge salience. Do not demand a visible contact frame for an approved offscreen event or ellipsis.

Make a second, differently focused pass over relevant subjects and relationships, rather than repeating the same general impression. Describe **what actually happens** before comparing it with the intended result; do not use the prompt as a transcript of the output. Track only material objects/relationships, not every screw or clothing fold:

| Subject/relation | Follow through time | Important countercase |
| --- | --- | --- |
| Person and visible body | identity, hand/body ownership, limb structure, contact, attention and persistent injury/wetness when relevant | stylized deformation, intentional hold or motion smear is not automatically malformed anatomy |
| Prop and operating state | location/holder, scale relative to hand/environment, orientation, use, disappearance/reappearance, damage | foreshortening, occlusion or a motivated offscreen handoff is not automatic size drift/teleportation |
| Space and movement | stable anchors, relative position, travel direction, support/contact, parallax and clearance | a new screen-left/right composition does not necessarily change world geography |
| Action and consequence | trigger, visible or established cause, response, residual state and endpoint | deliberate ellipsis/ambiguity need not expose every intermediate event |
| Across-cut state/sound | entering/leaving state, attention, ownership, environment and acoustic perspective | time jumps, doors, changed viewpoint and intentional silence can motivate differences |

For each material transition retain a compact observation: subject → before → change → after → supporting times/frames. This can live in the existing review note, not a new universal asset database. Check the listener/background interaction when relevant, not only the speaking face. Repeated individually small defects can become persistent flicker or a confusing relationship; assess accumulation at normal speed.

## 3. Evidence resolution and honest coverage

The existing `take_preflight.py` overview remains an index. `--dense-range START:END --dense-sampling all` extracts every decoded source frame whose timestamp begins in the half-open range, at native resolution, up to the explicit frame budget. Include a little contextual footage before/after the event as appropriate. If over budget, split into adjacent ranges; do not silently lower density and claim all-frame coverage. The manifest records decoded indices and source times, including variable-rate material. Do not interpret file numbering as milliseconds.

For approximate sampling keep `--dense-sampling sampled --dense-fps FPS`. Neither mode proves the images have been inspected. Native individual frames reveal detail; a scaled contact sheet cannot establish a tiny edge, letter or contact point. Raw all-frame output also cannot by itself establish normal-speed impact or acting. Reuse sufficient extraction; do not automatically rerun all technical detectors for every small detail question. The helper functions can extract only the needed range.

Coverage and result are different states:

- **Checked:** actual applicable evidence was inspected; report what it supported.
- **Unverified:** missing, inaccessible, insufficient, stale or not yet inspected evidence; do not call it no defect.
- **Not applicable:** give the reason, e.g. no sound in a picture-only scope or no prop interaction in this interval. Do not use it to bypass a critical event.

State the checked interval/modalities, targeted checkpoints, excluded/unverified aspects and detected findings. “No material issue observed in the reviewed range” is narrower than “no issues in the entire episode.” Avoid false numerical confidence scores or claimed recall rates without a labeled validation set. Exhausted attempts or favorable first impressions cannot change the baseline.

## 4. Separate severity from treatment

For each material finding record time range, subject, directly observed behavior, requirement/authority, normal-playback visibility, narrative/continuity impact and uncertainty. Distinguish a definite error from perspective, intentional style and insufficient evidence. Sparse before/after frames without the intervening event cannot prove a teleport or missing motion.

| Recommendation | Required reasoning | Boundary |
| --- | --- | --- |
| **Retain** | no material failure, or a detected minor issue fits the current tolerance and does not mislead or propagate | “not noticed” is not an accepted exception; a major/critical exception needs explicit version-specific acceptance |
| **Repair then review** | a bounded authorized trim, crop, composite or sound treatment can preserve the beat and already successful material | a proposed repair has not fixed the current file; do not mark it accepted before checking the result |
| **Regenerate affected unit** | identify the hard/major failure and why feasible local treatment would lose required identity, cause, space, performance or endpoint | keep successful unrelated footage; recommendation grants no credits, retries or permission to redo an episode |
| **Unverified** | decisive evidence or interpretation is missing | seek the minimum missing evidence; do not automatically accept or spend credits to resolve a review limitation |

Assess cost of repair against preservation of meaning, not just convenience. Do not hide a collision, clue, handoff or reaction with a crop/early cut, or apply unnatural speed-up merely to conceal an error. A removable unwanted sound should not force picture regeneration; a planned post-only sound's absence is not a defect. If interpretation is uncertain, inspect context before escalating severity. If a known hard defect already justifies regeneration, it is still valid to recommend it while clearly limiting other unreviewed aspects; incomplete review does not erase a known finding.

Minor tolerance is an active disposition, not skipped observation. Under a project baseline that allows it, harmless non-salient details may be retained without asking the user one by one. Do not require a new exception for every permitted minor imperfection. Accepted local exceptions cannot become future reference authority. Keep technical usability, creative realization, sequence fit and treatment separate; technically clean but dramatically ineffective footage may still fail its approved function.

## 5. Neighbors, repaired versions and final render

Compare applicable incoming/outgoing shots and the same-scene spatial/prop authority. Missing neighbors leave cross-cut fit unverified, not the whole isolated take unusable. A locally valid shot can still fail to join the approved sequence.

After authorized repair, bind the new hash/version and inspect the changed range plus boundary/dependency effects. A render/reorder/retime may change onset, endpoint, causality and sound sync; review the actual resulting file, not just the source thumbnails or edit plan. Reuse unaffected valid evidence where an explicit content/time mapping proves it applies; don't copy an old whole-file pass to a new file. Cite the old review and mapping when rebinding unchanged ranges, rather than claiming a new viewing that did not happen. Whole-cut approval requires normal-speed coverage of the actual cut, using previously inspected identical cut chunks only where reliably bound.

Do not write canon from a recommendation. Existing explicit acceptance, continuity-ledger rules and production attempt limits remain in force. General skill maintenance does not reopen an accepted episode, reset attempts or unpause a project.

## Optional machine-readable check

For a full review used for handoff, or when coverage/version consistency is hard to audit, `scripts/review_coverage_check.py REVIEW.json [--verify-source]` checks a declared record. Simple/targeted reviews may express the same information in existing notes without generating JSON. This helper never performs vision/listening, chooses risks, authenticates approval, modifies canon or grants acceptance. `passed_consistency_only` means recorded intervals/bindings/decisions are internally consistent; false observations can still pass.

Schema v1, times in seconds on one source timeline with exclusive outpoints:

- `source`: `path`, `sha256`, `duration_seconds`; `time_origin`, `baseline_ref`.
- `scope`: `kind` (`targeted`, `selected_range`, `take`, `sequence`, `final_render`), `range: [in,out]`, `modalities: ["picture"]`, `["sound"]` or both. Whole-object kinds cover `[0,duration]`; no silent promotion of a fragment/picture-only review.
- `coverage`: rows with `modality`, `range`, `method`, `source_sha256`, `evidence` (nonempty list of actual review/evidence references). Only `normal_playback` counts for normal picture coverage, only `normal_listening` for sound. `overview`, `sampled_frames`, `source_frames`, `native_detail`, `slow_playback`, `neighbor_comparison` are useful but do not replace them.
- `required_checks`: IDs selected from actual task risks, not a fixed universal checklist. Empty is allowed with `check_selection_reason`. `checks`: each has `id`, `targets`, `trigger`, `range`, `source_sha256`, `status` (`checked`, `unverified`, `not_applicable`); checked needs `observed` and `evidence`, not-applicable needs `reason`. Observations should include before/change/after when a state transition matters. External neighbor references may appear in evidence; the row's range still locates the current source being judged.
- `findings`: actual defects/uncertainties, empty only after inspection; each has `id`, `range`, `source_sha256`, `subject`, `observation`, `requirement_ref`, `impact`, `rationale`, `evidence`, `severity` (`minor`, `major`, `critical`, `uncertain`), `salience` (`normal_playback`, `detail_only`, `unknown`), `disposition` (`retain`, `repair`, `regenerate`, `unverified`). Repair/regenerate needs `next_action`; major/critical retention needs version-specific `acceptance_ref`.
- `verdict`: same four dispositions. It is a recommendation for this exact scope, not a substitute for user/project acceptance. An overall retain contradicting an unresolved repair/regenerate finding, or a repair-only verdict hiding a regeneration finding, fails consistency. Missing coverage/check evidence returns unverified, never no-defect. The checker does not calculate artistic severity from the labels.

Do not invent paths, observations, approval references or viewed intervals to make the checker pass. `--verify-source` additionally hashes the actual local source; without it the source hash remains declared, not independently verified. Exits: 0 consistency only, 3 unverified, 2 malformed/contradictory record or source mismatch. No exit code authorizes production.
