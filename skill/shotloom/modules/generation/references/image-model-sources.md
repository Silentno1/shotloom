# 三组生图模型：官方来源、覆盖与差异

核验日期：2026-10-02。适用官方面：Midjourney/Niji 网页与 Discord；Google Gemini API；OpenAI 图像 API。第三方别名、槽位、费用与可选版本未由这些文档验证。本索引记录方法来源，不是所有页面永不过期的完整镜像。

## Midjourney / Niji

| 编号 | 官方来源 | 适用内容 |
| --- | --- | --- |
| MJ-V | [Version](https://docs.midjourney.com/hc/en-us/articles/32199405667853-Version) | V6/6.1、V7、V8.1/8.2、Niji 版本和功能表；V8.0 退役 |
| MJ-P | [Prompt Basics](https://docs.midjourney.com/hc/en-us/articles/32023408776205-Prompt-Basics) | 主体/媒介/环境/构图等具体描述；不要堆无关词 |
| MJ-I | [Image Prompts](https://docs.midjourney.com/hc/en-us/articles/32040250122381-Image-Prompts) | 内容参考、URL/网页用法、Image Weight |
| MJ-S | [Style Reference](https://docs.midjourney.com/hc/en-us/articles/32180011136653-Style-Reference) | sref/sw/sv 的职责与版本区别 |
| MJ-O | [Omni Reference](https://docs.midjourney.com/hc/en-us/articles/36285124473997-Omni-Reference) | V7 单图 oref、ow 与不兼容操作 |
| MJ-E | [Edit Model](https://docs.midjourney.com/hc/en-us/articles/48495453462797-Edit-Model) | V8 编辑、最多四图、edit 参数及限制 |
| MJ-L | [Legacy Features](https://docs.midjourney.com/hc/en-us/articles/33329788681101-Legacy-Features) | 旧 Character Reference 与历史版本方法 |
| NJ-V | [Niji 7 release](https://nijijourney.com/blog/niji-7) | Niji 专门模型，cref 不支持；不将发布时 coming soon 当成当前永久不可用 |
| NJ-P | [Niji 7 Prompting Guide](https://nijijourney.com/blog/niji-7-prompting) | 字面描述、背景/裁切/光线、旧图 sref 与克制镜头 |

以上页面正文已读；示例图片用于说明的文字不等于逐张视觉评测，未运行对照生图。方法文件：[midjourney.md](midjourney.md)。

保留差异：旧 Character Reference 链接跳转到 Edit Model，旧规则从 MJ-L 追溯，不能覆盖历史任务。MJ-V 的主版本 Remix 支持与 MJ-E 的 Edit 禁用应按子模式区分。MJ-I 的 iw 表未列 V8.2，不填推断值。MJ-S 关于 Draft 的表述与 MJ-V 版本表不完全一致，具体版本/模式使用前重查，不默认支持。Niji 的发布说明与主版本编号不可相互外推。

## Nano Banana / Gemini Image

- NB-A：[官方 image-generation 文档](https://ai.google.dev/gemini-api/docs/image-generation)。读取型号概览、3.x 能力/参考表、搜索与多轮相关方法、提示指南的生成/编辑方法、限制及配置；代码仅按相关入口查阅，未逐语言逐行审查全部 SDK 示例。型号别名、数量、分辨率需依这份现行型号表，而非旧博客。
- NB-P：[Google Cloud 官方 prompting guide](https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-nano-banana)。读取正文五组方法、创作控制与注意事项；发布日期 2026-03-05，型号/Preview 名称可能早于 NB-A，作为方法补充而不是最新型号表。

方法文件：[nano-banana.md](nano-banana.md)。覆盖原版、Pro、2、2 Lite；没有把 Google 视频生成功能引进本次维护。

保留差异：NB-A 概览/参考表使用 `gemini-3-pro-image`，后部一个尺寸标题写“3.1 Pro Image”；不据这个标题发明新的模型 ID。使用需查 exact 型号的官方模型页。Lite 的参考数量与“不针对多参考优化”的定位并存，不能将数量上限等同质量保证。语义 masking 是提示方法，不凭此推导 API 像素蒙版参数。

## GPT Image 2.5

- GI-P：[官方 image-prompting guide](https://developers.openai.com/api/docs/guides/image-prompting)。读取 2.5 的型号选择、参数、基本方法及生成/编辑相关示例说明，包括透明、精确文字、多参考、草图和连续编辑；不将后部旧型号标签内容移植为 2.5 规则。
- GI-A：[官方 image-generation guide](https://developers.openai.com/api/docs/guides/image-generation)。查阅 2.5 请求、生成/编辑/多轮入口、输出控制与 earlier-model 边界；没有逐语言执行代码或接入接口。

方法文件：[gpt-image-25.md](gpt-image-25.md)。覆盖 Flare/Sunburst；不是将用户的 2.5 请求降级到 1.5/2。

保留差异：同页旧示例/旧 input_fidelity 说明不能证明 2.5 参数支持；以具体型号与任务字段为准。质量标签、官方迁移方案和对照图片不能转写成已测速度、固定成本或项目最佳型号。

## 证据使用和后续专项优化

以上支持“有官方方法可用”，不支持“已在本项目验证成片质量”。如遇新版本/新任务、冲突或影响提交的参数，回原始对应段落核查。来源不可访问或型号无法确认时，只保留已知任务意图与静态视觉合同，标明未知限制；不复制别家特殊语法，也不无依据宣布功能不存在。

日后用户实际使用并提供图片/视频时，记录 exact 模型、任务、参考职责、原始提示与设置，查看真实输出后再作专项优化；生成成功、文档可读、关键词检查通过都不是画质通过。任何新增付费验证仍服从当次授权和制作暂停。
