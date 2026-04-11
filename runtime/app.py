from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from runtime.project_slice import (
    ALLOWED_CANDIDATE_REVIEW_STATUSES,
    ALLOWED_MATCHING_ASSET_TYPES,
    ALLOWED_OUTPUT_SUITABILITY,
    ALLOWED_REVIEW_STATES,
    ALLOWED_SEMANTIC_ROLES,
    ProjectSlice,
    ProjectSliceStore,
    describe_warning_flags,
    semantic_completeness,
    split_sentences,
)
from runtime.ui.constants import (
    CANDIDATE_STATUS_FOCUS_OPTIONS,
    FOCUS_MODES,
    FOCUS_TO_SUITABILITY_KEY,
    ROUGH_CUT_FOCUS_OPTIONS,
)
from runtime.ui.layout import DNAFilmAppLayoutMixin


class DNAFilmApp(DNAFilmAppLayoutMixin):
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("DNA Film Content Engine - Semantic Review Workspace")
        self.root.geometry("1400x860")

        self.workspace_root = Path.cwd() / "runtime_projects"
        self.workspace_root.mkdir(exist_ok=True)
        self.store = ProjectSliceStore(self.workspace_root)
        self.project: ProjectSlice | None = None
        self.selected_block_id: str | None = None
        self.visible_blocks: list[dict] = []

        self.current_view = tk.StringVar(value="Project Home")
        self.header_title = tk.StringVar(value="No project loaded")
        self.header_status = tk.StringVar(value="Create a project to begin the semantic-first flow.")
        self.next_action = tk.StringVar(value="Next action: Create project")
        self.summary_text = tk.StringVar(value="No semantic map yet.")
        self.review_status_text = tk.StringVar(value="Semantic review: under_edit")
        self.completeness_text = tk.StringVar(value="Semantic completeness: Incomplete")
        self.issues_summary_text = tk.StringVar(value="Issue visibility: no semantic issues yet.")
        self.readiness_text = tk.StringVar(value="Approval readiness: not_ready")
        self.focus_mode_var = tk.StringVar(value=FOCUS_MODES[0])
        self.focus_status_text = tk.StringVar(value="Focus: All blocks | showing 0 of 0 blocks.")
        self.focus_span_text = tk.StringVar(value="Focus span: no matching blocks")
        self.focus_position_text = tk.StringVar(value="Focused item: 0 of 0")
        self.previous_context_text = tk.StringVar(value="Previous: No previous semantic block")
        self.next_context_text = tk.StringVar(value="Next: No next semantic block")
        self.approval_message_text = tk.StringVar(value="Approval message: Semantic map remains under edit.")
        self.approval_reason_text = tk.StringVar(value="Approval reason: Approve is blocked until semantic review is moved to ready_for_review.")
        self.reopen_text = tk.StringVar(value="Reopen state: none")
        self.matching_prep_text = tk.StringVar(value="Matching prep readiness: blocked | semantic map not established yet")
        self.scene_matching_text = tk.StringVar(value="Scene matching readiness: blocked | no accepted reference available yet")
        self.rough_cut_text = tk.StringVar(value="Rough cut readiness: blocked | no accepted reference available yet")
        self.output_builder_status_text = tk.StringVar(value="Output builder readiness: blocked | no rough-cut output path available yet")
        self.output_builder_summary_text = tk.StringVar(value="Packaging-ready script bundle: none built yet.")
        self.output_builder_path_text = tk.StringVar(value="Artifact path: none")
        self.scene_matching_reference_summary_text = tk.StringVar(value="Accepted scene reference stub: none created yet.")
        self.scene_matching_timecode_summary_text = tk.StringVar(value="Timecode range stub: none saved yet.")
        self.rough_cut_focus_summary_text = tk.StringVar(value="Focus: all saved segments | Visible: 0 | Saved total: 0 | Preferred total: 0")
        self.rough_cut_segment_summary_text = tk.StringVar(value="Rough-cut segment set: none saved yet.")
        self.matching_prep_status_text = tk.StringVar(value="Matching Prep is blocked until the semantic map is approved.")
        self.matching_prep_summary_text = tk.StringVar(value="Prep handoff: 0 approved semantic blocks available.")
        self.matching_asset_summary_text = tk.StringVar(value="Film-side registration: no prep inputs registered yet.")
        self.matching_accepted_reference_summary_text = tk.StringVar(value="Accepted reference: none accepted yet for later matching work.")
        self.matching_candidate_summary_text = tk.StringVar(value="Manual candidate stubs: none yet.")
        self.placeholder_text = tk.StringVar(value="Available after semantic-map approval in a later bounded packet.")

        self.project_name_var = tk.StringVar()
        self.film_title_var = tk.StringVar()
        self.language_var = tk.StringVar(value="en")
        self.block_title_var = tk.StringVar()
        self.block_role_var = tk.StringVar(value=ALLOWED_SEMANTIC_ROLES[0])
        self.review_status_var = tk.StringVar(value=ALLOWED_REVIEW_STATES[0])
        self.split_sentence_var = tk.StringVar(value="1")
        self.block_status_var = tk.StringVar(value="Select a semantic block to inspect, reorder, split, merge, and edit it here.")
        self.block_issues_text = tk.StringVar(value="Block issues: none")
        self.long_video_var = tk.StringVar(value=ALLOWED_OUTPUT_SUITABILITY[0])
        self.shorts_reels_var = tk.StringVar(value=ALLOWED_OUTPUT_SUITABILITY[0])
        self.carousel_var = tk.StringVar(value=ALLOWED_OUTPUT_SUITABILITY[0])
        self.packaging_var = tk.StringVar(value=ALLOWED_OUTPUT_SUITABILITY[0])
        self.asset_label_var = tk.StringVar()
        self.asset_type_var = tk.StringVar(value=ALLOWED_MATCHING_ASSET_TYPES[0])
        self.asset_reference_var = tk.StringVar()
        self.candidate_block_var = tk.StringVar()
        self.candidate_asset_var = tk.StringVar()
        self.candidate_note_var = tk.StringVar()
        self.candidate_stub_var = tk.StringVar()
        self.candidate_status_var = tk.StringVar(value=ALLOWED_CANDIDATE_REVIEW_STATUSES[0])
        self.candidate_rationale_var = tk.StringVar()
        self.candidate_focus_var = tk.StringVar(value=CANDIDATE_STATUS_FOCUS_OPTIONS[0])
        self.rough_cut_focus_var = tk.StringVar(value=ROUGH_CUT_FOCUS_OPTIONS[0])
        self.scene_reference_label_var = tk.StringVar()
        self.timecode_start_var = tk.StringVar()
        self.timecode_end_var = tk.StringVar()
        self.rough_cut_segment_label_var = tk.StringVar()
        self.rough_cut_segment_var = tk.StringVar()
        self.candidate_block_options: dict[str, str] = {}
        self.candidate_asset_options: dict[str, str] = {}
        self.candidate_stub_options: dict[str, str] = {}
        self.rough_cut_segment_options: dict[str, str] = {}

        self._build_layout()
        self._switch_view("Project Home")
        self._set_editor_enabled(False)
        self._set_structure_enabled(False, False, False, False, False)
        self._set_focus_navigation_enabled(False, False)
        self._set_matching_candidate_enabled(False, False, False)
        self._set_scene_matching_enabled(False)
        self._set_rough_cut_enabled(False)
        self._set_output_builder_enabled(False)

    def create_project(self) -> None:
        title = self.project_name_var.get().strip()
        try:
            project = self.store.create_project(
                title=title,
                film_title=self.film_title_var.get(),
                language=self.language_var.get(),
            )
        except ValueError as exc:
            messagebox.showerror("Project creation", str(exc))
            return
        except FileExistsError:
            messagebox.showerror("Project creation", "A project folder with the same generated name already exists.")
            return

        self.focus_mode_var.set(FOCUS_MODES[0])
        self._load_project_into_ui(project)
        self._switch_view("Source Intake")
        messagebox.showinfo("Project created", f"Project package created at:\n{project.project_dir}")

    def open_project(self) -> None:
        selected = filedialog.askdirectory(initialdir=self.workspace_root, title="Open project directory")
        if not selected:
            return
        try:
            project = self.store.load_project(Path(selected))
        except FileNotFoundError:
            messagebox.showerror("Open project", "Selected folder does not look like a DNA project package.")
            return
        self.focus_mode_var.set(FOCUS_MODES[0])
        self._load_project_into_ui(project)
        self._switch_view("Project Home")

    def save_analysis_text(self) -> None:
        if self.project is None:
            messagebox.showerror("Source intake", "Create or open a project first.")
            return
        text = self.analysis_text.get("1.0", "end")
        try:
            project = self.store.save_analysis_text(self.project.project_dir, text)
        except ValueError as exc:
            messagebox.showerror("Source intake", str(exc))
            return

        self.focus_mode_var.set(FOCUS_MODES[0])
        self._load_project_into_ui(project)
        self._switch_view("Semantic Map")
        if project.semantic_blocks:
            self._select_block_by_id(project.semantic_blocks[0]["record_id"])
        messagebox.showinfo("Semantic map ready", f"Saved analysis text and derived {len(project.semantic_blocks)} semantic blocks.")

    def on_block_selected(self, _event: object) -> None:
        if self.project is None:
            return
        selection = self.semantic_list.curselection()
        if not selection:
            self.selected_block_id = None
            self._set_editor_enabled(False)
            self._set_structure_enabled(False, False, False, False, False)
            self._set_focus_navigation_enabled(False, False)
            self.focus_position_text.set("Focused item: 0 of 0")
            self.focus_span_text.set("Focus span: no matching blocks")
            self.previous_context_text.set("Previous: No previous semantic block")
            self.next_context_text.set("Next: No next semantic block")
            self.block_issues_text.set("Block issues: none")
            return
        block = self.visible_blocks[selection[0]]
        self._show_block(block)

    def navigate_focus(self, direction: str) -> None:
        if not self.visible_blocks or self.selected_block_id is None:
            return
        current_index = next((index for index, block in enumerate(self.visible_blocks) if block["record_id"] == self.selected_block_id), None)
        if current_index is None:
            return
        if direction == "previous":
            target_index = current_index - 1
        elif direction == "next":
            target_index = current_index + 1
        else:
            raise ValueError("Navigation direction must be 'previous' or 'next'.")
        if target_index < 0 or target_index >= len(self.visible_blocks):
            self._update_focus_navigation_state()
            return
        self._select_block_by_id(self.visible_blocks[target_index]["record_id"])

    def save_selected_block(self) -> None:
        if self.project is None or self.selected_block_id is None:
            messagebox.showerror("Semantic map", "Select a semantic block first.")
            return
        notes = self.notes_text.get("1.0", "end").strip()
        output_suitability = {
            "long_video": self.long_video_var.get(),
            "shorts_reels": self.shorts_reels_var.get(),
            "carousel": self.carousel_var.get(),
            "packaging": self.packaging_var.get(),
        }
        try:
            project = self.store.update_semantic_block(
                self.project.project_dir,
                self.selected_block_id,
                self.block_title_var.get(),
                self.block_role_var.get(),
                notes,
                output_suitability=output_suitability,
            )
        except ValueError as exc:
            messagebox.showerror("Semantic map", str(exc))
            return
        self._load_project_into_ui(project, select_block_id=self.selected_block_id)
        self._switch_view("Semantic Map")
        self.block_status_var.set("Block review changes saved to the local project package.")
        messagebox.showinfo("Semantic map", "Selected block review changes were saved.")

    def reorder_selected_block(self, direction: str) -> None:
        if self.project is None or self.selected_block_id is None:
            messagebox.showerror("Semantic map", "Select a semantic block first.")
            return
        try:
            project = self.store.reorder_semantic_block(self.project.project_dir, self.selected_block_id, direction)
        except ValueError as exc:
            messagebox.showerror("Semantic map", str(exc))
            return
        self._load_project_into_ui(project, select_block_id=self.selected_block_id)
        self._switch_view("Semantic Map")
        self.block_status_var.set(f"Block order updated: moved {direction} and persisted to disk.")

    def split_selected_block(self) -> None:
        if self.project is None or self.selected_block_id is None:
            messagebox.showerror("Semantic map", "Select a semantic block first.")
            return
        try:
            split_after_sentence = int(self.split_sentence_var.get().strip())
        except ValueError:
            messagebox.showerror("Semantic map", "Split after sentence # must be a whole number.")
            return
        try:
            project = self.store.split_semantic_block(self.project.project_dir, self.selected_block_id, split_after_sentence)
        except ValueError as exc:
            messagebox.showerror("Semantic map", str(exc))
            return
        self._load_project_into_ui(project, select_block_id=self.selected_block_id)
        self._switch_view("Semantic Map")
        self.block_status_var.set("Selected block was split and the new semantic structure was persisted to disk.")
        messagebox.showinfo("Semantic map", "Selected block was split into two semantic blocks.")

    def merge_selected_block(self, direction: str) -> None:
        if self.project is None or self.selected_block_id is None:
            messagebox.showerror("Semantic map", "Select a semantic block first.")
            return
        try:
            project = self.store.merge_semantic_block(self.project.project_dir, self.selected_block_id, direction)
        except ValueError as exc:
            messagebox.showerror("Semantic map", str(exc))
            return
        self._load_project_into_ui(project, select_block_id=self.selected_block_id)
        self._switch_view("Semantic Map")
        self.block_status_var.set(f"Selected block was merged {direction} and the semantic structure was persisted to disk.")
        messagebox.showinfo("Semantic map", f"Selected block was merged {direction} with its adjacent neighbor.")

    def add_matching_prep_asset(self) -> None:
        if self.project is None:
            messagebox.showerror("Matching Prep", "Create or open a project first.")
            return
        try:
            project = self.store.add_matching_prep_asset(
                self.project.project_dir,
                self.asset_label_var.get(),
                self.asset_type_var.get(),
                self.asset_reference_var.get(),
                self.asset_notes_text.get("1.0", "end").strip(),
            )
        except ValueError as exc:
            messagebox.showerror("Matching Prep", str(exc))
            return

        current_block_id = self.selected_block_id
        self._load_project_into_ui(project, select_block_id=current_block_id)
        self._switch_view("Matching Prep")
        self.asset_label_var.set("")
        self.asset_type_var.set(ALLOWED_MATCHING_ASSET_TYPES[0])
        self.asset_reference_var.set("")
        self.asset_notes_text.delete("1.0", "end")
        messagebox.showinfo("Matching Prep", "Film-side prep input was registered in the local project package.")

    def add_matching_candidate_stub(self) -> None:
        if self.project is None:
            messagebox.showerror("Matching Prep", "Create or open a project first.")
            return
        block_id = self.candidate_block_options.get(self.candidate_block_var.get(), "")
        asset_id = self.candidate_asset_options.get(self.candidate_asset_var.get(), "")
        try:
            project = self.store.add_matching_candidate_stub(
                self.project.project_dir,
                block_id,
                asset_id,
                self.candidate_note_var.get(),
            )
        except ValueError as exc:
            messagebox.showerror("Matching Prep", str(exc))
            return

        current_block_id = self.selected_block_id
        self._load_project_into_ui(project, select_block_id=current_block_id)
        self._switch_view("Matching Prep")
        latest_stub = project.matching_candidate_stubs[-1] if project.matching_candidate_stubs else None
        if latest_stub is not None:
            latest_label = self._candidate_stub_option_label(project, latest_stub)
            if latest_label in self.candidate_stub_options:
                self.candidate_stub_var.set(latest_label)
                self.candidate_status_var.set(latest_stub.get("review_status", ALLOWED_CANDIDATE_REVIEW_STATUSES[0]))
                self.candidate_rationale_var.set(latest_stub.get("preferred_rationale", ""))
        self.candidate_note_var.set("")
        messagebox.showinfo("Matching Prep", "Manual candidate stub was saved in the local project package.")

    def save_matching_candidate_status(self) -> None:
        if self.project is None:
            messagebox.showerror("Matching Prep", "Create or open a project first.")
            return
        candidate_stub_id = self.candidate_stub_options.get(self.candidate_stub_var.get(), "")
        try:
            project = self.store.update_matching_candidate_stub_status(
                self.project.project_dir,
                candidate_stub_id,
                self.candidate_status_var.get(),
            )
        except ValueError as exc:
            messagebox.showerror("Matching Prep", str(exc))
            return

        current_block_id = self.selected_block_id
        current_candidate_id = candidate_stub_id
        self._load_project_into_ui(project, select_block_id=current_block_id)
        self._switch_view("Matching Prep")
        updated_stub = next((entry for entry in project.matching_candidate_stubs if entry["record_id"] == current_candidate_id), None)
        if updated_stub is not None:
            updated_label = self._candidate_stub_option_label(project, updated_stub)
            if updated_label in self.candidate_stub_options:
                self.candidate_stub_var.set(updated_label)
                self.candidate_status_var.set(updated_stub.get("review_status", ALLOWED_CANDIDATE_REVIEW_STATUSES[0]))
                self.candidate_rationale_var.set(updated_stub.get("preferred_rationale", ""))
        messagebox.showinfo("Matching Prep", "Manual candidate review status was saved in the local project package.")

    def save_matching_candidate_rationale(self) -> None:
        if self.project is None:
            messagebox.showerror("Matching Prep", "Create or open a project first.")
            return
        candidate_stub_id = self.candidate_stub_options.get(self.candidate_stub_var.get(), "")
        try:
            project = self.store.update_matching_candidate_stub_rationale(
                self.project.project_dir,
                candidate_stub_id,
                self.candidate_rationale_var.get(),
            )
        except ValueError as exc:
            messagebox.showerror("Matching Prep", str(exc))
            return

        current_block_id = self.selected_block_id
        current_candidate_id = candidate_stub_id
        self._load_project_into_ui(project, select_block_id=current_block_id)
        self._switch_view("Matching Prep")
        updated_stub = next((entry for entry in project.matching_candidate_stubs if entry["record_id"] == current_candidate_id), None)
        if updated_stub is not None:
            updated_label = self._candidate_stub_option_label(project, updated_stub)
            if updated_label in self.candidate_stub_options:
                self.candidate_stub_var.set(updated_label)
                self.candidate_status_var.set(updated_stub.get("review_status", ALLOWED_CANDIDATE_REVIEW_STATUSES[0]))
                self.candidate_rationale_var.set(updated_stub.get("preferred_rationale", ""))
        messagebox.showinfo("Matching Prep", "Manual candidate preferred rationale was saved in the local project package.")

    def promote_matching_candidate_to_accepted_reference(self) -> None:
        if self.project is None:
            messagebox.showerror("Matching Prep", "Create or open a project first.")
            return
        candidate_stub_id = self.candidate_stub_options.get(self.candidate_stub_var.get(), "")
        try:
            project = self.store.promote_matching_candidate_stub_to_accepted_reference(
                self.project.project_dir,
                candidate_stub_id,
            )
        except ValueError as exc:
            messagebox.showerror("Matching Prep", str(exc))
            return

        current_block_id = self.selected_block_id
        current_candidate_id = candidate_stub_id
        self._load_project_into_ui(project, select_block_id=current_block_id)
        self._switch_view("Matching Prep")
        accepted_stub = next((entry for entry in project.matching_candidate_stubs if entry["record_id"] == current_candidate_id), None)
        if accepted_stub is not None:
            accepted_label = self._candidate_stub_option_label(project, accepted_stub)
            if accepted_label in self.candidate_stub_options:
                self.candidate_stub_var.set(accepted_label)
                self.candidate_status_var.set(accepted_stub.get("review_status", ALLOWED_CANDIDATE_REVIEW_STATUSES[0]))
                self.candidate_rationale_var.set(accepted_stub.get("preferred_rationale", ""))
        messagebox.showinfo("Matching Prep", "Selected manual candidate stub was promoted to the current accepted reference for later matching work.")

    def remove_matching_candidate_stub(self) -> None:
        if self.project is None:
            messagebox.showerror("Matching Prep", "Create or open a project first.")
            return
        candidate_stub_id = self.candidate_stub_options.get(self.candidate_stub_var.get(), "")
        try:
            project = self.store.remove_matching_candidate_stub(
                self.project.project_dir,
                candidate_stub_id,
            )
        except ValueError as exc:
            messagebox.showerror("Matching Prep", str(exc))
            return

        current_block_id = self.selected_block_id
        self._load_project_into_ui(project, select_block_id=current_block_id)
        self._switch_view("Matching Prep")
        self.candidate_rationale_var.set("")
        messagebox.showinfo("Matching Prep", "Manual candidate stub was removed from the local project package.")

    def save_accepted_scene_reference_stub(self) -> None:
        if self.project is None:
            messagebox.showerror("Scene Matching", "Create or open a project first.")
            return
        try:
            project = self.store.save_accepted_scene_reference_stub(
                self.project.project_dir,
                self.scene_reference_label_var.get(),
            )
        except ValueError as exc:
            messagebox.showerror("Scene Matching", str(exc))
            return

        current_block_id = self.selected_block_id
        self._load_project_into_ui(project, select_block_id=current_block_id)
        self._switch_view("Scene Matching")
        self.scene_reference_label_var.set((project.accepted_scene_reference_stub or {}).get("scene_reference_label", ""))
        messagebox.showinfo("Scene Matching", "Accepted scene reference stub was saved in the local project package.")

    def save_timecode_range_stub(self) -> None:
        if self.project is None:
            messagebox.showerror("Scene Matching", "Create or open a project first.")
            return
        try:
            project = self.store.save_timecode_range_stub(
                self.project.project_dir,
                self.timecode_start_var.get(),
                self.timecode_end_var.get(),
            )
        except ValueError as exc:
            messagebox.showerror("Scene Matching", str(exc))
            return

        current_block_id = self.selected_block_id
        self._load_project_into_ui(project, select_block_id=current_block_id)
        self._switch_view("Scene Matching")
        self.timecode_start_var.set((project.timecode_range_stub or {}).get("start_timecode", ""))
        self.timecode_end_var.set((project.timecode_range_stub or {}).get("end_timecode", ""))
        messagebox.showinfo("Scene Matching", "Timecode range stub was saved in the local project package.")

    def save_rough_cut_segment_stub(self) -> None:
        if self.project is None:
            messagebox.showerror("Rough Cut", "Create or open a project first.")
            return
        try:
            project = self.store.save_rough_cut_segment_stub(
                self.project.project_dir,
                self.rough_cut_segment_label_var.get(),
            )
        except ValueError as exc:
            messagebox.showerror("Rough Cut", str(exc))
            return

        current_block_id = self.selected_block_id
        newest_segment_id = project.rough_cut_segment_stubs[-1]["record_id"] if project.rough_cut_segment_stubs else None
        self._load_project_into_ui(project, select_block_id=current_block_id)
        self._select_rough_cut_segment_by_id(newest_segment_id)
        self._switch_view("Rough Cut")
        self.rough_cut_segment_label_var.set("")
        messagebox.showinfo("Rough Cut", "Rough-cut segment stub was added to the local rough-cut set.")

    def build_packaging_script_bundle(self) -> None:
        if self.project is None:
            messagebox.showerror("Output Tracks", "Create or open a project first.")
            return
        try:
            project = self.store.build_packaging_script_bundle(self.project.project_dir)
        except ValueError as exc:
            messagebox.showerror("Output Tracks", str(exc))
            return

        current_block_id = self.selected_block_id
        self._load_project_into_ui(project, select_block_id=current_block_id)
        self._switch_view("Output Tracks")
        messagebox.showinfo("Output Tracks", "Packaging-ready script bundle was built and saved in the project package.")

    def on_rough_cut_segment_selected(self, _event: object | None = None) -> None:
        if self.project is None:
            self.rough_cut_segment_var.set("")
            return
        self._refresh_rough_cut_controls(self.project)
        self._update_rough_cut_surface(self.project)

    def on_rough_cut_focus_changed(self) -> None:
        if self.project is None:
            return
        self._refresh_rough_cut_controls(self.project)
        self._update_rough_cut_surface(self.project)

    def reorder_selected_rough_cut_segment(self, direction: str) -> None:
        if self.project is None:
            messagebox.showerror("Rough Cut", "Create or open a project first.")
            return
        segment_id = self.rough_cut_segment_options.get(self.rough_cut_segment_var.get(), "")
        try:
            project = self.store.reorder_rough_cut_segment_stub(self.project.project_dir, segment_id, direction)
        except ValueError as exc:
            messagebox.showerror("Rough Cut", str(exc))
            return

        current_block_id = self.selected_block_id
        selected_segment_id = segment_id
        self._load_project_into_ui(project, select_block_id=current_block_id)
        self._select_rough_cut_segment_by_id(selected_segment_id)
        self._switch_view("Rough Cut")

    def include_selected_rough_cut_segment(self) -> None:
        self._update_selected_rough_cut_subset_status("selected_for_current_rough_cut", "Selected rough-cut segment was included in the current preferred rough-cut subset.")

    def remove_selected_rough_cut_segment(self) -> None:
        self._update_selected_rough_cut_subset_status("saved_only", "Selected rough-cut segment was returned to the saved-only rough-cut set.")

    def remove_selected_saved_rough_cut_segment(self) -> None:
        if self.project is None:
            messagebox.showerror("Rough Cut", "Create or open a project first.")
            return
        segment_id = self.rough_cut_segment_options.get(self.rough_cut_segment_var.get(), "")
        current_ids = [entry["record_id"] for entry in self.project.rough_cut_segment_stubs]
        try:
            current_index = current_ids.index(segment_id)
        except ValueError:
            current_index = -1
        try:
            project = self.store.remove_rough_cut_segment_stub(self.project.project_dir, segment_id)
        except ValueError as exc:
            messagebox.showerror("Rough Cut", str(exc))
            return

        current_block_id = self.selected_block_id
        self._load_project_into_ui(project, select_block_id=current_block_id)
        remaining_entries = project.rough_cut_segment_stubs
        next_segment_id = None
        if remaining_entries:
            fallback_index = current_index
            if fallback_index < 0:
                fallback_index = 0
            if fallback_index >= len(remaining_entries):
                fallback_index = len(remaining_entries) - 1
            next_segment_id = remaining_entries[fallback_index]["record_id"]
        self._select_rough_cut_segment_by_id(next_segment_id)
        self._switch_view("Rough Cut")
        messagebox.showinfo("Rough Cut", "Selected rough-cut segment stub was removed from the local rough-cut set.")

    def _update_selected_rough_cut_subset_status(self, subset_status: str, success_message: str) -> None:
        if self.project is None:
            messagebox.showerror("Rough Cut", "Create or open a project first.")
            return
        segment_id = self.rough_cut_segment_options.get(self.rough_cut_segment_var.get(), "")
        try:
            project = self.store.update_rough_cut_segment_subset_status(self.project.project_dir, segment_id, subset_status)
        except ValueError as exc:
            messagebox.showerror("Rough Cut", str(exc))
            return

        current_block_id = self.selected_block_id
        self._load_project_into_ui(project, select_block_id=current_block_id)
        self._select_rough_cut_segment_by_id(segment_id)
        self._switch_view("Rough Cut")
        messagebox.showinfo("Rough Cut", success_message)

    def on_candidate_stub_selected(self, _event: object | None = None) -> None:
        if self.project is None:
            self.candidate_status_var.set(ALLOWED_CANDIDATE_REVIEW_STATUSES[0])
            self.candidate_rationale_var.set("")
            self.promote_accepted_reference_button.configure(state="disabled")
            return
        candidate_stub_id = self.candidate_stub_options.get(self.candidate_stub_var.get(), "")
        selected_stub = next((entry for entry in self.project.matching_candidate_stubs if entry["record_id"] == candidate_stub_id), None)
        self.candidate_status_var.set((selected_stub or {}).get("review_status", ALLOWED_CANDIDATE_REVIEW_STATUSES[0]))
        self.candidate_rationale_var.set((selected_stub or {}).get("preferred_rationale", ""))
        gate_state, _ = self._matching_prep_gate(self.project)
        can_promote = gate_state == "ready" and (selected_stub or {}).get("review_status", ALLOWED_CANDIDATE_REVIEW_STATUSES[0]) == "selected"
        self.promote_accepted_reference_button.configure(state="normal" if can_promote else "disabled")

    def on_candidate_focus_changed(self, _event: object | None = None) -> None:
        if self.project is None:
            return
        self._update_matching_prep_surface(self.project)

    def save_review_status(self) -> None:
        if self.project is None:
            messagebox.showerror("Semantic review", "Create or open a project first.")
            return
        try:
            project = self.store.update_semantic_review_status(self.project.project_dir, self.review_status_var.get())
        except ValueError as exc:
            messagebox.showerror("Semantic review", str(exc))
            return
        current_block_id = self.selected_block_id
        self._load_project_into_ui(project, select_block_id=current_block_id)
        self._switch_view("Semantic Map")
        if project.semantic_review_record.get("approval_block_reason") and project.semantic_review_record["review_status"] != "approved":
            messagebox.showinfo("Semantic review", project.semantic_review_record["approval_block_reason"])
        else:
            messagebox.showinfo("Semantic review", "Project-level semantic review status was saved.")

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
        return {"Incomplete": "premature", "Mixed": "mixed"}.get(completeness_label, "plausibly_reasonable")

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
        if completeness_label == "Mixed":
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
        rough_cut_state, rough_cut_reason = self._rough_cut_gate(project)
        if rough_cut_state != "ready":
            return ("blocked", f"rough cut is not ready yet ({rough_cut_reason})")
        if not project.rough_cut_segment_stubs:
            return ("blocked", "no rough-cut segment exists yet")
        return ("ready", "packaging-ready script bundle can be built from the current rough-cut handoff")

    def _output_builder_gate_text(self, project: ProjectSlice) -> str:
        state, reason = self._output_builder_gate(project)
        return f"Output builder readiness: {state} | {reason}"

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
        bundle_summary = self._packaging_script_bundle_summary(project)
        bundle = project.packaging_script_bundle
        artifact_path = bundle.get("artifact_relative_path", "none") if bundle else "none"
        self.output_builder_summary_text.set(bundle_summary)
        self.output_builder_path_text.set(f"Artifact path: {artifact_path}")
        self._set_output_builder_enabled(gate_state == "ready")
        lines = [
            "Packaging-ready script bundle builder",
            "",
            f"Readiness: {gate_state} | {gate_reason}.",
            bundle_summary,
            self._rough_cut_segment_stub_summary(project),
            self._rough_cut_preferred_subset_summary(project),
            "",
            *self._packaging_script_bundle_lines(project),
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
        if project.packaging_script_bundle is not None:
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


def main() -> None:
    root = tk.Tk()
    ttk.Style().theme_use("clam")
    DNAFilmApp(root)
    root.minsize(1200, 760)
    root.mainloop()


if __name__ == "__main__":
    main()

