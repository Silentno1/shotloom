# Seedance 2.5 operation methods

Read the selected branch with the [core adapter](seedance-25.md). [Official source and mode envelopes](seedance-25-sources.md) govern conflicts. These are prompt/control methods, not invented API fields; a third-party host's missing entry does not delete them. Preserve the approved director, visual, story and sound contracts in every branch.

## New clip and 30-second sequence

Use ordinary generation for a new causal unit within its documented range. A 30-second unit may contain several events/internal cuts, a sustained shot or changing speeds; it is not necessarily one slow action or one generation per shot.

1. Establish stable people, space, appearance, starting state and sound ownership once.
2. Organize the action into meaningful stages; carry state forward between them. Choose durations from actual events/dialogue, not a fixed number of sections.
3. Describe changes in framing, camera, focus, performance and sound at the relevant event. Make contact/reaction and reveal dependencies explicit.
4. End in the required state and motion, with any authorized edit handles. Check that the final beat fits the intended duration and does not contradict global constraints.

Useful scaffold (omit unused slots): `素材用途 → 场景与全局约束 → [时间段：事件、人物反应、镜头变化、原生声音] → 结束状态`.

Inspect static-to-moving transitions and simultaneous camera/character requests. Do not copy a demonstration's exaggerated movement, long opening or music into unrelated scenes. A timeline is a planning aid, not a guarantee of second/frame-perfect output.

## Ultra-long new video

The official ultra-long branch is distinct from ordinary generation and source extension. Its documented 30–180-second range is not a reason to label a 120-second plan invalid under the ordinary 30-second ceiling, or to claim a third-party ordinary endpoint can run it.

Build a sequence-level plan: global cast/design/voice/space anchors; chronological stages and local objectives; transitions and state carried between stages; dialogue/music/ambience progression where native-owned; planned ending and total duration. References can be assigned by stage/property rather than indiscriminately to the whole sequence. Maintain cause and effect between scenes even in a montage.

Spend detail on decisive changes and difficult joins; do not expand every second into equal blocks or repeat all global constraints in each stage. Reconcile local event times with the total and provide a legible progression over the full duration. A 60-, 90- or 120-second example does not establish an optimal duration or universal shot count.

Choose this branch when a sustained multi-stage result is actually wanted. Separately controlled shots remain appropriate when the approved precision/review needs call for them, but do not force fragmentation merely because one host lacks ultra-long mode. Report the execution gap and preserve the plan until an authorized path is selected.

Review continuity/drift across the entire result, omitted/repeated beats, time compression, transition logic, voice/sound continuity and ending; a few opening frames cannot establish long-sequence quality.

## Video extension

Bind the actual source video and distinguish source duration, added duration and expected final duration. The official workflow accepts a source no longer than 30 seconds and adds 4–30 seconds; a 30 + 30 operation can therefore yield 60 seconds. Iterative extension is possible only while the next source still satisfies the source-duration condition; this is not unlimited chaining or the same as ultra-long generation.

Treat source content as preserved and the prompt as instructions for the added interval. State the source's actual final pose/position/gaze/motion, camera/framing, light/time, carried props and relevant sound state, then what continues or changes and the new ending. Inspect the source before claiming those details. If continuing a time-coded plan, explicitly identify whether times are relative to the addition or absolute on the combined output; convert consistently instead of mixing clocks.

Useful scaffold: `承接指定源视频结尾；新增部分时长与计时基准；由现有状态发生的动作/镜头/声音变化；新增部分结束状态；需要保持的要素`.

An extension may continue motion or use a planned scene transition. Specify outgoing/incoming anchors and the intended transition instead of restarting the characters in a generic setup. Prompt instructions for the new segment do not authorize rewriting the preserved source. An intentional change of time/place must have an approved transition; accidental daylight/night, screen-direction or sound-bed jumps remain defects.

Review the source-preservation claim, final measured duration, visual/audio seam, continuity of movement and carry-forward state. For another extension, check the resulting source duration again. Do not pad one hit to the entire extension just because a minimum added duration exists; plan the surrounding authorized causal unit or an appropriate edit, not slower impact by default.

## Video editing, local annotations and retakes

First decide whether this is a new clip, an extension or a bounded transformation of an existing clip. For an edit bind the source, locate the target and time range, describe the change from existing to desired state, and declare what must remain unchanged. Choose whole-video vs bounded-interval scope explicitly. A selected frame identifies a target; it does not by itself establish the requested temporal scope.

Useful scaffold: `源视频及范围 → 目标定位 → 从原状态改为目标状态 → 保留人物/构图/运镜/动作/节奏等必要项 → 声音修改或保留要求`.

