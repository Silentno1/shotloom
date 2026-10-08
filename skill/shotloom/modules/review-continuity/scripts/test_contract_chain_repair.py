"""Synthetic dependency, version and timing regressions; no project mutations."""
import contextlib
import copy
import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import continuity_state as cs
import selection_manifest_check as selection
import take_preflight as take
import test_integrated_repair as fixtures


def update(i, tid=None, **kwargs):
    return {'shot_id': f'S{i}', 'take_id': tid or f'T{i}', 'sequence_index': i, 'status': 'accepted', **kwargs}


class DependencyRepairTests(unittest.TestCase):
    def chain(self):
        state = cs.apply_update(cs.initial('test'), update(1, canon_patch={'owner': 'A', 'clock': 'noon'}))
        state = cs.apply_update(state, update(2, canon_patch={'cup': 'broken'}))
        return cs.apply_update(state, update(1, 'replacement', canon_patch={'owner': 'B', 'clock': 'noon'}))

    def test_new_acceptance_cannot_skip_stale_predecessor(self):
        state = self.chain(); before = copy.deepcopy(state)
        with self.assertRaisesRegex(ValueError, 'unresolved predecessor'):
            cs.apply_update(state, update(3, canon_patch={'cup': 'bagged'}))
        self.assertEqual(state, before)

    def test_actual_predecessor_rereview_reopens_dependent_acceptance(self):
        state = cs.apply_update(self.chain(), update(2, 'reviewed', canon_patch={'cup': 'broken'}))
        state = cs.apply_update(state, update(3, canon_patch={'cup': 'bagged'}))
        self.assertEqual(state['current_state']['cup'], 'bagged')
        self.assertEqual(state['stale_takes'], {})

    def test_candidate_still_recordable_but_does_not_propagate(self):
        state = cs.apply_update(self.chain(), update(3, status='candidate', canon_effect='no-change'))
        self.assertIsNone(state['shots']['S3']['active_take'])
        self.assertIn('S2', state['stale_takes'])

    def test_independent_paths_need_review_and_leave_other_take_stale(self):
        state = self.chain()
        packet = update(4, depends_on=['state.clock'])
        with self.assertRaises(ValueError): cs.apply_update(state, packet)
        packet['stale_dependency_review'] = {'shot_ids': ['S2'], 'source': 'SYNTHETIC scoped dependency review'}
        result = cs.apply_update(state, packet)
        self.assertIn('S2', result['stale_takes']); self.assertNotIn('S4', result['stale_takes'])

    def test_overlapping_path_cannot_bypass_unresolved_writes(self):
        for path in ('state.cup', 'state.cup.owner'):
            packet = update(3, depends_on=[path], stale_dependency_review={'shot_ids': ['S2'], 'source': 'test'})
            with self.assertRaisesRegex(ValueError, 'overlap'): cs.apply_update(self.chain(), packet)

    def test_registry_domains_are_also_protected(self):
        state = cs.apply_update(cs.initial('test'), update(1, canon_patch={'owner': 'A'}))
        state = cs.apply_update(state, update(2, registry_patch={'props': {'cup': 'v2'}}))
        state = cs.apply_update(state, update(1, 'replacement', canon_patch={'owner': 'B'}))
        with self.assertRaisesRegex(ValueError, 'overlap'):
            cs.apply_update(state, update(3, depends_on=['registry.props.cup'], stale_dependency_review={'shot_ids': ['S2'], 'source': 'test'}))

    def test_exact_baseline_restores_structural_validity_without_new_review(self):
        state = self.chain(); original = copy.deepcopy(state['shots']['S2']['versions'])
        state = cs.apply_update(state, update(1, 'restored', canon_patch={'owner': 'A', 'clock': 'noon'}))
        self.assertNotIn('S2', state['stale_takes'])
        self.assertEqual(state['shots']['S2']['versions'], original)

    def test_chronology_restore_does_not_clear_explicit_invalidation(self):
        state = self.chain()
        for order in ({'S1': 2, 'S2': 1}, {'S1': 1, 'S2': 2}):
            state = cs.revise_state(state, {'expected_state_hash': cs.value_hash(state), 'reason': 'test', 'approval_source': 'fixture', 'sequence_indices': order})
        self.assertEqual(set(state['stale_takes']), {'S1', 'S2'})

    def test_version_and_usable_range_are_preserved(self):
        packet = update(1, source_file='/synthetic.mp4', source_sha256='a' * 64, usable_range=[0, 2])
        result = cs.apply_update(cs.initial('test'), packet)['shots']['S1']['versions'][0]
        self.assertEqual(result['source_sha256'], 'a' * 64)
        self.assertEqual(result['usable_range'], [0, 2])
        self.assertEqual(result['source_binding_status'], 'declared_hash_bound')

    def test_bad_ranges_missing_hash_and_ignored_context_are_rejected(self):
        for extra in ({'usable_range': [4, 2]}, {'usable_range': [0, False]}, {'usable_range': [0, float('nan')]}, {'source_file': '/a.mp4'}, {'source_file': '/a.mp4', 'source_sha256': 'bad'}, {'context_id': 'dream'}):
            with self.subTest(extra=extra), self.assertRaises(ValueError):
                cs.apply_update(cs.initial('test'), update(1, **extra))

    def test_legacy_source_record_is_not_backfilled(self):
        state = cs.apply_update(cs.initial('test'), update(1))
        record = state['shots']['S1']['versions'][0]
        record['source_file'] = '/legacy.mp4'; record.pop('source_sha256'); record.pop('source_binding_status')
        self.assertEqual(cs.validate_state(state), [])
        self.assertNotIn('source_sha256', cs.recompute(state)['shots']['S1']['versions'][0])

    def test_missing_path_is_not_equal_to_real_sentinel_shaped_value(self):
        state = cs.apply_update(cs.initial('test'), update(1, canon_effect='no-change'))
        state = cs.apply_update(state, update(2, depends_on=['state.props.key']))
        state = cs.apply_update(state, update(1, 'new', canon_patch={'props': {'key': {'__missing__': True}}}))
        self.assertIn('S2', state['stale_takes'])

    def test_presence_encoding_does_not_collide_with_wrapped_user_values(self):
        absent = cs.accepted_against({}, {}, ['state.key'])
        for value in ({'__missing__': True}, {'exists': False}, None, False, 0):
            present = cs.accepted_against({}, {'key': value}, ['state.key'])
            self.assertNotEqual(absent['dependency_hash'], present['dependency_hash'])

    def test_legacy_ambiguous_path_needs_review_without_rewriting_record(self):
        state = cs.apply_update(cs.initial('test'), update(1))
        state = cs.apply_update(state, update(2, depends_on=['state.key']))
        record = state['shots']['S2']['versions'][0]
        record['accepted_against'] = {'mode': 'paths', 'depends_on': ['state.key'], 'dependency_hash': cs.value_hash({'state.key': {'__missing__': True}})}
        original = copy.deepcopy(record)
        cs.recompute(state)
        self.assertIn('S2', state['stale_takes'])
        self.assertEqual(state['shots']['S2']['versions'][0], original)

    def test_unambiguous_legacy_path_stays_valid_in_original_encoding(self):
        state = cs.apply_update(cs.initial('test'), update(1, canon_patch={'key': 'A'}))
        state = cs.apply_update(state, update(2, depends_on=['state.key']))
        record = state['shots']['S2']['versions'][0]
        record['accepted_against'] = {'mode': 'paths', 'depends_on': ['state.key'], 'dependency_hash': cs.value_hash({'state.key': 'A'})}
        original = copy.deepcopy(record)
        cs.recompute(state)
        self.assertNotIn('S2', state['stale_takes'])
        self.assertEqual(record, original)


