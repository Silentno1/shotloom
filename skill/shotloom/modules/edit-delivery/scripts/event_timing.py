#!/usr/bin/env python3
"""Read-only timing arithmetic; not media inspection, caption export or approval."""

import argparse
from decimal import Decimal, localcontext
from fractions import Fraction
import json
import sys


def number(value, label):
    """Retain rational/decimal precision; timestamps use the caller's origin."""
    if isinstance(value, bool) or not isinstance(value, (str, int, float, Fraction)):
        raise ValueError(f"{label} must be a finite number or rational string")
    try:
        return Fraction(str(value))
    except (ValueError, ZeroDivisionError, OverflowError) as exc:
        raise ValueError(f"{label} must be a finite number or rational string") from exc


def positive_rate(value):
    rate = number(value, "rate")
    if rate <= 0:
        raise ValueError("rate must be positive; reverse/freeze/nonlinear maps are unsupported")
    return rate


def map_interval(source_in, source_out, timeline_in, rate, event_in, event_out):
    """Intersect [event_in,event_out) with a declared constant-rate source use."""
    source_in = number(source_in, "source_in")
    source_out = number(source_out, "source_out")
    timeline_in = number(timeline_in, "timeline_in")
    rate = positive_rate(rate)
    event_in = number(event_in, "event_in")
    event_out = number(event_out, "event_out")
    if source_out <= source_in or event_out <= event_in:
        raise ValueError("source and event ranges must have positive duration")
    start, end = max(source_in, event_in), min(source_out, event_out)
    result = {
        "status": "calculation_only",
        "mapping": "declared_constant_positive_rate",
        "timeline_window": [timeline_in, timeline_in + (source_out - source_in) / rate],
        "source_intersection": None,
        "timeline_event": None,
        "disposition": "excluded",
        "not_verified": ["source/version/origin", "audible words", "actual rate map", "rendered sync"],
    }
    if start < end:
        result.update(
            source_intersection=[start, end],
            timeline_event=[timeline_in + (start - source_in) / rate,
                            timeline_in + (end - source_in) / rate],
            disposition="retained" if (start, end) == (event_in, event_out)
            else "partial_requires_review",
        )
    return result


def sfx_placement(target, anchor_offset, rate=1, measured_delay=None):
    """Desired output anchor includes intent; positive measured delay means late."""
    target = number(target, "target")
    anchor_offset = number(anchor_offset, "anchor_offset")
    rate = positive_rate(rate)
    if anchor_offset < 0:
        raise ValueError("anchor_offset must be measured at/after the retained audio inpoint")
    nominal = target - anchor_offset / rate
    delay = None if measured_delay is None else number(measured_delay, "measured_delay")
    placement = nominal if delay is None else nominal - delay
    return {
        "status": "calculation_only",
        "nominal_placement": nominal,
        "placement": placement,
        "measured_delay": delay,
        "basis": "nominal_offset_unverified" if delay is None else "declared_measured_offset",
        "requires_preroll_or_edit_review": placement < 0,
        "not_verified": ["anchor perception", "measurement evidence", "pipeline validity", "listening"],
    }


def encode_fraction(value):
    if not isinstance(value, Fraction):
        raise TypeError(f"Unsupported output type: {type(value).__name__}")
    with localcontext() as context:
        context.prec = 28
        decimal = format(Decimal(value.numerator) / Decimal(value.denominator), "f")
    return {"seconds": decimal, "exact": str(value)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    mapping = commands.add_parser("map", help="map one interval through one constant-rate source use")
    for name in ("source-in", "source-out", "timeline-in", "event-in", "event-out"):
        mapping.add_argument("--" + name, required=True)
    mapping.add_argument("--rate", required=True, help="actual constant audio playback rate, not fps")
    sound = commands.add_parser("sfx", help="calculate nominal or measured-offset sound placement")
    sound.add_argument("--target", required=True)
    sound.add_argument("--anchor-offset", required=True)
    sound.add_argument("--rate", default="1")
    sound.add_argument("--measured-delay", help="optional measured export delay; positive is late")
    args = vars(parser.parse_args(argv))
    command = args.pop("command")
    try:
        result = map_interval(**args) if command == "map" else sfx_placement(**args)
    except ValueError as exc:
        print(json.dumps({"status": "invalid_input", "error": str(exc)}), file=sys.stderr)
        return 2
    print(json.dumps(result, default=encode_fraction, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
