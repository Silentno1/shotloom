#!/usr/bin/env python3
"""Legacy 0.1 fixture linter, not current model validation or production approval.

Retained for old examples only. Its fixed envelopes/timeline heuristics must not
override 0.2 operation-specific modules or reject their supported branches.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


MODEL_ALIASES = {
    "seedance-20": "Seedance 2.0",
    "seedance-25": "Seedance 2.5",
    "seedream-50": "Seedream 5.0",
}


def has_any(text: str, terms: tuple[str, ...]) -> bool:
    lowered = text.casefold()
    return any(term.casefold() in lowered for term in terms)


def missing_checks(
    text: str, checks: tuple[tuple[tuple[str, ...], str], ...]
) -> list[str]:
    return [message for terms, message in checks if not has_any(text, terms)]


def parse_duration(text: str) -> float | None:
    patterns = (
        r"(?:总时长|时长)\s*[:：]?\s*(\d+(?:\.\d+)?)\s*秒",
        r"(?:total\s+duration|duration)\s*[:：]?\s*(\d+(?:\.\d+)?)\s*(?:s|sec|seconds?)",
    )
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return float(match.group(1))
    return None


def parse_ranges(text: str) -> list[tuple[float, float]]:
    pattern = (
        r"(?:\[|【)?\s*(\d+(?:\.\d+)?)\s*(?:—|–|-|至|~)\s*"
        r"(\d+(?:\.\d+)?)\s*(?:秒|s|sec|seconds?)"
    )
    return [
        (float(start), float(end))
        for start, end in re.findall(pattern, text, flags=re.IGNORECASE)
    ]


def check_timeline(
    ranges: list[tuple[float, float]], duration: float | None
) -> list[str]:
    errors: list[str] = []
    if len(ranges) < 2:
        return ["时间轴至少需要两个连续时间段 / timeline needs at least two ranges"]
    if abs(ranges[0][0]) > 0.1:
        errors.append("时间轴必须从 0 秒开始 / timeline must start at 0")
    for start, end in ranges:
        if end <= start:
            errors.append("时间段终点必须晚于起点 / each range must end after it starts")
            break
    for previous, current in zip(ranges, ranges[1:]):
        if abs(previous[1] - current[0]) > 0.1:
            errors.append("时间轴存在空档或重叠 / timeline contains a gap or overlap")
            break
    if duration is not None and abs(ranges[-1][1] - duration) > 0.1:
        errors.append("最后一个时间段必须覆盖到总时长 / timeline must cover total duration")
    return errors


def lint_director(text: str, multi_person: bool = False) -> list[str]:
    checks = (
        (("场景功能", "叙事功能", "镜头功能", "scene job", "purpose"), "缺少场景或镜头功能 / missing scene or shot job"),
        (("转折", "变化", "触发", "turn"), "缺少节拍转折或触发 / missing beat turn or trigger"),
        (("进入状态", "开始状态", "起点", "entering state"), "缺少进入状态 / missing entering state"),
        (("结束状态", "结尾状态", "终点", "endpoint", "end state"), "缺少完成终点 / missing completed endpoint"),
        (("调度", "走位", "blocking", "动作链", "action chain"), "缺少调度或动作链 / missing blocking or action chain"),
        (("机位", "摄影机", "camera"), "缺少摄影机位置或方向 / missing camera position or direction"),
        (("背景", "地标", "landmark", "expected background"), "缺少验证机位方向的背景地标 / missing camera-direction landmarks"),
        (("连续性", "承接", "continuity", "must match"), "缺少连续性要求 / missing continuity requirement"),
        (("剪辑桥", "切点", "声音桥", "cut bridge", "edit handle"), "缺少剪辑桥或切点 / missing cut bridge or edit point"),
        (("风险", "备用", "失败", "fallback"), "缺少主要风险或备用方案 / missing primary risk or fallback"),
        (("验收", "检查", "review", "acceptance"), "缺少可观察验收标准 / missing observable acceptance checks"),
    )
    errors = missing_checks(text, checks)
    if multi_person:
        errors.extend(
            missing_checks(
                text,
                (
                    (("轴线", "180", "screen-left", "screen-right", "画面左", "画面右"), "多人镜头缺少轴线和左右关系 / multi-person shot lacks axis and screen positions"),
                    (("视线", "eyeline", "看向", "对视"), "多人镜头缺少视线关系 / multi-person shot lacks eyelines"),
                ),
            )
        )
    return errors


def lint_image(
    text: str, model: str, recurring_subject: bool = False
) -> list[str]:
    errors: list[str] = []
    if model != "seedream-50":
        errors.append("当前图片适配器应选择 seedream-50 / current image adapter is seedream-50")
    checks = (
        (("制作任务", "图片用途", "首帧", "image job", "production job"), "缺少图片制作任务 / missing image production job"),
        (("机位", "摄影机", "视角", "camera", "viewpoint"), "缺少机位或视角 / missing camera or viewpoint"),
        (("构图", "景别", "framing", "composition"), "缺少构图或景别 / missing composition or framing"),
        (("背景", "环境", "地标", "background", "landmark", "environment"), "缺少环境或背景地标 / missing environment or landmarks"),
        (("光", "照明", "lighting", "exposure"), "缺少光线说明 / missing lighting"),
        (("禁止", "不得", "不要", "preserve", "must not", "no extra"), "缺少保留项或排除项 / missing preservation or exclusions"),
        (("验收", "检查", "review", "acceptance"), "缺少验收标准 / missing acceptance checks"),
    )
    errors.extend(missing_checks(text, checks))
    if recurring_subject and not has_any(
        text, ("身份", "角色参考", "subject identity", "identity reference", "passport")
    ):
        errors.append("持续角色缺少身份或护照约束 / recurring subject lacks identity or passport lock")
    return errors


def lint_video(
    text: str,
    model: str,
    exact_dialogue: bool,
    clothing_text: bool,
    dialogue: bool = False,
    audio_ref: bool = False,
    recurring_subject: bool = False,
) -> list[str]:
    errors: list[str] = []
    if model == "seedream-50":
        errors.append("Seedream 5.0 是图片适配器，不用于视频 / Seedream 5.0 is an image adapter")

    duration = parse_duration(text)
    if duration is None:
        errors.append("缺少明确总时长 / missing total duration")
    elif model == "seedance-20" and not 0 < duration <= 15:
        errors.append("Seedance 2.0 当前模型档案按不超过 15 秒检查 / Seedance 2.0 profile checks a 15s ceiling")
    elif model == "seedance-25" and not 4 <= duration <= 30:
        errors.append("Seedance 2.5 标准生成应在 4-30 秒 / Seedance 2.5 standard generation is 4-30s")

    ranges = parse_ranges(text)
    if ranges:
        errors.extend(check_timeline(ranges, duration))
    elif model == "seedance-25" and duration is not None and duration >= 12:
        errors.append("较长 Seedance 2.5 视频缺少连续时间段 / longer Seedance 2.5 prompt needs continuous ranges")

    checks = (
        (("进入状态", "开始状态", "起点", "entering state"), "缺少进入状态 / missing entering state"),
        (("动作", "触发", "action", "trigger"), "缺少可见动作或触发 / missing visible action or trigger"),
        (("机位", "摄影机", "camera"), "缺少摄影机说明 / missing camera direction"),
        (("结尾状态", "结束状态", "终点", "endpoint", "end state"), "缺少完成终点 / missing completed endpoint"),
        (("环境声", "对白", "音效", "音乐", "无声", "ambience", "dialogue", "sound", "silence"), "缺少声音决定 / missing sound decision"),
        (("禁止", "不得", "不要", "preserve", "must not", "no extra"), "缺少保留项或排除项 / missing preservation or exclusions"),
        (("验收", "检查", "review", "acceptance"), "缺少验收标准 / missing acceptance checks"),
    )
    errors.extend(missing_checks(text, checks))

    if dialogue:
        errors.extend(
            missing_checks(
                text,
                (
                    (("台词", "说：", "说道", "dialogue", "line:"), "对白镜头缺少明确台词 / dialogue shot lacks an explicit line"),
                    (("语速", "重音", "音高", "句尾", "pace", "stress", "pitch", "ending"), "对白镜头缺少可执行的声音方向 / dialogue shot lacks executable vocal direction"),
                    (("不要字幕", "无字幕", "禁止字幕", "字幕后期", "no subtitles"), "对白镜头缺少字幕决定 / dialogue shot lacks a subtitle decision"),
                    (("面对", "听者", "listener", "speaking to"), "对白镜头缺少听者 / dialogue shot lacks a listener"),
                ),
            )
        )
    if audio_ref and not re.search(r"@(?:音频|audio)\s*\d+", text, flags=re.IGNORECASE):
        errors.append("存在声音参考但未绑定实际令牌 / audio reference is not bound to an actual token")
    if recurring_subject and not has_any(
        text, ("身份", "角色参考", "subject identity", "identity reference", "passport")
    ):
        errors.append("持续角色缺少身份约束 / recurring subject lacks identity lock")
    if exact_dialogue and not (
        has_any(text, ("逐字一致", "不得改写", "verbatim", "exact wording"))
        and has_any(text, ("不得增字", "不得漏字", "no added words", "no omitted words"))
    ):
        errors.append("关键台词缺少逐字约束 / exact dialogue lacks verbatim constraints")
    if clothing_text and not (
        has_any(text, ("镜像", "方向", "mirrored", "reading direction"))
        and has_any(text, ("变形", "乱码", "字形", "logo", "print", "deform"))
    ):
        errors.append("服装文字或标志缺少方向和防变形约束 / wardrobe text lacks direction and deformation locks")
    return errors


def lint_audio(text: str) -> list[str]:
    checks = (
        (("台词", "说：", "对白", "line", "dialogue"), "声音合同缺少实际台词 / audio contract lacks an actual line"),
        (("听者", "面对", "说给", "listener", "speaking to"), "声音合同缺少听者或交流关系 / audio contract lacks a listener or relationship"),
        (("目的", "意图", "想要", "objective", "tactic"), "声音合同缺少交流目的 / audio contract lacks a conversational objective"),
        (("音量", "响度", "loudness", "volume"), "声音合同缺少音量方向 / audio contract lacks loudness direction"),
        (("音色", "张力", "timbre", "tension"), "声音合同缺少音色或张力 / audio contract lacks timbre or tension"),
        (("语速", "节奏", "pace", "rate"), "声音合同缺少语速 / audio contract lacks speech rate"),
        (("停顿", "pause"), "声音合同缺少停顿设计 / audio contract lacks pause design"),
        (("音高", "句尾", "pitch", "ending"), "声音合同缺少音高或句尾 / audio contract lacks pitch or phrase ending"),
        (("不要", "避免", "禁止", "must not", "avoid"), "声音合同缺少排除风格 / audio contract lacks excluded styles"),
    )
    return missing_checks(text, checks)


def lint_state(text: str) -> list[str]:
    checks = (
        (("Project ID", "项目 ID", "项目ID"), "缺少项目 ID / missing project ID"),
        (("State mode", "状态模式", "file-backed", "conversation-only"), "缺少状态模式 / missing state mode"),
        (("status", "状态"), "缺少生产状态 / missing production status"),
        (("scene", "场景", "shot", "镜头"), "缺少当前场景或镜头 / missing current scene or shot"),
        (("accepted continuity endpoint", "已接受连续性终点", "accepted endpoint"), "缺少已接受连续性终点 / missing accepted continuity endpoint"),
        (("blocker", "冲突", "阻断"), "缺少阻断项或权威冲突字段 / missing blockers or authority conflicts"),
        (("Next task", "下一任务", "下一步任务"), "缺少唯一下一任务 / missing one next task"),
        (("Last updated from", "更新依据", "evidence source"), "缺少状态更新依据 / missing state update authority"),
    )
    return missing_checks(text, checks)


def lint_review(text: str) -> list[str]:
    checks = (
        (("Review ID", "审核 ID", "审核ID"), "缺少审核 ID / missing review ID"),
        (("take ID", "Take ID", "take:"), "缺少 Take ID / missing take ID"),
        (("Evidence", "证据"), "缺少证据来源 / missing evidence source"),
        (("Observed", "观察", "实测", "reported"), "缺少观察或测量结果 / missing observed or measured result"),
        (("Unknown", "未知"), "缺少未知检查字段 / missing unknown checks"),
        (("Blockers", "阻断项", "阻断"), "缺少阻断项字段 / missing blockers field"),
        (("Decision", "决定", "结论"), "缺少唯一审核决定 / missing review decision"),
        (("Diagnosed cause", "诊断原因", "原因"), "缺少诊断原因 / missing diagnosed cause"),
        (("Accepted observed endpoint", "接受的观察终点", "已接受终点"), "缺少接受终点字段 / missing accepted endpoint field"),
        (("Continuity", "连续性"), "缺少连续性更新字段 / missing continuity update field"),
        (("Next task", "下一任务", "下一步任务"), "缺少下一任务 / missing next task"),
    )
    return missing_checks(text, checks)


def lint_handoff(text: str) -> list[str]:
    checks = (
        (("Handoff ID", "交接 ID", "交接ID"), "缺少交接 ID / missing handoff ID"),
        (("Source file", "源文件"), "缺少源文件 / missing source file"),
        (("usable range", "可用范围", "in point", "out point"), "缺少可用范围 / missing usable range"),
        (("head", "tail", "头尾", "余量"), "缺少头尾余量 / missing head and tail handles"),
        (("endpoint", "终点", "结尾状态"), "缺少观察终点 / missing observed endpoint"),
        (("Cut bridge", "剪辑桥", "声音桥"), "缺少剪辑桥 / missing cut bridge"),
        (("dialogue", "对白", "audio", "声音"), "缺少声音依赖 / missing audio dependencies"),
        (("repairable", "可修复"), "缺少可修复问题字段 / missing repairable issues field"),
        (("must not be deferred", "不可延期", "阻断"), "缺少不可延期问题字段 / missing non-deferrable issues"),
        (("Continuity", "连续性"), "缺少传递给下一镜的连续性 / missing downstream continuity"),
        (("Next", "下一"), "缺少下一生产或后期任务 / missing next production or post task"),
    )
    return missing_checks(text, checks)


def reference_mapping_warning(text: str) -> list[str]:
    tokens = re.findall(r"@[\w\u4e00-\u9fff]+\s*\d+", text)
    if tokens and not has_any(
        text,
        ("参考职责", "素材职责", "只负责", "只控制", "controls", "reference map", "must not transfer"),
    ):
        return ["出现参考令牌但未说明职责 / reference tokens appear without a role map"]
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=tuple(MODEL_ALIASES))
    parser.add_argument(
        "--kind",
        choices=("director", "image", "video", "audio", "state", "review", "handoff"),
        required=True,
    )
    parser.add_argument("--dialogue", action="store_true")
    parser.add_argument("--audio-ref", action="store_true")
    parser.add_argument("--recurring-subject", "--main-character", action="store_true", dest="recurring_subject")
    parser.add_argument("--multi-person", action="store_true")
    parser.add_argument("--exact-dialogue", action="store_true")
    parser.add_argument("--clothing-text", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("path", nargs="?", type=Path)
    args = parser.parse_args()

    if args.kind in {"image", "video"} and args.model is None:
        parser.error(f"--model is required for --kind {args.kind}")

    text = args.path.read_text(encoding="utf-8") if args.path else sys.stdin.read()
    if args.kind == "director":
        errors = lint_director(text, args.multi_person)
    elif args.kind == "image":
        errors = lint_image(text, args.model or "", args.recurring_subject)
    elif args.kind == "video":
        errors = lint_video(
            text,
            args.model or "",
            args.exact_dialogue,
            args.clothing_text,
            args.dialogue,
            args.audio_ref,
            args.recurring_subject,
        )
    elif args.kind == "audio":
        errors = lint_audio(text)
    elif args.kind == "state":
        errors = lint_state(text)
    elif args.kind == "review":
        errors = lint_review(text)
    else:
        errors = lint_handoff(text)

    errors.extend(reference_mapping_warning(text))
    errors = list(dict.fromkeys(errors))
    payload = {
        "scope": "legacy_alpha_fixture_only; use current module checks for production",
        "status": "PASS" if not errors else "FAIL",
        "model": MODEL_ALIASES.get(args.model or "", "model-neutral"),
        "kind": args.kind,
        "errors": errors,
    }
    if args.as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(payload["scope"])
        print(payload["status"])
        for error in errors:
            print(f"- {error}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
