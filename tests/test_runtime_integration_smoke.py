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


class RuntimeIntegrationSmokeTests(unittest.TestCase):
    def test_analysis_to_rough_cut_flow_still_works(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))

            project = store.create_project("Smoke Flow", film_title="Demo Film", language="en")
            project = store.save_analysis_text(project.project_dir, SAMPLE_ANALYSIS)

            for block in list(project.semantic_blocks):
                project = store.update_semantic_block(
                    project.project_dir,
                    block["record_id"],
                    block["title"],
                    block["semantic_role"],
                    "Editor clarification added.",
                )

            project = store.update_semantic_review_status(project.project_dir, "ready_for_review")
            project = store.update_semantic_review_status(project.project_dir, "approved")
            project = store.add_matching_prep_asset(
                project.project_dir,
                "Main subtitle file",
                "subtitle_reference",
                "E:/demo/subtitles.srt",
                "Primary subtitle reference.",
            )
            project = store.add_matching_candidate_stub(
                project.project_dir,
                project.semantic_blocks[0]["record_id"],
                project.matching_prep_assets[0]["record_id"],
                "Accepted prep reference feeds downstream stub.",
            )
            project = store.update_matching_candidate_stub_status(
                project.project_dir,
                project.matching_candidate_stubs[0]["record_id"],
                "selected",
            )
            project = store.promote_matching_candidate_stub_to_accepted_reference(
                project.project_dir,
                project.matching_candidate_stubs[0]["record_id"],
            )
            project = store.save_accepted_scene_reference_stub(project.project_dir, "Opening courtroom exchange")
            project = store.save_timecode_range_stub(project.project_dir, "00:00:10", "00:00:18")
            project = store.save_rough_cut_segment_stub(project.project_dir, "Opening argument beat")

            self.assertIsNotNone(project.accepted_reference)
            self.assertIsNotNone(project.accepted_scene_reference_stub)
            self.assertIsNotNone(project.timecode_range_stub)
            self.assertEqual(len(project.rough_cut_segment_stubs), 1)
            self.assertEqual(project.rough_cut_segment_stubs[0]["segment_label"], "Opening argument beat")


if __name__ == "__main__":
    unittest.main()
