#!/usr/bin/env python3
import unittest
import hashlib
from pathlib import Path
import struct
import subprocess
import tempfile
import zlib
from reference_image_preflight import check_geometry, find_ffprobe, inspect_image


class ReferenceImageGeometryTests(unittest.TestCase):
    def test_outside_landscape_and_portrait(self):
        for size in [(2172, 724), (300, 1000)]:
            with self.subTest(size=size):
                self.assertTrue(check_geometry(*size, 0.4, 2.5))

    def test_inclusive_edges_and_regular_reference(self):
        for size in [(400, 1000), (2500, 1000), (1536, 1024)]:
            with self.subTest(size=size):
                self.assertEqual(check_geometry(*size, 0.4, 2.5), [])

    def test_bounds_are_not_global_model_defaults(self):
        self.assertEqual(check_geometry(2172, 724, 0.2, 4.0), [])

    def test_invalid_bounds_fail(self):
        for bounds in [(0, 2.5), (3, 2), (float('nan'), 2), (0.4, float('inf'))]:
            with self.subTest(bounds=bounds), self.assertRaises(ValueError):
                check_geometry(100, 100, *bounds)

    def test_invalid_dimensions_fail(self):
        for size in [(0, 100), (100, -1), (True, 100), (100.5, 100)]:
            with self.subTest(size=size), self.assertRaises(ValueError):
                check_geometry(*size, 0.4, 2.5)


class ReferenceImageFileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.ffprobe = find_ffprobe()
        except FileNotFoundError as exc:
            raise unittest.SkipTest(str(exc))

    def test_actual_file_dimensions_hash_and_rejection(self):
        def chunk(kind, payload):
            return struct.pack('>I', len(payload)) + kind + payload + struct.pack('>I', zlib.crc32(kind + payload))

        with tempfile.TemporaryDirectory(prefix='reference-geometry-test-') as directory:
            for width, height, accepted in [(30, 10, False), (15, 10, True)]:
                # Deliberately misleading filename: only actual pixels count.
                path = Path(directory) / '1536x1024.png'
                png = (b'\x89PNG\r\n\x1a\n'
                       + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0))
                       + chunk(b'IDAT', zlib.compress((b'\x00' + b'\x00\x00\x00' * width) * height))
                       + chunk(b'IEND', b''))
                path.write_bytes(png)
                result = inspect_image(path, 0.4, 2.5, self.ffprobe)
                self.assertEqual((result['width'], result['height']), (width, height))
                self.assertEqual(result['sha256'], hashlib.sha256(png).hexdigest())
                self.assertEqual(not result['errors'], accepted)

    def test_missing_and_unreadable_files_do_not_pass(self):
        with tempfile.TemporaryDirectory(prefix='reference-geometry-test-') as directory:
            path = Path(directory) / 'missing.png'
            with self.assertRaises(ValueError):
                inspect_image(path, 0.4, 2.5, self.ffprobe)
            path.write_bytes(b'not an image')
            with self.assertRaises((ValueError, subprocess.CalledProcessError)):
                inspect_image(path, 0.4, 2.5, self.ffprobe)


if __name__ == '__main__':
    unittest.main()
