#!/usr/bin/env python3
"""Extract technical evidence and review images from a video or audio take."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import math
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'director/scripts'))
from drama_contracts import decimal_seconds
from runtime_tools import find_binary


def run(command: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=check)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def probe(ffprobe: str, source: Path) -> dict[str, Any]:
    result = run([
        ffprobe, "-v", "error", "-show_format", "-show_streams", "-of", "json", str(source)
    ])
    return json.loads(result.stdout)


def parse_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def metadata(probe_data: dict[str, Any]) -> dict[str, Any]:
    streams = probe_data.get("streams", [])
    video = next((stream for stream in streams if stream.get("codec_type") == "video"), None)
    audio = next((stream for stream in streams if stream.get("codec_type") == "audio"), None)
    fmt = probe_data.get("format", {})
    result: dict[str, Any] = {
        "duration_seconds": parse_float(fmt.get("duration")),
        "format": fmt.get("format_name"),
        "bit_rate": parse_float(fmt.get("bit_rate")),
        "video": None,
        "audio": None,
    }
    if video:
        frame_rate = video.get("avg_frame_rate") or video.get("r_frame_rate")
        fps = None
        if frame_rate and "/" in frame_rate:
            numerator, denominator = frame_rate.split("/", 1)
            if float(denominator):
                fps = float(numerator) / float(denominator)
        result["video"] = {
            "codec": video.get("codec_name"),
            "width": video.get("width"),
            "height": video.get("height"),
            "fps": fps,
            "pixel_format": video.get("pix_fmt"),
            "duration_seconds": parse_float(video.get("duration")),
        }
    if audio:
        result["audio"] = {
            "codec": audio.get("codec_name"),
            "sample_rate": parse_float(audio.get("sample_rate")),
            "channels": audio.get("channels"),
            "channel_layout": audio.get("channel_layout"),
            "duration_seconds": parse_float(audio.get("duration")),
        }
    return result


def video_timing(data: dict[str, Any]) -> dict[str, Any]:
    """Bound the video clock, not a container clock that may include longer audio."""
    frames = data.get("frames", [])
    times = [decimal_seconds(frame.get("best_effort_timestamp_time")) for frame in frames]
    if not times or times != sorted(set(times)):
        raise ValueError("cannot establish ordered decoded video frame timestamps")
    stream = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), {})
    origin, last = times[0], times[-1]

    def positive(value: Any):
        try:
            number = decimal_seconds(value)
            return number if number > 0 else None
        except ValueError:
            return None

    def rational(value: Any):
        try:
            number = Fraction(str(value))
            return positive(decimal_seconds(number.numerator) / decimal_seconds(number.denominator))
        except (ValueError, ZeroDivisionError):
            return None

    # New FFprobe versions expose duration_time; older ones use pkt_duration_time.
    tail = positive(frames[-1].get("duration_time")) or positive(frames[-1].get("pkt_duration_time"))
    end, basis = None, "unknown"
    if tail is not None:
        end, basis = last + tail - origin, "last_decoded_frame_duration"
    else:
        stream_duration = positive(stream.get("duration"))
        if stream_duration is not None:
            try:
                stream_start = decimal_seconds(stream.get("start_time", origin))
            except ValueError:
                stream_start = origin
            if stream_start + stream_duration > last:
                end, basis = stream_start + stream_duration - origin, "video_stream_duration"
        # A missing last-frame duration cannot be recovered from average FPS on
        # VFR material. Only estimate a CFR tail when the declared rates agree
        # and every decoded timestamp matches that grid within one stream tick.
        rate = rational(stream.get("r_frame_rate"))
        average = rational(stream.get("avg_frame_rate"))
        tick = rational(stream.get("time_base")) or decimal_seconds("0.000001")
        if end is None and len(times) > 1 and rate and average == rate:
            period = decimal_seconds(1) / rate
            if tick < period and all(abs(t - origin - i * period) <= tick for i, t in enumerate(times)):
                end, basis = len(times) * period, "cfr_timestamp_grid_estimate"
    return {
        "time_origin": "first decoded video frame",
        "stream_origin_seconds": float(origin),
        "last_frame_start_seconds": float(last - origin),
        "end_seconds": float(end) if end is not None else None,
        "end_basis": basis,
        "end_is_estimate": basis == "cfr_timestamp_grid_estimate",
        "decoded_frame_count": len(times),
    }


def probe_video_timing(ffprobe: str, source: Path) -> dict[str, Any]:
    result = run([ffprobe, "-v", "error", "-select_streams", "v:0", "-show_frames", "-show_streams",
                  "-show_entries", "frame=best_effort_timestamp_time,duration_time,pkt_duration_time:"
                  "stream=codec_type,start_time,duration,r_frame_rate,avg_frame_rate,time_base",
                  "-of", "json", str(source)])
    return video_timing(json.loads(result.stdout))


def validate_video_outpoint(value: float, timing: dict[str, Any]) -> None:
    outpoint = decimal_seconds(value)
    if outpoint <= 0:
        raise ValueError("video outpoint must be positive finite seconds")
    end = timing["end_seconds"]
    if end is None:
        if outpoint > decimal_seconds(timing["last_frame_start_seconds"]):
            raise ValueError("video tail duration is unknown; cannot verify this outpoint")
    elif outpoint > decimal_seconds(end) + decimal_seconds("0.000001"):
        raise ValueError(f"outpoint {value:g} exceeds decoded video duration {end:g}")


def extract_frame(ffmpeg: str, source: Path, target: Path, timestamp: float) -> None:
    run([ffmpeg, "-hide_banner", "-loglevel", "error", "-ss", f"{max(timestamp, 0):.3f}", "-i", str(source), "-frames:v", "1", "-y", str(target)])


def extract_last_frame(ffmpeg: str, ffprobe: str, source: Path, target: Path,
                       before: float | None = None) -> dict[str, Any]:
    """Extract the actual last decoded video frame, optionally before an exclusive outpoint."""
    if before is not None and (not math.isfinite(before) or before <= 0):
        raise ValueError("selected outpoint must be positive finite seconds")
    frames = json.loads(run([ffprobe, "-v", "error", "-select_streams", "v:0", "-show_frames",
                            "-show_entries", "frame=best_effort_timestamp_time", "-of", "json", str(source)]).stdout).get("frames", [])
    times = [decimal_seconds(frame.get("best_effort_timestamp_time")) for frame in frames]
    if not times:
        raise ValueError("cannot establish decoded video frame timestamps")
    origin = times[0]
    normalized = [t - origin for t in times]
    if normalized != sorted(normalized):
        raise ValueError("decoded presentation timestamps are not ordered")
    candidates = [i for i, t in enumerate(normalized) if before is None or t < decimal_seconds(before)]
    if not candidates:
        raise ValueError("no decoded frame before selected outpoint")
    index = candidates[-1]
    run([ffmpeg, "-hide_banner", "-loglevel", "error", "-i", str(source), "-map", "0:v:0",
         "-vf", f"select='eq(n,{index})'", "-fps_mode", "vfr", "-frames:v", "1", "-y", str(target)])
    if not target.is_file():
        raise ValueError("boundary frame was not produced")
    return {"path": str(target), "decoded_frame_index": index, "source_timestamp_seconds": float(normalized[index]),
            "stream_timestamp_seconds": float(times[index]), "exclusive_outpoint_seconds": before,
            "time_origin": "first decoded video frame", "method": "decoded-frame-index", "resolution": "native"}


def contact_sheet(ffmpeg: str, source: Path, target: Path, duration: float, samples: int) -> dict[str, Any]:
    if not math.isfinite(duration) or duration <= 0 or samples < 1:
        raise ValueError("contact sheet needs positive finite duration and sample count")
    columns = 4
    rows = (samples + columns - 1) // columns
    interval = max(duration / max(samples, 1), 0.04)
    # Select existing frames without fps resampling: fps rewrites timestamps and
    # may label a future source frame with an earlier grid time.
    vf = (
        "setpts=PTS-STARTPTS,"
        f"select='lt(selected_n,{samples})*gte(t,selected_n*{interval:.9f})',"
        "scale=480:270:force_original_aspect_ratio=decrease,"
        "pad=480:270:(ow-iw)/2:(oh-ih)/2:color=black,"
        "showinfo,"
        f"drawtext=text='%{{pts\\:hms}}':x=12:y=h-th-10:fontsize=22:fontcolor=white:box=1:boxcolor=black@0.55,"
        f"tile={columns}x{rows}:padding=4:margin=4"
    )
    result = run([ffmpeg, "-hide_banner", "-loglevel", "info", "-i", str(source), "-vf", vf, "-frames:v", "1", "-y", str(target)])
    timestamps = [float(value) for value in re.findall(r"\bn:\s*\d+\s+pts:\s*-?\d+\s+pts_time:([-+0-9.eE]+)", result.stderr)]
    if not timestamps or len(timestamps) > samples:
        raise ValueError("could not establish contact-sheet source timestamps")
    return {
        "method": "source-frame-select-v2",
        "time_origin": "first decoded video frame; seconds on source video timeline",
        "requested_samples": samples,
        "actual_samples": len(timestamps),
        "source_timestamps_seconds": timestamps,
        "label_precision_seconds": 0.001,
        "purpose": "overview only; verify exact cut boundaries in source frames",
    }


def parse_dense_range(value: str) -> tuple[float, float]:
    try:
        start_text, end_text = value.split(":", 1)
        start, end = float(start_text), float(end_text)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"invalid dense range {value!r}; use START:END seconds") from exc
    if not math.isfinite(start) or not math.isfinite(end) or start < 0 or end <= start:
        raise ValueError(f"invalid dense range {value!r}; END must be greater than non-negative START")
    return start, end


def dense_frame_burst(
    ffmpeg: str,
    source: Path,
    out_dir: Path,
    start: float,
    end: float,
    fps: float,
    max_frames: int,
    resolution: str = "overview",
) -> dict[str, Any]:
    if not all(type(v) in (int, float) and math.isfinite(v) for v in (start, end, fps)) or not 0 <= start < end or fps <= 0:
        raise ValueError("dense extraction needs finite 0 <= start < end and positive fps")
    if type(max_frames) is not int or max_frames < 1:
        raise ValueError("max_frames must be a positive integer")
    if resolution not in ("overview", "native"):
        raise ValueError("resolution must be overview or native")
    expected = math.ceil((end - start) * fps)
    if expected > max_frames:
        raise ValueError(
            f"dense range {start:.3f}:{end:.3f} at {fps:g} fps requests about {expected} frames; "
            f"maximum is {max_frames}"
        )
    source_hash = sha256(source)
    out_dir.mkdir(parents=True, exist_ok=True)
    burst_dir = Path(tempfile.mkdtemp(prefix=f"dense-{source_hash[:12]}-{start:.3f}-{end:.3f}-", dir=out_dir))
    pattern = burst_dir / "frame-%04d.png"
    # Select existing source frames, never create a synthetic fps grid. Normalize
    # to the same first-decoded-video-frame origin used by overview sheets.
    vf = ("setpts=PTS-STARTPTS,"
          f"select='gte(t,{start:.9f})*lt(t,{end:.9f})*lt(selected_n,{expected})*"
          f"if(isnan(prev_selected_t),1,gt(floor((t-{start:.9f})*{fps:.9f}+0.5),floor((prev_selected_t-{start:.9f})*{fps:.9f}+0.5)))',"
          + ("scale=480:270:force_original_aspect_ratio=decrease,"
             "pad=480:270:(ow-iw)/2:(oh-ih)/2:color=black," if resolution == "overview" else "")
          + "showinfo")
    result = run([ffmpeg, "-hide_banner", "-loglevel", "info", "-i", str(source),
                  "-vf", vf, "-fps_mode", "vfr", "-y", str(pattern)])
    timestamps = [float(v) for v in re.findall(r"\bn:\s*\d+\s+pts:\s*-?\d+\s+pts_time:([-+0-9.eE]+)", result.stderr)]
    frames = [burst_dir / f"frame-{i:04d}.png" for i in range(1, len(timestamps) + 1)]
    if not frames or len(frames) > max_frames or not all(p.is_file() for p in frames) or sha256(source) != source_hash:
        raise ValueError("dense extraction could not bind produced files to source timestamps")
    if timestamps != sorted(set(timestamps)) or any(not start - 1e-6 <= t < end for t in timestamps):
        raise ValueError("dense source timestamps are inconsistent")
    columns = min(8, len(frames))
    rows = math.ceil(len(frames) / columns)
    sheet = burst_dir / "dense-contact-sheet.jpg"
    run([
        ffmpeg, "-hide_banner", "-loglevel", "error", "-framerate", "1", "-pattern_type", "glob",
        "-i", str(burst_dir / "frame-*.png"), "-vf",
        f"scale=480:270:force_original_aspect_ratio=decrease,pad=480:270:(ow-iw)/2:(oh-ih)/2:color=black,tile={columns}x{rows}:padding=4:margin=4",
        "-frames:v", "1", "-y", str(sheet)
    ])
    return {
        "start": start,
        "end": end,
        "requested_fps": fps,
        "frame_count": len(frames),
        "frames": [str(path) for path in frames],
        "contact_sheet": str(sheet),
        "source_sha256": source_hash,
        "frame_resolution": resolution,
        "contact_sheet_purpose": "overview only; inspect individual native frames for fine detail",
        "method": "source-frame-select-dense-v1",
        "time_origin": "first decoded video frame; seconds on source video timeline",
        "source_timestamps_seconds": timestamps,
        "sampling": "source-time buckets at requested_fps with bounded count; approximate spacing, no interpolation or duplication",
    }


def detector_log(ffmpeg: str, source: Path, filter_graph: str, audio: bool = False) -> dict[str, Any]:
    options = ["-vn", "-af", filter_graph] if audio else ["-vf", filter_graph, "-an"]
    try:
        completed = run([ffmpeg, "-hide_banner", "-nostats", "-i", str(source),
                         *options, "-f", "null", "-"], check=False)
        return {"status": "completed" if completed.returncode == 0 else "failed",
                "returncode": completed.returncode, "stderr": completed.stderr,
                "error": None if completed.returncode == 0 else completed.stderr[-2000:]}
    except OSError as exc:
        return {"status": "failed", "returncode": None, "stderr": "", "error": str(exc)}


def all_source_frame_burst(ffmpeg: str, ffprobe: str, source: Path, out_dir: Path,
                           start: float, end: float, max_frames: int) -> dict[str, Any]:
    """Extract every decoded frame in a bounded interval, not a requested-fps grid."""
    if not all(type(v) in (int, float) and math.isfinite(v) for v in (start, end)) or not 0 <= start < end:
        raise ValueError("all-frame extraction needs finite 0 <= start < end")
    if type(max_frames) is not int or max_frames < 1:
        raise ValueError("max_frames must be a positive integer")
    source_hash = sha256(source)
    decoded = json.loads(run([
        ffprobe, "-v", "error", "-select_streams", "v:0", "-show_frames",
        "-show_entries", "frame=best_effort_timestamp_time", "-of", "json", str(source)
    ]).stdout).get("frames", [])
    times = [decimal_seconds(frame.get("best_effort_timestamp_time")) for frame in decoded]
    if not times or times != sorted(times):
        raise ValueError("cannot establish ordered decoded source timestamps")
    # ffprobe reports decimal times. Preserve exact exclusive boundaries even
    # for nonzero origins (binary 2.3 - 2 can fall just below 0.3).
    origin = times[0]
    times = [t - origin for t in times]
    indices = [i for i, t in enumerate(times) if decimal_seconds(start) <= t < decimal_seconds(end)]
    if not indices:
        raise ValueError("no decoded frames in the requested interval")
    if len(indices) > max_frames:
        raise ValueError(f"all-frame range contains {len(indices)} frames; maximum is {max_frames}; "
                         "split the interval, do not silently lower sampling density")
    out_dir.mkdir(parents=True, exist_ok=True)
    burst_dir = Path(tempfile.mkdtemp(prefix=f"all-{source_hash[:12]}-{start:.3f}-{end:.3f}-", dir=out_dir))
    run([ffmpeg, "-hide_banner", "-loglevel", "error", "-i", str(source), "-map", "0:v:0",
         "-vf", f"select='between(n,{indices[0]},{indices[-1]})'", "-fps_mode", "passthrough",
         "-y", str(burst_dir / "frame-%04d.png")])
    frames = sorted(burst_dir.glob("frame-*.png"))
    if len(frames) != len(indices) or sha256(source) != source_hash:
        raise ValueError("all-frame count or source changed during extraction; evidence is unverified")
    columns = min(8, len(frames))
    rows = math.ceil(len(frames) / columns)
    sheet = burst_dir / "all-contact-sheet.jpg"
    run([ffmpeg, "-hide_banner", "-loglevel", "error", "-framerate", "1", "-pattern_type", "glob",
         "-i", str(burst_dir / "frame-*.png"), "-vf",
         f"scale=480:270:force_original_aspect_ratio=decrease,pad=480:270:(ow-iw)/2:(oh-ih)/2:color=black,tile={columns}x{rows}:padding=4:margin=4",
         "-frames:v", "1", "-y", str(sheet)])
    return {
        "start": start, "end": end, "requested_fps": None,
        "frame_count": len(frames), "expected_source_frames": len(indices),
        "frames": [str(p) for p in frames], "contact_sheet": str(sheet),
        "source_sha256": source_hash, "frame_resolution": "native",
        "decoded_frame_indices": indices, "source_timestamps_seconds": [float(times[i]) for i in indices],
        "method": "all-decoded-source-frames-v1", "time_origin": "first decoded video frame; out exclusive",
        "sampling": "every decoded source frame whose start timestamp is in [start,end); no resampling",
        "contact_sheet_purpose": "overview only; inspect native frames in temporal context",
        "review_status": "extracted_not_reviewed",
    }


def diagnostic_log(ffmpeg: str, source: Path, filter_graph: str) -> dict[str, Any]:
    return detector_log(ffmpeg, source, filter_graph)


def audio_log(ffmpeg: str, source: Path, filter_graph: str) -> dict[str, Any]:
    return detector_log(ffmpeg, source, filter_graph, audio=True)


def detector_status(records: dict) -> dict:
    return {key: {k: v for k, v in result.items() if k != "stderr"} for key, result in records.items()}


def parse_video_diagnostics(ffmpeg: str, source: Path, threshold: float) -> dict[str, Any]:
    logs = {
        "scene": diagnostic_log(ffmpeg, source, f"select='gt(scene,{threshold})',showinfo"),
        "black": diagnostic_log(ffmpeg, source, "blackdetect=d=0.15:pix_th=0.10"),
        "freeze": diagnostic_log(ffmpeg, source, "freezedetect=n=-50dB:d=0.5"),
    }
    scene_text = logs["scene"]["stderr"]
    scene_times = [float(value) for value in re.findall(r"pts_time:([0-9.]+)", scene_text)]
    black_text = logs["black"]["stderr"]
    black = [
        {"start": float(start), "end": float(end), "duration": float(duration)}
        for start, end, duration in re.findall(r"black_start:([0-9.]+) black_end:([0-9.]+) black_duration:([0-9.]+)", black_text)
    ]
    freeze_text = logs["freeze"]["stderr"]
    starts = [float(value) for value in re.findall(r"freeze_start: ([0-9.]+)", freeze_text)]
    ends = [float(value) for value in re.findall(r"freeze_end: ([0-9.]+)", freeze_text)]
    durations = [float(value) for value in re.findall(r"freeze_duration: ([0-9.]+)", freeze_text)]
    freezes = []
    for index, start in enumerate(starts):
        freezes.append({
            "start": start,
            "end": ends[index] if index < len(ends) else None,
            "duration": durations[index] if index < len(durations) else None,
        })
    return {"status": "completed" if all(v["status"] == "completed" for v in logs.values()) else "partial_or_failed",
            "checks": detector_status(logs), "scene_change_threshold": threshold,
            "scene_change_times": scene_times if logs["scene"]["status"] == "completed" else None,
            "black_ranges": black if logs["black"]["status"] == "completed" else None,
            "freeze_ranges": freezes if logs["freeze"]["status"] == "completed" else None}


def parse_audio_diagnostics(ffmpeg: str, source: Path) -> dict[str, Any]:
    logs = {"silence": audio_log(ffmpeg, source, "silencedetect=n=-45dB:d=0.4"),
            "volume": audio_log(ffmpeg, source, "volumedetect"),
            "loudness": audio_log(ffmpeg, source, "ebur128=peak=true")}
    silence_text = logs["silence"]["stderr"]
    starts = [float(value) for value in re.findall(r"silence_start: ([0-9.]+)", silence_text)]
    ends = [float(value) for value in re.findall(r"silence_end: ([0-9.]+)", silence_text)]
    durations = [float(value) for value in re.findall(r"silence_duration: ([0-9.]+)", silence_text)]
    silences = []
    for index, start in enumerate(starts):
        silences.append({
            "start": start,
            "end": ends[index] if index < len(ends) else None,
            "duration": durations[index] if index < len(durations) else None,
        })
    volume_text = logs["volume"]["stderr"] if logs["volume"]["status"] == "completed" else ""
    mean = re.search(r"mean_volume: ([^ ]+) dB", volume_text)
    maximum = re.search(r"max_volume: ([^ ]+) dB", volume_text)
    loudness_text = logs["loudness"]["stderr"] if logs["loudness"]["status"] == "completed" else ""
    integrated_matches = re.findall(r"I:\s*(-?[0-9.]+) LUFS", loudness_text)
    peak_matches = re.findall(r"Peak:\s*(-?[0-9.]+) dBFS", loudness_text)
    return {
        "status": "completed" if all(v["status"] == "completed" for v in logs.values()) else "partial_or_failed",
        "checks": detector_status(logs),
        "silence_threshold": "-45dB for 0.4s",
        "silence_ranges": silences if logs["silence"]["status"] == "completed" else None,
        "mean_volume_db": parse_float(mean.group(1)) if mean else None,
        "max_volume_db": parse_float(maximum.group(1)) if maximum else None,
        "integrated_loudness_lufs": parse_float(integrated_matches[-1]) if integrated_matches else None,
        "true_peak_dbfs": parse_float(peak_matches[-1]) if peak_matches else None,
    }


def audio_spectrogram(ffmpeg: str, source: Path, target: Path) -> None:
    run([
        ffmpeg, "-hide_banner", "-loglevel", "error", "-i", str(source), "-lavfi",
        "showspectrumpic=s=1600x900:legend=1:color=channel", "-frames:v", "1", "-y", str(target)
    ])


def review_boundary() -> dict[str, Any]:
    return {
        "automatic": "technical evidence only",
        "review_status": "extracted_not_reviewed",
        "coverage_warning": "An overview sheet does not cover the intervals between its samples. "
                            "Even an all-frame burst is extraction evidence, not proof those frames were reviewed.",
        "requires_human_or_visual_review": [
            "story job and performance", "identity and wardrobe", "prop ownership and contact physics",
            "exact text and UI", "camera intention and spatial continuity",
            "usable in/out points and transition landing"
        ],
        "requires_auditory_review": [
            "dialogue accuracy and voice identity", "naturalness and timbre", "synchronization and contact feel",
            "acoustic perspective and continuity", "artifacts and dramatic hierarchy"
        ],
        "warning": "Frames, spectra, loudness, black, freeze, silence and scene-change detections are evidence locations only. They cannot replace normal-speed playback, targeted dense-frame inspection or actual listening, and are never automatic rejection reasons."
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source")
    parser.add_argument("--out-dir")
    parser.add_argument("--samples", type=int, default=16)
    parser.add_argument("--scene-threshold", type=float, default=0.35)
    parser.add_argument("--dense-range", action="append", default=[], help="targeted START:END range in seconds; repeatable")
    parser.add_argument("--dense-fps", type=float, default=24.0)
    parser.add_argument("--dense-sampling", choices=["sampled", "all"], default="sampled",
                        help="all: every decoded source frame in each short range; native resolution, ignores dense-fps")
    parser.add_argument("--max-dense-frames", type=int, default=120)
    parser.add_argument("--dense-resolution", choices=["native", "overview"], default="native")
    parser.add_argument("--selected-out", type=float, help="exclusive source-video outpoint; also extract its last retained frame")
    args = parser.parse_args()
    try:
        if not 4 <= args.samples <= 36:
            raise ValueError("--samples must be from 4 to 36")
        if not 0.05 <= args.scene_threshold <= 0.95:
            raise ValueError("--scene-threshold must be from 0.05 to 0.95")
        if args.dense_sampling == "sampled" and not 1 <= args.dense_fps <= 60:
            raise ValueError("--dense-fps must be from 1 to 60")
        if args.dense_sampling == "all" and args.dense_resolution != "native":
            raise ValueError("all-frame evidence requires native resolution")
        if not 8 <= args.max_dense_frames <= 240:
            raise ValueError("--max-dense-frames must be from 8 to 240")
        source = Path(args.source).resolve()
        if not source.is_file():
            raise ValueError(f"source does not exist: {source}")
        ffmpeg = find_binary("ffmpeg")
        ffprobe = find_binary("ffprobe")
        source_hash = sha256(source)
        info = metadata(probe(ffprobe, source))
        if not info["video"] and not info["audio"]:
            raise ValueError("source has no supported video or audio stream")
        dense_ranges = [parse_dense_range(value) for value in args.dense_range]
        if info["video"]:
            timing = probe_video_timing(ffprobe, source)
            info["video"]["timeline"] = timing
            if args.selected_out is not None:
                validate_video_outpoint(args.selected_out, timing)
            for start, end in dense_ranges:
                validate_video_outpoint(end, timing)
            # An overview may use the observed span when the tail is unknown;
            # this sampling extent is not promoted to a verified video end.
            duration = timing["end_seconds"] or max(timing["last_frame_start_seconds"], 0.04)
        elif dense_ranges or args.selected_out is not None:
            raise ValueError("video ranges require a video stream")
        out_root = Path(args.out_dir).resolve() if args.out_dir else source.parent / f"{source.stem}_review"
        out_root.mkdir(parents=True, exist_ok=True)
        out_dir = Path(tempfile.mkdtemp(prefix=f"run-{source_hash[:12]}-", dir=out_root))
        artifacts: dict[str, Any] = {}
        diagnostics: dict[str, Any] = {}
        if info["video"]:
            first = out_dir / "first-frame.png"
            last = out_dir / "last-frame.png"
            sheet = out_dir / "contact-sheet.jpg"
            extract_frame(ffmpeg, source, first, 0.0)
            boundary = extract_last_frame(ffmpeg, ffprobe, source, last)
            sampling = contact_sheet(ffmpeg, source, sheet, duration, args.samples)
            artifacts.update(first_frame=str(first), last_frame=str(last), last_frame_evidence=boundary,
                             contact_sheet=str(sheet), contact_sheet_sampling=sampling)
            if args.selected_out is not None:
                artifacts["selected_out_frame"] = extract_last_frame(ffmpeg, ffprobe, source,
                    out_dir / "selected-out-frame.png", args.selected_out)
            diagnostics["video"] = parse_video_diagnostics(ffmpeg, source, args.scene_threshold)
            if dense_ranges:
                artifacts["dense_bursts"] = [
                    (all_source_frame_burst(ffmpeg, ffprobe, source, out_dir, start, end, args.max_dense_frames)
                     if args.dense_sampling == "all" else
                     dense_frame_burst(ffmpeg, source, out_dir, start, end, args.dense_fps, args.max_dense_frames, args.dense_resolution))
                    for start, end in dense_ranges
                ]
        if info["audio"]:
            diagnostics["audio"] = parse_audio_diagnostics(ffmpeg, source)
            spectrum = out_dir / "audio-spectrogram.png"
            audio_spectrogram(ffmpeg, source, spectrum)
            artifacts["audio_spectrogram"] = str(spectrum)
            artifacts["audition_source"] = str(source)
        if sha256(source) != source_hash:
            raise ValueError("source changed during extraction; discard this run as unverified and inspect the current version")
        manifest = {
            "source": {"path": str(source), "bytes": source.stat().st_size, "sha256": source_hash},
            "metadata": info,
            "artifacts": artifacts,
            "diagnostics": diagnostics,
            "review_boundary": review_boundary(),
        }
        manifest_path = out_dir / "review-manifest.json"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        complete = all(item.get("status") == "completed" for item in diagnostics.values())
        print(json.dumps({"ok": complete, "status": "evidence_extracted" if complete else "partial_or_failed",
                          "manifest": str(manifest_path), "artifacts": artifacts,
                          "not_checked": ["creative quality", "acceptance", "actual listening"]}, ensure_ascii=False, indent=2))
        if not complete:
            return 2
    except (OSError, ValueError, json.JSONDecodeError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
