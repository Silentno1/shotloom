#!/usr/bin/env python3
"""Read-only suitability arithmetic. Never infers grades, selects or authorizes."""
from __future__ import annotations

import argparse
import copy
import json
import re
from datetime import date
from pathlib import Path

import director_style as gate
from drama_contracts import EVIDENCE_KINDS, canonical_evidence_kind, external_id, profile_name_matches

REVISION = 'director-scoring-20261002'
DEFAULT_WEIGHTS = {'story': 25, 'performance': 25, 'narrative': 20,
                   'audiovisual': 15, 'rhythm': 15}
KINDS = EVIDENCE_KINDS


def require(condition, message):
    if not condition:
        raise ValueError(message)


def obj(value, path):
    require(isinstance(value, dict), f'{path}: expected object')
    return value


def texts(value, path):
    require(gate.strings(value), f'{path}: expected non-empty text list')
    return value


def fields(value, keys, path):
    obj(value, path)
    for key in keys:
        require(gate.nonempty(value.get(key)), f'{path}.{key}: required text')


def unique_texts(value, path):
    texts(value, path)
    require(len(value) == len(set(value)), f'{path}: duplicate values')
    return value


def schema(value, path):
    obj(value, path)
    require(type(value.get('schema_version')) is int and value['schema_version'] == 1,
            f'{path}: schema_version must be 1')
    fields(value, ('id', 'version'), path)


def validate_authority(value):
    fields(value, gate.AUTHORITY, 'authority')
    return {k: value[k] for k in gate.AUTHORITY}


def candidate_ids(rubric, db):
    comparison = obj(rubric.get('comparison'), 'comparison')
    fields(comparison, ('reason',), 'comparison')
    known = {p['id'] for p in db['profiles']}
    mode = comparison.get('mode')
    require(mode in ('all_catalog', 'bounded'), 'comparison: unknown mode')
    if mode == 'all_catalog':
        require('profile_ids' not in comparison, 'all_catalog cannot hide IDs behind a subset')
        return [p['id'] for p in db['profiles']]
    ids = unique_texts(comparison.get('profile_ids'), 'comparison.profile_ids')
    for pid in ids:
        require(pid not in db.get('retired_ids', {}), f'{pid}: retired identity')
        require(pid in known or external_id(pid),
                f'{pid}: unknown identity; verify external credit explicitly')
    return ids


def validate_rubric(rubric, db=None):
    db = gate.catalog() if db is None else db
    schema(rubric, 'rubric')
    fields(rubric, ('basis',), 'rubric')
    validate_authority(rubric.get('authority'))
    require(rubric.get('reading_scope') == 'complete_authoritative_scope',
            'rubric: excerpt reading cannot support whole-scope ranking')
    texts(rubric.get('script_sources'), 'rubric.script_sources')
    criteria = obj(rubric.get('criteria'), 'criteria')
    require(set(criteria) == set(DEFAULT_WEIGHTS), 'criteria: require exactly five dimensions')
    for key, row in criteria.items():
        fields(row, ('need', 'rationale'), key)
        weight = row.get('weight')
        require(type(weight) is int and weight > 0, f'{key}: weight must be positive integer')
        texts(row.get('script_refs'), key + '.script_refs')
    require(sum(v['weight'] for v in criteria.values()) == 100, 'weights must sum to 100')
    return candidate_ids(rubric, db)


def prepare(rubric, db=None):
    db = gate.catalog() if db is None else db
    ids = validate_rubric(rubric, db)
    names = {p['id']: p['name_zh'] for p in db['profiles']}
    candidates = []
    for pid in ids:
        candidates.append({
            'profile_id': pid, 'name': names.get(pid, pid),
            'research_status': 'not_reviewed', 'pending_reason': '尚未逐项核读剧本与对应方法依据',
            'reference_scope': None, 'evidence': [],
            'dimensions': {key: {'status': 'pending', 'score': None, 'reason': '尚未研究'}
                           for key in DEFAULT_WEIGHTS},
            'confidence': {'level': 'unknown', 'rationale': '尚未研究，不代表不适合'},
            'conflict_review': {'status': 'pending', 'summary': '尚未逐场核对核心冲突'},
            'conflicts': []})
    return {'schema_version': 1, 'id': rubric['id'] + '-assessment', 'version': '1',
            'rubric_sha256': gate.fingerprint(rubric), 'catalog_sha256': gate.fingerprint(db),
            'candidates': candidates}


