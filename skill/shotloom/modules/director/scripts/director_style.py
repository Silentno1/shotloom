#!/usr/bin/env python3
"""Read-only director catalog and production handoff gate; never selects or approves."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from drama_contracts import EVIDENCE_KINDS, canonical_evidence_kind, external_id, profile_name_matches

CATALOG = Path(__file__).resolve().parents[1] / 'references/director-profiles.json'
COVERAGE = Path(__file__).resolve().parents[1] / 'references/director-coverage.json'
STAGES = ('director', 'visual', 'generation', 'edit', 'review')
METHODS = ('performance', 'blocking', 'viewpoint', 'camera', 'time', 'editing', 'sound', 'transitions')
AUTHORITY = ('project_id', 'work_scope', 'script_version')


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def strings(value):
    return isinstance(value, list) and bool(value) and all(nonempty(x) for x in value)


def catalog():
    return json.loads(CATALOG.read_text(encoding='utf-8'))


def coverage():
    return json.loads(COVERAGE.read_text(encoding='utf-8'))


def term_matches(term, row):
    return term.casefold() in {s.casefold() for s in
                              (row['id'], row['label'], *row.get('aliases', []))}


def topic(query):
    if not nonempty(query):
        raise ValueError('topic requires a non-empty ID or exact alias')
    matches = [t for t in coverage()['topics'] if term_matches(query.strip(), t)]
    if len(matches) != 1:
        raise ValueError('unknown or ambiguous topic; inspect topics or use find with exact terms')
    return matches[0]


def find_terms(query):
    """Exact registered terms only: separate route lookup from creative selection."""
    if not nonempty(query):
        raise ValueError('find requires non-empty registered terms')
    terms = list(dict.fromkeys(t.casefold() for t in re.split(r'[\s,+，、]+', query.strip()) if t))
    if not terms:
        raise ValueError('find requires terms, not only separators')
    db = coverage()
    matches, unknown, media, seen = [], [], [], set()
    for term in terms:
        found = False
        if term in {m.casefold() for m in db['medium_terms']}:
            media.append(term)
            found = True
        for t in db['topics']:
            if term_matches(term, t):
                found = True
                key = ('topic', t['id'])
                if key not in seen:
                    seen.add(key)
                    matches.append({'kind': 'topic', 'topic': t})
            for b in t['branches']:
                if term_matches(term, b):
                    found = True
                    key = ('branch', t['id'], b['id'])
                    if key not in seen:
                        seen.add(key)
                        matches.append({'kind': 'branch', 'topic_id': t['id'],
                                        'topic_label': t['label'], 'branch': b})
        for m in db['mechanisms']:
            if term_matches(term, m):
                found = True
                key = ('mechanism', m['id'])
                if key not in seen:
                    seen.add(key)
                    matches.append({'kind': 'mechanism', 'mechanism': m})
        if not found:
            unknown.append(term)
    return {'scope': 'research-retrieval-only', 'ranked': False,
            'automatic_selection': False, 'matches': matches, 'unmatched_terms': unknown,
            'medium_terms': media, 'medium_notice': db['medium_notice'] if media else None,
            'notice': 'Exact aliases, not semantic classification. Read route limits and profile evidence; '
                      'no selection, approval, production readiness or generation authority is established.'}


def fingerprint(lock):
    return hashlib.sha256(json.dumps(lock, ensure_ascii=False, sort_keys=True,
                                   separators=(',', ':'), allow_nan=False).encode('utf-8')).hexdigest()


def validate_lock(lock):
    if not isinstance(lock, dict):
        return ['director_style_lock must be an object; formal production requires an approved directing method']
    errors = []
    method_mode = lock.get('method_mode', 'named_reference')
    if method_mode not in ('named_reference', 'project_authored'):
        errors.append('method_mode must be named_reference or project_authored')
    if type(lock.get('schema_version')) is not int or lock['schema_version'] != 1:
        errors.append('style schema_version must be 1')
    for key in ('id', 'version', 'variation_policy'):
        if not nonempty(lock.get(key)):
            errors.append(f'style {key} must be non-empty text')
    if lock.get('status') != 'selected':
        errors.append('style status must be selected')
    auth = lock.get('authority')
    if not isinstance(auth, dict) or any(not nonempty(auth.get(k)) for k in AUTHORITY):
        errors.append('style authority requires project_id, work_scope and script_version')
    approval = lock.get('authorization')
    if not isinstance(approval, dict):
        errors.append('style authorization must be an object')
    else:
        if approval.get('mode') not in ('user_selected', 'user_approved', 'ai_selection_delegated'):
            errors.append('style selection needs user selection, approval or explicit AI delegation')
        for key in ('source', 'scope'):
            if not nonempty(approval.get(key)):
                errors.append(f'style authorization.{key} required')
    fit = lock.get('fit_basis')
    if not isinstance(fit, dict):
        errors.append('style fit_basis must be an object')
    else:
        if fit.get('reading_scope') != 'complete_authoritative_scope':
            errors.append('style fit requires complete_authoritative_scope, not excerpts or tags')
        for key in ('rationale', 'countercase'):
            if not nonempty(fit.get(key)):
                errors.append(f'style fit_basis.{key} required')
        if not strings(fit.get('script_evidence')):
            errors.append('style fit_basis.script_evidence needs locations in the actual script')
    evidence = lock.get('evidence')
    ids = set()
    if not isinstance(evidence, list) or not evidence:
        errors.append('style evidence must contain scoped, checked claims')
    else:
        for row in evidence:
            if not isinstance(row, dict):
                errors.append('style evidence entry must be an object')
                continue
            for key in ('id', 'source', 'scope', 'supported_claim', 'checked_at'):
                if not nonempty(row.get(key)):
                    errors.append(f'style evidence.{key} required')
            eid = row.get('id')
            if nonempty(eid):
                if eid in ids:
                    errors.append('duplicate style evidence id')
                ids.add(eid)
            allowed_kinds = EVIDENCE_KINDS if method_mode != 'project_authored' else (
                *EVIDENCE_KINDS, 'project_design', 'user_requirement')
            if canonical_evidence_kind(row.get('kind')) not in allowed_kinds:
                errors.append('style evidence.kind must distinguish actual evidence from research leads')
    if method_mode == 'project_authored':
        method = lock.get('project_method')
        if not isinstance(method, dict) or any(not nonempty(method.get(k)) for k in ('name', 'design_basis')):
            errors.append('project_authored requires project_method.name and design_basis')
        if 'lead' in lock:
            errors.append('project_authored has no lead director identity; use named_reference for attribution')
    else:
        errors.extend(validate_named_lead(lock.get('lead'), ids))
    methods = lock.get('adopted_methods')
    if not isinstance(methods, dict) or any(not nonempty(methods.get(k)) for k in METHODS):
        errors.append('style adopted_methods must cover performance, blocking, viewpoint, camera, time, editing, sound, transitions')
    for key in ('excluded_methods', 'preserved_locks', 'review_criteria'):
        if not strings(lock.get(key)):
            errors.append(f'style {key} must be a non-empty text array')
    if 'supersedes' in lock:
        prior = lock['supersedes']
        if not isinstance(prior, dict) or any(not nonempty(prior.get(k)) for k in ('id', 'version')):
            errors.append('style supersedes requires id and version')
        elif prior['id'] == lock.get('id') and prior['version'] == lock.get('version'):
            errors.append('style replacement must use a new version or ID')
        if not nonempty(lock.get('change_authorization_source')):
            errors.append('style replacement needs change_authorization_source')
    return errors


def validate_named_lead(lead, ids):
    errors = []
    if not isinstance(lead, dict):
        errors.append('style lead must name an individual or scoped directing reference')
    else:
        pid = lead.get('profile_id')
        db = catalog()
        known = {p['id'] for p in db['profiles']}
        if not nonempty(pid):
            errors.append('style lead.profile_id required')
        elif pid in db['retired_ids']:
            errors.append('retired director profile requires a new scoped, authorized selection')
        elif pid not in known and not external_id(pid):
            errors.append('unknown director profile; use verified external:<slug> for a new reference')
        if not nonempty(lead.get('name')):
            errors.append('style lead.name required')
        elif nonempty(pid) and pid in known:
            profile = next(p for p in db['profiles'] if p['id'] == pid)
            if not profile_name_matches(profile, lead['name']):
                errors.append('style lead.name does not match catalog identity')
        elif external_id(pid) and lead['name'] == pid:
            errors.append('external lead needs a verified name, not its placeholder ID')
        refs = lead.get('reference_scope')
        if not isinstance(refs, list) or not refs:
            errors.append('style lead.reference_scope must specify actual works and scope')
        else:
            for ref in refs:
                if not isinstance(ref, dict):
                    errors.append('style reference_scope entry must be an object')
                    continue
                if any(not nonempty(ref.get(k)) for k in ('work', 'scope')):
                    errors.append('style reference_scope requires work and scope')
                links = ref.get('evidence_ids')
                if not strings(links) or any(k not in ids for k in links):
                    errors.append('style reference_scope evidence_ids must resolve to checked evidence')
    return errors


def validate_handoff(packet, stage='generation'):
    if not isinstance(packet, dict):
        return ['style handoff must be an object']
    if stage not in STAGES:
        return ['unknown style handoff stage']
    mode = packet.get('workflow_scope', 'production')
    if mode == 'diagnostic':
        return ['diagnostic is not a production-ready handoff; inspect without submission or acceptance']
    if mode == 'selection_exploration':
        ex = packet.get('exploration')
        if packet.get('production_level') not in (None, 'concept'):
            return ['selection_exploration cannot be continuity/formal production']
        if not isinstance(ex, dict) or not nonempty(ex.get('purpose')) or ex.get('not_for_production') is not True:
            return ['selection_exploration requires purpose and not_for_production: true']
        return []
    if mode != 'production':
        return ['workflow_scope must be production or explicitly bounded selection_exploration']
    lock = packet.get('director_style_lock')
    errors = validate_lock(lock)
    if not isinstance(lock, dict):
        return errors
    current = packet.get('current_authority')
    if not isinstance(current, dict) or any(not nonempty(current.get(k)) for k in AUTHORITY):
        errors.append('current_authority must be independently established from current project/script records')
    elif not isinstance(lock.get('authority'), dict) or any(current[k] != lock['authority'].get(k) for k in AUTHORITY):
        errors.append('style lock is stale or belongs to a different project/work/script')
    ref = packet.get('director_style_ref')
    if not isinstance(ref, dict):
        errors.append('artifact director_style_ref required')
    else:
        for key in ('id', 'version'):
            if ref.get(key) != lock.get(key) or not nonempty(ref.get(key)):
                errors.append(f'artifact director_style_ref.{key} differs from current style lock')
        try:
            if ref.get('sha256') != fingerprint(lock):
                errors.append('artifact director_style_ref.sha256 differs from current style lock content')
        except (ValueError, TypeError):
            errors.append('style lock must be finite JSON data')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('catalog')
    commands.add_parser('topics')
    p = commands.add_parser('topic'); p.add_argument('query')
    p = commands.add_parser('find'); p.add_argument('query')
    p = commands.add_parser('profile'); p.add_argument('id')
    p = commands.add_parser('fingerprint'); p.add_argument('file')
    p = commands.add_parser('check'); p.add_argument('file'); p.add_argument('--stage', choices=STAGES, required=True)
    args = parser.parse_args()
    try:
        if args.command == 'catalog':
            result = [{'id': p['id'], 'name': p['name_zh'], 'fit': p['fit']} for p in catalog()['profiles']]
        elif args.command == 'topics':
            db = coverage()
            result = {key: [{'id': r['id'], 'label': r['label'], 'aliases': r['aliases']}
                            for r in db[key]] for key in ('topics', 'mechanisms')}
        elif args.command == 'topic':
            result = {'scope': 'research-retrieval-only', 'automatic_selection': False,
                      'topic': topic(args.query)}
        elif args.command == 'find':
            result = find_terms(args.query)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 2 if result['unmatched_terms'] else 0
        elif args.command == 'profile':
            result = next((p for p in catalog()['profiles'] if p['id'] == args.id), None)
            if result is None:
                raise ValueError('unknown or retired profile; inspect current catalog')
        else:
            data = json.loads(Path(args.file).read_text(encoding='utf-8'))
            if args.command == 'fingerprint':
                result = {'sha256': fingerprint(data), 'approval': 'not-established-by-hash'}
            else:
                errors = validate_handoff(data, args.stage)
                result = {'ok': not errors, 'scope': 'structure-and-declared-version-only', 'errors': errors}
                print(json.dumps(result, ensure_ascii=False, indent=2))
                return 2 if errors else 0
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, TypeError) as exc:
        print(json.dumps({'ok': False, 'errors': [str(exc)]}, ensure_ascii=False))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
