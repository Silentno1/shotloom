"""Synthetic fixtures only: no real director, screenplay or authorization judgments."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import director_scoring as scoring
import director_style as gate


def rubric(ids=None):
    ids = ['alfred-hitchcock', 'david-fincher'] if ids is None else ids
    return {
        'schema_version': 1, 'id': 'SYNTHETIC-rubric', 'version': '1',
        'basis': 'TEST ONLY: fictional requirements, no real project',
        'authority': {'project_id': 'TEST-ONLY', 'work_scope': 'complete fixture', 'script_version': 'v1'},
        'reading_scope': 'complete_authoritative_scope', 'script_sources': ['SYNTHETIC complete fixture'],
        'criteria': {k: {'weight': w, 'need': 'SYNTHETIC need: ' + k,
                         'rationale': 'SYNTHETIC prior requirement', 'script_refs': ['fixture scene 1']}
                     for k, w in scoring.DEFAULT_WEIGHTS.items()},
        'comparison': {'mode': 'bounded', 'reason': 'SYNTHETIC bounded test', 'profile_ids': ids}}


def full_candidate(row, grade=4):
    row.update(research_status='reviewed', pending_reason='',
               reference_scope={'works': ['SYNTHETIC reference'], 'boundary': 'fixture only'},
               confidence={'level': 'medium', 'rationale': 'SYNTHETIC evidence limits'},
               conflict_review={'status': 'complete', 'summary': 'SYNTHETIC whole-scope countercheck'},
               strengths=['SYNTHETIC strength'], weaknesses=['SYNTHETIC limitation'],
               viewer_experience='SYNTHETIC intended experience', adaptation_cost='SYNTHETIC adaptation')
    row['evidence'] = []
    for key in scoring.DEFAULT_WEIGHTS:
        eid = 'TEST-' + key
        row['evidence'].append({'id': eid, 'source': 'SYNTHETIC source, not a historical claim',
            'locator': 'fixture paragraph', 'work': 'SYNTHETIC reference', 'claim': 'SYNTHETIC fact',
            'limits': 'test only', 'checked_at': '2026-10-02', 'kind': 'work_observation', 'supports': [key]})
        row['dimensions'][key] = {'status': 'scored', 'score': grade, 'rationale': 'SYNTHETIC fit reasoning',
            'adaptation': 'SYNTHETIC authored transfer, not director quote',
            'script_refs': ['fixture scene 1'], 'evidence_ids': [eid]}
    return row


def fixture():
    r = rubric()
    a = scoring.prepare(r)
    full_candidate(a['candidates'][0], 4)
    full_candidate(a['candidates'][1], 3)
    return r, a


class ScoringTests(unittest.TestCase):
    def run_score(self, r, a):
        return scoring.evaluate(r, a, copy.deepcopy(r['authority']))

    def test_exact_weighted_arithmetic_and_order(self):
        r, a = fixture()
        for key, grade in zip(scoring.DEFAULT_WEIGHTS, (5, 4, 3, 2, 1)):
            a['candidates'][0]['dimensions'][key]['score'] = grade
        result = self.run_score(r, a)
        self.assertEqual(result['candidates'][0]['score'], 66.0)
        self.assertEqual([v['score'] for v in result['ranking']], [66.0, 60.0])

    def test_all_catalog_prepare_is_69_pending_not_zero_or_reviewed(self):
        r = rubric(); r['comparison'] = {'mode': 'all_catalog', 'reason': 'whole-catalog test'}
        a = scoring.prepare(r); result = self.run_score(r, a)
        self.assertEqual(result['counts'], {'total': 69, 'fully_scored': 0, 'pending_scores': 69,
                                           'not_reviewed': 69, 'rankable': 0})
        self.assertEqual(result['ranking'], [])
        self.assertTrue(all(v['score'] is None for v in result['candidates']))

    def test_ledger_cannot_omit_add_or_duplicate_candidates(self):
        r, a = fixture()
        for mutation in ('omit', 'add', 'duplicate'):
            with self.subTest(mutation=mutation):
                b = copy.deepcopy(a)
                if mutation == 'omit': b['candidates'].pop()
                elif mutation == 'add':
                    row = copy.deepcopy(b['candidates'][0]); row['profile_id'] = 'yasujiro-ozu'; b['candidates'].append(row)
                else: b['candidates'].append(copy.deepcopy(b['candidates'][0]))
                with self.assertRaises(ValueError): self.run_score(r, b)

    def test_pending_dimension_never_normalizes_remaining_scores(self):
        r, a = fixture(); c = full_candidate(a['candidates'][0], 5)
        c['dimensions']['rhythm'] = {'status': 'pending', 'score': None, 'reason': 'missing series evidence'}
        c['pending_reason'] = 'missing series evidence'
        result = self.run_score(r, a)
        self.assertIsNone(result['candidates'][0]['score'])
        self.assertEqual(result['candidates'][0]['status'], 'pending')
        self.assertEqual(len(result['ranking']), 1)

    def test_pending_cannot_be_zero_or_have_no_reason(self):
        r = rubric(); a = scoring.prepare(r)
        for mutation in ('zero', 'no_reason', 'no_candidate_reason'):
            b = copy.deepcopy(a)
            if mutation == 'zero': b['candidates'][0]['dimensions']['story']['score'] = 0
            elif mutation == 'no_reason': b['candidates'][0]['dimensions']['story'].pop('reason')
            else: b['candidates'][0].pop('pending_reason')
            with self.assertRaises(ValueError): self.run_score(r, b)

    def test_evidenced_zero_is_valid_not_pending(self):
        r, a = fixture(); full_candidate(a['candidates'][0], 0)
        result = self.run_score(r, a)
        self.assertEqual(result['candidates'][0]['score'], 0.0)
        self.assertEqual(result['counts']['fully_scored'], 2)

    def test_high_score_with_blocking_conflict_cannot_rank(self):
        r, a = fixture(); c = full_candidate(a['candidates'][0], 5)
        c['conflicts'] = [{'severity': 'blocking', 'issue': 'SYNTHETIC central fact lost',
                          'script_refs': ['fixture ending'], 'treatment': 'cannot recommend this method scope'}]
        result = self.run_score(r, a)
        self.assertEqual(result['candidates'][0]['score'], 100)
        self.assertEqual(result['candidates'][0]['status'], 'blocking_conflict')
        self.assertIsNone(result['candidates'][0]['rank'])
        self.assertEqual(result['ranking'][0]['profile_id'], 'david-fincher')

    def test_known_blocking_conflict_survives_pending_score(self):
        r = rubric(); a = scoring.prepare(r)
        a['candidates'][0]['conflicts'] = [{'severity': 'blocking', 'issue': 'SYNTHETIC known issue',
            'script_refs': ['fixture scene'], 'treatment': 'review before any recommendation'}]
        result = self.run_score(r, a)
        self.assertEqual(result['candidates'][0]['status'], 'blocking_conflict')
        self.assertIsNone(result['candidates'][0]['score'])

    def test_conditional_risk_is_visible_and_not_silently_deducted(self):
        r, a = fixture()
        a['candidates'][0]['conflicts'] = [{'severity': 'conditional', 'issue': 'SYNTHETIC compromise',
            'script_refs': ['fixture scene'], 'treatment': 'requires explicit adaptation'}]
        result = self.run_score(r, a)
        self.assertEqual(result['ranking'][0]['status'], 'conditional')
        self.assertEqual(result['ranking'][0]['score'], 80)
        self.assertEqual(len(result['candidates'][0]['conflicts']), 1)

    def test_complete_score_with_unfinished_conflict_review_does_not_rank(self):
        r, a = fixture(); a['candidates'][0]['conflict_review']['status'] = 'pending'
        result = self.run_score(r, a)
        self.assertEqual(result['candidates'][0]['status'], 'conflict_unchecked')
        self.assertIsNone(result['candidates'][0]['rank'])

    def test_empty_conflicts_does_not_skip_review_explanation(self):
        r, a = fixture(); a['candidates'][0]['conflict_review']['summary'] = ''
        with self.assertRaises(ValueError): self.run_score(r, a)

    def test_confidence_is_not_a_score_multiplier(self):
        r, a = fixture(); a['candidates'][0]['confidence']['level'] = 'low'
        self.assertEqual(self.run_score(r, a)['candidates'][0]['score'], 80)

    def test_ties_stay_ties(self):
        r, a = fixture(); full_candidate(a['candidates'][1], 4)
        result = self.run_score(r, a)
        self.assertEqual([v['rank'] for v in result['ranking']], [1, 1])
        a['candidates'].reverse()
        self.assertEqual([v['rank'] for v in self.run_score(r, a)['ranking']], [1, 1])

    def test_missing_dimension_cannot_disappear(self):
        r, a = fixture(); a['candidates'][0]['dimensions'].pop('rhythm')
        with self.assertRaises(ValueError): self.run_score(r, a)

    def test_grades_reject_bool_fraction_out_of_range_and_nonfinite(self):
        for value in (True, False, -1, 6, 3.5, float('nan'), float('inf'), '4', None, []):
            with self.subTest(value=value):
                r, a = fixture(); a['candidates'][0]['dimensions']['story']['score'] = value
                with self.assertRaises(ValueError): self.run_score(r, a)

    def test_weights_are_positive_integers_and_sum_100(self):
        for value in (True, 0, -25, 25.0, 26, float('inf'), '25'):
            r = rubric(); r['criteria']['story']['weight'] = value
            with self.assertRaises(ValueError): scoring.prepare(r)

    def test_weights_can_change_before_scoring_not_after_binding(self):
        r, a = fixture()
        r['criteria']['story']['weight'] = 30; r['criteria']['rhythm']['weight'] = 10
        with self.assertRaises(ValueError): self.run_score(r, a)
        new = scoring.prepare(r)
        self.assertEqual(self.run_score(r, new)['weights']['story'], 30)

    def test_need_change_breaks_old_fingerprint_even_same_weights(self):
        r, a = fixture(); r['criteria']['story']['need'] = 'different target'
        with self.assertRaises(ValueError): self.run_score(r, a)

    def test_catalog_snapshot_change_requires_review_not_silent_reuse(self):
        r, a = fixture(); db = gate.catalog(); db['revision'] = 'changed-fixture'
        with self.assertRaises(ValueError): scoring.evaluate(r, a, r['authority'], db)

    def test_wrong_current_project_scope_or_script_is_rejected(self):
        r, a = fixture()
        for key in gate.AUTHORITY:
            current = dict(r['authority']); current[key] = 'stale'
            with self.assertRaises(ValueError): scoring.evaluate(r, a, current)

    def test_excerpt_cannot_rank_as_complete_work(self):
        r = rubric(); r['reading_scope'] = 'excerpts'
        with self.assertRaises(ValueError): scoring.prepare(r)

    def test_scope_cannot_hide_duplicates_unknowns_retired_or_subset(self):
        for ids in (['david-fincher', 'david-fincher'], ['unknown'], ['pascal-charrue-arnaud-delord'], []):
            with self.assertRaises(ValueError): scoring.prepare(rubric(ids))
        r = rubric(); r['comparison']['mode'] = 'all_catalog'
        with self.assertRaises(ValueError): scoring.prepare(r)

    def test_external_scoring_requires_credit_and_scoped_evidence(self):
        r = rubric(['external:synthetic-only']); a = scoring.prepare(r)
        full_candidate(a['candidates'][0])
        with self.assertRaises(ValueError): self.run_score(r, a)
        a['candidates'][0]['credit'] = {'source': 'SYNTHETIC credits', 'claim': 'test identity only'}
        with self.assertRaises(ValueError): self.run_score(r, a)
        a['candidates'][0]['name'] = 'SYNTHETIC individual'
        self.assertEqual(self.run_score(r, a)['counts']['rankable'], 1)

    def test_candidate_name_cannot_swap_catalog_identity(self):
        r, a = fixture(); a['candidates'][0]['name'] = 'unrelated person'
        with self.assertRaises(ValueError): self.run_score(r, a)

    def test_missing_or_wrong_dimension_evidence_is_rejected(self):
        for mutation in ('missing', 'wrong_dimension', 'duplicate', 'wrong_work', 'unread_kind', 'bad_date'):
            r, a = fixture(); c = a['candidates'][0]
            if mutation == 'missing': c['evidence'].pop(0)
            elif mutation == 'wrong_dimension': c['evidence'][0]['supports'] = ['rhythm']
            elif mutation == 'duplicate': c['evidence'].append(copy.deepcopy(c['evidence'][0]))
            elif mutation == 'wrong_work': c['evidence'][0]['work'] = 'outside reference'
            elif mutation == 'unread_kind': c['evidence'][0]['kind'] = 'unread_url'
            else: c['evidence'][0]['checked_at'] = '2026-02-30'
            with self.subTest(mutation=mutation), self.assertRaises(ValueError): self.run_score(r, a)

    def test_grades_need_script_transfer_and_source_locator_not_just_url(self):
        for key in ('script_refs', 'rationale', 'adaptation'):
            r, a = fixture(); a['candidates'][0]['dimensions']['story'].pop(key)
            with self.assertRaises(ValueError): self.run_score(r, a)
        r, a = fixture(); a['candidates'][0]['evidence'][0].pop('locator')
        with self.assertRaises(ValueError): self.run_score(r, a)

    def test_unreviewed_or_unknown_evidence_cannot_be_scored(self):
        r, a = fixture(); a['candidates'][0]['research_status'] = 'not_reviewed'
        with self.assertRaises(ValueError): self.run_score(r, a)
        r, a = fixture(); a['candidates'][0]['confidence']['level'] = 'unknown'
        with self.assertRaises(ValueError): self.run_score(r, a)

    def test_scoped_work_and_countercase_are_required(self):
        for key in ('reference_scope', 'strengths', 'weaknesses', 'viewer_experience', 'adaptation_cost'):
            r, a = fixture(); a['candidates'][0].pop(key)
            with self.assertRaises(ValueError): self.run_score(r, a)

    def test_malformed_nested_values_fail_cleanly(self):
        for key in ('dimensions', 'evidence', 'confidence', 'conflict_review', 'conflicts'):
            r, a = fixture(); a['candidates'][0][key] = 3
            with self.assertRaises(ValueError): self.run_score(r, a)
        for value in ([], None, 5, 'text'):
            with self.assertRaises(ValueError): scoring.prepare(value)

    def test_no_fixed_medium_or_model_penalty(self):
        r, a = fixture()
        first = self.run_score(r, a)
        a['appearance_family'] = 'cel_shaded'; a['model'] = 'SYNTHETIC model'
        self.assertEqual(first['ranking'], self.run_score(r, a)['ranking'])
        self.assertNotIn('medium', scoring.DEFAULT_WEIGHTS)

    def test_scoring_does_not_mutate_inputs_or_catalog(self):
        r, a = fixture(); db = gate.catalog(); before = copy.deepcopy((r, a, db))
        scoring.evaluate(r, a, r['authority'], db)
        self.assertEqual((r, a, db), before)

    def test_output_cannot_bypass_any_production_stage(self):
        r, a = fixture(); result = self.run_score(r, a)
        self.assertFalse(result['automatic_selection']); self.assertFalse(result['production_authorized'])
        self.assertNotIn('director_style_lock', result)
        for stage in gate.STAGES:
            self.assertTrue(gate.validate_handoff(result, stage))

    def test_lexical_lookup_is_still_unranked(self):
        result = gate.find_terms('言情')
        self.assertFalse(result['ranked']); self.assertFalse(result['automatic_selection'])

    def test_catalog_policy_allows_scoped_assessment_not_fixed_scores(self):
        db = gate.catalog()
        self.assertIn('No fixed director scores', db['selection_policy'])
        self.assertIn('director-scoring.md', db['selection_policy'])
        self.assertTrue(all('score' not in p for p in db['profiles']))

    def test_docs_and_entrypoint_route_to_scorer(self):
        root = Path(scoring.__file__).resolve().parents[1]
        for relative in ('WORKFLOW.md', 'references/director-selection.md', 'references/director-coverage.md'):
            self.assertIn('director-scoring.md', (root / relative).read_text())
        doc = (root / 'references/director-scoring.md').read_text()
        self.assertIn('director_scoring.py', doc)

    def test_cli_roundtrip_and_read_only(self):
        r, a = fixture()
        with tempfile.TemporaryDirectory() as folder:
            paths = [Path(folder) / s for s in ('rubric.json', 'assessment.json', 'authority.json')]
            for path, data in zip(paths, (r, a, r['authority'])):
                path.write_text(json.dumps(data), encoding='utf-8')
            before = [p.read_bytes() for p in paths]
            for arguments in (['fingerprint', str(paths[0])], ['prepare', str(paths[0])],
                              ['evaluate', str(paths[0]), str(paths[1]), '--authority', str(paths[2])]):
                result = subprocess.run([sys.executable, scoring.__file__, *arguments], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
                data = json.loads(result.stdout)
                if arguments[0] == 'evaluate': self.assertEqual(data['counts']['rankable'], 2)
                elif arguments[0] == 'fingerprint': self.assertEqual(data['sha256'], gate.fingerprint(r))
                else: self.assertTrue(all(c['research_status'] == 'not_reviewed' for c in data['candidates']))
            self.assertEqual(before, [p.read_bytes() for p in paths])
            self.assertEqual(len(list(Path(folder).iterdir())), 3)

    def test_cli_malformed_json_duplicate_keys_and_nonfinite_no_traceback(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'invalid.json'
            for content in ('{', '[]', '{"a":1,"a":2}', '{"score":NaN}', '{"score":Infinity}'):
                path.write_text(content, encoding='utf-8')
                result = subprocess.run([sys.executable, scoring.__file__, 'prepare', str(path)],
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, 2)
                self.assertFalse(json.loads(result.stdout)['ok'])
                self.assertNotIn('Traceback', result.stderr)


if __name__ == '__main__':
    unittest.main()