def validate_candidate(candidate):
    fields(candidate, ('profile_id', 'name'), 'candidate')
    pid = candidate['profile_id']
    research = candidate.get('research_status')
    require(research in ('not_reviewed', 'reviewed'), f'{pid}: research status required')
    dimensions = obj(candidate.get('dimensions'), pid + '.dimensions')
    require(set(dimensions) == set(DEFAULT_WEIGHTS), f'{pid}: require all five dimensions')
    scored = []
    for key, row in dimensions.items():
        obj(row, f'{pid}.{key}')
        if row.get('status') == 'pending':
            require('score' in row and row['score'] is None, f'{pid}.{key}: pending score must be null')
            fields(row, ('reason',), f'{pid}.{key}')
        else:
            require(row.get('status') == 'scored', f'{pid}.{key}: unknown status')
            require(type(row.get('score')) is int and 0 <= row['score'] <= 5,
                    f'{pid}.{key}: grade must be integer 0..5, not an evidence placeholder')
            fields(row, ('rationale', 'adaptation'), f'{pid}.{key}')
            texts(row.get('script_refs'), f'{pid}.{key}.script_refs')
            unique_texts(row.get('evidence_ids'), f'{pid}.{key}.evidence_ids')
            scored.append(key)
    if len(scored) < len(DEFAULT_WEIGHTS):
        fields(candidate, ('pending_reason',), pid)
    confidence = obj(candidate.get('confidence'), pid + '.confidence')
    require(confidence.get('level') in ('high', 'medium', 'low', 'unknown'),
            f'{pid}: unknown confidence level')
    fields(confidence, ('rationale',), pid + '.confidence')
    scope = candidate.get('reference_scope')
    if scope is not None:
        fields(scope, ('boundary',), pid + '.reference_scope')
        texts(scope.get('works'), pid + '.reference_scope.works')
    if scored:
        require(research == 'reviewed', f'{pid}: unreviewed candidates cannot have grades')
        require(confidence['level'] != 'unknown', f'{pid}: graded evidence cannot be unknown')
        require(scope is not None, f'{pid}: grades require a scoped reference')
        if pid.startswith('external:'):
            fields(candidate.get('credit'), ('source', 'claim'), pid + '.credit')
    elif research == 'not_reviewed':
        require(confidence['level'] == 'unknown', f'{pid}: unreviewed confidence must be unknown')
    evidence = candidate.get('evidence')
    require(isinstance(evidence, list), f'{pid}: evidence must be a list')
    evidence_map = {}
    for e in evidence:
        fields(e, ('id', 'source', 'locator', 'work', 'claim', 'limits', 'checked_at'), pid + '.evidence')
        require(e['id'] not in evidence_map, f'{pid}: duplicate evidence ID')
        require(canonical_evidence_kind(e.get('kind')) in KINDS, f'{pid}: unsupported evidence kind')
        require(re.fullmatch(r'\d{4}-\d{2}-\d{2}', e['checked_at']) is not None,
                f'{pid}: checked_at must be ISO date')
        date.fromisoformat(e['checked_at'])
        require(scope is not None and e['work'] in scope['works'], f'{pid}: evidence outside reference works')
        supports = unique_texts(e.get('supports'), pid + '.evidence.supports')
        require(set(supports) <= set(DEFAULT_WEIGHTS), f'{pid}: unknown supported dimension')
        evidence_map[e['id']] = e
    for key in scored:
        for eid in dimensions[key]['evidence_ids']:
            require(eid in evidence_map and key in evidence_map[eid]['supports'],
                    f'{pid}.{key}: missing or unrelated evidence {eid}')
    review = obj(candidate.get('conflict_review'), pid + '.conflict_review')
    require(review.get('status') in ('complete', 'pending'), f'{pid}: conflict review status required')
    fields(review, ('summary',), pid + '.conflict_review')
    require(research == 'reviewed' or review['status'] == 'pending',
            f'{pid}: unreviewed candidates cannot claim complete conflict checks')
    conflicts = candidate.get('conflicts')
    require(isinstance(conflicts, list), f'{pid}: conflicts must be a list')
    for conflict in conflicts:
        fields(conflict, ('issue', 'treatment'), pid + '.conflict')
        require(conflict.get('severity') in ('blocking', 'conditional'), f'{pid}: unknown conflict severity')
        texts(conflict.get('script_refs'), pid + '.conflict.script_refs')
    if len(scored) == len(DEFAULT_WEIGHTS):
        texts(candidate.get('strengths'), pid + '.strengths')
        texts(candidate.get('weaknesses'), pid + '.weaknesses')
        fields(candidate, ('viewer_experience', 'adaptation_cost'), pid)
    return scored


