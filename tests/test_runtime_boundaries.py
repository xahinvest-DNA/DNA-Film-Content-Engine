from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from runtime.project_slice import ProjectSliceStore


SAMPLE_ANALYSIS = """
The film analysis opens with a claim about inherited fear.

Because ritualized behavior turns fear into routine, the middle section explains the mechanism.

The last paragraph reframes the ending as a transition toward refusal.
""".strip()


class RuntimeBoundaryTests(unittest.TestCase):
    def test_manifest_remains_light_while_records_hold_editable_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))
            project = store.create_project("Boundary Map", film_title="Demo Film", language="en")
            project = store.save_analysis_text(project.project_dir, SAMPLE_ANALYSIS)

            manifest = json.loads((project.project_dir / "project.manifest").read_text(encoding="utf-8"))
            self.assertIn("primary_project_record", manifest)
            self.assertIn("primary_analysis_source_record", manifest)
            self.assertNotIn("semantic_blocks", manifest)
            self.assertNotIn("analysis_text", manifest)

            semantic_payload = json.loads((project.project_dir / "records" / "semantic" / "semantic_blocks.json").read_text(encoding="utf-8"))
            self.assertEqual(len(project.semantic_blocks), len(semantic_payload["blocks"]))

    def test_load_project_recreates_missing_status_payload(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))
            project = store.create_project("Boundary Status", film_title="Demo Film", language="en")
            project = store.save_analysis_text(project.project_dir, SAMPLE_ANALYSIS)
            status_path = project.project_dir / "project.meta" / "status.json"
            status_path.unlink()

            reloaded = store.load_project(project.project_dir)

            self.assertTrue(status_path.exists())
            recreated_status = json.loads(status_path.read_text(encoding="utf-8"))
            self.assertEqual(len(reloaded.semantic_blocks), recreated_status["semantic_block_count"])
            self.assertEqual(reloaded.semantic_review_record["review_status"], recreated_status["current_approval_state"])


if __name__ == "__main__":
    unittest.main()
