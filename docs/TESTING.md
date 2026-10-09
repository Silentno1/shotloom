# Public workflow verification

Run `python3 scripts/validate.py` and `python3 scripts/run_tests.py`. Module suites run in separate processes so identically named test modules cannot mask one another. Python bytecode caches are disabled. Tests use synthetic data and temporary files, never real project acceptance.

For complete media testing, use `python3 scripts/run_tests.py --require-media`. It requires FFmpeg and FFprobe, prints their versions, and rejects every skip or mismatch between discovered and executed test counts. The portable mode reports each skip explicitly; a passing portable run is not a full media pass.

## Release package verification — 2026-10-10 / 0.2.2

- The final installation archive was rebuilt in a fresh output directory after the installer and source-link follow-up. It contains **161 runtime files, 515,023 bytes**. ZIP integrity, complete inventory and byte-for-byte agreement with the current skill source passed. The earlier 514,957-byte local archive is not the release asset.
- SHA-256: `1a1b0fe869327444068932667618baa6dc6de7ae6624b4f2bc8be4f928d9f4f5` for `shotloom-0.2.2.zip`. The release includes a separate `.zip.sha256` file.
- After extraction outside the repository, Python **3.14.5** executed all **428 packaged module tests with zero skips**, using FFmpeg 6.0 and FFprobe 8.1.2. These are the same module cases included in the 485-test repository suite, not additional distinct tests. Repository installers and package-level tests are not part of the runtime ZIP.
- The [0.2.2 release notes](https://github.com/Silentno1/shotloom/releases/tag/v0.2.2) identify the final tag and its four-job CI run. The source-only CI evidence below remains a separate historical step; it is not a substitute for verifying the final release commit.
- The 0.2.1 tag, release notes and assets are retained as history. Their test results do not certify 0.2.2, and the 0.2.2 fixes do not change the old archive.
- Windows/PowerShell runtime behavior, real-film production and independent use across all agent hosts remain unverified. Automated and synthetic checks do not establish audiovisual or creative acceptance.

## Earlier GitHub source verification — 2026-10-10 / 0.2.2

- Source commit [`623109b`](https://github.com/Silentno1/shotloom/commit/623109b13872f25a387c0c5c6248470f9eda5268) includes all 27 changed/new files, including both new test files. The uploaded tree matched the complete local staged tree exactly; no tests were omitted from the commit.
- The [first four-job CI run](https://github.com/Silentno1/shotloom/actions/runs/37975853444) passed on Ubuntu 24.04.5 with Python **3.10.22 and 3.13.16**. Dates in this record use Asia/Shanghai.
- Each required-media job executed **485/485 tests with zero skips**, using FFmpeg and FFprobe **6.1.1-3ubuntu5**. Suite counts were 57 package/public, 131 director, 36 edit/delivery, 115 generation, 119 review/continuity and 27 visual. Running the same suite under two interpreters does not double the distinct test count.
- Each portable job deliberately hid the media executables: **485 discovered, 461 executed**, with five class-level skip events covering 24 unexecuted cases. These jobs passed their intended no-media checks; they are not full media passes.
- That step uploaded the 0.2.2 source only. It did not create a `v0.2.2` tag, Release or replacement installation archive; 0.2.1 was still the latest release at that point. The final 0.2.2 package is recorded above.
- Windows/PowerShell runtime behavior, real-film production and independent use across agent hosts remain unverified. These CI results establish only the tested automated behavior.

## Earlier local verification — 2026-10-09 / 0.2.2 installer follow-up

- Python **3.14.5 and 3.11.15**, macOS: each executed all **485 tests**, no skips, using required-media mode with FFmpeg 6.0 and FFprobe 8.1.2. Breakdown: 57 package/public, 131 director, 27 visual, 115 generation, 119 review/continuity and 36 edit/delivery.
- The Bash installer has ten regression cases (seven added in this follow-up). They cover unique backups on repeated updates, discovery-root isolation, copy/backup/swap/restore failures, symlinked targets, rejected linked storage, a simulated cross-filesystem boundary, missing arguments and self-install refusal. The recursive discovery check finds only the active `shotloom/SKILL.md`; when restoration is deliberately made impossible, the original remains in the reported external backup instead of being deleted.
- Both installers now stage and back up in a sibling `.<target-name>.shotloom-installer` directory, not inside the skills discovery root. The target's parent must be writable. Bash rejects cross-filesystem storage before moving the old installation; PowerShell uses filesystem move operations instead of a copy/delete fallback for directories. Old backups created by previous installers are not moved or deleted automatically.
- Package structure, relative links, privacy/Python syntax, skill frontmatter, Bash syntax and whitespace checks passed. The PowerShell changes were reviewed but **not executed**: no PowerShell runtime is available locally. No real agent installation was changed.
- The unnecessary K3-IO query parameter was removed. The parameter-free Chinese guide was readable in the scoped 2026-10-09 access check; this does not refresh model capabilities or certify external demonstrations.
- The original `dist/shotloom-0.2.2.zip` and checksum describe the **earlier snapshot recorded below**, not a package of this follow-up. The final release was rebuilt in a fresh output directory; do not treat the old source/archive equality check as current.
- At the end of this local follow-up, no staging/commit, push, tag, Git identity change or release had been performed, and the new GitHub CI matrix had not run remotely. Python 3.10/3.13, Windows/PowerShell and real-film/independent-agent behavior were not run in that local verification. The subsequent GitHub run is recorded above.

## Earlier local verification — 2026-10-09 / 0.2.2 before installer follow-up

- Python **3.14.5 and 3.11.15**, macOS: each executed all **478 tests**, no skips, using the required-media mode. Breakdown: 50 package/public, 131 director, 27 visual, 115 generation, 119 review/continuity and 36 edit/delivery. Repeating the same cases on two interpreters does not double the distinct test count.
- Executables reported **FFmpeg 6.0** and **FFprobe 8.1.2**. These versions are recorded separately; this local run is not an Ubuntu or same-version toolchain result.
- The video-tail regression uses a real 12-frame/120-fps clip while overriding only container duration to `0.092`. Both `--dense-range 0:0.1` and `--selected-out 0.1` succeed and retain the correct final frame. True out-of-bounds requests fail before creating evidence. Parser cases cover VFR, nonzero origins, longer audio, old/new FFprobe duration fields, unknown tails and a labeled CFR estimate.
- Dialogue checks cover both entry paths after relocation, Unicode case folding, JSON output, empty expected lines, malformed data, invalid timing and timing outside the supplied media duration. A text match remains `normalized_wording_only`.
- Missing-tool simulation on Python 3.11.15: 478 discovered, 454 executed, five class-level skip events covering 24 unexecuted tests. Reasons are printed. The same missing-tool condition makes required-media mode fail before the suites start.
- Runner regressions verify individual skips, whole-class skips, empty suites and real failures. Entry/reference wiring and selective director retrieval are checked; Chinese keyword presence does not prove automatic activation on every agent.
- Package structure, relative links, privacy/syntax checks, skill frontmatter validation and whitespace checks passed.
- Earlier `shotloom-0.2.2.zip`: **161 runtime files, 514,957 bytes**. Archive integrity, complete inventory and byte-for-byte equality with the skill folder **at that snapshot** passed. This archive predates the installer follow-up and source-link cleanup above. In an isolated directory outside the repository, all **428 module tests** ran again with no skips; these are the same module cases, not additional distinct tests. The published `0.2.1` archive is unchanged.
- This snapshot introduced Python 3.10/3.13 portable jobs with intentionally unavailable media tools and separate media jobs that install FFmpeg/FFprobe and prohibit skips. The matrix had not run remotely at that point; its subsequent result is recorded above. Neither Python 3.10 nor 3.13 was executed locally in this verification.
- The current written example is a fictional 0.2 workflow demonstration, not an actual-media acceptance fixture. Four Feishu sources and a linked official non-Feishu prompt guide received a scoped guest-access check; see the [source record](../skill/shotloom/modules/generation/references/seedance-25-sources.md). That check does not renew every historical model parameter or validate embedded demonstrations.

Those earlier local snapshots did not include a real-film end-to-end test, independent agent trial or PowerShell runtime test. They involved no remote generation, account change, dependency installation on the user's machine or publication.

## Historical release verification — 2026-10-09 / 0.2.1

- In the recorded local Python 3.14.5 run, all 449 tests passed with no reported skips after the release version and documentation updates: 39 package tests and 410 module tests. This is a historical result for that environment, not a claim that 0.2.1 passes on every toolchain.
- Package structure, local links, privacy/syntax checks, skill frontmatter validation and whitespace checks passed.
- `shotloom-0.2.1.zip` contains 160 runtime files. Archive integrity, complete file inventory and byte-for-byte agreement with the skill source folder passed.
- After extraction outside the repository, all five packaged module suites passed again (410 tests; not additional distinct cases).
- The release changes version metadata and documentation, not production behavior. It does not add real-film validation, independent agent trials, PowerShell runtime testing or fresh verification of external model sources.

Later cross-environment review found a video-tail failure in 0.2.1: a clip whose final frame ends at `0.1` seconds could report a container duration of `0.092`, causing a valid end-of-clip interval to be rejected. The 0.2.2 fix derives the video endpoint from frame timing and includes a regression for that discrepancy. The published 0.2.1 tag/archive has not been replaced and still contains the defect; its original local pass does not negate this later finding.

The [published CI job](https://github.com/Silentno1/shotloom/actions/runs/37847792931/job/113552903204) succeeded but did **not** execute all 449 cases: generation ran 113 with one class skip; review ran 81 with four class skips. Total executed was 427, with 22 cases omitted across those five class-level skip events. The original 449/no-skips result above describes the local environment only. The later 0.2.2 required-media jobs executed every discovered case, as recorded above; that result does not retroactively validate the old 0.2.1 archive.

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

FFmpeg-dependent tests skip visibly in portable mode when the executable is unavailable; required-media mode rejects that situation. Missing optional tools must not prevent reading the skill. PowerShell installation needs a Windows/PowerShell environment for runtime confirmation. Runtime helpers and the local test runner do not install dependencies or submit external jobs; the dedicated CI media job installs media tools only on its disposable runner.
