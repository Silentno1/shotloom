# Final-output audio synchronization

Use when precise dialogue/contact/music alignment matters or an export sounds delayed. Retain the approved sound ownership and per-element treatment. A sync check does not authorize adding sound, changing an accepted beat or regenerating picture; an intentionally silent or picture-only task need not perform it.

## Separate the three clocks

1. **Picture event:** actual decoded time/frame of the relevant contact, mouth action, cut or other anchor in the selected cut.
2. **Sound event:** the chosen audible onset/accent inside the retained audio asset. File start, leading silence, audible onset and largest amplitude peak are not interchangeable. A peak can belong to a later tail or unrelated noise.
3. **Rendered result:** where the corresponding sound event lands in the actual exported file, after trimming, retiming, processing, encoding, muxing and playback interpretation.

Choose the event for the intended perceptual relationship. A pre-lap, distant sound, subjective displacement, musical pickup or soft material contact need not peak at the picture contact. Preserve that intended lead/lag. Waveforms help locate candidate anchors; listening determines what event they represent.

For a constant positive **audio** rate `r`, an event offset `a` measured from the retained asset's inpoint, a desired output event time `T` (including intended lead/lag), and a separately measured pipeline displacement `d`:

`audio placement = T - a / r - d`

Here `d > 0` means the decoded exported event was late relative to its predicted timeline position; subtract it only once. `d < 0` means early. Do not use the picture's rate when the sound was kept at normal speed. Sample-rate conversion alone does not imply speed change. A negative required placement needs preroll/handles or a different authorized asset/edit solution; do not silently clamp it to zero, delete the attack, or move the story event.

Example: desired accent at `2.000 s`, retained-source accent offset `0.045 s`, audio rate `1`, and independently measured late displacement `0.080 s` imply a placement of `1.875 s`. With displacement unknown, `1.955 s` is only the nominal timeline placement, not proof of final sync. `python3 scripts/event_timing.py sfx --target 2 --anchor-offset .045 --rate 1 --measured-delay .08` performs this arithmetic only (optional Python 3.10+, standard library); omit `--measured-delay` when it is not measured. Without Python, apply the formula manually and retain the same evidence limits.

## Diagnose before applying an offset

- Bind measurements to the exact exported hash/version and time origin. Inspect decoded timestamps and the actual file rather than treating editor preview, requested seek position or container start metadata as the event itself.
- Compare a few relevant anchors across the affected interval. Similar displacement may indicate an offset; increasing drift suggests a rate/timebase mismatch; one displaced effect suggests a local trim/anchor problem. Do not “fix” increasing drift with a universal constant.
- If necessary and authorized, use a short non-production sync probe through the same export path. Keep diagnostic click/flash material out of production masters. A tool/version/settings change may invalidate that calibration; reuse current evidence instead of measuring every export from scratch.
- Keep source-anchor measurements separate from pipeline compensation. If an effect already had its leading silence trimmed or a delay already compensated upstream, do not subtract it again. Unknown displacement stays unknown; never copy another project's encoder-delay constant.
- Codec priming, timestamp handling and a player's behavior are hypotheses until inspected. Do not shift the master to compensate for one faulty player when the file's decoded events align; identify the actual delivery/playback problem first.

## Validate the delivered file

Check the corrected export around material events and joins, at normal playback and intended listening conditions. Use dense frame/decoded-audio evidence to resolve disputed alignment, then listen again. An estimated frame tolerance is task-specific, not a universal three-frame rule.

Also check whether the event is audible in the mix, whether the tail spills across a meaningful cut, whether dialogue is masked, and whether gain or dynamics processing introduced clipping or changed the intended texture. Timeline volume `1.0`, a visible track and a clean loudness report do not establish a comfortable audible result. Adjust individual layers only as needed; preserve comfortable native sound and intentional silence. No blanket normalization or fixed gain boost.

Report picture anchor, chosen sound anchor, intended relationship, measured residual, treatment, exact output version and evidence limits in the existing review/edit note. Actual listening unavailable means sound quality remains unverified; arithmetic, waveforms and technical checks must not be labeled a listening pass. Failures follow the existing repair/stop/accepted-exception authority, never automatic pass-after-N-rounds.

## Provenance

Independently adapted from [video-shotcraft's final-render sound checks](https://github.com/Vincentwei1021/video-shotcraft/blob/main/references/final-review.md), reviewed 2026-10-05. Its runtime-specific levels, fixed timing tolerances, mandatory alternate masters and product-film sound formulas were not imported. [Post-production](post-production.md) retains authority for the soundtrack and delivery scope.
