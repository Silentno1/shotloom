# Model adapter specification

A Shotloom adapter converts a shared approved source lock into one exact model/mode's prompt plan. It is documentation, not an API integration. The maintained implementations live under [generation](../modules/generation/WORKFLOW.md); an adapter may use an entry, operation branches and a source register rather than duplicate every section in each file.

## Required provenance

Every adapter must make the following information reachable from its entry:

- exact model or family name;
- supported variants;
- source record date and scope, distinguishing inherited snapshots from newly verified evidence;
- primary sources;
- confidence labels for volatile claims.

## Required coverage

1. **Scope:** tasks the adapter covers and explicitly excludes.
2. **Evidenced envelope:** duration, reference inputs, output or edit modes only when relevant primary sources support them; unresolved or stale limits remain explicit.
3. **Surface caveat:** controls that vary by provider, account, region, or interface.
4. **Compilation order:** how to arrange the production contract in model-facing prose.
5. **Reference rules:** binding syntax, ownership, and conflict handling.
6. **Timing or composition rules:** model-specific structure.
7. **Failure patterns:** symptoms, evidence-based causes and scoped diagnostics. One-variable changes help isolate a cause; they are not a quota or a ban on necessary coverage redesign.
8. **Review gates:** what must be inspected after generation.
9. **Version isolation:** facts that must not be inherited from sibling models.

## Evidence labels and destination separation

Use the [source policy](source-policy.md): `official-current`, `interface-observed`, `project-verified`, `community-observation` or `unknown`. Production methods are authored guidance, not volatile capability claims. Historical alpha labels remain historical until evidence supports a current label. A recorded date or passing validator never refreshes an old claim automatically.

Keep user-reported settings separate from directly inspected evidence. An unknown destination permits a labeled model-native draft, not invented reference syntax or a claimed execution pass. Use [destination bindings](../modules/generation/references/destination-bindings.md) only to compare supplied evidence; no service connection, account access, upload or generation is introduced.

## Acceptance test for a new adapter

Compile the same explicit fictional source lock independently for the compared adapters and confirm:

- no capability number comes from another model;
- all supplied references have explicit roles;
- the prompt preserves the shared scene job and endpoint;
- unsupported controls are omitted or marked for surface verification;
- the review checklist remains observable;
- package validation and unit tests pass.

Name the exact test's scope and unavailable media checks. Old golden-scene fixtures are useful historical examples, not current source-lock approval or proof that generated results match the plan. Run optional scripts only where available; otherwise retain the same manual review decisions without claiming machine validation.
