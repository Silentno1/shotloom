# MiniMax H3 adapter

Baseline source record: official `h3-prompt-writing` skill, base and Ref2VA guides, recorded as checked 2026-10-01. Source scope, unavailable legacy material and destination limitations: [model-manual-authority.md](model-manual-authority.md). This is inherited guidance, not a new source check or a requirement to install that original skill. Read this adapter as the native rewritten-prompt contract; the destination's input processing and available modes must be verified separately. Do not assume H3 Max is the same operation.

## Current official envelope

- Output: 4–15 seconds, 24 fps, native 32 kHz stereo audio.
- FL2VA family: zero, one or two image inputs for text, first-frame, last-frame or first-and-last-frame generation.
- Ref2VA: at most 9 reference images; at most 3 reference videos, each 2–15 seconds and 15 seconds total; at most 3 reference audios, each 2–15 seconds and 15 seconds total; at most 12 files across all input types.
- Reference audio cannot be the only Ref2VA input.

Do not add an unofficial prompt-length cap. If the active interface displays one, record its source and validate that interface separately.

## Mode router

- `T2VA`: no image anchor or reusable media reference.
- `I2VA`: one exact opening frame.
- `FL2VA`: exact opening and ending frames.
- `L2VA`: one exact ending frame.
- `Ref2VA`: reusable identity, style, scene, motion, editing structure, voice or other multimodal references.

Keep base-mode keyframe inputs separate from the Ref2VA manifest. However, the official Ref2VA guide explicitly supports a reference image acting as a first/last/keyframe or storyboard anchor within Ref2VA: define that role there and confirm the host supports it. Do not reject that valid semantic role merely because it is a frame anchor, or silently change it into a base-mode input.

## Hosted reference-image limits

