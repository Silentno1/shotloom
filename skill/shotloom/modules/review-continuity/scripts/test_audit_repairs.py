"""Real decoded-frame correspondence plus diagnostic-failure regressions."""
import json
import contextlib
import io
from pathlib import Path
import subprocess
import tempfile
import sys
import unittest
from unittest.mock import patch

import take_preflight as take


class DetectorFailureTests(unittest.TestCase):
    def test_failed_video_detectors_are_not_empty_success(self):
        with patch.object(take, 'run', return_value=subprocess.CompletedProcess([], 1, '', 'filter failed')):
            result = take.parse_video_diagnostics('ffmpeg', Path('/fixture'), .35)
        self.assertEqual(result['status'], 'partial_or_failed')
        for key in ('scene_change_times', 'black_ranges', 'freeze_ranges'):
            self.assertIsNone(result[key])
        self.assertTrue(all(v['status'] == 'failed' and v['error'] for v in result['checks'].values()))

    def test_partial_failure_preserves_successful_zero_detections(self):
        outputs = [subprocess.CompletedProcess([], 0, '', ''), subprocess.CompletedProcess([], 1, '', 'bad'),
                   subprocess.CompletedProcess([], 0, '', '')]
        with patch.object(take, 'run', side_effect=outputs):
            result = take.parse_video_diagnostics('ffmpeg', Path('/fixture'), .35)
        self.assertEqual(result['scene_change_times'], [])
        self.assertIsNone(result['black_ranges'])
        self.assertEqual(result['freeze_ranges'], [])
        self.assertEqual(result['status'], 'partial_or_failed')

    def test_failed_audio_detectors_are_explicit(self):
        with patch.object(take, 'run', side_effect=OSError('missing tool')):
            result = take.parse_audio_diagnostics('ffmpeg', Path('/fixture'))
        self.assertEqual(result['status'], 'partial_or_failed')
        self.assertIsNone(result['silence_ranges'])
        self.assertIsNone(result['mean_volume_db'])
        self.assertEqual(result['checks']['silence']['error'], 'missing tool')

    def test_nonfinite_ranges_fail_before_io(self):
        for value in ('nan:1', '0:inf', '-inf:1'):
            with self.assertRaises(ValueError):
                take.parse_dense_range(value)


class DenseFrameEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.ffmpeg = take.find_binary('ffmpeg')
            cls.ffprobe = take.find_binary('ffprobe')
        except FileNotFoundError as exc:
            raise unittest.SkipTest(str(exc))

    def fixture(self, root, timing='setpts=PTS'):
        source = root/'source.mkv'
        pixels = b''.join(bytes((i * 5, 0, 0)) * (64 * 36) for i in range(48))
        subprocess.run([self.ffmpeg, '-v', 'error', '-f', 'rawvideo', '-pixel_format', 'rgb24',
                        '-video_size', '64x36', '-framerate', '24', '-i', 'pipe:0', '-vf', timing,
                        '-fps_mode', 'vfr', '-c:v', 'ffv1', '-pix_fmt', 'bgr0', str(source)],
                       input=pixels, check=True, capture_output=True)
        frames = json.loads(subprocess.check_output([self.ffprobe, '-v', 'error', '-select_streams', 'v:0',
            '-show_frames', '-show_entries', 'frame=best_effort_timestamp_time', '-of', 'json', str(source)]))['frames']
        times = [float(f['best_effort_timestamp_time']) for f in frames]
        return source, [t - times[0] for t in times]

    def assert_correspondence(self, result, times):
        selected = result['source_timestamps_seconds']
        self.assertEqual(selected, sorted(set(selected)))
        self.assertEqual(len(selected), result['frame_count'])
        for filename, time in zip(result['frames'], selected):
            index = min(range(len(times)), key=lambda i: abs(times[i] - time))
            self.assertAlmostEqual(times[index], time, places=5)
            rgb = subprocess.check_output([self.ffmpeg, '-v', 'error', '-i', filename,
                '-vf', 'crop=1:1:240:80', '-f', 'rawvideo', '-pix_fmt', 'rgb24', 'pipe:1'])
            self.assertAlmostEqual(rgb[0], index * 5, delta=2)

    def test_repeated_range_cannot_reuse_old_frames(self):
        with tempfile.TemporaryDirectory(prefix='dense-regression-') as folder:
            root = Path(folder)
            source, times = self.fixture(root)
            first = take.dense_frame_burst(self.ffmpeg, source, root, 0, 1, 24, 120)
            second = take.dense_frame_burst(self.ffmpeg, source, root, 0, 1, 12, 120)
            self.assertEqual(first['frame_count'], 24)
            self.assertEqual(second['frame_count'], 12)
            self.assertNotEqual(Path(first['frames'][0]).parent, Path(second['frames'][0]).parent)
            self.assertTrue(set(first['frames']).isdisjoint(second['frames']))
            self.assertEqual(second['source_sha256'], take.sha256(source))
            self.assert_correspondence(second, times)

    def test_variable_rate_and_nonzero_start_keep_real_source_times(self):
        for timing, start, end in [
            ("setpts='if(lt(N,24),N,24+(N-24)*2)/(24*TB)'", 1.2, 2.8),
            ('setpts=PTS+2/TB', .25, 1.25),
        ]:
            with self.subTest(timing=timing), tempfile.TemporaryDirectory(prefix='dense-pts-') as folder:
                root = Path(folder)
                source, times = self.fixture(root, timing)
                result = take.dense_frame_burst(self.ffmpeg, source, root, start, end, 12, 120)
                self.assertTrue(all(start <= t < end for t in result['source_timestamps_seconds']))
                self.assert_correspondence(result, times)

    def test_oversampling_cannot_invent_unique_source_frames(self):
        with tempfile.TemporaryDirectory(prefix='dense-limit-') as folder:
            root = Path(folder)
            source, times = self.fixture(root)
            result = take.dense_frame_burst(self.ffmpeg, source, root, 0, .5, 60, 120)
            self.assertEqual(result['frame_count'], 12)
            self.assert_correspondence(result, times)

    def test_preflight_cli_uses_unique_manifests(self):
        with tempfile.TemporaryDirectory(prefix='preflight-cli-') as folder:
            root = Path(folder)
            source, _ = self.fixture(root)
            manifests = []
            for _ in range(2):
                result = subprocess.run([sys.executable, '-B', str(Path(take.__file__)), str(source),
                    '--out-dir', str(root/'evidence'), '--samples', '4', '--dense-range', '0:1', '--dense-fps', '12'],
                    capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                report = json.loads(result.stdout)
                self.assertEqual(report['status'], 'evidence_extracted')
                manifest = json.loads(Path(report['manifest']).read_text())
                self.assertEqual(manifest['source']['sha256'], take.sha256(source))
                self.assertEqual(manifest['diagnostics']['video']['status'], 'completed')
                self.assertEqual(manifest['artifacts']['dense_bursts'][0]['frame_count'], 12)
                manifests.append(report['manifest'])
            self.assertNotEqual(*manifests)

    def test_preflight_partial_failure_returns_non_success_and_manifest(self):
        with tempfile.TemporaryDirectory(prefix='preflight-partial-') as folder:
            root = Path(folder)
            source, _ = self.fixture(root)
            output = io.StringIO()
            with patch.object(sys, 'argv', ['take_preflight', str(source), '--out-dir', str(root/'evidence'), '--samples', '4']), \
                 patch.object(take, 'parse_video_diagnostics', return_value={'status': 'partial_or_failed', 'checks': {'scene': {'status': 'failed'}}}), \
                 contextlib.redirect_stdout(output):
                code = take.main()
            report = json.loads(output.getvalue())
            self.assertEqual(code, 2)
            self.assertFalse(report['ok'])
            self.assertEqual(report['status'], 'partial_or_failed')
            self.assertTrue(Path(report['manifest']).is_file())


if __name__ == '__main__':
    unittest.main()
