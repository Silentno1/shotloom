"""Behavioral regressions. All story, authorization and source values are SYNTHETIC."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import director_style as gate


def production_packet():
    authority = {'project_id': 'TEST-ONLY', 'work_scope': 'complete fixture', 'script_version': 'fixture-v1'}
    lock = {
        'schema_version': 1, 'id': 'TEST-STYLE', 'version': '1', 'status': 'selected',
        'authority': dict(authority),
        'lead': {'profile_id': 'alfred-hitchcock', 'name': 'Alfred Hitchcock',
                 'reference_scope': [{'work': 'SYNTHETIC reference', 'scope': 'fixture sequence', 'evidence_ids': ['E1']}]},
        'authorization': {'mode': 'user_approved', 'source': 'SYNTHETIC approval, not a real user decision', 'scope': 'fixture'},
        'fit_basis': {'reading_scope': 'complete_authoritative_scope', 'rationale': 'test information design',
                      'script_evidence': ['fixture scene 1'], 'countercase': 'no suspense device in unrelated scene'},
        'evidence': [{'id': 'E1', 'source': 'SYNTHETIC observation', 'scope': 'fixture scene',
                      'supported_claim': 'test claim only', 'checked_at': '2026-10-01', 'kind': 'work_observation'}],
        'adopted_methods': {k: 'fixture scoped method: ' + k for k in gate.METHODS},
        'excluded_methods': ['do not force suspense on every beat'], 'preserved_locks': ['fixture script and look'],
        'variation_policy': 'allow local intensity changes, retain information policy',
        'review_criteria': ['observable information access, not number of POV shots']}
    return {'workflow_scope': 'production', 'current_authority': authority, 'director_style_lock': lock,
            'director_style_ref': {'id': lock['id'], 'version': lock['version'], 'sha256': gate.fingerprint(lock)}}


def rebind(packet):
    packet['director_style_ref']['sha256'] = gate.fingerprint(packet['director_style_lock'])


class DirectorStyleTests(unittest.TestCase):
    def test_all_five_stages_accept_valid_record(self):
        for stage in gate.STAGES:
            self.assertEqual(gate.validate_handoff(production_packet(), stage), [])

    def test_all_five_stages_reject_no_selection(self):
        for stage in gate.STAGES:
            self.assertTrue(gate.validate_handoff({'production_level': 'formal'}, stage))

    def test_concept_label_alone_is_not_an_exemption(self):
        self.assertTrue(gate.validate_handoff({'production_level': 'concept'}))

    def test_exploration_can_precede_selection(self):
        data = {'workflow_scope': 'selection_exploration', 'production_level': 'concept',
                'exploration': {'purpose': 'compare methods', 'not_for_production': True}}
        for stage in gate.STAGES:
            self.assertEqual(gate.validate_handoff(data, stage), [])

    def test_exploration_cannot_label_formal_or_continuity(self):
        for level in ('formal', 'continuity'):
            self.assertTrue(gate.validate_handoff({'workflow_scope': 'selection_exploration',
                'production_level': level, 'exploration': {'purpose': 'test', 'not_for_production': True}}))

    def test_diagnostic_cannot_be_submitted_as_production(self):
        self.assertTrue(gate.validate_handoff({'workflow_scope': 'diagnostic'}))

    def test_bare_name_and_draft_fail(self):
        self.assertTrue(gate.validate_lock({'lead': {'name': 'a famous director'}}))
        data = production_packet(); data['director_style_lock']['status'] = 'draft'; rebind(data)
        self.assertTrue(gate.validate_handoff(data))

    def test_authorized_selection_modes(self):
        for mode in ('user_selected', 'user_approved', 'ai_selection_delegated'):
            data = production_packet(); data['director_style_lock']['authorization']['mode'] = mode; rebind(data)
            self.assertEqual(gate.validate_handoff(data), [])

    def test_score_or_default_is_not_authorization(self):
        for mode in ('auto_locked', 'highest_score', 'default', None, []):
            data = production_packet(); data['director_style_lock']['authorization']['mode'] = mode; rebind(data)
            self.assertTrue(gate.validate_handoff(data))

    def test_excerpt_or_tags_do_not_establish_whole_work_method(self):
        data = production_packet(); data['director_style_lock']['fit_basis']['reading_scope'] = 'excerpts'; rebind(data)
        self.assertTrue(gate.validate_handoff(data))

    def test_wrong_project_scope_or_script_is_stale(self):
        for key in gate.AUTHORITY:
            data = production_packet(); data['current_authority'][key] = 'different'
            self.assertTrue(gate.validate_handoff(data))

    def test_old_artifact_id_version_and_content_fail(self):
        for key in ('id', 'version', 'sha256'):
            data = production_packet(); data['director_style_ref'][key] = 'stale'
            self.assertTrue(gate.validate_handoff(data))

    def test_changed_method_without_rebinding_fails(self):
        data = production_packet(); data['director_style_lock']['adopted_methods']['camera'] = 'changed'
        self.assertTrue(gate.validate_handoff(data))

    def test_replacement_needs_explicit_change_authority(self):
        data = production_packet(); lock = data['director_style_lock']; lock['supersedes'] = {'id': 'old', 'version': '1'}
        rebind(data); self.assertTrue(gate.validate_handoff(data))
        lock['change_authorization_source'] = 'SYNTHETIC change approval'; rebind(data)
        self.assertEqual(gate.validate_handoff(data), [])

    def test_retired_false_arcane_duo_is_not_silently_migrated(self):
        data = production_packet(); data['director_style_lock']['lead']['profile_id'] = 'pascal-charrue-arnaud-delord'; rebind(data)
        self.assertTrue(gate.validate_handoff(data))

    def test_replacement_cannot_reuse_its_own_version(self):
        data = production_packet(); lock = data['director_style_lock']
        lock.update(supersedes={'id': lock['id'], 'version': lock['version']},
                    change_authorization_source='SYNTHETIC change')
        rebind(data); self.assertTrue(gate.validate_handoff(data))

    def test_capability_routes_are_reachable_from_all_five_entries(self):
        # Wiring evidence only; the behavior cases above establish gate semantics.
        root = Path(gate.__file__).resolve().parents[2]
        skills = ('director', 'visual-design', 'generation',
                  'edit-delivery', 'review-continuity')
        for skill in skills:
            entry = (root / skill / 'WORKFLOW.md').read_text(encoding='utf-8')
            self.assertIn('director-selection.md', entry, skill)
        doc = (root / 'director/references/director-selection.md').read_text(encoding='utf-8')
        self.assertIn('director-profiles.json', doc)
        self.assertTrue((root / 'director/references/director-profiles.json').is_file())
        entry = (root / 'director/WORKFLOW.md').read_text(encoding='utf-8')
        self.assertNotIn('does not require one named filmmaker', entry)

    def test_catalog_does_not_silently_replace_a_promised_director(self):
        expected = '''david-fincher stanley-kubrick denis-villeneuve alfred-hitchcock steven-spielberg
        bong-joon-ho sidney-lumet asghar-farhadi yasujiro-ozu hirokazu-koreeda edward-yang lee-changdong
        wong-karwai terrence-malick david-lynch alfonso-cuaron akira-kurosawa martin-scorsese george-miller
        john-woo gareth-evans edgar-wright stephen-chow wes-anderson jordan-peele ari-aster park-chanwook
        hayao-miyazaki satoshi-kon mamoru-oshii arcane-fortiche christopher-nolan james-cameron zhang-yimou'''
        self.assertTrue(set(expected.split()).issubset({p['id'] for p in gate.catalog()['profiles']}))

    def test_expansion_has_all_new_identities_and_no_duplicates(self):
        expected = '''nora-ephron nancy-meyers richard-linklater greta-gerwig celine-sciamma
        kong-sheng zheng-xiaolong yang-yang jiang-wei xin-shuang kang-honglei kathryn-bigelow
        sam-mendes ridley-scott tsui-hark peter-jackson james-wan john-carpenter david-cronenberg
        robert-eggers ryan-coogler damien-chazelle brad-bird pete-docter makoto-shinkai
        naoko-yamada james-burrows paul-greengrass robert-zemeckis ang-lee'''
        profiles = {p['id']: p for p in gate.catalog()['profiles']}
        self.assertTrue(set(expected.split()).issubset(profiles))
        for pid in expected.split():
            p = profiles[pid]
            self.assertTrue(p['credit_boundaries'])
            for e in p['evidence_notes']:
                self.assertIn(e['kind'], ('creator_account', 'collaborator_account', 'production_primary'))
                self.assertTrue(e['supported_claim'])
                self.assertTrue(e['limits'])
                self.assertIn(e['read_basis'], ('retrieved_body_or_transcript_passage', 'retrieved_interview_excerpt'))

    def test_external_verified_reference_is_allowed(self):
        data = production_packet(); data['director_style_lock']['lead']['profile_id'] = 'external:fixture-director'; rebind(data)
        self.assertEqual(gate.validate_handoff(data), [])

    def test_unknown_profile_and_dangling_evidence_fail(self):
        for mutate in ('profile', 'evidence'):
            data = production_packet()
            if mutate == 'profile':
                data['director_style_lock']['lead']['profile_id'] = 'not-a-profile'
            else:
                data['director_style_lock']['lead']['reference_scope'][0]['evidence_ids'] = ['missing']
            rebind(data); self.assertTrue(gate.validate_handoff(data))

    def test_empty_required_parts_fail_even_with_matching_hash(self):
        for key in ('authorization', 'fit_basis', 'evidence', 'lead', 'adopted_methods',
                    'excluded_methods', 'preserved_locks', 'review_criteria', 'authority'):
            data = production_packet(); data['director_style_lock'][key] = {}; rebind(data)
            self.assertTrue(gate.validate_handoff(data), key)

    def test_malformed_nested_values_report_not_crash(self):
        for value in (None, [], {}, True, 3, ''):
            for key in ('lead', 'evidence', 'fit_basis', 'authorization', 'adopted_methods'):
                data = production_packet(); data['director_style_lock'][key] = value; rebind(data)
                self.assertTrue(gate.validate_handoff(data))
        self.assertTrue(gate.validate_handoff([]))

    def test_no_medium_penalty_or_automatic_selection(self):
        for family in ('photographic', 'hand_drawn_2d', 'standard_3d', 'three_render_two',
                       'stop_motion', 'motion_graphics', 'mixed_media', 'other'):
            data = production_packet(); data['appearance_family'] = family
            self.assertEqual(gate.validate_handoff(data), [])
        for profile in gate.catalog()['profiles']:
            self.assertNotIn('scores', profile)
            self.assertNotIn('preferred_styles', profile)
            self.assertNotIn('avoid_styles', profile)

    def test_catalog_preserves_and_expands_with_honest_evidence_boundaries(self):
        profiles = gate.catalog()['profiles']
        self.assertEqual(len(profiles), 69)
        self.assertEqual(len({p['id'] for p in profiles}), 69)
        for p in profiles:
            self.assertTrue(p['research_sources'])
            self.assertTrue(p['research_scope_candidates'])
            self.assertEqual(set(p['transfer_hypotheses']), {'performance','blocking','camera','editing','sound','transitions'})
            self.assertTrue(p['method_status'])
        for pid in ('stephen-chow', 'mamoru-oshii', 'arcane-fortiche'):
            self.assertTrue(next(p for p in profiles if p['id'] == pid)['evidence_notes'])

    def test_fingerprint_ignores_key_order_not_content(self):
        self.assertEqual(gate.fingerprint({'a': 1, 'b': 2}), gate.fingerprint({'b': 2, 'a': 1}))
        self.assertNotEqual(gate.fingerprint({'a': 1}), gate.fingerprint({'a': 2}))

    def test_catalog_cli_and_invalid_packet_exit(self):
        script = str(Path(gate.__file__))
        result = subprocess.run([sys.executable, script, 'catalog'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0); self.assertEqual(len(json.loads(result.stdout)), 69)
        with tempfile.TemporaryDirectory() as temp:
            file = Path(temp) / 'fixture.json'; file.write_text('{}', encoding='utf-8')
            result = subprocess.run([sys.executable, script, 'check', str(file), '--stage', 'generation'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2); self.assertFalse(json.loads(result.stdout)['ok'])

    def test_topic_catalog_has_expected_domains_and_no_dangling_profiles(self):
        db = gate.coverage()
        expected = {'romance', 'youth', 'family-life', 'professional', 'crime-spy', 'war',
                    'history', 'eastern-fantasy', 'horror', 'action-adventure',
                    'science-fiction', 'comedy', 'performance-sport', 'children-family'}
        self.assertEqual({t['id'] for t in db['topics']}, expected)
        self.assertEqual(len(db['topics']), 14)
        known = {p['id'] for p in gate.catalog()['profiles']}
        routed = set()
        for t in db['topics']:
            self.assertTrue(t['decision'])
            self.assertEqual(len(t['branches']), len({b['id'] for b in t['branches']}))
            for b in t['branches']:
                self.assertTrue(b['limits'])
                self.assertTrue(b['options'])
                self.assertEqual(len(b['options']), len({o['profile_id'] for o in b['options']}))
                for o in b['options']:
                    self.assertIn(o['profile_id'], known)
                    self.assertTrue(o['why'])
                    routed.add(o['profile_id'])
        self.assertEqual(routed, known)

    def test_every_topic_id_and_alias_resolves(self):
        for t in gate.coverage()['topics']:
            for query in (t['id'], t['label'], *t['aliases']):
                self.assertEqual(gate.topic(query)['id'], t['id'], query)

    def test_every_branch_alias_is_retrievable_without_selection(self):
        for t in gate.coverage()['topics']:
            for b in t['branches']:
                for term in (b['id'], b['label'], *b['aliases']):
                    result = gate.find_terms(term)
                    self.assertFalse(result['automatic_selection'])
                    self.assertFalse(result['unmatched_terms'])
                    self.assertTrue(any(m['kind'] == 'branch' and m['topic_id'] == t['id']
                                        and m['branch']['id'] == b['id'] for m in result['matches']), term)

    def test_romance_has_distinct_choices_not_a_default_director(self):
        sweet = gate.find_terms('甜宠')['matches'][0]['branch']
        adult = gate.find_terms('婚姻')['matches'][0]['branch']
        self.assertGreater(len(sweet['options']), 1)
        self.assertNotEqual({o['profile_id'] for o in sweet['options']},
                            {o['profile_id'] for o in adult['options']})
        self.assertEqual(len({o['why'] for o in sweet['options']}), len(sweet['options']))

    def test_multiple_genres_are_preserved_not_intersection_ranked(self):
        result = gate.find_terms('甜宠+古偶+谍战')
        self.assertFalse(result['ranked'])
        self.assertFalse(result['automatic_selection'])
        self.assertFalse(result['unmatched_terms'])
        kinds = {m.get('topic_id', m.get('topic', {}).get('id')) for m in result['matches']}
        self.assertEqual(kinds, {'romance', 'history', 'crime-spy'})
        self.assertNotIn('director_style_lock', result)

    def test_shared_alias_returns_both_routes_without_arbitrary_tie_break(self):
        result = gate.find_terms('爱情喜剧')
        self.assertEqual({m['topic_id'] for m in result['matches']}, {'romance', 'comedy'})
        self.assertFalse(result['automatic_selection'])

    def test_mechanisms_are_distinct_from_genres(self):
        result = gate.find_terms('重生+逆袭+系统')
        self.assertEqual({m['kind'] for m in result['matches']}, {'mechanism'})
        self.assertEqual(len(result['matches']), 3)
        for m in result['matches']:
            self.assertNotIn('options', m['mechanism'])
            self.assertTrue(m['mechanism']['check'])

    def test_time_loop_can_be_topic_and_mechanism(self):
        result = gate.find_terms('时间循环')
        self.assertEqual({m['kind'] for m in result['matches']}, {'branch', 'mechanism'})

    def test_medium_terms_do_not_select_director_or_discard_genre(self):
        result = gate.find_terms('三渲二+2D+爱情')
        self.assertEqual(result['medium_terms'], ['三渲二', '2d'])
        self.assertTrue(result['medium_notice'])
        self.assertFalse(result['unmatched_terms'])
        self.assertEqual(len(result['matches']), 1)
        self.assertEqual(result['matches'][0]['topic']['id'], 'romance')
        self.assertEqual(gate.find_terms('3D')['matches'], [])

    def test_unknown_terms_do_not_fall_back_or_silently_disappear(self):
        result = gate.find_terms('甜宠+不存在的题材')
        self.assertEqual(result['unmatched_terms'], ['不存在的题材'])
        self.assertEqual(len(result['matches']), 1)
        self.assertEqual(gate.find_terms('不存在的题材')['matches'], [])
        with self.assertRaises(ValueError):
            gate.topic('不存在的题材')

    def test_empty_and_malformed_queries_fail(self):
        for query in ('', '   ', '+，', None, [], 3):
            with self.assertRaises(ValueError):
                gate.find_terms(query)
        for query in ('', None, [], 3):
            with self.assertRaises(ValueError):
                gate.topic(query)

    def test_alias_repetition_deduplicates_not_votes(self):
        result = gate.find_terms('甜宠，轻甜、甜宠')
        self.assertEqual(len(result['matches']), 1)
        self.assertFalse(result['ranked'])

    def test_retrieval_cannot_pass_the_production_gate(self):
        for query in ('甜宠', '战争', '三渲二', '时间循环'):
            result = gate.find_terms(query)
            for stage in gate.STAGES:
                self.assertTrue(gate.validate_handoff(result, stage))

    def test_expanded_profile_still_needs_real_declared_authorization(self):
        data = production_packet()  # SYNTHETIC test-only record, never a real project.
        data['director_style_lock']['lead']['profile_id'] = 'nora-ephron'
        data['director_style_lock']['lead']['name'] = 'Nora Ephron'
        rebind(data)
        self.assertEqual(gate.validate_handoff(data), [])
        del data['director_style_lock']['authorization']
        rebind(data)
        self.assertTrue(gate.validate_handoff(data))

    def test_every_profile_is_readable_through_cli(self):
        for p in gate.catalog()['profiles']:
            result = subprocess.run([sys.executable, gate.__file__, 'profile', p['id']],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, p['id'])
            self.assertEqual(json.loads(result.stdout), p)

    def test_coverage_cli_handles_index_alias_and_partial_failure(self):
        for command, query in (('topics', None), ('topic', '言情'), ('find', '甜宠+三渲二')):
            args = [sys.executable, gate.__file__, command] + ([query] if query else [])
            result = subprocess.run(args, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertTrue(json.loads(result.stdout))
        result = subprocess.run([sys.executable, gate.__file__, 'find', '甜宠+未登记题材'],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)['unmatched_terms'], ['未登记题材'])
        self.assertTrue(json.loads(result.stdout)['matches'])


if __name__ == '__main__':
    unittest.main()
