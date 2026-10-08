"""Maintenance regressions; mutated catalogs are synthetic, never production approvals."""
import copy
import json
import subprocess
import sys
import unittest

import director_catalog_audit as audit
import director_style as gate


class CatalogCompletionTests(unittest.TestCase):
    def setUp(self):
        self.p, self.c, self.a = gate.catalog(), gate.coverage(), audit.acceptance()

    def run_audit(self):
        return audit.audit(self.p, self.c, self.a)

    def branch(self, topic, branch):
        return next(b for t in self.c['topics'] if t['id'] == topic for b in t['branches'] if b['id'] == branch)

    def test_complete_catalog_contract(self):
        self.assertEqual(self.run_audit(), [])

    def test_all_promised_queries_return_executable_exact_routes(self):
        self.assertEqual(len(self.a['promised_routes']), 87)
        for row in self.a['promised_routes']:
            result = gate.find_terms(row['term'])
            with self.subTest(term=row['term'], topic=row['topic_id']):
                self.assertFalse(result['unmatched_terms'])
                self.assertTrue(any(m['kind'] == 'branch' and m['topic_id'] == row['topic_id']
                    and m['branch']['id'] == row['branch_id'] and
                    any(f['term'] == row['term'] for f in m['branch']['execution_facets'])
                    for m in result['matches']))
                for stage in gate.STAGES:
                    self.assertTrue(gate.validate_handoff(result, stage))

    def test_independent_missing_routes_are_not_umbrella_aliases(self):
        expected = {'养老': ('family-life', 'elder-care'), '本格推理': ('crime-spy', 'classic-mystery'),
            '追凶': ('crime-spy', 'manhunt'), '团队对抗': ('performance-sport', 'team-sport'),
            '儿童视点': ('children-family', 'child-viewpoint'), '都市生活': ('family-life', 'urban')}
        for term, key in expected.items():
            found = {(m['topic_id'], m['branch']['id']) for m in gate.find_terms(term)['matches'] if m['kind'] == 'branch'}
            self.assertIn(key, found)

    def test_every_legacy_profile_now_has_scoped_card_not_just_url(self):
        self.assertEqual(len(self.p['profiles']), 69)
        for p in self.p['profiles']:
            self.assertTrue(p['method_cards'])
            self.assertTrue(any(e['status'] == 'claim_checked' for e in p['evidence_notes']))

    def test_deleting_execution_but_retaining_alias_fails(self):
        self.branch('family-life', 'elder-care')['execution_facets'] = []
        self.assertTrue(self.run_audit())

    def test_dangling_source_fails(self):
        self.p['profiles'][0]['method_cards'][0]['evidence_ids'] = ['MISSING']
        self.assertTrue(self.run_audit())

    def test_research_url_cannot_be_upgraded_by_card(self):
        p = self.p['profiles'][0]
        p['evidence_notes'][0]['status'] = 'research_lead'
        self.assertTrue(self.run_audit())

    def test_claim_and_scope_cannot_be_broadened_silently(self):
        for key in ('source_fact', 'scope'):
            with self.subTest(field=key):
                p = copy.deepcopy(self.p)
                p['profiles'][0]['method_cards'][0][key] = 'unsupported all films claim'
                self.assertTrue(audit.audit(p, self.c, self.a))

    def test_sound_source_cannot_support_camera_dimension(self):
        p = next(p for p in self.p['profiles'] if p['id'] == 'david-fincher')
        p['method_basis']['camera']['related_method_cards'] = [p['method_cards'][0]['id']]
        self.assertTrue(self.run_audit())

    def test_authored_method_cannot_claim_full_verification(self):
        self.p['profiles'][0]['method_basis']['camera']['status'] = 'verified_director_fact'
        self.assertTrue(self.run_audit())

    def test_specialists_cannot_revert_to_generic_placeholders(self):
        for topic, branch in [('horror', 'found-footage'), ('performance-sport', 'competition')]:
            c = copy.deepcopy(self.c)
            b = next(b for t in c['topics'] if t['id'] == topic for b in t['branches'] if b['id'] == branch)
            b['options'] = copy.deepcopy(self.branch('romance', 'light')['options'])
            self.assertTrue(audit.audit(self.p, c, self.a))

    def test_method_card_cannot_reference_another_director(self):
        self.branch('horror', 'found-footage')['options'][0]['method_cards'] = ['david-fincher-method-1']
        self.assertTrue(self.run_audit())

    def test_child_viewpoint_and_family_audience_are_different_routes(self):
        child = gate.find_terms('儿童视点')['matches'][0]['branch']
        family = gate.find_terms('家庭冒险')['matches'][0]['branch']
        self.assertNotEqual(child['id'], family['id'])
        self.assertIn('不等于儿童适龄', child['limits'])
        self.assertIn('有限理解', child['label'])

    def test_team_and_individual_competition_have_distinct_actions(self):
        team = self.branch('performance-sport', 'team-sport')
        solo = self.branch('performance-sport', 'sports')
        self.assertNotEqual(team['execution_facets'], solo['execution_facets'])
        self.assertIn('队员角色', team['execution_facets'][0]['execute'])

    def test_evidence_read_basis_is_not_silently_promoted(self):
        for pid in ('sidney-lumet', 'hayao-miyazaki'):
            p = next(p for p in self.p['profiles'] if p['id'] == pid)
            self.assertEqual(p['evidence_notes'][-1]['read_basis'], 'retrieved_interview_excerpt')

    def test_joint_directing_remains_deferred(self):
        self.p['method_contract']['joint_directing'] = 'enabled'
        self.assertTrue(self.run_audit())

    def test_no_ranking_selection_or_medium_drift(self):
        for key in ('ranked', 'automatic_selection', 'automatic_style_lock'):
            c = copy.deepcopy(self.c); c['selection_policy'][key] = True
            self.assertTrue(audit.audit(self.p, c, self.a))

    def test_malformed_contract_reports_error(self):
        for value in (None, [], {}, True, 'wrong'):
            self.assertTrue(audit.audit(value, self.c, self.a))

    def test_audit_cli_is_read_only_and_not_production_approval(self):
        result = subprocess.run([sys.executable, audit.__file__], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        body = json.loads(result.stdout)
        self.assertTrue(body['ok'])
        self.assertFalse(body['production_authorized'])
        self.assertFalse(body['source_truth_automatically_proven'])


if __name__ == '__main__':
    unittest.main()
