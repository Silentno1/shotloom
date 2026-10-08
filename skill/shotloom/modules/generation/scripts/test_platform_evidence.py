#!/usr/bin/env python3
import unittest

import platform_evidence_check as checker


class PlatformEvidenceTests(unittest.TestCase):
    def valid(self):
        return {
            "platform": "MiniMax",
            "model": "H3",
            "surface": "official API",
            "required_claims": ["duration"],
            "claims": [{
                "id": "duration",
                "value": "4-15 seconds",
                "evidence_level": "official-current",
                "verified_at": "2026-09-04",
                "source": "https://github.com/MiniMax-AI/MiniMax-H3",
            }],
        }

    def test_current_official_evidence_can_support_required_claim(self):
        self.assertEqual(checker.validate_evidence(self.valid()), [])

    def test_community_observation_cannot_support_required_claim(self):
        data = self.valid()
        data["claims"][0]["evidence_level"] = "community-observation"
        self.assertTrue(any("needs official-current" in item for item in checker.validate_evidence(data)))

    def test_project_verified_requires_artifact_and_hash(self):
        data = self.valid()
        data["claims"][0]["evidence_level"] = "project-verified"
        errors = checker.validate_evidence(data)
        self.assertTrue(any("artifact" in item for item in errors))
        self.assertTrue(any("result_hash" in item for item in errors))


if __name__ == "__main__":
    unittest.main()
