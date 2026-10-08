#!/usr/bin/env python3
import unittest
import hashlib
import tempfile
from pathlib import Path

import delivery_check as checker


ROOT = Path(__file__).resolve().parents[1]


class DeliveryContractTests(unittest.TestCase):
    def test_phase_selection_preserves_picture_lock_and_export_checks(self):
        text = (ROOT / "WORKFLOW.md").read_text(encoding="utf-8")
        self.assertIn("Do not start post-production or platform research automatically", text)
        self.assertIn("Review the rough cut normally, silently and audio-only", text)
        self.assertIn("a new final export still needs technical verification", text)
        self.assertIn("packaging does not authorize publication", text)

    def valid_manifest(self, master):
        digest = hashlib.sha256(master.read_bytes()).hexdigest()
        return {
            "platform": "verified-platform",
            "production_level": "formal",
            "verification_date": "2026-09-04",
            "verification_source": "https://example.com/first-party-rule",
            "master_file": str(master),
            "master_sha256": digest,
            "technical_specs": {
                "duration_seconds": 10,
                "width": 1080,
                "height": 1920,
                "frame_rate": 24,
                "container": "mp4",
                "video_codec": "h264",
                "audio": "aac stereo",
            },
            "qc_result": {"status": "pass", "checks": [
                {"name": "picture", "status": "pass"},
                {"name": "sound", "status": "pass"},
                {"name": "captions", "status": "pass"},
            ]},
        }

    def test_platform_category_requires_current_interface(self):
        text = (ROOT / "references/release-and-compliance.md").read_text(encoding="utf-8")
        self.assertIn("actual current upload interface", text)
        self.assertIn("not the category itself", text)

    def test_timecodes_require_actual_media(self):
        text = (ROOT / "WORKFLOW.md").read_text(encoding="utf-8")
        self.assertIn("actual source files", text)
        self.assertIn("Never infer timecodes", text)

    def test_native_audio_is_decided_per_element(self):
        editing = (ROOT / "references/director-editing.md").read_text(encoding="utf-8")
        post = (ROOT / "references/post-production.md").read_text(encoding="utf-8")
        for treatment in ("retain", "clean", "supplement", "replace", "intentional_silence"):
            self.assertIn(treatment, editing)
        self.assertIn("Never impose a blanket rule", post)
        self.assertIn("Do not add ambience", editing)

    def test_failed_qc_cannot_pass(self):
        with tempfile.TemporaryDirectory() as folder:
            master = Path(folder) / "master.mp4"
            master.write_bytes(b"test-master")
            data = self.valid_manifest(master)
            data["qc_result"]["status"] = "failed"
            self.assertTrue(any("failed QC" in item for item in checker.validate_manifest(data)))

    def test_master_must_exist_and_hash_must_match(self):
        with tempfile.TemporaryDirectory() as folder:
            master = Path(folder) / "master.mp4"
            master.write_bytes(b"test-master")
            data = self.valid_manifest(master)
            data["master_sha256"] = "wrong"
            self.assertTrue(any("does not match" in item for item in checker.validate_manifest(data)))
            data["master_file"] = str(Path(folder) / "missing.mp4")
            self.assertTrue(any("must exist" in item for item in checker.validate_manifest(data)))

    def test_upload_category_must_be_observed(self):
        with tempfile.TemporaryDirectory() as folder:
            master = Path(folder) / "master.mp4"
            master.write_bytes(b"test-master")
            data = self.valid_manifest(master)
            data["upload_category"] = "2D animation"
            data["category_options_observed"] = ["3D animation"]
            self.assertTrue(any("must be one of" in item for item in checker.validate_manifest(data)))

    def test_failed_subcheck_cannot_hide_under_pass_summary(self):
        with tempfile.TemporaryDirectory() as folder:
            master = Path(folder) / "master.mp4"
            master.write_bytes(b"test-master")
            data = self.valid_manifest(master)
            data["qc_result"]["checks"][1]["status"] = "failed"
            self.assertTrue(any("not passing" in item for item in checker.validate_manifest(data)))


if __name__ == "__main__":
    unittest.main()
