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
)
from runtime.ui.constants import APP_VIEWS


class DNAFilmApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("DNA Film Content Engine - F-006A Desktop Slice")
        self.root.geometry("1280x820")

        self.workspace_root = Path.cwd() / "runtime_projects"
        self.workspace_root.mkdir(parents=True, exist_ok=True)
        self.store = ProjectSliceStore(self.workspace_root)
        self.project: ProjectSlice | None = None
        self.selected_block_id: str | None = None
        self.current_source_label = "analysis.txt"

        self.header_title = tk.StringVar(value="No project loaded")
        self.header_status = tk.StringVar(value="Create a project to begin the first local-first desktop slice.")
        self.next_action = tk.StringVar(value="Next action: Create project")
        self.package_path_text = tk.StringVar(value="Project package: not created yet")
        self.project_summary_text = tk.StringVar(value="Project status: no project loaded")
        self.source_status_text = tk.StringVar(value="Source status: no primary analysis source loaded")
        self.semantic_status_text = tk.StringVar(value="Semantic status: no semantic blocks yet")
        self.block_status_text = tk.StringVar(value="Select a semantic block to inspect it here.")

        self.project_name_var = tk.StringVar()
        self.film_title_var = tk.StringVar()
        self.language_var = tk.StringVar(value="en")
        self.review_status_var = tk.StringVar(value=ALLOWED_REVIEW_STATES[0])
        self.block_title_var = tk.StringVar()
        self.block_role_var = tk.StringVar(value=ALLOWED_SEMANTIC_ROLES[0])
        self.block_suitability_var = tk.StringVar(value=ALLOWED_OUTPUT_SUITABILITY[0])

        self.views: dict[str, ttk.Frame] = {}

        self._build_layout()
        self._switch_view("Project Home")
        self._set_block_editor_enabled(False)
        self._set_review_controls_enabled(False)

    def _build_layout(self) -> None:
        self.root.columnconfigure(1, weight=1)
        self.root.columnconfigure(2, weight=0)
        self.root.rowconfigure(1, weight=1)

        header = ttk.Frame(self.root, padding=12)
        header.grid(row=0, column=0, columnspan=3, sticky="nsew")
        header.columnconfigure(0, weight=1)
        ttk.Label(header, text="DNA Film Content Engine", font=("Segoe UI", 18, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(header, textvariable=self.header_title, font=("Segoe UI", 11, "bold")).grid(row=1, column=0, sticky="w")
        ttk.Label(header, textvariable=self.header_status, wraplength=980).grid(row=2, column=0, sticky="w", pady=(4, 0))
        ttk.Label(header, textvariable=self.next_action, foreground="#0b5cad").grid(row=3, column=0, sticky="w", pady=(4, 0))
        ttk.Label(header, textvariable=self.package_path_text, wraplength=980).grid(row=4, column=0, sticky="w", pady=(4, 0))

        nav = ttk.Frame(self.root, padding=(12, 8))
        nav.grid(row=1, column=0, sticky="nsw")
        for view_name in APP_VIEWS:
            ttk.Button(nav, text=view_name, width=22, command=lambda item=view_name: self._switch_view(item)).pack(anchor="w", pady=4)

        main = ttk.Frame(self.root, padding=12)
        main.grid(row=1, column=1, sticky="nsew")
        main.columnconfigure(0, weight=1)
        main.rowconfigure(0, weight=1)

        inspector = ttk.Frame(self.root, padding=12)
        inspector.grid(row=1, column=2, sticky="nsew")
        inspector.columnconfigure(0, weight=1)
        inspector.rowconfigure(8, weight=1)
        ttk.Label(inspector, text="Semantic Block Inspector", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(inspector, textvariable=self.block_status_text, wraplength=320).grid(row=1, column=0, sticky="w", pady=(6, 10))
        ttk.Label(inspector, text="Title").grid(row=2, column=0, sticky="w")
        self.block_title_entry = ttk.Entry(inspector, textvariable=self.block_title_var, width=36)
        self.block_title_entry.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        ttk.Label(inspector, text="Role").grid(row=4, column=0, sticky="w")
        self.block_role_combo = ttk.Combobox(inspector, textvariable=self.block_role_var, values=ALLOWED_SEMANTIC_ROLES, state="readonly")
        self.block_role_combo.grid(row=5, column=0, sticky="ew", pady=(0, 10))
        ttk.Label(inspector, text="Output suitability").grid(row=6, column=0, sticky="w")
        self.block_suitability_combo = ttk.Combobox(
            inspector,
            textvariable=self.block_suitability_var,
            values=ALLOWED_OUTPUT_SUITABILITY,
            state="readonly",
        )
        self.block_suitability_combo.grid(row=7, column=0, sticky="ew", pady=(0, 10))
        ttk.Label(inspector, text="Notes").grid(row=8, column=0, sticky="w")
        self.notes_text = tk.Text(inspector, height=8, wrap="word")
        self.notes_text.grid(row=9, column=0, sticky="nsew", pady=(0, 10))
        ttk.Label(inspector, text="Block content").grid(row=10, column=0, sticky="w")
        self.content_text = tk.Text(inspector, height=10, wrap="word")
        self.content_text.grid(row=11, column=0, sticky="nsew", pady=(0, 10))
        self.content_text.configure(state="disabled")
        self.save_block_button = ttk.Button(inspector, text="Save Block Changes", command=self.save_selected_block)
        self.save_block_button.grid(row=12, column=0, sticky="ew")

        self.views["Project Home"] = self._build_home_view(main)
        self.views["Source Intake"] = self._build_intake_view(main)
        self.views["Semantic Map"] = self._build_semantic_view(main)

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
        ttk.Entry(frame, textvariable=self.language_var, width=16).grid(row=3, column=1, sticky="w", pady=(8, 0))

        actions = ttk.Frame(frame)
        actions.grid(row=4, column=0, columnspan=2, sticky="w", pady=16)
        ttk.Button(actions, text="Create Project", command=self.create_project).pack(side="left")
        ttk.Button(actions, text="Open Existing Project", command=self.open_project).pack(side="left", padx=(8, 0))

        ttk.Label(frame, text="Current project state", font=("Segoe UI", 11, "bold")).grid(row=5, column=0, columnspan=2, sticky="w")
        ttk.Label(frame, textvariable=self.project_summary_text, wraplength=760).grid(row=6, column=0, columnspan=2, sticky="w", pady=(6, 0))
        ttk.Label(frame, textvariable=self.source_status_text, wraplength=760).grid(row=7, column=0, columnspan=2, sticky="w", pady=(6, 0))
        ttk.Label(frame, textvariable=self.semantic_status_text, wraplength=760).grid(row=8, column=0, columnspan=2, sticky="w", pady=(6, 0))
        return frame

    def _build_intake_view(self, parent: ttk.Frame) -> ttk.Frame:
        frame = ttk.Frame(parent, padding=12)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(2, weight=1)

        ttk.Label(frame, text="Source Intake", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(frame, textvariable=self.source_status_text, wraplength=760).grid(row=1, column=0, sticky="w", pady=(6, 10))
        self.analysis_text = tk.Text(frame, wrap="word")
        self.analysis_text.grid(row=2, column=0, sticky="nsew", pady=(0, 12))
        actions = ttk.Frame(frame)
        actions.grid(row=3, column=0, sticky="w")
        ttk.Button(actions, text="Load Text File", command=self.load_source_file).pack(side="left")
        ttk.Button(actions, text="Save Source and Create Provisional Semantic Blocks", command=self.save_analysis_text).pack(side="left", padx=(8, 0))
        return frame

    def _build_semantic_view(self, parent: ttk.Frame) -> ttk.Frame:
        frame = ttk.Frame(parent, padding=12)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(2, weight=1)

        ttk.Label(frame, text="Semantic Map Workspace", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, sticky="w")
        controls = ttk.Frame(frame)
        controls.grid(row=1, column=0, sticky="ew", pady=(10, 10))
        ttk.Label(controls, textvariable=self.semantic_status_text).pack(side="left")
        ttk.Label(controls, text="Review state").pack(side="left", padx=(20, 8))
        self.review_status_combo = ttk.Combobox(
            controls,
            textvariable=self.review_status_var,
            values=ALLOWED_REVIEW_STATES,
            state="readonly",
            width=18,
        )
        self.review_status_combo.pack(side="left")
        self.save_review_button = ttk.Button(controls, text="Save Review State", command=self.save_review_status)
        self.save_review_button.pack(side="left", padx=(8, 0))

        self.semantic_list = tk.Listbox(frame, activestyle="none")
        self.semantic_list.grid(row=2, column=0, sticky="nsew")
        self.semantic_list.bind("<<ListboxSelect>>", self.on_block_selected)
        return frame

    def _switch_view(self, name: str) -> None:
        for frame in self.views.values():
            frame.grid_remove()
        self.views[name].grid()

    def create_project(self) -> None:
        try:
            project = self.store.create_project(
                self.project_name_var.get(),
                film_title=self.film_title_var.get(),
                language=self.language_var.get(),
            )
        except ValueError as exc:
            messagebox.showerror("Project creation", str(exc))
            return
        except FileExistsError:
            messagebox.showerror("Project creation", "A project package with the same generated name already exists.")
            return

        self.current_source_label = "analysis.txt"
        self._load_project_into_ui(project)
        self._switch_view("Source Intake")
        messagebox.showinfo("Project created", f"Project package created at:\n{project.project_dir}")

    def open_project(self) -> None:
        selected = filedialog.askdirectory(initialdir=self.workspace_root, title="Open DNA project package")
        if not selected:
            return
        self.load_project_from_path(Path(selected))

    def load_project_from_path(self, project_dir: Path) -> None:
        try:
            project = self.store.load_project(project_dir)
        except FileNotFoundError:
            messagebox.showerror("Open project", "Selected folder does not look like a DNA project package.")
            return
        self._load_project_into_ui(project)
        self._switch_view("Project Home")

    def load_source_file(self) -> None:
        selected = filedialog.askopenfilename(
            initialdir=self.workspace_root,
            title="Load analysis text",
            filetypes=(("Text files", "*.txt *.md"), ("All files", "*.*")),
        )
        if not selected:
            return
        path = Path(selected)
        self.current_source_label = path.name
        self.analysis_text.delete("1.0", "end")
        self.analysis_text.insert("1.0", path.read_text(encoding="utf-8"))
        self.source_status_text.set(f"Source status: loaded text from {path.name} and waiting to save it into the project package.")

    def save_analysis_text(self) -> None:
        if self.project is None:
            messagebox.showerror("Source intake", "Create or open a project first.")
            return
        text = self.analysis_text.get("1.0", "end")
        try:
            project = self.store.save_analysis_text(self.project.project_dir, text, self.current_source_label)
        except ValueError as exc:
            messagebox.showerror("Source intake", str(exc))
            return

        self._load_project_into_ui(project, select_block_id=project.semantic_blocks[0]["record_id"] if project.semantic_blocks else None)
        self._switch_view("Semantic Map")
        messagebox.showinfo("Semantic map ready", f"Saved source and created {len(project.semantic_blocks)} provisional semantic blocks.")

    def save_review_status(self) -> None:
        if self.project is None:
            messagebox.showerror("Semantic review", "Create or open a project first.")
            return
        try:
            project = self.store.update_semantic_review_status(self.project.project_dir, self.review_status_var.get())
        except ValueError as exc:
            messagebox.showerror("Semantic review", str(exc))
            return
        self._load_project_into_ui(project, select_block_id=self.selected_block_id)
        self._switch_view("Semantic Map")
        messagebox.showinfo("Semantic review", "Semantic review state was saved.")

    def on_block_selected(self, _event: object | None = None) -> None:
        if self.project is None:
            return
        selection = self.semantic_list.curselection()
        if not selection:
            self.selected_block_id = None
            self._clear_block_editor()
            self._set_block_editor_enabled(False)
            return
        block = self.project.semantic_blocks[selection[0]]
        self._show_block(block)

    def save_selected_block(self) -> None:
        if self.project is None or self.selected_block_id is None:
            messagebox.showerror("Semantic Map", "Select a semantic block first.")
            return
        try:
            project = self.store.update_semantic_block(
                self.project.project_dir,
                self.selected_block_id,
                self.block_title_var.get(),
                self.block_role_var.get(),
                self.notes_text.get("1.0", "end").strip(),
                self.block_suitability_var.get(),
            )
        except ValueError as exc:
            messagebox.showerror("Semantic Map", str(exc))
            return
        self._load_project_into_ui(project, select_block_id=self.selected_block_id)
        self._switch_view("Semantic Map")
        self.block_status_text.set("Selected semantic block was saved to the local project package.")
        messagebox.showinfo("Semantic Map", "Selected semantic block changes were saved.")

    def _load_project_into_ui(self, project: ProjectSlice, select_block_id: str | None = None) -> None:
        self.project = project
        self.header_title.set(
            f"{project.project_record['title']} | {project.project_record.get('film_title') or 'Film title optional'} | {project.project_record.get('language', 'en')}"
        )
        self.header_status.set(project.project_record["current_readiness_summary"])
        self.next_action.set(self._next_action_label(project))
        self.package_path_text.set(f"Project package: {project.project_dir}")
        self.project_summary_text.set(
            f"Project status: {project.project_record['project_status']} | Intake: {project.intake_record['intake_readiness']} | Last saved: {project.status_record['last_saved_at']}"
        )
        self.source_status_text.set(self._source_status_label(project))
        self.semantic_status_text.set(
            f"Semantic status: {len(project.semantic_blocks)} block(s) | Review state: {project.semantic_review_record['review_status']} | Edit state: {project.status_record['current_edit_state']}"
        )
        self.review_status_var.set(project.semantic_review_record["review_status"])
        self._set_review_controls_enabled(bool(project.semantic_blocks))

        self.analysis_text.delete("1.0", "end")
        if project.analysis_source_record is not None:
            self.current_source_label = project.analysis_source_record["source_label"]
            self.analysis_text.insert("1.0", self.store.read_analysis_text(project.project_dir))
        else:
            self.current_source_label = "analysis.txt"

        self._refresh_semantic_list(select_block_id)

    def _refresh_semantic_list(self, select_block_id: str | None = None) -> None:
        self.semantic_list.delete(0, "end")
        if self.project is None or not self.project.semantic_blocks:
            self.selected_block_id = None
            self._clear_block_editor()
            self._set_block_editor_enabled(False)
            return

        for block in self.project.semantic_blocks:
            self.semantic_list.insert(
                "end",
                f"{block['sequence']:02d}. {block['title']} [{block['semantic_role']}] | suitability: {block['output_suitability']}",
            )

        target_id = select_block_id or self.selected_block_id or self.project.semantic_blocks[0]["record_id"]
        for index, block in enumerate(self.project.semantic_blocks):
            if block["record_id"] == target_id:
                self.semantic_list.selection_clear(0, "end")
                self.semantic_list.selection_set(index)
                self.semantic_list.activate(index)
                self._show_block(block)
                return

    def _show_block(self, block: dict) -> None:
        self.selected_block_id = block["record_id"]
        self.block_title_var.set(block["title"])
        self.block_role_var.set(block["semantic_role"])
        self.block_suitability_var.set(block["output_suitability"])
        self.notes_text.delete("1.0", "end")
        self.notes_text.insert("1.0", block.get("notes", ""))
        self.content_text.configure(state="normal")
        self.content_text.delete("1.0", "end")
        self.content_text.insert("1.0", block["content"])
        self.content_text.configure(state="disabled")
        self.block_status_text.set(
            f"{block['record_id']} | sequence {block['sequence']} | role {block['semantic_role']} | review {self.project.semantic_review_record['review_status']}"
        )
        self._set_block_editor_enabled(True)

    def _clear_block_editor(self) -> None:
        self.block_title_var.set("")
        self.block_role_var.set(ALLOWED_SEMANTIC_ROLES[0])
        self.block_suitability_var.set(ALLOWED_OUTPUT_SUITABILITY[0])
        self.notes_text.delete("1.0", "end")
        self.content_text.configure(state="normal")
        self.content_text.delete("1.0", "end")
        self.content_text.configure(state="disabled")
        self.block_status_text.set("Select a semantic block to inspect it here.")

    def _set_block_editor_enabled(self, enabled: bool) -> None:
        entry_state = "normal" if enabled else "disabled"
        combo_state = "readonly" if enabled else "disabled"
        text_state = "normal" if enabled else "disabled"
        button_state = "normal" if enabled else "disabled"
        self.block_title_entry.configure(state=entry_state)
        self.block_role_combo.configure(state=combo_state)
        self.block_suitability_combo.configure(state=combo_state)
        self.notes_text.configure(state=text_state)
        self.save_block_button.configure(state=button_state)

    def _set_review_controls_enabled(self, enabled: bool) -> None:
        self.review_status_combo.configure(state="readonly" if enabled else "disabled")
        self.save_review_button.configure(state="normal" if enabled else "disabled")

    def _source_status_label(self, project: ProjectSlice) -> str:
        source = project.analysis_source_record
        if source is None:
            return "Source status: no primary analysis source loaded"
        return (
            f"Source status: primary analysis source saved as {source['source_label']} | "
            f"{source['text_char_count']} chars | canonical record stored"
        )

    def _next_action_label(self, project: ProjectSlice) -> str:
        if project.analysis_source_record is None:
            return "Next action: Load analysis text"
        if not project.semantic_blocks:
            return "Next action: Generate provisional semantic blocks"
        if project.semantic_review_record["review_status"] == "approved":
            return "Next action: Reopen or continue inspecting the Semantic Map"
        if project.semantic_review_record["review_status"] == "ready_for_review":
            return "Next action: Review and approve the semantic map"
        return "Next action: Inspect and edit semantic blocks"
