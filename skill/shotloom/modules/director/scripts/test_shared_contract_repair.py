"""Synthetic boundary cases for shared identity/value contracts."""
import copy
import unittest

import drama_contracts as common
import director_style as gate
import director_scoring as scoring
import director_catalog_audit as catalog_audit
from test_director_style import production_packet, rebind
from test_director_scoring import fixture


class SharedRepairTests(unittest.TestCase):
    def test_required_description_rejects_empty_sentinels(self):
        for value in (False, True, 0, 1, None, '', ' \t', [], {}, [None], ['text', None], {'label': ' '}, float('nan')):
            with self.subTest(value=value):
                self.assertFalse(common.meaningful(value))

    def test_meaningful_structure_preserves_zero_boolean_and_absence(self):
        for value in ('no outlines', {'at': 0, 'cue': 'contact'}, {'enabled': False, 'reason': 'silent scene'}, ['a', {'b': 'c'}]):
            self.assertTrue(common.meaningful(value))
        self.assertFalse(common.meaningful({'cue': 'a', 'at': float('inf')}))

    def test_mismatched_identity_fails_every_handoff(self):
        packet = production_packet()
        packet['director_style_lock']['lead']['name'] = 'Wong Kar-wai'
        rebind(packet)
        for stage in gate.STAGES:
            self.assertTrue(gate.validate_handoff(packet, stage))

    def test_chinese_and_english_names_pass_without_fuzzy_matching(self):
        profile = next(p for p in gate.catalog()['profiles'] if p['id'] == 'alfred-hitchcock')
        for name in (profile['name_zh'], profile['name_en']):
            packet = production_packet(); packet['director_style_lock']['lead']['name'] = name; rebind(packet)
            self.assertEqual(gate.validate_handoff(packet), [])

    def test_external_identity_uses_same_bounded_slug(self):
        for pid, valid in [('external:test-creator', True), ('external:', False), ('external:Test', False), ('external:a--b', False), ('external:a b', False)]:
            packet = production_packet(); packet['director_style_lock']['lead'].update(profile_id=pid, name='Test Creator'); rebind(packet)
            self.assertEqual(not gate.validate_handoff(packet), valid)
            self.assertEqual(common.external_id(pid), valid)

    def test_legacy_evidence_vocabulary_remains_compatible_without_mutation(self):
        for old, canonical in common.EVIDENCE_ALIASES.items():
            packet = production_packet(); packet['director_style_lock']['evidence'][0]['kind'] = old; rebind(packet)
            before = copy.deepcopy(packet)
            self.assertEqual(gate.validate_handoff(packet), [])
            self.assertEqual(packet, before)
            r, a = fixture()
            for evidence in a['candidates'][0]['evidence']:
                evidence['kind'] = old
            self.assertEqual(scoring.evaluate(r, a, r['authority'])['counts']['fully_scored'], 2)
            self.assertEqual(common.canonical_evidence_kind(old), canonical)

    def test_catalog_normalization_preserves_all_six_scoped_legacy_sources(self):
        evidence = [e for p in gate.catalog()['profiles'] for e in p['evidence_notes'] if 'original_kind' in e]
        self.assertEqual(len(evidence), 6)
        for item in evidence:
            self.assertEqual(item['kind'], common.EVIDENCE_ALIASES[item['original_kind']])
            self.assertTrue(item['scope']); self.assertTrue(item['limits'])
            if item['original_kind'] == 'production_primary_excerpt':
                self.assertEqual(item['status'], 'excerpt_only')

    def test_catalog_rejects_restored_mandatory_facet_policy(self):
        p, c, a = gate.catalog(), gate.coverage(), catalog_audit.acceptance()
        self.assertEqual(catalog_audit.audit(p, c, a), [])
        c['facet_policy']['unused_option_is_failure'] = True
        self.assertTrue(catalog_audit.audit(p, c, a))

    def test_decimal_exclusive_boundary_is_not_float_subtraction(self):
        self.assertEqual(common.decimal_seconds('2.3') - common.decimal_seconds('2'), common.decimal_seconds('.3'))
        for value in (True, 'NaN', float('inf'), None):
            with self.assertRaises(ValueError): common.decimal_seconds(value)


if __name__ == '__main__':
    unittest.main()
