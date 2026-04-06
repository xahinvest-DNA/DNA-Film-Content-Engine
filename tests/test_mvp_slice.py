from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from runtime.project_slice import ProjectSliceStore


SAMPLE_ANALYSIS = """
The opening movement argues that the film is really about inherited fear rather than simple survival. The critic frames the family house as a system that teaches each character how to obey the past.

Because the mother keeps translating danger into ritual, the essay reveals how ordinary domestic behavior becomes a mechanism of control. That repeated behavior gives the audience a way to feel the pressure before any explicit explanation arrives.

However, the final section suggests that the film does not stay inside despair. It shows a transition from passive inheritance toward a more conscious refusal to repeat the same emotional pattern.
""".strip()


class ProjectSliceStoreTests(unittest.TestCase):
    def test_create_project_and_build_semantic_map(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))
            project = store.create_project("Hereditary Essay", film_title="Hereditary", language="en")

            self.assertTrue((project.project_dir / "project.manifest").exists())
            self.assertEqual(project.project_record["project_status"], "intake_required")
            self.assertEqual(project.intake_record["intake_readiness"], "blocked")

            updated = store.save_analysis_text(project.project_dir, SAMPLE_ANALYSIS)

            self.assertEqual(updated.intake_record["intake_readiness"], "ready")
            self.assertEqual(updated.project_record["project_status"], "semantic_map_ready")
            self.assertEqual(len(updated.semantic_blocks), 3)
            self.assertTrue((updated.project_dir / "sources" / "analysis" / "analysis.txt").exists())
            self.assertTrue((updated.project_dir / "records" / "semantic" / "semantic_blocks.json").exists())

            first_block = updated.semantic_blocks[0]
            self.assertEqual(first_block["record_type"], "semantic_block")
            self.assertEqual(first_block["sequence"], 1)
            self.assertIn(first_block["semantic_role"], {"claim", "insight", "mechanism", "transition", "emotional_beat"})

    def test_analysis_text_must_be_meaningful(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))
            project = store.create_project("Short Input")

            with self.assertRaises(ValueError):
                store.save_analysis_text(project.project_dir, "Too short")


if __name__ == "__main__":
    unittest.main()