Read [platform-routing.md](platform-routing.md#reference-file-geometry) before reference submission. A host's `mixed2video` name or successful plan validation does not itself establish every downstream H3 gateway limit. Preserve scoped runtime-error evidence when an image is rejected; verify actual input width/height rather than the requested output ratio. Apply numeric limits only with current evidence for the exact hosted operation, not as a permanent rule for every H3 mode or provider.

## Required schema

Base modes use exactly this order:

```text
integrated_multimodal_description:
overall_soundscape:
non_diegetic_music:
```

Ref2VA uses exactly this order:

```text
subject_definitions:
summary:
retention_analysis:
detailed_description:
overall_soundscape:
non_diegetic_music:
```

Use English control prose. Preserve exact dialogue, lyrics, visible text and identifiers in their source language when the selected audible or picture-sync strategy compiles them into this operation. Use `<Picture N>`, `<Video N>`, `<Audio N>` and `<Subject N>` consistently; never import Seedance `@图片N` syntax.

In shot grammar, `[Shot 1]` has no timestamp. Later cuts use `[Shot N] At MM:SS.mmm`. A camera move is not a cut.

### Base keyframe alignment

T2VA starts directly with the three fields. Other base modes require the guide's first-line alignment instruction, then a blank line before the fields. Substitute the actual last shot number and duration with exactly two decimals; these are alignment references, not extra shots:

```text
I2VA: For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.
FL2VA: How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot N) aligns with the S.SS-second mark of the target video.
L2VA: How the reference pictures align with the target video — <Picture 1> (from [Shot N]) aligns with the S.SS-second mark of the target video.
```

The mode labels before each example line are explanatory, not pasteable prompt text. Develop forward from an opening image, continuously connect both endpoint states for FL2VA, or converge to the ending image for L2VA. FL2VA normally favors one continuous shot; do not introduce unrequested cuts to evade the transition.

### Ref2VA reference semantics and detail

- `<Subject N>` is reusable visible content, not simply an uploaded file: one subject may combine several inputs and one input may contain several subjects. Identity, scene, costume, action or visual style can each be referenced content.
- Give `<Picture N>` its own definition only when that image is independently used as a concrete frame/composition/storyboard anchor. If it only supplies identity, cite its source inside the Subject definition.
- `<Video N>` identifies an edited/continued original or temporal/camera structure; a person/action extracted from it remains a Subject. Merely referencing movement does not mean editing the original.
- `<Audio N>` denotes a separately provided signal or an explicitly enabled synchronized track from a video. Video and Audio numbering are independent; do not infer audio reuse from the mere presence of a sound-bearing video. Bind voice timbre separately from copying spoken content.
- `summary` starts with appropriate bracketed task types: `keyframe completion`, `reference generation`, `video editing`, `video continuation`, `audio reuse`, `audio reference`, combined without duplicates. Video editing identifies the edited source, not a new video vaguely inspired by it.
- `retention_analysis` gives the applicable reference labels their retained scope and shot placement. Visual markers: `fully_preserved`, `partially_preserved`, `attribute_transfer`, `weak_reference`. Audio markers: `fully_copy`, `partially_copy`, `reference`, `weak_reference`. These are relative to the defined role, so a new action is not an identity-preservation failure. Shot references in definitions/retention are legitimate; they are not timeline blocks.
- Before `[Shot 1]`, `detailed_description` establishes the selected appearance in one or two English sentences. It then develops composition, subjects, light/space, action/state changes, camera and approved sound shot by shot, applying references where they matter. Official guidance normally recommends 350–500 English words for generation; dialogue-dense/editing tasks have stated exceptions. Treat this as guidance, not a hard minimum or permission to invent details, fill with adjectives or exceed the host limit. Reconcile the actual surface before delivery.

### Dialogue and camera grammar

Use stable `(S1)`, `(S2)` by actual vocal-event order, not Subject numbering. Referenced speakers use both `<Subject N> (Sx)`. Keep delivery/action outside `<d>[Language] exact spoken words</d>`. An identity that never vocalizes needs no speaker ID. Voiceover uses `says in an off-screen voiceover` with the corresponding visible lips remaining closed. Cross-cut speech uses `<scenetrans>` at the joining parts and explicit continuity; end-truncated speech uses `<cutoff>`. These tags describe an approved event, not permission to truncate a locked line. Visible writing is quoted in its original language. Preserve user-locked wording/punctuation; if a reference-transcription normalization recommendation conflicts with that lock, retain the user text and disclose the exception.

Write camera movement naturally in the shot, distinguishing lens zoom from camera travel, pan from lateral translation, tilt from elevation. Add speed/amplitude when meaningful; do not append an indiscriminate camera-parameter list.

Populate `overall_soundscape` only with audible layers assigned `native_required` or selected `native_optional` in the source lock, summarized in 1–4 English sentences. Do not repeat dialogue/lyrics there; they belong in the timeline. Post-owned ambience, effects, dialogue masters and music remain outside the audible generation request. A post-only dialogue may still leave its approved visible mouth-performance cue in the picture description, not a native-speech request. The guide uses `non_diegetic_music: N/A` for absent audience-only music and `overall_soundscape: N/A` only for explicitly intended complete silence. If there is native dialogue but no owned ambience/effects, describe that exclusion precisely rather than declaring complete silence or inventing room tone. A silent picture pass is silence for this operation, not a claim the final edited film is silent. H3's native audio does not guarantee omitted layers stay absent; listening/cleanup and unsupported control disclosures remain necessary.

## Project-verified capability boundary

Do not store an undocumented local result as a permanent H3 capability. A `project-verified` claim records test date, exact model and surface, source hashes, operation/prompt version, reviewed output path or hash, observed success and failure, and the genre/control scope it actually tested. Without that evidence record, keep the claim `unknown` or `community-observation`; one stylized-animation test does not establish a universal strength or incapability.

## H3 action compilation

Use the director's complete causal beat. Choose the shortest duration that contains readable setup, acceleration, peak, visible consequence and required handle; do not stretch a hit to fill 15 seconds.

For each dense phase choose one high-risk precision owner: camera, contact, environment, subtle performance or dominant effect. Support it with keyframes/reference media/focused composition or simplify competitors. Name the observable acceleration and arrest; otherwise attractive motion may become uniformly eased.

Use the shared [appearance activation scope](../../visual-design/references/appearance-family-routing.md) to load [three-render-two-compilation.md](three-render-two-compilation.md) for the whole operation or only an approved local owner inside `mixed_media`. Keep stable appearance once in the H3 schema and only shot-specific changes in shot events. Name the local owner; preserve the other layers and root family. This does not add a generation operation or transfer local rules to photographic, drawn, standard 3D or custom layers.

## Reference manifest

Use JSON shaped like:

```json
{
  "first_frames": 0,
  "last_frames": 0,
  "reference_images": [{"id": 1, "role": "identity"}],
  "reference_videos": [{"id": 1, "duration": 6.0, "role": "camera rhythm"}],
  "reference_audios": [{"id": 1, "duration": 4.0, "role": "voice"}]
}
```

Run `scripts/prompt_structure_check.py --platform h3 --mode Ref2VA --duration 8 --prompt PROMPT --manifest MANIFEST` before delivery. A pass proves only deterministic structure.

For explicitly enabled audio from a reference video, an audio-label entry may use `source_video_id` matching that video's manifest ID; its duration is the enabled track span. It is a semantic Audio label, not another uploaded audio file. Do not add one merely because the source video has audio. This local manifest representation is not a proprietary API parameter. Actual host track enablement must still be verified.

Also validate the source lock's sound partition. H3 prompt structure alone cannot prove that a post-owned audible layer was excluded or that a visible post-dub performance cue was preserved.
