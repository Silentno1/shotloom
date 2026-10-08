# Platform routing and evidence

Compare only dimensions relevant to the task: input roles, identity, acting, spatial motion, exact contact, internal edits, first/last frames, audio, text/UI, duration, aspect ratio, cost, iteration and the user's verified interface.

## Evidence labels

- `official-current`: exact current first-party documentation for model and surface.
- `interface-observed`: visible in the user's active interface.
- `project-verified`: reproduced and reviewed in the current workflow.
- `community-observation`: useful hypothesis, not a capability guarantee.
- `unknown`: do not claim.

Documentation says an operation exists; it does not guarantee fidelity. Project tests say a result happened; they do not prove all genres.

Separate capability/method support from submission readiness. Maintain and use officially documented branches even when a third-party host has not exposed them. For explanations, maintenance and prompt-only plans, do not require a live interface, credentials, API integration or a paid test; label intended mode/settings and unresolved host bindings. At actual submission, verify the selected host's controls and bounds. If absent, report that host limitation and preserve the original model-native plan; do not delete the feature, pretend a prose keyword implements an API, or silently downgrade the creative contract.

Use [model-manual-authority.md](model-manual-authority.md) to distinguish official grammar, manual recommendations, host constraints and empirical examples. Read the applicable manual section before adopting another model's prompt method. A retained official document is a dated baseline, not automatically `official-current`; verify consequential changing claims on the exact surface. If official and host limits differ, retain both scopes and resolve the active operation conservatively rather than overwriting either source.

Every consequential changing claim records a stable claim id, value, evidence level, verification date and source. `project-verified` also records exact model/surface, test artifact or output path, result hash and tested scope. A community observation or unknown claim cannot satisfy a hard production requirement. Run `scripts/platform_evidence_check.py` on the evidence packet before relying on it.

For a model-native plan, scope official evidence to the documented model/product surface and record the unresolved destination separately. Do not label the packet as a verified third-party operation merely because official-manual claims passed provenance checks.

## Routing discipline

For video model selection or material reassessment, follow [task-based selection](video-model-selection.md) and the [dated model profiles](video-model-profiles.md). Profiles supply provisional candidates, not fixed genre assignments or permission to call every listed model. Keep capability evidence, quality evidence and host execution readiness distinct; propagate the decision's risks to actual-media review. Other media retain their own task-specific adapters.

1. Name the control problem.
2. Identify the minimum inputs that solve it.
3. Compare current verified candidates.
4. State decisive advantage, decisive risk and evidence label.
5. If the platform cannot honor a hard fact or lock, change platform, add a focused authority, simplify the director variable or plan an edit. Do not rewrite story facts.

Any change to a locked creative variable, approved model, production method or paid operation remains subject to its existing authorization. A recommendation or fallback condition does not unlock a paused task, reset attempts or authorize generation.

## Reference-file geometry

Before an image-reference submission, read the dimensions of the actual bound file and compare them with evidenced input limits for that surface/model/mode, separately from output aspect ratio. A hosted plan/schema validator may omit downstream gateway constraints. When it passes but the gateway rejects an input, retain the actual error and operation scope; do not retry the unchanged invalid input or call a parameter rejection a content-quality failure.

For known aspect bounds, run `scripts/reference_image_preflight.py IMAGE [IMAGE ...] --min-aspect MIN --max-aspect MAX --evidence 'surface/model/mode/date and constraint source'`. The script has no default platform limits, does not edit images and only checks encoded pixel dimensions. Missing/failed dimension reads are unverified, not passes; orientation metadata or platform transforms need separate verification when relevant. A local file check must correspond to the bound uploaded version/hash, not a same-named substitute. Unknown limits stay unknown rather than blocking all unrelated work or being silently invented.

If a reference fails, prefer an already approved compatible asset that still carries the required information. Cropping, padding or splitting may change reference meaning and authority; inspect any authorized derivative and preserve identity/design before binding it. Never stretch an image or crop off required identity views merely to pass a ratio test. A successful local check does not prove server acceptance or artistic suitability.

## Platform adapters

- MiniMax H3: [minimax-h3.md](minimax-h3.md)
- Google video: [google-video.md](google-video.md)
- Runway Gen-4.5: [runway-gen45.md](runway-gen45.md)
- Seedance/Seedream: [seedance-seedream.md](seedance-seedream.md)
- Kling 3.0 series (video/image, Omni/O3, Turbo, motion control): [kling-3-series.md](kling-3-series.md)
- Wan 3.0 video (standard/prime, generation/reference/edit/extension): [wan-3.md](wan-3.md)
- Image platforms (Midjourney version branches, Nano Banana variants, GPT Image 2.5): [image-platforms.md](image-platforms.md)
- Other platforms: [platform-adapters.md](platform-adapters.md)

Recheck changing facts at use time. Keep unsupported platforms on a generic contract until the exact current documentation or interface is available.
