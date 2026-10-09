# Changelog

All notable changes to Shotloom will be documented here.

## [0.2.2] - Unreleased

### Fixes

- Bound video review ranges by decoded video timestamps and the final frame's duration, not container duration. Preserve VFR/nonzero-origin handling, reject genuine out-of-range requests and label a tightly checked CFR fallback as an estimate.
- Use one dialogue-audit implementation behind both entry paths, preserving `--json` and Unicode case folding. Reject empty expected dialogue, malformed transcript data and invalid/out-of-media timing; a wording match does not imply listening or creative approval.
- Separate portable CI from required-media CI on Python 3.10 and 3.13. The media job explicitly installs FFmpeg/FFprobe, records versions and fails on any skipped or unexecuted discovered test.

### Documentation and routing

- Add Chinese task keywords and concrete short-drama/comic-style-drama examples to the bilingual introduction.
- Expand the current written workflow with shot plans, a scoped prompt draft and evidence-limited review examples. Keep the historical golden scene separate from current acceptance claims.
- Record guest access to all four Feishu sources on 2026-10-09, add a verified official non-Feishu prompt guide and document offline fallback. Access verification does not renew all historical model claims.
- Route the main entry directly to maintained references while retaining old compatibility paths. Keep director research optional and explicitly prohibit preloading the full JSON catalog for ordinary work.

This revision is prepared locally. It has not been published, and the new GitHub CI matrix has not yet run.

## [0.2.1] - 2026-10-09

### Production workflows

- Packaged directing, visual design, generation planning, review/continuity and edit/delivery as five internal modules behind one Shotloom entry.
- Included 69 director/work reference profiles, source locks, actual-media review, dependency-aware continuity and edit/finishing guidance.
- Supported named-reference and project-authored directing methods through the same authority/version checks; catalog scoring remains optional.
- Added file-backed and conversation-only production state, story development, voice/dialogue contracts, take reviews and post-production handoffs.
- Included model-native prompt guidance with dated sources and explicit gaps. Generation, accounts, uploads, spending and publication remain outside the skill's runtime scope.

### Shot patterns and post-production

- Added five conditional shot-pattern cases without imposing a fixed director, look, duration or shot recipe.
- Added capability-first local editing/compositing guidance. Named tool skills are optional examples, not package dependencies.
- Added caption correction and source-to-cut reconform for audible selections, partial words, repeated source uses and changed cuts.
- Added final-output audio synchronization methods that separate source anchors, intended lead/lag and measured export displacement.
- Added a read-only standard-library timing helper with arithmetic tests and manual equivalents.

### Packaging and documentation

- Included bilingual documentation, compatible-agent guidance, installable examples and a single-folder release archive.
- Added optional Python and media helpers, recoverable staged installation, a package builder and automated validation.
- Included isolated module tests, relocated-folder checks and synthetic review/continuity fixtures.
- Documented resource provenance and third-party sources without requiring a specific notebook, private manual, account or installed companion skill.
- Kept validation limits explicit: structural and synthetic tests do not certify production quality or every agent environment.
