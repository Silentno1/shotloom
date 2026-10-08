# Source lock, transcode and repair

## Source lock

Before model syntax is introduced, assemble one versioned generation snapshot from the authoritative screenplay/current continuity, director contract, visual bible and approved asset records. This snapshot is a handoff packet, not a new authority that may overwrite its sources.

Bind the current director-style selection as specified in [director-selection.md](../../director/references/director-selection.md): `workflow_scope`, independently resolved `current_authority`, `director_style_lock` and the artifact's `director_style_ref`. Resolve the current lock from its actual authority before comparing the artifact's original ID/version/hash. Never refresh a stale binding silently to make a check pass. `source_lock_check.py` enforces this shared structural gate even when production_level is concept; only explicit, bounded selection_exploration is exempt. Diagnostic fragments are not executable production packets. Keep the chosen methods in relevant observable directing/visual/review fields; these metadata keys are not model API settings and the platform need not expose a director preset.

Record only fields relevant to the operation:

```text
authority_sources_and_versions
production_level
fixed_story_facts_and_current_state
story_beat_current_action_and_required_endpoint
character_identity_blocking_and_object_contact
performance_contract_when_character_acting_is_material
space_topology_visual_center_and_layering
camera_position_path_focus_and_internal_cuts
motivated_light_color_and_material
appearance_family_base_lock_and_contract_version
shot_appearance_delta_and_dimension_disposition
reference_manifest_with_roles_and_priority
exact_dialogue_and_visible_text
sound_ownership_plan
must_preserve
allowed_delta
forbidden_substitution
platform_or_interface_facts_with_evidence_level
review_criteria_and_open_unknowns
```

Do not fill irrelevant fields for completeness. If two authorities conflict, identify the conflict and route it to the owning skill or user; a compiler may not choose a new story or visual answer.

For a beat with a director-defined creative carrier, preserve it inside the existing action/camera, `must_preserve` and review fields: intended audience effect, the concrete relationship carrying it, visibility condition and acceptable variation. Its design authority is [scene-direction.md](../../director/references/scene-direction.md); compilation does not invent one. Distinguish required meaning from an optional cue and an exact execution lock. Do not introduce a new mandatory schema or force every operation to have a special visual device.

For multi-opponent action or scale-critical imagery, preserve the relevant optional decisions inside the existing action/spatial/review fields: attention and threat changes, participants' causal positions/actions, carried damage or resources, comparison anchors, relative size/support, reveal and permitted environment response. These are semantic requirements, not new API keys or mandatory fields for every operation. Missing consequential decisions return to the owning director/visual skill; do not invent an opponent, victory, destruction or reference object while compiling. The structural source-lock checker does not establish the completeness or readability of these decisions.

When acting is material, carry the director-owned `performance_contract`: entering state and objective, perceived trigger, intended outward expression/ambiguity, observable development and intensity limits, selected attention/face/breath/body cues and their timing relationships, endpoint, required/optional cues and review criteria. Preserve this semantic content under the project's existing representation; no new proprietary platform field is implied. `source_lock_check.py` does not validate acting completeness or emotional credibility. Compare this contract manually during compilation and actual-media review.

For each material sound, `sound_ownership_plan` records an identifier, category, continuity scope and exactly one `audible_ownership`: `native_required`, `native_optional`, `post_only` or `intentional_silence`. When picture performance depends on it, separately record `picture_cue`, `sync_anchor`, `picture_sync_strategy` and `post_handoff`. These fields describe ownership and control, not quality: actual native audio remains candidate material until reviewed.

`production_level` is `concept`, `continuity` or `formal`. Concept work may use explicitly pending references. Continuity and formal work may bind only inspected, approved references for recurring identity, space, props, voice and other hard continuity authorities. Never let a pending reference silently enter release-bound work.

For deterministic validation, serialize the relevant source lock as JSON. `reference_manifest` is an array of objects with `id`, `approval_state`, `primary_role`, `allowed_transfer`, `forbidden_transfer` and `priority`. `sound_ownership_plan` contains `sound_events`, `compiled_generation_audio_ids` and `post_handoff_ids`; an event may add exact `audible_prompt_markers` for leakage checking. Run `scripts/source_lock_check.py` before compilation and `scripts/sound_contract_check.py CONTRACT --prompt PROMPT` afterward. Passing proves the ownership and approval partition is internally consistent, not that the creative choices are good or that paraphrased leakage is impossible.

