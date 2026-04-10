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

    def test_manual_candidate_stub_persists_after_reload(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))
            project = store.create_project("Manual Candidate Map", film_title="Demo Film", language="en")
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
            project = store.update_semantic_review_status(project.project_dir, "ready_for_review")
            project = store.update_semantic_review_status(project.project_dir, "approved")
            project = store.add_matching_prep_asset(
                project.project_dir,
                "Main subtitle file",
                "subtitle_reference",
                "E:/demo/subtitles.srt",
                "Primary subtitle reference.",
            )
            project = store.add_matching_prep_asset(
                project.project_dir,
                "Scene stills",
                "film_asset_reference",
                "E:/demo/scene-stills",
                "Prepared stills for manual prep review.",
            )
            project = store.add_matching_candidate_stub(
                project.project_dir,
                project.semantic_blocks[0]["record_id"],
                project.matching_prep_assets[0]["record_id"],
                "Manual opening candidate.",
            )
            project = store.add_matching_candidate_stub(
                project.project_dir,
                project.semantic_blocks[1]["record_id"],
                project.matching_prep_assets[1]["record_id"],
                "Fallback visual candidate.",
            )

            self.assertEqual(len(project.matching_candidate_stubs), 2)
            self.assertEqual(project.matching_candidate_stubs[0]["semantic_block_id"], project.semantic_blocks[0]["record_id"])
            self.assertEqual(project.matching_candidate_stubs[1]["prep_asset_id"], project.matching_prep_assets[1]["record_id"])
            self.assertEqual(project.matching_candidate_stubs[0]["review_status"], "tentative")
            self.assertEqual(project.matching_candidate_stubs[1]["review_status"], "tentative")

            project = store.update_matching_candidate_stub_status(
                project.project_dir,
                project.matching_candidate_stubs[0]["record_id"],
                "selected",
            )
            project = store.update_matching_candidate_stub_rationale(
                project.project_dir,
                project.matching_candidate_stubs[0]["record_id"],
                "Opening scene carries the clearest semantic proof.",
            )
            project = store.update_matching_candidate_stub_status(
                project.project_dir,
                project.matching_candidate_stubs[1]["record_id"],
                "rejected",
            )

            reloaded = store.load_project(project.project_dir)
            self.assertEqual(len(reloaded.matching_candidate_stubs), 2)
            self.assertEqual(reloaded.matching_candidate_stubs[0]["note"], "Manual opening candidate.")
            self.assertEqual(reloaded.matching_candidate_stubs[0]["review_status"], "selected")
            self.assertEqual(reloaded.matching_candidate_stubs[0]["preferred_rationale"], "Opening scene carries the clearest semantic proof.")
            self.assertEqual(reloaded.matching_candidate_stubs[1]["record_id"], "candidate-stub-002")
            self.assertEqual(reloaded.matching_candidate_stubs[1]["review_status"], "rejected")
            self.assertTrue((reloaded.project_dir / "records" / "matching_prep" / "candidate_stubs.json").exists())

            removed = store.remove_matching_candidate_stub(reloaded.project_dir, reloaded.matching_candidate_stubs[1]["record_id"])
            self.assertEqual(len(removed.matching_candidate_stubs), 1)
            removed_reloaded = store.load_project(removed.project_dir)
            self.assertEqual(len(removed_reloaded.matching_candidate_stubs), 1)
            self.assertEqual(removed_reloaded.matching_candidate_stubs[0]["record_id"], "candidate-stub-001")

    def test_duplicate_manual_candidate_stub_is_blocked_for_same_semantic_block_and_prep_asset(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))
            project = store.create_project("Duplicate Guard", film_title="Demo Film", language="en")
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
                "Original manual candidate.",
            )

            with self.assertRaisesRegex(ValueError, "already exists for the selected semantic block and prep input"):
                store.add_matching_candidate_stub(
                    project.project_dir,
                    project.semantic_blocks[0]["record_id"],
                    project.matching_prep_assets[0]["record_id"],
                    "Duplicate manual candidate.",
                )

            reloaded = store.load_project(project.project_dir)
            self.assertEqual(len(reloaded.matching_candidate_stubs), 1)
            self.assertEqual(reloaded.matching_candidate_stubs[0]["note"], "Original manual candidate.")

    def test_selected_candidate_can_be_promoted_to_accepted_reference_and_persist_after_reload(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))
            project = store.create_project("Accepted Reference Map", film_title="Demo Film", language="en")
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
                "Selected candidate promoted to accepted reference.",
            )
            project = store.update_matching_candidate_stub_status(
                project.project_dir,
                project.matching_candidate_stubs[0]["record_id"],
                "selected",
            )
            project = store.update_matching_candidate_stub_rationale(
                project.project_dir,
                project.matching_candidate_stubs[0]["record_id"],
                "Current strongest manual support for later matching work.",
            )

            promoted = store.promote_matching_candidate_stub_to_accepted_reference(
                project.project_dir,
                project.matching_candidate_stubs[0]["record_id"],
            )

            self.assertIsNotNone(promoted.accepted_reference)
            self.assertEqual(promoted.accepted_reference["source_candidate_stub_id"], promoted.matching_candidate_stubs[0]["record_id"])
            self.assertEqual(promoted.accepted_reference["record_type"], "accepted_scene_reference")
            self.assertTrue((promoted.project_dir / "records" / "matching_prep" / "accepted_reference.json").exists())

            reloaded = store.load_project(promoted.project_dir)
            self.assertIsNotNone(reloaded.accepted_reference)
            self.assertEqual(reloaded.accepted_reference["source_candidate_stub_id"], reloaded.matching_candidate_stubs[0]["record_id"])
            self.assertEqual(reloaded.accepted_reference["semantic_block_id"], reloaded.matching_candidate_stubs[0]["semantic_block_id"])

    def test_tentative_candidate_cannot_be_promoted_to_accepted_reference(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))
            project = store.create_project("Tentative Promotion Block", film_title="Demo Film", language="en")
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
                "Tentative candidate stays tentative.",
            )

            with self.assertRaisesRegex(ValueError, "Only selected manual candidate stubs can be promoted"):
                store.promote_matching_candidate_stub_to_accepted_reference(
                    project.project_dir,
                    project.matching_candidate_stubs[0]["record_id"],
                )

    def test_rejected_candidate_cannot_be_promoted_to_accepted_reference(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))
            project = store.create_project("Rejected Promotion Block", film_title="Demo Film", language="en")
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
                "Rejected candidate cannot be promoted.",
            )
            project = store.update_matching_candidate_stub_status(
                project.project_dir,
                project.matching_candidate_stubs[0]["record_id"],
                "rejected",
            )

            with self.assertRaisesRegex(ValueError, "Only selected manual candidate stubs can be promoted"):
                store.promote_matching_candidate_stub_to_accepted_reference(
                    project.project_dir,
                    project.matching_candidate_stubs[0]["record_id"],
                )

    def test_new_selected_candidate_replaces_prior_accepted_reference(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = ProjectSliceStore(Path(temp_dir))
            project = store.create_project("Accepted Reference Replacement", film_title="Demo Film", language="en")
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
            project = store.add_matching_prep_asset(
                project.project_dir,
                "Scene stills",
                "film_asset_reference",
                "E:/demo/scene-stills",
                "Prepared stills for manual prep review.",
            )
            project = store.add_matching_candidate_stub(
                project.project_dir,
                project.semantic_blocks[0]["record_id"],
                project.matching_prep_assets[0]["record_id"],
                "First selected candidate.",
            )
            project = store.add_matching_candidate_stub(
                project.project_dir,
                project.semantic_blocks[1]["record_id"],
                project.matching_prep_assets[1]["record_id"],
                "Second selected candidate replaces first.",
            )
            project = store.update_matching_candidate_stub_status(
                project.project_dir,
                project.matching_candidate_stubs[0]["record_id"],
                "selected",
            )
            project = store.update_matching_candidate_stub_status(
                project.project_dir,
                project.matching_candidate_stubs[1]["record_id"],
                "selected",
            )
            project = store.promote_matching_candidate_stub_to_accepted_reference(
                project.project_dir,
                project.matching_candidate_stubs[0]["record_id"],
            )
            replaced = store.promote_matching_candidate_stub_to_accepted_reference(
                project.project_dir,
                project.matching_candidate_stubs[1]["record_id"],
            )

            self.assertIsNotNone(replaced.accepted_reference)
            self.assertEqual(replaced.accepted_reference["source_candidate_stub_id"], replaced.matching_candidate_stubs[1]["record_id"])
            self.assertEqual(replaced.accepted_reference["prep_asset_id"], replaced.matching_candidate_stubs[1]["prep_asset_id"])
            self.assertEqual(replaced.accepted_reference["record_id"], "accepted-reference-current")

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


    def test_app_focus_navigation_moves_within_all_blocks_and_respects_boundaries(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = ProjectSliceStore(app.workspace_root)

                with patch("runtime.app.messagebox.showinfo"), patch("runtime.app.messagebox.showerror"):
                    app.project_name_var.set("UI Focus Navigation Map")
                    app.film_title_var.set("Demo Film")
                    app.language_var.set("en")
                    app.create_project()
                    app.analysis_text.insert("1.0", SAMPLE_ANALYSIS)
                    app.save_analysis_text()

                first_block_id = app.project.semantic_blocks[0]["record_id"]
                second_block_id = app.project.semantic_blocks[1]["record_id"]
                third_block_id = app.project.semantic_blocks[2]["record_id"]

                self.assertEqual(app.selected_block_id, first_block_id)
                self.assertEqual(app.focus_position_text.get(), "Focused item: 1 of 3")
                self.assertEqual(str(app.previous_focus_button.cget("state")), "disabled")
                self.assertEqual(str(app.next_focus_button.cget("state")), "normal")

                app.navigate_focus("next")
                self.assertEqual(app.selected_block_id, second_block_id)
                self.assertEqual(app.focus_position_text.get(), "Focused item: 2 of 3")
                self.assertEqual(str(app.previous_focus_button.cget("state")), "normal")
                self.assertEqual(str(app.next_focus_button.cget("state")), "normal")

                app.navigate_focus("next")
                self.assertEqual(app.selected_block_id, third_block_id)
                self.assertEqual(app.focus_position_text.get(), "Focused item: 3 of 3")
                self.assertEqual(str(app.previous_focus_button.cget("state")), "normal")
                self.assertEqual(str(app.next_focus_button.cget("state")), "disabled")

                app.navigate_focus("next")
                self.assertEqual(app.selected_block_id, third_block_id)
            finally:
                root.destroy()

    def test_app_focus_navigation_tracks_issue_and_suitability_subsets(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = ProjectSliceStore(app.workspace_root)

                with patch("runtime.app.messagebox.showinfo"), patch("runtime.app.messagebox.showerror"):
                    app.project_name_var.set("UI Focus Subset Map")
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

                issue_block_id = app.project.semantic_blocks[0]["record_id"]
                long_video_block_id = app.project.semantic_blocks[1]["record_id"]
                third_block_id = app.project.semantic_blocks[2]["record_id"]

                app.focus_mode_var.set("Issues present")
                app.apply_focus_mode()
                self.assertEqual(app.selected_block_id, issue_block_id)
                self.assertEqual(app.focus_position_text.get(), "Focused item: 1 of 1")
                self.assertEqual(str(app.previous_focus_button.cget("state")), "disabled")
                self.assertEqual(str(app.next_focus_button.cget("state")), "disabled")

                app.focus_mode_var.set("Review-ready")
                app.apply_focus_mode()
                self.assertEqual(app.selected_block_id, long_video_block_id)
                self.assertEqual(app.focus_position_text.get(), "Focused item: 1 of 2")
                self.assertEqual(str(app.previous_focus_button.cget("state")), "disabled")
                self.assertEqual(str(app.next_focus_button.cget("state")), "normal")

                app.navigate_focus("next")
                self.assertEqual(app.selected_block_id, third_block_id)
                self.assertEqual(app.focus_position_text.get(), "Focused item: 2 of 2")

                app.focus_mode_var.set("Long video focus")
                app.apply_focus_mode()
                self.assertEqual(app.selected_block_id, long_video_block_id)
                self.assertEqual(app.focus_position_text.get(), "Focused item: 1 of 1")
                self.assertEqual(str(app.previous_focus_button.cget("state")), "disabled")
                self.assertEqual(str(app.next_focus_button.cget("state")), "disabled")
            finally:
                root.destroy()


    def test_app_adjacent_context_shows_middle_and_boundary_neighbors(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = ProjectSliceStore(app.workspace_root)

                with patch("runtime.app.messagebox.showinfo"), patch("runtime.app.messagebox.showerror"):
                    app.project_name_var.set("UI Adjacent Context Map")
                    app.film_title_var.set("Demo Film")
                    app.language_var.set("en")
                    app.create_project()
                    app.analysis_text.insert("1.0", SAMPLE_ANALYSIS)
                    app.save_analysis_text()

                first_block_id = app.project.semantic_blocks[0]["record_id"]
                second_block = app.project.semantic_blocks[1]
                third_block = app.project.semantic_blocks[2]

                app._select_block_by_id(second_block["record_id"])
                self.assertIn("01.", app.previous_context_text.get())
                self.assertIn("03.", app.next_context_text.get())
                self.assertNotIn(second_block["title"], app.previous_context_text.get())
                self.assertNotIn(second_block["title"], app.next_context_text.get())

                app._select_block_by_id(first_block_id)
                self.assertEqual(app.previous_context_text.get(), "Previous: No previous semantic block")
                self.assertIn("02.", app.next_context_text.get())

                app._select_block_by_id(third_block["record_id"])
                self.assertIn("02.", app.previous_context_text.get())
                self.assertEqual(app.next_context_text.get(), "Next: No next semantic block")
            finally:
                root.destroy()

    def test_app_adjacent_context_stays_canonical_under_focus_mode(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = ProjectSliceStore(app.workspace_root)

                with patch("runtime.app.messagebox.showinfo"), patch("runtime.app.messagebox.showerror"):
                    app.project_name_var.set("UI Canonical Neighbor Map")
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

                target_block_id = app.project.semantic_blocks[1]["record_id"]
                app.focus_mode_var.set("Long video focus")
                app.apply_focus_mode()

                self.assertEqual(app.selected_block_id, target_block_id)
                self.assertIn("01.", app.previous_context_text.get())
                self.assertIn("03.", app.next_context_text.get())
                self.assertEqual(app.semantic_list.size(), 1)
            finally:
                root.destroy()

    def test_app_adjacent_context_recomputes_after_reorder_and_split(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = ProjectSliceStore(app.workspace_root)

                with patch("runtime.app.messagebox.showinfo"), patch("runtime.app.messagebox.showerror"):
                    app.project_name_var.set("UI Context Recompute Map")
                    app.film_title_var.set("Demo Film")
                    app.language_var.set("en")
                    app.create_project()
                    app.analysis_text.insert("1.0", SAMPLE_ANALYSIS)
                    app.save_analysis_text()

                    second_block_id = app.project.semantic_blocks[1]["record_id"]
                    app._select_block_by_id(second_block_id)
                    app.reorder_selected_block("up")
                    self.assertEqual(app.selected_block_id, second_block_id)
                    self.assertEqual(app.previous_context_text.get(), "Previous: No previous semantic block")
                    self.assertIn("02.", app.next_context_text.get())

                    first_block_id = app.project.semantic_blocks[0]["record_id"]
                    app._select_block_by_id(first_block_id)
                    app.split_sentence_var.set("1")
                    app.split_selected_block()

                self.assertEqual(app.selected_block_id, first_block_id)
                self.assertEqual(app.previous_context_text.get(), "Previous: No previous semantic block")
                self.assertIn("02.", app.next_context_text.get())
            finally:
                root.destroy()


    def test_app_focus_span_summary_covers_full_and_filtered_ranges(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = ProjectSliceStore(app.workspace_root)

                with patch("runtime.app.messagebox.showinfo"), patch("runtime.app.messagebox.showerror"):
                    app.project_name_var.set("UI Focus Span Map")
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

                self.assertEqual(app.focus_span_text.get(), "Focus span: 3 blocks | seq 01-03")

                app.focus_mode_var.set("Review-ready")
                app.apply_focus_mode()
                self.assertEqual(app.focus_span_text.get(), "Focus span: 2 blocks | seq 02-03")

                app.focus_mode_var.set("Long video focus")
                app.apply_focus_mode()
                self.assertEqual(app.focus_span_text.get(), "Focus span: 1 block | seq 02")
            finally:
                root.destroy()

    def test_app_focus_span_summary_handles_empty_subset(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = ProjectSliceStore(app.workspace_root)

                with patch("runtime.app.messagebox.showinfo"), patch("runtime.app.messagebox.showerror"):
                    app.project_name_var.set("UI Empty Span Map")
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
                self.assertEqual(app.focus_span_text.get(), "Focus span: no matching blocks")
            finally:
                root.destroy()

    def test_app_focus_span_summary_recomputes_after_structure_changes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = ProjectSliceStore(app.workspace_root)

                with patch("runtime.app.messagebox.showinfo"), patch("runtime.app.messagebox.showerror"):
                    app.project_name_var.set("UI Structure Span Map")
                    app.film_title_var.set("Demo Film")
                    app.language_var.set("en")
                    app.create_project()
                    app.analysis_text.insert("1.0", SAMPLE_ANALYSIS)
                    app.save_analysis_text()

                    self.assertEqual(app.focus_span_text.get(), "Focus span: 3 blocks | seq 01-03")

                    second_block_id = app.project.semantic_blocks[1]["record_id"]
                    app._select_block_by_id(second_block_id)
                    app.reorder_selected_block("up")
                    self.assertEqual(app.focus_span_text.get(), "Focus span: 3 blocks | seq 01-03")

                    first_block_id = app.project.semantic_blocks[0]["record_id"]
                    app._select_block_by_id(first_block_id)
                    app.split_sentence_var.set("1")
                    app.split_selected_block()
                    self.assertEqual(app.focus_span_text.get(), "Focus span: 4 blocks | seq 01-04")

                    current_first = app.project.semantic_blocks[0]["record_id"]
                    app._select_block_by_id(current_first)
                    app.merge_selected_block("down")

                self.assertEqual(app.focus_span_text.get(), "Focus span: 3 blocks | seq 01-03")
            finally:
                root.destroy()


    def test_app_matching_prep_gate_tracks_under_edit_to_approved(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = ProjectSliceStore(app.workspace_root)

                with patch("runtime.app.messagebox.showinfo"), patch("runtime.app.messagebox.showerror"):
                    app.project_name_var.set("UI Matching Gate Map")
                    app.film_title_var.set("Demo Film")
                    app.language_var.set("en")
                    app.create_project()

                    self.assertEqual(app.matching_prep_text.get(), "Matching prep readiness: blocked | semantic map not established yet")

                    app.analysis_text.insert("1.0", SAMPLE_ANALYSIS)
                    app.save_analysis_text()
                    self.assertEqual(app.matching_prep_text.get(), "Matching prep readiness: conditionally plausible | semantic map is mixed and should be tightened")

                    project = app.project
                    for block in list(project.semantic_blocks):
                        project = app.store.update_semantic_block(
                            project.project_dir,
                            block["record_id"],
                            block["title"],
                            block["semantic_role"],
                            "Editor clarification added.",
                        )
                    app._load_project_into_ui(project)
                    self.assertEqual(app.matching_prep_text.get(), "Matching prep readiness: blocked | semantic map is still under edit")

                    app.review_status_var.set("ready_for_review")
                    app.save_review_status()
                    self.assertEqual(app.matching_prep_text.get(), "Matching prep readiness: conditionally plausible | semantic review is staged but approval is still pending")

                    app.review_status_var.set("approved")
                    app.save_review_status()
                    self.assertEqual(app.matching_prep_text.get(), "Matching prep readiness: ready | semantic map approved")
            finally:
                root.destroy()

    def test_app_matching_prep_gate_surfaces_reopen_and_structure_changes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = ProjectSliceStore(app.workspace_root)

                with patch("runtime.app.messagebox.showinfo"), patch("runtime.app.messagebox.showerror"):
                    app.project_name_var.set("UI Reopen Gate Map")
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
                        )
                    app._load_project_into_ui(project)
                    app.review_status_var.set("ready_for_review")
                    app.save_review_status()
                    app.review_status_var.set("approved")
                    app.save_review_status()
                    self.assertEqual(app.matching_prep_text.get(), "Matching prep readiness: ready | semantic map approved")

                    second_block_id = app.project.semantic_blocks[1]["record_id"]
                    app._select_block_by_id(second_block_id)
                    app.reorder_selected_block("up")
                    self.assertEqual(app.matching_prep_text.get(), "Matching prep readiness: blocked | semantic approval was reopened after change")

                    reloaded = app.store.load_project(app.project.project_dir)
                    self.assertTrue(reloaded.semantic_review_record["reopened_after_change"])
                    self.assertEqual(app._matching_prep_gate_text(reloaded), "Matching prep readiness: blocked | semantic approval was reopened after change")
            finally:
                root.destroy()

    def test_app_matching_prep_gate_handles_mixed_review_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = ProjectSliceStore(app.workspace_root)

                with patch("runtime.app.messagebox.showinfo"), patch("runtime.app.messagebox.showerror"):
                    app.project_name_var.set("UI Mixed Gate Map")
                    app.film_title_var.set("Demo Film")
                    app.language_var.set("en")
                    app.create_project()
                    app.analysis_text.insert("1.0", SAMPLE_ANALYSIS)
                    app.save_analysis_text()

                    first_block = app.project.semantic_blocks[0]
                    second_block = app.project.semantic_blocks[1]
                    project = app.store.update_semantic_block(
                        app.project.project_dir,
                        second_block["record_id"],
                        second_block["title"],
                        second_block["semantic_role"],
                        "Editor clarification added.",
                    )
                    app._load_project_into_ui(project)
                    self.assertEqual(app.matching_prep_text.get(), "Matching prep readiness: conditionally plausible | semantic map is mixed and should be tightened")

                    app._select_block_by_id(first_block["record_id"])
                    app.split_sentence_var.set("1")
                    app.split_selected_block()
                    self.assertEqual(app.matching_prep_text.get(), "Matching prep readiness: conditionally plausible | semantic map is mixed and should be tightened")

                    current_first = app.project.semantic_blocks[0]["record_id"]
                    app._select_block_by_id(current_first)
                    app.merge_selected_block("down")
                    self.assertEqual(app.matching_prep_text.get(), "Matching prep readiness: conditionally plausible | semantic map is mixed and should be tightened")
            finally:
                root.destroy()


    def test_app_matching_prep_view_stays_blocked_without_semantic_map(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = ProjectSliceStore(app.workspace_root)

                with patch("runtime.app.messagebox.showinfo"), patch("runtime.app.messagebox.showerror"):
                    app.project_name_var.set("UI Matching Prep Blocked Map")
                    app.film_title_var.set("Demo Film")
                    app.language_var.set("en")
                    app.create_project()

                app._switch_view("Matching Prep")
                handoff = app.matching_prep_handoff.get("1.0", "end").strip()

                self.assertEqual(app.current_view.get(), "Matching Prep")
                self.assertEqual(app.matching_prep_text.get(), "Matching prep readiness: blocked | semantic map not established yet")
                self.assertIn("blocked", app.matching_prep_status_text.get().lower())
                self.assertIn("0 approved semantic blocks", app.matching_prep_summary_text.get())
                self.assertIn("Matching Prep remains blocked", handoff)
            finally:
                root.destroy()

    def test_app_matching_prep_view_opens_with_approved_semantic_handoff(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = ProjectSliceStore(app.workspace_root)

                with patch("runtime.app.messagebox.showinfo"), patch("runtime.app.messagebox.showerror"):
                    app.project_name_var.set("UI Matching Prep Open Map")
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
                        )
                    app._load_project_into_ui(project)
                    app.review_status_var.set("ready_for_review")
                    app.save_review_status()
                    app.review_status_var.set("approved")
                    app.save_review_status()

                app._switch_view("Matching Prep")
                handoff = app.matching_prep_handoff.get("1.0", "end").strip()

                self.assertEqual(app.current_view.get(), "Matching Prep")
                self.assertEqual(app.next_action.get(), "Next action: Open Matching Prep")
                self.assertEqual(app.matching_prep_text.get(), "Matching prep readiness: ready | semantic map approved")
                self.assertIn("Matching Prep is open", app.matching_prep_status_text.get())
                self.assertIn("3 approved semantic block(s)", app.matching_prep_summary_text.get())
                self.assertIn("Approved semantic handoff for later matching prep", handoff)
                self.assertIn("01.", handoff)
                self.assertIn("Notes: Editor clarification added.", handoff)
            finally:
                root.destroy()

    def test_app_matching_prep_view_returns_to_blocked_after_reopen(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = ProjectSliceStore(app.workspace_root)

                with patch("runtime.app.messagebox.showinfo"), patch("runtime.app.messagebox.showerror"):
                    app.project_name_var.set("UI Matching Prep Reopen Map")
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
                        )
                    app._load_project_into_ui(project)
                    app.review_status_var.set("ready_for_review")
                    app.save_review_status()
                    app.review_status_var.set("approved")
                    app.save_review_status()

                    target_block_id = app.project.semantic_blocks[1]["record_id"]
                    app._select_block_by_id(target_block_id)
                    app.reorder_selected_block("up")

                app._switch_view("Matching Prep")
                handoff = app.matching_prep_handoff.get("1.0", "end").strip()

                self.assertEqual(app.matching_prep_text.get(), "Matching prep readiness: blocked | semantic approval was reopened after change")
                self.assertIn("blocked", app.matching_prep_status_text.get().lower())
                self.assertIn("0 approved semantic blocks", app.matching_prep_summary_text.get())
                self.assertIn("semantic approval was reopened after change", handoff)
            finally:
                root.destroy()


    def test_app_matching_prep_asset_registration_persists_after_reload(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = ProjectSliceStore(app.workspace_root)

                with patch("runtime.app.messagebox.showinfo"), patch("runtime.app.messagebox.showerror"):
                    app.project_name_var.set("UI Matching Prep Asset Map")
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
                        )
                    app._load_project_into_ui(project)
                    app.review_status_var.set("ready_for_review")
                    app.save_review_status()
                    app.review_status_var.set("approved")
                    app.save_review_status()

                    app._switch_view("Matching Prep")
                    app.asset_label_var.set("Main subtitle file")
                    app.asset_type_var.set("subtitle_reference")
                    app.asset_reference_var.set("E:/demo/subtitles.srt")
                    app.asset_notes_text.insert("1.0", "Russian subtitle reference for later matching review.")
                    app.add_matching_prep_asset()

                    app.asset_label_var.set("Film scene folder")
                    app.asset_type_var.set("film_asset_reference")
                    app.asset_reference_var.set("E:/demo/scene-stills")
                    app.asset_notes_text.insert("1.0", "Folder with manually prepared scene stills.")
                    app.add_matching_prep_asset()

                handoff = app.matching_prep_handoff.get("1.0", "end").strip()
                reloaded = app.store.load_project(app.project.project_dir)

                self.assertEqual(len(reloaded.matching_prep_assets), 2)
                self.assertIn("semantic-plus-asset registration present", app.matching_prep_summary_text.get())
                self.assertIn("2 prep input(s) registered", app.matching_asset_summary_text.get())
                self.assertIn("no manual candidate stubs yet", app.matching_candidate_summary_text.get())
                self.assertIn("Manual candidate stubs", handoff)
                self.assertIn("- none yet", handoff)
                self.assertIn("Main subtitle file", handoff)
                self.assertIn("Film scene folder", handoff)
                self.assertIn("E:/demo/subtitles.srt", handoff)
                self.assertEqual(reloaded.matching_prep_assets[0]["asset_type"], "subtitle_reference")
                self.assertEqual(reloaded.matching_prep_assets[1]["asset_type"], "film_asset_reference")
            finally:
                root.destroy()

    def test_app_matching_prep_manual_candidate_stub_persists_after_reload(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = ProjectSliceStore(app.workspace_root)

                with patch("runtime.app.messagebox.showinfo"), patch("runtime.app.messagebox.showerror"):
                    app.project_name_var.set("UI Matching Candidate Map")
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
                        )
                    app._load_project_into_ui(project)
                    app.review_status_var.set("ready_for_review")
                    app.save_review_status()
                    app.review_status_var.set("approved")
                    app.save_review_status()

                    app._switch_view("Matching Prep")
                    app.asset_label_var.set("Main subtitle file")
                    app.asset_type_var.set("subtitle_reference")
                    app.asset_reference_var.set("E:/demo/subtitles.srt")
                    app.asset_notes_text.insert("1.0", "Subtitle reference for manual candidate linking.")
                    app.add_matching_prep_asset()

                    app.asset_label_var.set("Scene stills")
                    app.asset_type_var.set("film_asset_reference")
                    app.asset_reference_var.set("E:/demo/scene-stills")
                    app.asset_notes_text.insert("1.0", "Still-frame folder for manual review.")
                    app.add_matching_prep_asset()

                    app.candidate_block_var.set(app.candidate_block_combo["values"][0])
                    app.candidate_asset_var.set(app.candidate_asset_combo["values"][0])
                    app.candidate_note_var.set("Opening candidate stub.")
                    app.add_matching_candidate_stub()

                    app.candidate_block_var.set(app.candidate_block_combo["values"][1])
                    app.candidate_asset_var.set(app.candidate_asset_combo["values"][1])
                    app.candidate_note_var.set("Second semantic-to-asset stub.")
                    app.add_matching_candidate_stub()

                    app.candidate_stub_var.set(app.candidate_stub_combo["values"][0])
                    app.on_candidate_stub_selected()
                    app.candidate_status_var.set("selected")
                    app.save_matching_candidate_status()

                    app.candidate_stub_var.set(app.candidate_stub_combo["values"][1])
                    app.on_candidate_stub_selected()
                    app.candidate_status_var.set("rejected")
                    app.save_matching_candidate_status()

                handoff = app.matching_prep_handoff.get("1.0", "end").strip()
                reloaded = app.store.load_project(app.project.project_dir)

                self.assertEqual(len(reloaded.matching_candidate_stubs), 2)
                self.assertIn("2 saved in this project", app.matching_candidate_summary_text.get())
                self.assertIn("selected 1", app.matching_candidate_summary_text.get())
                self.assertIn("rejected 1", app.matching_candidate_summary_text.get())
                self.assertIn("Manual candidate stubs", handoff)
                self.assertIn("Opening candidate stub.", handoff)
                self.assertIn("Second semantic-to-asset stub.", handoff)
                self.assertIn("Review status: selected", handoff)
                self.assertIn("Review status: rejected", handoff)
                self.assertIn("candidate-stub-001", handoff)
                self.assertEqual(reloaded.matching_candidate_stubs[0]["review_status"], "selected")
                self.assertEqual(reloaded.matching_candidate_stubs[1]["record_id"], "candidate-stub-002")
                self.assertEqual(reloaded.matching_candidate_stubs[1]["review_status"], "rejected")
            finally:
                root.destroy()

    def test_app_matching_prep_shows_accepted_reference_after_selected_promotion(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = ProjectSliceStore(app.workspace_root)

                with patch("runtime.app.messagebox.showinfo"), patch("runtime.app.messagebox.showerror"):
                    app.project_name_var.set("UI Accepted Reference Map")
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
                        )
                    app._load_project_into_ui(project)
                    app.review_status_var.set("ready_for_review")
                    app.save_review_status()
                    app.review_status_var.set("approved")
                    app.save_review_status()

                    app._switch_view("Matching Prep")
                    app.asset_label_var.set("Main subtitle file")
                    app.asset_type_var.set("subtitle_reference")
                    app.asset_reference_var.set("E:/demo/subtitles.srt")
                    app.asset_notes_text.insert("1.0", "Subtitle reference for accepted reference promotion.")
                    app.add_matching_prep_asset()

                    app.candidate_block_var.set(app.candidate_block_combo["values"][0])
                    app.candidate_asset_var.set(app.candidate_asset_combo["values"][0])
                    app.candidate_note_var.set("Selected candidate promoted in app flow.")
                    app.add_matching_candidate_stub()

                    app.candidate_stub_var.set(app.candidate_stub_combo["values"][0])
                    app.on_candidate_stub_selected()
                    app.candidate_status_var.set("selected")
                    app.save_matching_candidate_status()
                    app.candidate_rationale_var.set("Current strongest accepted prep reference.")
                    app.save_matching_candidate_rationale()
                    app.promote_matching_candidate_to_accepted_reference()

                handoff = app.matching_prep_handoff.get("1.0", "end").strip()
                reloaded = app.store.load_project(app.project.project_dir)
                self.assertIsNotNone(reloaded.accepted_reference)
                self.assertIn("current accepted reference exists", app.matching_accepted_reference_summary_text.get())
                self.assertIn("Accepted reference for later matching work", handoff)
                self.assertIn("Selected candidate promoted in app flow.", handoff)
                self.assertIn("Current strongest accepted prep reference.", handoff)
                self.assertIn("Accepted from selected candidate stub: candidate-stub-001", handoff)
                self.assertIn("not a timecoded final match", handoff)
            finally:
                root.destroy()

    def test_app_matching_prep_accepted_reference_remains_visible_when_lane_reopens(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = ProjectSliceStore(app.workspace_root)

                with patch("runtime.app.messagebox.showinfo"), patch("runtime.app.messagebox.showerror"):
                    app.project_name_var.set("UI Accepted Reference Reopen Map")
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
                        )
                    app._load_project_into_ui(project)
                    app.review_status_var.set("ready_for_review")
                    app.save_review_status()
                    app.review_status_var.set("approved")
                    app.save_review_status()

                    app._switch_view("Matching Prep")
                    app.asset_label_var.set("Transcript reference")
                    app.asset_type_var.set("transcript_reference")
                    app.asset_reference_var.set("E:/demo/transcript.txt")
                    app.asset_notes_text.insert("1.0", "Transcript prepared for accepted reference visibility.")
                    app.add_matching_prep_asset()

                    app.candidate_block_var.set(app.candidate_block_combo["values"][0])
                    app.candidate_asset_var.set(app.candidate_asset_combo["values"][0])
                    app.candidate_note_var.set("Accepted reference remains visible when reopened.")
                    app.add_matching_candidate_stub()

                    app.candidate_stub_var.set(app.candidate_stub_combo["values"][0])
                    app.on_candidate_stub_selected()
                    app.candidate_status_var.set("selected")
                    app.save_matching_candidate_status()
                    app.promote_matching_candidate_to_accepted_reference()

                    target_block_id = app.project.semantic_blocks[1]["record_id"]
                    app._select_block_by_id(target_block_id)
                    app.reorder_selected_block("up")
                    app._switch_view("Matching Prep")

                handoff = app.matching_prep_handoff.get("1.0", "end").strip()
                self.assertEqual(app.matching_prep_text.get(), "Matching prep readiness: blocked | semantic approval was reopened after change")
                self.assertIn("current accepted reference exists", app.matching_accepted_reference_summary_text.get())
                self.assertIn("Accepted reference for later matching work", handoff)
                self.assertIn("Accepted reference remains visible when reopened.", handoff)
                self.assertIn("Accepted from selected candidate stub: candidate-stub-001", handoff)
            finally:
                root.destroy()

    def test_app_matching_prep_blocks_exact_duplicate_manual_candidate_stub(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = ProjectSliceStore(app.workspace_root)
                with patch("runtime.app.messagebox.showinfo"), patch("runtime.app.messagebox.showerror") as mock_error:
                    app.project_name_var.set("Duplicate Guard")
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
                        )
                    project = app.store.update_semantic_review_status(project.project_dir, "ready_for_review")
                    project = app.store.update_semantic_review_status(project.project_dir, "approved")
                    app._load_project_into_ui(project)

                    app._switch_view("Matching Prep")
                    app.asset_label_var.set("Main subtitle file")
                    app.asset_type_var.set("subtitle_reference")
                    app.asset_reference_var.set("E:/demo/subtitles.srt")
                    app.asset_notes_text.insert("1.0", "Subtitle reference for manual candidate linking.")
                    app.add_matching_prep_asset()

                    app.candidate_block_var.set(app.candidate_block_combo["values"][0])
                    app.candidate_asset_var.set(app.candidate_asset_combo["values"][0])
                    app.candidate_note_var.set("Original manual candidate.")
                    app.add_matching_candidate_stub()

                    app.candidate_block_var.set(app.candidate_block_combo["values"][0])
                    app.candidate_asset_var.set(app.candidate_asset_combo["values"][0])
                    app.candidate_note_var.set("Duplicate manual candidate.")
                    app.add_matching_candidate_stub()

                reloaded = app.store.load_project(app.project.project_dir)
                self.assertEqual(len(reloaded.matching_candidate_stubs), 1)
                self.assertEqual(reloaded.matching_candidate_stubs[0]["note"], "Original manual candidate.")
                mock_error.assert_called_once()
                self.assertIn("already exists for the selected semantic block and prep input", mock_error.call_args.args[1])
                self.assertIn("1 visible of 1 saved in this project", app.matching_candidate_summary_text.get())
            finally:
                root.destroy()

    def test_app_matching_prep_can_remove_tentative_candidate_stub(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = ProjectSliceStore(app.workspace_root)

                with patch("runtime.app.messagebox.showinfo"), patch("runtime.app.messagebox.showerror"):
                    app.project_name_var.set("UI Matching Remove Tentative Map")
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
                        )
                    app._load_project_into_ui(project)
                    app.review_status_var.set("ready_for_review")
                    app.save_review_status()
                    app.review_status_var.set("approved")
                    app.save_review_status()

                    app._switch_view("Matching Prep")
                    app.asset_label_var.set("Transcript reference")
                    app.asset_type_var.set("transcript_reference")
                    app.asset_reference_var.set("E:/demo/transcript.txt")
                    app.asset_notes_text.insert("1.0", "Transcript prepared for manual linking.")
                    app.add_matching_prep_asset()

                    app.candidate_block_var.set(app.candidate_block_combo["values"][0])
                    app.candidate_asset_var.set(app.candidate_asset_combo["values"][0])
                    app.candidate_note_var.set("Tentative candidate to remove.")
                    app.add_matching_candidate_stub()

                    app.candidate_stub_var.set(app.candidate_stub_combo["values"][0])
                    app.on_candidate_stub_selected()
                    app.remove_matching_candidate_stub()

                handoff = app.matching_prep_handoff.get("1.0", "end").strip()
                reloaded = app.store.load_project(app.project.project_dir)
                self.assertEqual(len(reloaded.matching_candidate_stubs), 0)
                self.assertIn("no manual candidate stubs yet", app.matching_candidate_summary_text.get())
                self.assertIn("- none yet", handoff)
            finally:
                root.destroy()

    def test_app_matching_prep_can_remove_selected_candidate_and_recompute_cues(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = ProjectSliceStore(app.workspace_root)

                with patch("runtime.app.messagebox.showinfo"), patch("runtime.app.messagebox.showerror"):
                    app.project_name_var.set("UI Matching Remove Selected Map")
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
                        )
                    app._load_project_into_ui(project)
                    app.review_status_var.set("ready_for_review")
                    app.save_review_status()
                    app.review_status_var.set("approved")
                    app.save_review_status()

                    app._switch_view("Matching Prep")
                    app.asset_label_var.set("Transcript reference")
                    app.asset_type_var.set("transcript_reference")
                    app.asset_reference_var.set("E:/demo/transcript.txt")
                    app.asset_notes_text.insert("1.0", "Transcript prepared for manual linking.")
                    app.add_matching_prep_asset()

                    app.candidate_block_var.set(app.candidate_block_combo["values"][0])
                    app.candidate_asset_var.set(app.candidate_asset_combo["values"][0])
                    app.candidate_note_var.set("Selected candidate to remove.")
                    app.add_matching_candidate_stub()

                    app.candidate_block_var.set(app.candidate_block_combo["values"][1])
                    app.candidate_asset_var.set(app.candidate_asset_combo["values"][0])
                    app.candidate_note_var.set("Tentative candidate remains.")
                    app.add_matching_candidate_stub()

                    app.candidate_stub_var.set(app.candidate_stub_combo["values"][0])
                    app.on_candidate_stub_selected()
                    app.candidate_status_var.set("selected")
                    app.save_matching_candidate_status()
                    app.candidate_rationale_var.set("Current best manual proof choice.")
                    app.save_matching_candidate_rationale()

                    app.remove_matching_candidate_stub()

                handoff = app.matching_prep_handoff.get("1.0", "end").strip()
                reloaded = app.store.load_project(app.project.project_dir)
                self.assertEqual(len(reloaded.matching_candidate_stubs), 1)
                self.assertIn("Preferred subset readiness: preferred subset not fixed yet", app.matching_candidate_summary_text.get())
                self.assertIn("Selected candidates currently preferred for review: none yet.", app.matching_candidate_summary_text.get())
                self.assertNotIn("Selected candidate to remove.", handoff)
                self.assertNotIn("Current best manual proof choice.", handoff)
                self.assertIn("Tentative candidate remains.", handoff)
            finally:
                root.destroy()

    def test_app_matching_prep_candidate_removal_survives_reload(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = ProjectSliceStore(app.workspace_root)

                with patch("runtime.app.messagebox.showinfo"), patch("runtime.app.messagebox.showerror"):
                    app.project_name_var.set("UI Matching Remove Reload Map")
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
                        )
                    app._load_project_into_ui(project)
                    app.review_status_var.set("ready_for_review")
                    app.save_review_status()
                    app.review_status_var.set("approved")
                    app.save_review_status()

                    app._switch_view("Matching Prep")
                    app.asset_label_var.set("Transcript reference")
                    app.asset_type_var.set("transcript_reference")
                    app.asset_reference_var.set("E:/demo/transcript.txt")
                    app.asset_notes_text.insert("1.0", "Transcript prepared for manual linking.")
                    app.add_matching_prep_asset()

                    app.candidate_block_var.set(app.candidate_block_combo["values"][0])
                    app.candidate_asset_var.set(app.candidate_asset_combo["values"][0])
                    app.candidate_note_var.set("First candidate removed before reload.")
                    app.add_matching_candidate_stub()

                    app.candidate_block_var.set(app.candidate_block_combo["values"][1])
                    app.candidate_asset_var.set(app.candidate_asset_combo["values"][0])
                    app.candidate_note_var.set("Remaining candidate after reload.")
                    app.add_matching_candidate_stub()

                    app.candidate_stub_var.set(app.candidate_stub_combo["values"][0])
                    app.on_candidate_stub_selected()
                    app.remove_matching_candidate_stub()

                reloaded = app.store.load_project(app.project.project_dir)
                app._load_project_into_ui(reloaded)
                app._switch_view("Matching Prep")
                handoff = app.matching_prep_handoff.get("1.0", "end").strip()
                self.assertEqual(len(reloaded.matching_candidate_stubs), 1)
                self.assertIn("Remaining candidate after reload.", handoff)
                self.assertNotIn("First candidate removed before reload.", handoff)
            finally:
                root.destroy()

    def test_app_matching_prep_candidate_removal_remains_coherent_when_gated(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = ProjectSliceStore(app.workspace_root)

                with patch("runtime.app.messagebox.showinfo"), patch("runtime.app.messagebox.showerror"):
                    app.project_name_var.set("UI Matching Remove Gated Map")
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
                        )
                    app._load_project_into_ui(project)
                    app.review_status_var.set("ready_for_review")
                    app.save_review_status()
                    app.review_status_var.set("approved")
                    app.save_review_status()

                    app._switch_view("Matching Prep")
                    app.asset_label_var.set("Transcript reference")
                    app.asset_type_var.set("transcript_reference")
                    app.asset_reference_var.set("E:/demo/transcript.txt")
                    app.asset_notes_text.insert("1.0", "Transcript prepared for manual linking.")
                    app.add_matching_prep_asset()

                    app.candidate_block_var.set(app.candidate_block_combo["values"][0])
                    app.candidate_asset_var.set(app.candidate_asset_combo["values"][0])
                    app.candidate_note_var.set("Selected candidate to remove before gate closes.")
                    app.add_matching_candidate_stub()

                    app.candidate_block_var.set(app.candidate_block_combo["values"][1])
                    app.candidate_asset_var.set(app.candidate_asset_combo["values"][0])
                    app.candidate_note_var.set("Tentative candidate remains while gated.")
                    app.add_matching_candidate_stub()

                    app.candidate_stub_var.set(app.candidate_stub_combo["values"][0])
                    app.on_candidate_stub_selected()
                    app.candidate_status_var.set("selected")
                    app.save_matching_candidate_status()
                    app.remove_matching_candidate_stub()

                    target_block_id = app.project.semantic_blocks[1]["record_id"]
                    app._select_block_by_id(target_block_id)
                    app.reorder_selected_block("up")
                    app._switch_view("Matching Prep")

                handoff = app.matching_prep_handoff.get("1.0", "end").strip()
                self.assertIn("Preferred subset readiness: preferred subset not fixed yet", app.matching_candidate_summary_text.get())
                self.assertIn("Tentative candidate remains while gated.", handoff)
                self.assertNotIn("Selected candidate to remove before gate closes.", handoff)
            finally:
                root.destroy()

    def test_app_matching_prep_selected_candidate_rationale_displays_in_handoff(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = ProjectSliceStore(app.workspace_root)

                with patch("runtime.app.messagebox.showinfo"), patch("runtime.app.messagebox.showerror"):
                    app.project_name_var.set("UI Matching Rationale Map")
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
                        )
                    app._load_project_into_ui(project)
                    app.review_status_var.set("ready_for_review")
                    app.save_review_status()
                    app.review_status_var.set("approved")
                    app.save_review_status()

                    app._switch_view("Matching Prep")
                    app.asset_label_var.set("Transcript reference")
                    app.asset_type_var.set("transcript_reference")
                    app.asset_reference_var.set("E:/demo/transcript.txt")
                    app.asset_notes_text.insert("1.0", "Transcript prepared for manual linking.")
                    app.add_matching_prep_asset()

                    app.candidate_block_var.set(app.candidate_block_combo["values"][0])
                    app.candidate_asset_var.set(app.candidate_asset_combo["values"][0])
                    app.candidate_note_var.set("Selected candidate with rationale.")
                    app.add_matching_candidate_stub()

                    app.candidate_stub_var.set(app.candidate_stub_combo["values"][0])
                    app.on_candidate_stub_selected()
                    app.candidate_status_var.set("selected")
                    app.save_matching_candidate_status()
                    app.candidate_rationale_var.set("It best captures the film's opening claim.")
                    app.save_matching_candidate_rationale()

                handoff = app.matching_prep_handoff.get("1.0", "end").strip()
                self.assertIn("Preferred rationale: It best captures the film's opening claim.", handoff)
            finally:
                root.destroy()

    def test_app_matching_prep_selected_candidate_rationale_falls_back_honestly(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = ProjectSliceStore(app.workspace_root)

                with patch("runtime.app.messagebox.showinfo"), patch("runtime.app.messagebox.showerror"):
                    app.project_name_var.set("UI Matching Rationale Fallback Map")
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
                        )
                    app._load_project_into_ui(project)
                    app.review_status_var.set("ready_for_review")
                    app.save_review_status()
                    app.review_status_var.set("approved")
                    app.save_review_status()

                    app._switch_view("Matching Prep")
                    app.asset_label_var.set("Transcript reference")
                    app.asset_type_var.set("transcript_reference")
                    app.asset_reference_var.set("E:/demo/transcript.txt")
                    app.asset_notes_text.insert("1.0", "Transcript prepared for manual linking.")
                    app.add_matching_prep_asset()

                    app.candidate_block_var.set(app.candidate_block_combo["values"][0])
                    app.candidate_asset_var.set(app.candidate_asset_combo["values"][0])
                    app.candidate_note_var.set("Selected candidate without rationale.")
                    app.add_matching_candidate_stub()

                    app.candidate_stub_var.set(app.candidate_stub_combo["values"][0])
                    app.on_candidate_stub_selected()
                    app.candidate_status_var.set("selected")
                    app.save_matching_candidate_status()

                handoff = app.matching_prep_handoff.get("1.0", "end").strip()
                self.assertIn("Preferred rationale: not recorded yet", handoff)
            finally:
                root.destroy()

    def test_app_matching_prep_selected_candidate_rationale_survives_reload(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = ProjectSliceStore(app.workspace_root)

                with patch("runtime.app.messagebox.showinfo"), patch("runtime.app.messagebox.showerror"):
                    app.project_name_var.set("UI Matching Rationale Reload Map")
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
                        )
                    app._load_project_into_ui(project)
                    app.review_status_var.set("ready_for_review")
                    app.save_review_status()
                    app.review_status_var.set("approved")
                    app.save_review_status()

                    app._switch_view("Matching Prep")
                    app.asset_label_var.set("Transcript reference")
                    app.asset_type_var.set("transcript_reference")
                    app.asset_reference_var.set("E:/demo/transcript.txt")
                    app.asset_notes_text.insert("1.0", "Transcript prepared for manual linking.")
                    app.add_matching_prep_asset()

                    app.candidate_block_var.set(app.candidate_block_combo["values"][0])
                    app.candidate_asset_var.set(app.candidate_asset_combo["values"][0])
                    app.candidate_note_var.set("Selected candidate after reload with rationale.")
                    app.add_matching_candidate_stub()

                    app.candidate_stub_var.set(app.candidate_stub_combo["values"][0])
                    app.on_candidate_stub_selected()
                    app.candidate_status_var.set("selected")
                    app.save_matching_candidate_status()
                    app.candidate_rationale_var.set("It keeps the strongest symbolic link.")
                    app.save_matching_candidate_rationale()

                reloaded_project = app.store.load_project(app.project.project_dir)
                app._load_project_into_ui(reloaded_project)
                app._switch_view("Matching Prep")
                handoff = app.matching_prep_handoff.get("1.0", "end").strip()
                self.assertIn("Preferred rationale: It keeps the strongest symbolic link.", handoff)
            finally:
                root.destroy()

    def test_app_matching_prep_selected_candidate_rationale_remains_visible_when_gated(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = ProjectSliceStore(app.workspace_root)

                with patch("runtime.app.messagebox.showinfo"), patch("runtime.app.messagebox.showerror"):
                    app.project_name_var.set("UI Matching Rationale Gated Map")
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
                        )
                    app._load_project_into_ui(project)
                    app.review_status_var.set("ready_for_review")
                    app.save_review_status()
                    app.review_status_var.set("approved")
                    app.save_review_status()

                    app._switch_view("Matching Prep")
                    app.asset_label_var.set("Transcript reference")
                    app.asset_type_var.set("transcript_reference")
                    app.asset_reference_var.set("E:/demo/transcript.txt")
                    app.asset_notes_text.insert("1.0", "Transcript prepared for manual linking.")
                    app.add_matching_prep_asset()

                    app.candidate_block_var.set(app.candidate_block_combo["values"][0])
                    app.candidate_asset_var.set(app.candidate_asset_combo["values"][0])
                    app.candidate_note_var.set("Selected candidate while gated with rationale.")
                    app.add_matching_candidate_stub()

                    app.candidate_stub_var.set(app.candidate_stub_combo["values"][0])
                    app.on_candidate_stub_selected()
                    app.candidate_status_var.set("selected")
                    app.save_matching_candidate_status()
                    app.candidate_rationale_var.set("It is the cleanest current manual proof choice.")
                    app.save_matching_candidate_rationale()

                    target_block_id = app.project.semantic_blocks[1]["record_id"]
                    app._select_block_by_id(target_block_id)
                    app.reorder_selected_block("up")
                    app._switch_view("Matching Prep")

                handoff = app.matching_prep_handoff.get("1.0", "end").strip()
                self.assertIn("Preferred rationale: It is the cleanest current manual proof choice.", handoff)
            finally:
                root.destroy()

    def test_app_matching_prep_selected_readiness_cue_reflects_preferred_subset_exists(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = ProjectSliceStore(app.workspace_root)

                with patch("runtime.app.messagebox.showinfo"), patch("runtime.app.messagebox.showerror"):
                    app.project_name_var.set("UI Matching Selected Readiness Map")
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
                        )
                    app._load_project_into_ui(project)
                    app.review_status_var.set("ready_for_review")
                    app.save_review_status()
                    app.review_status_var.set("approved")
                    app.save_review_status()

                    app._switch_view("Matching Prep")
                    app.asset_label_var.set("Transcript reference")
                    app.asset_type_var.set("transcript_reference")
                    app.asset_reference_var.set("E:/demo/transcript.txt")
                    app.asset_notes_text.insert("1.0", "Transcript prepared for manual linking.")
                    app.add_matching_prep_asset()

                    app.candidate_block_var.set(app.candidate_block_combo["values"][0])
                    app.candidate_asset_var.set(app.candidate_asset_combo["values"][0])
                    app.candidate_note_var.set("Selected candidate creates readiness cue.")
                    app.add_matching_candidate_stub()

                    app.candidate_stub_var.set(app.candidate_stub_combo["values"][0])
                    app.on_candidate_stub_selected()
                    app.candidate_status_var.set("selected")
                    app.save_matching_candidate_status()

                handoff = app.matching_prep_handoff.get("1.0", "end").strip()
                self.assertIn("Preferred subset readiness: preferred subset exists now", app.matching_candidate_summary_text.get())
                self.assertIn("Preferred subset readiness: preferred subset exists now", handoff)
            finally:
                root.destroy()

    def test_app_matching_prep_selected_readiness_cue_reflects_not_fixed_yet(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = ProjectSliceStore(app.workspace_root)

                with patch("runtime.app.messagebox.showinfo"), patch("runtime.app.messagebox.showerror"):
                    app.project_name_var.set("UI Matching No Selected Readiness Map")
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
                        )
                    app._load_project_into_ui(project)
                    app.review_status_var.set("ready_for_review")
                    app.save_review_status()
                    app.review_status_var.set("approved")
                    app.save_review_status()

                    app._switch_view("Matching Prep")
                    app.asset_label_var.set("Main subtitle file")
                    app.asset_type_var.set("subtitle_reference")
                    app.asset_reference_var.set("E:/demo/subtitles.srt")
                    app.asset_notes_text.insert("1.0", "Subtitle reference for manual candidate linking.")
                    app.add_matching_prep_asset()

                    app.candidate_block_var.set(app.candidate_block_combo["values"][0])
                    app.candidate_asset_var.set(app.candidate_asset_combo["values"][0])
                    app.candidate_note_var.set("Tentative candidate only.")
                    app.add_matching_candidate_stub()

                handoff = app.matching_prep_handoff.get("1.0", "end").strip()
                self.assertIn("Preferred subset readiness: preferred subset not fixed yet", app.matching_candidate_summary_text.get())
                self.assertIn("Preferred subset readiness: preferred subset not fixed yet", handoff)
            finally:
                root.destroy()

    def test_app_matching_prep_selected_readiness_cue_survives_reload(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = ProjectSliceStore(app.workspace_root)

                with patch("runtime.app.messagebox.showinfo"), patch("runtime.app.messagebox.showerror"):
                    app.project_name_var.set("UI Matching Readiness Reload Map")
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
                        )
                    app._load_project_into_ui(project)
                    app.review_status_var.set("ready_for_review")
                    app.save_review_status()
                    app.review_status_var.set("approved")
                    app.save_review_status()

                    app._switch_view("Matching Prep")
                    app.asset_label_var.set("Transcript reference")
                    app.asset_type_var.set("transcript_reference")
                    app.asset_reference_var.set("E:/demo/transcript.txt")
                    app.asset_notes_text.insert("1.0", "Transcript prepared for manual linking.")
                    app.add_matching_prep_asset()

                    app.candidate_block_var.set(app.candidate_block_combo["values"][0])
                    app.candidate_asset_var.set(app.candidate_asset_combo["values"][0])
                    app.candidate_note_var.set("Selected candidate after reload for readiness cue.")
                    app.add_matching_candidate_stub()

                    app.candidate_stub_var.set(app.candidate_stub_combo["values"][0])
                    app.on_candidate_stub_selected()
                    app.candidate_status_var.set("selected")
                    app.save_matching_candidate_status()

                reloaded_project = app.store.load_project(app.project.project_dir)
                app._load_project_into_ui(reloaded_project)
                app._switch_view("Matching Prep")
                handoff = app.matching_prep_handoff.get("1.0", "end").strip()
                self.assertIn("Preferred subset readiness: preferred subset exists now", app.matching_candidate_summary_text.get())
                self.assertIn("Preferred subset readiness: preferred subset exists now", handoff)
            finally:
                root.destroy()

    def test_app_matching_prep_selected_readiness_cue_remains_when_gated(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = ProjectSliceStore(app.workspace_root)

                with patch("runtime.app.messagebox.showinfo"), patch("runtime.app.messagebox.showerror"):
                    app.project_name_var.set("UI Matching Readiness Gated Map")
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
                        )
                    app._load_project_into_ui(project)
                    app.review_status_var.set("ready_for_review")
                    app.save_review_status()
                    app.review_status_var.set("approved")
                    app.save_review_status()

                    app._switch_view("Matching Prep")
                    app.asset_label_var.set("Transcript reference")
                    app.asset_type_var.set("transcript_reference")
                    app.asset_reference_var.set("E:/demo/transcript.txt")
                    app.asset_notes_text.insert("1.0", "Transcript prepared for manual linking.")
                    app.add_matching_prep_asset()

                    app.candidate_block_var.set(app.candidate_block_combo["values"][0])
                    app.candidate_asset_var.set(app.candidate_asset_combo["values"][0])
                    app.candidate_note_var.set("Selected candidate keeps readiness cue while gated.")
                    app.add_matching_candidate_stub()

                    app.candidate_stub_var.set(app.candidate_stub_combo["values"][0])
                    app.on_candidate_stub_selected()
                    app.candidate_status_var.set("selected")
                    app.save_matching_candidate_status()

                    target_block_id = app.project.semantic_blocks[1]["record_id"]
                    app._select_block_by_id(target_block_id)
                    app.reorder_selected_block("up")
                    app._switch_view("Matching Prep")

                handoff = app.matching_prep_handoff.get("1.0", "end").strip()
                self.assertIn("Preferred subset readiness: preferred subset exists now", app.matching_candidate_summary_text.get())
                self.assertIn("Preferred subset readiness: preferred subset exists now", handoff)
            finally:
                root.destroy()

    def test_app_matching_prep_selected_candidates_get_dominant_handoff_readability(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = ProjectSliceStore(app.workspace_root)

                with patch("runtime.app.messagebox.showinfo"), patch("runtime.app.messagebox.showerror"):
                    app.project_name_var.set("UI Matching Selected Dominant Map")
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
                        )
                    app._load_project_into_ui(project)
                    app.review_status_var.set("ready_for_review")
                    app.save_review_status()
                    app.review_status_var.set("approved")
                    app.save_review_status()

                    app._switch_view("Matching Prep")
                    app.asset_label_var.set("Transcript reference")
                    app.asset_type_var.set("transcript_reference")
                    app.asset_reference_var.set("E:/demo/transcript.txt")
                    app.asset_notes_text.insert("1.0", "Transcript prepared for manual linking.")
                    app.add_matching_prep_asset()

                    app.candidate_block_var.set(app.candidate_block_combo["values"][0])
                    app.candidate_asset_var.set(app.candidate_asset_combo["values"][0])
                    app.candidate_note_var.set("Tentative candidate for comparison.")
                    app.add_matching_candidate_stub()

                    app.candidate_block_var.set(app.candidate_block_combo["values"][1])
                    app.candidate_asset_var.set(app.candidate_asset_combo["values"][0])
                    app.candidate_note_var.set("Selected candidate should lead handoff.")
                    app.add_matching_candidate_stub()

                    app.candidate_stub_var.set(app.candidate_stub_combo["values"][1])
                    app.on_candidate_stub_selected()
                    app.candidate_status_var.set("selected")
                    app.save_matching_candidate_status()

                handoff = app.matching_prep_handoff.get("1.0", "end").strip()
                self.assertIn("Selected candidates currently preferred for review: 1 present.", app.matching_candidate_summary_text.get())
                self.assertIn("Selected candidates currently preferred for review", handoff)
                self.assertIn("Selected candidate should lead handoff.", handoff)
                self.assertTrue(handoff.index("Selected candidates currently preferred for review") < handoff.index("Manual candidate stubs | focus: all candidate stubs"))
            finally:
                root.destroy()

    def test_app_matching_prep_explicitly_shows_no_selected_candidates_yet(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = ProjectSliceStore(app.workspace_root)

                with patch("runtime.app.messagebox.showinfo"), patch("runtime.app.messagebox.showerror"):
                    app.project_name_var.set("UI Matching No Selected Map")
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
                        )
                    app._load_project_into_ui(project)
                    app.review_status_var.set("ready_for_review")
                    app.save_review_status()
                    app.review_status_var.set("approved")
                    app.save_review_status()

                    app._switch_view("Matching Prep")
                    app.asset_label_var.set("Main subtitle file")
                    app.asset_type_var.set("subtitle_reference")
                    app.asset_reference_var.set("E:/demo/subtitles.srt")
                    app.asset_notes_text.insert("1.0", "Subtitle reference for manual candidate linking.")
                    app.add_matching_prep_asset()

                    app.candidate_block_var.set(app.candidate_block_combo["values"][0])
                    app.candidate_asset_var.set(app.candidate_asset_combo["values"][0])
                    app.candidate_note_var.set("Tentative candidate only.")
                    app.add_matching_candidate_stub()

                handoff = app.matching_prep_handoff.get("1.0", "end").strip()
                self.assertIn("Selected candidates currently preferred for review: none yet.", app.matching_candidate_summary_text.get())
                self.assertIn("Selected candidates currently preferred for review", handoff)
                self.assertIn("- none selected yet", handoff)
            finally:
                root.destroy()

    def test_app_matching_prep_selected_dominant_readability_survives_reload(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = ProjectSliceStore(app.workspace_root)

                with patch("runtime.app.messagebox.showinfo"), patch("runtime.app.messagebox.showerror"):
                    app.project_name_var.set("UI Matching Selected Reload Map")
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
                        )
                    app._load_project_into_ui(project)
                    app.review_status_var.set("ready_for_review")
                    app.save_review_status()
                    app.review_status_var.set("approved")
                    app.save_review_status()

                    app._switch_view("Matching Prep")
                    app.asset_label_var.set("Transcript reference")
                    app.asset_type_var.set("transcript_reference")
                    app.asset_reference_var.set("E:/demo/transcript.txt")
                    app.asset_notes_text.insert("1.0", "Transcript prepared for manual linking.")
                    app.add_matching_prep_asset()

                    app.candidate_block_var.set(app.candidate_block_combo["values"][0])
                    app.candidate_asset_var.set(app.candidate_asset_combo["values"][0])
                    app.candidate_note_var.set("Selected candidate after reload.")
                    app.add_matching_candidate_stub()

                    app.candidate_stub_var.set(app.candidate_stub_combo["values"][0])
                    app.on_candidate_stub_selected()
                    app.candidate_status_var.set("selected")
                    app.save_matching_candidate_status()

                reloaded_project = app.store.load_project(app.project.project_dir)
                app._load_project_into_ui(reloaded_project)
                app._switch_view("Matching Prep")
                handoff = app.matching_prep_handoff.get("1.0", "end").strip()

                self.assertIn("Selected candidates currently preferred for review: 1 present.", app.matching_candidate_summary_text.get())
                self.assertIn("Selected candidate after reload.", handoff)
                self.assertTrue(handoff.index("Selected candidates currently preferred for review") < handoff.index("Manual candidate stubs | focus: all candidate stubs"))
            finally:
                root.destroy()

    def test_app_matching_prep_selected_dominant_readability_remains_when_gated(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = ProjectSliceStore(app.workspace_root)

                with patch("runtime.app.messagebox.showinfo"), patch("runtime.app.messagebox.showerror"):
                    app.project_name_var.set("UI Matching Selected Gated Map")
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
                        )
                    app._load_project_into_ui(project)
                    app.review_status_var.set("ready_for_review")
                    app.save_review_status()
                    app.review_status_var.set("approved")
                    app.save_review_status()

                    app._switch_view("Matching Prep")
                    app.asset_label_var.set("Transcript reference")
                    app.asset_type_var.set("transcript_reference")
                    app.asset_reference_var.set("E:/demo/transcript.txt")
                    app.asset_notes_text.insert("1.0", "Transcript prepared for manual linking.")
                    app.add_matching_prep_asset()

                    app.candidate_block_var.set(app.candidate_block_combo["values"][0])
                    app.candidate_asset_var.set(app.candidate_asset_combo["values"][0])
                    app.candidate_note_var.set("Selected candidate remains dominant while gated.")
                    app.add_matching_candidate_stub()

                    app.candidate_stub_var.set(app.candidate_stub_combo["values"][0])
                    app.on_candidate_stub_selected()
                    app.candidate_status_var.set("selected")
                    app.save_matching_candidate_status()

                    target_block_id = app.project.semantic_blocks[1]["record_id"]
                    app._select_block_by_id(target_block_id)
                    app.reorder_selected_block("up")
                    app._switch_view("Matching Prep")

                handoff = app.matching_prep_handoff.get("1.0", "end").strip()
                self.assertIn("Selected candidates currently preferred for review: 1 present.", app.matching_candidate_summary_text.get())
                self.assertIn("Selected candidate remains dominant while gated.", handoff)
                self.assertIn("Selected candidates currently preferred for review", handoff)
                self.assertTrue(handoff.index("Selected candidates currently preferred for review") < handoff.index("Manual candidate stubs | focus: all candidate stubs"))
            finally:
                root.destroy()

    def test_app_matching_prep_visible_listing_pins_selected_candidates_first(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = ProjectSliceStore(app.workspace_root)

                with patch("runtime.app.messagebox.showinfo"), patch("runtime.app.messagebox.showerror"):
                    app.project_name_var.set("UI Matching Selected First Map")
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
                        )
                    app._load_project_into_ui(project)
                    app.review_status_var.set("ready_for_review")
                    app.save_review_status()
                    app.review_status_var.set("approved")
                    app.save_review_status()

                    app._switch_view("Matching Prep")
                    app.asset_label_var.set("Transcript reference")
                    app.asset_type_var.set("transcript_reference")
                    app.asset_reference_var.set("E:/demo/transcript.txt")
                    app.asset_notes_text.insert("1.0", "Transcript prepared for manual linking.")
                    app.add_matching_prep_asset()

                    app.candidate_block_var.set(app.candidate_block_combo["values"][0])
                    app.candidate_asset_var.set(app.candidate_asset_combo["values"][0])
                    app.candidate_note_var.set("Tentative candidate listed later.")
                    app.add_matching_candidate_stub()

                    app.candidate_block_var.set(app.candidate_block_combo["values"][1])
                    app.candidate_asset_var.set(app.candidate_asset_combo["values"][0])
                    app.candidate_note_var.set("Selected candidate should appear first in listing.")
                    app.add_matching_candidate_stub()

                    app.candidate_block_var.set(app.candidate_block_combo["values"][2])
                    app.candidate_asset_var.set(app.candidate_asset_combo["values"][0])
                    app.candidate_note_var.set("Rejected candidate listed after selected.")
                    app.add_matching_candidate_stub()

                    app.candidate_stub_var.set(app.candidate_stub_combo["values"][1])
                    app.on_candidate_stub_selected()
                    app.candidate_status_var.set("selected")
                    app.save_matching_candidate_status()

                    app.candidate_stub_var.set(app.candidate_stub_combo["values"][2])
                    app.on_candidate_stub_selected()
                    app.candidate_status_var.set("rejected")
                    app.save_matching_candidate_status()

                handoff = app.matching_prep_handoff.get("1.0", "end").strip()
                section = handoff.split("Manual candidate stubs | focus: all candidate stubs", 1)[1]
                self.assertTrue(section.index("Selected candidate should appear first in listing.") < section.index("Tentative candidate listed later."))
                self.assertTrue(section.index("Selected candidate should appear first in listing.") < section.index("Rejected candidate listed after selected."))
            finally:
                root.destroy()

    def test_app_matching_prep_selected_first_visibility_does_not_change_persistence_order(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = ProjectSliceStore(app.workspace_root)

                with patch("runtime.app.messagebox.showinfo"), patch("runtime.app.messagebox.showerror"):
                    app.project_name_var.set("UI Matching Persistence Order Map")
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
                        )
                    app._load_project_into_ui(project)
                    app.review_status_var.set("ready_for_review")
                    app.save_review_status()
                    app.review_status_var.set("approved")
                    app.save_review_status()

                    app._switch_view("Matching Prep")
                    app.asset_label_var.set("Transcript reference")
                    app.asset_type_var.set("transcript_reference")
                    app.asset_reference_var.set("E:/demo/transcript.txt")
                    app.asset_notes_text.insert("1.0", "Transcript prepared for manual linking.")
                    app.add_matching_prep_asset()

                    app.candidate_block_var.set(app.candidate_block_combo["values"][0])
                    app.candidate_asset_var.set(app.candidate_asset_combo["values"][0])
                    app.candidate_note_var.set("First persisted candidate.")
                    app.add_matching_candidate_stub()

                    app.candidate_block_var.set(app.candidate_block_combo["values"][1])
                    app.candidate_asset_var.set(app.candidate_asset_combo["values"][0])
                    app.candidate_note_var.set("Second persisted candidate becomes selected.")
                    app.add_matching_candidate_stub()

                    app.candidate_stub_var.set(app.candidate_stub_combo["values"][1])
                    app.on_candidate_stub_selected()
                    app.candidate_status_var.set("selected")
                    app.save_matching_candidate_status()

                reloaded = app.store.load_project(app.project.project_dir)
                self.assertEqual(reloaded.matching_candidate_stubs[0]["note"], "First persisted candidate.")
                self.assertEqual(reloaded.matching_candidate_stubs[1]["note"], "Second persisted candidate becomes selected.")
            finally:
                root.destroy()

    def test_app_matching_prep_selected_first_visibility_remains_coherent_when_gated(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = ProjectSliceStore(app.workspace_root)

                with patch("runtime.app.messagebox.showinfo"), patch("runtime.app.messagebox.showerror"):
                    app.project_name_var.set("UI Matching Selected First Gated Map")
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
                        )
                    app._load_project_into_ui(project)
                    app.review_status_var.set("ready_for_review")
                    app.save_review_status()
                    app.review_status_var.set("approved")
                    app.save_review_status()

                    app._switch_view("Matching Prep")
                    app.asset_label_var.set("Transcript reference")
                    app.asset_type_var.set("transcript_reference")
                    app.asset_reference_var.set("E:/demo/transcript.txt")
                    app.asset_notes_text.insert("1.0", "Transcript prepared for manual linking.")
                    app.add_matching_prep_asset()

                    app.candidate_block_var.set(app.candidate_block_combo["values"][0])
                    app.candidate_asset_var.set(app.candidate_asset_combo["values"][0])
                    app.candidate_note_var.set("Tentative candidate stays later while gated.")
                    app.add_matching_candidate_stub()

                    app.candidate_block_var.set(app.candidate_block_combo["values"][1])
                    app.candidate_asset_var.set(app.candidate_asset_combo["values"][0])
                    app.candidate_note_var.set("Selected candidate stays first while gated.")
                    app.add_matching_candidate_stub()

                    app.candidate_stub_var.set(app.candidate_stub_combo["values"][1])
                    app.on_candidate_stub_selected()
                    app.candidate_status_var.set("selected")
                    app.save_matching_candidate_status()

                    target_block_id = app.project.semantic_blocks[2]["record_id"]
                    app._select_block_by_id(target_block_id)
                    app.reorder_selected_block("up")
                    app._switch_view("Matching Prep")

                handoff = app.matching_prep_handoff.get("1.0", "end").strip()
                section = handoff.split("Manual candidate stubs | focus: all candidate stubs", 1)[1]
                self.assertTrue(section.index("Selected candidate stays first while gated.") < section.index("Tentative candidate stays later while gated."))
            finally:
                root.destroy()

    def test_app_matching_prep_candidate_status_focus_filters_visible_subset(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = ProjectSliceStore(app.workspace_root)

                with patch("runtime.app.messagebox.showinfo"), patch("runtime.app.messagebox.showerror"):
                    app.project_name_var.set("UI Matching Candidate Focus Map")
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
                        )
                    app._load_project_into_ui(project)
                    app.review_status_var.set("ready_for_review")
                    app.save_review_status()
                    app.review_status_var.set("approved")
                    app.save_review_status()

                    app._switch_view("Matching Prep")
                    app.asset_label_var.set("Main subtitle file")
                    app.asset_type_var.set("subtitle_reference")
                    app.asset_reference_var.set("E:/demo/subtitles.srt")
                    app.asset_notes_text.insert("1.0", "Subtitle reference for manual candidate linking.")
                    app.add_matching_prep_asset()

                    app.asset_label_var.set("Scene stills")
                    app.asset_type_var.set("film_asset_reference")
                    app.asset_reference_var.set("E:/demo/scene-stills")
                    app.asset_notes_text.insert("1.0", "Still-frame folder for manual review.")
                    app.add_matching_prep_asset()

                    app.candidate_block_var.set(app.candidate_block_combo["values"][0])
                    app.candidate_asset_var.set(app.candidate_asset_combo["values"][0])
                    app.candidate_note_var.set("Tentative opening candidate.")
                    app.add_matching_candidate_stub()

                    app.candidate_block_var.set(app.candidate_block_combo["values"][1])
                    app.candidate_asset_var.set(app.candidate_asset_combo["values"][1])
                    app.candidate_note_var.set("Selected semantic-to-asset stub.")
                    app.add_matching_candidate_stub()

                    app.candidate_block_var.set(app.candidate_block_combo["values"][2])
                    app.candidate_asset_var.set(app.candidate_asset_combo["values"][0])
                    app.candidate_note_var.set("Rejected semantic-to-asset stub.")
                    app.add_matching_candidate_stub()

                    app.candidate_stub_var.set(app.candidate_stub_combo["values"][1])
                    app.on_candidate_stub_selected()
                    app.candidate_status_var.set("selected")
                    app.save_matching_candidate_status()

                    app.candidate_stub_var.set(app.candidate_stub_combo["values"][2])
                    app.on_candidate_stub_selected()
                    app.candidate_status_var.set("rejected")
                    app.save_matching_candidate_status()

                    app.candidate_focus_var.set("selected")
                    app.on_candidate_focus_changed()
                    selected_summary = app.matching_candidate_summary_text.get()
                    selected_handoff = app.matching_prep_handoff.get("1.0", "end").strip()

                    app.candidate_focus_var.set("tentative")
                    app.on_candidate_focus_changed()
                    tentative_summary = app.matching_candidate_summary_text.get()
                    tentative_handoff = app.matching_prep_handoff.get("1.0", "end").strip()

                    app.candidate_focus_var.set("rejected")
                    app.on_candidate_focus_changed()
                    rejected_summary = app.matching_candidate_summary_text.get()
                    rejected_handoff = app.matching_prep_handoff.get("1.0", "end").strip()

                    app.candidate_focus_var.set("all")
                    app.on_candidate_focus_changed()
                    all_summary = app.matching_candidate_summary_text.get()
                    all_handoff = app.matching_prep_handoff.get("1.0", "end").strip()

                self.assertIn("focus: selected only", selected_summary)
                self.assertIn("Selected semantic-to-asset stub.", selected_handoff)
                self.assertNotIn("Rejected semantic-to-asset stub.", selected_handoff)
                self.assertNotIn("Tentative opening candidate.", selected_handoff)
                self.assertIn("focus: tentative only", tentative_summary)
                self.assertIn("focus: tentative only", tentative_handoff)
                self.assertIn("Tentative opening candidate.", tentative_handoff)
                self.assertIn("Selected candidates currently preferred for review", tentative_handoff)
                self.assertTrue(tentative_handoff.index("Selected candidates currently preferred for review") < tentative_handoff.index("Manual candidate stubs | focus: tentative only"))
                self.assertIn("focus: rejected only", rejected_summary)
                self.assertIn("focus: rejected only", rejected_handoff)
                self.assertIn("Rejected semantic-to-asset stub.", rejected_handoff)
                self.assertIn("Selected candidates currently preferred for review", rejected_handoff)
                self.assertTrue(rejected_handoff.index("Selected candidates currently preferred for review") < rejected_handoff.index("Manual candidate stubs | focus: rejected only"))
                self.assertIn("focus: all candidate stubs", all_summary)
                self.assertIn("focus: all candidate stubs", all_handoff)
                self.assertIn("Tentative opening candidate.", all_handoff)
                self.assertIn("Selected semantic-to-asset stub.", all_handoff)
                self.assertIn("Rejected semantic-to-asset stub.", all_handoff)
            finally:
                root.destroy()

    def test_app_matching_prep_candidate_focus_remains_coherent_after_reload(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = ProjectSliceStore(app.workspace_root)

                with patch("runtime.app.messagebox.showinfo"), patch("runtime.app.messagebox.showerror"):
                    app.project_name_var.set("UI Matching Candidate Focus Reload Map")
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
                        )
                    app._load_project_into_ui(project)
                    app.review_status_var.set("ready_for_review")
                    app.save_review_status()
                    app.review_status_var.set("approved")
                    app.save_review_status()

                    app._switch_view("Matching Prep")
                    app.asset_label_var.set("Transcript reference")
                    app.asset_type_var.set("transcript_reference")
                    app.asset_reference_var.set("E:/demo/transcript.txt")
                    app.asset_notes_text.insert("1.0", "Transcript prepared for manual linking.")
                    app.add_matching_prep_asset()

                    app.candidate_block_var.set(app.candidate_block_combo["values"][0])
                    app.candidate_asset_var.set(app.candidate_asset_combo["values"][0])
                    app.candidate_note_var.set("Tentative candidate after reload.")
                    app.add_matching_candidate_stub()

                    app.candidate_block_var.set(app.candidate_block_combo["values"][1])
                    app.candidate_asset_var.set(app.candidate_asset_combo["values"][0])
                    app.candidate_note_var.set("Selected candidate after reload.")
                    app.add_matching_candidate_stub()

                    app.candidate_stub_var.set(app.candidate_stub_combo["values"][1])
                    app.on_candidate_stub_selected()
                    app.candidate_status_var.set("selected")
                    app.save_matching_candidate_status()

                reloaded_project = app.store.load_project(app.project.project_dir)
                app._load_project_into_ui(reloaded_project)
                app._switch_view("Matching Prep")
                app.candidate_focus_var.set("selected")
                app.on_candidate_focus_changed()
                handoff = app.matching_prep_handoff.get("1.0", "end").strip()

                self.assertIn("1 visible of 2", app.matching_candidate_summary_text.get())
                self.assertIn("focus: selected only", app.matching_candidate_summary_text.get())
                self.assertIn("Selected candidate after reload.", handoff)
                self.assertNotIn("Tentative candidate after reload.", handoff)
            finally:
                root.destroy()

    def test_app_matching_prep_candidate_stubs_remain_visible_when_lane_reopens(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = ProjectSliceStore(app.workspace_root)

                with patch("runtime.app.messagebox.showinfo"), patch("runtime.app.messagebox.showerror"):
                    app.project_name_var.set("UI Matching Candidate Reopen Map")
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
                        )
                    app._load_project_into_ui(project)
                    app.review_status_var.set("ready_for_review")
                    app.save_review_status()
                    app.review_status_var.set("approved")
                    app.save_review_status()

                    app._switch_view("Matching Prep")
                    app.asset_label_var.set("Transcript reference")
                    app.asset_type_var.set("transcript_reference")
                    app.asset_reference_var.set("E:/demo/transcript.txt")
                    app.asset_notes_text.insert("1.0", "Transcript prepared for manual linking.")
                    app.add_matching_prep_asset()

                    app.candidate_block_var.set(app.candidate_block_combo["values"][0])
                    app.candidate_asset_var.set(app.candidate_asset_combo["values"][0])
                    app.candidate_note_var.set("Candidate visible even if gate reopens.")
                    app.add_matching_candidate_stub()
                    app.candidate_stub_var.set(app.candidate_stub_combo["values"][0])
                    app.on_candidate_stub_selected()
                    app.candidate_status_var.set("selected")
                    app.save_matching_candidate_status()

                    target_block_id = app.project.semantic_blocks[1]["record_id"]
                    app._select_block_by_id(target_block_id)
                    app.reorder_selected_block("up")
                    app._switch_view("Matching Prep")

                handoff = app.matching_prep_handoff.get("1.0", "end").strip()
                app.candidate_focus_var.set("selected")
                app.on_candidate_focus_changed()
                handoff = app.matching_prep_handoff.get("1.0", "end").strip()
                self.assertEqual(app.matching_prep_text.get(), "Matching prep readiness: blocked | semantic approval was reopened after change")
                self.assertIn("1 visible of 1 stored but currently gated", app.matching_candidate_summary_text.get())
                self.assertIn("focus: selected only", app.matching_candidate_summary_text.get())
                self.assertIn("Candidate visible even if gate reopens.", handoff)
                self.assertIn("Review status: selected", handoff)
                self.assertIn("Manual candidate stubs | focus: selected only", handoff)
            finally:
                root.destroy()

    def test_app_matching_prep_shows_registered_inputs_while_semantic_state_is_gated(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = tk.Tk()
            root.withdraw()
            try:
                app = DNAFilmApp(root)
                app.workspace_root = Path(temp_dir)
                app.store = ProjectSliceStore(app.workspace_root)

                with patch("runtime.app.messagebox.showinfo"), patch("runtime.app.messagebox.showerror"):
                    app.project_name_var.set("UI Matching Prep Gated Asset Map")
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
                        )
                    app._load_project_into_ui(project)
                    app.review_status_var.set("ready_for_review")
                    app.save_review_status()
                    app.review_status_var.set("approved")
                    app.save_review_status()

                    app._switch_view("Matching Prep")
                    app.asset_label_var.set("Transcript reference")
                    app.asset_type_var.set("transcript_reference")
                    app.asset_reference_var.set("E:/demo/transcript.txt")
                    app.asset_notes_text.insert("1.0", "Transcript prepared for later semantic-to-scene review.")
                    app.add_matching_prep_asset()

                    target_block_id = app.project.semantic_blocks[1]["record_id"]
                    app._select_block_by_id(target_block_id)
                    app.reorder_selected_block("up")
                    app._switch_view("Matching Prep")

                handoff = app.matching_prep_handoff.get("1.0", "end").strip()
                self.assertEqual(app.matching_prep_text.get(), "Matching prep readiness: blocked | semantic approval was reopened after change")
                self.assertIn("1 prep input(s) registered but currently gated", app.matching_asset_summary_text.get())
                self.assertIn("Transcript reference", handoff)
                self.assertIn("semantic approval was reopened after change", handoff)
            finally:
                root.destroy()

if __name__ == "__main__":
    unittest.main()
