"""Behavioral regressions for sound/adapter/source-lock integration and H3 parsing."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from sound_contract_check import check_sound_contract, validate_sound_contract
from source_lock_check import validate_source_lock
from test_director_gate import production_fields
from prompt_structure_check import check_h3, normalize_manifest


class AuditRepairTests(unittest.TestCase):
    def contract(self, ownership='native_required'):
        native = ownership == 'native_required'
        event = {'id': 'line', 'category': 'dialogue', 'continuity_scope': 'shot',
                 'audible_ownership': ownership, 'selected_for_generation': native,
                 'audible_prompt_markers': ['等一下。']}
        if ownership == 'post_only':
            event['post_handoff'] = 'approved dubbing'
        return {'sound_events': [event], 'compiled_generation_audio_ids': ['line'] if native else [],
                'post_handoff_ids': ['line'] if ownership == 'post_only' else []}

    def prompt(self, timeline, sound='Footsteps.', reference=False):
        prefix = 'subject_definitions: A person.\nsummary: Reference.\nretention_analysis: Identity.\n' if reference else ''
        key = 'detailed_description' if reference else 'integrated_multimodal_description'
        return f'{prefix}{key}: [Shot 1] {timeline}\noverall_soundscape: {sound}\nnon_diegetic_music: N/A'

    def test_native_dialogue_in_both_h3_timeline_modes(self):
        for ref in (False, True):
            result = check_sound_contract(self.contract(), self.prompt('(S1) says <d>[Chinese] 等一下。</d>', reference=ref))
            self.assertTrue(result['ok'], result)
            self.assertEqual(result['status'], 'passed_scoped_checks')

    def test_post_dialogue_in_tagged_speech_is_leak(self):
        result = check_sound_contract(self.contract('post_only'), self.prompt('(S1) says <d>[Chinese] 等一下。</d>'))
        self.assertEqual(result['status'], 'failed')
        self.assertTrue(any('leaked' in e for e in result['errors']))

    def test_post_untagged_timeline_is_not_silent_pass(self):
        result = check_sound_contract(self.contract('post_only'), self.prompt('等一下。 is heard loudly.'))
        self.assertEqual(result['status'], 'unverified')
        self.assertFalse(result['ok'])

    def test_silent_mouth_cue_not_misclassified_as_native_speech(self):
        result = check_sound_contract(self.contract('post_only'), self.prompt('Silently mouths 等一下。 for later dubbing.'))
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['status'], 'unverified')

    def test_natural_language_and_unknown_schemas_never_false_pass(self):
        for text in ('角色大声说等一下。', '角色无声地做口型：等一下。', 'overall_soundscape: 等一下。'):
            result = check_sound_contract(self.contract('post_only'), text)
            self.assertEqual(result['status'], 'unverified')
            self.assertFalse(result['ok'])

    def test_negative_sound_clause_needs_review_not_leak_rejection(self):
        result = check_sound_contract(self.contract('post_only'), self.prompt('Waits.', 'Do not generate 等一下。'))
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['status'], 'unverified')

    def test_guide_track_does_not_get_native_master_verdict(self):
        data = self.contract('post_only')
        data['sound_events'][0]['picture_sync_strategy'] = 'guide_track_not_for_master'
        result = check_sound_contract(data, self.prompt('(S1) says <d>[Chinese] 等一下。</d>'))
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['status'], 'unverified')

    def test_missing_required_literal_is_error(self):
        result = check_sound_contract(self.contract(), self.prompt('Waits.'))
        self.assertEqual(result['status'], 'failed')

    def test_optional_unselected_audio_leak_is_rejected(self):
        data = self.contract('native_optional')
        self.assertTrue(check_sound_contract(data, self.prompt('Waits.', '等一下。'))['errors'])

    def test_no_markers_discloses_unverified_coverage(self):
        data = self.contract()
        data['sound_events'][0].pop('audible_prompt_markers')
        self.assertEqual(check_sound_contract(data, self.prompt('Waits.'))['status'], 'unverified')

    def test_invalid_marker_types_are_structured_errors(self):
        for markers in (None, 'word', {}, [None]):
            data = self.contract()
            data['sound_events'][0]['audible_prompt_markers'] = markers
            self.assertTrue(check_sound_contract(data, self.prompt('Waits.'))['errors'])

    def test_source_lock_image_and_video_applicability(self):
        data = {**production_fields(), 'media_type': 'image', 'production_level': 'concept',
                'authority_sources_and_versions': ['approved fixture'], 'appearance_family': 'photographic',
                'required_endpoint': 'portrait', 'review_criteria': ['face'], 'reference_manifest': []}
        self.assertEqual(validate_source_lock(data), [])
        data['media_type'] = 'video'
        self.assertTrue(validate_source_lock(data))
        data['sound_ownership_plan'] = self.contract()
        self.assertEqual(validate_source_lock(data), [])
        result = check_sound_contract(data['sound_ownership_plan'], self.prompt('(S1) says <d>[Chinese] 等一下。</d>'))
        self.assertTrue(result['ok'])
        data['media_type'] = 'image'
        self.assertTrue(any('not applicable' in e for e in validate_source_lock(data)))

    def test_explicit_empty_image_sound_and_legacy_video(self):
        data = {**production_fields(), 'media_type': 'image', 'production_level': 'concept', 'authority_sources_and_versions': ['fixture'],
                'appearance_family': 'photographic', 'required_endpoint': 'portrait', 'review_criteria': ['face'],
                'sound_ownership_plan': {'sound_events': [], 'compiled_generation_audio_ids': [], 'post_handoff_ids': []}}
        self.assertEqual(validate_source_lock(data), [])
        data.pop('media_type')
        self.assertEqual(validate_source_lock(data), [])

    def test_h3_timestamp_full_token_validation(self):
        for value, valid in [('00:02.500', True), ('00:02.5000', False), ('00:02.5', False),
                             ('00:02.500garbage', False), ('00:60.000', False), ('1:02.500', False)]:
            text = self.prompt(f'Wait. [Shot 2] At {value}, turn.')
            errors, _ = check_h3(text, 'T2VA', 7, {})
            self.assertEqual(not errors, valid, (value, errors))

    def test_h3_malformed_input_shapes_do_not_crash(self):
        for manifest in (None, [], {'reference_videos': [None]}, {'reference_images': 'bad'}, {'first_frames': True}):
            errors, _ = check_h3(self.prompt('Wait.'), 'T2VA', 7, manifest)
            self.assertTrue(errors)
        for duration in (True, None, '7', float('nan'), float('inf')):
            self.assertTrue(check_h3(self.prompt('Wait.'), 'T2VA', duration, {})[0])

    def test_unknown_coverage_has_distinct_cli_exit(self):
        with tempfile.TemporaryDirectory() as folder:
            contract, prompt = Path(folder)/'contract.json', Path(folder)/'prompt.txt'
            contract.write_text(json.dumps(self.contract('post_only')))
            prompt.write_text('等一下。')
            result = subprocess.run([sys.executable, '-B', str(Path(__file__).with_name('sound_contract_check.py')),
                                     str(contract), '--prompt', str(prompt)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 3)
            self.assertEqual(json.loads(result.stdout)['status'], 'unverified')


if __name__ == '__main__':
    unittest.main()
