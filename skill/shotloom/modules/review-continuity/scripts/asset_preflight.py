#!/usr/bin/env python3
"""Inventory project media and surface reference-coverage gaps.

This helper discovers candidates only. It never promotes a file to canon without
handoff evidence and human visual/audio inspection.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


MEDIA_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".heic",
    ".tif",
    ".tiff",
    ".mp4",
    ".mov",
    ".m4v",
    ".webm",
    ".avi",
    ".mp3",
    ".wav",
    ".m4a",
    ".aac",
    ".ogg",
    ".flac",
}

REJECT_MARKERS = (
    "废稿",
    "废片",
    "未采用",
    "不采用",
    "错误",
    "作废",
    "obsolete",
    "rejected",
    "reject",
    "draft",
    "discard",
)

HANDOFF_REJECT_HINTS = (
    "移至废稿",
    "放入废稿",
    "未采用",
    "不采用",
    "已作废",
    "已否定",
    "不得作为",
    "从当前剪辑中删除",
    "用户已明确把",
    "handoff-rejected",
    "rejected",
)

ROLE_RULES: dict[str, tuple[str, ...]] = {
    "frame": ("首帧", "尾帧", "关键帧", "起始帧", "结束帧", "firstframe", "lastframe"),
    "identity": ("人物", "角色", "形象", "数字演员", "角色卡", "标准脸", "正脸", "脸部", "面部", "头像", "三视图", "45度", "四十五度", "侧面", "identity", "character"),
    "body": ("全身", "身材", "体型", "身体比例", "正背面", "body", "proportion"),
    "wardrobe": ("服装", "衣服", "穿搭", "造型", "外衬", "衬衫", "鞋履", "鞋靴", "配饰", "发饰", "腰带", "标志", "logo", "wardrobe", "costume", "outfit"),
    "expression": ("表情", "情绪", "疲惫", "伤痕", "泪痕", "哭泣", "expression", "emotion"),
    "location": ("场景", "固定场景", "环境", "户型", "白模", "全景", "空间", "location", "environment", "room", "set"),
    "prop": ("道具", "手机", "合同", "屏幕", "界面", "计算器", "容器", "工具", "食材", "材料", "prop", "phone", "screen", "ui"),
    "voice": ("声音参考", "声线", "人声", "对白", "配音", "voice", "dialogue", "speech"),
    "motion": ("动作参考", "表演参考", "运动参考", "走位参考", "motion", "movement", "gesture", "blocking"),
    "endpoint": ("目标尾帧", "尾帧", "结束帧", "终点", "结尾状态", "endpoint", "endstate"),
    "music": ("音乐", "配乐", "bgm", "music", "score"),
    "take": ("片段", "成片", "视频", "镜头", "take", "clip", "shot"),
}

ACCEPT_HINTS = ("正式", "通过", "确认", "锁定", "采用", "accepted", "approved", "canonical")
FORMAL_DIR_HINTS = ("人物", "固定场景", "声音参考", "道具", "正式", "首帧图", "封面")


@dataclass
class Asset:
    path: str
    media_type: str
    roles: list[str]
    approval_hint: str
    query_score: int


def normalize(value: str) -> str:
    return re.sub(r"[\s_\-—–·.（）()【】\[\]/\\]+", "", value).casefold()


def media_type(path: Path) -> str:
    ext = path.suffix.casefold()
    if ext in {".png", ".jpg", ".jpeg", ".webp", ".heic", ".tif", ".tiff"}:
        return "image"
    if ext in {".mp4", ".mov", ".m4v", ".webm", ".avi"}:
        return "video"
    return "audio"


def classify_roles(path_text: str, kind: str) -> list[str]:
    normalized = normalize(path_text)
    roles = [role for role, words in ROLE_RULES.items() if any(normalize(word) in normalized for word in words)]
    if kind == "audio" and not any(role in roles for role in ("voice", "music")):
        roles.append("audio")
    if kind == "video" and "take" not in roles:
        roles.append("video")
    if kind == "image" and not roles:
        roles.append("image")
    return sorted(set(roles))


def load_handoff_text(root: Path) -> str:
    chunks: list[str] = []
    for path in root.rglob("*.md"):
        if "交接" not in path.name and "handoff" not in path.name.casefold():
            continue
        try:
            chunks.append(path.read_text(encoding="utf-8", errors="ignore"))
        except OSError:
            continue
    return "\n".join(chunks)


def handoff_hint(relative_path: str, handoff: str) -> str | None:
    if not handoff:
        return None
    needles = (relative_path, Path(relative_path).name)
    best: str | None = None
    for needle in needles:
        start = 0
        while True:
            index = handoff.find(needle, start)
            if index < 0:
                break
            window_start = max(0, index - 100)
            window_end = min(len(handoff), index + len(needle) + 140)
            window = handoff[window_start:window_end].casefold()
            relative_index = index - window_start

            def nearest(markers: tuple[str, ...]) -> int | None:
                distances = []
                for marker in markers:
                    marker_key = marker.casefold()
                    offset = window.find(marker_key)
                    while offset >= 0:
                        distances.append(abs(offset - relative_index))
                        offset = window.find(marker_key, offset + len(marker_key))
                return min(distances) if distances else None

            reject_distance = nearest(HANDOFF_REJECT_HINTS)
            accept_distance = nearest(ACCEPT_HINTS)
            if reject_distance is not None and (accept_distance is None or reject_distance < accept_distance):
                return "handoff-rejected"
            if accept_distance is not None:
                best = "handoff-accepted"
            start = index + len(needle)
    return best


def approval_hint(relative_path: str, handoff: str) -> str:
    normalized = normalize(relative_path)
    if any(normalize(marker) in normalized for marker in REJECT_MARKERS):
        return "path-rejected"
    from_handoff = handoff_hint(relative_path, handoff)
    if from_handoff:
        return from_handoff
    if any(normalize(marker) in normalized for marker in ACCEPT_HINTS):
        return "name-accepted-hint"
    if any(normalize(marker) in normalized for marker in FORMAL_DIR_HINTS):
        return "formal-directory-hint"
    return "unverified"


def query_terms(query: str, extra_terms: list[str]) -> list[str]:
    raw = [query, *extra_terms]
    terms: list[str] = []
    for item in raw:
        for part in re.split(r"[\s,，;；:：|/\\]+", item):
            token = normalize(part)
            if len(token) >= 2:
                terms.append(token)
    return sorted(set(terms))


def context_score(relative_path: str, handoff: str, terms: list[str]) -> int:
    if not handoff or not terms:
        return 0
    score = 0
    for needle in (relative_path, Path(relative_path).name):
        start = 0
        while True:
            index = handoff.find(needle, start)
            if index < 0:
                break
            line_start = handoff.rfind("\n", 0, index) + 1
            line_end = handoff.find("\n", index)
            if line_end < 0:
                line_end = len(handoff)
            window = normalize(handoff[line_start:line_end])
            score = max(score, sum(6 for term in terms if term in window))
            start = index + len(needle)
    return score


def score_path(relative_path: str, handoff: str, terms: list[str], approval: str) -> int:
    normalized = normalize(relative_path)
    score = sum(10 for term in terms if term in normalized)
    score += context_score(relative_path, handoff, terms)
    if approval == "handoff-accepted":
        score += 3
    elif approval in {"name-accepted-hint", "formal-directory-hint"}:
        score += 1
    elif "rejected" in approval:
        score -= 50
    return score


def scan(root: Path, terms: list[str], include_rejected: bool) -> list[Asset]:
    handoff = load_handoff_text(root)
    assets: list[Asset] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.casefold() not in MEDIA_EXTENSIONS:
            continue
        relative = path.relative_to(root).as_posix()
        approval = approval_hint(relative, handoff)
        if not include_rejected and "rejected" in approval:
            continue
        kind = media_type(path)
        assets.append(
            Asset(
                path=relative,
                media_type=kind,
                roles=classify_roles(relative, kind),
                approval_hint=approval,
                query_score=score_path(relative, handoff, terms, approval),
            )
        )
    return sorted(assets, key=lambda item: (-item.query_score, item.path.casefold()))


def parse_need(raw: str) -> tuple[str, str]:
    if ":" not in raw:
        return raw.strip().casefold(), ""
    role, subject = raw.split(":", 1)
    return role.strip().casefold(), subject.strip()


def need_candidates(assets: list[Asset], role: str, subject: str) -> tuple[list[Asset], bool]:
    subject_key = normalize(subject)
    role_matches = [asset for asset in assets if role in asset.roles]
    matches = role_matches
    if subject_key:
        matches = [asset for asset in matches if subject_key in normalize(asset.path)]
    if matches:
        return matches, False
    contextual = [asset for asset in role_matches if asset.query_score > 8]
    if contextual:
        return contextual, True
    fallback_kind = {
        "frame": "image",
        "identity": "image",
        "body": "image",
        "wardrobe": "image",
        "expression": "image",
        "location": "image",
        "prop": "image",
        "voice": "audio",
        "motion": "video",
        "endpoint": "image",
    }.get(role)
    if fallback_kind:
        fallback = [asset for asset in assets if asset.media_type == fallback_kind]
        if role in {"identity", "body", "wardrobe", "expression"}:
            fallback = [
                asset
                for asset in fallback
                if any(candidate in asset.roles for candidate in ("identity", "body", "wardrobe", "expression", "frame"))
            ]
        elif role == "location":
            fallback = [asset for asset in fallback if "location" in asset.roles]
        elif role == "prop":
            fallback = [asset for asset in fallback if "prop" in asset.roles or "frame" in asset.roles]
        if subject_key:
            fallback = [asset for asset in fallback if subject_key in normalize(asset.path)]
        if fallback:
            return fallback, True
    return [], False


def coverage_status(matches: list[Asset], fallback: bool) -> str:
    if not matches:
        return "missing"
    if fallback:
        return "fallback-requires-inspection"
    return "candidate-requires-inspection"


def markdown_report(root: Path, assets: list[Asset], needs: list[tuple[str, str]], limit: int) -> str:
    lines = [
        f"# Asset preflight: {root}",
        "",
        "Discovery is not approval or inspection. Open every selected file before assigning its role.",
        "",
    ]
    if needs:
        lines.extend(("## Coverage", "", "| Need | Status | Best candidates |", "|---|---|---|"))
        for role, subject in needs:
            matches, fallback = need_candidates(assets, role, subject)
            label = f"{role}:{subject}" if subject else role
            if matches:
                choices = "<br>".join(f"`{asset.path}` ({asset.approval_hint})" for asset in matches[:3])
                status = (
                    "**MISSING exact match**; fallback candidates require inspection"
                    if fallback
                    else "candidate found; inspect before use"
                )
                lines.append(f"| {label} | {status} | {choices} |")
            else:
                lines.append(f"| {label} | **MISSING** | no filename/path match |")
        lines.append("")
    else:
        lines.extend(("**INCOMPLETE PREFLIGHT:** no `--need` coverage requirements were declared; this is inventory only.", ""))
    lines.extend(("## Ranked candidates", "", "| Score | Type | Roles | Approval hint | Path |", "|---:|---|---|---|---|"))
    shown = [asset for asset in assets if asset.query_score > 0][:limit]
    if not shown:
        shown = assets[:limit]
    for asset in shown:
        roles = ", ".join(asset.roles)
        lines.append(f"| {asset.query_score} | {asset.media_type} | {roles} | {asset.approval_hint} | `{asset.path}` |")
    lines.extend(("", f"Scanned {len(assets)} non-rejected media files; showing {len(shown)}."))
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root")
    parser.add_argument("--query", default="", help="shot id, character, location, and prop terms")
    parser.add_argument("--term", action="append", default=[], help="extra relevance term; repeatable")
    parser.add_argument("--need", action="append", default=[], help="coverage requirement such as voice:角色A")
    parser.add_argument("--limit", type=int, default=40)
    parser.add_argument("--include-rejected", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = Path(args.project_root).expanduser().resolve()
    if not root.is_dir():
        print(f"Project root is not a directory: {root}", file=sys.stderr)
        return 2
    terms = query_terms(args.query, args.term)
    needs = [parse_need(item) for item in args.need]
    assets = scan(root, terms, args.include_rejected)
    if args.json:
        payload = {
            "project_root": str(root),
            "needs": [],
            "assets": [asdict(asset) for asset in assets[: args.limit]],
        }
        for role, subject in needs:
            candidates, fallback = need_candidates(assets, role, subject)
            payload["needs"].append({
                "role": role,
                "subject": subject,
                "status": coverage_status(candidates, fallback),
                "is_fallback": fallback,
                "candidates": [asdict(asset) for asset in candidates[:5]],
            })
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(markdown_report(root, assets, needs, args.limit))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
