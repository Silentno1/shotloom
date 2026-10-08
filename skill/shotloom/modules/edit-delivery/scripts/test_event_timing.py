"""Synthetic arithmetic tests; none inspect media or establish audible quality."""

from contextlib import redirect_stderr, redirect_stdout
from fractions import Fraction as F
import io
import json
import unittest

import event_timing as timing


class IntervalTests(unittest.TestCase):
    def test_constant_rate_example(self):
        result = timing.map_interval(10, 12, 3, 2, "10.8", "11.2")
        self.assertEqual(result["timeline_event"], [F("3.4"), F("3.6")])
        self.assertEqual(result["timeline_window"], [F(3), F(4)])
        self.assertEqual(result["disposition"], "retained")
        self.assertEqual(result["status"], "calculation_only")

    def test_outpoint_is_exclusive(self):
        for start, end in ((12, 13), (9, 10)):
            result = timing.map_interval(10, 12, 3, 1, start, end)
            self.assertEqual(result["disposition"], "excluded")
            self.assertIsNone(result["timeline_event"])

    def test_full_window_and_exact_end_are_retained(self):
        self.assertEqual(timing.map_interval(10, 12, 3, 1, 10, 12)["timeline_event"], [F(3), F(5)])
        self.assertEqual(timing.map_interval(10, 12, 3, 1, 11, 12)["disposition"], "retained")

    def test_partial_word_never_becomes_retained(self):
        for start, end in ((9, 11), (11, 13), (9, 13)):
            result = timing.map_interval(10, 12, 3, 1, start, end)
            self.assertEqual(result["disposition"], "partial_requires_review")
            self.assertIsNotNone(result["timeline_event"])

    def test_repeated_source_has_distinct_timeline_instances(self):
        first = timing.map_interval(10, 12, 0, 1, 11, 12)
        second = timing.map_interval(10, 12, 20, 1, 11, 12)
        self.assertEqual(first["timeline_event"], [F(1), F(2)])
        self.assertEqual(second["timeline_event"], [F(21), F(22)])

    def test_cut_away_audio_gap_is_excluded(self):
        for source_in, source_out, timeline_in in ((0, 2, 0), (4, 6, 2)):
            result = timing.map_interval(source_in, source_out, timeline_in, 1, "2.5", "3.5")
            self.assertEqual(result["disposition"], "excluded")

    def test_audio_placement_can_precede_picture(self):
        result = timing.map_interval(10, 12, 2, 1, 10, 11)
        self.assertEqual(result["timeline_event"], [F(2), F(3)])

    def test_rational_rate_and_decimal_origin(self):
        result = timing.map_interval("10.001", "11.002", "3.003", "1001/1000", "10.001", "11.002")
        self.assertEqual(result["timeline_event"], [F("3.003"), F("4.003")])

    def test_negative_media_origin_is_not_silently_clamped(self):
        self.assertEqual(timing.map_interval(-1, 1, -2, 1, -1, 0)["timeline_event"], [F(-2), F(-1)])

    def test_invalid_ranges_rates_and_nonfinite_values(self):
        for args in ((2, 1, 0, 1, 1, 2), (0, 2, 0, 1, 1, 1),
                     (0, 2, 0, 0, 0, 1), (0, 2, 0, -1, 0, 1),
                     (0, 2, 0, "ramp", 0, 1), (0, "NaN", 0, 1, 0, 1),
                     (0, 2, True, 1, 0, 1), (0, 2, 0, 1, 0, float("inf"))):
            with self.subTest(args=args), self.assertRaises(ValueError):
                timing.map_interval(*args)


class SoundTests(unittest.TestCase):
    def test_measured_late_delay(self):
        result = timing.sfx_placement(2, ".045", 1, ".08")
        self.assertEqual(result["placement"], F("1.875"))
        self.assertEqual(result["nominal_placement"], F("1.955"))

    def test_unknown_delay_is_not_claimed_measured_zero(self):
        result = timing.sfx_placement(2, ".045")
        self.assertIsNone(result["measured_delay"])
        self.assertEqual(result["basis"], "nominal_offset_unverified")
        self.assertEqual(result["placement"], F("1.955"))
        known = timing.sfx_placement(2, ".045", measured_delay=0)
        self.assertEqual(known["measured_delay"], 0)
        self.assertEqual(known["basis"], "declared_measured_offset")

    def test_measured_early_offset_has_opposite_sign(self):
        self.assertEqual(timing.sfx_placement(2, ".045", 1, "-.08")["placement"], F("2.035"))

    def test_audio_rate_scales_anchor_not_export_delay(self):
        self.assertEqual(timing.sfx_placement(2, ".2", 2, ".08")["placement"], F("1.82"))

    def test_negative_placement_requires_review_not_clamping(self):
        result = timing.sfx_placement(".01", ".2", 1, ".08")
        self.assertEqual(result["placement"], F("-.27"))
        self.assertTrue(result["requires_preroll_or_edit_review"])

    def test_trimmed_anchor_zero_is_valid(self):
        self.assertEqual(timing.sfx_placement(2, 0, 1, 0)["placement"], 2)

    def test_invalid_sound_values(self):
        for args in ((2, -.1, 1, 0), (2, .1, 0, 0), (2, .1, -1, 0),
                     (2, .1, 1, "NaN"), ("inf", .1, 1, 0), (2, True, 1, 0)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                timing.sfx_placement(*args)


class CommandTests(unittest.TestCase):
    def test_map_command_reports_exact_rationals(self):
        stream = io.StringIO()
        with redirect_stdout(stream):
            code = timing.main(["map", "--source-in", "10", "--source-out", "12",
                                "--timeline-in", "3", "--rate", "2",
                                "--event-in", "10.8", "--event-out", "11.2"])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(stream.getvalue())["timeline_event"][0], {"seconds": "3.4", "exact": "17/5"})

    def test_sfx_command_preserves_unverified_measurement(self):
        stream = io.StringIO()
        with redirect_stdout(stream):
            code = timing.main(["sfx", "--target", "2", "--anchor-offset", ".045"])
        self.assertEqual(code, 0)
        self.assertIsNone(json.loads(stream.getvalue())["measured_delay"])

    def test_invalid_cli_returns_error_without_success(self):
        output, error = io.StringIO(), io.StringIO()
        with redirect_stdout(output), redirect_stderr(error):
            code = timing.main(["sfx", "--target", "2", "--anchor-offset", ".1", "--rate", "0"])
        self.assertEqual(code, 2)
        self.assertEqual(output.getvalue(), "")
        self.assertEqual(json.loads(error.getvalue())["status"], "invalid_input")

    def test_nonterminating_decimal_keeps_exact_value(self):
        result = timing.encode_fraction(F(1, 3))
        self.assertEqual(result["exact"], "1/3")
        self.assertTrue(result["seconds"].startswith("0.3333"))


if __name__ == "__main__":
    unittest.main()
