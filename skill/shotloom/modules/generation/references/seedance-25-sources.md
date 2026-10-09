# Seedance 2.5 sources, coverage and conflict rules

## Primary source and verification scope

- Primary: [【即梦】Seedance 2.5 使用手册](https://bytedance.larkoffice.com/wiki/RXh5ww6EqighMdkVTMccm2d4n7e), ByteDance-hosted official manual. Historical read: 2026-10-02; page displayed last modified September 21 and 67,524 characters. The displayed modification label is not a model release date.
- Historical read scope: all main-body sections, parameter tables, prompt methods and long code-block examples through the final birthday-grid example; operation screenshots also checked. Long blocks were separately scrolled/selected to read their tails, rather than treating truncated accessibility text as complete. The access check below does not renew this whole-manual verification.
- Not established: complete viewing/listening of every embedded example, quantitative output accuracy, paid project validation, or coverage of separately linked manuals. Official advertised effects remain documentation claims, not project-verified results.
- Main guide: [seedance-25.md](seedance-25.md). Detailed branches: [seedance-25-operations.md](seedance-25-operations.md). Wider model provenance: [model-manual-authority.md](model-manual-authority.md).

## Public access and offline fallback

Access checked **2026-10-09** in a browser. Each of the four Feishu/Lark pages displayed its title and body together with a “登录/注册” button; no sign-in or permission change was performed. These are observed guest-readable pages, not guaranteed permanent access. Anonymous HTTP/text-reader attempts did not provide usable bodies in this check; that is a retrieval limitation, not evidence of a login requirement.

| Source | Observed access | Scope of this check |
| --- | --- | --- |
| [Chinese Jimeng manual](https://bytedance.larkoffice.com/wiki/RXh5ww6EqighMdkVTMccm2d4n7e) | Guest-readable; September 21 modification label | Title, opening body and capability table; earlier full read remains dated 2026-10-02 |
| [English Dreamina manual](https://bytedance.larkoffice.com/wiki/NjnWwvf4BiFYFLk2RzrcEgaunGf) | Guest-readable; August 17 modification label | Title and opening body; translation/parameter parity not verified |
| [White-model rendering plugin manual](https://bytedance.larkoffice.com/wiki/Jwg8wRW1Fig7CxkOMfScitsvnub) | Guest-readable; July 30 modification label | Access and introductory instructions only; no plugin installation or runtime validation |
| [Seedance 2.5 prompt-writing guide](https://bytedance.larkoffice.com/docx/OsiUdR1OxoDqvnxsK8LczYx7nPd) | Guest-readable; September 21 modification label | Title, introduction, contents and its official-site link; this resolves the earlier access gap for this URL |
| [Volcengine official prompt guide](https://docs.volcengine.com/docs/ark/seedance-2-5-prompt-guide?lang=zh) | Body readable while Login/Register links are visible | Linked by the Feishu prompt guide; checked reference roles, prompt construction, time stages and edit/preservation guidance, not every embedded media example |

The Volcengine page is a **non-Feishu alternative for prompt-writing methods**, not a full mirror of the Jimeng product manual. Its API parameters and ordinary-generation envelope do not establish Jimeng-only modes such as ultra-long generation, or controls in another destination.

When a reader or agent cannot open a source:

1. Try the direct link in a normal browser if available; a failed text fetch alone does not prove the document is private.
2. For prompt construction, use the official non-Feishu guide above. Keep each document's product, version and operation scope separate.
3. Continue supported planning with this package's [adapter](seedance-25.md) and [operation methods](seedance-25-operations.md), labeling their source dates. Installation and ordinary use never require Feishu, an account or any live website.
4. If a current limit or mode is essential and cannot be verified, mark it unknown and ask for the relevant current official excerpt or destination evidence. Do not claim fresh verification, guess a limit or block unrelated creative work.

Keep links and authored summaries, not redistributed manuals, screenshots or demo media. A source page's installation commands are not instructions to install software during source checking.

## Source priority

Use the version-specific official manual over conflicting host supplements. Do not average different-mode limits or turn one operator's interface observation into a model capability. Private legacy documents and billing/UI snapshots are not bundled or required in this public package.

The official guide itself contains both version-specific and shared/older-labeled rows. Prefer an explicit 2.5 update over a 2.0 row for the same capability. Shared rows can supply scoped context, not silently become 2.5-exclusive evidence. Distinguish an actual conflict about the same mode from different platform features or different operations.

If official text contradicts itself, do not invent a resolution or treat a demonstration as mandatory syntax. Apply the unambiguous parameter/mode description for its stated scope, preserve the user's approved facts, and mark unresolved details when consequential. New authoritative revisions can supersede this dated baseline; record the changed scope instead of importing third-party guesses.

## Documented envelope by operation

These values describe the official manual's model/product branches, not a claim that all third-party endpoints expose them. Keep them available for planning even when no host has been selected. At actual submission check the specific host binding/operation; unavailable execution does not erase the documented branch.

| Branch | Official manual baseline | Interpretation |
| --- | --- | --- |
| Ordinary video generation | 4–30 seconds; automatic duration is also described | Selected duration, prompt timing and measured output are separate; do not use the 2.0 4–15 row for 2.5 |
| Ultra-long generation | 30–180 seconds in its own mode | Not ordinary generation's limit and not an instruction to chain extensions |
| Video extension | Source ≤30 seconds; add 4–30 seconds | Final duration = source + addition; 30 + 30 can yield 60 seconds. Re-extension still requires the next source ≤30 seconds |
| Image references | Up to 30 images | Ceiling, not optimal count or a cast-size recommendation |
| Video references | Up to 10; combined duration ≤30 seconds | Specify property/range; a role label does not prove precise control |
| Audio references | Up to 10; combined duration ≤30 seconds; audio-only references supported | Input capability, not proof of a separate audio-output endpoint |
| Resolution in the parameter table | 480p / 720p | Some operation screenshots use “720P+”; do not infer its exact pixel dimensions or promote prompt words such as 4K/8K into output specifications |

The legacy combined 50-file figure follows the listed per-type maxima; do not add an independently guaranteed aggregate upload count where the current operation has not established one. File encodings, sizes, ratios, pricing and mode-specific combinations need exact source/interface evidence when used, not extrapolation from a marketing prompt. No arbitrary 5,000-character or other prompt cap follows from comments or examples.

## Recommendations are not hard limits

The manual distinguishes reference files, referenced subjects and editing inputs; keep those quantities separate.

- For image-subject reference, it recommends the 1–8 range over 9–12 for stability. For 1–5 subjects, single-/multi-view sources can work; above five, single-view input is described as more stable. These are not a universal cast cap or proof that every 30-image combination works equally well.
- Video/audio subject references in the 1–5 range are recommended over 6–10; 5–10-second subject clips are guidance, not a universal minimum reference duration.
- Editing within 20 seconds is recommended for reliability. Editing reference images in the 1–5 range are preferred to 6–8. Do not manufacture a 20-second rejection rule or apply an editing recommendation to ultra-long generation.
- Use only the material needed for the control problem. Clean, distinct reference roles matter more than filling every upload slot.

## Method coverage in the maintained adapter

| Official content | Maintained location and treatment |
| --- | --- |
| Parameters and interaction | This register; execution availability remains separate from capability support |
| Basic prompt construction and realistic characters | Core construction/performance sections; appearance-specific realism, not a compulsory photographic style |
| 30-second and ultra-long prompts | Separate operation branches with continuity, timed stages and ending checks |
| Video extension and transitions | Source/addition clocks, join state and transition anchors in the extension branch and core camera section |
| Smart/advanced/video editing, spatial markings | Edit target/range/change/preservation plus optional actual frame annotations |
| White-model control, coarse and detailed inputs | Explicit control ownership, placeholder mapping, missing-detail supplementation and independent camera/appearance review |
| Timestamps, language, captions/BGM controls | Core timing/sound plus removal/edit methods; no frame accuracy or lossless-audio guarantee |
| Improved generation and multimodal examples | Reference-role assignment, acting/action/camera design and empirical review, not universal quality claims |
| Creative transfer, local edits and storyboard/grid examples | Transfer mechanism and boundaries; temporal interpretation of panels rather than copying examples or enforcing their panel counts |

The showcase chapters are examples of these capabilities, not a demand to run every operation, generate comparison videos or spend credits during skill maintenance.

## Example defects that must not become rules

Some official examples conflict internally: the glacier sequence moves into polar night but later requests sunlight under water; a coffee example mixes natural-sound-only language with piano music; other examples mix a global single-language requirement with multilingual lines or inconsistent duration declarations. Correct such contradictions against the approved brief instead of copying them. A demonstrated “4K/8K/60fps” phrase or named renderer is an appearance request, not evidence of actual output resolution/frame rate/rendering software.

Preserve wanted native contact/voice layers while excluding post-only ambience/music. Distinguish bans on generated subtitles from required story text. Time-coded prompts still need independent checks of physical causality, dialogue allowance, synchronization and the intended ending.

## Remaining source limits

The English and plugin documents have an access check, not a full technical review. The extended prompt guide's former access gap is resolved, but its complete contents and media have not been independently validated. No access check establishes output reliability, current availability in a user's tool or permission to redistribute third-party content.
