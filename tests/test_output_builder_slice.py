from __future__ import annotations

import tempfile
import tkinter as tk
import unittest
from pathlib import Path
from unittest.mock import patch

from runtime.app import DNAFilmApp
from runtime.project_slice import ProjectSliceStore


SAMPLE_ANALYSIS = """
The opening movement argues that the film is really about inherited fear rather than simple survival. The critic frames the family house as a system that teaches each character how to obey the past.

Because the mother keeps translating danger into ritual, the essay reveals how ordinary domestic behavior becomes a mechanism of control. That repeated behavior gives the audience a way to feel the pressure before any explicit explanation arrives.

However, the final section suggests that the film does not stay inside despair. It shows a transition from passive inheritance toward a more conscious refusal to repeat the same emotional pattern.
""".strip()


class OutputBuilderTests(unittest.TestCase):
    def _build_rough_cut_ready_project(self, store: ProjectSliceStore, title: str):
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
        return project

    def test_packaging_script_bundle_persists_after_reload(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))
            project = self._build_rough_cut_ready_project(store, "Packaging Persistence")

            built = store.build_packaging_script_bundle(project.project_dir)

            self.assertIsNotNone(built.packaging_script_bundle)
            self.assertEqual(built.packaging_script_bundle["record_type"], "packaging_script_bundle")
            self.assertTrue((built.project_dir / "records" / "output" / "packaging_script_bundle.json").exists())
            self.assertTrue((built.project_dir / "outputs" / "packaging" / "packaging_script_bundle.md").exists())

            reloaded = store.load_project(built.project_dir)
            self.assertIsNotNone(reloaded.packaging_script_bundle)
            self.assertEqual(reloaded.packaging_script_bundle["segment_count"], 2)
            self.assertIn("Packaging Script Bundle", reloaded.packaging_script_bundle["title"])

    def test_packaging_script_bundle_uses_preferred_subset_when_present(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))
            project = self._build_rough_cut_ready_project(store, "Packaging Preferred Subset")
            project = store.update_rough_cut_segment_subset_status(
                project.project_dir,
                project.rough_cut_segment_stubs[0]["record_id"],
                "selected_for_current_rough_cut",
            )

            built = store.build_packaging_script_bundle(project.project_dir)
            bundle = built.packaging_script_bundle

            self.assertIsNotNone(bundle)
            self.assertEqual(bundle["source_focus_mode"], "preferred_subset_only")
            self.assertEqual(bundle["source_rough_cut_segment_ids"], [project.rough_cut_segment_stubs[0]["record_id"]])
            self.assertIn("Opening hook", bundle["markdown_content"])
            self.assertNotIn("Mechanism beat", bundle["markdown_content"])

    def test_shorts_reels_script_persists_after_reload(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))
            project = self._build_rough_cut_ready_project(store, "Shorts Persistence")

            built = store.build_shorts_reels_script(project.project_dir)

            self.assertIsNotNone(built.shorts_reels_script)
            self.assertEqual(built.shorts_reels_script["record_type"], "shorts_reels_script")
            self.assertTrue((built.project_dir / "records" / "output" / "shorts_reels_script.json").exists())
            self.assertTrue((built.project_dir / "outputs" / "shorts_reels" / "shorts_reels_script.md").exists())

            reloaded = store.load_project(built.project_dir)
            self.assertIsNotNone(reloaded.shorts_reels_script)
            self.assertEqual(reloaded.shorts_reels_script["segment_count"], 2)
            self.assertIn("Shorts Reels Script", reloaded.shorts_reels_script["title"])

    def test_shorts_reels_script_uses_preferred_subset_when_present(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))
            project = self._build_rough_cut_ready_project(store, "Shorts Preferred Subset")
            project = store.update_rough_cut_segment_subset_status(
                project.project_dir,
                project.rough_cut_segment_stubs[0]["record_id"],
                "selected_for_current_rough_cut",
            )

            built = store.build_shorts_reels_script(project.project_dir)
            script = built.shorts_reels_script

            self.assertIsNotNone(script)
            self.assertEqual(script["source_focus_mode"], "preferred_subset_only")
            self.assertEqual(script["source_rough_cut_segment_ids"], [project.rough_cut_segment_stubs[0]["record_id"]])
            self.assertIn("## Hook / Opening angle", script["markdown_content"])
            self.assertIn("Lead with the inherited-fear framing as the opening packaging hook.", script["markdown_content"])
            self.assertNotIn("Mechanism beat", script["markdown_content"])

    def test_long_video_script_persists_after_reload(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))
            project = self._build_rough_cut_ready_project(store, "Long Video Persistence")

            built = store.build_long_video_script(project.project_dir)

            self.assertIsNotNone(built.long_video_script)
            self.assertEqual(built.long_video_script["record_type"], "long_video_script")
            self.assertTrue((built.project_dir / "records" / "output" / "long_video_script.json").exists())
            self.assertTrue((built.project_dir / "outputs" / "long_video" / "long_video_script.md").exists())

            reloaded = store.load_project(built.project_dir)
            self.assertIsNotNone(reloaded.long_video_script)
            self.assertEqual(reloaded.long_video_script["segment_count"], 2)
            self.assertIn("Long Video Script", reloaded.long_video_script["title"])

    def test_long_video_script_uses_preferred_subset_when_present(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))
            project = self._build_rough_cut_ready_project(store, "Long Video Preferred Subset")
            project = store.update_rough_cut_segment_subset_status(
                project.project_dir,
                project.rough_cut_segment_stubs[0]["record_id"],
                "selected_for_current_rough_cut",
            )

            built = store.build_long_video_script(project.project_dir)
            script = built.long_video_script

            self.assertIsNotNone(script)
            self.assertEqual(script["source_focus_mode"], "preferred_subset_only")
            self.assertEqual(script["source_rough_cut_segment_ids"], [project.rough_cut_segment_stubs[0]["record_id"]])
            self.assertIn("## Opening setup", script["markdown_content"])
            self.assertIn("## Continuity / transitions", script["markdown_content"])
            self.assertNotIn("Mechanism beat", script["markdown_content"])

    def test_long_video_script_has_distinct_long_form_structure(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))
            project = self._build_rough_cut_ready_project(store, "Long Video Identity")

            packaging = store.build_packaging_script_bundle(project.project_dir)
            shorts = store.build_shorts_reels_script(project.project_dir)
            long_video = store.build_long_video_script(project.project_dir)

            self.assertIn("## Editorial summary", packaging.packaging_script_bundle["markdown_content"])
            self.assertIn("## Hook / Opening angle", shorts.shorts_reels_script["markdown_content"])
            self.assertIn("## Opening setup", long_video.long_video_script["markdown_content"])
            self.assertIn("## Main progression", long_video.long_video_script["markdown_content"])
            self.assertIn("## Expanded voiceover spine", long_video.long_video_script["markdown_content"])
            self.assertIn("## Continuity / transitions", long_video.long_video_script["markdown_content"])
            self.assertNotEqual(long_video.long_video_script["markdown_content"], packaging.packaging_script_bundle["markdown_content"])
            self.assertNotEqual(long_video.long_video_script["markdown_content"], shorts.shorts_reels_script["markdown_content"])

    def test_carousel_script_persists_after_reload(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))
            project = self._build_rough_cut_ready_project(store, "Carousel Persistence")

            built = store.build_carousel_script(project.project_dir)

            self.assertIsNotNone(built.carousel_script)
            self.assertEqual(built.carousel_script["record_type"], "carousel_script")
            self.assertTrue((built.project_dir / "records" / "output" / "carousel_script.json").exists())
            self.assertTrue((built.project_dir / "outputs" / "carousel" / "carousel_script.md").exists())

            reloaded = store.load_project(built.project_dir)
            self.assertIsNotNone(reloaded.carousel_script)
            self.assertEqual(reloaded.carousel_script["segment_count"], 2)
            self.assertEqual(reloaded.carousel_script["slide_count"], 4)
            self.assertIn("Carousel Script", reloaded.carousel_script["title"])

    def test_carousel_script_uses_preferred_subset_when_present(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))
            project = self._build_rough_cut_ready_project(store, "Carousel Preferred Subset")
            project = store.update_rough_cut_segment_subset_status(
                project.project_dir,
                project.rough_cut_segment_stubs[0]["record_id"],
                "selected_for_current_rough_cut",
            )

            built = store.build_carousel_script(project.project_dir)
            script = built.carousel_script

            self.assertIsNotNone(script)
            self.assertEqual(script["source_focus_mode"], "preferred_subset_only")
            self.assertEqual(script["source_rough_cut_segment_ids"], [project.rough_cut_segment_stubs[0]["record_id"]])
            self.assertIn("## Cover slide / first-slide hook", script["markdown_content"])
            self.assertIn("### Slide 02", script["markdown_content"])
            self.assertNotIn("Mechanism beat", script["markdown_content"])

    def test_carousel_script_has_distinct_slide_structure(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))
            project = self._build_rough_cut_ready_project(store, "Carousel Identity")

            packaging = store.build_packaging_script_bundle(project.project_dir)
            shorts = store.build_shorts_reels_script(project.project_dir)
            long_video = store.build_long_video_script(project.project_dir)
            carousel = store.build_carousel_script(project.project_dir)

            self.assertIn("## Editorial summary", packaging.packaging_script_bundle["markdown_content"])
            self.assertIn("## Hook / Opening angle", shorts.shorts_reels_script["markdown_content"])
            self.assertIn("## Opening setup", long_video.long_video_script["markdown_content"])
            self.assertIn("## Cover slide / first-slide hook", carousel.carousel_script["markdown_content"])
            self.assertIn("## Slide-by-slide progression", carousel.carousel_script["markdown_content"])
            self.assertIn("## Reading continuity", carousel.carousel_script["markdown_content"])
            self.assertIn("## Final slide / CTA", carousel.carousel_script["markdown_content"])
            self.assertNotEqual(carousel.carousel_script["markdown_content"], packaging.packaging_script_bundle["markdown_content"])
            self.assertNotEqual(carousel.carousel_script["markdown_content"], shorts.shorts_reels_script["markdown_content"])
            self.assertNotEqual(carousel.carousel_script["markdown_content"], long_video.long_video_script["markdown_content"])

    def test_app_can_build_and_show_packaging_script_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))
            project = self._build_rough_cut_ready_project(store, "Packaging UI Flow")

            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = store
                app._load_project_into_ui(project)
                app._switch_view("Output Tracks")

                with patch("runtime.app.messagebox.showinfo"), patch("runtime.app.messagebox.showerror"):
                    app.build_packaging_script_bundle()

                self.assertIsNotNone(app.project.packaging_script_bundle)
                self.assertIn("Packaging-ready script bundle:", app.output_builder_summary_text.get())
                self.assertIn("Packaging path: outputs/packaging/packaging_script_bundle.md", app.output_builder_path_text.get())
                self.assertIn("Packaging Script Bundle", app.output_builder_handoff.get("1.0", "end"))
            finally:
                root.destroy()

    def test_app_can_build_and_show_shorts_reels_script(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))
            project = self._build_rough_cut_ready_project(store, "Shorts UI Flow")

            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = store
                app._load_project_into_ui(project)
                app._switch_view("Output Tracks")

                with patch("runtime.app.messagebox.showinfo"), patch("runtime.app.messagebox.showerror"):
                    app.build_shorts_reels_script()

                self.assertIsNotNone(app.project.shorts_reels_script)
                self.assertIn("Shorts/Reels script:", app.output_builder_summary_text.get())
                self.assertIn("Shorts/Reels path: outputs/shorts_reels/shorts_reels_script.md", app.output_builder_path_text.get())
                self.assertIn("Shorts Reels Script", app.output_builder_handoff.get("1.0", "end"))
            finally:
                root.destroy()

    def test_app_can_build_and_show_long_video_script(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))
            project = self._build_rough_cut_ready_project(store, "Long Video UI Flow")

            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = store
                app._load_project_into_ui(project)
                app._switch_view("Output Tracks")

                with patch("runtime.app.messagebox.showinfo"), patch("runtime.app.messagebox.showerror"):
                    app.build_long_video_script()

                self.assertIsNotNone(app.project.long_video_script)
                self.assertIn("Long-video script:", app.output_builder_summary_text.get())
                self.assertIn("Long-video path: outputs/long_video/long_video_script.md", app.output_builder_path_text.get())
                self.assertIn("Long Video Script", app.output_builder_handoff.get("1.0", "end"))
            finally:
                root.destroy()

    def test_app_can_build_and_show_carousel_script(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))
            project = self._build_rough_cut_ready_project(store, "Carousel UI Flow")

            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = store
                app._load_project_into_ui(project)
                app._switch_view("Output Tracks")

                with patch("runtime.app.messagebox.showinfo"), patch("runtime.app.messagebox.showerror"):
                    app.build_carousel_script()

                self.assertIsNotNone(app.project.carousel_script)
                self.assertIn("Carousel script:", app.output_builder_summary_text.get())
                self.assertIn("Carousel path: outputs/carousel/carousel_script.md", app.output_builder_path_text.get())
                self.assertIn("Carousel Script", app.output_builder_handoff.get("1.0", "end"))
            finally:
                root.destroy()


if __name__ == "__main__":
    unittest.main()
