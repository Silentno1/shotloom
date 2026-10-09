# Worked example: the workshop key / 修理铺的钥匙

This is a fictional written example for the 0.2 workflow, maintained with 0.2.2. It shows the brief, shot plan, prompt draft and evidence-limited review an agent can return. No video, still, voice, actual inspection or real user approval is represented here. Never copy its fictional decisions into a real project's approval record.

这是当前流程的文字教材，下面的补充简报和审核场景均为虚构。它展示交付物的具体写法，不冒充真实生成案例；目前没有可供展示的实测画面或 GIF。

## Request and bounded authority

“Two siblings close a workshop. The sister hands the key from her right hand into the brother's left hand and says exactly: 店交给你了。The brother looks at the key before answering. Use my own directing method: keep the shared task visible, let the listener own the pause, and avoid a heroic music cue. Plan two shots; no generation or file writes.”

The agent reads the complete supplied scene and treats the quoted method as user-supplied direction for this planning task. No celebrity research is required. It clarifies only materially missing story facts, labels drafts as drafts and does not invent the brother's exact answer.

## Minimal conversation record

- Project: workshop-example; script: scene-v1; scope: this complete scene only.
- Method: project_authored / shared-task-v1; authority: the actual request, not a fabricated external reference.
- Shot A plan: establish both people and the visible key transfer; required endpoint is key in brother's left hand.
- Shot B plan: receiver's attention moves from key to sister before the authorized answer; inherits key ownership and position.
- Appearance: unresolved until user supplies/approves it; do not default to a house style.
- Sound: exact line and sync requirements retained; no music unless later approved; actual native versus post ownership must be settled before formal compilation.
- Storage: conversation-only; user retains this record. No hash or saved-file claim.

The missing appearance/answer/sound choices need not block a blocking diagnosis, but they prevent pretending this draft is a fully approved production prompt. Once those relevant choices are approved, each chosen model is independently compiled from the same source lock. The user operates generation outside Shotloom.

## Shot-plan excerpt / 分镜交付片段

| Shot | Proposed image and action | Sound | Expected state, not observed state |
| --- | --- | --- | --- |
| A, proposed 8 s | Fixed medium two-shot; faces and both receiving/passing hands visible. Sister speaks, extends her right hand; brother receives with his left; sister releases; brother checks the key. | Exact sister line: “店交给你了。” No invented reply. | One key in brother's left hand; sister's right hand empty. |
| B, duration open | Receiver-focused closer view on the same side of the action axis. His gaze moves from the key to his sister before his answer. | Brother's wording and duration remain unresolved. | Inherit the key's accepted position only after A is actually reviewed and accepted. |

The framing serves the shared task in A and the receiver's pause in B. Eight seconds is a proposed allowance for this example, not a fixed duration per action or a model capability claim. An unreadable handoff is a coverage issue to resolve before committing to the shot.

## Prompt-draft excerpt / 提示词交付片段

For this next **fictional** exercise, the brief supplies additional choices for A: live-action appearance, ordinary daylight, blue work shirt on the sister, grey T-shirt on the brother, sister screen-left and brother screen-right. Native sound carries her line and the key contact; room ambience is post-production only, with no score. These are teaching inputs, not defaults for other projects. B still lacks its approved answer and is not ready for formal compilation.

Planned references, if supplied: sister identity, brother identity, workshop layout and key design each have a separate role. None are attached to this example or claimed inspected. The agent must check actual assets and bind their real upload order outside the pasteable prompt; it must not fabricate reference IDs.

Seedance 2.5 ordinary-generation writing draft for A:

```text
真人实拍外观，日光下的修理铺内。姐姐穿蓝色工作衬衫，位于画面左侧；弟弟穿灰色 T 恤，位于画面右侧。固定平视中景，两人的脸和交接钥匙的双手始终可见。

0–2 秒：姐姐右手握着唯一的一把修理铺钥匙，看向弟弟，以日常交代工作的音量说普通话：“店交给你了。”弟弟看着姐姐，尚未接钥匙。
2–5 秒：姐姐伸出右手；弟弟伸左手接住钥匙。等弟弟的左手已经握住钥匙，姐姐才松开右手。
5–8 秒：姐姐收回空着的右手。弟弟低头看左手里的钥匙，随后开始抬眼看向姐姐，不说话。钥匙一直留在弟弟左手，不换手。

原生声音只包含姐姐的这句对白，以及钥匙接触时轻微、同步的金属声。此段不生成房间环境底声、背景音乐、额外对白或对白字幕。保留从接住到松开的连续动作，不用切镜隐藏接触；结尾仍是弟弟持有钥匙的状态。
```

Operator notes stay outside the prompt: intended duration 8 s; actual model/mode, supported duration, reference bindings, assets and voice identity need the user's current evidence before submission. The [local adapter](../../skill/shotloom/modules/generation/references/seedance-25.md) supplies writing guidance with dated sources. This text is a draft, not a tested recipe or permission to generate.

Review targets: correct speaker and exact line; visible right-to-left-hand transfer; receiver grips before release; one stable key; no hand switch; the planned listening pause; accessible native audio versus post-only layers. Expected checks do not establish that any output meets them.

## Returned evidence and iteration

If the user later returns only three frames, report observed visible state but leave transfer motion, reaction timing and sound unverified. Do not label the entire take accepted. If an actually reviewed video shows a wrong-hand transfer, identify the violated lock and choose a bounded repair or changed control/coverage plan; adding an insert that changes the shot design is an upstream coverage revision, not merely a wording reroll.

Example review response for the **hypothetical** three-frame case:

```text
检查范围：仅收到的三张静帧；没有视频播放和实际监听证据。
可见状态：假设首张可见姐姐右手持钥匙，末张可见弟弟左手持钥匙，只能确认这些画面中的状态。
未验证：抓握到松手的连续过程、是否中途消失或换手、弟弟反应时机、逐字对白、声线和声画同步。
处理：整段暂不接受，也不因证据不足直接要求重做。请提供对应版本的实际视频与声音，再定点检查交接区间。
连续性：预期“钥匙在弟弟左手”暂不升级为已接受事实，不更新 B 镜的批准记录。
```

If later actual review instead observes the key switching to the right hand, the repair brief should name that observed interval and preserve the accepted look, line and blocking elsewhere. A corrected prompt alone does not fix the media; review the returned replacement before changing continuity.

After a reviewed correction and explicit version-specific acceptance, record Shot A's observed endpoint. Only then does Shot B inherit it. If Shot A is subsequently replaced with different ownership, mark Shot B stale rather than silently rewriting its approval. In file-backed mode the optional ledger automates this dependency check; in conversation-only mode expose and resolve it manually.

## Edit and handoff

Source acceptance only makes the take eligible. If the selected cut removes the handoff, review whether it remains clearly implied or whether the event is now unresolved. Track source versus selected time, sound ownership, method version and affected state. A transcript is not sound-quality approval and a planned trim is not an accomplished repair.

Return the approved current state, inspected/unverified evidence, intended edit and next task in the conversation. Save the same record only when a project location and write authority are established. The example requires no notebook, installed sibling, account or generation API.

For machine-path behavior, the repository's public-method tests exercise project-authored image/video/audio source locks and all five method gates after relocating the single skill folder.

The [historical golden scene](../golden-scene/README.md) retains early 0.1 teaching records. It is not the current walkthrough or an accepted-media fixture for 0.2.
