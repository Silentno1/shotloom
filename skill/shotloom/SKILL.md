---
name: shotloom
description: Direct an identified AI film, drama or scene through story and visual design, model-native prompt planning, actual-media review, continuity, iteration and editing handoff. Use for concrete production work, not general film questions or model names alone. Does not call generation services or publish.
license: MIT
metadata:
  version: "0.2.1"
---

# Shotloom

Shotloom directs AI filmmaking through planning, actual-media review and iteration. Its directing, visual, generation-planning, review/continuity and edit/delivery workflows share one portable package. Prompts are compiled artifacts inside that loop, not its entire product.

## Boundaries and environment

Read [environment](references/environment.md) when establishing tool availability, storage or a handoff. Use the user's current authority and authorized scope; a local question does not activate all five modules.

- No generation service calls, provider selection, uploads, credentials, credits or publication. Deliver a native prompt and intended setup; the user returns actual results.
- File writes and local edits need explicit scoped authorization. A read-only request never creates records or handoffs.
- No prerequisite notebook, private manual, installed sibling skill or account. Resources are relative to this folder.
- Python and media tools are optional enhancements. Without them, use the same decisions as copyable Markdown, and state which checks or observations are unavailable.
- A prompt is intent. Only explicitly accepted actual evidence can become continuity authority. A declared hash or passing schema does not authenticate approval or quality.
- Preserve user-approved identities, story facts, exact words, visual locks and rights. Read [safety and rights](references/safety-and-rights.md) when applicable.
- Do not read unrelated projects or promote one user's preferences and accepted exceptions into universal rules.

## Route only the work requested

| Task | Internal module | Important return path |
| --- | --- | --- |
| Story diagnosis, method, scene, acting, camera, action or time | [Director](modules/director/WORKFLOW.md) | Unresolved story or audience meaning stays here |
| Production method, appearance, assets, space, light/color | [Visual design](modules/visual-design/WORKFLOW.md) | Design choices do not approve actual assets |
| Model choice, references, image/video/audio prompts or repair planning | [Generation planning](modules/generation/WORKFLOW.md) | Unsupported controls return to the owning design, never silently weaken it |
| Actual images/video/audio, asset approval, failures or accepted state | [Review and continuity](modules/review-continuity/WORKFLOW.md) | Inspect first; accept separately; only then propagate state |
| Timed previs, selection, cut, sound/post or delivery checks | [Edit and delivery](modules/edit-delivery/WORKFLOW.md) | Selected cuts and changed exports need their own review |

Read each selected module's `WORKFLOW.md` and only its applicable references. A named module is a folder in this package, not another skill to install. Tools shown under a module's `scripts/` resolve from that module.

## Establish and carry the method

Formal production uses one coherent approved directing method, from either a named reference or a project-authored method. Follow the shared [method selection](modules/director/references/director-selection.md). No famous director, catalog scoring or external research is mandatory for a user-authored method. Whole-work choices require the complete authoritative scope; local work inherits approved decisions.

Separate story facts, narrative function, director variables and exact locks. Keep directing method, appearance and model syntax independent. A model switch recompiles the same source lock; it does not redesign the work.

## Core decision loop

1. Establish the current task, authority/version, relevant locks, evidence and capabilities.
2. Design only the missing decisions; preserve the approved method and story.
3. Plan the smallest sufficient assets, references and production units.
4. Compile image/video/audio independently from the same source lock using the exact model/mode adapter.
5. Return a copy-ready prompt, intended settings/bindings, risks, observable checks and the expected next state. External generation remains the user's operation.
6. Review the actual returned source, selected interval and accessible modalities. Distinguish observation, severity and treatment.
7. Recommend retain, repair then review, regenerate affected unit or unverified. Trace the earliest evidenced failure; preserve successes and change one principal variable when diagnostic.
8. After explicit acceptance and authorized recording, update observed continuity. An upstream replacement makes affected downstream material stale until resolved.
9. Select actual source ranges for editing; source acceptance is not whole-cut approval. Preserve events, sound ownership, versioned turnover and final verification.

See [core workflow](references/core-workflow.md) for orchestration, [production state](references/production-state.md) for file-backed or conversation-only records, and [artifact templates](references/artifact-templates.md) only when a stable record is needed.

## Models and evidence

Use [model routing](references/model-selection.md) to distinguish detailed adapters, limited guidance and unsupported versions. Do not load every adapter, transplant proprietary syntax or claim dated baseline facts were freshly verified. Source dates and limitations are in the [manual register](modules/generation/references/model-manual-authority.md) and [source policy](references/source-policy.md).

## Supporting routes

[Story development](references/story-development.md), [voice/dialogue](references/voice-and-dialogue.md), [take review](references/take-review.md) and [post handoff](references/post-production-handoff.md) remain compact entry routes. They point to the maintained module authority rather than introduce competing rules.

Optional helpers check explicit structure, timing, source bindings and dependency validity. They cannot certify actual viewing, listening, creative success, identity rights or user approval. When running is unavailable, do not turn a required decision into a required software dependency.
