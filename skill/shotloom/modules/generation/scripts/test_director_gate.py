"""Exercise the real source-lock entry, not only the standalone style validator."""
import importlib.util
import sys
import unittest
from pathlib import Path

import source_lock_check as source

DIRECTOR_SCRIPTS = Path(__file__).resolve().parents[2] / 'director/scripts'
sys.path.insert(0, str(DIRECTOR_SCRIPTS))
from test_director_style import production_packet


def production_fields():
    return production_packet()


class GenerationDirectorGateTests(unittest.TestCase):
    def packet(self):
        return {**production_fields(), 'media_type': 'video', 'production_level': 'formal',
                'authority_sources_and_versions': ['fixture-v1'], 'appearance_family': 'standard_3d',
                'required_endpoint': 'fixture endpoint', 'review_criteria': ['fixture criteria'], 'reference_manifest': [],
                'sound_ownership_plan': {'sound_events': [], 'compiled_generation_audio_ids': [], 'post_handoff_ids': []}}

    def test_real_entry_accepts_current_selection(self):
        self.assertEqual(source.validate_source_lock(self.packet()), [])

    def test_real_entry_rejects_missing_selection(self):
        data = self.packet(); del data['director_style_lock']
        self.assertTrue(any('director_style' in e for e in source.validate_source_lock(data)))

    def test_real_entry_rejects_stale_selection(self):
        data = self.packet(); data['director_style_ref']['version'] = 'old'
        self.assertTrue(any('director_style' in e for e in source.validate_source_lock(data)))

    def test_concept_does_not_silently_bypass(self):
        data = self.packet(); data['production_level'] = 'concept'; del data['director_style_lock']
        self.assertTrue(source.validate_source_lock(data))

    def test_explicit_exploration_is_allowed_not_promoted(self):
        data = self.packet(); del data['director_style_lock']
        data.update(workflow_scope='selection_exploration', production_level='concept',
                    exploration={'purpose': 'selection test', 'not_for_production': True})
        self.assertEqual(source.validate_source_lock(data), [])
        data['production_level'] = 'formal'; self.assertTrue(source.validate_source_lock(data))

    def test_picture_and_audio_cannot_skip_gate(self):
        for media in ('image', 'video', 'audio'):
            data = self.packet(); data['media_type'] = media; del data['director_style_lock']
            self.assertTrue(any('director_style' in e for e in source.validate_source_lock(data)))


if __name__ == '__main__':
    unittest.main()
