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

SHORT_AND_MIXED_ANALYSIS = """
Tiny thought.

This second paragraph is long enough to keep the intake accepted while still leaving the first semantic block obviously too short for confident review.
""".strip()


class ProjectSliceStoreTests(unittest.TestCase):
    def test_create_project_and_build_semantic_map(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))
            project = store.create_project("Hereditary Essay", film_title="Hereditary", language="en")

            self.assertTrue((project.project_dir / "project.manifest").exists())
            self.assertTrue((project.project_dir / "records" / "review" / "semantic_review.json").exists())
            self.assertEqual(project.project_record["project_status"], "intake_required")
            self.assertEqual(project.intake_record["intake_readiness"], "blocked")
            self.assertEqual(project.semantic_review_record["review_status"], "under_edit")

            updated = store.save_analysis_text(project.project_dir, SAMPLE_ANALYSIS)

            self.assertEqual(updated.intake_record["intake_readiness"], "ready")
            self.assertEqual(updated.project_record["project_status"], "semantic_map_under_edit")
            self.assertEqual(updated.semantic_review_record["review_status"], "under_edit")
            self.assertEqual(len(updated.semantic_blocks), 3)
            self.assertTrue((updated.project_dir / "sources" / "analysis" / "analysis.txt").exists())
            self.assertTrue((updated.project_dir / "records" / "semantic" / "semantic_blocks.json").exists())

    def test_issue_flags_and_incomplete_completeness_persist_after_reload(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))
            project = store.create_project("Weak Map", film_title="Demo Film", language="en")
            project = store.save_analysis_text(project.project_dir, SHORT_AND_MIXED_ANALYSIS)

            first_block = project.semantic_blocks[0]
            self.assertIn("very_short_content", first_block["warning_flags"])
            self.assertIn("weak_title", first_block["warning_flags"])
            self.assertEqual(store._approval_readiness_label(project.intake_record, project.semantic_blocks, project.semantic_review_record), "premature")

            status_payload = (project.project_dir / "project.meta" / "status.json").read_text(encoding="utf-8")
            self.assertIn('"semantic_completeness": "Incomplete"', status_payload)
            self.assertIn('"blocks_with_issues": 2', status_payload)

            reloaded = store.load_project(project.project_dir)
            self.assertIn("very_short_content", reloaded.semantic_blocks[0]["warning_flags"])
            self.assertIn("weak_title", reloaded.semantic_blocks[0]["warning_flags"])

    def test_completeness_can_become_plausibly_ready_after_fixing_notes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))
            project = store.create_project("Readyish Map", film_title="Demo Film", language="en")
            project = store.save_analysis_text(project.project_dir, SAMPLE_ANALYSIS)

            for block in list(project.semantic_blocks):
                project = store.update_semantic_block(
                    project.project_dir,
                    block["record_id"],
                    block["title"],
                    block["semantic_role"],
                    "Editor clarification added.",
                )

            self.assertTrue(all(not block["warning_flags"] for block in project.semantic_blocks))
            self.assertEqual(store._approval_readiness_label(project.intake_record, project.semantic_blocks, project.semantic_review_record), "plausibly_reasonable")
            status_payload = (project.project_dir / "project.meta" / "status.json").read_text(encoding="utf-8")
            self.assertIn('"semantic_completeness": "Plausibly ready for review"', status_payload)
            self.assertIn('"semantic_issue_count": 0', status_payload)

    def test_output_suitability_edit_persists_after_reload(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))
            project = store.create_project("Suitability Map", film_title="Demo Film", language="en")
            project = store.save_analysis_text(project.project_dir, SAMPLE_ANALYSIS)
            first_block = project.semantic_blocks[0]

            project = store.update_semantic_block(
                project.project_dir,
                first_block["record_id"],
                first_block["title"],
                first_block["semantic_role"],
                first_block["notes"],
                output_suitability={
                    "long_video": "strong",
                    "shorts_reels": "weak",
                    "carousel": "candidate",
                    "packaging": "not_suitable",
                },
            )

            updated = project.semantic_blocks[0]["output_suitability"]
            self.assertEqual(updated["long_video"], "strong")
            self.assertEqual(updated["shorts_reels"], "weak")
            self.assertEqual(updated["packaging"], "not_suitable")

            reloaded = store.load_project(project.project_dir)
            self.assertEqual(reloaded.semantic_blocks[0]["output_suitability"]["long_video"], "strong")
            self.assertEqual(reloaded.semantic_blocks[0]["output_suitability"]["packaging"], "not_suitable")

    def test_suitability_edit_reopens_approved_map(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))
            project = store.create_project("Suitability Reopen", film_title="Demo Film", language="en")
            project = store.save_analysis_text(project.project_dir, SAMPLE_ANALYSIS)
            for block in list(project.semantic_blocks):
                project = store.update_semantic_block(
                    project.project_dir,
                    block["record_id"],
                    block["title"],
                    block["semantic_role"],
                    "Editor clarification added.",
                    output_suitability={
                        "long_video": "candidate",
                        "shorts_reels": "candidate",
                        "carousel": "candidate",
                        "packaging": "candidate",
                    },
                )
            project = store.update_semantic_review_status(project.project_dir, "ready_for_review")
            project = store.update_semantic_review_status(project.project_dir, "approved")
            first_block = project.semantic_blocks[0]

            reopened = store.update_semantic_block(
                project.project_dir,
                first_block["record_id"],
                first_block["title"],
                first_block["semantic_role"],
                first_block["notes"],
                output_suitability={
                    "long_video": "strong",
                    "shorts_reels": "candidate",
                    "carousel": "candidate",
                    "packaging": "candidate",
                },
            )

            self.assertTrue(reopened.semantic_review_record["reopened_after_change"])
            self.assertIn("output suitability changed after approval", reopened.semantic_review_record["reopen_reason"])

    def test_blocked_approval_persists_reason(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))
            project = store.create_project("Guardrail Map", film_title="Demo Film", language="en")
            project = store.save_analysis_text(project.project_dir, SAMPLE_ANALYSIS)
            blocked = store.update_semantic_review_status(project.project_dir, "approved")

            self.assertEqual(blocked.semantic_review_record["review_status"], "under_edit")
            self.assertFalse(blocked.semantic_review_record["approved"])
            self.assertIn("Approve is blocked", blocked.semantic_review_record["approval_block_reason"])
            self.assertIn("blocked", blocked.semantic_review_record["approval_transition_message"])

            reloaded = store.load_project(project.project_dir)
            self.assertIn("Approve is blocked", reloaded.semantic_review_record["approval_block_reason"])

    def test_split_block_persists_after_reload(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))
            project = store.create_project("Boundary Map", film_title="Demo Film", language="en")
            project = store.save_analysis_text(project.project_dir, SAMPLE_ANALYSIS)

            first_block_id = project.semantic_blocks[0]["record_id"]
            split_project = store.split_semantic_block(project.project_dir, first_block_id, 1)

            self.assertEqual(len(split_project.semantic_blocks), 4)
            self.assertEqual([block["sequence"] for block in split_project.semantic_blocks], [1, 2, 3, 4])
            self.assertEqual(split_project.semantic_blocks[0]["record_id"], first_block_id)
            self.assertEqual(
                split_project.semantic_blocks[0]["content"],
                "The opening movement argues that the film is really about inherited fear rather than simple survival.",
            )
            self.assertEqual(
                split_project.semantic_blocks[1]["content"],
                "The critic frames the family house as a system that teaches each character how to obey the past.",
            )
            self.assertEqual(split_project.semantic_blocks[0]["source_record_id"], split_project.semantic_blocks[1]["source_record_id"])

            reloaded = store.load_project(project.project_dir)
            self.assertEqual(len(reloaded.semantic_blocks), 4)
            self.assertEqual(reloaded.semantic_blocks[1]["sequence"], 2)
            self.assertEqual(reloaded.semantic_blocks[1]["record_id"], "sb-004")

    def test_merge_adjacent_block_persists_after_reload(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))
            project = store.create_project("Merge Map", film_title="Demo Film", language="en")
            project = store.save_analysis_text(project.project_dir, SAMPLE_ANALYSIS)

            second_block_id = project.semantic_blocks[1]["record_id"]
            merged = store.merge_semantic_block(project.project_dir, second_block_id, "down")

            self.assertEqual(len(merged.semantic_blocks), 2)
            self.assertEqual([block["sequence"] for block in merged.semantic_blocks], [1, 2])
            self.assertEqual(merged.semantic_blocks[1]["record_id"], second_block_id)
            self.assertIn("Because the mother keeps translating danger into ritual", merged.semantic_blocks[1]["content"])
            self.assertIn("However, the final section suggests", merged.semantic_blocks[1]["content"])

            reloaded = store.load_project(project.project_dir)
            self.assertEqual(len(reloaded.semantic_blocks), 2)
            self.assertEqual(reloaded.semantic_blocks[1]["record_id"], second_block_id)
            status_payload = (reloaded.project_dir / "project.meta" / "status.json").read_text(encoding="utf-8")
            self.assertIn('"semantic_block_count": 2', status_payload)

    def test_reopen_after_structural_change_persists_after_reload(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))
            project = store.create_project("Reopen Structure Map", film_title="Demo Film", language="en")
            project = store.save_analysis_text(project.project_dir, SAMPLE_ANALYSIS)
            project = store.update_semantic_review_status(project.project_dir, "ready_for_review")
            project = store.update_semantic_review_status(project.project_dir, "approved")
            first_block_id = project.semantic_blocks[0]["record_id"]

            reopened = store.split_semantic_block(project.project_dir, first_block_id, 1)

            self.assertEqual(reopened.project_record["project_status"], "semantic_map_reopened")
            self.assertTrue(reopened.semantic_review_record["reopened_after_change"])
            self.assertIn("reopened", reopened.semantic_review_record["approval_transition_message"].lower())
            self.assertIn("boundaries changed after approval", reopened.semantic_review_record["reopen_reason"])

            reloaded = store.load_project(project.project_dir)
            self.assertTrue(reloaded.semantic_review_record["reopened_after_change"])
            self.assertIn("boundaries changed after approval", reloaded.semantic_review_record["reopen_reason"])

    def test_reorder_and_readiness_persist_after_reload(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))
            project = store.create_project("Ordered Map", film_title="Demo Film", language="en")
            project = store.save_analysis_text(project.project_dir, SAMPLE_ANALYSIS)

            second_block_id = project.semantic_blocks[1]["record_id"]
            project = store.reorder_semantic_block(project.project_dir, second_block_id, "up")
            reloaded = store.load_project(project.project_dir)

            self.assertEqual(reloaded.semantic_blocks[0]["record_id"], second_block_id)
            status_payload = (reloaded.project_dir / "project.meta" / "status.json").read_text(encoding="utf-8")
            self.assertIn('"approval_readiness": "mixed"', status_payload)

            reloaded = store.update_semantic_review_status(reloaded.project_dir, "ready_for_review")
            self.assertEqual(reloaded.project_record["project_status"], "semantic_map_ready_for_review")
            status_payload = (reloaded.project_dir / "project.meta" / "status.json").read_text(encoding="utf-8")
            self.assertIn('"approval_readiness": "ready_for_approval"', status_payload)

    def test_analysis_text_must_be_meaningful(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))
            project = store.create_project("Short Input")

            with self.assertRaises(ValueError):
                store.save_analysis_text(project.project_dir, "Too short")


