# Actual take review

For full video review and retain/repair/regenerate decisions, read [review-coverage-and-disposition.md](review-coverage-and-disposition.md). It defines normal-speed coverage, event-triggered inspection even when no anomaly was first noticed, object-state tracking, neighbor/final-render checks and evidence-bounded recommendations. Targeted questions stay targeted. Use the active project's tolerance; do not replace detection with assumed tolerance or tolerance with frame-perfect scrutiny.

## Review order

Choose evidence resolution separately from temporal density. Preflight CLI dense bursts now default to native-resolution individual PNGs; the sheet remains an overview. Inspect those source-detail frames (or a clearly identified pixel-preserving region) for eyes, tears, line stability, fine contact and text. Enlarged thumbnail pixels do not recover missing detail. The compatibility Python helper defaults to overview unless `resolution="native"` is passed; check the manifest's `frame_resolution` before judging detail. `--dense-resolution overview` is an explicit lighter option, not adequate proof for tiny features.

`last_frame_evidence` identifies the actual last decoded video frame, with frame index and timestamp, not duration minus a fixed offset. `--selected-out SECONDS` additionally extracts the last frame strictly before an exclusive source outpoint, relative to the first decoded video frame. The file's last frame, selected fragment endpoint and final rendered cut endpoint are different evidence; after retiming/compositing inspect the actual final render too. Decode failure is unverified, not permission to reuse an approximate tail.

`metadata.video.timeline` records the video clock used to validate selected/dense outpoints: decoded frame count, normalized last-frame start, video end and its basis. Prefer the last decoded frame's duration, then video-stream duration. A CFR fallback requires matching declared rates and timestamp grid and is labeled `end_is_estimate`; an unknown VFR/single-frame tail stays unknown. Container duration may omit the last frame or include longer audio, so it does not bound video ranges. This avoids a blanket extra-frame allowance while rejecting genuinely out-of-range selections. Timing evidence is not review or acceptance.

Contact sheets are overview indexes, not edit decision lists. New `source-frame-select-v2` sheets retain selected source-frame times relative to the first decoded video frame and record them in `contact_sheet_sampling`. Older sheets without this marker may label an `fps` resampling grid rather than the pictured frame's source time; do not reuse those labels for exact cuts. Verify only the relevant source interval/PTS when timing matters, without reopening unrelated historical reviews. Even correctly timestamped sparse samples cannot locate a cut between samples; millisecond labels do not confer sub-frame accuracy.

Remote fast/keyframe snapshots may return the same decoded frame for different requested times. Record requested time separately from verified source time; repeated pictures do not by themselves establish a freeze, pose hold, missing motion or a failed reaction. Use supported accurate seek/decoding and playback for temporal claims, or keep that dimension unverified. More duplicate thumbnails are not denser temporal evidence.

New preflight runs use unique subdirectories under the requested output root; consume the returned manifest path, not a guessed old `review-manifest.json`. Dense bursts marked `source-frame-select-dense-v1` bind each output file to a selected source timestamp and source hash. Requested fps is an approximate sampling budget, not proof of unique native frames at that rate; frames are selected, never interpolated or duplicated. Compare `frames` and `source_timestamps_seconds` in order. Do not reuse unversioned/resampled burst numbering as precise source time. Technical detectors retain per-check completion/failure/error; failed ranges are null, not an empty successful result. A partial/failed report requires targeted recovery or an explicit unverified finding, never a no-defect verdict.

`--dense-sampling all` produces `all-decoded-source-frames-v1` evidence with every decoded frame beginning inside the selected interval, native pixel dimensions, decoded frame indices and source times. The explicit maximum is enforced without silent truncation or subsampling; split an overlong range. Both sampled and all-frame outputs remain extracted evidence, not completed review. Short intervals may need contextual frames before/after the event. Increasing overview tile count alone cannot establish temporal coverage.

Preflight and dense extraction compare source SHA-256 before and after processing. A detected change invalidates that run; do not attach old extracted pixels to a new file hash or consume partial outputs as valid evidence. Stabilize the intended source and rerun only the affected evidence. Exclusive outpoints are compared using decimal source timestamps before conversion to display floats: a frame at exactly the boundary is excluded even with a nonzero source start. This does not claim sub-frame accuracy or detect an adversarial file changed and restored between both checks.

