import unittest
from visual_contract import validate_contract, COMMON_REQUIRED, FAMILY_REQUIRED


class VisualApplicabilityTests(unittest.TestCase):
    def fixture(self, family='standard_3d'):
        data = {k: 'specified' for k in COMMON_REQUIRED | FAMILY_REQUIRED[family]}
        data['appearance_family'] = family
        return data

    def test_independently_evidenced_equal_labels_are_legal(self):
        data = self.fixture()
        data.update(production_method='3D动画', upload_category='3D动画', upload_platform='fixture',
                    category_options_observed=['3D动画'], category_verification_source='observed interface fixture')
        self.assertEqual(validate_contract(data), [])

    def test_different_labels_without_evidence_do_not_pass(self):
        data = self.fixture()
        data.update(production_method='hybrid', upload_category='animation', upload_platform='fixture')
        self.assertTrue(validate_contract(data))

    def test_static_contracts_do_not_require_temporal_fields(self):
        for family in FAMILY_REQUIRED:
            data = self.fixture(family)
            data['media_type'] = 'image'
            for key in ('motion_cadence', 'replacement_cadence', 'interpolation_and_timing',
                        'deformation', 'rig_and_deformation', 'vfx_compositing'):
                data.pop(key, None)
            self.assertEqual(validate_contract(data), [], family)
            data['media_type'] = 'video'
            self.assertTrue(validate_contract(data), family)

    def test_static_vfx_explicitly_used_still_needs_contract(self):
        data = self.fixture()
        data.update(media_type='image', vfx_present=True)
        data.pop('vfx_compositing')
        self.assertTrue(any('vfx_compositing' in e for e in validate_contract(data)))

    def test_unknown_family_or_media_type_is_error(self):
        for key, value in [('media_type', 'anything'), ('appearance_family', [])]:
            data = self.fixture()
            data[key] = value
            self.assertTrue(validate_contract(data))


if __name__ == '__main__':
    unittest.main()
