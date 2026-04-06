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

            first_block = updated.semantic_blocks[0]
            self.assertEqual(first_block["record_type"], "semantic_block")
            self.assertEqual(first_block["sequence"], 1)
            self.assertIn(first_block["semantic_role"], {"claim", "insight", "mechanism", "transition", "emotional_beat"})

    def test_block_edits_and_review_status_persist_after_reload(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))
            project = store.create_project("Editable Map", film_title="Demo Film", language="en")
            project = store.save_analysis_text(project.project_dir, SAMPLE_ANALYSIS)
            first_block_id = project.semantic_blocks[0]["record_id"]

            project = store.update_semantic_block(
                project.project_dir,
                first_block_id,
                "Opening fear system",
                "mechanism",
                "Use this as the anchor block for later semantic approval.",
            )
            project = store.update_semantic_review_status(project.project_dir, "approved")
            reloaded = store.load_project(project.project_dir)

            edited_block = next(block for block in reloaded.semantic_blocks if block["record_id"] == first_block_id)
            self.assertEqual(edited_block["title"], "Opening fear system")
            self.assertEqual(edited_block["semantic_role"], "mechanism")
            self.assertEqual(edited_block["notes"], "Use this as the anchor block for later semantic approval.")
            self.assertEqual(reloaded.semantic_review_record["review_status"], "approved")
            self.assertTrue(reloaded.semantic_review_record["approved"])
            self.assertEqual(reloaded.project_record["project_status"], "semantic_map_approved")

    def test_reorder_and_readiness_persist_after_reload(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))
            project = store.create_project("Ordered Map", film_title="Demo Film", language="en")
            project = store.save_analysis_text(project.project_dir, SAMPLE_ANALYSIS)

            second_block_id = project.semantic_blocks[1]["record_id"]
            project = store.reorder_semantic_block(project.project_dir, second_block_id, "up")
            reloaded = store.load_project(project.project_dir)

            self.assertEqual(reloaded.semantic_blocks[0]["record_id"], second_block_id)
            self.assertEqual(reloaded.semantic_blocks[0]["sequence"], 1)
            self.assertEqual(reloaded.semantic_blocks[1]["sequence"], 2)

            status_payload = (reloaded.project_dir / "project.meta" / "status.json").read_text(encoding="utf-8")
            self.assertIn('"approval_readiness": "editable_but_complete"', status_payload)

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
    def test_app_saves_block_edits_and_review_status(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = ProjectSliceStore(app.workspace_root)

                with patch("runtime.app.messagebox.showinfo"), patch("runtime.app.messagebox.showerror"):
                    app.project_name_var.set("UI Editable Map")
                    app.film_title_var.set("Demo Film")
                    app.language_var.set("en")
                    app.create_project()
                    app.analysis_text.insert("1.0", SAMPLE_ANALYSIS)
                    app.save_analysis_text()

                    first_block_id = app.project.semantic_blocks[0]["record_id"]
                    app._select_block_by_id(first_block_id)
                    app.block_title_var.set("Edited in UI")
                    app.block_role_var.set("insight")
                    app.notes_text.delete("1.0", "end")
                    app.notes_text.insert("1.0", "Inspector notes persisted through the app layer.")
                    app.save_selected_block()

                    app.review_status_var.set("ready_for_review")
                    app.save_review_status()

                reloaded = app.store.load_project(app.project.project_dir)
                edited_block = next(block for block in reloaded.semantic_blocks if block["record_id"] == first_block_id)
                self.assertEqual(edited_block["title"], "Edited in UI")
                self.assertEqual(edited_block["semantic_role"], "insight")
                self.assertEqual(edited_block["notes"], "Inspector notes persisted through the app layer.")
                self.assertEqual(reloaded.semantic_review_record["review_status"], "ready_for_review")
            finally:
                root.destroy()

    def test_app_reorders_blocks_and_updates_readiness_visibility(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = ProjectSliceStore(app.workspace_root)

                with patch("runtime.app.messagebox.showinfo"), patch("runtime.app.messagebox.showerror"):
                    app.project_name_var.set("UI Ordered Map")
                    app.film_title_var.set("Demo Film")
                    app.language_var.set("en")
                    app.create_project()
                    app.analysis_text.insert("1.0", SAMPLE_ANALYSIS)
                    app.save_analysis_text()

                    second_block_id = app.project.semantic_blocks[1]["record_id"]
                    app._select_block_by_id(second_block_id)
                    app.reorder_selected_block("up")
                    app.review_status_var.set("ready_for_review")
                    app.save_review_status()

                reloaded = app.store.load_project(app.project.project_dir)
                self.assertEqual(reloaded.semantic_blocks[0]["record_id"], second_block_id)
                self.assertEqual(app.readiness_text.get(), "Approval readiness: ready_for_approval")
            finally:
                root.destroy()


if __name__ == "__main__":
    unittest.main()