1. Identity of source file/version and technical integrity.
2. Hard facts and exact execution locks.
3. Narrative function and endpoint.
4. Identity, wardrobe, props, text, space and sound continuity.
5. Performance, camera, rhythm, action and spectacle.
6. Medium-specific appearance.
7. Usable ranges and edit handles.

## Creative realization is a separate finding

For selected-director realization, use the approved decisions under [director-decision-practice.md](../../director/references/director-decision-practice.md), not resemblance to a famous film. Check the circumstance/knowledge, character tactic, audience carrier and meaningful change together. Does delivery coordinate with listener, gaze/body and framing? Does timing follow the event rather than a generic emotion preset? Separate a faithful but ineffective design from a lost-in-generation decision or an editorially removed response. Different contexts may require different intensity/cut rates under the same method; no compulsory technique or reference-film match. Written comparisons and method retrieval cannot approve audiovisual quality.

For a full take/sequence review, compare the director-defined creative carrier with the actual selected range, not just the prompt or best frame. State whether the required relationship is **realized**, **partially realized**, **absent** or **unverified**, and identify the observed evidence. These are descriptive review findings, not automatic acceptance or a new required JSON schema. Keep technical usability, creative realization and sequence fit separate; no artifact is not the same as effective direction. A targeted defect question does not require this entire review.

If the carrier is missing from the design, report that upstream gap rather than inventing a retrospective intention. If it exists and survives the result, preserve that success; do not blame all dissatisfaction on missing prompt detail. Judge its timing at normal playback and intended display size. A static contact sheet can establish visible framing or pose but cannot establish a convincing reaction, rhythm or emotional flow.

For a sequence, inspect adjacent attention owners, shot relationships, progress/hold and residual states. Repeated framing may intentionally sustain pressure; do not reject it by a shot-count formula. When it is unintended sameness, identify what approved effect fails to develop rather than prescribing random inserts or constant motion. Required creative meaning lost in a crop or cut is an editorial finding even if all remaining faces, words and technical checks pass. Financial investment or exhausted attempts do not lower the target; follow the existing pause/exception authority.

## Severity by salience

Use the current project's accepted baseline and keep severity separate from the treatment decision in [review-coverage-and-disposition.md](review-coverage-and-disposition.md). Detect and describe before deciding to tolerate. A harmless detail-only issue may be retained when the applicable baseline allows it; repeated small defects can accumulate into a major normal-playback problem. Compare the world relationship, not just screen-left/right or exact pixel similarity to a reference.

- **Blocker:** changes story fact, identity, critical text/dialogue, ownership, contact, geography or required endpoint.
- **Major:** clearly visible at normal playback and damages performance, action or continuity.
- **Minor:** visible on focused review but does not mislead or propagate.
- **Local accepted exception:** user knowingly accepts it and it is explicitly prevented from becoming future authority.

## Medium branches

Use the actual approved [open appearance contract](../../visual-design/references/appearance-family-routing.md); these branches are examples/maintained routes, not a closed style list. Inspect observable identity, narrative relationships and the contract's visual/temporal rules. A source label such as anime or watercolor alone does not tell whether outlines, lens depth, smooth motion or physical shading are required. Missing material intent is a specific unknown, not permission to select another look.

- Photographic/live-action: anatomy, skin/material response, lens/light behavior and natural performance.
- 2D animation: the contracted line/edge or outline-free language, shape, layers, paint/texture, cadence and deformation. Distinguish approved line boil/paint evolution/holds from unintended identity or temporal drift.
- Standard 3D: volume, rig/deformation, material and light response, camera parallax and motion quality; do not require cel shading or 2D effects.
- Three-render-two, only when the approved appearance family says so: volume/parallax, contours, shadow bands, material separation, texture adhesion, 2D-effect depth/contact, cadence and deformation. Compare the stable base lock with the current shot delta.
- Stop-motion/material: material persistence, replacement cadence, contact, scale and deliberate stepping.
- Motion graphics: hierarchy, typography, interpolation, timing and information legibility.
- Mixed media: inspect each owned layer/subject or bounded interval against its own look and cadence, then the interfaces, occlusion, synchronization and retained narrative anchors. A local three-render-two effect does not impose its checklist on photographic or drawn layers. Permanent composites need coherent coexistence, not an invented return to one style; intentional transitions use their actual entry/exit rules.
- Custom / `other`: derive checks from the explicit project-specific appearance contract, even when the name is unfamiliar. Do not force it into an existing branch or call it unreviewable because it is absent from this list. Unspecified material behavior stays unverified until clarified; do not invent a defect or an automatic pass.

