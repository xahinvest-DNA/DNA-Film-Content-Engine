from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from runtime.project_slice import (
    ALLOWED_CANDIDATE_REVIEW_STATUSES,
    ALLOWED_MATCHING_ASSET_TYPES,
    ALLOWED_OUTPUT_SUITABILITY,
    ALLOWED_REVIEW_STATES,
    ALLOWED_SEMANTIC_ROLES,
)
from runtime.ui.constants import CANDIDATE_STATUS_FOCUS_OPTIONS, FOCUS_MODES, ROUGH_CUT_FOCUS_OPTIONS


class DNAFilmAppLayoutMixin:
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
        ttk.Label(header, textvariable=self.matching_prep_text, wraplength=980).grid(row=10, column=0, sticky="w")
        ttk.Label(header, textvariable=self.scene_matching_text, wraplength=980).grid(row=11, column=0, sticky="w")
        ttk.Label(header, textvariable=self.rough_cut_text, wraplength=980).grid(row=12, column=0, sticky="w")

        nav = ttk.Frame(self.root, padding=(12, 8))
        nav.grid(row=1, column=0, sticky="nsw")
        for name in ("Project Home", "Source Intake", "Semantic Map", "Matching Prep", "Scene Matching", "Rough Cut", "Output Tracks"):
            ttk.Button(nav, text=name, width=22, command=lambda item=name: self._switch_view(item)).pack(anchor="w", pady=4)
        for name in ("Export Center",):
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
        self.views["Matching Prep"] = self._build_matching_prep_view(main)
        self.views["Scene Matching"] = self._build_scene_matching_view(main)
        self.views["Rough Cut"] = self._build_rough_cut_view(main)
        self.views["Output Tracks"] = self._build_output_tracks_view(main)

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
        ttk.Label(frame, textvariable=self.matching_prep_text, wraplength=700).grid(row=11, column=0, columnspan=2, sticky="w", pady=(4, 0))
        ttk.Label(frame, textvariable=self.scene_matching_text, wraplength=700).grid(row=12, column=0, columnspan=2, sticky="w", pady=(4, 0))
        ttk.Label(frame, textvariable=self.rough_cut_text, wraplength=700).grid(row=13, column=0, columnspan=2, sticky="w", pady=(4, 0))
        ttk.Label(frame, textvariable=self.approval_message_text, wraplength=700).grid(row=14, column=0, columnspan=2, sticky="w", pady=(4, 0))
        ttk.Label(frame, textvariable=self.approval_reason_text, wraplength=700).grid(row=15, column=0, columnspan=2, sticky="w", pady=(4, 0))
        ttk.Label(frame, textvariable=self.reopen_text, wraplength=700).grid(row=16, column=0, columnspan=2, sticky="w", pady=(4, 0))
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
        ttk.Label(frame, textvariable=self.focus_span_text, wraplength=760).grid(row=4, column=0, sticky="w")
        ttk.Label(frame, textvariable=self.summary_text, wraplength=760).grid(row=5, column=0, sticky="w")
        ttk.Label(frame, textvariable=self.issues_summary_text, wraplength=760).grid(row=6, column=0, sticky="w")
        ttk.Label(frame, textvariable=self.matching_prep_text, wraplength=760).grid(row=7, column=0, sticky="w")
        ttk.Label(frame, textvariable=self.scene_matching_text, wraplength=760).grid(row=8, column=0, sticky="w")
        ttk.Label(frame, textvariable=self.approval_message_text, wraplength=760).grid(row=9, column=0, sticky="w")
        ttk.Label(frame, textvariable=self.approval_reason_text, wraplength=760).grid(row=10, column=0, sticky="w")
        ttk.Label(frame, textvariable=self.reopen_text, wraplength=760).grid(row=11, column=0, sticky="w")
        return frame

    def _build_matching_prep_view(self, parent: ttk.Frame) -> ttk.Frame:
        frame = ttk.Frame(parent, padding=12)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(9, weight=1)

        ttk.Label(frame, text="Matching Prep", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(frame, text="This is the first downstream-facing entry surface. It stays local-first and only opens as a real handoff when the semantic map is approved.", wraplength=760).grid(row=1, column=0, sticky="w", pady=(8, 6))
        ttk.Label(frame, textvariable=self.matching_prep_status_text, wraplength=760).grid(row=2, column=0, sticky="w", pady=(0, 4))
        ttk.Label(frame, textvariable=self.matching_prep_summary_text, wraplength=760).grid(row=3, column=0, sticky="nw", pady=(0, 4))
        ttk.Label(frame, textvariable=self.matching_asset_summary_text, wraplength=760).grid(row=4, column=0, sticky="w", pady=(0, 4))
        ttk.Label(frame, textvariable=self.matching_accepted_reference_summary_text, wraplength=760).grid(row=5, column=0, sticky="w", pady=(0, 4))
        ttk.Label(frame, textvariable=self.matching_candidate_summary_text, wraplength=760).grid(row=6, column=0, sticky="w", pady=(0, 8))

        registration = ttk.LabelFrame(frame, text="Film-side input registration", padding=8)
        registration.grid(row=7, column=0, sticky="ew", pady=(0, 8))
        registration.columnconfigure(1, weight=1)
        registration.columnconfigure(3, weight=1)
        ttk.Label(registration, text="Label").grid(row=0, column=0, sticky="w")
        ttk.Entry(registration, textvariable=self.asset_label_var, width=28).grid(row=0, column=1, sticky="ew", padx=(8, 12))
        ttk.Label(registration, text="Type").grid(row=0, column=2, sticky="w")
        ttk.Combobox(registration, textvariable=self.asset_type_var, values=ALLOWED_MATCHING_ASSET_TYPES, state="readonly", width=24).grid(row=0, column=3, sticky="ew")
        ttk.Label(registration, text="Local path / reference").grid(row=1, column=0, sticky="w", pady=(8, 0))
        ttk.Entry(registration, textvariable=self.asset_reference_var, width=28).grid(row=1, column=1, sticky="ew", padx=(8, 12), pady=(8, 0))
        ttk.Label(registration, text="Notes").grid(row=1, column=2, sticky="w", pady=(8, 0))
        self.asset_notes_text = tk.Text(registration, height=3, wrap="word")
        self.asset_notes_text.grid(row=1, column=3, sticky="ew", pady=(8, 0))
        ttk.Button(registration, text="Register Prep Input", command=self.add_matching_prep_asset).grid(row=2, column=0, columnspan=4, sticky="w", pady=(8, 0))

        candidate_frame = ttk.LabelFrame(frame, text="Manual candidate stub", padding=8)
        candidate_frame.grid(row=8, column=0, sticky="ew", pady=(0, 8))
        candidate_frame.columnconfigure(1, weight=1)
        candidate_frame.columnconfigure(3, weight=1)
        ttk.Label(candidate_frame, text="Semantic block").grid(row=0, column=0, sticky="w")
        self.candidate_block_combo = ttk.Combobox(candidate_frame, textvariable=self.candidate_block_var, state="readonly", width=32)
        self.candidate_block_combo.grid(row=0, column=1, sticky="ew", padx=(8, 12))
        ttk.Label(candidate_frame, text="Prep input").grid(row=0, column=2, sticky="w")
        self.candidate_asset_combo = ttk.Combobox(candidate_frame, textvariable=self.candidate_asset_var, state="readonly", width=28)
        self.candidate_asset_combo.grid(row=0, column=3, sticky="ew")
        ttk.Label(candidate_frame, text="Optional note").grid(row=1, column=0, sticky="w", pady=(8, 0))
        ttk.Entry(candidate_frame, textvariable=self.candidate_note_var, width=48).grid(row=1, column=1, columnspan=3, sticky="ew", pady=(8, 0))
        self.add_candidate_button = ttk.Button(candidate_frame, text="Save Manual Candidate Stub", command=self.add_matching_candidate_stub)
        self.add_candidate_button.grid(row=2, column=0, columnspan=4, sticky="w", pady=(8, 0))
        ttk.Label(candidate_frame, text="Existing stub").grid(row=3, column=0, sticky="w", pady=(10, 0))
        self.candidate_stub_combo = ttk.Combobox(candidate_frame, textvariable=self.candidate_stub_var, state="readonly", width=32)
        self.candidate_stub_combo.grid(row=3, column=1, sticky="ew", padx=(8, 12), pady=(10, 0))
        self.candidate_stub_combo.bind("<<ComboboxSelected>>", self.on_candidate_stub_selected)
        ttk.Label(candidate_frame, text="Review status").grid(row=3, column=2, sticky="w", pady=(10, 0))
        self.candidate_status_combo = ttk.Combobox(candidate_frame, textvariable=self.candidate_status_var, values=ALLOWED_CANDIDATE_REVIEW_STATUSES, state="readonly", width=28)
        self.candidate_status_combo.grid(row=3, column=3, sticky="ew", pady=(10, 0))
        self.save_candidate_status_button = ttk.Button(candidate_frame, text="Save Candidate Review Status", command=self.save_matching_candidate_status)
        self.save_candidate_status_button.grid(row=4, column=0, columnspan=2, sticky="w", pady=(8, 0))
        self.remove_candidate_button = ttk.Button(candidate_frame, text="Remove Selected Candidate Stub", command=self.remove_matching_candidate_stub)
        self.remove_candidate_button.grid(row=4, column=2, columnspan=2, sticky="w", pady=(8, 0))
        ttk.Label(candidate_frame, text="Preferred rationale").grid(row=5, column=0, sticky="w", pady=(10, 0))
        ttk.Entry(candidate_frame, textvariable=self.candidate_rationale_var, width=48).grid(row=5, column=1, columnspan=2, sticky="ew", padx=(8, 12), pady=(10, 0))
        self.save_candidate_rationale_button = ttk.Button(candidate_frame, text="Save Preferred Rationale", command=self.save_matching_candidate_rationale)
        self.save_candidate_rationale_button.grid(row=5, column=3, sticky="w", pady=(10, 0))
        self.promote_accepted_reference_button = ttk.Button(candidate_frame, text="Promote Selected Candidate to Accepted Reference", command=self.promote_matching_candidate_to_accepted_reference)
        self.promote_accepted_reference_button.grid(row=6, column=0, columnspan=4, sticky="w", pady=(10, 0))
        ttk.Label(candidate_frame, text="Status focus").grid(row=7, column=0, sticky="w", pady=(10, 0))
        self.candidate_focus_combo = ttk.Combobox(candidate_frame, textvariable=self.candidate_focus_var, values=CANDIDATE_STATUS_FOCUS_OPTIONS, state="readonly", width=28)
        self.candidate_focus_combo.grid(row=7, column=1, sticky="w", padx=(8, 12), pady=(10, 0))
        self.candidate_focus_combo.bind("<<ComboboxSelected>>", self.on_candidate_focus_changed)

        self.matching_prep_handoff = tk.Text(frame, height=18, wrap="word")
        self.matching_prep_handoff.grid(row=9, column=0, sticky="nsew")
        self.matching_prep_handoff.configure(state="disabled")
        return frame
    def _build_scene_matching_view(self, parent: ttk.Frame) -> ttk.Frame:
        frame = ttk.Frame(parent, padding=12)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(7, weight=1)

        ttk.Label(frame, text="Scene Matching", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(frame, text="This is the first scene-matching-facing entry lane. It opens only when one current accepted prep reference exists and stays explicitly pre-automation, pre-timecode, and pre-final-match.", wraplength=760).grid(row=1, column=0, sticky="w", pady=(8, 6))
        self.scene_matching_status_label = ttk.Label(frame, textvariable=self.scene_matching_text, wraplength=760)
        self.scene_matching_status_label.grid(row=2, column=0, sticky="w", pady=(0, 4))
        ttk.Label(frame, textvariable=self.scene_matching_reference_summary_text, wraplength=760).grid(row=3, column=0, sticky="w", pady=(0, 4))
        ttk.Label(frame, textvariable=self.scene_matching_timecode_summary_text, wraplength=760).grid(row=4, column=0, sticky="w", pady=(0, 8))

        scene_reference_frame = ttk.LabelFrame(frame, text="Accepted scene reference stub", padding=8)
        scene_reference_frame.grid(row=5, column=0, sticky="ew", pady=(0, 8))
        scene_reference_frame.columnconfigure(1, weight=1)
        ttk.Label(scene_reference_frame, text="Scene-side label").grid(row=0, column=0, sticky="w")
        self.scene_reference_label_entry = ttk.Entry(scene_reference_frame, textvariable=self.scene_reference_label_var, width=48)
        self.scene_reference_label_entry.grid(row=0, column=1, sticky="ew", padx=(8, 12))
        self.save_scene_reference_button = ttk.Button(scene_reference_frame, text="Save Accepted Scene Reference Stub", command=self.save_accepted_scene_reference_stub)
        self.save_scene_reference_button.grid(row=0, column=2, sticky="w")

        timecode_frame = ttk.LabelFrame(frame, text="Timecode range stub", padding=8)
        timecode_frame.grid(row=6, column=0, sticky="ew", pady=(0, 8))
        timecode_frame.columnconfigure(1, weight=1)
        timecode_frame.columnconfigure(3, weight=1)
        ttk.Label(timecode_frame, text="Start").grid(row=0, column=0, sticky="w")
        self.timecode_start_entry = ttk.Entry(timecode_frame, textvariable=self.timecode_start_var, width=18)
        self.timecode_start_entry.grid(row=0, column=1, sticky="ew", padx=(8, 12))
        ttk.Label(timecode_frame, text="End").grid(row=0, column=2, sticky="w")
        self.timecode_end_entry = ttk.Entry(timecode_frame, textvariable=self.timecode_end_var, width=18)
        self.timecode_end_entry.grid(row=0, column=3, sticky="ew", padx=(8, 12))
        self.save_timecode_button = ttk.Button(timecode_frame, text="Save Timecode Range Stub", command=self.save_timecode_range_stub)
        self.save_timecode_button.grid(row=0, column=4, sticky="w")
        ttk.Label(timecode_frame, text="Use HH:MM:SS | manual provisional range only", wraplength=760).grid(row=1, column=0, columnspan=5, sticky="w", pady=(6, 0))

        self.scene_matching_handoff = tk.Text(frame, height=18, wrap="word")
        self.scene_matching_handoff.grid(row=7, column=0, sticky="nsew")
        self.scene_matching_handoff.configure(state="disabled")
        return frame


    def _build_rough_cut_view(self, parent: ttk.Frame) -> ttk.Frame:
        frame = ttk.Frame(parent, padding=12)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(5, weight=1)

        ttk.Label(frame, text="Rough Cut", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(frame, text="This is the first assembly-facing downstream lane. It opens only when one current accepted reference, accepted scene reference stub, and timecode range stub exist and stays explicitly provisional, local-first, pre-render, and pre-final-cut.", wraplength=760).grid(row=1, column=0, sticky="w", pady=(8, 6))
        ttk.Label(frame, textvariable=self.rough_cut_text, wraplength=760).grid(row=2, column=0, sticky="w", pady=(0, 4))
        ttk.Label(frame, textvariable=self.rough_cut_focus_summary_text, wraplength=760).grid(row=3, column=0, sticky="w", pady=(0, 4))
        ttk.Label(frame, textvariable=self.rough_cut_segment_summary_text, wraplength=760).grid(row=4, column=0, sticky="w", pady=(0, 8))

        segment_frame = ttk.LabelFrame(frame, text="Rough-cut segment stub", padding=8)
        segment_frame.grid(row=5, column=0, sticky="ew", pady=(0, 8))
        segment_frame.columnconfigure(1, weight=1)
        ttk.Label(segment_frame, text="Segment label").grid(row=0, column=0, sticky="w")
        self.rough_cut_segment_label_entry = ttk.Entry(segment_frame, textvariable=self.rough_cut_segment_label_var, width=48)
        self.rough_cut_segment_label_entry.grid(row=0, column=1, sticky="ew", padx=(8, 12))
        self.save_rough_cut_segment_button = ttk.Button(segment_frame, text="Save Rough-Cut Segment Stub", command=self.save_rough_cut_segment_stub)
        self.save_rough_cut_segment_button.grid(row=0, column=2, sticky="w")
        ttk.Label(segment_frame, text="Assembly-facing stub only | not a real cut or render-ready output", wraplength=760).grid(row=1, column=0, columnspan=3, sticky="w", pady=(6, 0))

        list_frame = ttk.LabelFrame(frame, text="Saved rough-cut segment set", padding=8)
        list_frame.grid(row=6, column=0, sticky="ew", pady=(0, 8))
        list_frame.columnconfigure(0, weight=1)
        focus_controls = ttk.Frame(list_frame)
        focus_controls.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))
        ttk.Radiobutton(
            focus_controls,
            text="Show All Saved Segments",
            value=ROUGH_CUT_FOCUS_OPTIONS[0],
            variable=self.rough_cut_focus_var,
            command=self.on_rough_cut_focus_changed,
        ).pack(side="left")
        ttk.Radiobutton(
            focus_controls,
            text="Show Preferred Subset Only",
            value=ROUGH_CUT_FOCUS_OPTIONS[1],
            variable=self.rough_cut_focus_var,
            command=self.on_rough_cut_focus_changed,
        ).pack(side="left", padx=(12, 0))
        self.rough_cut_segment_combo = ttk.Combobox(list_frame, textvariable=self.rough_cut_segment_var, state="readonly")
        self.rough_cut_segment_combo.grid(row=1, column=0, sticky="ew")
        self.rough_cut_segment_combo.bind("<<ComboboxSelected>>", self.on_rough_cut_segment_selected)
        controls = ttk.Frame(list_frame)
        controls.grid(row=1, column=1, sticky="w", padx=(12, 0))
        self.rough_cut_move_up_button = ttk.Button(controls, text="Move Up", command=lambda: self.reorder_selected_rough_cut_segment("up"))
        self.rough_cut_move_up_button.pack(side="left")
        self.rough_cut_move_down_button = ttk.Button(controls, text="Move Down", command=lambda: self.reorder_selected_rough_cut_segment("down"))
        self.rough_cut_move_down_button.pack(side="left", padx=(8, 0))
        self.include_rough_cut_subset_button = ttk.Button(controls, text="Include in Current Rough Cut", command=self.include_selected_rough_cut_segment)
        self.include_rough_cut_subset_button.pack(side="left", padx=(8, 0))
        self.remove_rough_cut_subset_button = ttk.Button(controls, text="Remove from Current Rough Cut", command=self.remove_selected_rough_cut_segment)
        self.remove_rough_cut_subset_button.pack(side="left", padx=(8, 0))
        self.remove_rough_cut_segment_button = ttk.Button(controls, text="Remove Selected Segment", command=self.remove_selected_saved_rough_cut_segment)
        self.remove_rough_cut_segment_button.pack(side="left", padx=(8, 0))

        self.rough_cut_handoff = tk.Text(frame, height=18, wrap="word")
        self.rough_cut_handoff.grid(row=7, column=0, sticky="nsew")
        self.rough_cut_handoff.configure(state="disabled")
        return frame

    def _build_output_tracks_view(self, parent: ttk.Frame) -> ttk.Frame:
        frame = ttk.Frame(parent, padding=12)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(5, weight=1)

        ttk.Label(frame, text="Output Tracks", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(
            frame,
            text="This output-builder surface now builds packaging, Shorts/Reels, and long-video script artifacts from the current rough-cut handoff.",
            wraplength=760,
        ).grid(row=1, column=0, sticky="w", pady=(8, 6))
        ttk.Label(frame, textvariable=self.output_builder_status_text, wraplength=760).grid(row=2, column=0, sticky="w", pady=(0, 4))
        ttk.Label(frame, textvariable=self.output_builder_summary_text, wraplength=760).grid(row=3, column=0, sticky="w", pady=(0, 8))
        action_frame = ttk.Frame(frame)
        action_frame.grid(row=4, column=0, sticky="w", pady=(0, 8))
        self.build_packaging_bundle_button = ttk.Button(
            action_frame,
            text="Build Packaging-Ready Script Bundle",
            command=self.build_packaging_script_bundle,
        )
        self.build_packaging_bundle_button.pack(side="left")
        self.build_shorts_reels_button = ttk.Button(
            action_frame,
            text="Build Shorts/Reels Script",
            command=self.build_shorts_reels_script,
        )
        self.build_shorts_reels_button.pack(side="left", padx=(8, 0))
        self.build_long_video_button = ttk.Button(
            action_frame,
            text="Build Long-Video Script",
            command=self.build_long_video_script,
        )
        self.build_long_video_button.pack(side="left", padx=(8, 0))
        ttk.Label(action_frame, textvariable=self.output_builder_path_text, wraplength=520).pack(side="left", padx=(12, 0))
        self.output_builder_handoff = tk.Text(frame, height=20, wrap="word")
        self.output_builder_handoff.grid(row=5, column=0, sticky="nsew")
        self.output_builder_handoff.configure(state="disabled")
        return frame


    def _switch_view(self, name: str) -> None:
        self.current_view.set(name)
        for frame in list(self.views.values()) + [self.placeholder_view]:
            frame.grid_remove()
        self.views.get(name, self.placeholder_view).grid()
