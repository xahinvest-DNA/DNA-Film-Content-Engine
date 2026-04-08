from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from runtime.project_slice import (
    ALLOWED_OUTPUT_SUITABILITY,
    ALLOWED_REVIEW_STATES,
    ALLOWED_SEMANTIC_ROLES,
    ProjectSlice,
    ProjectSliceStore,
    describe_warning_flags,
    semantic_completeness,
    split_sentences,
)


FOCUS_MODES = (
    "All blocks",
    "Issues present",
    "Review-ready",
    "Long video focus",
    "Shorts/reels focus",
    "Carousel focus",
    "Packaging focus",
)

FOCUS_TO_SUITABILITY_KEY = {
    "Long video focus": "long_video",
    "Shorts/reels focus": "shorts_reels",
    "Carousel focus": "carousel",
    "Packaging focus": "packaging",
}


class DNAFilmApp:
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
        self.focus_position_text = tk.StringVar(value="Focused item: 0 of 0")
        self.previous_context_text = tk.StringVar(value="Previous: No previous semantic block")
        self.next_context_text = tk.StringVar(value="Next: No next semantic block")
        self.approval_message_text = tk.StringVar(value="Approval message: Semantic map remains under edit.")
        self.approval_reason_text = tk.StringVar(value="Approval reason: Approve is blocked until semantic review is moved to ready_for_review.")
        self.reopen_text = tk.StringVar(value="Reopen state: none")
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

        self._build_layout()
        self._switch_view("Project Home")
        self._set_editor_enabled(False)
        self._set_structure_enabled(False, False, False, False, False)
        self._set_focus_navigation_enabled(False, False)

    def _build_layout(self) -> None:
        self.root.columnconfigure(1, weight=1)
        self.root.columnconfigure(2, weight=0)
        self.root.rowconfigure(1, weight=1)

        header = ttk.Frame(self.root, padding=12)
        header.grid(row=0, column=0, columnspan=3, sticky="nsew")
        header.columnconfigure(0, weight=1)
        ttk.Label(header, text="DNA Film Content Engine", font=("Segoe UI", 18, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(header, textvariable=self.header_title, font=("Segoe UI", 11, "bold")).grid(row=1, column=0, sticky="w")
        ttk.Label(header, textvariable=self.header_status, wraplength=980).grid(row=2, column=0, sticky="w")
        ttk.Label(header, textvariable=self.next_action, foreground="#0b5cad").grid(row=3, column=0, sticky="w")
        ttk.Label(header, textvariable=self.completeness_text).grid(row=4, column=0, sticky="w")
        ttk.Label(header, textvariable=self.issues_summary_text, wraplength=980).grid(row=5, column=0, sticky="w")
        ttk.Label(header, textvariable=self.readiness_text).grid(row=6, column=0, sticky="w")
        ttk.Label(header, textvariable=self.approval_message_text, wraplength=980).grid(row=7, column=0, sticky="w")
        ttk.Label(header, textvariable=self.approval_reason_text, wraplength=980).grid(row=8, column=0, sticky="w")
        ttk.Label(header, textvariable=self.reopen_text, wraplength=980).grid(row=9, column=0, sticky="w")

        nav = ttk.Frame(self.root, padding=(12, 8))
        nav.grid(row=1, column=0, sticky="nsw")
        for name in ("Project Home", "Source Intake", "Semantic Map"):
            ttk.Button(nav, text=name, width=22, command=lambda item=name: self._switch_view(item)).pack(anchor="w", pady=4)
        for name in ("Matching Prep", "Output Tracks", "Export Center"):
            ttk.Button(nav, text=name, width=22, state="disabled").pack(anchor="w", pady=4)

        main = ttk.Frame(self.root, padding=12)
        main.grid(row=1, column=1, sticky="nsew")
        main.columnconfigure(0, weight=1)
        main.rowconfigure(0, weight=1)

        inspector = ttk.Frame(self.root, padding=12)
        inspector.grid(row=1, column=2, sticky="nsew")
        inspector.columnconfigure(0, weight=1)
        inspector.rowconfigure(17, weight=1)
        ttk.Label(inspector, text="Block Detail / Inspector", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(inspector, textvariable=self.block_status_var, wraplength=320).grid(row=1, column=0, sticky="w", pady=(4, 6))
        ttk.Label(inspector, textvariable=self.block_issues_text, wraplength=320).grid(row=2, column=0, sticky="w", pady=(0, 8))
        context_frame = ttk.LabelFrame(inspector, text="Adjacent semantic context", padding=8)
        context_frame.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        context_frame.columnconfigure(0, weight=1)
        ttk.Label(context_frame, textvariable=self.previous_context_text, wraplength=320, justify="left").grid(row=0, column=0, sticky="w")
        ttk.Label(context_frame, textvariable=self.next_context_text, wraplength=320, justify="left").grid(row=1, column=0, sticky="w", pady=(8, 0))

        order_controls = ttk.Frame(inspector)
        order_controls.grid(row=4, column=0, sticky="ew", pady=(0, 8))
        self.move_up_button = ttk.Button(order_controls, text="Move Up", command=lambda: self.reorder_selected_block("up"))
        self.move_up_button.pack(side="left")
        self.move_down_button = ttk.Button(order_controls, text="Move Down", command=lambda: self.reorder_selected_block("down"))
        self.move_down_button.pack(side="left", padx=(8, 0))

        merge_controls = ttk.Frame(inspector)
        merge_controls.grid(row=5, column=0, sticky="ew", pady=(0, 8))
        self.merge_up_button = ttk.Button(merge_controls, text="Merge Up", command=lambda: self.merge_selected_block("up"))
        self.merge_up_button.pack(side="left")
        self.merge_down_button = ttk.Button(merge_controls, text="Merge Down", command=lambda: self.merge_selected_block("down"))
        self.merge_down_button.pack(side="left", padx=(8, 0))

        ttk.Label(inspector, text="Split after sentence #").grid(row=6, column=0, sticky="w")
        split_controls = ttk.Frame(inspector)
        split_controls.grid(row=7, column=0, sticky="ew", pady=(0, 10))
        self.split_sentence_entry = ttk.Entry(split_controls, textvariable=self.split_sentence_var, width=8)
        self.split_sentence_entry.pack(side="left")
        self.split_button = ttk.Button(split_controls, text="Split Block", command=self.split_selected_block)
        self.split_button.pack(side="left", padx=(8, 0))

        ttk.Label(inspector, text="Title").grid(row=8, column=0, sticky="w")
        self.block_title_entry = ttk.Entry(inspector, textvariable=self.block_title_var, width=36)
        self.block_title_entry.grid(row=9, column=0, sticky="ew", pady=(0, 10))
        ttk.Label(inspector, text="Semantic role").grid(row=10, column=0, sticky="w")
        self.block_role_combo = ttk.Combobox(inspector, textvariable=self.block_role_var, values=ALLOWED_SEMANTIC_ROLES, state="readonly")
        self.block_role_combo.grid(row=11, column=0, sticky="ew", pady=(0, 10))
        ttk.Label(inspector, text="Notes").grid(row=12, column=0, sticky="w")
        self.notes_text = tk.Text(inspector, height=6, wrap="word")
        self.notes_text.grid(row=13, column=0, sticky="nsew")
        ttk.Label(inspector, text="Output suitability").grid(row=14, column=0, sticky="w", pady=(10, 0))
        suitability = ttk.Frame(inspector)
        suitability.grid(row=15, column=0, sticky="ew", pady=(4, 10))
        suitability.columnconfigure(1, weight=1)
        suitability.columnconfigure(3, weight=1)
        ttk.Label(suitability, text="Long video").grid(row=0, column=0, sticky="w")
        self.long_video_combo = ttk.Combobox(suitability, textvariable=self.long_video_var, values=ALLOWED_OUTPUT_SUITABILITY, state="readonly")
        self.long_video_combo.grid(row=0, column=1, sticky="ew", padx=(8, 12))
        ttk.Label(suitability, text="Shorts/reels").grid(row=0, column=2, sticky="w")
        self.shorts_reels_combo = ttk.Combobox(suitability, textvariable=self.shorts_reels_var, values=ALLOWED_OUTPUT_SUITABILITY, state="readonly")
        self.shorts_reels_combo.grid(row=0, column=3, sticky="ew")
        ttk.Label(suitability, text="Carousel").grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.carousel_combo = ttk.Combobox(suitability, textvariable=self.carousel_var, values=ALLOWED_OUTPUT_SUITABILITY, state="readonly")
        self.carousel_combo.grid(row=1, column=1, sticky="ew", padx=(8, 12), pady=(8, 0))
        ttk.Label(suitability, text="Packaging").grid(row=1, column=2, sticky="w", pady=(8, 0))
        self.packaging_combo = ttk.Combobox(suitability, textvariable=self.packaging_var, values=ALLOWED_OUTPUT_SUITABILITY, state="readonly")
        self.packaging_combo.grid(row=1, column=3, sticky="ew", pady=(8, 0))
        ttk.Label(inspector, text="Full block text").grid(row=16, column=0, sticky="w", pady=(10, 0))
        self.content_text = tk.Text(inspector, height=8, wrap="word")
        self.content_text.grid(row=17, column=0, sticky="nsew", pady=(0, 10))
        self.content_text.configure(state="disabled")
        self.save_block_button = ttk.Button(inspector, text="Save Block Review", command=self.save_selected_block)
        self.save_block_button.grid(row=18, column=0, sticky="ew")

        self.views: dict[str, ttk.Frame] = {}
        self.views["Project Home"] = self._build_home_view(main)
        self.views["Source Intake"] = self._build_intake_view(main)
        self.views["Semantic Map"] = self._build_semantic_view(main)

        self.placeholder_view = ttk.Frame(main, padding=12)
        self.placeholder_view.grid(row=0, column=0, sticky="nsew")
        ttk.Label(self.placeholder_view, text="Later-phase placeholder", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        ttk.Label(self.placeholder_view, textvariable=self.placeholder_text, wraplength=540).pack(anchor="w", pady=(8, 0))

    def _build_home_view(self, parent: ttk.Frame) -> ttk.Frame:
        frame = ttk.Frame(parent, padding=12)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="Project Home", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Label(frame, text="Project title").grid(row=1, column=0, sticky="w", pady=(12, 0))
        ttk.Entry(frame, textvariable=self.project_name_var, width=40).grid(row=1, column=1, sticky="ew", pady=(12, 0))
        ttk.Label(frame, text="Film title").grid(row=2, column=0, sticky="w", pady=(8, 0))
        ttk.Entry(frame, textvariable=self.film_title_var, width=40).grid(row=2, column=1, sticky="ew", pady=(8, 0))
        ttk.Label(frame, text="Language").grid(row=3, column=0, sticky="w", pady=(8, 0))
        ttk.Entry(frame, textvariable=self.language_var, width=12).grid(row=3, column=1, sticky="w", pady=(8, 0))

        actions = ttk.Frame(frame)
        actions.grid(row=4, column=0, columnspan=2, sticky="w", pady=16)
        ttk.Button(actions, text="Create Project", command=self.create_project).pack(side="left")
        ttk.Button(actions, text="Open Existing Project", command=self.open_project).pack(side="left", padx=(8, 0))

        ttk.Label(frame, text="Readiness overview", font=("Segoe UI", 11, "bold")).grid(row=5, column=0, columnspan=2, sticky="w")
        ttk.Label(frame, textvariable=self.summary_text, wraplength=700).grid(row=6, column=0, columnspan=2, sticky="w", pady=(6, 0))
        ttk.Label(frame, textvariable=self.review_status_text, wraplength=700).grid(row=7, column=0, columnspan=2, sticky="w", pady=(8, 0))
        ttk.Label(frame, textvariable=self.completeness_text, wraplength=700).grid(row=8, column=0, columnspan=2, sticky="w", pady=(4, 0))
        ttk.Label(frame, textvariable=self.issues_summary_text, wraplength=700).grid(row=9, column=0, columnspan=2, sticky="w", pady=(4, 0))
        ttk.Label(frame, textvariable=self.readiness_text, wraplength=700).grid(row=10, column=0, columnspan=2, sticky="w", pady=(4, 0))
        ttk.Label(frame, textvariable=self.approval_message_text, wraplength=700).grid(row=11, column=0, columnspan=2, sticky="w", pady=(4, 0))
        ttk.Label(frame, textvariable=self.approval_reason_text, wraplength=700).grid(row=12, column=0, columnspan=2, sticky="w", pady=(4, 0))
        ttk.Label(frame, textvariable=self.reopen_text, wraplength=700).grid(row=13, column=0, columnspan=2, sticky="w", pady=(4, 0))
        return frame

    def _build_intake_view(self, parent: ttk.Frame) -> ttk.Frame:
        frame = ttk.Frame(parent, padding=12)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        ttk.Label(frame, text="Source Intake", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, sticky="w")
        self.analysis_text = tk.Text(frame, wrap="word")
        self.analysis_text.grid(row=1, column=0, sticky="nsew", pady=(12, 12))
        ttk.Button(frame, text="Save Analysis Text and Derive Semantic Blocks", command=self.save_analysis_text).grid(row=2, column=0, sticky="w")
        return frame

    def _build_semantic_view(self, parent: ttk.Frame) -> ttk.Frame:
        frame = ttk.Frame(parent, padding=12)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(2, weight=1)

        ttk.Label(frame, text="Semantic Map Workspace", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, sticky="w")
        toolbar = ttk.Frame(frame)
        toolbar.grid(row=1, column=0, sticky="ew", pady=(10, 10))
        ttk.Label(toolbar, text="Focus").pack(side="left")
        self.focus_mode_combo = ttk.Combobox(toolbar, textvariable=self.focus_mode_var, values=FOCUS_MODES, state="readonly", width=20)
        self.focus_mode_combo.pack(side="left", padx=(8, 8))
        self.focus_mode_combo.bind("<<ComboboxSelected>>", self.apply_focus_mode)
        self.previous_focus_button = ttk.Button(toolbar, text="Previous", command=lambda: self.navigate_focus("previous"))
        self.previous_focus_button.pack(side="left", padx=(8, 0))
        self.next_focus_button = ttk.Button(toolbar, text="Next", command=lambda: self.navigate_focus("next"))
        self.next_focus_button.pack(side="left", padx=(8, 16))
        ttk.Label(toolbar, textvariable=self.focus_position_text).pack(side="left", padx=(0, 16))
        ttk.Label(toolbar, text="Project semantic review").pack(side="left")
        self.review_status_combo = ttk.Combobox(toolbar, textvariable=self.review_status_var, values=ALLOWED_REVIEW_STATES, state="readonly", width=18)
        self.review_status_combo.pack(side="left", padx=(8, 8))
        ttk.Button(toolbar, text="Save Review Status", command=self.save_review_status).pack(side="left")
        ttk.Label(toolbar, textvariable=self.review_status_text).pack(side="left", padx=(16, 0))
        ttk.Label(toolbar, textvariable=self.completeness_text).pack(side="left", padx=(16, 0))
        ttk.Label(toolbar, textvariable=self.readiness_text).pack(side="left", padx=(16, 0))

        self.semantic_list = tk.Listbox(frame, activestyle="none")
        self.semantic_list.grid(row=2, column=0, sticky="nsew", pady=(0, 12))
        self.semantic_list.bind("<<ListboxSelect>>", self.on_block_selected)
        ttk.Label(frame, textvariable=self.focus_status_text, wraplength=760).grid(row=3, column=0, sticky="w")
        ttk.Label(frame, textvariable=self.summary_text, wraplength=760).grid(row=4, column=0, sticky="w")
        ttk.Label(frame, textvariable=self.issues_summary_text, wraplength=760).grid(row=5, column=0, sticky="w")
        ttk.Label(frame, textvariable=self.approval_message_text, wraplength=760).grid(row=6, column=0, sticky="w")
        ttk.Label(frame, textvariable=self.approval_reason_text, wraplength=760).grid(row=7, column=0, sticky="w")
        ttk.Label(frame, textvariable=self.reopen_text, wraplength=760).grid(row=8, column=0, sticky="w")
        return frame

    def _switch_view(self, name: str) -> None:
        self.current_view.set(name)
        for frame in list(self.views.values()) + [self.placeholder_view]:
            frame.grid_remove()
        self.views.get(name, self.placeholder_view).grid()

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
        warnings = project.intake_record.get("intake_warnings", [])
        warning_text = f"Warnings: {', '.join(warnings)}" if warnings else "Warnings: none"
        suitability_summary = self._project_suitability_summary(project)
        self.summary_text.set(
            f"Project status: {project.project_record['project_status']} | Intake: {project.intake_record['intake_readiness']} | Semantic blocks: {len(project.semantic_blocks)} | Review: {project.semantic_review_record['review_status']} | Completeness: {completeness_label} | Readiness: {readiness} | Suitability: {suitability_summary} | {warning_text}"
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
            self.previous_context_text.set("Previous: No previous semantic block")
            self.next_context_text.set("Next: No next semantic block")
            self._set_editor_enabled(False)
            self._set_structure_enabled(False, False, False, False, False)
            self._set_focus_navigation_enabled(False, False)
            self._clear_block_editor()

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
        if review_status == "approved":
            return "Next action: Matching prep will unlock in a later packet"
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