Do not use photoreal pores or hair strands as universal quality criteria.
Do not infer three-render-two from anime subject matter, outlines or effects, and do not apply its checklist to another family.

Intentional stepping, material roughness, nonphysical shading or controlled shape replacement can pass their approved contract; artistic intent does not excuse wrong ownership, a lost required event, unapproved style drift or a broken endpoint. Temporal detectors are only review locators: expected held/replaced frames or texture changes are not automatic failures. Normal-playback and focused evidence requirements remain unchanged.

For three-render-two motion, sample densely around turns, occlusions, camera movement, pose holds, smears and effect contact. Check whether contours/shadow bands flicker, painted texture swims, smooth interpolation erases intended cadence, deformation loses the character volume, or 2D effects detach from depth and contact. A still frame cannot approve motion-only dimensions.

## Sound review

For embodied expression, also apply the performance section below; correct words or sound cannot establish that the visible acting passes.

Compare each material sound with the source `audible_ownership`: `native_required`, `native_optional`, `post_only` or `intentional_silence`, and separately compare any picture cue/sync strategy. Inspect synchronization, semantic correctness, intelligibility, acoustic perspective, continuity, artifacts and dramatic hierarchy. Then recommend one actual-media treatment: `retain`, `clean`, `supplement`, `replace` or `intentional_silence`.

Listen to the actual file at normal speed and, when needed, around critical sync points. A transcript can test wording; a waveform can locate events; loudness and spectra can expose technical clues. None can establish naturalness, timbre, spatial comfort, impact feel or dramatic hierarchy without auditory review. If the current environment cannot audition the source, report that limit and do not issue a sound-quality approval.

Do not prefer post-production merely because it is controllable. Natural native dialogue, impact or prop contact may be the best source and should be retained when it passes. Do not prefer native audio merely because it exists. Missing `post_only` sound is expected, not a take defect; an unexpectedly generated post-owned layer is reviewed for removability and continuity rather than silently accepted.

Across cuts in one scene, compare acoustic identity and motivated perspective, not identical loudness. Camera distance, enclosure, doors, attention and point of view may justify change. An unexplained disappearance of established room or crowd sound is a continuity finding; an intentionally quiet scene is not.

For a suspected export offset or a timing-critical sound, use [final-output sync calibration](../../edit-delivery/references/output-sync-calibration.md) to distinguish the source's audible anchor, intended lead/lag and measured export displacement. Diagnosis does not authorize applying the repair. For caption-bearing delivery, compare the actual captions with the audible edit and approved caption treatment under [subtitle conform](../../edit-delivery/references/subtitle-conform.md); a correct text file or timing calculation does not prove the rendered captions are legible, complete or synchronized.

## Shot, camera and time-treatment review

When these decisions matter, compare the actual range with the director's framing/viewpoint, movement/focus, reveal and exit; use [shot-camera-time-design.md](../../director/references/shot-camera-time-design.md) for distinctions, not as a requirement to demonstrate every technique. Check whether required detail is readable at intended display size and whether a crop, focus miss, unintended drift or early cut erases it. Do not fail a fixed shot, continued-motion exit, motivated axis crossing, flat composition or deliberate disorientation merely for departing from a default.

At intended playback, distinguish a slower character, camera-speed change, repeated frames, pose hold, global slowdown and local speed ramp. Verify material transition anchors, duration and body/prop/camera/effect/sound synchronization against the plan. Output fps and sparse thumbnails cannot establish high-frame-rate capture, smooth slow motion, an accurate ramp or convincing cadence. Use source-timed dense evidence for disputed intervals, state which temporal dimensions remain unverified, and return to normal viewing to judge effect rather than rewarding the number of techniques.

