from __future__ import annotations

from runtime.project_slice import (
    ALLOWED_CANDIDATE_REVIEW_STATUSES,
    ALLOWED_OUTPUT_SUITABILITY,
    ALLOWED_SEMANTIC_ROLES,
    ProjectSlice,
    describe_warning_flags,
    semantic_completeness,
    split_sentences,
)
from runtime.domain.workflow_rules import builder_gate, output_artifact_inventory
from runtime.ui.constants import CANDIDATE_STATUS_FOCUS_OPTIONS, FOCUS_TO_SUITABILITY_KEY, ROUGH_CUT_FOCUS_OPTIONS


class DNAFilmAppPresentationMixin:
    def _load_project_into_ui(self, project: ProjectSlice, select_block_id: str | None = None) -> None:
        self.project = project
        self.header_title.set(
            f"{project.project_record['title']} | {project.project_record.get('film_title') or 'Film title optional'} | {project.project_record['language']}"
        )
        self.header_status.set(project.project_record["current_readiness_summary"])
        self.next_action.set(self._next_action_label(project))
        self.review_status_var.set(project.semantic_review_record["review_status"])
        self.review_status_text.set(f"Semantic review: {project.semantic_review_record['review_status']}")
        completeness_label, issue_count, blocks_with_issues = semantic_completeness(project.intake_record, project.semantic_blocks)
        self.completeness_text.set(f"Semantic completeness: {completeness_label}")
        self.issues_summary_text.set(f"Issue visibility: {issue_count} issue(s) across {blocks_with_issues} block(s).")
        readiness = self._approval_readiness(project)
        self.readiness_text.set(f"Approval readiness: {readiness}")
        self.approval_message_text.set(f"Approval message: {project.semantic_review_record.get('approval_transition_message', '')}")
        block_reason = project.semantic_review_record.get("approval_block_reason", "") or "none"
        self.approval_reason_text.set(f"Approval reason: {block_reason}")
        reopen_reason = project.semantic_review_record.get("reopen_reason", "") or "none"
        reopened = "reopened" if project.semantic_review_record.get("reopened_after_change") else "not_reopened"
        self.reopen_text.set(f"Reopen state: {reopened} | reason: {reopen_reason}")
        matching_prep_gate = self._matching_prep_gate_text(project)
        self.matching_prep_text.set(matching_prep_gate)
        scene_matching_gate = self._scene_matching_gate_text(project)
        self.scene_matching_text.set(scene_matching_gate)
        rough_cut_gate = self._rough_cut_gate_text(project)
        self.rough_cut_text.set(rough_cut_gate)
        output_builder_gate = self._output_builder_gate_text(project)
        self.output_builder_status_text.set(output_builder_gate)
        self._update_matching_prep_surface(project)
        self._update_scene_matching_surface(project)
        self._update_rough_cut_surface(project)
        self._update_output_tracks_surface(project)
        self._refresh_matching_candidate_controls(project)
        self._refresh_rough_cut_controls(project)
        self.scene_reference_label_var.set((project.accepted_scene_reference_stub or {}).get("scene_reference_label", ""))
        self.timecode_start_var.set((project.timecode_range_stub or {}).get("start_timecode", ""))
        self.timecode_end_var.set((project.timecode_range_stub or {}).get("end_timecode", ""))
        warnings = project.intake_record.get("intake_warnings", [])
        warning_text = f"Warnings: {', '.join(warnings)}" if warnings else "Warnings: none"
        suitability_summary = self._project_suitability_summary(project)
        self.summary_text.set(
            f"Project status: {project.project_record['project_status']} | Intake: {project.intake_record['intake_readiness']} | Semantic blocks: {len(project.semantic_blocks)} | Review: {project.semantic_review_record['review_status']} | Completeness: {completeness_label} | Readiness: {readiness} | {matching_prep_gate} | {scene_matching_gate} | {rough_cut_gate} | {output_builder_gate} | Suitability: {suitability_summary} | {warning_text}"
        )

        self.analysis_text.delete("1.0", "end")
        analysis_path = project.project_dir / "sources" / "analysis" / "analysis.txt"
        if analysis_path.exists():
            self.analysis_text.insert("1.0", analysis_path.read_text(encoding="utf-8"))

        self._refresh_semantic_list(select_block_id)

    def apply_focus_mode(self, _event: object | None = None) -> None:
        if self.project is None:
            self.focus_status_text.set(f"Focus: {self.focus_mode_var.get()} | showing 0 of 0 blocks.")
            self.focus_position_text.set("Focused item: 0 of 0")
            self.focus_span_text.set("Focus span: no matching blocks")
            self.previous_context_text.set("Previous: No previous semantic block")
            self.next_context_text.set("Next: No next semantic block")
            self._set_focus_navigation_enabled(False, False)
            return
        preferred_block_id = self.selected_block_id
        self._refresh_semantic_list(preferred_block_id)

    def _refresh_semantic_list(self, select_block_id: str | None = None) -> None:
        if self.project is None:
            self.visible_blocks = []
            self.semantic_list.delete(0, "end")
            self.focus_status_text.set(f"Focus: {self.focus_mode_var.get()} | showing 0 of 0 blocks.")
            self.focus_position_text.set("Focused item: 0 of 0")
            self.focus_span_text.set("Focus span: no matching blocks")
            self.previous_context_text.set("Previous: No previous semantic block")
            self.next_context_text.set("Next: No next semantic block")
            self._set_focus_navigation_enabled(False, False)
            return

        self.visible_blocks = self._visible_blocks_for_focus(self.project.semantic_blocks)
        self.semantic_list.delete(0, "end")
        for block in self.visible_blocks:
            preview = block["content"][:56].replace("\n", " ")
            issue_suffix = f" | issues:{len(block.get('warning_flags', []))}" if block.get("warning_flags") else ""
            suitability_suffix = f" | {self._suitability_summary(block)}"
            self.semantic_list.insert("end", f"{block['sequence']:02d}. {block['title']} [{block['semantic_role']}] - {preview}{issue_suffix}{suitability_suffix}")

        focus_mode = self.focus_mode_var.get()
        total_blocks = len(self.project.semantic_blocks)
        shown_blocks = len(self.visible_blocks)
        if shown_blocks:
            self.focus_status_text.set(f"Focus: {focus_mode} | showing {shown_blocks} of {total_blocks} blocks.")
        else:
            self.focus_status_text.set(f"Focus: {focus_mode} | {self._focus_empty_message(focus_mode)}")
        self.focus_span_text.set(self._focus_span_summary())

        if self.visible_blocks:
            preferred_id = select_block_id or self.selected_block_id
            if preferred_id and any(block["record_id"] == preferred_id for block in self.visible_blocks):
                self._select_block_by_id(preferred_id)
            else:
                self._select_block_by_id(self.visible_blocks[0]["record_id"])
        else:
            self.semantic_list.selection_clear(0, "end")
            self.selected_block_id = None
            self.block_status_var.set(self._focus_empty_message(focus_mode))
            self.block_issues_text.set("Block issues: none")
            self.focus_position_text.set("Focused item: 0 of 0")
            self.focus_span_text.set("Focus span: no matching blocks")
            self.previous_context_text.set("Previous: No previous semantic block")
            self.next_context_text.set("Next: No next semantic block")
            self._set_editor_enabled(False)
            self._set_structure_enabled(False, False, False, False, False)
            self._set_focus_navigation_enabled(False, False)
            self._clear_block_editor()

    def _focus_span_summary(self) -> str:
        if not self.visible_blocks:
            return "Focus span: no matching blocks"
        sequences = [block["sequence"] for block in self.visible_blocks]
        count = len(self.visible_blocks)
        if count == 1:
            return f"Focus span: 1 block | seq {sequences[0]:02d}"
        return f"Focus span: {count} blocks | seq {min(sequences):02d}-{max(sequences):02d}"

    def _visible_blocks_for_focus(self, semantic_blocks: list[dict]) -> list[dict]:
        focus_mode = self.focus_mode_var.get()
        return [block for block in semantic_blocks if self._block_matches_focus(block, focus_mode)]

    def _block_matches_focus(self, block: dict, focus_mode: str) -> bool:
        if focus_mode == "All blocks":
            return True
        if focus_mode == "Issues present":
            return bool(block.get("warning_flags"))
        if focus_mode == "Review-ready":
            return not block.get("warning_flags")
        suitability_key = FOCUS_TO_SUITABILITY_KEY.get(focus_mode)
        if suitability_key:
            return block.get("output_suitability", {}).get(suitability_key) == "strong"
        return True

    def _focus_empty_message(self, focus_mode: str) -> str:
        if focus_mode == "Issues present":
            return "No blocks with issues."
        if focus_mode == "Review-ready":
            return "No blocks currently look review-ready."
        if focus_mode in FOCUS_TO_SUITABILITY_KEY:
            return "No blocks currently match this suitability focus."
        return "No semantic blocks match the current focus."

    def _show_block(self, block: dict) -> None:
        self.selected_block_id = block["record_id"]
        self.block_title_var.set(block["title"])
        self.block_role_var.set(block["semantic_role"])
        self.notes_text.delete("1.0", "end")
        self.notes_text.insert("1.0", block.get("notes", ""))
        suitability = block.get("output_suitability", {})
        self.long_video_var.set(suitability.get("long_video", ALLOWED_OUTPUT_SUITABILITY[0]))
        self.shorts_reels_var.set(suitability.get("shorts_reels", ALLOWED_OUTPUT_SUITABILITY[0]))
        self.carousel_var.set(suitability.get("carousel", ALLOWED_OUTPUT_SUITABILITY[0]))
        self.packaging_var.set(suitability.get("packaging", ALLOWED_OUTPUT_SUITABILITY[0]))
        self.content_text.configure(state="normal")
        self.content_text.delete("1.0", "end")
        self.content_text.insert("1.0", block["content"])
        self.content_text.configure(state="disabled")
        sentence_count = len(split_sentences(block["content"]))
        self.split_sentence_var.set("1" if sentence_count > 1 else "0")
        current_index = next((index for index, item in enumerate(self.project.semantic_blocks) if item["record_id"] == block["record_id"]), 0)
        can_move_up = current_index > 0
        can_move_down = current_index < len(self.project.semantic_blocks) - 1
        can_split = sentence_count > 1
        self._set_structure_enabled(can_move_up, can_move_down, can_split, can_move_up, can_move_down)
        reopen_note = self.project.semantic_review_record.get("reopen_reason", "")
        status_suffix = f" | reopen reason: {reopen_note}" if reopen_note else ""
        issue_labels = describe_warning_flags(block.get("warning_flags", []))
        issue_text = ", ".join(issue_labels) if issue_labels else "none"
        self.block_issues_text.set(f"Block issues: {issue_text} | suitability: {self._suitability_summary(block)}")
        self.block_status_var.set(
            f"Editing {block['record_id']} | sequence: {block['sequence']} | review state: {self.project.semantic_review_record['review_status']} | issues: {len(block.get('warning_flags', []))}{status_suffix}"
        )
        self._set_editor_enabled(True)
        self._update_focus_navigation_state()
        self._update_adjacent_context(block)

    def _select_block_by_id(self, block_id: str) -> None:
        if self.project is None:
            return
        for index, block in enumerate(self.visible_blocks):
            if block["record_id"] == block_id:
                self.semantic_list.selection_clear(0, "end")
                self.semantic_list.selection_set(index)
                self.semantic_list.activate(index)
                self._show_block(block)
                return
        self.semantic_list.selection_clear(0, "end")
        self.selected_block_id = None
        self._set_editor_enabled(False)
        self._set_structure_enabled(False, False, False, False, False)
        self._set_focus_navigation_enabled(False, False)
        self.focus_position_text.set("Focused item: 0 of 0")
        self.focus_span_text.set("Focus span: no matching blocks")
        self.previous_context_text.set("Previous: No previous semantic block")
        self.next_context_text.set("Next: No next semantic block")
        self.block_issues_text.set("Block issues: none")

    def _update_adjacent_context(self, block: dict | None) -> None:
        if self.project is None or block is None:
            self.previous_context_text.set("Previous: No previous semantic block")
            self.next_context_text.set("Next: No next semantic block")
            return
        current_index = next((index for index, item in enumerate(self.project.semantic_blocks) if item["record_id"] == block["record_id"]), None)
        if current_index is None:
            self.previous_context_text.set("Previous: No previous semantic block")
            self.next_context_text.set("Next: No next semantic block")
            return
        previous_block = self.project.semantic_blocks[current_index - 1] if current_index > 0 else None
        next_block = self.project.semantic_blocks[current_index + 1] if current_index < len(self.project.semantic_blocks) - 1 else None
        self.previous_context_text.set(self._format_adjacent_context("Previous", previous_block, "No previous semantic block"))
        self.next_context_text.set(self._format_adjacent_context("Next", next_block, "No next semantic block"))

    def _format_adjacent_context(self, label: str, block: dict | None, empty_text: str) -> str:
        if block is None:
            return f"{label}: {empty_text}"
        preview = block["content"][:72].replace("\n", " ").strip()
        return f"{label}: {block['sequence']:02d}. {block['title']} [{block['semantic_role']}] - {preview}"

    def _update_focus_navigation_state(self) -> None:
        total = len(self.visible_blocks)
        if total == 0 or self.selected_block_id is None:
            self.focus_position_text.set("Focused item: 0 of 0")
            self._set_focus_navigation_enabled(False, False)
            return
        current_index = next((index for index, block in enumerate(self.visible_blocks) if block["record_id"] == self.selected_block_id), None)
        if current_index is None:
            self.focus_position_text.set(f"Focused item: 0 of {total}")
            self._set_focus_navigation_enabled(False, False)
            return
        self.focus_position_text.set(f"Focused item: {current_index + 1} of {total}")
        self._set_focus_navigation_enabled(current_index > 0, current_index < total - 1)

    def _set_focus_navigation_enabled(self, can_move_previous: bool, can_move_next: bool) -> None:
        self.previous_focus_button.configure(state="normal" if can_move_previous else "disabled")
        self.next_focus_button.configure(state="normal" if can_move_next else "disabled")

    def _set_matching_candidate_enabled(self, create_enabled: bool, review_enabled: bool, promote_enabled: bool) -> None:
        create_combo_state = "readonly" if create_enabled else "disabled"
        review_combo_state = "readonly" if review_enabled else "disabled"
        self.candidate_block_combo.configure(state=create_combo_state)
        self.candidate_asset_combo.configure(state=create_combo_state)
        self.add_candidate_button.configure(state="normal" if create_enabled else "disabled")
        self.candidate_stub_combo.configure(state=review_combo_state)
        self.candidate_status_combo.configure(state=review_combo_state)
        self.save_candidate_status_button.configure(state="normal" if review_enabled else "disabled")
        self.remove_candidate_button.configure(state="normal" if review_enabled else "disabled")
        self.promote_accepted_reference_button.configure(state="normal" if promote_enabled else "disabled")

    def _set_scene_matching_enabled(self, enabled: bool) -> None:
        entry_state = "normal" if enabled else "disabled"
        button_state = "normal" if enabled else "disabled"
        self.scene_reference_label_entry.configure(state=entry_state)
        self.save_scene_reference_button.configure(state=button_state)
        self.timecode_start_entry.configure(state=entry_state)
        self.timecode_end_entry.configure(state=entry_state)
        self.save_timecode_button.configure(state=button_state)

    def _set_rough_cut_enabled(self, enabled: bool) -> None:
        entry_state = "normal" if enabled else "disabled"
        button_state = "normal" if enabled else "disabled"
        combo_state = "readonly" if enabled and self.rough_cut_segment_combo.cget("values") else "disabled"
        self.rough_cut_segment_label_entry.configure(state=entry_state)
        self.save_rough_cut_segment_button.configure(state=button_state)
        self.rough_cut_segment_combo.configure(state=combo_state)
        if not enabled:
            self.rough_cut_move_up_button.configure(state="disabled")
            self.rough_cut_move_down_button.configure(state="disabled")
            self.include_rough_cut_subset_button.configure(state="disabled")
            self.remove_rough_cut_subset_button.configure(state="disabled")
            self.remove_rough_cut_segment_button.configure(state="disabled")

    def _set_output_builder_enabled(self, enabled: bool) -> None:
        self.build_packaging_bundle_button.configure(state="normal" if enabled else "disabled")
        self.build_shorts_reels_button.configure(state="normal" if enabled else "disabled")
        self.build_long_video_button.configure(state="normal" if enabled else "disabled")
        self.build_carousel_button.configure(state="normal" if enabled else "disabled")

    def _set_editor_enabled(self, enabled: bool) -> None:
        entry_state = "normal" if enabled else "disabled"
        combo_state = "readonly" if enabled else "disabled"
        text_state = "normal" if enabled else "disabled"
        button_state = "normal" if enabled else "disabled"
        self.block_title_entry.configure(state=entry_state)
        self.block_role_combo.configure(state=combo_state)
        self.notes_text.configure(state=text_state)
        self.long_video_combo.configure(state=combo_state)
        self.shorts_reels_combo.configure(state=combo_state)
        self.carousel_combo.configure(state=combo_state)
        self.packaging_combo.configure(state=combo_state)
        self.save_block_button.configure(state=button_state)

    def _set_structure_enabled(
        self,
        can_move_up: bool,
        can_move_down: bool,
        can_split: bool,
        can_merge_up: bool,
        can_merge_down: bool,
    ) -> None:
        self.move_up_button.configure(state="normal" if can_move_up else "disabled")
        self.move_down_button.configure(state="normal" if can_move_down else "disabled")
        self.merge_up_button.configure(state="normal" if can_merge_up else "disabled")
        self.merge_down_button.configure(state="normal" if can_merge_down else "disabled")
        self.split_sentence_entry.configure(state="normal" if can_split else "disabled")
        self.split_button.configure(state="normal" if can_split else "disabled")

    def _clear_block_editor(self) -> None:
        self.block_title_var.set("")
        self.block_role_var.set(ALLOWED_SEMANTIC_ROLES[0])
        self.split_sentence_var.set("1")
        self.long_video_var.set(ALLOWED_OUTPUT_SUITABILITY[0])
        self.shorts_reels_var.set(ALLOWED_OUTPUT_SUITABILITY[0])
        self.carousel_var.set(ALLOWED_OUTPUT_SUITABILITY[0])
        self.packaging_var.set(ALLOWED_OUTPUT_SUITABILITY[0])
        self.notes_text.configure(state="normal")
        self.notes_text.delete("1.0", "end")
        self.notes_text.configure(state="disabled")
        self.block_issues_text.set("Block issues: none")
        self.focus_span_text.set("Focus span: no matching blocks")
        self.previous_context_text.set("Previous: No previous semantic block")
        self.next_context_text.set("Next: No next semantic block")
        self.content_text.configure(state="normal")
        self.content_text.delete("1.0", "end")
        self.content_text.insert("1.0", "Select a semantic block to inspect it here.")
        self.content_text.configure(state="disabled")

    def _approval_readiness(self, project: ProjectSlice) -> str:
        if project.intake_record["intake_readiness"] != "ready" or not project.semantic_blocks:
            return "not_ready"
        review_status = project.semantic_review_record["review_status"]
        if review_status == "approved":
            return "approved"
        if review_status == "ready_for_review":
            return "ready_for_approval"
        if project.semantic_review_record.get("reopened_after_change"):
            return "reopened_after_change"
        completeness_label, _, _ = semantic_completeness(project.intake_record, project.semantic_blocks)
        return {
            "Incomplete": "premature",
            "Needs tightening": "mixed",
            "Plausibly ready for review": "plausibly_reasonable",
        }.get(completeness_label, "plausibly_reasonable")

    def _matching_prep_gate(self, project: ProjectSlice) -> tuple[str, str]:
        if project.intake_record["intake_readiness"] != "ready":
            return ("blocked", "semantic map not established yet")
        if not project.semantic_blocks:
            return ("blocked", "semantic map has no blocks yet")
        if project.semantic_review_record.get("reopened_after_change"):
            return ("blocked", "semantic approval was reopened after change")

        completeness_label, issue_count, _ = semantic_completeness(project.intake_record, project.semantic_blocks)
        review_status = project.semantic_review_record["review_status"]

        if review_status == "approved":
            return ("ready", "semantic map approved")
        if completeness_label == "Incomplete":
            return ("blocked", "semantic issues remain")
        if completeness_label == "Needs tightening":
            return ("conditionally plausible", "semantic map is mixed and should be tightened")
        if review_status == "under_edit":
            return ("blocked", "semantic map is still under edit")
        if review_status == "ready_for_review":
            if issue_count:
                return ("conditionally plausible", "semantic review is staged but issues remain visible")
            return ("conditionally plausible", "semantic review is staged but approval is still pending")
        return ("conditionally plausible", "semantic review looks plausibly ready but is not yet approved")

    def _matching_prep_gate_text(self, project: ProjectSlice) -> str:
        state, reason = self._matching_prep_gate(project)
        return f"Matching prep readiness: {state} | {reason}"

    def _scene_matching_gate(self, project: ProjectSlice) -> tuple[str, str]:
        if project.accepted_reference is None:
            return ("blocked", "no accepted reference available yet")
        if project.semantic_review_record.get("reopened_after_change"):
            return ("blocked", "accepted reference remains visible but upstream semantic approval was reopened")
        return ("ready", "current accepted reference available for scene-matching-facing handoff")

    def _scene_matching_gate_text(self, project: ProjectSlice) -> str:
        state, reason = self._scene_matching_gate(project)
        return f"Scene matching readiness: {state} | {reason}"

    def _rough_cut_gate(self, project: ProjectSlice) -> tuple[str, str]:
        if project.accepted_reference is None:
            return ("blocked", "no accepted reference available yet")
        if project.accepted_scene_reference_stub is None:
            return ("blocked", "no accepted scene reference stub available yet")
        if project.timecode_range_stub is None:
            return ("blocked", "no timecode range stub available yet")
        if project.semantic_review_record.get("reopened_after_change"):
            return ("blocked", "rough-cut handoff remains visible but upstream semantic approval was reopened")
        return ("ready", "current downstream handoff chain available for first assembly-facing stub work")

    def _rough_cut_gate_text(self, project: ProjectSlice) -> str:
        state, reason = self._rough_cut_gate(project)
        return f"Rough cut readiness: {state} | {reason}"

    def _output_builder_gate(self, project: ProjectSlice) -> tuple[str, str]:
        return builder_gate(project)

    def _output_builder_gate_text(self, project: ProjectSlice) -> str:
        state, reason = self._output_builder_gate(project)
        return f"Output builder readiness: {state} | {reason}"

    def _output_inventory(self, project: ProjectSlice) -> dict:
        return output_artifact_inventory(
            project.packaging_script_bundle,
            project.shorts_reels_script,
            project.long_video_script,
            project.carousel_script,
        )

    def _output_inventory_text(self, project: ProjectSlice) -> str:
        inventory = self._output_inventory(project)
        built_count = inventory["built_count"]
        total_slots = inventory["total_slots"]
        if not built_count:
            missing_text = ", ".join(inventory["missing_labels"])
            return f"Output inventory: 0 of {total_slots} artifacts built. Missing: {missing_text}."
        if inventory["runtime_state"] == "all_built":
            built_text = ", ".join(inventory["built_labels"])
            return f"Output inventory: all {total_slots} artifacts built and currently available. Built: {built_text}."
        built_text = ", ".join(inventory["built_labels"])
        missing_text = ", ".join(inventory["missing_labels"])
        return f"Output inventory: {built_count} of {total_slots} artifacts built. Built: {built_text}. Missing: {missing_text}."

    def _output_recovery_text(self, project: ProjectSlice, gate_state: str, gate_reason: str) -> str:
        inventory = self._output_inventory(project)
        if gate_state != "ready":
            if project.semantic_review_record.get("reopened_after_change"):
                return "Output trust: upstream semantic approval was reopened, so downstream rough-cut and output artifacts were cleared and must be rebuilt from the refreshed chain."
            return f"Output trust: no current output artifact can be treated as ready because {gate_reason}."
        if inventory["runtime_state"] == "none_built":
            return "Output trust: the downstream chain is current and ready for the first builder run."
        if inventory["runtime_state"] == "all_built":
            return "Output trust: all four artifacts are current, reload-safe, and ready for repeated local review or rebuild."
        return "Output trust: built artifacts remain current and reload-safe, while missing artifacts can be added without rebuilding the ones already present."

    def _output_paths_text(self, project: ProjectSlice) -> str:
        entries = [
            ("Packaging", project.packaging_script_bundle),
            ("Shorts/Reels", project.shorts_reels_script),
            ("Long Video", project.long_video_script),
            ("Carousel", project.carousel_script),
        ]
        built_paths = [
            f"{label}: {artifact.get('artifact_relative_path', 'none')}"
            for label, artifact in entries
            if artifact is not None
        ]
        if not built_paths:
            return "Built artifact paths: none yet."
        return "Built artifact paths: " + " | ".join(built_paths)

    def _builder_slot_status_lines(self, label: str, artifact: dict | None, empty_text: str) -> list[str]:
        if artifact is None:
            return [f"- {label}: not built yet", f"  State: {empty_text}", ""]
        return [
            f"- {label}: built and current",
            f"  Path: {artifact.get('artifact_relative_path', 'none')}",
            f"  Source focus: {artifact.get('source_focus_mode', 'all_saved_segments')}",
            "",
        ]

    def _refresh_rough_cut_controls(self, project: ProjectSlice | None) -> None:
        if project is None:
            self.rough_cut_segment_options = {}
            self.rough_cut_segment_combo.configure(values=())
            self.rough_cut_segment_var.set("")
            self.rough_cut_segment_label_var.set("")
            self.include_rough_cut_subset_button.configure(state="disabled")
            self.remove_rough_cut_subset_button.configure(state="disabled")
            self.remove_rough_cut_segment_button.configure(state="disabled")
            return
        current_display = self.rough_cut_segment_var.get()
        visible_entries = self._visible_rough_cut_segments(project)
        self.rough_cut_segment_options = {
            self._rough_cut_segment_option_label(entry): entry["record_id"]
            for entry in visible_entries
        }
        values = tuple(self.rough_cut_segment_options.keys())
        self.rough_cut_segment_combo.configure(values=values)
        selected_display = current_display if current_display in self.rough_cut_segment_options else (values[0] if values else "")
        self.rough_cut_segment_var.set(selected_display)
        selected_entry = next((entry for entry in visible_entries if self._rough_cut_segment_option_label(entry) == selected_display), None)
        if selected_entry is not None:
            self.rough_cut_segment_label_var.set(selected_entry.get("segment_label", ""))
        elif not self.rough_cut_segment_label_var.get().strip():
            self.rough_cut_segment_label_var.set("")
        gate_state, _ = self._rough_cut_gate(project)
        combo_state = "readonly" if gate_state == "ready" and values else "disabled"
        self.rough_cut_segment_combo.configure(state=combo_state)
        selected_index = values.index(selected_display) if selected_display in values else -1
        reorder_allowed = self._rough_cut_focus_label() == "all saved segments"
        move_enabled = gate_state == "ready" and selected_index >= 0 and reorder_allowed
        self.rough_cut_move_up_button.configure(state="normal" if move_enabled and selected_index > 0 else "disabled")
        self.rough_cut_move_down_button.configure(state="normal" if move_enabled and 0 <= selected_index < len(values) - 1 else "disabled")
        selected_subset_status = (selected_entry or {}).get("subset_status", "saved_only")
        subset_enabled = gate_state == "ready" and selected_entry is not None
        self.include_rough_cut_subset_button.configure(
            state="normal" if subset_enabled and selected_subset_status != "selected_for_current_rough_cut" else "disabled"
        )
        self.remove_rough_cut_subset_button.configure(
            state="normal" if subset_enabled and selected_subset_status == "selected_for_current_rough_cut" else "disabled"
        )
        self.remove_rough_cut_segment_button.configure(
            state="normal" if subset_enabled else "disabled"
        )

    def _visible_rough_cut_segments(self, project: ProjectSlice) -> list[dict]:
        focus = self.rough_cut_focus_var.get() if self.rough_cut_focus_var.get() in ROUGH_CUT_FOCUS_OPTIONS else ROUGH_CUT_FOCUS_OPTIONS[0]
        if focus == "show_preferred_subset_only":
            return self._preferred_rough_cut_segments(project)
        return list(project.rough_cut_segment_stubs)

    def _rough_cut_focus_label(self) -> str:
        focus = self.rough_cut_focus_var.get() if self.rough_cut_focus_var.get() in ROUGH_CUT_FOCUS_OPTIONS else ROUGH_CUT_FOCUS_OPTIONS[0]
        if focus == "show_preferred_subset_only":
            return "preferred subset only"
        return "all saved segments"

    def _rough_cut_reorder_guidance(self) -> str:
        if self._rough_cut_focus_label() == "preferred subset only":
            return "Reorder is available only in all-saved focus because saved order belongs to the full rough-cut set."
        return "Reorder applies to the full saved rough-cut order."

    def _rough_cut_focus_summary(self, project: ProjectSlice) -> str:
        visible_count = len(self._visible_rough_cut_segments(project))
        saved_total = len(project.rough_cut_segment_stubs)
        preferred_total = len(self._preferred_rough_cut_segments(project))
        return f"Focus: {self._rough_cut_focus_label()} | Visible: {visible_count} | Saved total: {saved_total} | Preferred total: {preferred_total}"

    def _rough_cut_segment_option_label(self, entry: dict) -> str:
        return f"{entry.get('sequence', 0):02d}. {entry.get('segment_label', 'Untitled segment')} [{entry.get('record_id', 'unknown')}]"

    def _select_rough_cut_segment_by_id(self, segment_id: str | None) -> None:
        if not segment_id or self.project is None:
            return
        display = next((label for label, record_id in self.rough_cut_segment_options.items() if record_id == segment_id), "")
        if display:
            self.rough_cut_segment_var.set(display)
            self._refresh_rough_cut_controls(self.project)
            self._update_rough_cut_surface(self.project)

    def _refresh_matching_candidate_controls(self, project: ProjectSlice | None) -> None:
        if project is None:
            self.candidate_block_options = {}
            self.candidate_asset_options = {}
            self.candidate_stub_options = {}
            self.candidate_block_combo.configure(values=())
            self.candidate_asset_combo.configure(values=())
            self.candidate_stub_combo.configure(values=())
            self.candidate_block_var.set("")
            self.candidate_asset_var.set("")
            self.candidate_stub_var.set("")
            self.candidate_status_var.set(ALLOWED_CANDIDATE_REVIEW_STATUSES[0])
            self.candidate_rationale_var.set("")
            self.candidate_focus_var.set(CANDIDATE_STATUS_FOCUS_OPTIONS[0])
            self._set_matching_candidate_enabled(False, False, False)
            return

        current_block_display = self.candidate_block_var.get()
        current_asset_display = self.candidate_asset_var.get()
        current_stub_display = self.candidate_stub_var.get()
        self.candidate_block_options = {
            self._candidate_block_option_label(block): block["record_id"]
            for block in project.semantic_blocks
        }
        self.candidate_asset_options = {
            self._candidate_asset_option_label(entry): entry["record_id"]
            for entry in project.matching_prep_assets
        }
        self.candidate_stub_options = {
            self._candidate_stub_option_label(project, entry): entry["record_id"]
            for entry in project.matching_candidate_stubs
        }
        block_values = tuple(self.candidate_block_options.keys())
        asset_values = tuple(self.candidate_asset_options.keys())
        stub_values = tuple(self.candidate_stub_options.keys())
        self.candidate_block_combo.configure(values=block_values)
        self.candidate_asset_combo.configure(values=asset_values)
        self.candidate_stub_combo.configure(values=stub_values)
        self.candidate_focus_combo.configure(values=CANDIDATE_STATUS_FOCUS_OPTIONS)
        self.candidate_block_var.set(current_block_display if current_block_display in self.candidate_block_options else (block_values[0] if block_values else ""))
        self.candidate_asset_var.set(current_asset_display if current_asset_display in self.candidate_asset_options else (asset_values[0] if asset_values else ""))
        selected_stub_display = current_stub_display if current_stub_display in self.candidate_stub_options else (stub_values[0] if stub_values else "")
        self.candidate_stub_var.set(selected_stub_display)
        selected_stub = next((entry for entry in project.matching_candidate_stubs if self._candidate_stub_option_label(project, entry) == selected_stub_display), None)
        self.candidate_status_var.set((selected_stub or {}).get("review_status", ALLOWED_CANDIDATE_REVIEW_STATUSES[0]))
        self.candidate_rationale_var.set((selected_stub or {}).get("preferred_rationale", ""))
        gate_state, _ = self._matching_prep_gate(project)
        can_create = gate_state == "ready" and bool(block_values) and bool(asset_values)
        can_review = gate_state == "ready" and bool(stub_values)
        can_promote = gate_state == "ready" and (selected_stub or {}).get("review_status", ALLOWED_CANDIDATE_REVIEW_STATUSES[0]) == "selected"
        self._set_matching_candidate_enabled(can_create, can_review, can_promote)

    def _candidate_block_option_label(self, block: dict) -> str:
        return f"{block['sequence']:02d}. {block['title']} [{block['record_id']}]"

    def _candidate_asset_option_label(self, entry: dict) -> str:
        return f"{entry['asset_label']} [{entry['asset_type']}] ({entry['record_id']})"

    def _candidate_stub_option_label(self, project: ProjectSlice, entry: dict) -> str:
        block_lookup = {block['record_id']: block for block in project.semantic_blocks}
        block = block_lookup.get(entry.get("semantic_block_id"))
        block_label = f"{block['sequence']:02d}. {block['title']}" if block else entry.get("semantic_block_id", "unknown semantic block")
        review_status = entry.get("review_status", ALLOWED_CANDIDATE_REVIEW_STATUSES[0])
        return f"{block_label} [{entry['record_id']}] ({review_status})"

    def _candidate_status_summary(self, project: ProjectSlice) -> str:
        if not project.matching_candidate_stubs:
            return "none yet"
        counts = {status: 0 for status in ALLOWED_CANDIDATE_REVIEW_STATUSES}
        for entry in project.matching_candidate_stubs:
            counts[entry.get("review_status", ALLOWED_CANDIDATE_REVIEW_STATUSES[0])] += 1
        return ", ".join(f"{status} {counts[status]}" for status in ALLOWED_CANDIDATE_REVIEW_STATUSES if counts[status])

    def _accepted_reference_source_candidate(self, project: ProjectSlice) -> dict | None:
        accepted_reference = project.accepted_reference
        if accepted_reference is None:
            return None
        source_candidate_stub_id = accepted_reference.get("source_candidate_stub_id", "").strip()
        if not source_candidate_stub_id:
            return None
        return next((entry for entry in project.matching_candidate_stubs if entry.get("record_id") == source_candidate_stub_id), None)

    def _accepted_reference_summary(self, project: ProjectSlice) -> str:
        if project.accepted_reference is None:
            return "Accepted reference: none accepted yet for later matching work."
        return "Accepted reference: current accepted reference exists for later matching work."

    def _accepted_scene_reference_stub_summary(self, project: ProjectSlice) -> str:
        if project.accepted_scene_reference_stub is None:
            return "Accepted scene reference stub: none created yet."
        return "Accepted scene reference stub: current scene-side artifact exists for later timecode prep."

    def _timecode_range_stub_summary(self, project: ProjectSlice) -> str:
        if project.timecode_range_stub is None:
            return "Timecode range stub: none saved yet."
        return "Timecode range stub: current provisional temporal artifact exists for later assembly work."

    def _rough_cut_segment_stub_summary(self, project: ProjectSlice) -> str:
        segment_count = len(project.rough_cut_segment_stubs)
        preferred_count = len(self._preferred_rough_cut_segments(project))
        if not segment_count:
            return "Rough-cut segment set: none saved yet."
        if preferred_count:
            return f"Rough-cut segment set: {segment_count} assembly-facing segment stub(s) saved in current order | Preferred current rough cut: {preferred_count} segment(s) currently selected for later assembly."
        return f"Rough-cut segment set: {segment_count} assembly-facing segment stub(s) saved in current order | Preferred current rough cut: none selected yet."

    def _preferred_rough_cut_segments(self, project: ProjectSlice) -> list[dict]:
        return [
            entry
            for entry in project.rough_cut_segment_stubs
            if entry.get("subset_status", "saved_only") == "selected_for_current_rough_cut"
        ]

    def _rough_cut_preferred_subset_summary(self, project: ProjectSlice) -> str:
        preferred_count = len(self._preferred_rough_cut_segments(project))
        if preferred_count:
            return f"Preferred current rough cut: {preferred_count} segment(s) currently selected for later assembly."
        return "Preferred current rough cut: none selected yet."

    def _packaging_script_bundle_summary(self, project: ProjectSlice) -> str:
        bundle = project.packaging_script_bundle
        if bundle is None:
            return "Packaging-ready script bundle: none built yet."
        return (
            f"Packaging-ready script bundle: {bundle.get('segment_count', 0)} segment(s) built from "
            f"{bundle.get('source_focus_mode', 'all_saved_segments')}."
        )

    def _packaging_script_bundle_lines(self, project: ProjectSlice) -> list[str]:
        bundle = project.packaging_script_bundle
        if bundle is None:
            return ["No packaging-ready script bundle has been built yet."]
        return [bundle.get("markdown_content", "").rstrip() or "No packaging-ready script bundle content available."]

    def _shorts_reels_script_summary(self, project: ProjectSlice) -> str:
        script = project.shorts_reels_script
        if script is None:
            return "Shorts/Reels script: none built yet."
        return (
            f"Shorts/Reels script: {script.get('segment_count', 0)} beat(s) built from "
            f"{script.get('source_focus_mode', 'all_saved_segments')} with hook '{script.get('hook_line', '').strip() or 'none'}'."
        )

    def _shorts_reels_script_lines(self, project: ProjectSlice) -> list[str]:
        script = project.shorts_reels_script
        if script is None:
            return ["No Shorts/Reels script has been built yet."]
        return [script.get("markdown_content", "").rstrip() or "No Shorts/Reels script content available."]

    def _long_video_script_summary(self, project: ProjectSlice) -> str:
        script = project.long_video_script
        if script is None:
            return "Long-video script: none built yet."
        return (
            f"Long-video script: {script.get('segment_count', 0)} beat(s) built from "
            f"{script.get('source_focus_mode', 'all_saved_segments')} with working title '{script.get('working_title', '').strip() or 'none'}'."
        )

    def _long_video_script_lines(self, project: ProjectSlice) -> list[str]:
        script = project.long_video_script
        if script is None:
            return ["No long-video script has been built yet."]
        return [script.get("markdown_content", "").rstrip() or "No long-video script content available."]

    def _carousel_script_summary(self, project: ProjectSlice) -> str:
        script = project.carousel_script
        if script is None:
            return "Carousel script: none built yet."
        return (
            f"Carousel script: {script.get('slide_count', 0)} slide(s) built from "
            f"{script.get('source_focus_mode', 'all_saved_segments')} with angle '{script.get('carousel_angle', '').strip() or 'none'}'."
        )

    def _carousel_script_lines(self, project: ProjectSlice) -> list[str]:
        script = project.carousel_script
        if script is None:
            return ["No carousel script has been built yet."]
        return [script.get("markdown_content", "").rstrip() or "No carousel script content available."]

    def _accepted_reference_lines(self, project: ProjectSlice) -> list[str]:
        accepted_reference = project.accepted_reference
        if accepted_reference is None:
            return ["- none accepted yet", ""]
        source_candidate = self._accepted_reference_source_candidate(project)
        block_lookup = {block['record_id']: block for block in project.semantic_blocks}
        asset_lookup = {asset['record_id']: asset for asset in project.matching_prep_assets}
        block = block_lookup.get(accepted_reference.get("semantic_block_id"))
        asset = asset_lookup.get(accepted_reference.get("prep_asset_id"))
        block_label = f"{block['sequence']:02d}. {block['title']}" if block else accepted_reference.get("semantic_block_id", "unknown semantic block")
        asset_label = f"{asset['asset_label']} [{asset['asset_type']}]" if asset else accepted_reference.get("prep_asset_id", "unknown prep input")
        note = (source_candidate or {}).get("note", "").strip() or "none"
        rationale = (source_candidate or {}).get("preferred_rationale", "").strip() or "not recorded yet"
        source_candidate_stub_id = accepted_reference.get("source_candidate_stub_id", "unknown candidate stub")
        return [
            "",
            f"- {block_label} -> {asset_label}",
            f"  Accepted from selected candidate stub: {source_candidate_stub_id}",
            "  Acceptance scope: current accepted prep reference for later matching work only, not a timecoded final match.",
            f"  Preferred rationale: {rationale}",
            f"  Note: {note}",
            f"  Accepted reference id: {accepted_reference.get('record_id', 'accepted-reference-current')}",
            "",
        ]

    def _accepted_scene_reference_stub_lines(self, project: ProjectSlice) -> list[str]:
        accepted_scene_reference_stub = project.accepted_scene_reference_stub
        if accepted_scene_reference_stub is None:
            return ["- none created yet", ""]
        accepted_reference = project.accepted_reference or {}
        source_candidate = self._accepted_reference_source_candidate(project)
        block_lookup = {block['record_id']: block for block in project.semantic_blocks}
        asset_lookup = {asset['record_id']: asset for asset in project.matching_prep_assets}
        block = block_lookup.get(accepted_scene_reference_stub.get("semantic_block_id"))
        asset = asset_lookup.get(accepted_scene_reference_stub.get("prep_asset_id"))
        block_label = f"{block['sequence']:02d}. {block['title']}" if block else accepted_scene_reference_stub.get("semantic_block_id", "unknown semantic block")
        asset_label = f"{asset['asset_label']} [{asset['asset_type']}]" if asset else accepted_scene_reference_stub.get("prep_asset_id", "unknown prep input")
        rationale = (source_candidate or {}).get("preferred_rationale", "").strip() or "not recorded yet"
        note = (source_candidate or {}).get("note", "").strip() or "none"
        return [
            "",
            f"- Scene-side label: {accepted_scene_reference_stub.get('scene_reference_label', 'none')}",
            f"  Semantic block: {block_label}",
            f"  Prep input: {asset_label}",
            f"  Source accepted prep reference: {accepted_reference.get('record_id', 'accepted-reference-current')}",
            "  Scene-side scope: current accepted scene reference stub for later timecode prep only, not automatic matching or final output.",
            f"  Upstream preferred rationale: {rationale}",
            f"  Upstream note: {note}",
            f"  Accepted scene reference stub id: {accepted_scene_reference_stub.get('record_id', 'accepted-scene-reference-current')}",
            "",
        ]

    def _timecode_range_stub_lines(self, project: ProjectSlice) -> list[str]:
        timecode_range_stub = project.timecode_range_stub
        if timecode_range_stub is None:
            return ["- none saved yet", ""]
        accepted_scene_reference_stub = project.accepted_scene_reference_stub or {}
        scene_label = accepted_scene_reference_stub.get("scene_reference_label", "none")
        return [
            "",
            f"- Start: {timecode_range_stub.get('start_timecode', 'none')}",
            f"  End: {timecode_range_stub.get('end_timecode', 'none')}",
            f"  Scene-side source: {scene_label}",
            "  Temporal scope: provisional timecode range stub for later assembly only, not transcript-aligned timing or final edit output.",
            f"  Timecode range stub id: {timecode_range_stub.get('record_id', 'timecode-range-current')}",
            "",
        ]

    def _rough_cut_segment_stub_lines(self, project: ProjectSlice) -> list[str]:
        visible_entries = self._visible_rough_cut_segments(project)
        if not project.rough_cut_segment_stubs:
            return ["- none saved yet", ""]
        if not visible_entries:
            return [f"- none in current focus ({self._rough_cut_focus_label()})", ""]
        selected_segment_id = self.rough_cut_segment_options.get(self.rough_cut_segment_var.get(), "")
        lines: list[str] = [""]
        for entry in visible_entries:
            selected_marker = " | selected" if entry.get("record_id") == selected_segment_id else ""
            subset_marker = " | in current preferred rough cut" if entry.get("subset_status", "saved_only") == "selected_for_current_rough_cut" else ""
            lines.extend([
                f"- {entry.get('sequence', 0):02d}. {entry.get('segment_label', 'none')}{selected_marker}{subset_marker}",
                f"  Start: {entry.get('start_timecode', 'none')}",
                f"  End: {entry.get('end_timecode', 'none')}",
                f"  Rough-cut segment stub id: {entry.get('record_id', 'unknown')}",
                "  Assembly scope: provisional rough-cut segment stub for later assembly only, not a real cut or render-ready output.",
                "",
            ])
        return lines

    def _preferred_rough_cut_segment_lines(self, project: ProjectSlice) -> list[str]:
        preferred_entries = self._preferred_rough_cut_segments(project)
        if not preferred_entries:
            return ["- none selected yet", ""]
        selected_segment_id = self.rough_cut_segment_options.get(self.rough_cut_segment_var.get(), "")
        lines: list[str] = [""]
        for entry in preferred_entries:
            selected_marker = " | selected" if entry.get("record_id") == selected_segment_id else ""
            lines.extend([
                f"- {entry.get('sequence', 0):02d}. {entry.get('segment_label', 'none')}{selected_marker}",
                f"  Start: {entry.get('start_timecode', 'none')}",
                f"  End: {entry.get('end_timecode', 'none')}",
                f"  Rough-cut segment stub id: {entry.get('record_id', 'unknown')}",
                "  Editorial scope: current preferred rough-cut subset for later assembly only, not a real cut or final timeline.",
                "",
            ])
        return lines

    def _selected_candidate_stubs(self, project: ProjectSlice) -> list[dict]:
        return [
            entry
            for entry in project.matching_candidate_stubs
            if entry.get("review_status", ALLOWED_CANDIDATE_REVIEW_STATUSES[0]) == "selected"
        ]

    def _selected_candidate_summary(self, project: ProjectSlice) -> str:
        selected_count = len(self._selected_candidate_stubs(project))
        if selected_count:
            return f"Selected candidates currently preferred for review: {selected_count} present."
        return "Selected candidates currently preferred for review: none yet."

    def _selected_candidate_readiness_cue(self, project: ProjectSlice) -> str:
        selected_count = len(self._selected_candidate_stubs(project))
        if selected_count:
            return f"Preferred subset readiness: preferred subset exists now ({selected_count} selected candidate(s))."
        return "Preferred subset readiness: preferred subset not fixed yet (no selected candidates)."

    def _candidate_entry_lines(self, project: ProjectSlice, entry: dict, include_rationale: bool = False) -> list[str]:
        block_lookup = {block['record_id']: block for block in project.semantic_blocks}
        asset_lookup = {asset['record_id']: asset for asset in project.matching_prep_assets}
        block = block_lookup.get(entry.get("semantic_block_id"))
        asset = asset_lookup.get(entry.get("prep_asset_id"))
        block_label = f"{block['sequence']:02d}. {block['title']}" if block else entry.get("semantic_block_id", "unknown semantic block")
        asset_label = f"{asset['asset_label']} [{asset['asset_type']}]" if asset else entry.get("prep_asset_id", "unknown prep input")
        note = entry.get("note", "").strip() or "none"
        review_status = entry.get("review_status", ALLOWED_CANDIDATE_REVIEW_STATUSES[0])
        lines = [
            f"- {block_label} -> {asset_label}",
            f"  Review status: {review_status}",
        ]
        if include_rationale:
            rationale = entry.get("preferred_rationale", "").strip() or "not recorded yet"
            lines.append(f"  Preferred rationale: {rationale}")
        lines.extend([
            f"  Note: {note}",
            f"  Stub id: {entry['record_id']}",
            "",
        ])
        return lines

    def _selected_candidate_lines(self, project: ProjectSlice) -> list[str]:
        selected_entries = self._selected_candidate_stubs(project)
        if not selected_entries:
            return ["- none selected yet", ""]
        lines: list[str] = [""]
        for entry in selected_entries:
            lines.extend(self._candidate_entry_lines(project, entry, include_rationale=True))
        return lines

    def _visible_candidate_stubs(self, project: ProjectSlice) -> list[dict]:
        focus = self.candidate_focus_var.get() if self.candidate_focus_var.get() in CANDIDATE_STATUS_FOCUS_OPTIONS else CANDIDATE_STATUS_FOCUS_OPTIONS[0]
        if focus == "all":
            visible_entries = list(project.matching_candidate_stubs)
        else:
            visible_entries = [entry for entry in project.matching_candidate_stubs if entry.get("review_status", ALLOWED_CANDIDATE_REVIEW_STATUSES[0]) == focus]

        selected_entries = [entry for entry in visible_entries if entry.get("review_status", ALLOWED_CANDIDATE_REVIEW_STATUSES[0]) == "selected"]
        other_entries = [entry for entry in visible_entries if entry.get("review_status", ALLOWED_CANDIDATE_REVIEW_STATUSES[0]) != "selected"]
        return [*selected_entries, *other_entries]

    def _candidate_focus_label(self) -> str:
        focus = self.candidate_focus_var.get() if self.candidate_focus_var.get() in CANDIDATE_STATUS_FOCUS_OPTIONS else CANDIDATE_STATUS_FOCUS_OPTIONS[0]
        return "all candidate stubs" if focus == "all" else f"{focus} only"

    def _candidate_stub_lines(self, project: ProjectSlice) -> list[str]:
        if not project.matching_candidate_stubs:
            return ["- none yet", ""]
        visible_entries = self._visible_candidate_stubs(project)
        if not visible_entries:
            return [f"- none in current focus ({self._candidate_focus_label()})", ""]
        lines: list[str] = [""]
        for entry in visible_entries:
            lines.extend(self._candidate_entry_lines(project, entry))
        return lines

    def _update_matching_prep_surface(self, project: ProjectSlice) -> None:
        gate_state, gate_reason = self._matching_prep_gate(project)
        asset_count = len(project.matching_prep_assets)
        candidate_count = len(project.matching_candidate_stubs)
        visible_candidate_count = len(self._visible_candidate_stubs(project))
        focus_label = self._candidate_focus_label()
        if gate_state != "ready":
            self.matching_prep_status_text.set(f"Matching Prep is blocked: {gate_reason}.")
            self.matching_prep_summary_text.set("Prep handoff: 0 approved semantic blocks available.")
            if asset_count:
                self.matching_asset_summary_text.set(f"Film-side registration: {asset_count} prep input(s) registered but currently gated.")
            else:
                self.matching_asset_summary_text.set("Film-side registration: no prep inputs registered yet.")
            self.matching_accepted_reference_summary_text.set(self._accepted_reference_summary(project))
            if candidate_count:
                self.matching_candidate_summary_text.set(f"{self._selected_candidate_readiness_cue(project)} | {self._selected_candidate_summary(project)} | Manual candidate stubs: {visible_candidate_count} visible of {candidate_count} stored but currently gated | focus: {focus_label} | {self._candidate_status_summary(project)}.")
            else:
                self.matching_candidate_summary_text.set("Manual candidate stubs: none yet.")
            lines = [
                "Matching Prep remains blocked in this project state.",
                "",
                f"Reason: {gate_reason}.",
                self._accepted_reference_summary(project),
                self._selected_candidate_readiness_cue(project),
                self._selected_candidate_summary(project),
                "",
                "Registered film-side inputs",
            ]
            if project.matching_prep_assets:
                lines.append("")
                for entry in project.matching_prep_assets:
                    reference_value = entry.get("reference_value", "").strip() or "none"
                    notes = entry.get("notes", "").strip() or "none"
                    lines.extend(
                        [
                            f"- {entry['asset_label']} [{entry['asset_type']}]",
                            f"  Reference: {reference_value}",
                            f"  Notes: {notes}",
                            "",
                        ]
                    )
            else:
                lines.extend(["- none yet", ""])
            lines.extend(["Accepted reference for later matching work", *self._accepted_reference_lines(project), "Selected candidates currently preferred for review", *self._selected_candidate_lines(project), f"Manual candidate stubs | focus: {focus_label}", *self._candidate_stub_lines(project)])
            lines.append("This first downstream-facing slice opens only after the semantic map is approved.")
            handoff_text = "\n".join(lines).rstrip()
        else:
            block_count = len(project.semantic_blocks)
            asset_state = "semantic-plus-asset registration present" if asset_count else "semantic-only handoff present"
            self.matching_prep_status_text.set(
                "Matching Prep is open: approved semantic handoff is available for later scene matching work."
            )
            self.matching_prep_summary_text.set(
                f"Prep handoff: {block_count} approved semantic block(s) ready for later matching prep | {asset_state}."
            )
            if asset_count:
                self.matching_asset_summary_text.set(f"Film-side registration: {asset_count} prep input(s) registered.")
            else:
                self.matching_asset_summary_text.set("Film-side registration: no prep inputs registered yet.")
            self.matching_accepted_reference_summary_text.set(self._accepted_reference_summary(project))
            if candidate_count:
                self.matching_candidate_summary_text.set(f"{self._selected_candidate_readiness_cue(project)} | {self._selected_candidate_summary(project)} | Manual candidate stubs: {visible_candidate_count} visible of {candidate_count} saved in this project | focus: {focus_label} | {self._candidate_status_summary(project)}.")
            else:
                self.matching_candidate_summary_text.set("Manual candidate stubs: no manual candidate stubs yet.")
            lines = [
                "Approved semantic handoff for later matching prep",
                f"Project: {project.project_record['title']}",
                f"Semantic blocks: {block_count}",
                f"Registered prep inputs: {asset_count}",
                self._accepted_reference_summary(project),
                self._selected_candidate_readiness_cue(project),
                self._selected_candidate_summary(project),
                f"Manual candidate stubs: {visible_candidate_count} visible of {candidate_count} | focus: {focus_label} | {self._candidate_status_summary(project)}",
                "",
                "Registered film-side inputs",
            ]
            if project.matching_prep_assets:
                lines.append("")
                for entry in project.matching_prep_assets:
                    reference_value = entry.get("reference_value", "").strip() or "none"
                    notes = entry.get("notes", "").strip() or "none"
                    lines.extend(
                        [
                            f"- {entry['asset_label']} [{entry['asset_type']}]",
                            f"  Reference: {reference_value}",
                            f"  Notes: {notes}",
                            "",
                        ]
                    )
            else:
                lines.extend(["- none yet", ""])
            lines.extend(["Accepted reference for later matching work", *self._accepted_reference_lines(project), "Selected candidates currently preferred for review", *self._selected_candidate_lines(project), f"Manual candidate stubs | focus: {focus_label}", *self._candidate_stub_lines(project)])
            lines.extend(["Approved semantic handoff", ""])
            for block in project.semantic_blocks:
                notes = block.get("notes", "").strip() or "none"
                lines.extend(
                    [
                        f"{block['sequence']:02d}. {block['title']} [{block['semantic_role']}]",
                        f"Notes: {notes}",
                        f"Suitability: {self._suitability_summary(block)}",
                        "",
                    ]
                )
            handoff_text = "\n".join(lines).rstrip()

        self.matching_prep_handoff.configure(state="normal")
        self.matching_prep_handoff.delete("1.0", "end")
        self.matching_prep_handoff.insert("1.0", handoff_text)
        self.matching_prep_handoff.configure(state="disabled")

    def _update_scene_matching_surface(self, project: ProjectSlice) -> None:
        gate_state, gate_reason = self._scene_matching_gate(project)
        accepted_reference_summary = self._accepted_reference_summary(project)
        accepted_scene_reference_stub_summary = self._accepted_scene_reference_stub_summary(project)
        timecode_range_stub_summary = self._timecode_range_stub_summary(project)
        self.scene_matching_reference_summary_text.set(accepted_scene_reference_stub_summary)
        self.scene_matching_timecode_summary_text.set(timecode_range_stub_summary)
        self._set_scene_matching_enabled(gate_state == "ready")
        lines: list[str]
        if gate_state != "ready":
            lines = [
                "Scene Matching remains blocked in this project state.",
                "",
                f"Reason: {gate_reason}.",
                accepted_reference_summary,
                accepted_scene_reference_stub_summary,
                timecode_range_stub_summary,
                "",
                "Current timecode range stub",
                *self._timecode_range_stub_lines(project),
                "Current accepted scene reference stub",
                *self._accepted_scene_reference_stub_lines(project),
                "Current accepted reference handoff",
                *self._accepted_reference_lines(project),
                "This lane is scene-matching-facing only. It remains pre-automation, pre-timecode, and pre-final-output and does not perform automatic matching yet.",
            ]
        else:
            lines = [
                "Scene Matching handoff is open.",
                accepted_reference_summary,
                accepted_scene_reference_stub_summary,
                timecode_range_stub_summary,
                "",
                "Current timecode range stub",
                *self._timecode_range_stub_lines(project),
                "Current accepted scene reference stub",
                *self._accepted_scene_reference_stub_lines(project),
                "Current accepted reference for scene matching work",
                *self._accepted_reference_lines(project),
                "This lane is the first honest entry into scene matching work.",
                "It remains provisional, pre-automation, pre-timecode, and pre-final-match.",
            ]
        handoff_text = "\n".join(lines).rstrip()
        self.scene_matching_handoff.configure(state="normal")
        self.scene_matching_handoff.delete("1.0", "end")
        self.scene_matching_handoff.insert("1.0", handoff_text)
        self.scene_matching_handoff.configure(state="disabled")

    def _update_rough_cut_surface(self, project: ProjectSlice) -> None:
        gate_state, gate_reason = self._rough_cut_gate(project)
        accepted_reference_summary = self._accepted_reference_summary(project)
        accepted_scene_reference_stub_summary = self._accepted_scene_reference_stub_summary(project)
        timecode_range_stub_summary = self._timecode_range_stub_summary(project)
        rough_cut_segment_stub_summary = self._rough_cut_segment_stub_summary(project)
        rough_cut_preferred_subset_summary = self._rough_cut_preferred_subset_summary(project)
        rough_cut_focus_label = self._rough_cut_focus_label()
        rough_cut_reorder_guidance = self._rough_cut_reorder_guidance()
        visible_segment_count = len(self._visible_rough_cut_segments(project))
        rough_cut_focus_summary = self._rough_cut_focus_summary(project)
        self.rough_cut_focus_summary_text.set(rough_cut_focus_summary)
        self.rough_cut_segment_summary_text.set(rough_cut_segment_stub_summary)
        self._set_rough_cut_enabled(gate_state == "ready")
        if gate_state != "ready":
            lines = [
                "Rough Cut remains blocked in this project state.",
                "",
                f"Reason: {gate_reason}.",
                accepted_reference_summary,
                accepted_scene_reference_stub_summary,
                timecode_range_stub_summary,
                rough_cut_segment_stub_summary,
                rough_cut_preferred_subset_summary,
                rough_cut_focus_summary,
                f"Rough-cut focus: {rough_cut_focus_label} | visible segments: {visible_segment_count}.",
                rough_cut_reorder_guidance,
                "",
                "Current preferred rough-cut subset",
                *self._preferred_rough_cut_segment_lines(project),
                f"Current rough-cut segment set | focus: {rough_cut_focus_label}",
                *self._rough_cut_segment_stub_lines(project),
                "Current timecode range stub",
                *self._timecode_range_stub_lines(project),
                "Current accepted scene reference stub",
                *self._accepted_scene_reference_stub_lines(project),
                "Current accepted reference handoff",
                *self._accepted_reference_lines(project),
                "This lane is assembly-facing only. It remains provisional, local-first, pre-render, not a real cut, and not a final timeline and does not perform real editing yet.",
            ]
        else:
            lines = [
                "Rough Cut handoff is open.",
                accepted_reference_summary,
                accepted_scene_reference_stub_summary,
                timecode_range_stub_summary,
                rough_cut_segment_stub_summary,
                rough_cut_preferred_subset_summary,
                rough_cut_focus_summary,
                f"Rough-cut focus: {rough_cut_focus_label} | visible segments: {visible_segment_count}.",
                rough_cut_reorder_guidance,
                "",
                "Current preferred rough-cut subset",
                *self._preferred_rough_cut_segment_lines(project),
                f"Current rough-cut segment set | focus: {rough_cut_focus_label}",
                *self._rough_cut_segment_stub_lines(project),
                "Current timecode range stub",
                *self._timecode_range_stub_lines(project),
                "Current accepted scene reference stub",
                *self._accepted_scene_reference_stub_lines(project),
                "Current accepted reference for assembly-facing work",
                *self._accepted_reference_lines(project),
                "This lane is the first honest entry into rough-cut-facing work.",
                "It remains provisional, local-first, pre-render, not a real cut, and not a final timeline.",
            ]
        handoff_text = "\n".join(lines).rstrip()
        self.rough_cut_handoff.configure(state="normal")
        self.rough_cut_handoff.delete("1.0", "end")
        self.rough_cut_handoff.insert("1.0", handoff_text)
        self.rough_cut_handoff.configure(state="disabled")

    def _update_output_tracks_surface(self, project: ProjectSlice) -> None:
        gate_state, gate_reason = self._output_builder_gate(project)
        inventory_text = self._output_inventory_text(project)
        recovery_text = self._output_recovery_text(project, gate_state, gate_reason)
        bundle_summary = self._packaging_script_bundle_summary(project)
        shorts_summary = self._shorts_reels_script_summary(project)
        long_video_summary = self._long_video_script_summary(project)
        carousel_summary = self._carousel_script_summary(project)
        bundle = project.packaging_script_bundle
        shorts_script = project.shorts_reels_script
        long_video_script = project.long_video_script
        carousel_script = project.carousel_script
        packaging_path = bundle.get("artifact_relative_path", "none") if bundle else "none"
        shorts_path = shorts_script.get("artifact_relative_path", "none") if shorts_script else "none"
        long_video_path = long_video_script.get("artifact_relative_path", "none") if long_video_script else "none"
        carousel_path = carousel_script.get("artifact_relative_path", "none") if carousel_script else "none"
        self.output_builder_inventory_text.set(inventory_text)
        self.output_builder_summary_text.set(recovery_text)
        self.output_builder_path_text.set(self._output_paths_text(project))
        self._set_output_builder_enabled(gate_state == "ready")
        lines = [
            "Output builders",
            "",
            f"Readiness: {gate_state} | {gate_reason}.",
            inventory_text,
            recovery_text,
            f"Next sensible action: {self._next_action_label(project).replace('Next action: ', '', 1)}",
            self._rough_cut_segment_stub_summary(project),
            self._rough_cut_preferred_subset_summary(project),
            "",
            "Current builder slots",
            *self._builder_slot_status_lines("Packaging", bundle, "Build Packaging-Ready Script Bundle to create the first packaging artifact."),
            *self._builder_slot_status_lines("Shorts/Reels", shorts_script, "Build Shorts/Reels Script to add the short-form output path."),
            *self._builder_slot_status_lines("Long Video", long_video_script, "Build Long-Video Script to add the long-form output path."),
            *self._builder_slot_status_lines("Carousel", carousel_script, "Build Carousel Script to add the slide-based output path."),
            "",
            "Packaging-ready script bundle builder",
            bundle_summary,
            f"Path: {packaging_path}",
            "",
            "Shorts/Reels script builder",
            shorts_summary,
            f"Path: {shorts_path}",
            "",
            "Long-video script builder",
            long_video_summary,
            f"Path: {long_video_path}",
            "",
            "Carousel script builder",
            carousel_summary,
            f"Path: {carousel_path}",
            "",
            "Packaging-ready script bundle preview",
            *self._packaging_script_bundle_lines(project),
            "",
            "Shorts/Reels script preview",
            *self._shorts_reels_script_lines(project),
            "",
            "Long-video script preview",
            *self._long_video_script_lines(project),
            "",
            "Carousel script preview",
            *self._carousel_script_lines(project),
        ]
        self.output_builder_handoff.configure(state="normal")
        self.output_builder_handoff.delete("1.0", "end")
        self.output_builder_handoff.insert("1.0", "\n".join(lines).rstrip())
        self.output_builder_handoff.configure(state="disabled")

    def _suitability_summary(self, block: dict) -> str:
        short = {
            "long_video": "LV",
            "shorts_reels": "SR",
            "carousel": "CA",
            "packaging": "PK",
        }
        value_short = {
            "candidate": "cand",
            "strong": "strong",
            "weak": "weak",
            "not_suitable": "no",
        }
        parts: list[str] = []
        for key in ("long_video", "shorts_reels", "carousel", "packaging"):
            value = block.get("output_suitability", {}).get(key, "candidate")
            if value != "candidate":
                parts.append(f"{short[key]}:{value_short[value]}")
        return "suit: all-candidate" if not parts else "suit: " + ", ".join(parts)

    def _project_suitability_summary(self, project: ProjectSlice) -> str:
        counts = {"strong": 0, "weak": 0, "not_suitable": 0}
        for block in project.semantic_blocks:
            for value in block.get("output_suitability", {}).values():
                if value in counts:
                    counts[value] += 1
        visible = [f"{key}:{value}" for key, value in counts.items() if value]
        return "all candidate" if not visible else ", ".join(visible)

    def _next_action_label(self, project: ProjectSlice) -> str:
        if not project.analysis_source_record:
            return "Next action: Load analysis text"
        review_status = project.semantic_review_record["review_status"]
        readiness = self._approval_readiness(project)
        rough_cut_state, _ = self._rough_cut_gate(project)
        output_builder_state, _ = self._output_builder_gate(project)
        if output_builder_state == "ready" and project.packaging_script_bundle is None:
            return "Next action: Build packaging-ready script bundle"
        if output_builder_state == "ready" and project.shorts_reels_script is None:
            return "Next action: Build Shorts/Reels script"
        if output_builder_state == "ready" and project.long_video_script is None:
            return "Next action: Build long-video script"
        if output_builder_state == "ready" and project.carousel_script is None:
            return "Next action: Build carousel script"
        if (
            project.packaging_script_bundle is not None
            or project.shorts_reels_script is not None
            or project.long_video_script is not None
            or project.carousel_script is not None
        ):
            return "Next action: Open Output Tracks"
        if rough_cut_state == "ready":
            return "Next action: Open Rough Cut"
        if project.accepted_reference is not None and not project.semantic_review_record.get("reopened_after_change"):
            return "Next action: Open Scene Matching"
        if review_status == "approved":
            return "Next action: Open Matching Prep"
        if readiness == "ready_for_approval":
            return "Next action: Approve semantic map"
        if readiness == "reopened_after_change":
            return "Next action: Re-approve semantic map after reviewing reopened changes"
        if readiness == "premature":
            return "Next action: Resolve incomplete semantic blocks"
        if readiness == "mixed":
            return "Next action: Tighten weak blocks before review"
        return "Next action: Reorder, split, merge, and refine semantic blocks"
