#!/usr/bin/env python3
import unittest

import take_preflight as preflight


class TakePreflightContractTests(unittest.TestCase):
    def test_dense_range_parser(self):
        self.assertEqual(preflight.parse_dense_range("1.25:1.75"), (1.25, 1.75))

    def test_dense_range_rejects_reverse_or_negative(self):
        for value in ("2:1", "-1:2", "bad"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    preflight.parse_dense_range(value)

    def test_review_manifest_requires_auditory_review(self):
        boundary = preflight.review_boundary()
        self.assertTrue(boundary["requires_auditory_review"])
        self.assertIn("cannot replace", boundary["warning"])


if __name__ == "__main__":
    unittest.main()
