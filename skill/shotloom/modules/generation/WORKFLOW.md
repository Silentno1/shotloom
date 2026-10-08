> Shotloom module, not a separately installed skill. The package [entry](../../SKILL.md) and [environment contract](../../references/environment.md) govern permissions, tool availability and storage. Formal methods may be named references or user-authored; see the shared method-selection contract.

Script checks below are optional tool-assisted forms of the same decisions. Without Python or required media tools, use the documented manual checks and mark unavailable evidence; do not invent a machine pass or block unrelated planning.

# AI Media Generation

Compile an approved creative contract into a model-native prompt/operation plan. Return intended settings and a user verification checklist; the user performs external generation and returns the result. This module never uploads, submits, spends credits or operates accounts.

Keep documented model capabilities and writing methods independent of third-party feature exposure. Skill maintenance, capability explanations and prompt-only planning do not require a live host or API. If the destination is unknown, deliver a clearly labeled model-native plan with intended settings/reference roles; resolve host bindings and available controls before submission. Do not remove a documented capability because one host lacks it, or claim an unverified host can execute it.

Formal production prompts and operations require the current authorized director-style lock and matching artifact reference under [director-selection.md](../director/references/director-selection.md). `scripts/source_lock_check.py` calls the shared gate for image, video and production audio. A concept-level label alone does not bypass selection. Explicit non-production selection-test plans use its bounded exploration branch; any recorded generation authorization concerns the user's external operation, never service access by Shotloom. Explanation/diagnosis remains available without a production packet. Compile observable methods, not a director-name incantation; keep model-specific official syntax and the separately selected appearance family.

For standalone voice, ADR, narration, effects, ambience or music operations, read [references/audio-production.md](references/audio-production.md). Use its audio source lock and exact tool evidence instead of image/video appearance requirements; do not run video-specific adapters on an audio job.

## Task modes

- **Explanation or diagnosis:** answer the specific operation/adapter question or inspect the supplied prompt. Read only the relevant adapter or failure guide; for video-model comparison, use [references/video-model-selection.md](references/video-model-selection.md) and only the relevant profile/adapter branches. Do not require a full production packet, rewrite the prompt, generate media or create project records.
- **Local prompt revision:** reuse the current source lock and accepted brief; read only affected adapter/reference sections and revalidate affected fields plus their dependencies. Preserve exact dialogue, reference bindings and sound ownership. Missing material inputs require clarification, not a restart of the whole intake.
- **New compilation:** use the entry gate and applicable checks below. Shotloom produces the plan, not the remote generation. Preserve any authorized project attempt bounds without creating or spending an extra allowance. Do not ask again for unchanged internal planning steps already authorized.
- Reuse equivalent successful checks only while source lock, prompt, relevant settings, validator and consequential platform evidence remain valid. Do not skip final consistency checks on a changed operation or claim a diagnostic fragment passed full production validation. Follow user file-write and project handoff boundaries.

## Entry gate for new compilation or generation

Require:

- production level: `concept`, `continuity` or `formal`;
- authority and exact locks;
- observable director contract;
- production method/final appearance for image/video, or the audio brief for standalone sound;
- reference roles whose approval state is allowed by that production level;
- intended endpoint and review criteria;
- actual platform/model/interface when known.

Missing information that materially changes the operation must be identified, not silently invented.
The generation packet is a versioned compilation snapshot of those authorities, not a replacement source of truth.

## Workflow (new compilation; select affected steps for revisions)

The numbered workflow below covers image/video compilation. Standalone audio uses the linked audio workflow and common authority/reference/evidence checks, not appearance compilers, video adapters or picture-generation audio partitions. Return the audio brief and intended settings for the user's external operation; compare supplied readback without submitting anything.

