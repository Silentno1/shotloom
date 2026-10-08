# 导演方法选择、批准与继承

这是 Shotloom 五模块共同的规则。正式制作需要清楚、已获授权且适用于当前作品的导演方法；**不要求绑定知名导演，不要求所有作品先做导演排名**。它不授权写文件、生成、上传、花费或发布。

## 两条平等路径

- `named_reference`：采用具名导演或署名正确、范围明确的作品级参考。限定作品、季集、段落及方法，区分来源事实与本片改编。仅此路径需要导演资料库、署名研究和来源卡片。
- `project_authored`：从用户要求、完整权威作品范围和资源设计本片方法。记录观看立场、表演、调度、摄影、时间、剪辑和声音规则及反例，不虚构名人背书。用户已有原创方法也走这条路径，无需补选导演。

已有明确方法就复用；没有时可提出与任务规模相称的建议。只读分析、局部诊断、未批准的方案草稿不要求先完成方法锁。正式分镜、正式资产、制作提示词、正式剪辑和验收继承有效记录。`concept` 标签不能把正式制作伪装成草稿。

只有选择具名参考或明确要求适配比较时才使用 [director-scoring.md](director-scoring.md)；不是自建方法的前置条件。明确 `selection_exploration` 的纸面对照、已有材料粗预演可先于锁定，不能自动成为正式资产。

## 先读作品，再确定方法

建立全作品方法前，读完用户指定的当前完整权威范围。只有大纲就明确“大纲范围”，只有片段就只作局部判断。提炼观众关系、冲突、信息策略、表演尺度、空间动作、时间与声音。局部调整只读相关片段、现行方法和依赖，不重启全流程。

具名路径用 `scripts/director_style.py catalog` 读索引、`profile ID` 读 [director-profiles.json](director-profiles.json) 中有关档案；题材检索见 [director-coverage.md](director-coverage.md)。`fit/avoid`、迁移假设、题材路线是检索辅助，不是适配证明。库外参考用 `external:<slug>`，仍核对真实署名、作品范围和依据。

自建路径把方法写入 [authority-and-method-bible.md](authority-and-method-bible.md) 的同一份记录。没有外部来源不妨碍原创设计，但须称为设计提案，不是已验证导演习惯或模型效果。

## 授权、版本与局部变化

权限来自用户明确指定、认可方案，或明确委托智能体选择。分数、默认第一名、模糊“继续”不创造权限；已有明确委托不逐步重复询问。普通分析不增加独立签字环节。

一个作品一份当前方法记录，承接方法圣经，不建立竞争权威。两条路径都记录授权依据、作品/剧本版本、采用与排除方法、保留事实/画风/精确锁、允许变化、验收及限制。实质改变方法须授权和新版本；日常强弱变化遵守原允许范围。公共资料升级不使有效项目锁失效。

保持一套连贯方法。多种参考可作为职责明确的研究来源，但本包没有自动多导演投票、权重混合或冲突调和算法。未实现的算法不是通用创作禁令，也不能成为拼贴矛盾风格的借口。

## 从方法到执行

关键决定遵循：作品处境 → 观众应知道或感到什么 → 本片方法 → 可见/可听执行 → 何时不适用 → 如何检查。见 [director-decision-practice.md](director-decision-practice.md)。

具名参考用 `scripts/director_methods.py profile ID` 时区分来源卡片与原创应用建议。自建方法沿用相同决策链，不运行人物检索、不造卡片。不要求每场展现某位导演独有招式。纸面对照不授权生成，未用某手法不是失败。

## 五模块继承

导演方法、画风、模型语法不能互相替代。director 定义意图；visual-design 保留独立画风；generation 从同源记录编译；review-continuity 检查实际结果；edit-delivery 保留观看立场和节奏。每件工件只携带相关方法与 `director_style_ref`。

缺锁或版本失配可诊断，不能作正式验收或传播批准。换模型不换方法，改公共目录不重做已接受素材。静态图片不证明动态，结构检查不证明艺术质量。

## 可选机器记录

无 Python 时用同字段 Markdown：明确 ID/版本并人工核对内容，不编哈希或声称程序通过。有 Python 时运行 `scripts/director_style.py check PACKET --stage director|visual|generation|review|edit`。命令相对模块目录，其他目录使用实际包路径。

正式包有 `workflow_scope: production`、独立从项目读取的 `current_authority: {project_id, work_scope, script_version}`、当前 `director_style_lock`、工件原有 `director_style_ref: {id, version, sha256}`。不可从旧工件反推当前权威，或刷新过期引用掩盖变更。

共用字段：

- `schema_version: 1`、`id`、`version`、`status: selected`、`method_mode`、`authority`。
- `authorization: {mode: user_selected|user_approved|ai_selection_delegated, source, scope}`，来源须是真实决议位置。
- `fit_basis: {reading_scope: complete_authoritative_scope, rationale, script_evidence: [...], countercase}`。
- `evidence: [{id, source, scope, supported_claim, kind, checked_at}]`，对应真实已读资料/决定，不用空链接冒充依据。
- `adopted_methods` 含 performance/blocking/viewpoint/camera/time/editing/sound/transitions；不相关维度说明不适用及理由。
- 非空 `excluded_methods`、`preserved_locks`、`review_criteria` 文字列表，及 `variation_policy`。
- 替换带 `supersedes: {id, version}` 和 `change_authorization_source`。

具名路径另有 `lead: {profile_id, name, reference_scope: [{work, scope, evidence_ids}]}`。库内名称与 ID 一致，退役档案不可静默改名。证据种类 creator_account、collaborator_account、production_primary、work_observation、critical_analysis 及既有别名映射保持；映射不提升可信度。

自建路径另有 `project_method: {name, design_basis}`，不填写 `lead`。新增 `project_design`、`user_requirement` 表示原创设计与用户要求；外部事实仍用其对应种类，不把原创方案冒充导演史实。剧本和用户决定足以支撑原创方法，无需名人资料。

省略 `method_mode` 的旧记录按 `named_reference` 检查，不重解释历史。`fingerprint LOCK` 计算规范 JSON 指纹；变更须显式升版和更新受影响工件。程序不认证授权真假、完整阅读、来源可靠性或作品好坏。

探索包用 `workflow_scope: selection_exploration`、concept 或未标级别、`exploration: {purpose, not_for_production: true}`。`diagnostic` 不是生产包。Shotloom 交付外部生成计划，不提交生成请求。
