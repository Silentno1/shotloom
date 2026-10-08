# Seedance 2.0 adapter

Authority: retained Jimeng manual and scope in [model-manual-authority.md](model-manual-authority.md). Applies to full Seedance 2.0, not automatically Mini/Fast or 2.5. Check the exact current host before submission.

## Route the task before writing

- Text/new generation: natural-language scene, subject, action development, camera and approved audio. No mandatory H3 section schema or English rewrite.
- Exact opening/ending image: use the host's verified frame mode and describe movement from/to those actual states. The Jimeng manual distinguishes 首尾帧 from 全能参考; multiple modalities require the latter there, not a guessed universal button name.
- Multimodal reference: bind appearance, scene, action, camera, effects and audio to their actual sources. State whether the source is reference guidance, an edited original or a continuation source. A video used for camera movement is not automatically a video-edit task.
- Editing: identify source video, changed span/content and preserved content. Do not regenerate all successful details merely because a prompt was rewritten.
- Extension: distinguish original duration, added duration and final total. The manual's explicit instruction selects the **newly generated part's** duration; one demonstration's ambiguous “extend to” wording does not override that. Confirm the host's operation semantics.

## Native expression

The manual uses natural Chinese or other natural-language description with `@`-bound material references. Its examples include both continuous prose and timed sections; timestamps are available, not compulsory for every simple action. Preserve chronological/causal transitions. For a complex action already supplied by a suitable video, name the desired action/camera transfer and exceptions rather than replacing the reference with speculative mechanics.

For each source, identify the target subject and transferred property: identity is different from costume, location from camera path, and voice timbre from dialogue content. Repeat a reference where it actually disambiguates a stage; do not scatter labels as decoration. A voice reference does not authorize copying its spoken words. Storyboard order must be explicit if order matters; it does not prove exact frame matching.

The publisher manual uses `@`-bound material. Other destinations may use different labels; keep intended roles explicit until the user supplies binding evidence. Never inherit another operator's labels or indices. Labels are not file uploads. See [destination bindings](destination-bindings.md).

Keep the director's decisive interaction, reveal and ending; remove generic camera-brand praise and repeated style text before required content. Do not infer “long is better” from elaborate canvas prompts or “short is better” from another model's keyframe task. For performance, name the perceivable change and its target, not just an emotional adjective; the required detail depends on what approved references already carry.

## Envelope and sound

Retained manual baseline: output 4–15 seconds; up to 9 images, 3 videos with total 2–15 seconds, 3 audio files totaling at most 15 seconds, and 12 mixed files. Input format/size/resolution and compliance restrictions belong to the exact dated surface; recheck before relying on them. Read the known catalog discrepancy in the authority index, not a silently merged envelope.

The manual demonstrates synchronized speech, effects/music references and continuous audio; demonstrations do not override the source sound partition. Ask only for generation-owned layers. For a host audio-off control, verify that switching it off does not remove required native dialogue/effects. Post-owned room tone or score stays outside the generation request; unwanted automatic audio still requires listening and cleanup.
