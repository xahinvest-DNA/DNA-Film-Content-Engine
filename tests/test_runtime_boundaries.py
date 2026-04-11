from __future__ import annotations

import json
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

    def _recover_downstream_chain(
        self,
        store: ProjectSliceStore,
        project,
        *,
        scene_label: str,
        segment_labels: list[str],
        timecode_start: str = "00:00:10",
        timecode_end: str = "00:00:18",
    ):
        project = store.update_semantic_review_status(project.project_dir, "ready_for_review")
        project = store.update_semantic_review_status(project.project_dir, "approved")
        project = store.update_matching_candidate_stub_status(
            project.project_dir,
            project.matching_candidate_stubs[0]["record_id"],
            "selected",
        )
        project = store.promote_matching_candidate_stub_to_accepted_reference(
            project.project_dir,
            project.matching_candidate_stubs[0]["record_id"],
        )
        project = store.save_accepted_scene_reference_stub(project.project_dir, scene_label)
        project = store.save_timecode_range_stub(project.project_dir, timecode_start, timecode_end)
        for label in segment_labels:
            project = store.save_rough_cut_segment_stub(project.project_dir, label)
        return project

    def _build_output_subset(self, store: ProjectSliceStore, project, builder_keys: list[str]):
        builders = {
            "packaging": store.build_packaging_script_bundle,
            "shorts_reels": store.build_shorts_reels_script,
            "long_video": store.build_long_video_script,
            "carousel": store.build_carousel_script,
        }
        for key in builder_keys:
            project = builders[key](project.project_dir)
        return project

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

    def test_status_payload_tracks_partial_and_complete_output_inventory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))
            built = self._build_output_ready_project(store, "Boundary Status Payload")

            status_path = built.project_dir / "project.meta" / "status.json"
            status = json.loads(status_path.read_text(encoding="utf-8"))
            self.assertEqual(1, status["output_artifacts_built_count"])
            self.assertEqual(4, status["output_artifacts_total_slots"])
            self.assertEqual("partially_built", status["output_runtime_state"])
            self.assertEqual(["packaging"], status["built_output_families"])

            built = store.build_carousel_script(built.project_dir)
            built = store.build_long_video_script(built.project_dir)
            built = store.build_shorts_reels_script(built.project_dir)
            status = json.loads(status_path.read_text(encoding="utf-8"))
            self.assertEqual(4, status["output_artifacts_built_count"])
            self.assertEqual("all_built", status["output_runtime_state"])
            self.assertEqual([], status["missing_output_families"])

    def test_rebuild_order_variance_keeps_coherent_output_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))
            project = self._build_output_ready_project(store, "Boundary Build Order")
            project = store.build_carousel_script(project.project_dir)
            project = store.build_long_video_script(project.project_dir)
            project = store.build_shorts_reels_script(project.project_dir)
            reloaded = store.load_project(project.project_dir)
            rebuilt = store.build_packaging_script_bundle(reloaded.project_dir)

            self.assertIsNotNone(rebuilt.packaging_script_bundle)
            self.assertIsNotNone(rebuilt.shorts_reels_script)
            self.assertIsNotNone(rebuilt.long_video_script)
            self.assertIsNotNone(rebuilt.carousel_script)
            self.assertEqual("all_output_tracks_ready", rebuilt.project_record["project_status"])
            self.assertIn("All 4 output artifacts are currently built", rebuilt.project_record["current_readiness_summary"])

    def test_load_project_self_heals_tampered_status_payload(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))
            built = self._build_output_ready_project(store, "Boundary Status Self Heal")

            status_path = built.project_dir / "project.meta" / "status.json"
            tampered = json.loads(status_path.read_text(encoding="utf-8"))
            tampered["output_artifacts_built_count"] = 4
            tampered["output_runtime_state"] = "all_built"
            tampered["built_output_families"] = ["packaging", "shorts_reels", "long_video", "carousel"]
            tampered["missing_output_families"] = []
            status_path.write_text(json.dumps(tampered, indent=2) + "\n", encoding="utf-8")

            reloaded = store.load_project(built.project_dir)
            healed = json.loads(status_path.read_text(encoding="utf-8"))

            self.assertIsNotNone(reloaded.packaging_script_bundle)
            self.assertIsNone(reloaded.shorts_reels_script)
            self.assertEqual(1, healed["output_artifacts_built_count"])
            self.assertEqual("partially_built", healed["output_runtime_state"])
            self.assertEqual(["packaging"], healed["built_output_families"])
            self.assertEqual(["shorts_reels", "long_video", "carousel"], healed["missing_output_families"])

    def test_load_project_removes_resurrected_stale_output_files_after_reopen(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))
            project = self._build_output_ready_project(store, "Boundary Stale File Heal")
            project = store.build_shorts_reels_script(project.project_dir)
            project = store.build_long_video_script(project.project_dir)
            project = store.build_carousel_script(project.project_dir)

            stale_packaging = project.packaging_script_bundle
            stale_shorts = project.shorts_reels_script
            stale_long = project.long_video_script
            stale_carousel = project.carousel_script

            reopened = store.update_semantic_block(
                project.project_dir,
                project.semantic_blocks[0]["record_id"],
                project.semantic_blocks[0]["title"],
                project.semantic_blocks[0]["semantic_role"],
                "Reopen should invalidate all stale output files on disk.",
            )
            self.assertTrue(reopened.semantic_review_record["reopened_after_change"])

            resurrected_payloads = [
                ("records/output/packaging_script_bundle.json", stale_packaging),
                ("records/output/shorts_reels_script.json", stale_shorts),
                ("records/output/long_video_script.json", stale_long),
                ("records/output/carousel_script.json", stale_carousel),
            ]
            resurrected_markdowns = [
                ("outputs/packaging/packaging_script_bundle.md", stale_packaging["markdown_content"]),
                ("outputs/shorts_reels/shorts_reels_script.md", stale_shorts["markdown_content"]),
                ("outputs/long_video/long_video_script.md", stale_long["markdown_content"]),
                ("outputs/carousel/carousel_script.md", stale_carousel["markdown_content"]),
            ]
            for relative_path, payload in resurrected_payloads:
                target = reopened.project_dir / relative_path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            for relative_path, content in resurrected_markdowns:
                target = reopened.project_dir / relative_path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8")

            status_path = reopened.project_dir / "project.meta" / "status.json"
            tampered = json.loads(status_path.read_text(encoding="utf-8"))
            tampered["output_artifacts_built_count"] = 4
            tampered["output_runtime_state"] = "all_built"
            tampered["built_output_families"] = ["packaging", "shorts_reels", "long_video", "carousel"]
            tampered["missing_output_families"] = []
            status_path.write_text(json.dumps(tampered, indent=2) + "\n", encoding="utf-8")

            healed = store.load_project(reopened.project_dir)
            healed_status = json.loads(status_path.read_text(encoding="utf-8"))

            self.assertIsNone(healed.packaging_script_bundle)
            self.assertIsNone(healed.shorts_reels_script)
            self.assertIsNone(healed.long_video_script)
            self.assertIsNone(healed.carousel_script)
            self.assertFalse((healed.project_dir / "records" / "output" / "packaging_script_bundle.json").exists())
            self.assertFalse((healed.project_dir / "records" / "output" / "shorts_reels_script.json").exists())
            self.assertFalse((healed.project_dir / "records" / "output" / "long_video_script.json").exists())
            self.assertFalse((healed.project_dir / "records" / "output" / "carousel_script.json").exists())
            self.assertEqual(0, healed_status["output_artifacts_built_count"])
            self.assertEqual("none_built", healed_status["output_runtime_state"])

    def test_partial_rebuild_after_reopen_restores_coherent_truth(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))
            project = self._build_output_ready_project(store, "Boundary Partial Rebuild")
            project = store.build_shorts_reels_script(project.project_dir)
            project = store.build_long_video_script(project.project_dir)
            project = store.build_carousel_script(project.project_dir)

            project = store.update_semantic_block(
                project.project_dir,
                project.semantic_blocks[0]["record_id"],
                project.semantic_blocks[0]["title"],
                project.semantic_blocks[0]["semantic_role"],
                "Reset upstream truth before partial downstream reconstruction.",
            )
            project = store.update_semantic_review_status(project.project_dir, "ready_for_review")
            project = store.update_semantic_review_status(project.project_dir, "approved")
            project = store.update_matching_candidate_stub_status(
                project.project_dir,
                project.matching_candidate_stubs[0]["record_id"],
                "selected",
            )
            project = store.promote_matching_candidate_stub_to_accepted_reference(
                project.project_dir,
                project.matching_candidate_stubs[0]["record_id"],
            )
            project = store.save_accepted_scene_reference_stub(project.project_dir, "Opening courtroom exchange rebuilt")
            project = store.save_timecode_range_stub(project.project_dir, "00:00:10", "00:00:18")
            project = store.save_rough_cut_segment_stub(project.project_dir, "Recovered opening hook")
            project = store.build_packaging_script_bundle(project.project_dir)
            project = store.build_shorts_reels_script(project.project_dir)
            reloaded = store.load_project(project.project_dir)
            status = json.loads((project.project_dir / "project.meta" / "status.json").read_text(encoding="utf-8"))

            self.assertIsNotNone(reloaded.packaging_script_bundle)
            self.assertIsNotNone(reloaded.shorts_reels_script)
            self.assertIsNone(reloaded.long_video_script)
            self.assertIsNone(reloaded.carousel_script)
            self.assertEqual(2, status["output_artifacts_built_count"])
            self.assertEqual("partially_built", status["output_runtime_state"])
            self.assertEqual(["packaging", "shorts_reels"], status["built_output_families"])

    def test_multiple_recovery_cycles_keep_output_truth_coherent(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))
            project = self._build_output_ready_project(store, "Boundary Multi Cycle")
            project = self._build_output_subset(store, project, ["shorts_reels", "long_video", "carousel"])

            project = store.update_semantic_block(
                project.project_dir,
                project.semantic_blocks[0]["record_id"],
                project.semantic_blocks[0]["title"],
                project.semantic_blocks[0]["semantic_role"],
                "First reopen cycle should clear all downstream output truth.",
            )
            project = self._recover_downstream_chain(
                store,
                project,
                scene_label="Cycle one scene",
                segment_labels=["Cycle one hook", "Cycle one mechanism"],
            )
            project = self._build_output_subset(store, project, ["packaging", "carousel"])

            project = store.update_semantic_block(
                project.project_dir,
                project.semantic_blocks[1]["record_id"],
                project.semantic_blocks[1]["title"],
                project.semantic_blocks[1]["semantic_role"],
                "Second reopen cycle should also clear partial rebuilt output truth.",
            )
            project = self._recover_downstream_chain(
                store,
                project,
                scene_label="Cycle two scene",
                segment_labels=["Cycle two short hook"],
            )
            project = self._build_output_subset(store, project, ["shorts_reels", "long_video"])
            reloaded = store.load_project(project.project_dir)
            status = json.loads((project.project_dir / "project.meta" / "status.json").read_text(encoding="utf-8"))

            self.assertIsNone(reloaded.packaging_script_bundle)
            self.assertIsNotNone(reloaded.shorts_reels_script)
            self.assertIsNotNone(reloaded.long_video_script)
            self.assertIsNone(reloaded.carousel_script)
            self.assertEqual(2, status["output_artifacts_built_count"])
            self.assertEqual("partially_built", status["output_runtime_state"])
            self.assertEqual(["shorts_reels", "long_video"], status["built_output_families"])
            self.assertEqual(["packaging", "carousel"], status["missing_output_families"])
            self.assertFalse((project.project_dir / "records" / "output" / "packaging_script_bundle.json").exists())
            self.assertFalse((project.project_dir / "records" / "output" / "carousel_script.json").exists())

    def test_load_project_self_heals_mixed_partial_output_drift_after_second_cycle(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))
            project = self._build_output_ready_project(store, "Boundary Mixed Drift")
            project = self._build_output_subset(store, project, ["shorts_reels", "long_video", "carousel"])

            stale_packaging = project.packaging_script_bundle
            stale_shorts = project.shorts_reels_script
            stale_long = project.long_video_script
            stale_carousel = project.carousel_script

            project = store.update_semantic_block(
                project.project_dir,
                project.semantic_blocks[0]["record_id"],
                project.semantic_blocks[0]["title"],
                project.semantic_blocks[0]["semantic_role"],
                "Cycle reset before mixed partial drift self-heal.",
            )
            project = self._recover_downstream_chain(
                store,
                project,
                scene_label="Mixed drift scene",
                segment_labels=["Mixed drift hook"],
            )
            project = store.build_packaging_script_bundle(project.project_dir)

            resurrected_payloads = [
                ("records/output/shorts_reels_script.json", stale_shorts),
                ("records/output/long_video_script.json", stale_long),
                ("records/output/carousel_script.json", stale_carousel),
            ]
            resurrected_markdowns = [
                ("outputs/shorts_reels/shorts_reels_script.md", stale_shorts["markdown_content"]),
                ("outputs/long_video/long_video_script.md", stale_long["markdown_content"]),
                ("outputs/carousel/carousel_script.md", stale_carousel["markdown_content"]),
            ]
            for relative_path, payload in resurrected_payloads:
                target = project.project_dir / relative_path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            for relative_path, content in resurrected_markdowns:
                target = project.project_dir / relative_path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8")

            status_path = project.project_dir / "project.meta" / "status.json"
            tampered = json.loads(status_path.read_text(encoding="utf-8"))
            tampered["output_artifacts_built_count"] = 4
            tampered["output_runtime_state"] = "all_built"
            tampered["built_output_families"] = ["packaging", "shorts_reels", "long_video", "carousel"]
            tampered["missing_output_families"] = []
            status_path.write_text(json.dumps(tampered, indent=2) + "\n", encoding="utf-8")

            healed = store.load_project(project.project_dir)
            healed_status = json.loads(status_path.read_text(encoding="utf-8"))

            self.assertIsNotNone(healed.packaging_script_bundle)
            self.assertIsNone(healed.shorts_reels_script)
            self.assertIsNone(healed.long_video_script)
            self.assertIsNone(healed.carousel_script)
            self.assertTrue((project.project_dir / "records" / "output" / "packaging_script_bundle.json").exists())
            self.assertFalse((project.project_dir / "records" / "output" / "shorts_reels_script.json").exists())
            self.assertFalse((project.project_dir / "records" / "output" / "long_video_script.json").exists())
            self.assertFalse((project.project_dir / "records" / "output" / "carousel_script.json").exists())
            self.assertTrue((project.project_dir / "outputs" / "packaging" / "packaging_script_bundle.md").exists())
            self.assertFalse((project.project_dir / "outputs" / "shorts_reels" / "shorts_reels_script.md").exists())
            self.assertFalse((project.project_dir / "outputs" / "long_video" / "long_video_script.md").exists())
            self.assertFalse((project.project_dir / "outputs" / "carousel" / "carousel_script.md").exists())
            self.assertEqual(1, healed_status["output_artifacts_built_count"])
            self.assertEqual("partially_built", healed_status["output_runtime_state"])
            self.assertEqual(["packaging"], healed_status["built_output_families"])
            self.assertEqual(["shorts_reels", "long_video", "carousel"], healed_status["missing_output_families"])


if __name__ == "__main__":
    unittest.main()
