"""Behavior tests for public method choices and one-folder distribution."""
from __future__ import annotations

import copy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skill/shotloom"
DIRECTOR = SKILL / "modules/director/scripts"
GENERATION = SKILL / "modules/generation/scripts"
sys.path.insert(0, str(DIRECTOR))
sys.path.insert(0, str(GENERATION))
import director_style as gate
import source_lock_check as source_gate


def authored_packet():
    authority = {"project_id": "fixture-project", "work_scope": "one complete fictional scene", "script_version": "1"}
    lock = {
        "schema_version": 1, "id": "method-fixture", "version": "1", "status": "selected",
        "method_mode": "project_authored", "authority": authority,
        "project_method": {"name": "Shared space, delayed answer", "design_basis": "This fictional handoff scene is carried by visible task and listener attention."},
        "authorization": {"mode": "user_approved", "source": "synthetic test approval, never real authority", "scope": "fixture scene"},
        "fit_basis": {"reading_scope": "complete_authoritative_scope", "rationale": "Keep both people and the handoff readable.",
                      "script_evidence": ["synthetic-scene:1-4"], "countercase": "A private thought needs a different viewpoint."},
        "evidence": [{"id": "design-1", "source": "synthetic-scene:1-4", "scope": "fixture only",
                      "supported_claim": "A shared frame is an authored design, not a historical director fact.",
                      "kind": "project_design", "checked_at": "2026-10-04"}],
        "adopted_methods": {key: "Fixture design: preserve the shared task and required response." for key in gate.METHODS},
        "excluded_methods": ["No cut concealing the required handoff"], "preserved_locks": ["exact line and prop ownership"],
        "review_criteria": ["The receiver obtains the prop before answering"], "variation_policy": "Optional gaze can vary; ownership cannot.",
    }
    return {"workflow_scope": "production", "current_authority": authority, "director_style_lock": lock,
            "director_style_ref": {"id": lock["id"], "version": lock["version"], "sha256": gate.fingerprint(lock)}}


def rebind(packet):
    packet["director_style_ref"]["sha256"] = gate.fingerprint(packet["director_style_lock"])


class PublicMethodTests(unittest.TestCase):
    def test_original_method_passes_all_five_stages_without_a_person(self):
        for stage in gate.STAGES:
            with self.subTest(stage=stage):
                self.assertEqual([], gate.validate_handoff(authored_packet(), stage))

    def test_original_method_passes_real_image_video_and_audio_source_gate(self):
        for media in ("image", "video", "audio"):
            packet = authored_packet()
            packet.update(media_type=media, production_level="formal", authority_sources_and_versions=["synthetic-script-v1"],
                          appearance_family="hand_drawn_2d", required_endpoint="B holds the key", review_criteria=["transfer visible"], reference_manifest=[])
            if media == "video":
                packet["sound_ownership_plan"] = {"sound_events": [], "compiled_generation_audio_ids": [], "post_handoff_ids": []}
            if media == "audio":
                packet.pop("appearance_family")
                packet["audio_brief"] = {key: "Fictional audio design" for key in
                    ("purpose", "content", "timing", "voice_or_source_identity", "acoustic_perspective", "usage_authority")}
                packet["audio_brief"].update(delivery_role="guide", sound_ids=["line-1"])
            self.assertEqual([], source_gate.validate_source_lock(packet), media)

    def test_custom_is_not_an_approval_or_stale_version_bypass(self):
        mutations = [lambda p: p["director_style_lock"].pop("authorization"),
                     lambda p: p["current_authority"].update(script_version="changed"),
                     lambda p: p["director_style_ref"].update(version="old"),
                     lambda p: p["director_style_lock"]["adopted_methods"].update(camera=""),
                     lambda p: p["director_style_lock"]["fit_basis"].update(reading_scope="excerpt"),
                     lambda p: p["director_style_lock"].update(method_mode="anything")]
        for mutation in mutations:
            packet = copy.deepcopy(authored_packet())
            # Break shared in-memory authority identity just as serialized data does.
            packet = json.loads(json.dumps(packet))
            mutation(packet)
            rebind(packet)
            self.assertTrue(gate.validate_handoff(packet))

    def test_custom_cannot_smuggle_named_identity_or_drop_design_basis(self):
        for change in ({"lead": {"profile_id": "invented", "name": "Famous director"}}, {"project_method": {"name": "Cinematic"}}):
            packet = authored_packet(); packet["director_style_lock"].update(change); rebind(packet)
            self.assertTrue(gate.validate_handoff(packet))

    def test_named_path_cannot_use_original_design_as_historical_evidence(self):
        packet = authored_packet()
        packet["director_style_lock"]["method_mode"] = "named_reference"
        rebind(packet)
        self.assertTrue(gate.validate_handoff(packet))

    def test_single_folder_works_relocated_without_installed_siblings(self):
        with tempfile.TemporaryDirectory(prefix="shotloom-portability-") as folder:
            target = Path(folder) / "isolated folder" / "shotloom"
            shutil.copytree(SKILL, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            packet = Path(folder) / "packet.json"
            packet.write_text(json.dumps(authored_packet()), encoding="utf-8")
            env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
            for stage in gate.STAGES:
                result = subprocess.run([sys.executable, "-B", str(target / "modules/director/scripts/director_style.py"),
                                         "check", str(packet), "--stage", stage], cwd=folder, env=env, text=True, capture_output=True)
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            packet_data = authored_packet()
            packet_data.update(media_type="image", production_level="formal", authority_sources_and_versions=["script-v1"],
                               appearance_family="other", required_endpoint="still", review_criteria=["shape"], reference_manifest=[])
            packet.write_text(json.dumps(packet_data), encoding="utf-8")
            result = subprocess.run([sys.executable, "-B", str(target / "modules/generation/scripts/source_lock_check.py"), str(packet)],
                                    cwd=folder, env=env, text=True, capture_output=True)
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
