import unittest
import visual_contract as visual


class VisualValueRepairTests(unittest.TestCase):
    def valid(self):
        return {'production_method': 'AI composited custom drawing', 'final_appearance': 'outline-free ink collage',
                'appearance_family': 'other', 'space_and_perspective': 'planar overlaps',
                'motion_cadence': 'approved stepped motion', 'vfx_compositing': 'paper masks',
                'forbidden_drift': ['no glossy 3D'], 'family_specific_contract': 'no contour; tonal silhouette separation'}

    def test_custom_style_remains_open_and_outline_free(self):
        self.assertEqual(visual.validate_contract(self.valid()), [])

    def test_all_required_fields_reject_fake_descriptions(self):
        for key in self.valid():
            if key == 'appearance_family': continue
            for value in (False, 0, ' ', [None]):
                packet = self.valid(); packet[key] = value
                self.assertTrue(visual.validate_contract(packet), (key, value))

    def test_explicit_disabled_effect_is_a_described_decision(self):
        packet = self.valid(); packet['vfx_compositing'] = {'enabled': False, 'reason': 'no added effects in this shot'}
        self.assertEqual(visual.validate_contract(packet), [])


if __name__ == '__main__': unittest.main()
