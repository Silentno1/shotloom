"""Research retrieval regressions. These do not grade authored prose or generated media."""
import copy
import hashlib
import json
import subprocess
import sys
import unittest

import director_methods as methods
import director_style as gate


class ConditionalMethodTests(unittest.TestCase):
    def setUp(self):
        self.c, self.g, self.digest = methods.load()

    def check(self):
        return methods.audit(self.c, self.g, self.digest)

    def test_all_profiles_retrievable_with_original_source(self):
        self.assertEqual(self.check(), [])
        self.assertEqual(len(self.g['profiles']), 69)
        self.assertEqual(sum(len(p['basis_card_ids']) for p in self.g['profiles']), 73)
        for p in self.c['profiles']:
            r = methods.profile(p['id'], self.c, self.g, self.digest)
            self.assertEqual(r['profile'], p)
            self.assertFalse(r['automatic_selection'])
            self.assertEqual(r['default_generation_calls'], 0)

    def test_missing_profile(self):
        self.g['profiles'].pop()
        self.assertTrue(self.check())

    def test_duplicate_profile(self):
        self.g['profiles'].append(copy.deepcopy(self.g['profiles'][0]))
        self.assertTrue(self.check())

    def test_unknown_profile(self):
        self.g['profiles'][0]['profile_id'] = 'made-up'
        self.assertTrue(self.check())

    def test_missing_fields(self):
        for field in methods.FIELDS:
            g = copy.deepcopy(self.g)
            g['profiles'][0][field] = ' '
            with self.subTest(field=field):
                self.assertTrue(methods.audit(self.c, g, self.digest))

    def test_foreign_source(self):
        self.g['profiles'][0]['basis_card_ids'] = self.g['profiles'][1]['basis_card_ids']
        self.assertTrue(self.check())

    def test_duplicate_source(self):
        self.g['profiles'][0]['basis_card_ids'] *= 2
        self.assertTrue(self.check())

    def test_missing_second_card(self):
        p = next(p for p in self.g['profiles'] if len(p['basis_card_ids']) == 2)
        p['basis_card_ids'].pop()
        self.assertTrue(self.check())

    def test_application_cannot_be_source_fact(self):
        self.g['profiles'][0]['status'] = 'verified_director_fact'
        self.assertTrue(self.check())

    def test_catalog_bytes_and_revision_bound(self):
        self.assertTrue(methods.audit(self.c, self.g, '0' * 64))
        self.c['revision'] = 'changed'
        self.assertTrue(self.check())

    def test_policy_mutations_rejected(self):
        for field, value in [('automatic_selection', True), ('default_generation_calls', 2),
                             ('not_for_production', False), ('joint_directing', 'enabled'),
                             ('authored_applications', False)]:
            g = copy.deepcopy(self.g)
            g['policy'][field] = value
            with self.subTest(field=field):
                self.assertTrue(methods.audit(self.c, g, self.digest))

    def test_unsupported_dimensions_explicit(self):
        r = methods.profile('david-fincher', self.c, self.g, self.digest)
        self.assertIn('camera', r['dimensions_without_source_card'])
        self.assertIn('sound', r['source_card_dimensions'])
        self.assertNotIn('camera', r['source_card_dimensions'])

    def test_source_scopes_not_merged(self):
        r = methods.profile('sam-mendes', self.c, self.g, self.digest)
        self.assertEqual(len(r['profile']['method_cards']), 2)
        self.assertNotEqual(r['profile']['method_cards'][0]['scope'],
                            r['profile']['method_cards'][1]['scope'])

    def test_cannot_pass_any_production_gate(self):
        r = methods.profile('sidney-lumet', self.c, self.g, self.digest)
        for stage in gate.STAGES:
            with self.subTest(stage=stage):
                self.assertTrue(gate.validate_handoff(r, stage))
                relabeled = dict(r, workflow_scope='production')
                self.assertTrue(gate.validate_handoff(relabeled, stage))

    def test_unknown_id_no_fallback(self):
        with self.assertRaises(ValueError):
            methods.profile('unknown', self.c, self.g, self.digest)

    def test_stale_guide_not_returned(self):
        with self.assertRaises(ValueError):
            methods.profile('sidney-lumet', self.c, self.g, 'stale')

    def test_cli_readonly_and_errors(self):
        paths = [methods.REFERENCES / 'director-profiles.json',
                 methods.REFERENCES / 'director-decision-methods.json']
        before = [hashlib.sha256(p.read_bytes()).hexdigest() for p in paths]
        for args, success in [(['audit'], True), (['profile', 'arcane-fortiche'], True),
                              (['profile', 'unknown'], False)]:
            run = subprocess.run([sys.executable, methods.__file__, *args], capture_output=True, text=True)
            self.assertEqual(run.returncode == 0, success)
            json.loads(run.stdout)
            self.assertNotIn('Traceback', run.stderr)
        self.assertEqual(before, [hashlib.sha256(p.read_bytes()).hexdigest() for p in paths])

    def test_malformed_entries_and_schema(self):
        for value in (None, {}, [None], [{'profile_id': []}]):
            g = copy.deepcopy(self.g)
            g['profiles'] = value
            self.assertTrue(methods.audit(self.c, g, self.digest))
        self.g['schema_version'] = 9
        self.assertTrue(self.check())


if __name__ == '__main__':
    unittest.main()