1. Route by the current task using [references/platform-routing.md](references/platform-routing.md). When choosing or materially reconsidering a **video** model/mode, use [references/video-model-selection.md](references/video-model-selection.md) and its dated profiles: filter hard operation requirements, distinguish task fit from quality evidence and host readiness, then carry the choice rationale, risks, review targets and conditional fallback into the existing plan. Reuse a still-valid choice for the same scene/group; this is not automatic switching, a paid comparison or a new gate for image/audio work. Model claims must be `official-current`, `interface-observed`, `project-verified`, `community-observation` or `unknown`.
2. Plan units with [references/generation-units.md](references/generation-units.md). Optimize for causal clarity, control and reviewability—not for the fewest operations at any cost.
3. Build the smallest sufficient reference manifest. Every asset has one role, approval state, allowed transfer and forbidden transfer. Pending references are allowed only for `concept`; recurring `continuity` and release-bound `formal` work require approved authorities. Check actual reference-file geometry against the active operation's evidenced input limits as described in `references/platform-routing.md`; output video ratio and a passing remote plan check do not validate reference image dimensions.
4. Build or reuse a source lock, transcode from that lock rather than from another model's prompt, and apply the diagnosis/repair gate in [references/source-lock-transcode-repair.md](references/source-lock-transcode-repair.md). Run `scripts/source_lock_check.py` for a new or changed lock before compilation; do not rerun an equivalent valid check for an unchanged lock.
5. Preserve the open appearance contract under [appearance-family-routing.md](../visual-design/references/appearance-family-routing.md), including custom looks and mixed-layer ownership. Load an appearance-specific compiler only for the approved operation/layer that requires it. For `three_render_two`, read [references/three-render-two-compilation.md](references/three-render-two-compilation.md); never infer that family from broad style words or impose it on an entire mixed-media work.
6. Read the exact adapter and its applicable manual baseline in [references/model-manual-authority.md](references/model-manual-authority.md). For H3, read [references/minimax-h3.md](references/minimax-h3.md) completely; for Seedance, route through [references/seedance-seedream.md](references/seedance-seedream.md) to the exact version. Seedance 2.5 uses the current Jimeng official manual over conflicting legacy third-party guidance; its adapter routes to operation-specific methods. For Kling 3.0 video/image, Omni/O3, Turbo or motion control, use [references/kling-3-series.md](references/kling-3-series.md) and only the selected mode's references. Wan 3.0 uses [references/wan-3.md](references/wan-3.md), including mode-exclusive inputs and unresolved extension-duration semantics. Midjourney, Nano Banana and GPT Image 2.5 use [references/image-platforms.md](references/image-platforms.md) to load the exact image/version adapter. Identify model variant and input mode before choosing detail density; bind host-native syntax when the destination is known, and before submission. A canvas example never overrides the corresponding manual.
7. Compile the pasteable prompt with [references/prompt-compilation.md](references/prompt-compilation.md), including its performance-compilation check when the operation contains character acting. Preserve the director's observable performance development and intensity limits. Keep operator instructions and upload lists outside it.
8. Compare the compiled operation back to the source lock. Run `scripts/sound_contract_check.py` when a sound partition is present or required, `scripts/platform_evidence_check.py` for consequential capability claims, the exact adapter validator when one exists, and `scripts/appearance_coverage_check.py` when an appearance-coverage packet is used. Inspect each check's scope: sound `unverified` requires a semantic review, not a pass, an automatic rewrite or a paid retry. Recheck affected dependencies after changes; do not create unrelated packets just to run every validator. `prompt_structure_check.py --platform generic` is deliberately non-passing because it cannot validate a proprietary interface. A pass does not prove artistic quality.
9. For user verification before external submission, compare the final prompt/timing plan with available settings/reference evidence using [references/operation-reconciliation.md](references/operation-reconciliation.md) and [destination bindings](references/destination-bindings.md). If no evidence is supplied, deliver intended settings outside the prompt and mark bindings unverified; do not connect to a platform. The optional checker detects declared discrepancies, not semantic correctness, actual observation or model capability.

## Rules

- Never transfer syntax, limits or reference labels between platforms.
- A model change may alter expression, density, settings and supported controls; it may not silently alter creative facts, spatial logic, exact locks or accepted state.
- Compile each target independently from the same source lock. Do not translate one target-native prompt into the next.
- Appearance-family rules are conditional, and examples are not a closed style list. Photographic, hand-drawn 2D, standard 3D, stop-motion, motion graphics, mixed-media and custom work keep their approved contracts; they must not inherit three-render-two requirements. In a mixed work, those requirements apply only to its explicitly authorized three-render-two layer/sub-operation, never to the whole composite by default. The ability to represent a style is not evidence that every model can realize it.
- When asked to check only, diagnose without rewriting. A rewrite or retry must be explicitly requested.
- Never use a stale product fact without labeling and rechecking it when consequential.
- No arbitrary prompt-length cap. Enforce a limit only when a current official source or the active interface establishes it.
- Do not treat a keyword checklist as semantic validation.
- Duration is chosen for the causal unit and platform envelope. Maximum duration is not a target.
- Internal cuts or framing changes do not automatically require separate generations.
- One dense phase has one high-risk precision owner; support or simplify competing exact demands.
- The source lock always preserves exact dialogue and visible text in the requested language. Prompt output preserves them according to the adapter and the approved picture-sync strategy.
- Respect the source sound-ownership plan. Never place a `post_only` audible layer in soundscape/music requests, but preserve any separately approved picture cue, exact line timing or synchronization anchor needed for the image. Never assume native audio should always be kept or always be replaced.
- Actual generated media must be reviewed by `review-continuity` before production acceptance; a prompt-only answer does not trigger media review. Generation success never writes canon.
