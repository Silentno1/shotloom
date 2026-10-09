#!/usr/bin/env python3
import unittest

import take_preflight as preflight


class TakePreflightContractTests(unittest.TestCase):
    def test_dense_range_parser(self):
        self.assertEqual(preflight.parse_dense_range("1.25:1.75"), (1.25, 1.75))

    def test_dense_range_rejects_reverse_or_negative(self):
        for value in ("2:1", "-1:2", "bad"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    preflight.parse_dense_range(value)

    def test_review_manifest_requires_auditory_review(self):
        boundary = preflight.review_boundary()
        self.assertTrue(boundary["requires_auditory_review"])
        self.assertIn("cannot replace", boundary["warning"])


class VideoTimingTests(unittest.TestCase):
    def fixture(self, times, tail_duration=None, **stream):
        frames = [{"best_effort_timestamp_time": str(t)} for t in times]
        if tail_duration is not None:
            frames[-1]["duration_time"] = str(tail_duration)
        return {"format": {"duration": "0.092"}, "frames": frames,
                "streams": [{"codec_type": "video", "time_base": "1/1000", **stream}]}

    def test_last_frame_duration_not_container_duration(self):
        timing = preflight.video_timing(self.fixture([0, .008, .017, .092], .008))
        self.assertEqual(timing["end_seconds"], .1)
        self.assertFalse(timing["end_is_estimate"])
        preflight.validate_video_outpoint(.1, timing)
        with self.assertRaisesRegex(ValueError, "exceeds decoded video"):
            preflight.validate_video_outpoint(.108, timing)

    def test_older_ffprobe_duration_field(self):
        data = self.fixture([0, .05])
        data["frames"][-1]["pkt_duration_time"] = ".05"
        self.assertEqual(preflight.video_timing(data)["end_seconds"], .1)

    def test_vfr_tail_and_nonzero_origin(self):
        timing = preflight.video_timing(self.fixture([2, 2.1, 2.3], .2))
        self.assertEqual(timing["end_seconds"], .5)
        self.assertEqual(timing["stream_origin_seconds"], 2)
        preflight.validate_video_outpoint(.5, timing)
        with self.assertRaises(ValueError):
            preflight.validate_video_outpoint(2.5, timing)

    def test_longer_audio_cannot_extend_video(self):
        data = self.fixture([0, .5], .5)
        data["format"]["duration"] = "2"
        data["streams"].append({"codec_type": "audio", "duration": "2"})
        timing = preflight.video_timing(data)
        with self.assertRaises(ValueError):
            preflight.validate_video_outpoint(1.5, timing)

    def test_missing_tail_can_use_video_stream_duration(self):
        timing = preflight.video_timing(self.fixture([2, 2.1, 2.3], start_time="2", duration="0.5"))
        self.assertEqual(timing["end_seconds"], .5)
        self.assertEqual(timing["end_basis"], "video_stream_duration")

    def test_cfr_fallback_requires_matching_timestamps_and_declares_estimate(self):
        timing = preflight.video_timing(self.fixture([0, .033, .067], r_frame_rate="30/1", avg_frame_rate="30/1"))
        self.assertEqual(timing["end_seconds"], .1)
        self.assertTrue(timing["end_is_estimate"])
        unknown = preflight.video_timing(self.fixture([0, .033, .1], r_frame_rate="30/1", avg_frame_rate="30/1"))
        self.assertIsNone(unknown["end_seconds"])
        preflight.validate_video_outpoint(.1, unknown)
        with self.assertRaisesRegex(ValueError, "unknown"):
            preflight.validate_video_outpoint(.11, unknown)

    def test_unknown_single_frame_tail_is_not_guessed(self):
        timing = preflight.video_timing(self.fixture([2], r_frame_rate="30/1", avg_frame_rate="30/1"))
        self.assertIsNone(timing["end_seconds"])
        with self.assertRaises(ValueError):
            preflight.validate_video_outpoint(.01, timing)

    def test_invalid_frame_times_and_outpoints_are_rejected(self):
        for times in ([], [0, 0], [1, 0], [0, "NaN"]):
            with self.subTest(times=times), self.assertRaises(ValueError):
                preflight.video_timing(self.fixture(times))
        timing = preflight.video_timing(self.fixture([0, .05], .05))
        for value in (-1, 0, float("nan"), float("inf"), True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                preflight.validate_video_outpoint(value, timing)


if __name__ == "__main__":
    unittest.main()
