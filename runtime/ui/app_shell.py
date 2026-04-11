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
)
from runtime.ui.constants import CANDIDATE_STATUS_FOCUS_OPTIONS, FOCUS_MODES, ROUGH_CUT_FOCUS_OPTIONS
from runtime.ui.layout import DNAFilmAppLayoutMixin
from runtime.ui.presentation import DNAFilmAppPresentationMixin


class DNAFilmApp(DNAFilmAppLayoutMixin, DNAFilmAppPresentationMixin):
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
        self.output_builder_summary_text = tk.StringVar(
            value="Packaging-ready script bundle: none built yet. Shorts/Reels script: none built yet. Long-video script: none built yet. Carousel script: none built yet."
        )
        self.output_builder_path_text = tk.StringVar(value="Packaging path: none | Shorts/Reels path: none | Long-video path: none | Carousel path: none")
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

    def build_shorts_reels_script(self) -> None:
        if self.project is None:
            messagebox.showerror("Output Tracks", "Create or open a project first.")
            return
        try:
            project = self.store.build_shorts_reels_script(self.project.project_dir)
        except ValueError as exc:
            messagebox.showerror("Output Tracks", str(exc))
            return

        current_block_id = self.selected_block_id
        self._load_project_into_ui(project, select_block_id=current_block_id)
        self._switch_view("Output Tracks")
        messagebox.showinfo("Output Tracks", "Shorts/Reels script was built and saved in the project package.")

    def build_long_video_script(self) -> None:
        if self.project is None:
            messagebox.showerror("Output Tracks", "Create or open a project first.")
            return
        try:
            project = self.store.build_long_video_script(self.project.project_dir)
        except ValueError as exc:
            messagebox.showerror("Output Tracks", str(exc))
            return

        current_block_id = self.selected_block_id
        self._load_project_into_ui(project, select_block_id=current_block_id)
        self._switch_view("Output Tracks")
        messagebox.showinfo("Output Tracks", "Long-video script was built and saved in the project package.")

    def build_carousel_script(self) -> None:
        if self.project is None:
            messagebox.showerror("Output Tracks", "Create or open a project first.")
            return
        try:
            project = self.store.build_carousel_script(self.project.project_dir)
        except ValueError as exc:
            messagebox.showerror("Output Tracks", str(exc))
            return

        current_block_id = self.selected_block_id
        self._load_project_into_ui(project, select_block_id=current_block_id)
        self._switch_view("Output Tracks")
        messagebox.showinfo("Output Tracks", "Carousel script was built and saved in the project package.")

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

