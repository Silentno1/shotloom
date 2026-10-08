# Portable environment and project handoff

Shotloom is one self-contained skill folder. Its five modules are internal resources, not installed sibling skills. Resolve resources from this package, never from a maintainer's home directory. A module's `scripts/` command is relative to that module; use the full resolved package path when the working directory differs. Do not run all workflows or scan all project files just because a module exists.

## Capabilities, not a required application stack

| Available capability | Supported work | Honest fallback |
| --- | --- | --- |
| Conversation and relevant instruction text | Diagnosis, direction, design, model-native prompts, manual review guidance and copyable state | User retains records; no claim of saved files or inspection of unseen media |
| Authorized project file access | Read authority, save changed records and handoffs | User-selected location; clarify only when a missing location matters to a requested write |
| Python 3.10+ | Optional consistency, source-lock and continuity helpers | Apply documented checks manually; never manufacture a pass or hash |
| Local FFmpeg/FFprobe | Optional source-timed frames and technical evidence | Request accessible evidence or mark dimensions unverified; no automatic installation |
| Actual image/video/audio perception | Review the inspected source, range and modalities | Thumbnails do not prove motion; transcripts do not prove listening |
| Authorized local editing tools | Scoped previs, edit, repair, render and verification | Deliver a reproducible edit/post plan; never claim an unperformed edit |

No database, notebook app, account, connector or generation API is required. `agents/openai.yaml` is optional host metadata. Other agents use the same entry and references without it. Portability means explicit fallback with missing tools, not a guarantee that every agent can perform every media operation.

Optional media helpers resolve executables through `PATH`, or explicit `SHOTLOOM_FFMPEG` and `SHOTLOOM_FFPROBE` executable paths. An invalid explicit override reports an error instead of secretly choosing another binary. No home-directory fallback or automatic package installation is used.

## Storage and approvals

Keep one current project authority. Reuse the user's layout and rules. If files are authorized but no convention exists, propose a small `shotloom/` folder inside the selected project for state, reviews and handoffs; do not create it for a discussion. Source footage and renders stay in their authorized locations. No mandatory notebook or global memory directory is introduced.

Before a write, identify scope and impact and obtain or reuse explicit authorization. A bounded approved operation includes necessary checks and repairs, not uploads, spending, publication or unrelated changes. Read-only requests remain read-only, including handoffs. Preserve originals and existing work. Handoffs use the user's designated location; otherwise return them in the conversation. Do not silently migrate old records.

For conversation-only operation, return stable IDs, versions, authority, checked evidence, decisions, unknowns and the next action in copyable Markdown. The user brings that record to a new conversation. Version/content checks are manual when hashing is unavailable; machine-only guarantees are not implied.

## Generation stays outside the package

Shotloom prepares model-native prompts, role maps, intended settings and user verification checklists. It does not select providers, log in, bind remote nodes, call generation services, upload assets, spend credits or publish. Users return actual results and relevant observed settings. A connector in the surrounding agent does not expand this skill's scope.

Model documentation and destination readiness are separate. Unknown destination permits a labeled native draft; unknown proprietary syntax stays unresolved. User-supplied readback is user-reported, not independently observed. No credentials are requested. Optional destination-binding checks compare supplied evidence only; they never connect to a service.

## Source and evidence freshness

Bundled model and director references are dated baseline material, not fresh research performed on each use. Preserve date, scope, uncertainty and counterexamples. Recheck consequential changing claims against public primary sources when available; otherwise label them historical/unverified and withhold unsupported execution claims. Private manuals, private canvases and one user's accepted examples are not prerequisites or public proof. See [source-policy.md](source-policy.md).
