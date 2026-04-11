from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from runtime.builders import build_carousel_script as builder_build_carousel_script
from runtime.builders import build_packaging_script_bundle as builder_build_packaging_script_bundle
from runtime.builders import build_long_video_script as builder_build_long_video_script
from runtime.builders import build_shorts_reels_script as builder_build_shorts_reels_script
from runtime.builders import packaging_bundle_source_segments as builder_packaging_bundle_source_segments
from runtime.project_slice import ProjectSliceStore
from runtime.services.output_builder import build_carousel_script as service_build_carousel_script
from runtime.services.output_builder import build_packaging_script_bundle as service_build_packaging_script_bundle
from runtime.services.output_builder import build_long_video_script as service_build_long_video_script
from runtime.services.output_builder import build_shorts_reels_script as service_build_shorts_reels_script
from runtime.services.output_builder import packaging_bundle_source_segments as service_packaging_bundle_source_segments


SAMPLE_ANALYSIS = """
The opening movement argues that the film is really about inherited fear rather than simple survival. The critic frames the family house as a system that teaches each character how to obey the past.

Because the mother keeps translating danger into ritual, the essay reveals how ordinary domestic behavior becomes a mechanism of control. That repeated behavior gives the audience a way to feel the pressure before any explicit explanation arrives.

However, the final section suggests that the film does not stay inside despair. It shows a transition from passive inheritance toward a more conscious refusal to repeat the same emotional pattern.
""".strip()