class TimingRepairTests(unittest.TestCase):
    def packet(self): return fixtures.SelectionTests().packet()

    def test_normal_speed_rejects_stretch(self):
        packet = self.packet(); packet['fragments'][0].update(source_in=4, source_out=8, timeline_in=0, timeline_out=40)
        self.assertFalse(selection.check(packet)['ok'])
        packet['fragments'][0]['timeline_out'] = 4
        self.assertTrue(selection.check(packet)['ok'])

    def test_constant_speed_and_invalid_speeds(self):
        packet = self.packet(); fragment = packet['fragments'][0]
        fragment.update(source_in=4, source_out=8, timeline_in=0, timeline_out=2, time_mapping={'kind': 'constant', 'speed': 2})
        self.assertTrue(selection.check(packet)['ok'])
        for speed in (0, False, -2, float('nan')):
            fragment['time_mapping']['speed'] = speed
            self.assertFalse(selection.check(packet)['ok'])

    def test_external_map_binds_ranges_and_hash_not_media_truth(self):
        packet = self.packet(); fragment = packet['fragments'][0]
        fragment['time_mapping'] = {'kind': 'map', 'reference': 'synthetic map', 'sha256': 'c' * 64, 'source_range': [1, 2], 'timeline_range': [0, 1]}
        self.assertTrue(selection.check(packet)['ok'])
        fragment['time_mapping']['source_range'] = [1, 3]
        self.assertFalse(selection.check(packet)['ok'])

    def test_legacy_retime_reference_is_not_a_timing_pass_or_story_event(self):
        packet = self.packet(); packet['fragments'][0]['time_mapping'] = 'custom ramp in editor'
        result = selection.check(packet)
        self.assertEqual(result['status'], 'unverified')
        self.assertTrue(result['unverified_timing']); self.assertEqual(result['unresolved_event_ids'], [])


