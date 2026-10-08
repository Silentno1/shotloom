# Contributing to Shotloom

Shotloom covers directing, visual design, generation planning, review/continuity and editing. Review the [package architecture](docs/PUBLIC-BASELINE.md) and source-file map before replacing or removing a capability. Keep the review-and-iteration loop intact and avoid dependencies on a maintainer's local environment.

Keep one public entry and five internal modules. Resolve all runtime resources inside the installable folder. Keep conversation-only and optional-tool paths usable. Source data and accepted project state are never modified as a side effect of skill maintenance.

Named-reference and project-authored methods must both pass the same authority/version safeguards. Do not make celebrity selection or catalog scoring mandatory. Test both positive and negative behavior when changing gates; keyword assertions are wiring evidence only.

Model adapters preserve exact version/mode, native expression, reference roles, sound ownership and evidence scope. Official model documentation, destination readiness and actual output quality are separate. No connectors, account data, private documents, pricing assumptions or remote submission code enter the runtime. Sources can link to official documentation; links do not mean the documentation is freshly verified.

Use original explanations and scoped source attribution. Publicly readable material is not automatically licensed for copying. Keep historical source dates, unavailable evidence and countercases. Do not promote synthetic tests or one project's accepted exception into production proof.

Run `python3 scripts/validate.py` and `python3 scripts/run_tests.py`. Optional media tests report skips when tools are absent. Include realistic tool-limited/manual cases and relocated-install behavior. Do not add paid tests, new dependencies or unrelated project changes to complete a contribution.

The maintainer-only `scripts/import_baseline.py` imports into a new staging directory and refuses overwrite. It performs mechanical normalization, not finished public adaptation; review its output against the current public contracts before merging. Never run it as an automatic user-project updater.