class DNAFilmAppTests(unittest.TestCase):
    def test_app_shows_blocked_approval_reason(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = ProjectSliceStore(app.workspace_root)

                with patch("runtime.app.messagebox.showinfo"), patch("runtime.app.messagebox.showerror"):
                    app.project_name_var.set("UI Guardrail Map")
                    app.film_title_var.set("Demo Film")
                    app.language_var.set("en")
                    app.create_project()
                    app.analysis_text.insert("1.0", SAMPLE_ANALYSIS)
                    app.save_analysis_text()
                    app.review_status_var.set("approved")
                    app.save_review_status()

                self.assertIn("Approve is blocked", app.approval_reason_text.get())
                self.assertEqual(app.readiness_text.get(), "Approval readiness: mixed")
            finally:
                root.destroy()

    def test_app_surfaces_issue_visibility_in_list_and_inspector(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = ProjectSliceStore(app.workspace_root)

                with patch("runtime.app.messagebox.showinfo"), patch("runtime.app.messagebox.showerror"):
                    app.project_name_var.set("UI Issues Map")
                    app.film_title_var.set("Demo Film")
                    app.language_var.set("en")
                    app.create_project()
                    app.analysis_text.insert("1.0", SHORT_AND_MIXED_ANALYSIS)
                    app.save_analysis_text()

                self.assertIn("issues:", app.semantic_list.get(0))
                self.assertIn("Semantic completeness: Incomplete", app.completeness_text.get())
                self.assertIn("Block issues:", app.block_issues_text.get())
                self.assertIn("very short content", app.block_issues_text.get())
            finally:
                root.destroy()

    def test_app_surfaces_suitability_controls_and_persistence(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = ProjectSliceStore(app.workspace_root)

                with patch("runtime.app.messagebox.showinfo"), patch("runtime.app.messagebox.showerror"):
                    app.project_name_var.set("UI Suitability Map")
                    app.film_title_var.set("Demo Film")
                    app.language_var.set("en")
                    app.create_project()
                    app.analysis_text.insert("1.0", SAMPLE_ANALYSIS)
                    app.save_analysis_text()
                    first_block_id = app.project.semantic_blocks[0]["record_id"]
                    app._select_block_by_id(first_block_id)
                    app.long_video_var.set("strong")
                    app.shorts_reels_var.set("weak")
                    app.packaging_var.set("not_suitable")
                    app.save_selected_block()

                self.assertIn("LV:strong", app.semantic_list.get(0))
                self.assertIn("suitability:", app.block_issues_text.get())
                reloaded = app.store.load_project(app.project.project_dir)
                self.assertEqual(reloaded.semantic_blocks[0]["output_suitability"]["long_video"], "strong")
                self.assertEqual(reloaded.semantic_blocks[0]["output_suitability"]["packaging"], "not_suitable")
            finally:
                root.destroy()

    def test_app_split_and_merge_controls_persist_structure(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = ProjectSliceStore(app.workspace_root)

                with patch("runtime.app.messagebox.showinfo"), patch("runtime.app.messagebox.showerror"):
                    app.project_name_var.set("UI Structure Map")
                    app.film_title_var.set("Demo Film")
                    app.language_var.set("en")
                    app.create_project()
                    app.analysis_text.insert("1.0", SAMPLE_ANALYSIS)
                    app.save_analysis_text()
                    first_block_id = app.project.semantic_blocks[0]["record_id"]
                    app._select_block_by_id(first_block_id)
                    app.split_sentence_var.set("1")
                    app.split_selected_block()
                    self.assertEqual(len(app.project.semantic_blocks), 4)
                    app.merge_selected_block("down")

                self.assertEqual(len(app.project.semantic_blocks), 3)
                reloaded = app.store.load_project(app.project.project_dir)
                self.assertEqual(len(reloaded.semantic_blocks), 3)
                self.assertEqual(reloaded.semantic_blocks[0]["record_id"], first_block_id)
            finally:
                root.destroy()

    def test_app_reopen_signal_survives_reload_after_structural_change(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = ProjectSliceStore(app.workspace_root)

                with patch("runtime.app.messagebox.showinfo"), patch("runtime.app.messagebox.showerror"):
                    app.project_name_var.set("UI Reopen Map")
                    app.film_title_var.set("Demo Film")
                    app.language_var.set("en")
                    app.create_project()
                    app.analysis_text.insert("1.0", SAMPLE_ANALYSIS)
                    app.save_analysis_text()
                    app.review_status_var.set("ready_for_review")
                    app.save_review_status()
                    app.review_status_var.set("approved")
                    app.save_review_status()
                    first_block_id = app.project.semantic_blocks[0]["record_id"]
                    app._select_block_by_id(first_block_id)
                    app.split_sentence_var.set("1")
                    app.split_selected_block()

                reloaded = app.store.load_project(app.project.project_dir)
                self.assertTrue(reloaded.semantic_review_record["reopened_after_change"])
                self.assertIn("reopened", app.approval_message_text.get().lower())
                self.assertIn("boundaries changed after approval", app.reopen_text.get())
            finally:
                root.destroy()


    def test_app_focus_modes_filter_blocks_and_keep_selection_coherent(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = ProjectSliceStore(app.workspace_root)

                with patch("runtime.app.messagebox.showinfo"), patch("runtime.app.messagebox.showerror"):
                    app.project_name_var.set("UI Focus Map")
                    app.film_title_var.set("Demo Film")
                    app.language_var.set("en")
                    app.create_project()
                    app.analysis_text.insert("1.0", SAMPLE_ANALYSIS)
                    app.save_analysis_text()

                    first_block, second_block, third_block = app.project.semantic_blocks
                    project = app.store.update_semantic_block(
                        app.project.project_dir,
                        second_block["record_id"],
                        second_block["title"],
                        second_block["semantic_role"],
                        "Editor clarification added.",
                        output_suitability={
                            "long_video": "strong",
                            "shorts_reels": "candidate",
                            "carousel": "weak",
                            "packaging": "weak",
                        },
                    )
                    project = app.store.update_semantic_block(
                        app.project.project_dir,
                        third_block["record_id"],
                        third_block["title"],
                        third_block["semantic_role"],
                        "Editor clarification added.",
                        output_suitability={
                            "long_video": "weak",
                            "shorts_reels": "strong",
                            "carousel": "strong",
                            "packaging": "not_suitable",
                        },
                    )
                    app._load_project_into_ui(project)

                self.assertEqual(app.semantic_list.size(), 3)
                self.assertIn("showing 3 of 3", app.focus_status_text.get())

                issue_block_id = app.project.semantic_blocks[0]["record_id"]
                long_video_block_id = app.project.semantic_blocks[1]["record_id"]

                app._select_block_by_id(long_video_block_id)
                app.focus_mode_var.set("Issues present")
                app.apply_focus_mode()
                self.assertEqual(app.semantic_list.size(), 1)
                self.assertEqual(app.selected_block_id, issue_block_id)
                self.assertIn("Issues present", app.focus_status_text.get())

                app.focus_mode_var.set("Review-ready")
                app.apply_focus_mode()
                self.assertEqual(app.semantic_list.size(), 2)
                self.assertEqual(app.selected_block_id, long_video_block_id)
                self.assertIn("showing 2 of 3", app.focus_status_text.get())

                app.focus_mode_var.set("Long video focus")
                app.apply_focus_mode()
                self.assertEqual(app.semantic_list.size(), 1)
                self.assertEqual(app.selected_block_id, long_video_block_id)
                self.assertIn("LV:strong", app.semantic_list.get(0))
            finally:
                root.destroy()

    def test_app_focus_empty_state_for_suitability_mode(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = ProjectSliceStore(app.workspace_root)

                with patch("runtime.app.messagebox.showinfo"), patch("runtime.app.messagebox.showerror"):
                    app.project_name_var.set("UI Empty Focus Map")
                    app.film_title_var.set("Demo Film")
                    app.language_var.set("en")
                    app.create_project()
                    app.analysis_text.insert("1.0", SAMPLE_ANALYSIS)
                    app.save_analysis_text()

                    project = app.project
                    for block in list(project.semantic_blocks):
                        project = app.store.update_semantic_block(
                            project.project_dir,
                            block["record_id"],
                            block["title"],
                            block["semantic_role"],
                            "Editor clarification added.",
                            output_suitability={
                                "long_video": "candidate",
                                "shorts_reels": "candidate",
                                "carousel": "candidate",
                                "packaging": "not_suitable",
                            },
                        )
                    app._load_project_into_ui(project)

                app.focus_mode_var.set("Packaging focus")
                app.apply_focus_mode()

                self.assertEqual(app.semantic_list.size(), 0)
                self.assertIsNone(app.selected_block_id)
                self.assertIn("No blocks currently match this suitability focus.", app.focus_status_text.get())
                self.assertIn("No blocks currently match this suitability focus.", app.block_status_var.get())
            finally:
                root.destroy()


if __name__ == "__main__":
    unittest.main()
