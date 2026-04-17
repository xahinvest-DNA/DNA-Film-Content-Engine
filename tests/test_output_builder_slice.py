from __future__ import annotations

import tempfile
import tkinter as tk
import unittest
from pathlib import Path
from unittest.mock import patch

from runtime.app import DNAFilmApp
from runtime.project_slice import ProjectSliceStore


SAMPLE_ANALYSIS = """
Opening frame
The essay opens by claiming that the film is really about inherited fear.

Because rituals make danger feel ordinary, the middle paragraph explains the mechanism that locks the characters into repetition.

The closing paragraph reframes the ending as a transition toward refusal.
""".strip()


class DesktopUISliceTests(unittest.TestCase):
    def test_app_supports_create_intake_edit_and_reopen_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = ProjectSliceStore(app.workspace_root)

                with patch("runtime.ui.app_shell.messagebox.showinfo"), patch("runtime.ui.app_shell.messagebox.showerror"):
                    app.project_name_var.set("UI Slice Project")
                    app.film_title_var.set("Demo Film")
                    app.language_var.set("en")
                    app.create_project()

                    app.analysis_text.insert("1.0", SAMPLE_ANALYSIS)
                    app.save_analysis_text()

                    app._show_block(app.project.semantic_blocks[0])
                    app.block_title_var.set("UI edited opening block")
                    app.block_role_var.set("insight")
                    app.block_suitability_var.set("strong")
                    app.notes_text.delete("1.0", "end")
                    app.notes_text.insert("1.0", "Saved from the inspector.")
                    app.save_selected_block()

                    project_dir = app.project.project_dir
                    app.load_project_from_path(project_dir)

                self.assertEqual("UI edited opening block", app.project.semantic_blocks[0]["title"])
                self.assertEqual("insight", app.project.semantic_blocks[0]["semantic_role"])
                self.assertEqual("strong", app.project.semantic_blocks[0]["output_suitability"])
                self.assertEqual("Saved from the inspector.", app.project.semantic_blocks[0]["notes"])
                self.assertIn("Semantic status: 3 block(s)", app.semantic_status_text.get())
            finally:
                root.destroy()


if __name__ == "__main__":
    unittest.main()
