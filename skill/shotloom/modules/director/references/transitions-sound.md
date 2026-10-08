# Transitions, sound and edit intent

Design transitions as a pair: outgoing final state/motion/light/sound; mechanism; incoming first state/motion/light/sound; information gained.

Use hard cuts, action matches, eyeline matches, graphic matches, foreground wipes, motivated full-frame effects, light changes, J-cuts, L-cuts or dissolves only for a dramatic reason.

For an intended invisible continuous join, a flash, smoke cloud, debris field or motion blur needs an established cause, sufficient coverage of the changing region (full-frame when hiding the whole image), and a compatible incoming carrier before revealing the continuing state. This is not a rule for graphic cuts, deliberate time jumps, subjective memories or discontinuous montage; those need their intended visual/sound relation, not invented physical continuity.

Separate dialogue/voice, physical action and ambience, and non-diegetic music. Assign who owns the peak. Sound may lead picture or carry across it, but random per-generation music must not rewrite the scene's music logic.

## Sound ownership before generation

For every sound event that materially affects performance, causality or continuity, record a stable identifier, category, continuity scope and one **audible ownership** state:

- `native_required`: the sound should be attempted with picture generation because embodied timing, mouth performance or contact synchronization materially benefits;
- `native_optional`: the source may generate it and a natural result may be retained, but the shot does not depend on it;
- `post_only`: do not ask the picture-generation model to create the audible master; continuity or precise control belongs to post-production;
- `intentional_silence`: absence is part of the dramatic design.

Assign ownership case by case. Dialogue, impacts, footsteps, prop contact, ambience and music do not have universal defaults. A cup touching a table or a well-timed strike may sound better natively; cross-generation crowd murmur, room tone, recurring interface cues, score or narration may need post ownership when continuity and control matter. These are examples, not fixed category rules.

Audible ownership does not own the visible performance. Record these separately when relevant:

- `picture_cue`: the visible mouth, breath, contact, recoil or reaction that the picture must contain;
- `sync_anchor`: the observable start, peak/contact and stop points needed for later synchronization;
- `picture_sync_strategy`: `none`, `native_audio_driver`, `silent_performance_cue`, `guide_track_not_for_master` or `external_lipsync`;
- `post_handoff`: the exact line/effect identity, perspective and timing material needed in post.

A `post_only` dialogue master may still require exact dialogue text and mouth-performance timing in the source lock. Do not turn that text into an audible-generation request. Compile it only through an explicitly selected picture-sync strategy. If the platform cannot separate lip performance from synthesized speech, expose the mismatch and choose a guide-and-replace, external-lipsync, silent-performance or different-platform route. Do not delete the performance cue merely to keep the soundtrack clean.

For a scene spanning several generation units, define any required scene-level acoustic identity: source, density, distance, enclosure and motivated changes in perspective. The level may change with camera distance, doors, attention or point of view. Do not require ambience in every scene, and do not call a motivated reduction to silence a continuity error.

The downstream generator must receive the ownership plan. `post_only` means its **audible layer** stays outside soundscape/music requests; it does not erase an approved line, visible action or synchronization anchor needed to create the picture. If a platform cannot suppress unrequested audio, that limitation is reported rather than hidden.

Edit intent identifies the dramatic beat and required handles; it does not invent source timecodes before media exists.

## Auditory perspective and music dramaturgy

Voice delivery is not a soundtrack mood preset. Preserve the character's approved vocal identity while changing the interpersonal tactic and selected audible cues at a scene-supported trigger; coordinate these with the listening actor, body action and shot visibility under [director-decision-practice.md](director-decision-practice.md). Assign the perceptual foreground for each material phase: dialogue, action, ambience, music or intentional absence may carry it. Loudness, actor urgency and cutting speed are independent choices; neither whispered threat nor shouted danger is a universal recipe. This design does not change any layer's audible ownership.

Decide whose listening organizes a material passage and what sound reveals outside the frame. Hearing before seeing may create expectation; withholding a visible source's sound may express subjectivity or intentional silence. Establish why distance, enclosure, obstruction or attention changes the sound, rather than forcing one constant ambience volume. A sound bridge may connect or contrast spaces/times; check what simultaneity it implies.

Spot music by dramatic function, entry/exit and relation to dialogue/action, not by filling every empty interval. It may support, withhold, counterpoint or recur with changed meaning. Reserve silence and dynamic contrast; maximum loudness at every hit removes hierarchy. Preserve approved motifs and voice identities across scenes without copying one unvarying cue everywhere. No music genre is mandated by appearance family.

Choose source ownership using the existing plan, then route an actual standalone voice/effect/music request to [audio production](../../generation/references/audio-production.md). A post-only master stays out of the picture-generation audio request; it may be produced later as a separate authorized audio operation. Temporary music/voice used for timing is not cleared final material.
