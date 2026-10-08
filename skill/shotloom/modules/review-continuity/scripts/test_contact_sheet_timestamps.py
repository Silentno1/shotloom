"""Real-media regression: every tile must match its reported source frame."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from take_preflight import contact_sheet, find_binary


class ContactSheetTimestampTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.ffmpeg = find_binary("ffmpeg")
            cls.ffprobe = find_binary("ffprobe")
        except FileNotFoundError as exc:
            raise unittest.SkipTest(str(exc))

    def check_fixture(self, timing, duration):
        with tempfile.TemporaryDirectory(prefix="contact-pts-test-") as directory:
            source = Path(directory) / "source.mkv"
            sheet = Path(directory) / "sheet.png"
            # Each source frame has a unique, losslessly encoded red value.
            pixels = b"".join(bytes((i * 5, 0, 0)) * (64 * 36) for i in range(48))
            subprocess.run([
                self.ffmpeg, "-v", "error", "-f", "rawvideo", "-pixel_format", "rgb24",
                "-video_size", "64x36", "-framerate", "24", "-i", "pipe:0",
                "-vf", timing, "-fps_mode", "vfr", "-c:v", "ffv1", "-pix_fmt", "bgr0",
                str(source),
            ], input=pixels, check=True, capture_output=True)
            frames = json.loads(subprocess.check_output([
                self.ffprobe, "-v", "error", "-select_streams", "v:0", "-show_frames",
                "-show_entries", "frame=best_effort_timestamp_time", "-of", "json", str(source),
            ]))["frames"]
            times = [float(frame["best_effort_timestamp_time"]) for frame in frames]
            times = [time - times[0] for time in times]
            result = contact_sheet(self.ffmpeg, source, sheet, duration, 7)
            selected = result["source_timestamps_seconds"]
            self.assertEqual(result["actual_samples"], 7)
            self.assertEqual(selected[0], 0)
            self.assertEqual(selected, sorted(set(selected)))
            rgb = subprocess.check_output([
                self.ffmpeg, "-v", "error", "-i", str(sheet),
                "-f", "rawvideo", "-pix_fmt", "rgb24", "pipe:1",
            ])
            width = 4 * 480 + 5 * 4
            for tile, timestamp in enumerate(selected):
                frame = min(range(len(times)), key=lambda i: abs(times[i] - timestamp))
                self.assertAlmostEqual(times[frame], timestamp, places=5)
                # Sample away from the timestamp overlay and tile borders.
                x = 4 + (tile % 4) * 484 + 240
                y = 4 + (tile // 4) * 274 + 80
                offset = (y * width + x) * 3
                self.assertAlmostEqual(rgb[offset], frame * 5, delta=2)
                self.assertLessEqual(rgb[offset + 1], 2)
                self.assertLessEqual(rgb[offset + 2], 2)

    def test_non_integer_sampling_interval(self):
        self.check_fixture("setpts=PTS", 2)

    def test_variable_frame_timestamps(self):
        self.check_fixture("setpts='if(lt(N,24),N,24+(N-24)*2)/(24*TB)'", 3)

    def test_nonzero_source_start(self):
        self.check_fixture("setpts=PTS+2/TB", 2)

    def test_invalid_duration_rejected_before_media_access(self):
        for duration in (0, -1, float("nan"), float("inf")):
            with self.subTest(duration=duration), self.assertRaises(ValueError):
                contact_sheet(self.ffmpeg, Path("missing"), Path("unused"), duration, 7)


if __name__ == "__main__":
    unittest.main()
