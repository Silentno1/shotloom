# Changelog

All notable changes to Shotloom will be documented here.

## [0.2.2] - 2026-10-10

### 中文

0.2.2 是一次修复与文档更新，延续原有五模块制作流程。

- 修复审片区间刚好到片尾时可能被误判超长的问题。按解码后的视频帧时间确认边界，仍拒绝真正越界的区间。
- 统一两条对白审核入口的实现，补全 JSON 输出、Unicode 文本和异常输入检查。文字匹配不等于已经听审或通过创作验收。
- 将 Bash 和 PowerShell 安装器的暂存、备份放到技能扫描目录之外，避免旧备份被识别成第二个技能。重复更新保留独立备份；不自动移动或删除旧安装器留下的备份。
- GitHub CI 分开验证无媒体工具和完整媒体环境。Python 3.10、3.13 的完整媒体测试均执行 485 项、零跳过；修正历史测试记录的适用范围。
- 补充中文触发词、短剧和漫剧说明、分镜与提示词文字示例；保留旧路径兼容，并明确导演资料库按需检索。
- 记录四份飞书资料的访客访问检查，提供非飞书官方备用资料和离线处理说明；移除一处来源链接中不必要的分享参数。来源可访问不等于所有历史模型参数已重新核实。

升级时下载本版本的 `shotloom-0.2.2.zip`，先备份自行修改的技能文件，再更换整个 `shotloom` 文件夹。仓库安装器的 `--force` / `-Force` 选项会备份已有安装；安装器不包含在运行时 ZIP 中。GitHub 自动生成的 Source code 压缩包是完整仓库。此次升级不迁移用户项目或修改媒体文件。Windows/PowerShell 运行、真实全片制作和所有 Agent 环境仍未逐一验证。

### English

### Fixes

- Bound video review ranges by decoded video timestamps and the final frame's duration, not container duration. Preserve VFR/nonzero-origin handling, reject genuine out-of-range requests and label a tightly checked CFR fallback as an estimate.
- Use one dialogue-audit implementation behind both entry paths, preserving `--json` and Unicode case folding. Reject empty expected dialogue, malformed transcript data and invalid/out-of-media timing; a wording match does not imply listening or creative approval.
- Move Bash and PowerShell installer staging and backups outside the skills discovery root, so an old backup cannot be loaded as another skill. Keep distinct backups on repeated updates and recover the old installation after a failed swap. Backups made by older installers are not moved or deleted automatically.
- Separate portable CI from required-media CI on Python 3.10 and 3.13. The media job explicitly installs FFmpeg/FFprobe, records versions and fails on any skipped or unexecuted discovered test.

### Documentation and routing

- Add Chinese task keywords and concrete short-drama/comic-style-drama examples to the bilingual introduction.
- Expand the current written workflow with shot plans, a scoped prompt draft and evidence-limited review examples. Keep the historical golden scene separate from current acceptance claims.
- Record guest access to all four Feishu sources on 2026-10-09, add a verified official non-Feishu prompt guide and document offline fallback. Access verification does not renew all historical model claims.
- Remove an unnecessary sharing query parameter from a source link and correct the scope of historical test claims.
- Route the main entry directly to maintained references while retaining old compatibility paths. Keep director research optional and explicitly prohibit preloading the full JSON catalog for ordinary work.

### Verification and upgrading

Both Python 3.10 and 3.13 required-media CI jobs executed all **485 tests with zero skips**. Portable CI deliberately omits media tools and is not a full media pass. See [testing evidence and limits](docs/TESTING.md).

Download `shotloom-0.2.2.zip`, back up any personal edits, then replace the complete `shotloom` folder. The repository installers offer `--force` / `-Force` with backup; those installers are not included in the runtime ZIP. GitHub's automatic Source code archives contain the full repository. This update does not migrate projects or modify user media. Windows/PowerShell execution, real-film production and every agent environment remain unverified.

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
