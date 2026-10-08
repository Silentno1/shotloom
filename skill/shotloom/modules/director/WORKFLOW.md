> Shotloom module, not a separately installed skill. The package [entry](../../SKILL.md) and [environment contract](../../references/environment.md) govern permissions, tool availability and storage. Formal methods may be named references or user-authored; see the shared method-selection contract.

Script checks below are optional tool-assisted forms of the same decisions. Without Python or required media tools, use the documented manual checks and mark unavailable evidence; do not invent a machine pass or block unrelated planning.

# AI Drama Director

Create a platform-independent directing contract. Keep story facts and user-approved locks intact; improve only director-owned variables.

## Scope boundary

This skill owns screenplay and scene diagnosis; dramatic objective and endpoint; performance, blocking, camera, stylized action, transition, sound and edit intent; and a coherent whole-work method bible.

Route production-method and look work to `visual-design`, model selection and prompts to `generation`, actual-media review and canon writes to `review-continuity`, and source editing or delivery to `edit-delivery`.

## Choose the task scope

- For a local question or adjustment, use the named scene/shot, relevant established locks and the immediately needed context. Return the requested diagnosis or delta, not a full director package.
- For scene direction, build the relevant scene contract. For a new or substantially revised whole-work method, read the complete authoritative work and build one method bible; never infer a whole-work method from selected excerpts.
- Reuse current approved decisions already in context. In this workflow, confirm means establish from evidence; ask the user only when ambiguity or a changed lock would materially affect the result. An approved task does not need another approval for each internal step.
- Load the references below only for the work being done. Route to another internal module only when that capability is actually needed, not as a mandatory production chain. File writes and handoffs follow the user's authorization and the user-selected project handoff policy.

## Operating sequence (select relevant steps)

1. Confirm the authoritative screenplay, requested scope and latest user decisions. Historical notes never override the current authority.
2. Preserve hard facts, narrative function, director variables and exact execution locks. Read [references/authority-and-method-bible.md](references/authority-and-method-bible.md) when establishing or changing that map or a whole-work method, not for every local revision.
3. Before formal production, approve a coherent named-reference or project-authored method and build its bible from the complete authoritative scope. Read [references/director-selection.md](references/director-selection.md) for both paths and the shared gate. Only named-reference research needs [references/director-coverage.md](references/director-coverage.md) and relevant catalog profiles. Reuse valid decisions across episodes; analysis and bounded selection exploration may precede approval, but formal assets/prompts may not.
   Only for a requested named-reference suitability comparison, use [references/director-scoring.md](references/director-scoring.md): establish screenplay-derived criteria before scoring. Scores never select or authorize production. Project-authored methods, existing locks and local questions do not trigger catalog scoring.
   For whole-work preparation, risky sequence planning or cross-stage repair, use [references/production-workflow.md](references/production-workflow.md). It owns workflow dependencies and preparation priorities, not each sibling's detailed methods. For nonlinear or parallel narrative time, also use [references/narrative-time.md](references/narrative-time.md).
4. For screenplay or episode diagnosis, read [references/screenwriting-development.md](references/screenwriting-development.md). Use structure as diagnosis and preserve the authoritative story; do not silently rewrite it.
5. When building or changing a scene's dramatic structure or coverage, use [references/scene-direction.md](references/scene-direction.md): choose causal scene or purposeful montage/atmosphere, then define progression, audience effect, its visible/audible carrier, endpoint and cut bridge. For sequence-level diagnosis, check how neighboring shots develop that effect, not just whether individual shots are correct. A local camera or wording adjustment need not rebuild an unchanged contract.
6. For performance or camera decisions, use [references/performance-camera.md](references/performance-camera.md). When choosing framing, viewpoint, movement, focus or screen-time treatment, read [references/shot-camera-time-design.md](references/shot-camera-time-design.md); select methods for the intended audience effect, not a technique quota. For emotional expression, gaze, listening, concealment, ensemble interaction or body acting, read [references/whole-body-performance.md](references/whole-body-performance.md). Define observable development and appropriate intensity rather than relying on emotion labels or mandatory micro-reactions. A camera move has an intended function and exit: a landing, continued motion into the cut, or a deliberate interruption.
7. For combat, chase, powers, transformation or anime-PV spectacle, read [references/stylized-action.md](references/stylized-action.md) completely. Do not reduce action to physical clarity alone.
8. For tool contact or a screen-within-screen, read [references/tool-object-actions.md](references/tool-object-actions.md) or [references/embedded-media-direction.md](references/embedded-media-direction.md).
9. When transitions, sound ownership or edit intent are in scope, use [references/transitions-sound.md](references/transitions-sound.md). Keep audible ownership separate from visible performance and synchronization cues.
10. Deliver the requested directing decisions, not a platform prompt. Pass only relevant observable decisions and locks when another internal module is needed.

When translating a selected method into scene choices, resolving performance/voice/camera/rhythm interactions, or comparing methods, use [references/director-decision-practice.md](references/director-decision-practice.md). Named-reference work may retrieve a relevant profile with `scripts/director_methods.py profile ID`; project-authored methods skip this retrieval. Keep facts separate from authored applications. Comparisons are text-only by default, not a mandatory per-scene process or generation authorization.

## Non-negotiable rules

- Do not invent story facts, dialogue, injuries, powers or relationships.
- Do not auto-lock a named director from a score. Formal production requires an authorized selection; translate its scoped evidence into executable behaviors, not a celebrity label or fixed shot package. Keep director method, final appearance and model syntax separate.
- Evidence-assisted script extraction is not interpretation. Read the full screenplay before recommending a whole-work method; label excerpt-based conclusions as local, not whole-work conclusions.
- No fixed “one hit equals N seconds.” Contact may occupy a fraction of a second; the complete causal beat determines duration.
- Framing changes and internal cuts do not automatically imply separate generations.
- One beat has one primary spectacle owner. Camera, VFX, sound and deformation support rather than compete.
- In story causality, a trigger precedes its consequence; audience presentation may deliberately reverse, omit or revisit it. Effects cannot create contact that bodies, tools or powers did not establish. Do not force chronological editing onto a nonlinear story.
- Preserve accepted exceptions as local exceptions; do not promote them to general rules.

## Deliverable

Return only the requested detail. A full package contains authority map, current director-style lock/reference and method inheritance, scene contract, blocking/performance, camera/coverage, action contract when applicable, transition/sound bridge, required ending state and motion at exit, editorial intent and open risks. Validate formal handoffs with `scripts/director_style.py check PACKET --stage director`; reuse valid unchanged checks. The gate checks declared authority/version, not artistic quality or actual approval truth.

Use `scripts/script_evidence.py` only when structural inventory is needed. Its output remains `evidence-only`; neither keyword counts nor extracted snippets replace direct reading and interpretation. Do not add a separate human sign-off for ordinary analysis; actual user approval is still required to change creative locks.
