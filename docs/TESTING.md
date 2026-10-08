# Public workflow verification

Run `python3 scripts/validate.py` and `python3 scripts/run_tests.py`. Module suites run in separate processes so identically named test modules cannot mask one another. Python bytecode caches are disabled. Tests use synthetic data and temporary files, never real project acceptance.

## Release verification — 2026-10-09 / 0.2.1

- Python 3.14.5: all 449 tests passed with no reported skips after the release version and documentation updates: 39 package tests and 410 module tests.
- Package structure, local links, privacy/syntax checks, skill frontmatter validation and whitespace checks passed.
- `shotloom-0.2.1.zip` contains 160 runtime files. Archive integrity, complete file inventory and byte-for-byte agreement with the skill source folder passed.
- After extraction outside the repository, all five packaged module suites passed again (410 tests; not additional distinct cases).
- The release changes version metadata and documentation, not production behavior. It does not add real-film validation, independent agent trials, PowerShell runtime testing or fresh verification of external model sources.

The records below describe earlier development snapshots and are retained for traceability, not as additional public releases.

## Recorded local verification — 2026-10-09 / 0.2.1-alpha

- Python 3.14.5: all 449 tests passed with no reported skips: 39 package/public tests, 131 director, 27 visual, 115 generation, 101 review/continuity and 36 edit/delivery.
- The additions comprise 21 timing-arithmetic tests and three standalone CLI checks. The latter copy only the helper to a temporary path containing spaces, use Python's isolated mode and an empty executable search path, and verify that no files are created or changed.
- Covered timing behavior includes partial/excluded intervals, repeated source uses, rational rates, unknown versus declared measured delay, negative-placement warnings and rejection of unsupported input. These are arithmetic checks, not transcription, subtitle rendering or audiovisual approval.
- Package structure, local links, source-map coverage, privacy/syntax checks and the skill frontmatter validator passed. The full suite also reran relocated method gates, temporary Bash installation and local zip-builder checks.
- The final local zip contains 160 runtime files, with complete inventory and byte-for-byte agreement with the source folder. After extraction outside the repository, all five packaged module suites passed again (410 tests; not an additional 410 distinct cases).
- All 135 mapped source fingerprints matched the synchronized records. Files outside the declared update scope remained unchanged.
- The shot examples, tool-choice guidance and no-Python fallback were reviewed as instructions; no independent agent trial, actual captioned film, compositing runtime or export-sync listening test was performed. No external-source refresh, real installation or publication was performed.

The previous verification below remains a historical record, not the current test count.

## Recorded local verification — 2026-10-04

- Python 3.14.5: 425 tests passed, no reported skips (36 package/public tests, 131 director, 27 visual, 115 generation, 101 review/continuity, 15 edit/delivery).
- Package structure, syntax, relative links, personal-dependency scan and the skill frontmatter validator passed.
- The director catalog audits passed for 69 profiles, 61 branches and 87 declared route cases. These are catalog structure/provenance checks, not source-truth certification.
- Relocated-folder checks passed. Bash installation was exercised only in temporary destinations, including spaces, default replacement refusal, distinct forced-update backups and self-install refusal.
- Local zip tests passed for complete runtime inventory, bundled license, archive integrity, replacement refusal and symlink rejection before packaging. No real agent installation or publication was performed.
- All 129 recorded source fingerprints remained unchanged. PowerShell, other Python versions, other operating systems and arbitrary agent hosts were not executed as part of this local verification.

These results describe this revision and environment. Re-run the checks after changes; they are not permanent certification.

## Forward scenarios

| Request / available capability | Required behavior | Incorrect behavior |
| --- | --- | --- |
| “Plan this complete scene using my own method”; no Python | Use project-authored method and Markdown authority/version; return bounded plan | Require a famous director, 69-person scoring or a script pass |
| “Explain this one blocking error”; read-only | Diagnose the named relation with current locks | Create project records, reselect method or launch all modules |
| Same contract, a different supported model | Independently compile from original source lock; keep exact words/state/look/sound | Translate the previous native prompt and inherit its syntax |
| Accepted first shot is replaced and changes prop ownership | Preserve history, mark relevant later take stale, resolve in story order | Treat the latest operation as story order or silently update later approval |
| Cut removes the visible transfer but aftermath may imply it | Review selected event evidence and actual cut; retain/mark unresolved with reason | Blindly apply or erase the full source endpoint |
| Only contact sheets and transcript are available | Review supported visual details and wording; temporal/audio quality stays unverified | Claim normal playback or actual listening |
| User provides a new workspace, no notebook or installed siblings | Resolve all module resources inside the copied folder; ask/reuse output location only when writing | Read the author's home folder or require a plugin |
| A standalone audio brief | Use audio source-lock fields and ownership, then user-operated generation and actual listening | Require appearance fields or run a video adapter |
| Changed final export | Recheck relevant audiovisual joins and actual output, preserve source | Reuse the old entire-file approval without content mapping |
| “Compare a push-in with a fixed shared frame”; current method is project-authored | Use a relevant conditional case and its countercase; keep the approved method and appearance | Require a named director, fixed seconds or mandatory camera movement |
| Captions after a cut with detached dialogue, repeated source or speed changes | Map through the actual audible selection, retain separate corrections and flag partially cut words | Copy picture offsets, remove repeated instances or restore missing speech in text |
| Timing-critical sound with unknown export displacement | Report nominal placement, preserve intended lead/lag and request actual evidence before compensation | Treat an unknown delay as measured zero or claim an arithmetic listening pass |
| A compositing request with no suitable local runtime | Return the bounded operation plan and unavailable checks | Install a plugin, connect a generation service or claim a completed render |

These cases are desk-review acceptance criteria, not a claim that an independent agent or real model executed them. Automated tests establish only their explicit code invariants and relocation behavior. The full director catalog is checked for references and declared evidence partitions, not historical truth or artistic effectiveness.

FFmpeg-dependent tests skip visibly when the executable is unavailable; missing optional tools must not prevent reading the skill. PowerShell installation needs a Windows/PowerShell environment for runtime confirmation. No script installs dependencies or submits external jobs.