class RuntimeBoundaryTests(unittest.TestCase):
    def _build_output_ready_project(self, store: ProjectSliceStore, title: str):
        project = store.create_project(title, film_title="Demo Film", language="en")
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
        project = store.update_matching_candidate_stub_rationale(
            project.project_dir,
            project.matching_candidate_stubs[0]["record_id"],
            "Lead with the inherited-fear framing as the opening packaging hook.",
        )
        project = store.promote_matching_candidate_stub_to_accepted_reference(
            project.project_dir,
            project.matching_candidate_stubs[0]["record_id"],
        )
        project = store.save_accepted_scene_reference_stub(project.project_dir, "Opening courtroom exchange")
        project = store.save_timecode_range_stub(project.project_dir, "00:00:10", "00:00:18")
        project = store.save_rough_cut_segment_stub(project.project_dir, "Opening hook")
        project = store.save_rough_cut_segment_stub(project.project_dir, "Mechanism beat")
        return store.build_packaging_script_bundle(project.project_dir)

    def test_builder_boundary_reexports_single_packaging_builder(self) -> None:
        self.assertIs(builder_build_carousel_script, service_build_carousel_script)
        self.assertIs(builder_build_packaging_script_bundle, service_build_packaging_script_bundle)
        self.assertIs(builder_build_long_video_script, service_build_long_video_script)
        self.assertIs(builder_build_shorts_reels_script, service_build_shorts_reels_script)
        self.assertIs(builder_packaging_bundle_source_segments, service_packaging_bundle_source_segments)

    def test_reopen_after_semantic_change_clears_downstream_chain(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))
            project = self._build_output_ready_project(store, "Boundary Reopen Cleanup")

            updated = store.update_semantic_block(
                project.project_dir,
                project.semantic_blocks[0]["record_id"],
                project.semantic_blocks[0]["title"],
                project.semantic_blocks[0]["semantic_role"],
                "Semantic change after approval should invalidate downstream state.",
            )

            self.assertTrue(updated.semantic_review_record["reopened_after_change"])
            self.assertIsNone(updated.accepted_reference)
            self.assertIsNone(updated.accepted_scene_reference_stub)
            self.assertIsNone(updated.timecode_range_stub)
            self.assertEqual(updated.rough_cut_segment_stubs, [])
            self.assertIsNone(updated.packaging_script_bundle)
            self.assertIsNone(updated.shorts_reels_script)
            self.assertIsNone(updated.long_video_script)
            self.assertIsNone(updated.carousel_script)
            self.assertFalse((updated.project_dir / "records" / "output" / "packaging_script_bundle.json").exists())
            self.assertFalse((updated.project_dir / "outputs" / "packaging" / "packaging_script_bundle.md").exists())
            self.assertFalse((updated.project_dir / "records" / "output" / "shorts_reels_script.json").exists())
            self.assertFalse((updated.project_dir / "outputs" / "shorts_reels" / "shorts_reels_script.md").exists())
            self.assertFalse((updated.project_dir / "records" / "output" / "long_video_script.json").exists())
            self.assertFalse((updated.project_dir / "outputs" / "long_video" / "long_video_script.md").exists())
            self.assertFalse((updated.project_dir / "records" / "output" / "carousel_script.json").exists())
            self.assertFalse((updated.project_dir / "outputs" / "carousel" / "carousel_script.md").exists())

    def test_demoting_selected_candidate_clears_stale_output_after_reload(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))
            project = self._build_output_ready_project(store, "Boundary Candidate Cleanup")

            updated = store.update_matching_candidate_stub_status(
                project.project_dir,
                project.matching_candidate_stubs[0]["record_id"],
                "rejected",
            )

            self.assertIsNone(updated.accepted_reference)
            self.assertIsNone(updated.accepted_scene_reference_stub)
            self.assertIsNone(updated.timecode_range_stub)
            self.assertEqual(updated.rough_cut_segment_stubs, [])
            self.assertIsNone(updated.packaging_script_bundle)
            self.assertIsNone(updated.shorts_reels_script)
            self.assertIsNone(updated.long_video_script)

            reloaded = store.load_project(updated.project_dir)
            self.assertIsNone(reloaded.accepted_reference)
            self.assertEqual(reloaded.rough_cut_segment_stubs, [])
            self.assertIsNone(reloaded.packaging_script_bundle)
            self.assertIsNone(reloaded.shorts_reels_script)
            self.assertIsNone(reloaded.long_video_script)
            self.assertIsNone(reloaded.carousel_script)

    def test_builder_rebuild_is_reproducible_after_reload(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))
            built = self._build_output_ready_project(store, "Boundary Rebuild")
            first_bundle = built.packaging_script_bundle

            reloaded = store.load_project(built.project_dir)
            rebuilt = store.build_packaging_script_bundle(reloaded.project_dir)
            second_bundle = rebuilt.packaging_script_bundle

            self.assertIsNotNone(first_bundle)
            self.assertIsNotNone(second_bundle)
            self.assertEqual(first_bundle["builder_id"], second_bundle["builder_id"])
            self.assertEqual(first_bundle["source_focus_mode"], second_bundle["source_focus_mode"])
            self.assertEqual(first_bundle["source_rough_cut_segment_ids"], second_bundle["source_rough_cut_segment_ids"])
            self.assertEqual(first_bundle["segment_count"], second_bundle["segment_count"])
            self.assertEqual(first_bundle["segments"], second_bundle["segments"])

    def test_shorts_builder_rebuild_is_reproducible_after_reload(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))
            built = self._build_output_ready_project(store, "Boundary Shorts Rebuild")
            built = store.build_shorts_reels_script(built.project_dir)
            first_script = built.shorts_reels_script

            reloaded = store.load_project(built.project_dir)
            rebuilt = store.build_shorts_reels_script(reloaded.project_dir)
            second_script = rebuilt.shorts_reels_script

            self.assertIsNotNone(first_script)
            self.assertIsNotNone(second_script)
            self.assertEqual(first_script["builder_id"], second_script["builder_id"])
            self.assertEqual(first_script["source_focus_mode"], second_script["source_focus_mode"])
            self.assertEqual(first_script["source_rough_cut_segment_ids"], second_script["source_rough_cut_segment_ids"])
            self.assertEqual(first_script["segment_count"], second_script["segment_count"])
            self.assertEqual(first_script["segments"], second_script["segments"])

    def test_long_video_builder_rebuild_is_reproducible_after_reload(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))
            built = self._build_output_ready_project(store, "Boundary Long Video Rebuild")
            built = store.build_long_video_script(built.project_dir)
            first_script = built.long_video_script

            reloaded = store.load_project(built.project_dir)
            rebuilt = store.build_long_video_script(reloaded.project_dir)
            second_script = rebuilt.long_video_script

            self.assertIsNotNone(first_script)
            self.assertIsNotNone(second_script)
            self.assertEqual(first_script["builder_id"], second_script["builder_id"])
            self.assertEqual(first_script["source_focus_mode"], second_script["source_focus_mode"])
            self.assertEqual(first_script["source_rough_cut_segment_ids"], second_script["source_rough_cut_segment_ids"])
            self.assertEqual(first_script["segment_count"], second_script["segment_count"])
            self.assertEqual(first_script["segments"], second_script["segments"])

    def test_carousel_builder_rebuild_is_reproducible_after_reload(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))
            built = self._build_output_ready_project(store, "Boundary Carousel Rebuild")
            built = store.build_carousel_script(built.project_dir)
            first_script = built.carousel_script

            reloaded = store.load_project(built.project_dir)
            rebuilt = store.build_carousel_script(reloaded.project_dir)
            second_script = rebuilt.carousel_script

            self.assertIsNotNone(first_script)
            self.assertIsNotNone(second_script)
            self.assertEqual(first_script["builder_id"], second_script["builder_id"])
            self.assertEqual(first_script["source_focus_mode"], second_script["source_focus_mode"])
            self.assertEqual(first_script["source_rough_cut_segment_ids"], second_script["source_rough_cut_segment_ids"])
            self.assertEqual(first_script["segment_count"], second_script["segment_count"])
            self.assertEqual(first_script["segments"], second_script["segments"])

    def test_all_four_builders_can_coexist_without_regression(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))
            built = self._build_output_ready_project(store, "Boundary Coexistence")
            built = store.build_shorts_reels_script(built.project_dir)
            built = store.build_long_video_script(built.project_dir)
            built = store.build_carousel_script(built.project_dir)

            self.assertIsNotNone(built.packaging_script_bundle)
            self.assertIsNotNone(built.shorts_reels_script)
            self.assertIsNotNone(built.long_video_script)
            self.assertIsNotNone(built.carousel_script)
            self.assertTrue((built.project_dir / "records" / "output" / "packaging_script_bundle.json").exists())
            self.assertTrue((built.project_dir / "records" / "output" / "shorts_reels_script.json").exists())
            self.assertTrue((built.project_dir / "records" / "output" / "long_video_script.json").exists())
            self.assertTrue((built.project_dir / "records" / "output" / "carousel_script.json").exists())


if __name__ == "__main__":
    unittest.main()