def evaluate(rubric, assessment, current_authority, db=None):
    db = gate.catalog() if db is None else db
    ids = validate_rubric(rubric, db)
    require(validate_authority(current_authority) == validate_authority(rubric['authority']),
            'current authority differs: do not rank stale/cross-project assessments')
    schema(assessment, 'assessment')
    require(assessment.get('rubric_sha256') == gate.fingerprint(rubric),
            'rubric changed: review all affected candidates against the same version')
    require(assessment.get('catalog_sha256') == gate.fingerprint(db),
            'catalog snapshot changed: review assessment sources, not existing production locks')
    candidates = assessment.get('candidates')
    require(isinstance(candidates, list), 'candidates: expected list')
    for c in candidates:
        fields(c, ('profile_id',), 'candidate')
    actual_ids = [c['profile_id'] for c in candidates]
    require(len(actual_ids) == len(set(actual_ids)), 'duplicate candidate IDs')
    require(set(actual_ids) == set(ids), 'candidate ledger must exactly cover declared comparison scope')
    names = {p['id']: p for p in db['profiles']}
    results = []
    for candidate in candidates:
        scored = validate_candidate(candidate)
        pid = candidate['profile_id']
        if pid in names:
            require(profile_name_matches(names[pid], candidate['name']), f'{pid}: name does not match catalog identity')
        elif scored:
            require(candidate['name'] != pid, f'{pid}: replace the external placeholder with verified name')
        result = copy.deepcopy(candidate)
        complete = len(scored) == len(DEFAULT_WEIGHTS)
        result['score'] = round(sum(candidate['dimensions'][k]['score'] * rubric['criteria'][k]['weight']
                                    for k in DEFAULT_WEIGHTS) / 5, 1) if complete else None
        if any(c['severity'] == 'blocking' for c in candidate['conflicts']):
            status = 'blocking_conflict'
        elif not complete:
            status = 'pending'
        elif candidate['conflict_review']['status'] != 'complete':
            status = 'conflict_unchecked'
        elif candidate['conflicts']:
            status = 'conditional'
        else:
            status = 'eligible'
        result.update(status=status, rank=None)
        results.append(result)
    # Only complete, conflict-reviewed non-blocking candidates are rankable.
    rankable = sorted((r for r in results if r['status'] in ('eligible', 'conditional')),
                      key=lambda r: -r['score'])
    last_score, last_rank = None, None
    for index, row in enumerate(rankable, 1):
        if row['score'] != last_score:
            last_rank = index
        row['rank'] = last_rank
        last_score = row['score']
    by_id = {r['profile_id']: r for r in results}
    counts = {'total': len(results), 'fully_scored': sum(r['score'] is not None for r in results),
              'pending_scores': sum(r['score'] is None for r in results),
              'not_reviewed': sum(r['research_status'] == 'not_reviewed' for r in results),
              'rankable': len(rankable)}
    groups = {s: [r['profile_id'] for r in results if r['status'] == s]
              for s in ('eligible', 'conditional', 'pending', 'conflict_unchecked', 'blocking_conflict')}
    return {'revision': REVISION, 'workflow_scope': 'diagnostic', 'automatic_selection': False,
            'production_authorized': False, 'authority': validate_authority(current_authority),
            'rubric_ref': {'id': rubric['id'], 'version': rubric['version'], 'sha256': gate.fingerprint(rubric)},
            'assessment_ref': {'id': assessment['id'], 'version': assessment['version'],
                               'sha256': gate.fingerprint(assessment)},
            'catalog_sha256': gate.fingerprint(db), 'comparison': copy.deepcopy(rubric['comparison']),
            'weights': {k: v['weight'] for k, v in rubric['criteria'].items()},
            'counts': counts, 'groups': groups,
            'ranking': [{'profile_id': r['profile_id'], 'score': r['score'], 'rank': r['rank'],
                         'status': r['status'], 'confidence': r['confidence']} for r in rankable],
            'candidates': [by_id[pid] for pid in ids],
            'notice': 'Ranking is only among assessed, conflict-reviewed candidates in this scope. '
                      'Rankability is not a recommendation; all candidates may be unsuitable. '
                      'Ties remain ties. Evidence truth, reading completeness and artistic quality '
                      'are not machine-verified. No selection or production authorization.'}


def read_json(path):
    def reject_constant(value):
        raise ValueError(f'non-finite JSON number: {value}')
    def no_duplicate_keys(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, f'duplicate JSON key: {key}')
            result[key] = value
        return result
    return json.loads(Path(path).read_text(encoding='utf-8'), parse_constant=reject_constant,
                      object_pairs_hook=no_duplicate_keys)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    for name in ('fingerprint', 'prepare', 'evaluate'):
        command = commands.add_parser(name)
        command.add_argument('rubric')
        if name == 'evaluate':
            command.add_argument('assessment')
            command.add_argument('--authority', required=True)
    args = parser.parse_args()
    try:
        rubric = read_json(args.rubric)
        if args.command == 'evaluate':
            result = evaluate(rubric, read_json(args.assessment), read_json(args.authority))
        elif args.command == 'prepare':
            result = prepare(rubric)
        else:
            validate_rubric(rubric)
            result = {'sha256': gate.fingerprint(rubric), 'automatic_selection': False}
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return 0
    except (ValueError, OSError, UnicodeError) as exc:
        print(json.dumps({'ok': False, 'error': str(exc), 'production_authorized': False}, ensure_ascii=False))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
