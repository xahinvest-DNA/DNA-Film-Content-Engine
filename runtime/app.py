from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from runtime.project_slice import ProjectSlice, ProjectSliceStore


class DNAFilmApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("DNA Film Content Engine - First MVP Slice")
        self.root.geometry("1280x780")

        self.workspace_root = Path.cwd() / "runtime_projects"
        self.workspace_root.mkdir(exist_ok=True)
        self.store = ProjectSliceStore(self.workspace_root)
        self.project: ProjectSlice | None = None

        self.current_view = tk.StringVar(value="Project Home")
        self.header_title = tk.StringVar(value="No project loaded")
        self.header_status = tk.StringVar(value="Create a project to begin the semantic-first flow.")
        self.next_action = tk.StringVar(value="Next action: Create project")
        self.summary_text = tk.StringVar(value="No semantic map yet.")
        self.placeholder_text = tk.StringVar(value="Available after semantic-map approval in a later bounded packet.")

        self.project_name_var = tk.StringVar()
        self.film_title_var = tk.StringVar()
        self.language_var = tk.StringVar(value="en")

        self._build_layout()
        self._switch_view("Project Home")

    def _build_layout(self) -> None:
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(1, weight=1)

        header = ttk.Frame(self.root, padding=12)
        header.grid(row=0, column=0, columnspan=3, sticky="nsew")
        header.columnconfigure(0, weight=1)
        ttk.Label(header, text="DNA Film Content Engine", font=("Segoe UI", 18, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(header, textvariable=self.header_title, font=("Segoe UI", 11, "bold")).grid(row=1, column=0, sticky="w")
        ttk.Label(header, textvariable=self.header_status, wraplength=900).grid(row=2, column=0, sticky="w")
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
        inspector.rowconfigure(1, weight=1)
        ttk.Label(inspector, text="Block Detail / Inspector", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, sticky="w")
        self.inspector_text = tk.Text(inspector, width=36, wrap="word")
        self.inspector_text.grid(row=1, column=0, sticky="nsew")
        self.inspector_text.insert("1.0", "Select a semantic block to inspect it here.")
        self.inspector_text.configure(state="disabled")

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
        ttk.Label(frame, textvariable=self.summary_text, wraplength=640).grid(row=6, column=0, columnspan=2, sticky="w", pady=(6, 0))
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
        frame.rowconfigure(1, weight=1)

        ttk.Label(frame, text="Semantic Map Workspace", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, sticky="w")
        self.semantic_list = tk.Listbox(frame, activestyle="none")
        self.semantic_list.grid(row=1, column=0, sticky="nsew", pady=(12, 12))
        self.semantic_list.bind("<<ListboxSelect>>", self.on_block_selected)
        ttk.Label(frame, textvariable=self.summary_text, wraplength=640).grid(row=2, column=0, sticky="w")
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
            self.semantic_list.selection_clear(0, "end")
            self.semantic_list.selection_set(0)
            self.semantic_list.event_generate("<<ListboxSelect>>")
        messagebox.showinfo("Semantic map ready", f"Saved analysis text and derived {len(project.semantic_blocks)} semantic blocks.")

    def on_block_selected(self, _event: object) -> None:
        if self.project is None:
            return
        selection = self.semantic_list.curselection()
        if not selection:
            return
        block = self.project.semantic_blocks[selection[0]]
        details = (
            f"Title: {block['title']}\n\n"
            f"Role: {block['semantic_role']}\n"
            f"Review state: {block['review_state']}\n"
            f"Sequence: {block['sequence']}\n\n"
            f"Content:\n{block['content']}\n\n"
            f"Output suitability:\n"
            f"- Long video: {block['output_suitability']['long_video']}\n"
            f"- Shorts/Reels: {block['output_suitability']['shorts_reels']}\n"
            f"- Carousel: {block['output_suitability']['carousel']}\n"
            f"- Packaging: {block['output_suitability']['packaging']}\n"
        )
        self.inspector_text.configure(state="normal")
        self.inspector_text.delete("1.0", "end")
        self.inspector_text.insert("1.0", details)
        self.inspector_text.configure(state="disabled")

    def _load_project_into_ui(self, project: ProjectSlice) -> None:
        self.project = project
        self.header_title.set(
            f"{project.project_record['title']} | {project.project_record.get('film_title') or 'Film title optional'} | {project.project_record['language']}"
        )
        self.header_status.set(project.project_record["current_readiness_summary"])
        self.next_action.set(self._next_action_label(project))
        warnings = project.intake_record.get("intake_warnings", [])
        warning_text = f"Warnings: {', '.join(warnings)}" if warnings else "Warnings: none"
        self.summary_text.set(
            f"Project status: {project.project_record['project_status']} | Intake: {project.intake_record['intake_readiness']} | Semantic blocks: {len(project.semantic_blocks)} | {warning_text}"
        )

        self.analysis_text.delete("1.0", "end")
        analysis_path = project.project_dir / "sources" / "analysis" / "analysis.txt"
        if analysis_path.exists():
            self.analysis_text.insert("1.0", analysis_path.read_text(encoding="utf-8"))

        self.semantic_list.delete(0, "end")
        for block in project.semantic_blocks:
            self.semantic_list.insert("end", f"{block['sequence']:02d}. {block['title']} [{block['semantic_role']}]")

        if not project.semantic_blocks:
            self.inspector_text.configure(state="normal")
            self.inspector_text.delete("1.0", "end")
            self.inspector_text.insert("1.0", "Select a semantic block to inspect it here.")
            self.inspector_text.configure(state="disabled")

    def _next_action_label(self, project: ProjectSlice) -> str:
        if not project.analysis_source_record:
            return "Next action: Load analysis text"
        if project.semantic_blocks:
            return "Next action: Review proposed blocks"
        return "Next action: Complete source intake"


def main() -> None:
    root = tk.Tk()
    ttk.Style().theme_use("clam")
    DNAFilmApp(root)
    root.minsize(1080, 680)
    root.mainloop()


if __name__ == "__main__":
    main()
