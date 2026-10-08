# Caption correction and source-to-cut conform

Use for requested dialogue captions, accessibility captions or their revision after an edit. Do not add captions automatically. Establish whether the target is verbatim speech, approved translation/adaptation, accessibility description or an in-world text graphic: these have different content authority. Exact story-bearing screen text remains an approved visual asset, not an ASR guess.

## Keep words, corrections and layout separable

- Preserve source hash, actual audio stream/channel, timing origin/timebase and transcription/alignment version. Cache valid raw timed words and corrections for that source/configuration; unchanged content need not be transcribed again merely because the cut changed. A changed soundtrack or demonstrably inadequate timing may require targeted re-alignment or authorized transcription, not an unconditional cache-reuse rule.
- Use stable source-word IDs and separate display corrections where the tools support them. A simpler task can use equivalent source ranges and correction notes; no compulsory database or new schema.
- A project glossary resolves verified names/terms, not every similar-sounding word. Inspect replacements in context. The script helps diagnose ASR errors but cannot make an actually omitted or differently spoken line exist. Correct an ASR misrecognition only with supporting evidence; preserve a substantive performance mismatch as a finding, not a silently rewritten caption.
- Ordinary verbatim captioning does not authorize adding missing speech or improving a character's wording. Preserve authorized translation/adaptation choices separately. For an unresolved name or unclear sound, locate the uncertain word and seek evidence instead of guessing; listening remains necessary for auditory claims.

## Map through the audible edit

Work from the actual selected **audio** ranges and their timeline placements. J/L cuts, offscreen speech, detached dialogue, ADR and overlap may not follow picture in/out points. Two uses of the same source range are two timeline instances, not duplicate errors to remove. A subtitle can legitimately cross a picture cut while the utterance continues.

Use half-open source ranges `[in, out)`, retain precision until delivery formatting, and establish whether each supplied timestamp is source-media time or time relative to a decoded/extracted start. ASR timestamp precision is not evidence of acoustic accuracy. For constant positive playback rate `r`:

`timeline_time = timeline_in + (source_time - source_in) / r`

Map retained word start/end through each actual audio segment. The source window's timeline duration is `(source_out - source_in) / r`. This assumes a linear audio time mapping, not merely a picture-speed setting. Sample-rate conversion that preserves duration is not a change in `r`.

- A word outside the retained audio window is excluded there. A word intersecting a cut edge is **partially retained**, not a valid whole-word subtitle just because its interval can be clipped mathematically. Inspect the actual sound; adjust the cut within authorization, correct inaccurate alignment, or report a genuinely cut word. Never silently restore a missing word in text.
- Split a cue across an actual removed audio gap when needed; do not stretch the original sentence subtitle over words that were removed. Preserve deliberate overlaps and speaker distinctions according to the caption treatment.
- A speed ramp needs the actual nonlinear audio time map or a verified re-alignment to the transformed dialogue. Do not average endpoint rates, infer it from picture alone or interpolate unknown mapping. Freeze/reverse/remixed speech likewise needs a supported mapping and meaning review.
- CFR frame conversion uses the evidenced rational frame rate; VFR requires actual timestamps. Do not treat a frame index as milliseconds or convert `30000/1001` to an assumed 30. Account for stream start offsets and time-origin changes explicitly.

Optional arithmetic helper (Python 3.10+, standard library only): `python3 scripts/event_timing.py map --source-in 10 --source-out 12 --timeline-in 3 --rate 2 --event-in 10.8 --event-out 11.2` reports `[3.4, 3.6)`. It only computes a declared constant-rate interval and flags partial/excluded events; it does not inspect audio, validate the edit or write subtitles. Without Python, use the same mapping manually and state what remains unverified; do not install a runtime just to use this method. No packet is required for ordinary caption work.

## Group and verify at the viewing size

Regroup mapped words by meaning, speech and readable screen area. Preserve approved spelling, speaker treatment, font, outline, placement and safe areas. Do not impose one line per screen, one cue per comma, a universal minimum duration or a fixed character count. Short exclamations may be intentionally brief; dense important text still needs an actual readability check.

Do not solve overcrowding by silently deleting dialogue, shrinking text beyond legibility or covering a face/clue. Use an authorized layout/grouping change or disclose the conflict. Keep original corrected words separate from formatting so a reflow does not erase editorial work. Overwriting manually corrected timing/grouping requires the task's overwrite authorization and a recoverable version.

Check the actual final output: wording, timing against heard speech, speaker attribution, appearance/disappearance, overlap, missing/duplicated cues, glyphs, crop/safe areas, and occlusion by other layers. Ordinary accessibility/dialogue captions usually sit above decorative overlays; in-world text or an explicitly designed behind-subject treatment has different compositing requirements. A universal “all subtitles last” filter recipe cannot choose those requirements.

Preview-only subtitles are not burned-in deliverables. Sidecar SRT/VTT, styled/structured captions, clean masters and burned-in variants are chosen for the actual delivery request; none is universally mandatory. Verify the requested variant after export rather than reporting the editor preview as completion.

## Reconform only what changed

Bind captions to the cut and soundtrack version. Locate affected cue/word IDs and source/timeline ranges after trims, repeats, moves, rate changes, audio replacement or corrected words. A ripple edit can shift unchanged downstream content: preserve its text but recompute its new placement. A changed correction can reflow neighboring cues. Do not issue only a vague “subtitles may be stale” warning.

Reuse unaffected verified content; check changed boundaries and downstream timing consequences, then the requested final deliverable. Do not claim a new listening pass when only arithmetic was checked.

## Provenance

Independently adapted from [chengfeng subtitle correction](https://github.com/Agentchengfeng/chengfeng-videocut-skills/blob/main/plugins/chengfeng-videocut/skills/chengfeng-subtitle/references/subtitle-correction.md) and [video-use's transcript/EDL mapping](https://github.com/browser-use/video-use/blob/main/SKILL.md), reviewed 2026-10-05. No upstream code, mandatory single-line layout, runtime-specific JSON requirement, blanket audio-first editing or fixed padding/fade was imported.
