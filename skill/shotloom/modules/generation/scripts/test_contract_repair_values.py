"""Executable contracts reject fake descriptions without breaking typed controls."""
import unittest
import source_lock_check as source
import sound_contract_check as sound
import test_source_lock as source_fixture
import test_sound_ownership_contract as sound_fixture


class ValueRepairTests(unittest.TestCase):
    def test_source_required_descriptions_are_not_false_zero_or_null_lists(self):
        for key in ('required_endpoint', 'review_criteria', 'authority_sources_and_versions'):
            for value in (False, 0, ' ', [None]):
                packet = source_fixture.SourceLockTests().valid(); packet[key] = value
                self.assertTrue(source.validate_source_lock(packet), (key, value))

    def test_reference_roles_need_text_but_zero_priority_is_valid(self):
        packet = source_fixture.SourceLockTests().valid(); packet['reference_manifest'][0]['priority'] = 0
        self.assertEqual(source.validate_source_lock(packet), [])
        for key in ('primary_role', 'allowed_transfer', 'forbidden_transfer'):
            packet = source_fixture.SourceLockTests().valid(); packet['reference_manifest'][0][key] = False
            self.assertTrue(source.validate_source_lock(packet))

    def test_nontext_prompt_returns_error_not_exception(self):
        for value in (0, False, [], {}, ['prompt']):
            result = sound.check_sound_contract(sound_fixture.SoundOwnershipContractTests().valid(), value)
            self.assertTrue(result['errors'])

    def test_post_handoff_cannot_be_false_or_empty_container(self):
        for value in (False, 0, ' ', [None], {}):
            packet = sound_fixture.SoundOwnershipContractTests().valid(); packet['sound_events'][0]['post_handoff'] = value
            self.assertTrue(sound.validate_sound_contract(packet))

    def test_sync_anchor_can_start_at_zero(self):
        packet = sound_fixture.SoundOwnershipContractTests().valid()
        packet['sound_events'][0]['sync_anchor'] = {'start_seconds': 0, 'cue': 'first mouth opening'}
        self.assertEqual(sound.validate_sound_contract(packet), [])

    def test_wrong_director_cannot_enter_source_snapshot(self):
        packet = source_fixture.SourceLockTests().valid()
        packet['director_style_lock']['lead']['name'] = 'Wong Kar-wai'
        import director_style
        packet['director_style_ref']['sha256'] = director_style.fingerprint(packet['director_style_lock'])
        self.assertTrue(source.validate_source_lock(packet))


if __name__ == '__main__': unittest.main()
