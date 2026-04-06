from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from runtime.project_slice import (
    ALLOWED_REVIEW_STATES,
    ALLOWED_SEMANTIC_ROLES,
    ProjectSlice,
    ProjectSliceStore,
)


class DNAFilmApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("DNA Film Content Engine - Semantic Review Workspace")
        self.root.geometry("1360x820")

        self.workspace_root = Path.cwd() / "runtime_projects"
        self.workspace_root.mkdir(exist_ok=True)
        self.store = ProjectSliceStore(self.workspace_root)
        self.project: ProjectSlice | None = None
        self.selected_block_id: str | None = None

        self.current_view = tk.StringVar(value="Project Home")
        self.header_title = tk.StringVar(value="No project loaded")
        self.header_status = tk.StringVar(value="Create a project to begin the semantic-first flow.")
        self.next_action = tk.StringVar(value="Next action: Create project")
        self.summary_text = tk.StringVar(value="No semantic map yet.")
        self.review_status_text = tk.StringVar(value="Semantic review: under_edit")
        self.placeholder_text = tk.StringVar(value="Available after semantic-map approval in a later bounded packet.")

        self.project_name_var = tk.StringVar()
        self.film_title_var = tk.StringVar()
        self.language_var = tk.StringVar(value="en")
        self.block_title_var = tk.StringVar()
        self.block_role_var = tk.StringVar(value=ALLOWED_SEMANTIC_ROLES[0])
        self.review_status_var = tk.StringVar(value=ALLOWED_REVIEW_STATES[0])
        self.block_status_var = tk.StringVar(value="Select a semantic block to inspect and edit it here.")

        self._build_layout()
        self._switch_view("Project Home")
        self._set_editor_enabled(False)

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
        inspector.rowconfigure(7, weight=1)
        ttk.Label(inspector, text="Block Detail / Inspector", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(inspector, textvariable=self.block_status_var, wraplength=320).grid(row=1, column=0, sticky="w", pady=(4, 10))
        ttk.Label(inspector, text="Title").grid(row=2, column=0, sticky="w")
        self.block_title_entry = ttk.Entry(inspector, textvariable=self.block_title_var, width=36)
        self.block_title_entry.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        ttk.Label(inspector, text="Semantic role").grid(row=4, column=0, sticky="w")
        self.block_role_combo = ttk.Combobox(inspector, textvariable=self.block_role_var, values=ALLOWED_SEMANTIC_ROLES, state="readonly")
        self.block_role_combo.grid(row=5, column=0, sticky="ew", pady=(0, 10))
        ttk.Label(inspector, text="Notes").grid(row=6, column=0, sticky="w")
        self.notes_text = tk.Text(inspector, height=8, wrap="word")
        self.notes_text.grid(row=7, column=0, sticky="nsew")
        ttk.Label(inspector, text="Full block text").grid(row=8, column=0, sticky="w", pady=(10, 0))
        self.content_text = tk.Text(inspector, height=10, wrap="word")
        self.content_text.grid(row=9, column=0, sticky="nsew", pady=(0, 10))
        self.content_text.configure(state="disabled")
        self.save_block_button = ttk.Button(inspector, text="Save Block Changes", command=self.save_selected_block)
        self.save_block_button.grid(row=10, column=0, sticky="ew")

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
        ttk.Label(toolbar, text="Project semantic review").pack(side="left")
        self.review_status_combo = ttk.Combobox(toolbar, textvariable=self.review_status_var, values=ALLOWED_REVIEW_STATES, state="readonly", width=18)
        self.review_status_combo.pack(side="left", padx=(8, 8))
        ttk.Button(toolbar, text="Save Review Status", command=self.save_review_status).pack(side="left")
        ttk.Label(toolbar, textvariable=self.review_status_text).pack(side="left", padx=(16, 0))

        self.semantic_list = tk.Listbox(frame, activestyle="none")
        self.semantic_list.grid(row=2, column=0, sticky="nsew", pady=(0, 12))
        self.semantic_list.bind("<<ListboxSelect>>", self.on_block_selected)
        ttk.Label(frame, textvariable=self.summary_text, wraplength=760).grid(row=3, column=0, sticky="w")
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
            return
        block = self.project.semantic_blocks[selection[0]]
        self._show_block(block)

    def save_selected_block(self) -> None:
        if self.project is None or self.selected_block_id is None:
            messagebox.showerror("Semantic map", "Select a semantic block first.")
            return
        notes = self.notes_text.get("1.0", "end").strip()
        try:
            project = self.store.update_semantic_block(
                self.project.project_dir,
                self.selected_block_id,
                self.block_title_var.get(),
                self.block_role_var.get(),
                notes,
            )
        except ValueError as exc:
            messagebox.showerror("Semantic map", str(exc))
            return
        self._load_project_into_ui(project, select_block_id=self.selected_block_id)
        self._switch_view("Semantic Map")
        self.block_status_var.set("Block changes saved to the local project package.")
        messagebox.showinfo("Semantic map", "Selected block changes were saved.")

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
        messagebox.showinfo("Semantic review", "Project-level semantic review status was saved.")

    def _load_project_into_ui(self, project: ProjectSlice, select_block_id: str | None = None) -> None:
        self.project = project
        self.header_title.set(
            f"{project.project_record['title']} | {project.project_record.get('film_title') or 'Film title optional'} | {project.project_record['language']}"
        )
        self.header_status.set(project.project_record["current_readiness_summary"])
        self.next_action.set(self._next_action_label(project))
        self.review_status_var.set(project.semantic_review_record["review_status"])
        self.review_status_text.set(
            f"Semantic review: {project.semantic_review_record['review_status']}"
        )
        warnings = project.intake_record.get("intake_warnings", [])
        warning_text = f"Warnings: {', '.join(warnings)}" if warnings else "Warnings: none"
        self.summary_text.set(
            f"Project status: {project.project_record['project_status']} | Intake: {project.intake_record['intake_readiness']} | Semantic blocks: {len(project.semantic_blocks)} | Review: {project.semantic_review_record['review_status']} | {warning_text}"
        )

        self.analysis_text.delete("1.0", "end")
        analysis_path = project.project_dir / "sources" / "analysis" / "analysis.txt"
        if analysis_path.exists():
            self.analysis_text.insert("1.0", analysis_path.read_text(encoding="utf-8"))

        self.semantic_list.delete(0, "end")
        for block in project.semantic_blocks:
            preview = block["content"][:72].replace("\n", " ")
            self.semantic_list.insert("end", f"{block['sequence']:02d}. {block['title']} [{block['semantic_role']}] - {preview}")

        if project.semantic_blocks:
            target_block_id = select_block_id or project.semantic_blocks[0]["record_id"]
            self._select_block_by_id(target_block_id)
        else:
            self.selected_block_id = None
            self.block_status_var.set("Select a semantic block to inspect and edit it here.")
            self._set_editor_enabled(False)
            self._clear_block_editor()

    def _show_block(self, block: dict) -> None:
        self.selected_block_id = block["record_id"]
        self.block_title_var.set(block["title"])
        self.block_role_var.set(block["semantic_role"])
        self.notes_text.delete("1.0", "end")
        self.notes_text.insert("1.0", block.get("notes", ""))
        self.content_text.configure(state="normal")
        self.content_text.delete("1.0", "end")
        self.content_text.insert("1.0", block["content"])
        self.content_text.configure(state="disabled")
        self.block_status_var.set(
            f"Editing {block['record_id']} | review state: {self.project.semantic_review_record['review_status']}"
        )
        self._set_editor_enabled(True)

    def _select_block_by_id(self, block_id: str) -> None:
        if self.project is None:
            return
        for index, block in enumerate(self.project.semantic_blocks):
            if block["record_id"] == block_id:
                self.semantic_list.selection_clear(0, "end")
                self.semantic_list.selection_set(index)
                self.semantic_list.activate(index)
                self._show_block(block)
                return
        self.semantic_list.selection_clear(0, "end")
        self.selected_block_id = None
        self._set_editor_enabled(False)

    def _set_editor_enabled(self, enabled: bool) -> None:
        entry_state = "normal" if enabled else "disabled"
        combo_state = "readonly" if enabled else "disabled"
        text_state = "normal" if enabled else "disabled"
        button_state = "normal" if enabled else "disabled"
        self.block_title_entry.configure(state=entry_state)
        self.block_role_combo.configure(state=combo_state)
        self.notes_text.configure(state=text_state)
        self.save_block_button.configure(state=button_state)

    def _clear_block_editor(self) -> None:
        self.block_title_var.set("")
        self.block_role_var.set(ALLOWED_SEMANTIC_ROLES[0])
        self.notes_text.configure(state="normal")
        self.notes_text.delete("1.0", "end")
        self.notes_text.configure(state="disabled")
        self.content_text.configure(state="normal")
        self.content_text.delete("1.0", "end")
        self.content_text.insert("1.0", "Select a semantic block to inspect it here.")
        self.content_text.configure(state="disabled")

    def _next_action_label(self, project: ProjectSlice) -> str:
        if not project.analysis_source_record:
            return "Next action: Load analysis text"
        review_status = project.semantic_review_record["review_status"]
        if review_status == "approved":
            return "Next action: Matching prep will unlock in a later packet"
        if review_status == "ready_for_review":
            return "Next action: Approve semantic map"
        return "Next action: Review and refine semantic blocks"


def main() -> None:
    root = tk.Tk()
    ttk.Style().theme_use("clam")
    DNAFilmApp(root)
    root.minsize(1160, 720)
    root.mainloop()


if __name__ == "__main__":
    main()
