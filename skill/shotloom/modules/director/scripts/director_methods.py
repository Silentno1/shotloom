"""Read-only conditional-method retrieval; never select, score or approve production."""
import argparse
import hashlib
import json
from pathlib import Path

REFERENCES = Path(__file__).resolve().parent.parent / 'references'
DIMENSIONS = ('performance', 'blocking', 'camera', 'editing', 'sound', 'transitions')
FIELDS = ('question', 'when', 'choice', 'alternative', 'countercase', 'review')
POLICY = {'authored_applications': True,
          'source_facts': 'director-profiles.json only; each card retains its own scope',
          'not_for_production': True, 'default_generation_calls': 0,
          'automatic_selection': False, 'joint_directing': 'deferred'}


def load():
    raw = (REFERENCES / 'director-profiles.json').read_bytes()
    return (json.loads(raw),
            json.loads((REFERENCES / 'director-decision-methods.json').read_text()),
            hashlib.sha256(raw).hexdigest())


def audit(catalog, guide, digest):
    """Validate coverage/provenance/declared bounds, not prose truth or artistic quality."""
    errors = []
    if guide.get('schema_version') != 1:
        errors.append('unsupported schema')
    if not isinstance(guide.get('revision'), str) or not guide['revision'].strip():
        errors.append('missing guide revision')
    if guide.get('catalog_revision') != catalog.get('revision') or guide.get('catalog_sha256') != digest:
        errors.append('catalog changed: review derived guidance; do not revoke project locks')
    if guide.get('policy') != POLICY:
        errors.append('research-only policy changed')
    canonical = {p['id']: p for p in catalog['profiles']}
    entries = guide.get('profiles')
    if not isinstance(entries, list):
        return errors + ['profiles must be a list']
    seen = set()
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get('profile_id'), str):
            errors.append('invalid profile entry')
            continue
        pid = entry['profile_id']
        if pid in seen:
            errors.append(f'{pid}: duplicate')
        seen.add(pid)
        if pid not in canonical:
            errors.append(f'{pid}: unknown profile')
            continue
        if entry.get('status') != 'authored_application_not_director_fact':
            errors.append(f'{pid}: application must not claim sourced fact')
        for field in FIELDS:
            if not isinstance(entry.get(field), str) or not entry[field].strip():
                errors.append(f'{pid}: missing {field}')
        owned = {c['id'] for c in canonical[pid]['method_cards']}
        basis = entry.get('basis_card_ids')
        if (not isinstance(basis, list) or not all(isinstance(x, str) for x in basis)
                or not basis or len(basis) != len(set(basis)) or set(basis) != owned):
            errors.append(f'{pid}: missing, foreign or duplicate basis card')
    if seen != set(canonical):
        errors.append('coverage must match current catalog exactly')
    return errors


def profile(pid, catalog, guide, digest):
    errors = audit(catalog, guide, digest)
    if errors:
        raise ValueError('; '.join(errors))
    source = next((p for p in catalog['profiles'] if p['id'] == pid), None)
    if source is None:
        raise ValueError(f'unknown profile: {pid}')
    application = next(p for p in guide['profiles'] if p['profile_id'] == pid)
    covered = {d for c in source['method_cards'] for d in c['dimensions']}
    return {
        'workflow_scope': 'diagnostic',
        'research': {'purpose': 'conditional method research', 'not_for_production': True},
        'revision': guide['revision'], 'catalog_revision': catalog['revision'],
        'default_generation_calls': 0, 'automatic_selection': False,
        'profile': source, 'authored_application': application,
        'source_card_dimensions': sorted(covered),
        'dimensions_without_source_card': [d for d in DIMENSIONS if d not in covered],
        'boundary': ('Card dimensions do not prove all methods in that dimension. '
                     'Keep each card scope and evidence limits; other choices are project design. '
                     'No selection, production approval, generation or project mutation.')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('audit')
    sub.add_parser('profile').add_argument('id')
    args = parser.parse_args()
    try:
        catalog, guide, digest = load()
        if args.command == 'audit':
            errors = audit(catalog, guide, digest)
            result = {'ok': not errors, 'errors': errors,
                      'profiles': len(guide['profiles']),
                      'scope': 'structure and provenance only; not artistic validation'}
        else:
            result = profile(args.id, catalog, guide, digest)
            errors = []
    except (ValueError, OSError, KeyError, TypeError) as exc:
        result, errors = {'ok': False, 'error': str(exc)}, [str(exc)]
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
