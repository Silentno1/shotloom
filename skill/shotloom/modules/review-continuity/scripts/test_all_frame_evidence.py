"""Real short synthetic clips prove extraction correspondence, not anomaly recognition."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import take_preflight as take


class AllFrameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.ffmpeg, cls.ffprobe = take.find_binary("ffmpeg"), take.find_binary("ffprobe")
        except FileNotFoundError as exc:
            raise unittest.SkipTest(str(exc))

    def fixture(self, root, fps=60, count=12, timing="setpts=PTS", single_flash=False):
        source = root / "source.mkv"
        pixels = b"".join(bytes((255 if i == 1 else 0, 0, 0) if single_flash else (i * 10, 0, 0)) * (32 * 48)
                          for i in range(count))
        subprocess.run([self.ffmpeg, "-v", "error", "-f", "rawvideo", "-pixel_format", "rgb24",
                        "-video_size", "32x48", "-framerate", str(fps), "-i", "pipe:0", "-vf", timing,
                        "-fps_mode", "vfr", "-c:v", "ffv1", "-pix_fmt", "bgr0", str(source)],
                       input=pixels, capture_output=True, check=True)
        return source

    def red(self, path):
        return subprocess.check_output([self.ffmpeg, "-v", "error", "-i", str(path), "-vf", "crop=1:1:0:0",
                                        "-f", "rawvideo", "-pix_fmt", "rgb24", "pipe:1"])[0]

    def test_every_native_frame_and_timestamp_are_bound_to_source(self):
        with tempfile.TemporaryDirectory(prefix="all-frames-") as folder:
            root = Path(folder)
            source = self.fixture(root)
            result = take.all_source_frame_burst(self.ffmpeg, self.ffprobe, source, root / "evidence", 0, .2, 12)
            self.assertEqual(result["decoded_frame_indices"], list(range(12)))
            self.assertEqual([self.red(p) for p in result["frames"]], list(range(0, 120, 10)))
            info = take.metadata(take.probe(self.ffprobe, Path(result["frames"][0])))["video"]
            self.assertEqual((info["width"], info["height"]), (32, 48))
            self.assertEqual(result["source_sha256"], take.sha256(source))
            self.assertEqual(result["review_status"], "extracted_not_reviewed")

    def test_single_source_frame_flash_can_be_absent_from_sampled_burst(self):
        with tempfile.TemporaryDirectory(prefix="single-flash-") as folder:
            root = Path(folder)
            source = self.fixture(root, single_flash=True)
            sampled = take.dense_frame_burst(self.ffmpeg, source, root, 0, .2, 24, 12, "native")
            complete = take.all_source_frame_burst(self.ffmpeg, self.ffprobe, source, root, 0, .2, 12)
            self.assertNotIn(255, [self.red(p) for p in sampled["frames"]])
            self.assertEqual([self.red(p) for p in complete["frames"]].count(255), 1)

    def test_variable_rate_nonzero_origin_and_exclusive_boundary(self):
        with tempfile.TemporaryDirectory(prefix="all-vfr-") as folder:
            root = Path(folder)
            source = self.fixture(root, fps=10, count=6, timing="setpts='if(lt(N,3),N,3+(N-3)*2)/(10*TB)+2/TB'")
            result = take.all_source_frame_burst(self.ffmpeg, self.ffprobe, source, root, 0, .3, 6)
            self.assertEqual(result["decoded_frame_indices"], [0, 1, 2])
            self.assertEqual(result["source_timestamps_seconds"], [0, .1, .2])
            later = take.all_source_frame_burst(self.ffmpeg, self.ffprobe, source, root, .3, .7, 6)
            self.assertEqual(later["decoded_frame_indices"], [3, 4])
            self.assertEqual([self.red(p) for p in later["frames"]], [30, 40])

    def test_over_budget_fails_without_silent_subsampling_or_outputs(self):
        with tempfile.TemporaryDirectory(prefix="all-budget-") as folder:
            root = Path(folder)
            source = self.fixture(root)
            out = root / "evidence"
            with self.assertRaisesRegex(ValueError, "split the interval"):
                take.all_source_frame_burst(self.ffmpeg, self.ffprobe, source, out, 0, .2, 8)
            self.assertFalse(out.exists())

    def test_repeated_extraction_uses_distinct_evidence_paths(self):
        with tempfile.TemporaryDirectory(prefix="all-repeat-") as folder:
            root = Path(folder)
            source = self.fixture(root)
            first = take.all_source_frame_burst(self.ffmpeg, self.ffprobe, source, root, 0, .1, 12)
            second = take.all_source_frame_burst(self.ffmpeg, self.ffprobe, source, root, 0, .1, 12)
            self.assertTrue(set(first["frames"]).isdisjoint(second["frames"]))
            self.assertEqual(first["decoded_frame_indices"], second["decoded_frame_indices"])

    def test_empty_or_invalid_range_is_not_an_empty_success(self):
        for start, end in ((0, float("inf")), (float("nan"), 1), (1, 0), (-1, 1), (False, 1)):
            with self.subTest(start=start, end=end), self.assertRaises(ValueError):
                take.all_source_frame_burst("unused", "unused", Path("missing"), Path("unused"), start, end, 12)
        with tempfile.TemporaryDirectory(prefix="all-empty-") as folder:
            root = Path(folder)
            source = self.fixture(root, fps=1, count=2)
            with self.assertRaisesRegex(ValueError, "no decoded frames"):
                take.all_source_frame_burst(self.ffmpeg, self.ffprobe, source, root, .2, .3, 12)

    def test_cli_all_ignores_fps_grid_and_preserves_review_boundary(self):
        with tempfile.TemporaryDirectory(prefix="all-cli-") as folder:
            root = Path(folder)
            source = self.fixture(root, fps=120)
            result = subprocess.run([sys.executable, "-B", str(Path(take.__file__)), str(source),
                                     "--out-dir", str(root / "evidence"), "--samples", "4",
                                     "--dense-range", "0:0.1", "--dense-sampling", "all", "--dense-fps", "1"],
                                    text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            output = json.loads(result.stdout)
            manifest = json.loads(Path(output["manifest"]).read_text())
            burst = manifest["artifacts"]["dense_bursts"][0]
            self.assertEqual(burst["frame_count"], 12)
            self.assertIsNone(burst["requested_fps"])
            self.assertEqual(manifest["review_boundary"]["review_status"], "extracted_not_reviewed")


if __name__ == "__main__":
    unittest.main()
