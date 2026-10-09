# Contributing to Shotloom

Shotloom covers directing, visual design, generation planning, review/continuity and editing. Review the [package architecture](docs/PUBLIC-BASELINE.md) and source-file map before replacing or removing a capability. Keep the review-and-iteration loop intact and avoid dependencies on a maintainer's local environment.

Keep one public entry and five internal modules. Resolve all runtime resources inside the installable folder. Keep conversation-only and optional-tool paths usable. Source data and accepted project state are never modified as a side effect of skill maintenance.

Named-reference and project-authored methods must both pass the same authority/version safeguards. Do not make celebrity selection or catalog scoring mandatory. Test both positive and negative behavior when changing gates; keyword assertions are wiring evidence only.

Model adapters preserve exact version/mode, native expression, reference roles, sound ownership and evidence scope. Official model documentation, destination readiness and actual output quality are separate. No connectors, account data, private documents, pricing assumptions or remote submission code enter the runtime. Sources can link to official documentation; links do not mean the documentation is freshly verified.

Use original explanations and scoped source attribution. Publicly readable material is not automatically licensed for copying. Keep historical source dates, unavailable evidence and countercases. Do not promote synthetic tests or one project's accepted exception into production proof.

Run `python3 scripts/validate.py` and `python3 scripts/run_tests.py`. Optional media tests report skips when tools are absent. Include realistic tool-limited/manual cases and relocated-install behavior. Do not add paid tests, new dependencies or unrelated project changes to complete a contribution.

The maintainer-only `scripts/import_baseline.py` imports into a new staging directory and refuses overwrite. It performs mechanical normalization, not finished public adaptation; review its output against the current public contracts before merging. Never run it as an automatic user-project updater.

## Publishing a version

A version release includes the source commit, a matching `vX.Y.Z` tag, dated Chinese and English update notes, a freshly built installation ZIP and its SHA-256 file, and a GitHub Release. Updating the default branch alone is not a release. Routine maintenance does not authorize publication; publish only when the maintainer requests a version release.

1. Align the skill version, both READMEs, changelog and verification record. Include new files in the commit and review the complete staged change.
2. Build with `scripts/build_release.py` into a fresh output directory. Check ZIP integrity, inventory and byte-for-byte agreement with the final skill source; run the packaged module tests after isolated extraction. Do not reuse an earlier archive with the same version label.
3. Upload the final commit and wait for all four CI jobs. Each required-media job must run every discovered test with zero skips. Record the final CI link in the release notes.
4. Create only the requested version tag at that verified commit. Publish the ZIP, checksum and bilingual notes as a regular Release and mark it Latest unless a prerelease was explicitly requested. Retain previous tags, releases and assets; do not push all local tags.
5. Check the public version page, Latest status, tag target and downloaded asset checksum. Report a blocker as an incomplete release, not a successful source-only substitute.
