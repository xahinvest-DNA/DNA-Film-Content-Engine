from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from runtime.project_slice import ProjectSliceStore


SAMPLE_ANALYSIS = """
Opening claim
The analysis starts by arguing that the film's real subject is inherited fear instead of simple danger.

Because each family ritual turns anxiety into routine, the essay explains how repetition becomes the mechanism that keeps the characters trapped.

The ending paragraph describes a transition toward refusal, which gives the semantic map a final pivot instead of a flat conclusion.
""".strip()


class RuntimeIntegrationSmokeTests(unittest.TestCase):
    def test_create_intake_edit_save_and_reopen_flow_works(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))

            project = store.create_project("Smoke Flow", film_title="Demo Film", language="en")
            project = store.save_analysis_text(project.project_dir, SAMPLE_ANALYSIS)
            first_block_id = project.semantic_blocks[0]["record_id"]

            project = store.update_semantic_block(
                project.project_dir,
                first_block_id,
                "Opening thematic claim",
                "claim",
                "Use this as the opening anchor in the workspace.",
                "candidate",
            )
            project = store.update_semantic_review_status(project.project_dir, "approved")

            reopened = store.load_project(project.project_dir)

            self.assertEqual("approved", reopened.semantic_review_record["review_status"])
            self.assertEqual(3, len(reopened.semantic_blocks))
            self.assertEqual("Opening thematic claim", reopened.semantic_blocks[0]["title"])
            self.assertEqual("Use this as the opening anchor in the workspace.", reopened.semantic_blocks[0]["notes"])
            self.assertEqual("semantic_map_approved", reopened.project_record["project_status"])


if __name__ == "__main__":
    unittest.main()
