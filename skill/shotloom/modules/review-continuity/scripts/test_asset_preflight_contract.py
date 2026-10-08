#!/usr/bin/env python3
import unittest

import asset_preflight as preflight


class AssetPreflightContractTests(unittest.TestCase):
    def test_json_coverage_status_distinguishes_fallback(self):
        asset = preflight.Asset("角色.png", "image", ["identity"], "unverified", 0)
        self.assertEqual(preflight.coverage_status([asset], False), "candidate-requires-inspection")
        self.assertEqual(preflight.coverage_status([asset], True), "fallback-requires-inspection")
        self.assertEqual(preflight.coverage_status([], False), "missing")


if __name__ == "__main__":
    unittest.main()
