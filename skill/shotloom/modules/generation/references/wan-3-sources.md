# Wan 3.0 官方来源与覆盖

基线记录的读取日期：2026-10-02。适用面：阿里云 Model Studio 的 Wan 3.0 视频预览版；不代表任何第三方使用入口已验证，也不代表公开化时重新核实。方法入口：[wan-3.md](wan-3.md)。

## 来源

| 编号 | 官方来源 | 本次读取与用途 |
| --- | --- | --- |
| W3-P | [Wan 3.0 prompt guide](https://www.alibabacloud.com/help/en/model-studio/wan3-video-generation-prompt-guide) | 完整读取通用写法、任务/引用/时间/对话/声音/风格规则；针对性读取多主体、分镜、白模、画线运镜、时序迁移、音频、编辑、延长和首尾帧方法与选定示例。未逐条通读全部行业展示提示词，未逐个观看嵌入成片；未安装页面附带的优化 Skill 压缩包。 |
| W3-G | [Wan 3.0 usage guide](https://www.alibabacloud.com/help/en/model-studio/wan3-video-generation-guide) | 阅读模型/任务概览、模式表及相关使用示例，用于与提示指南和参数表交叉核对；未把全部语言示例代码当成已执行测试。 |
| W3-A | [Wan 3.0 API reference](https://www.alibabacloud.com/help/en/model-studio/wan3-video-generation-api-reference) | 完整读取页面正文及参数/素材组合/响应说明；只提取影响提示与操作计划的事实，不接入 API、不执行示例。 |

## 关键事实索引

下列为 2026-10-02 核验的官方面事实；复用时按 [model-manual-authority.md](model-manual-authority.md) 判断是否需要更新，不能永久标作 current。

- `wan3.variant`：standard/prime 的 exact ID 与 preview 状态，W3-A 的 model / introduction。
- `wan3.input-combinations`：首尾帧与参考组互斥，file/link 互斥，音频可独立作为参考组输入；W3-A Material combinations。
- `wan3.input-envelope`：各媒体数量、时长、尺寸、格式和大小；W3-A input.media。
- `wan3.output-envelope`：时长、帧率、分辨率及带视频的约束；W3-A parameters / usage。不能将 output 限制套给 input。
- `wan3.reference-labels`：Image/Video/Audio 分别计数；W3-P Reference material citation，W3-A input.prompt/media。
- `wan3.rewrite-not-extension`：prompt_extend 为改写且 file/link 必须开启；W3-A parameters。

## 冲突与不可推导项

1. **延长时长：**W3-P Video extension 的 duration 建议，与 W3-A 的带视频总时长口径不能直接合并。保留源片/新增/最终长度三项，实际入口需澄清。不能套 Seedance 的新增时长语义。
2. **延长方向：**有的英文示例使用 forward，却描述源片之后的动作；另一段按首帧之前解释。使用明确的首/尾边界，不继承含混译词。
3. **镜头建议：**提示指南常见 2–5 秒与使用指南的 4–6 秒是不同写法建议，不是硬限制；局部示例时间段存在空隙，不照抄。
4. **示例素材编号：**展示图标签与部分示例文字不一致。只以真实本次上传顺序编译，不复制示例映射。
5. **能力宣传：**“一致”“精确”“还原”等是意图/能力描述，不证明身份、物理运动、口型或音轨必然合格。没有本项目实测证据。

不使用同名商业网站或仅自称 Official 的仓库代替以上第一方来源。未找到或未读到的分支保留 `unknown`，只交付不含伪参数的通用意图合同；不因此否认整款模型存在，也不自动追加付费测试。
