#!/usr/bin/env python3
"""Read-only catalog contract audit. Does not certify source truth or approve production."""
import json
from pathlib import Path

import director_style as gate
from drama_contracts import EVIDENCE_KINDS, canonical_evidence_kind

CONTRACT = Path(__file__).resolve().parents[1] / 'references/director-acceptance.json'
DIMS = ('performance', 'blocking', 'camera', 'editing', 'sound', 'transitions')


def acceptance():
    return json.loads(CONTRACT.read_text(encoding='utf-8'))


def audit(profiles_db, routes_db, contract):
    """Validate provenance edges and promised executable routes, not just text presence."""
    errors = []
    def require(condition, message):
        if not condition:
            errors.append(message)
    try:
        profiles = profiles_db['profiles']
        by_id = {p['id']: p for p in profiles}
        require(len(by_id) == len(profiles), 'duplicate profile identity')
        require(profiles_db['revision'] == routes_db['revision'] == contract['revision'], 'revision mismatch')
        require(profiles_db['method_contract']['joint_directing'] == 'not_implemented', 'joint directing must remain deferred')
        require(routes_db['completion_contract']['joint_directing'] == 'deferred', 'route joint directing mismatch')
        for key in ('automatic_selection', 'automatic_style_lock', 'ranked'):
            require(routes_db['selection_policy'][key] is False, 'retrieval must not select: ' + key)
        require(routes_db['selection_policy']['medium_independent'] is True, 'medium independence required')
        require(len(routes_db['topics']) == 14, '14 agreed topic families required')
        require(len(routes_db['mechanisms']) == 7, 'mechanisms must remain separate')
        policy = routes_db.get('facet_policy', {})
        require(policy.get('activation') == 'approved_scene_need_not_genre_label', 'facets need scene-specific activation')
        require(policy.get('acceptance_basis') == 'approved_project_intent_not_example_reproduction', 'facet examples cannot be acceptance standards')
        require(policy.get('may_add_story_facts') is False and policy.get('unused_option_is_failure') is False, 'facet options cannot add facts or mandate usage')
        for p in profiles:
            pid = p['id']
            evidence = {e['id']: e for e in p['evidence_notes']}
            for e in evidence.values():
                require(canonical_evidence_kind(e.get('kind')) in EVIDENCE_KINDS, pid + ': invalid evidence kind')
            require(len(evidence) == len(p['evidence_notes']), pid + ': duplicate evidence id')
            require(any(e.get('status') == 'claim_checked' for e in evidence.values()), pid + ': no checked scoped claim')
            cards = {m['id']: m for m in p['method_cards']}
            require(bool(cards) and len(cards) == len(p['method_cards']), pid + ': missing or duplicate method cards')
            for mid, m in cards.items():
                require(m['status'] == 'sourced_fact_with_authored_adaptation', mid + ': false proof status')
                for key in ('scope', 'source_fact', 'adaptation', 'countercase', 'verification'):
                    require(gate.nonempty(m[key]), mid + ': missing ' + key)
                require(gate.strings(m['dimensions']) and set(m['dimensions']) <= set(DIMS), mid + ': invalid dimensions')
                require(gate.strings(m['evidence_ids']), mid + ': no evidence edge')
                resolved = [evidence.get(eid) for eid in m['evidence_ids']]
                require(all(e and e.get('status') == 'claim_checked' for e in resolved), mid + ': unchecked/dangling evidence')
                # A card may only restate the checked claim it actually references.
                require(any(e and e['supported_claim'] == m['source_fact'] and e['scope'] == m['scope'] for e in resolved), mid + ': unsupported fact or scope expansion')
            require(set(p['method_basis']) == set(DIMS), pid + ': incomplete dimension ledger')
            require(set(p['transfer_hypotheses']) == set(DIMS), pid + ': missing authored method dimension')
            for dim in DIMS:
                basis = p['method_basis'][dim]
                require(basis['status'] == 'authored_transfer_not_director_fact', pid + ': suggestions presented as historical fact')
                expected = {mid for mid, m in cards.items() if dim in m['dimensions']}
                require(isinstance(basis['related_method_cards'], list), pid + ': method references must be a list')
                require(set(basis['related_method_cards']) == expected, pid + ': wrong-dimension provenance ' + dim)
                require(gate.nonempty(basis['use_rule']), pid + ': missing provenance use rule')
        routes = {}
        routed = set()
        for t in routes_db['topics']:
            for b in t['branches']:
                key = (t['id'], b['id'])
                require(key not in routes, 'duplicate branch ' + str(key))
                routes[key] = b
                require(bool(b['execution_facets']), 'branch without actionable facets ' + str(key))
                for f in b['execution_facets']:
                    for field in ('id', 'term', 'decision', 'execute', 'acceptance', 'when', 'countercase'):
                        require(gate.nonempty(f[field]), 'facet missing ' + field + ': ' + str(key))
                    require(f.get('role') == 'conditional_method_option', 'facet must be a conditional option')
                    require(f['basis'] == 'authored_production_design_not_director_quote', 'genre design falsely attributed to director')
                    require(gate.term_matches(f['term'], b), 'facet not retrievable: ' + f['term'])
                require(bool(b['options']), 'branch without candidate')
                for option in b['options']:
                    pid = option['profile_id']; routed.add(pid)
                    require(pid in by_id, 'unknown candidate ' + pid)
                    known_cards = {m['id'] for m in by_id.get(pid, {}).get('method_cards', [])}
                    require(gate.strings(option['method_cards']) and set(option['method_cards']) <= known_cards, 'candidate missing/dangling method cards: ' + pid)
                    require(gate.nonempty(option['reference_boundary']), 'missing candidate evidence boundary')
        require(routed == set(by_id), 'unrouted profile')
        for row in contract['promised_routes']:
            key = (row['topic_id'], row['branch_id'])
            b = routes.get(key)
            require(bool(b), 'promised branch missing: ' + str(key))
            if b:
                require(any(f['term'] == row['term'] for f in b['execution_facets']), 'promise has alias but no execution: ' + row['term'])
                require(gate.term_matches(row['term'], b), 'promised query not registered: ' + row['term'])
        for term, specialists in contract['required_specialists'].items():
            matched = [b for b in routes.values() if gate.term_matches(term, b)]
            found = {o['profile_id'] for b in matched for o in b['options']}
            require(set(specialists) <= found, 'specialty downgraded to generic transfer: ' + term)
    except (KeyError, TypeError, AttributeError) as exc:
        errors.append('malformed catalog contract: ' + str(exc))
    return errors


def main():
    try:
        p, c, a = gate.catalog(), gate.coverage(), acceptance()
        errors = audit(p, c, a)
        print(json.dumps({'ok': not errors, 'revision': p['revision'],
            'scope': 'catalog-structure-provenance-edges-and-promised-routes-only',
            'production_authorized': False, 'source_truth_automatically_proven': False,
            'profiles': len(p['profiles']), 'branches': sum(len(t['branches']) for t in c['topics']),
            'promised_route_cases': len(a['promised_routes']), 'errors': errors}, ensure_ascii=False, indent=2))
        return 2 if errors else 0
    except (OSError, ValueError) as exc:
        print(json.dumps({'ok': False, 'errors': [str(exc)]}, ensure_ascii=False))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
