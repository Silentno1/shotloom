# Package architecture and maintenance

Shotloom 0.2.1 contains five production modules behind one portable skill entry. Maintain the complete directing, visual, generation-planning, review/continuity and edit/delivery loop when changing the package.

## Capability ownership

| Component | Supported work | Package location |
| --- | --- | --- |
| Director | Story authority, method bible, 69 reference profiles, topic retrieval/scoring, scene/performance/camera/time/action/sound and previs preparation | [director](../skill/shotloom/modules/director/WORKFLOW.md) |
| Visual design | Open appearance families, custom/mixed media, characters/space/props, references, light/color, scale and visual validation | [visual-design](../skill/shotloom/modules/visual-design/WORKFLOW.md) |
| Generation planning | Source locks, image/video/audio planning, reference roles, native model methods, sound partition, consistency/geometry checks and failure repair | [generation](../skill/shotloom/modules/generation/WORKFLOW.md) |
| Review/continuity | Source-timed evidence, coverage/salience, actual media/asset review, failure attribution, immutable accepted state, dependency invalidation, nonlinear contexts and selected-cut reconciliation | [review-continuity](../skill/shotloom/modules/review-continuity/WORKFLOW.md) |
| Edit/delivery | Timed previs, dramatic selection, retiming, temporary sound, three-pass cut review, post turnover/reconform and destination-specific delivery checks | [edit-delivery](../skill/shotloom/modules/edit-delivery/WORKFLOW.md) |

The [file map](baseline-map.json) records 135 synchronized resources and their source fingerprints without storing machine paths. `source_sha256` identifies each recorded source; `previous_source_snapshots` preserves older fingerprints, dates and changed/added target lists. Package adaptations need not match the source bytes. Version labels in the map identify development snapshots, not published releases. The map is provenance data, not a required runtime service.

## Shot patterns and post-production

The 2026-10-09 update adds six resources for conditional shot-pattern cases, local execution routing, caption conform, final-output sound calibration and the read-only timing helper with its tests. Five direction/review/edit files route to these methods only when relevant. The update does not replace model adapters, visual contracts, the director catalog or method-selection rules.

- Tool choice is capability-first. Named tool skills are optional examples; missing tools permit a bounded plan and explicit evidence limits, not automatic installation or a compulsory plugin.
- Missing performance or story material can return to a generation plan, but external generation stays with the user. No paid-call or upload authorization is introduced.
- Constant-rate caption mapping and sound-placement arithmetic are available in prose as well as optional standard-library Python. A calculated timestamp is not media inspection, subtitle export, a listening pass or approval.
- Recorded source dates are historical evidence. An update does not imply a fresh check of cited external repositories or licenses.

## Portability and authority

1. Formal production requires an approved method. Named-reference and project-authored methods are equal paths, checked through the same five-stage version/approval gate. Catalog scoring is conditional, not compulsory.
2. All five modules live inside one skill folder. Relative imports and resources travel together; one entry routes by the user's actual task.
3. Storage is user-selected, with conversation-only handoff available. No absolute home path, private project data or global-memory service is required.
4. Python and FFmpeg are optional enhancements. The decisions and evidence limits remain available as prose. Missing media perception is an unverified dimension, not simulated approval.
5. Destination readiness uses user-supplied evidence. Model-native guidance stays separate from remote generation, account access, uploads, billing and publication.
6. Private source documents and unmatched production examples are not public proof. Keep public source links and historical dates, with unavailable-source gaps explicit.
7. One project's model preferences and accepted exceptions are not universal defaults. Unmaintained versions use an explicit adapter gap, not another model's rules.

## Maintenance and verification

Use the file map to check coverage before editing a module. Keep one authoritative reference per decision; earlier reference paths are compatibility routers, not parallel specifications. Skill maintenance never automatically edits a user's project, reopens accepted media or migrates old state.

Run package validation, all isolated test suites and relocated-install checks. Behavioral tests cover both method paths, stale bindings, source-lock consumers, continuity and media evidence. Documentation/keyword assertions remain wiring checks, not behavioral or artistic proof.

No remote generation, production film validation, complete external-source recheck or multi-agent-host certification is implied. Test media are synthetic local fixtures. See [testing scenarios](TESTING.md) for the manual/tool-limited cases.
