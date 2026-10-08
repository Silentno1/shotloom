# Seedance 2.5 adapter

Primary authority: the [Jimeng official Seedance 2.5 manual](https://bytedance.larkoffice.com/wiki/RXh5ww6EqighMdkVTMccm2d4n7e), read 2026-10-02. It supersedes conflicting legacy third-party instructions. See [sources, mode envelopes and conflict rules](seedance-25-sources.md); use that register when a parameter or source distinction matters. These methods are specific to 2.5, not a template for H3, 2.0, Mini/Fast or Kling.

Support the documented capabilities regardless of which third-party platform currently exposes them. For prompt-only work, choose the model-native operation and intended references/settings; platform integration is not a prerequisite. Before an authorized submission, bind the actual host labels and verify its operation. Missing host support is an execution gap, not a reason to remove the branch or silently change the brief.

## Select the operation, then the control carrier

For extension, ultra-long generation, editing, white-model control or structured storyboard/keyframe work, read the corresponding section of [seedance-25-operations.md](seedance-25-operations.md). Ordinary generation uses the core methods below. Sound/language controls apply across these branches, not as an unverified standalone audio-generation endpoint.

| Intended task | Instruction scope and carrier |
| --- | --- |
| New video from text/images, including a 30-second sequence | Reference-role mapping, concise scene premise, ordered events, stable constraints |
| Accurate movement/performance/camera reference | Transfer the designated property and source range; describe differences and missing information |
| Ultra-long new video | Sustained global continuity plus stages, transitions and a planned ending; not repeated short-clip boilerplate |
| Continue an existing video | Preserve the source; describe the added segment and its join, not a rewrite of the source |
| Edit an existing video | Target/range, change, preserved state, sound treatment; optional frame annotations refine localization |
| White-model/previsualization rendering | Identify authoritative geometry/camera/blocking; map placeholders and supply absent appearance/scene detail |
| Storyboard/grid/ordered keyframes | Declare panel/frame order and roles; describe the temporal links that still images do not carry |
| Remove captions/BGM or change speech language | Specify the unwanted layer or exact speech change and everything that must survive |

## Core prompt construction

Use four conceptual parts, not compulsory headings or a fixed length: reference assignments; scene/task summary; observable events in playback order; remaining global constraints. Omit empty parts. Put a consequential task declaration (edit, extend, first/last frame) early. Choose one place for stable constraints rather than repeating them in every beat.

- **References:** identify which uploaded image/video/audio carries identity, scene, motion, camera, timbre or music. Use actual upload order and source ranges where relevant. Multiple views of one person remain one identity. A name printed on a picture is not sufficient binding.
- **Premise:** who is where, doing what, with the approved appearance and dramatic purpose. Do not import a demonstration's genre, famous film, lighting or sound merely because the manual used it.
- **Events:** action/reaction, attention targets, consequential contacts and state changes; framing, camera, focus, transitions and audible events when required. Include timing where it resolves a real dependency.
- **Global constraints:** stable identity/design/space, sound ownership, exact language, final state and relevant exclusions. Keep operator instructions, upload lists and provenance outside the pasteable prompt.

When the destination is unknown, use clear source names/roles in a native draft and list intended bindings outside it. The user confirms actual labels before external submission. Publisher examples and destination labels are not universally interchangeable; never carry Seedance labels into H3.

## Reference scope and detail density

Inspect the input before delegating to it. A precise finished motion/performance reference can carry its movement and ordering; state the allowed transfer, relevant range and differences rather than describing every joint again. Preserve decisive contact, reaction, outcome and exceptions required by the approved brief. A continuous action sequence benefits from its overall trajectory plus selected key moments, not either an empty “fight intensely” or a frame-by-frame motor program.

An incomplete white model needs missing character, scene, material, lighting, appearance and action information. A spatial/camera reference does not automatically dictate choreography. Explicitly distinguish “retain this path/layout” from “copy this movement”; a second reference may supply a bounded action or voice without replacing the first source's geometry or the approved identity. Do not treat all uploaded videos as equally authoritative or let one override every property.

For creative transfer, state the transferable mechanism (composition, movement, transition, rhythm or sound relationship) and the new subject/context. Do not copy the reference's story, cast, speech or aesthetic without authorization. Maximum input counts are not recommended counts; use the smallest sufficient set with clear roles.

## Performance and photographic realism

Across all appearance families, translate emotional intention into selected observable behavior: what the character attends to, what triggers the change, how eyes/body/face/voice coordinate, intensity and endpoint. Preserve mixed feelings and restraint when specified; do not impose subtlety on every scene. “Sad” alone is not a performance instruction, and adding tears to every sad beat is not an improvement.

For photographic work, ground the approved person in credible physical appearance, expression/action, clothing, environment and light/camera treatment. Use concrete visible cues instead of beauty-filter or quality-word stacks. Do not demand every realism dimension in every shot or transfer photographic skin/material instructions to 2D, standard 3D or three-render-two. The approved visual contract still determines appearance.

For precise gaze, crying, impact or bodily contact, retain trigger → visible action → consequence and the required scale. If exact movement is not carried by a reference, identify it as text-directed and review it; do not promise precision from a detailed description alone.

## Timing, camera and transitions

For a multi-beat clip, use timestamped stages when useful, while leaving simple shots in natural language. Stage boundaries follow state changes, not a quota or an equal-time grid. Second-scale timing is supported as a writing method; millisecond timecodes or a promised action frequency do not establish frame-accurate execution. Do not allocate five seconds to every strike or make a maximum-duration clip the default.

Reconcile the timeline with intended output duration, dialogue time, overlaps, transitions and ending. Parallel actions are not additive. A slow-motion interval, a camera move, an internal cut and output frame rate are different decisions. Preserve a moving exit if intended; do not append a freeze to every ending. For 30-second and ultra-long plans, see the operation guide.

Use familiar framing/movement terms alongside the visible intent: what moves relative to what, which subject becomes sharp, what is revealed, where the move ends. Translate unusual terminology into observable changes. Avoid simultaneous locked-camera/tracking demands unless clearly separated in time. For a transition, specify outgoing anchor, trigger, method/direction, incoming anchor and any required sound bridge; distinguish a cut/dissolve/occlusion from a continuous one-shot transformation.

## Sound, speech and language

Separate dialogue/voice, contact effects, ambience and score. Compile only the sound layers assigned to native generation under the source sound contract. “No BGM” does not mean mute; cup contact, footsteps, breathing or impact can remain native while scene-wide ambience/score is post-only. Do not place post-only layers in the audible request, and preserve approved silent picture-sync cues separately.

Bind timbre references to the intended speaker, distinct from line content, language, emotion and delivery. The official manual supports audio-only reference input; do not import H3's different input rule or infer a standalone audio output mode. With several speakers, identify who speaks when and prevent unwanted voice/reference transfer. Keep exact approved speech/lyrics and intended language; for deliberate multilingual dialogue state the language per speaker/segment and do not contradict it with a global single-language ban.

For unwanted subtitles/on-screen text, dialogue, sound effects or BGM, specify the relevant exclusion only. Required story text must survive a ban on added captions/watermarks. Removing existing BGM/captions is a separate edit task; see the operation guide. Prompt wording and a feature announcement do not prove clean separation, silence, lip sync or exact timbre.

## Review against the approved brief

Before delivery check the selected operation, reference assignments, missing information, temporal causality, camera consistency, exact words/language, sound ownership and endpoint. Check the official manual's mode-specific envelope without turning recommendations into rejection rules. A model-native prompt-only plan is not a verified platform submission.

After generation, review actual identity/design, spatial continuity, movement/contact, performance, timing/cuts, speech and sound. For reference transfer assess the requested property rather than resemblance alone. For edits/extension inspect preserved parts and join/range boundaries; for grids verify order and omitted/merged panels. Documentation coverage and passing local checks are not evidence that a generated clip meets artistic acceptance.