class SourceMutationTests(unittest.TestCase):
    def test_changed_source_during_preflight_cannot_publish_a_manifest(self):
        for changed in (False, True):
            with self.subTest(changed=changed), tempfile.TemporaryDirectory(prefix='preflight-source-binding-') as folder:
                root = Path(folder); source = root / 'source.wav'; source.write_bytes(b'old fixture')
                original_hash = take.sha256(source)
                def diagnostic(*args):
                    if changed: source.write_bytes(b'new fixture')
                    return {'status': 'completed'}
                with patch('sys.argv', ['take_preflight', str(source), '--out-dir', str(root / 'out')]), patch.object(take, 'find_binary', return_value='fixture'), patch.object(take, 'probe', return_value={}), patch.object(take, 'metadata', return_value={'video': None, 'audio': True, 'duration_seconds': 1}), patch.object(take, 'parse_audio_diagnostics', side_effect=diagnostic), patch.object(take, 'audio_spectrogram'), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                    result = take.main()
                manifests = list(root.rglob('review-manifest.json'))
                self.assertEqual(result, 2 if changed else 0)
                self.assertEqual(len(manifests), 0 if changed else 1)
                if manifests: self.assertEqual(json.loads(manifests[0].read_text())['source']['sha256'], original_hash)

    def test_sampled_helper_also_rejects_changed_source(self):
        with tempfile.TemporaryDirectory(prefix='dense-source-binding-') as folder:
            root = Path(folder); source = root / 'source.mp4'; source.write_bytes(b'old')
            def extract(command, **kwargs):
                Path(command[-1].replace('%04d', '0001')).write_bytes(b'frame')
                source.write_bytes(b'changed')
                return SimpleNamespace(stderr='n: 0 pts: 0 pts_time:0', stdout='')
            with patch.object(take, 'run', side_effect=extract), self.assertRaises(ValueError):
                take.dense_frame_burst('fixture', source, root, 0, 1, 1, 2)


if __name__ == '__main__': unittest.main()
