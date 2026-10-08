"""Shared value/identity contracts for the five drama skills, not creative approval."""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
import math
import re


EVIDENCE_KINDS = ('creator_account', 'collaborator_account', 'production_primary',
                  'work_observation', 'critical_analysis')
EVIDENCE_ALIASES = {'creator_interview': 'creator_account',
                    'collaborator_interview': 'collaborator_account',
                    'production_primary_excerpt': 'production_primary'}


def text(value):
    return isinstance(value, str) and bool(value.strip())


def meaningful(value):
    """Descriptive content: nonblank text or finite JSON structure containing it.

    Bare booleans/numbers, blank leaves and empty containers cannot stand in for
    a required decision. Numbers/bools inside a genuinely described object are
    allowed (e.g. a sync anchor with time 0, or outlines explicitly disabled).
    """
    def finite_json(item):
        if item is None or isinstance(item, (str, bool)):
            return True
        if type(item) in (int, float):
            return math.isfinite(item)
        if isinstance(item, list):
            return all(finite_json(v) for v in item)
        if isinstance(item, dict):
            return all(text(k) and finite_json(v) for k, v in item.items())
        return False

    def description(item):
        if text(item):
            return True
        if isinstance(item, list):
            return bool(item) and all(description(v) for v in item)
        if isinstance(item, dict):
            return bool(item) and any(description(v) for v in item.values())
        return False

    return finite_json(value) and description(value)


def digest(value):
    return isinstance(value, str) and re.fullmatch(r'[0-9a-f]{64}', value) is not None


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


def interval(value):
    return (isinstance(value, list) and len(value) == 2
            and all(number(x) for x in value) and 0 <= value[0] < value[1])


def decimal_seconds(value):
    if isinstance(value, bool) or not isinstance(value, (str, int, float, Decimal)):
        raise ValueError('time must be finite decimal seconds')
    try:
        result = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError('time must be finite decimal seconds') from exc
    if not result.is_finite():
        raise ValueError('time must be finite decimal seconds')
    return result


def canonical_evidence_kind(value):
    """Normalize legacy vocabulary only; never upgrade evidence strength."""
    return EVIDENCE_ALIASES.get(value, value) if isinstance(value, str) else None


def external_id(value):
    return text(value) and re.fullmatch(r'external:[a-z0-9]+(?:-[a-z0-9]+)*', value) is not None


def profile_name_matches(profile, name):
    # Preserve canonical Chinese/English names; no fuzzy matching of people.
    return text(name) and name.strip() in {profile['name_zh'], profile['name_en'], *profile.get('name_aliases', [])}
