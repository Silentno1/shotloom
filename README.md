# Shotloom

English | [简体中文](README.zh-CN.md)

**A directing skill for AI filmmaking, driven by review and iteration.**

Shotloom is an open-source directing skill for AI films, short dramas and animated/comic-style dramas. It helps an agent turn a script and creative intent into shot plans and model-specific prompts, review the returned media, and carry revision decisions into later shots and the edit.

Use it for a full production workflow or a single scene, shot or review. The package contains instructions, references and optional checking scripts, loaded according to the task.

Working version: `0.2.2` (unreleased). The latest published package is [v0.2.1](https://github.com/Silentno1/shotloom/releases/tag/v0.2.1). To try changes in this checkout, install its complete `skill/shotloom` folder as described below.

## A small example

Input: “A sister hands a workshop key from her right hand to her brother's left and says exactly ‘店交给你了。’. He looks at the key before answering. Keep the shared task visible.”

| Deliverable | What Shotloom makes explicit |
| --- | --- |
| Script and shot plan | Shot A shows the transfer; Shot B gives the receiver's pause room. The brother's unspecified answer remains a question, not invented dialogue. |
| Prompt draft | Ordered actions, exact speech, reference roles, sound ownership and a final state: the key stays in the brother's left hand. |
| Review | Three stills can support visible-state observations; they cannot establish the transfer motion or sound. Those checks remain unverified. |
| Revision record | After actual review and explicit acceptance, record the observed endpoint. Replacing Shot A makes dependent continuity in Shot B due for another check. |

See the [worked example with shot and prompt excerpts](examples/public-workflow/README.md). It is a fictional teaching example, not a generated film or a claim of production success.

## How it works

1. **Establish the creative plan.** Identify the script, directing approach, visual treatment and details that must stay unchanged.
2. **Prepare generation.** Plan shots and references, then write prompts, proposed settings and review criteria for the chosen model.
3. **Generate in your own tools.** You operate the generation tool and bring the resulting images, video or audio back to the agent.
4. **Review and iterate.** Use accessible evidence to decide what to keep, repair, regenerate or leave unverified. Trace how a change affects later work.
5. **Continue into editing and delivery.** Use actual media to plan selections, rhythm, captions, sound and post-production handoff. Execute local edits only with suitable tools and authorization.

Prompts describe intent. Only reviewed and explicitly accepted media states become continuity references. When an earlier shot is replaced, work that depended on its old state needs another check.

## What you can use it for

| Area | Typical tasks |
| --- | --- |
| Direction and shot design | Diagnose a scene's purpose; plan performance and blocking; compare framing, camera movement, action and rhythm |
| Visual design | Define production method and appearance; organize characters, locations, props and reference assets |
| Generation planning | Write image, video and audio prompts independently from the same approved plan; specify reference roles and unverified settings |
| Review and continuity | Inspect actual media, diagnose failures and track accepted states and their effects on later shots |
| Editing and post-production | Plan timed previs and selections, reconform captions after edits, calibrate final-output audio sync, and prepare handoffs and final checks |

Formal production needs an explicit, approved directing approach. It can draw on a named director or work, or be authored for the project. The 69-profile director/work catalog offers optional retrieval and suitability scoring. Ordinary work keeps the current approved method; project-authored methods skip the catalog. Named-reference research retrieves only relevant topics or profiles, without loading all JSON into the conversation. See [loading and compatibility](docs/PUBLIC-BASELINE.md).

Prompt guidance covers H3, Seedance, Seedream, Kling, Wan and several image-model families. Depth varies by version and task; see [model routing and coverage](skill/shotloom/references/model-selection.md). References carry source dates. Changing capabilities and limits still need verification when used.

The skill's authored guidance is included locally. Feishu or any live documentation site is not an installation requirement. The [Seedance source register](skill/shotloom/modules/generation/references/seedance-25-sources.md) records guest access, a non-Feishu official alternative and what to do when a source cannot be read.

## Quick start

### Compatible agents

Shotloom is designed for mainstream AI agents that can load `SKILL.md` and its supporting resources. The repository provides installation presets for Codex, Claude Code and the shared `.agents/skills` directory. For other compatible agents, use `--target` to select their skill directory.

These are skill-loading options, not a claim of end-to-end testing on every agent. Media review and local execution depend on the agent's actual capabilities.

### Install

Copy the complete `skill/shotloom` directory into a compatible agent's skills directory. If you have a `shotloom-VERSION.zip` package, extract and place its entire `shotloom` folder there.

Alternatively, choose one installation command from the repository directory:

```bash
./scripts/install.sh --agent agents
./scripts/install.sh --agent codex
./scripts/install.sh --agent claude
```

Use `--target` for another destination. Existing installs are refused by default; `--force` first preserves a backup. PowerShell: `.\scripts\install.ps1 -Agent codex`.

All workflows are included in this folder; no companion skills are required. Agents without skill discovery can read `SKILL.md` and follow its resource links. Pasting only the entry without the referenced files is not a complete installation. `agents/openai.yaml` is optional UI metadata.

### Start with a concrete task

Provide the current goal, relevant script or media, and anything that must stay unchanged. Each request below can be used on its own:

```text
Use Shotloom to read this scene. Keep my own directing approach and check blocking and performance first. Do not choose a named director, generate media or write files.
```

```text
Use Shotloom to write separate H3 and Seedance 2.5 prompts for the same approved shot. Preserve the dialogue, look, sound-source assignments and ending state. Flag any unverified settings for each model.
```

```text
Use Shotloom to review this video. State what you inspected, what remains unverified, and whether to keep, repair or regenerate it. Do not update continuity yet.
```

```text
The first shot has been replaced. Use Shotloom to identify later shots that depend on the old state. Only list what needs another review.
```

The worked example above follows the current workflow. The older golden-scene fixture is retained as historical teaching material and linked from that example, not used as current release acceptance evidence.

## Capabilities and boundaries

What the agent can complete depends on the capabilities it actually has:

- **Conversation and complete skill material:** creative planning, prompt preparation, manual review guidance and copyable state records.
- **Project file permissions:** authorized records and handoffs in a user-chosen location, with no required notebook app, database or fixed directory.
- **Python 3.10+:** optional structure, version, continuity and timing checks. The written methods remain usable without Python.
- **FFmpeg/FFprobe:** optional media metadata and technical evidence extraction, not a prerequisite for installing the skill.
- **Authorized local editing or compositing tools:** scoped previs, edits, repairs and exports. Otherwise, return a reproducible operation plan.

Actual-media review also requires the relevant image, video or audio perception. Thumbnails do not establish motion quality; transcripts do not replace listening. Unavailable checks stay unverified, even when arithmetic or scripts pass. See [environment](skill/shotloom/references/environment.md) for the full contract.

Shotloom does not call generation services, manage accounts, select providers, upload assets, spend credits or publish. File changes and local edits follow user authorization. You operate external generation tools.

## Development status and contribution

Current checks cover resource structure, local links, rule and arithmetic checks, and execution after relocation. Tests use synthetic records and local synthetic media, without remote generation. Passing tests does not establish creative quality, source authenticity or real user approval.

Run from the repository directory:

```bash
python3 scripts/validate.py
python3 scripts/run_tests.py
```

For full local media verification, install FFmpeg and FFprobe, then run `python3 scripts/run_tests.py --require-media`. This mode prints tool versions and fails on skipped tests. The portable run above reports skips and does not count as full media verification. All four Python 3.10/3.13 portable and media-required CI jobs passed on 2026-10-10; each media job executed all 485 tests with no skips. See the [recorded CI results](docs/TESTING.md).

This version has not completed real-film end-to-end validation or been verified across all agent environments. PowerShell installation still needs runtime confirmation. See [testing scope](docs/TESTING.md) for results and unverified areas.

After verification, maintainers can run `python3 scripts/build_release.py` to create a local package. This does not upload, publish or replace an existing archive.

[Contributing](CONTRIBUTING.md) · [Attribution](ATTRIBUTION.md) · [MIT](LICENSE)

No model weights, service code, private manuals, personal project media or third-party film assets are bundled. Shotloom has no affiliation with or endorsement from the named model developers.
