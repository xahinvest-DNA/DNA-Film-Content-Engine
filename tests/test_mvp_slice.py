from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from runtime.project_slice import ProjectSliceStore


SAMPLE_ANALYSIS = """
# Core argument
The film essay argues that the story is less about plot twists and more about inherited behavior. It frames the home as a system that teaches each character how to repeat fear.

Because the mother translates danger into ritual, the analysis reveals how ordinary domestic behavior becomes a mechanism of control. That pressure gives the audience a way to feel the theme before any explicit explanation arrives.

However, the final section suggests that the story does not stay inside despair. It points toward a transition from passive inheritance to conscious refusal.
""".strip()


class ProjectSliceStoreTests(unittest.TestCase):
    def test_create_project_builds_minimal_local_first_package(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))

            project = store.create_project("Hereditary Essay", film_title="Hereditary", language="en")

            self.assertTrue((project.project_dir / "project.manifest").exists())
            self.assertTrue((project.project_dir / "project.meta" / "status.json").exists())
            self.assertTrue((project.project_dir / "records" / "project" / "project.json").exists())
            self.assertTrue((project.project_dir / "records" / "intake" / "intake.json").exists())
            self.assertTrue((project.project_dir / "records" / "review" / "semantic_review.json").exists())
            self.assertTrue((project.project_dir / "sources" / "analysis").exists())
            self.assertTrue((project.project_dir / "derived" / "semantic").exists())
            self.assertEqual("project_created", project.project_record["project_status"])
            self.assertEqual("blocked", project.intake_record["intake_readiness"])
            self.assertEqual("under_edit", project.semantic_review_record["review_status"])

    def test_analysis_intake_creates_canonical_records_and_bootstrap_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))
            project = store.create_project("Semantic Intake", film_title="Demo Film", language="en")

            updated = store.save_analysis_text(project.project_dir, SAMPLE_ANALYSIS)

            self.assertTrue((updated.project_dir / "sources" / "analysis" / "analysis.txt").exists())
            self.assertTrue((updated.project_dir / "records" / "intake" / "analysis_source.json").exists())
            self.assertTrue((updated.project_dir / "records" / "semantic" / "semantic_blocks.json").exists())
            self.assertTrue((updated.project_dir / "derived" / "semantic" / "provisional_bootstrap.json").exists())
            self.assertEqual("ready", updated.intake_record["intake_readiness"])
            self.assertEqual("semantic_map_under_edit", updated.project_record["project_status"])
            self.assertGreaterEqual(len(updated.semantic_blocks), 3)
            self.assertEqual("analysis-source-primary", updated.analysis_source_record["record_id"])
            self.assertEqual(
                [block["record_id"] for block in updated.semantic_blocks],
                updated.semantic_bootstrap_artifact["generated_block_ids"],
            )

    def test_block_edit_and_review_state_persist_after_reload(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))
            project = store.create_project("Semantic Reload", film_title="Demo Film", language="en")
            project = store.save_analysis_text(project.project_dir, SAMPLE_ANALYSIS)
            first_block = project.semantic_blocks[0]

            project = store.update_semantic_block(
                project.project_dir,
                first_block["record_id"],
                "Inherited fear as structure",
                "insight",
                "Clarify why this block anchors the map.",
                "strong",
            )
            project = store.update_semantic_review_status(project.project_dir, "ready_for_review")
            reloaded = store.load_project(project.project_dir)

            block = reloaded.semantic_blocks[0]
            self.assertEqual("Inherited fear as structure", block["title"])
            self.assertEqual("insight", block["semantic_role"])
            self.assertEqual("strong", block["output_suitability"])
            self.assertEqual("Clarify why this block anchors the map.", block["notes"])
            self.assertEqual("ready_for_review", reloaded.semantic_review_record["review_status"])

            status_payload = json.loads((reloaded.project_dir / "project.meta" / "status.json").read_text(encoding="utf-8"))
            self.assertTrue(status_payload["source_loaded"])
            self.assertTrue(status_payload["semantic_blocks_created"])
            self.assertEqual("ready_for_review", status_payload["current_approval_state"])


if __name__ == "__main__":
    unittest.main()