- **Text-directed edit:** identify a unique target through approved visual/spatial anchors, not merely “change this.” Separate an object/wardrobe/background replacement from an action or camera rewrite.
- **Frame annotation:** where available, a box, arrow, point or drawing localizes an edit at a selected frame/time. Pair the actual annotation with prose specifying target, change and time coverage. Preserve colors/markers as annotation identifiers, not newly generated story objects. Do not fabricate a mask API or infer whole-clip tracking quality from one marked frame.
- **Reference-assisted edit:** declare what the additional image supplies and which source properties remain authoritative. Do not let replacement identity or styling transfer unrelated composition/motion.
- **Multiple changes:** resolve interacting requests and target ambiguity before combining them; do not scatter contradictory “keep everything” and “change the whole scene” directions.

The official descriptions include smart editing plus advanced/video-editing interaction. Their names/UI routes are not universal third-party endpoint identifiers. Use the documented semantic operation now; only actual execution needs the host's current entry and reference support. Legacy legacy host region-reshoot billing or layout does not govern this operation.

Review edited and supposedly preserved regions, temporal consistency, tracking at occlusion, range boundaries, original action/camera/timing and retained audio. Do not accept a locally correct screenshot as proof that the full video was repaired. The manual's shorter-edit recommendations concern reliability, not a fabricated hard rejection limit.

## Caption/BGM removal and other audio edits

Separate prevention during new generation from removal in an existing clip. For removal bind the source and unwanted layer/region/range; identify what must remain (story text vs added captions; dialogue, breath, contact sounds and ambience vs music). A broad “remove all sound/text” is wrong when approved content must survive.

For existing BGM removal, request removal of music while preserving designated voices/effects/ambience, and review the whole audio track for remnants, lost transients, voice artifacts and synchronization. The official capability claim does not prove lossless separation. Do not claim to have listened when only frames/text were inspected.

For speech replacement or multilingual content, bind speaker/timbre, exact text, target language, delivery and relevant time scope separately. Preserve everything not authorized to change, including other speakers. New lyrics/music requests must remain within native ownership; post-only score stays out of the generation prompt. If a guide track is for synchronization only, distinguish it from a master-audio request.

## White-model / previsualization rendering

The official manual distinguishes coarse and more detailed control inputs. Identify what the actual white model carries: geometry/scale, spatial layout, camera path/framing, actor blocking/motion, timing or lighting changes. Do not infer all of them merely from a file labeled “white model.”

- **Coarse input:** describe the missing scene construction, target characters, materials, light, appearance and required action, while retaining the specific geometry/camera/blocking that the source does establish.
- **Detailed input:** delegate the inspected layout/movement/camera/timing to it and describe authorized substitutions/appearance and remaining gaps. More input detail can reduce repeated prose, not remove the need to identify transfer boundaries.
- Map each placeholder/body/color/object to its intended character or prop. Distinguish scale and position from final identity/design; maintain subject count and path relationships when locked.
- If another video supplies only one action interval, identify that interval and its property. It must not silently overwrite the spatial/camera source, bring in another identity, or restart the scene at its first pose.
- Describe whether light/camera/motion is retained or replaced. “Follow the camera exactly” and a new contradictory camera path cannot both stand.

Useful scaffold: `控制视频保留项 → 占位体与成片对象映射 → 其他素材各自用途/区间 → 补全场景、外观与声音 → 允许变化及结束状态`.

The final appearance can be photographic, 2D, standard 3D, three-render-two or another approved family; white-model input does not force a 3D-looking result. Maya/Blender plugin export is one documented input-preparation route, not a dependency that must be installed for every prompt. Its separate linked plugin manual was not read in this integration; do not invent plugin operations or claim metric/pixel-exact control.

Review camera trajectory/framing, preserved spatial relations/scale, paths/contacts and the desired render appearance independently. Attractive rendering is not evidence of correct blocking.

## Storyboards, grids and ordered keyframes

Determine whether the input is an identity sheet, a storyboard, a complete concept sequence, a first/last-frame pair or ordered keyframes. A grid is not automatically a temporal instruction. State panel order, which panels belong to which events, and what is a reference versus an exact starting/ending state.

For a sparse line storyboard, supply missing character/scene/material/light/appearance and the causal movement/camera between panels. For a sufficiently complete concept sequence, delegate the visible composition/state and explain timing, transitions, acting and sound not carried by still images. Preserve continuous action across panel boundaries instead of generating a slideshow of static poses.

Declare a required start/end or ordered-frame task early, keep individual uploads in the declared order, and use the actual mode at execution. Several views of one character are not several shots/characters. The official grid examples do not impose nine panels universally; neither the legacy “fewer than 15 panels” suggestion nor a host upload maximum is a guaranteed panel-following limit.

Review omitted, merged, reordered or invented beats, transition logic, spatial/identity continuity and final state. Numbers/labels on a planning grid are instructions, not required on-screen text unless the approved story says otherwise.

## Branch-level final checks

Check operation scope first: new sequence, added interval, bounded edit or reference rendering. Then inspect source roles, exact content, retained state, timeline/clock, sound ownership and ending. Consult the source register for limits only in the relevant branch. Distinguish official documentation, current host readiness and actual reviewed output; none substitutes for the others.