Declare `media_type: image` for static image operations, `video` for audiovisual operations, or `audio` for standalone sound; omitted legacy packets retain video requirements. Image locks may omit the sound plan or carry its empty form, but must not bundle future-video sound events into the current image operation. Video locks retain sound partition validation even for an intentionally silent pass. Audio locks follow [audio-production.md](audio-production.md), without an appearance requirement or a picture-generation sound partition. Do not infer the type from words such as portrait or anime.

The checker uses literal top-level keys `production_level`, `authority_sources_and_versions`, `appearance_family`, `required_endpoint`, `review_criteria`, `reference_manifest` and the applicable `media_type`/sound plan. The earlier inventory names describe semantic content, not alternate JSON key spellings. Preserve richer creative content under the project's existing representation rather than forcing all prose into these minimum structural fields.

Sound checking separates partition consistency from prompt coverage. The report lists `checked`, `not_checked`, `errors` and `unverified`; `passed_scoped_checks` is not a semantic or audio-quality approval. H3 literal checks include tagged dialogue in either timeline as well as sound/music fields. Natural-language prompts (including Seedance), untagged timeline mentions, negations, silent mouth cues, guide-track contexts or absent markers may return `unverified` (CLI exit 3), not a false pass or automatic leakage rejection. Actual errors return exit 2. Do not move H3 dialogue into soundscape to satisfy a checker. Review unresolved meaning against the source lock, record the scoped finding in the existing handoff, and keep source listening separate; do not merely relabel the script result as passed.

If `native_required` is unsupported by the active model or interface, expose the capability mismatch and choose a permitted control or production route. If `post_only`, do not depend on the generated audio as master and do not silently convert it to `native_optional`. Post-only dialogue may still drive visible mouth timing through the declared picture-sync strategy.

The appearance family is explicit. Broad words such as `anime`, `animation`, `cinematic`, `stylized`, `cyberpunk`, `2D` or `3D` do not activate a family-specific compiler. Carry only the selected family's base lock and current shot delta.

## Transcode

For every target model:

1. Start from the same source lock, not from another model's finished prompt.
2. Let the adapter change ordering, clause density, native labels, supported settings, exclusion form and edit wording.
3. Keep story facts, current state, action, performance intent/development/intensity limits, visual center, space, camera relationship, motivated sources, appearance family/base lock, exact text/dialogue, sound ownership, endpoint and explicit restrictions invariant unless the user approved a change.
4. Compare the compiled operation back to the lock. Report any unsupported requirement or unresolved interface dependency rather than silently weakening it.

Prompts for different models should look native to their models while remaining traceable to the same creative and continuity authorities.

## Prompt diagnosis

When the user asks only for a check, do not rewrite. Report the few findings that most affect execution and separate:

- **upstream contract failure:** story beat, blocking, topology, camera, light, appearance or endpoint is missing or contradictory;
- **compilation failure:** repetition, lost invariant, ambiguous reference role, mixed adapter syntax or impossible priority;
- **platform uncertainty:** a required control or limit is not verified in the actual model/interface;
- **cosmetic symptom:** generic praise words or decorative polish caused by a deeper structural failure.

Do not diagnose prompt length or missing style adjectives when the real issue is an absent physical or narrative relationship.

## Repair gate

Repair instructions require evidence from the actual result through `review-continuity`.

- If the source contract is sound and the failure is local, issue a retry packet with one principal `change_scope`, a list of `locked_successes`, expected observable improvement and a stopping/escalation condition.
- If story, blocking, topology, camera logic, appearance authority or required endpoint is wrong, return to the owning upstream contract and rebuild the generation snapshot. Do not stack cosmetic wording onto a failed structure.
- If the model or interface lacks the required control, change control method, unit boundary, reference plan, platform or editorial strategy rather than pretending prose can guarantee it.

Never allow a repair to redesign successful identity, wardrobe, props, space, light, timing or state merely because the entire prompt was rewritten.
