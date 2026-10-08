import copy
import hashlib
from pathlib import Path
import tempfile
import unittest
from delivery_check import validate_manifest


class DeliveryRepairTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.master = Path(self.directory.name)/'fixture.bin'
        self.master.write_bytes(b'synthetic-manifest-fixture-not-media')
        self.data = {'platform': 'fixture', 'production_level': 'formal', 'verification_date': '2026-09-04',
            'verification_source': 'fixture observed rules', 'master_file': str(self.master),
            'master_sha256': hashlib.sha256(self.master.read_bytes()).hexdigest(),
            'technical_specs': {'duration_seconds': 10, 'width': 1920, 'height': 1080, 'frame_rate': 24,
                                'container': 'mp4', 'video_codec': 'h264', 'audio': 'none'},
            'qc_result': {'status': 'pass', 'checks': [{'name': 'picture', 'status': 'pass'}]}}

    def test_baseline_and_rational_frame_rates(self):
        for rate in (24, 23.976, '30000/1001', '24', '23.976'):
            self.data['technical_specs']['frame_rate'] = rate
            self.assertEqual(validate_manifest(self.data), [])

    def test_invalid_numeric_technical_values(self):
        for key, values in {'duration_seconds': [-1, 0, True, float('nan'), float('inf')],
                            'width': [-1, 0, True, 1.2], 'height': [-1, None],
                            'frame_rate': ['0/0', '24/0', 'NaN', '-24', 'oops', 0, True, float('inf')]}.items():
            for value in values:
                data = copy.deepcopy(self.data)
                data['technical_specs'][key] = value
                self.assertTrue(validate_manifest(data), (key, value))

    def test_equal_category_with_observed_option_is_allowed(self):
        self.data.update(production_method='3D动画', upload_category='3D动画', category_options_observed=['3D动画'])
        self.assertEqual(validate_manifest(self.data), [])

    def test_exception_cannot_hide_under_pass(self):
        self.data['qc_result']['checks'].append({'name': 'sound', 'status': 'accepted_exception'})
        self.assertTrue(validate_manifest(self.data))
        self.data['qc_result']['status'] = 'accepted_exception'
        self.assertTrue(validate_manifest(self.data))

    def exception_fixture(self):
        qc = self.data['qc_result']
        qc['status'] = 'accepted_exception'
        qc['checks'].append({'name': 'sound', 'status': 'accepted_exception'})
        qc['exceptions'] = [{'check': 'sound', 'reason': 'approved fixture reason',
                             'scope': 'specific fixture range', 'acceptance_source': 'explicit approval fixture'}]
        return qc

    def test_documented_exception_passes_scoped_check(self):
        self.exception_fixture()
        self.assertEqual(validate_manifest(self.data), [])

    def test_exception_requires_matching_check_and_acceptance(self):
        qc = self.exception_fixture()
        for key in ('check', 'reason', 'scope', 'acceptance_source'):
            data = copy.deepcopy(self.data)
            data['qc_result']['exceptions'][0].pop(key)
            self.assertTrue(validate_manifest(data), key)
        qc['exceptions'][0]['check'] = 'unrelated'
        self.assertTrue(validate_manifest(self.data))

    def test_duplicate_checks_or_orphan_exceptions_fail(self):
        qc = self.exception_fixture()
        qc['checks'].append({'name': 'sound', 'status': 'pass'})
        self.assertTrue(validate_manifest(self.data))


if __name__ == '__main__':
    unittest.main()