## Action review

Inspect dense frames around preparation, contact and consequence where the approved coverage shows them, using targeted source-frame-rate evidence rather than only evenly spaced thumbnails. Verify relevant support, hips/torso transmission, silhouette, visible contact, reaction delay, recoil, camera/VFX/sound order, damage persistence and new spatial state. For deliberate offscreen action or ellipsis, judge the established cause, retained evidence and aftermath across the coverage; do not demand a contact frame that was intentionally excluded or use that exception to excuse a required visible hit that failed. Flag “smoothness collapse” when continuous eased movement erases acceleration, arrest, reversal or a readable peak.

For multi-opponent action, also compare the actual sequence with its intended attention/threat map: can the viewer locate relevant opponents, understand focus switches and track persistent positions/injuries? Flag unexplained waiting, disappearing participants, identity/weapon migration, teleports or unreadable collisions where they damage the intended beat. Do not reject deliberate hesitation, offscreen threats, simultaneous attacks or a transfer of focus merely because they depart from a single-protagonist template. Return to normal playback to judge clarity; dense frames alone cannot establish pace or impact.

For powers or area effects, check activation, origin/target, affected region, opponent response and resulting state against the approved power rules. Non-contact effects need their established causal trigger, not invented physical contact. A brighter/larger effect is not evidence of correct ownership, escalation or aftermath.

## Scale-critical imagery review

Apply only when relative scale or mass is an intended requirement. Compare the selected known-size anchors, proportions, support and overlap across the actual views; distinguish changed framing/perspective from unexplained size drift. For motion, inspect weight cues and any authorized environment response in temporal context. Record a lost scale comparison, sliding support, impossible clearance or inconsistent response by its consequence and visibility, not by counting missing atmosphere layers. A static subject, full-body view, flat 2D composition or agile giant can pass when intentionally designed. Still-image approval does not establish temporal mass or motion continuity.

## Performance review

Compare actual acting with the director's `performance_contract`, not just the emotion word or the prettiest frame. If no observable performance target exists, report the design gap; do not invent an intended motive to justify or reject the take.

First inspect the beat in temporal context at normal playback and intended display scale. Then use targeted dense frames around attention changes, facial/body transitions, contact or visible physical effects; return to normal playback to judge rhythm and salience. Still frames can establish pose or wetness, not reaction timing or emotional flow. If playback cannot be assessed, label temporal credibility unverified rather than approving it from thumbnails.

Check only channels relevant to this beat:

- **Readable intent and intensity:** does the required audience-visible change register, while preserving intended concealment or ambiguity? Flag both under-expression (absent/illegible required change) and over-expression (unmotivated grimace, gesture or breakdown). Deliberate stillness and approved stylized exaggeration are not automatic defects.
- **Attention and eyes:** target matches space and interaction; shifts or holds are motivated; head/eye relationships remain credible for the selected style. Flag wandering, wrong-target fixation, mechanical blink loops or unintended lens contact. Do not infer a hidden emotional state from gaze alone.
- **Whole expression:** face, gaze, breath and body form a readable performance or the approved deliberate contradiction. Watch for a pasted smile, frozen face over active body, unrelated gestures, synchronized expression switching or an unintended mood.
- **Temporal response:** available stimulus precedes reaction; onset, change, interruption, overlap and aftermath serve the beat without a universal delay or mandatory recovery. Check the listener as well as the speaker. Absence of continuous motion is not itself failure.
- **Physical detail and continuity:** when relevant, inspect wetness/fluid travel, tremor, laughter or breath-related movement, interaction with hands/objects and residual state; distinguish intended stylization from floating overlays, broken contact or unmotivated resets. No symptom is universally required for an emotion.
- **Coverage:** is the required acting readable in the actual framing and edit? If a cue exists but is hidden or cut off, attribute coverage/edit failure rather than demanding a stronger expression by default.

Record time range, observed behavior, violated requirement, normal-playback impact and uncertainty for material findings. Judge the response as a whole before comparing individual cues; an optional gesture differing from the plan is not a failure when intent, locks, intensity and continuity pass. Facial keyword matches and structural checks cannot approve emotional credibility.
