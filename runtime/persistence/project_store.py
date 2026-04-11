from __future__ import annotations

import re
import uuid
from pathlib import Path

from runtime.builders import build_long_video_script, build_packaging_script_bundle, build_shorts_reels_script, packaging_bundle_source_segments
from runtime.domain.project_types import ProjectSlice
from runtime.domain.semantic_rules import (
    ALLOWED_CANDIDATE_REVIEW_STATUSES,
    ALLOWED_MATCHING_ASSET_TYPES,
    ALLOWED_MERGE_DIRECTIONS,
    ALLOWED_OUTPUT_SUITABILITY,
    ALLOWED_REORDER_DIRECTIONS,
    ALLOWED_REVIEW_STATES,
    ALLOWED_ROUGH_CUT_SUBSET_STATUSES,
    ALLOWED_SEMANTIC_ROLES,
    APPROVAL_BLOCK_REASON,
    APPROVAL_READY_REASON,
    MANUAL_TIMECODE_PATTERN,
    REOPEN_BLOCK_EDIT_REASON,
    REOPEN_REORDER_REASON,
    REOPEN_SOURCE_REASON,
    REOPEN_STRUCTURE_REASON,
    REOPEN_SUITABILITY_REASON,
    build_semantic_blocks,
    completeness_readiness_hint,
    copy_analysis_record,
    describe_warning_flags,
    derive_warning_flags,
    next_block_id,
    normalize_accepted_reference,
    normalize_accepted_scene_reference_stub,
    normalize_long_video_script,
    normalize_matching_candidate_stubs,
    normalize_output_suitability,
    normalize_packaging_script_bundle,
    normalize_rough_cut_segment_stubs,
    normalize_semantic_blocks,
    normalize_shorts_reels_script,
    normalize_timecode_range_stub,
    parse_manual_timecode,
    resequence_blocks,
    semantic_completeness,
    semantic_role_for,
    slugify,
    split_sentences,
    title_for,
    utc_now,
)
from runtime.domain.workflow_rules import (
    apply_project_summary,
    approval_readiness_label,
    default_review_record,
    mark_reopened_if_needed,
    reconcile_accepted_reference,
    reconcile_accepted_scene_reference_stub,
    reconcile_long_video_script,
    reconcile_packaging_script_bundle,
    reconcile_rough_cut_segment_stubs,
    reconcile_shorts_reels_script,
    reconcile_timecode_range_stub,
    status_payload,
)
from runtime.persistence.json_store import read_json, write_json


PROJECT_FORMAT_VERSION = "0.5"
ANALYSIS_RECORD_FILENAME = "analysis_source.json"
REVIEW_RECORD_FILENAME = "semantic_review.json"
MATCHING_PREP_ASSET_FILENAME = "asset_references.json"
MATCHING_CANDIDATE_FILENAME = "candidate_stubs.json"
ACCEPTED_REFERENCE_FILENAME = "accepted_reference.json"
ACCEPTED_SCENE_REFERENCE_STUB_FILENAME = "accepted_scene_reference_stub.json"
TIMECODE_RANGE_STUB_FILENAME = "timecode_range_stub.json"
ROUGH_CUT_SEGMENTS_FILENAME = "rough_cut_segments.json"
PACKAGING_SCRIPT_BUNDLE_FILENAME = "packaging_script_bundle.json"
SHORTS_REELS_SCRIPT_FILENAME = "shorts_reels_script.json"
LONG_VIDEO_SCRIPT_FILENAME = "long_video_script.json"
KEEP_EXISTING = object()


class ProjectSliceStore:
    def __init__(self, workspace_root: Path) -> None:
        self.workspace_root = workspace_root

    def create_project(
        self,
        title: str,
        film_title: str = "",
        language: str = "en",
    ) -> ProjectSlice:
        clean_title = title.strip()
        if not clean_title:
            raise ValueError("Project title is required.")

        project_id = f"project-{uuid.uuid4().hex[:8]}"
        folder_name = f"{slugify(clean_title)}-{project_id[-4:]}"
        project_dir = self.workspace_root / folder_name
        project_dir.mkdir(parents=True, exist_ok=False)

        created_at = utc_now()
        manifest = {
            "project_id": project_id,
            "project_format_version": PROJECT_FORMAT_VERSION,
            "project_title": clean_title,
            "film_title": film_title.strip(),
            "language": language.strip() or "en",
            "records_root": "records",
            "primary_analysis_source": None,
            "created_at": created_at,
            "updated_at": created_at,
        }
        project_record = {
            "project_id": project_id,
            "record_id": "project-record",
            "record_type": "project",
            "title": clean_title,
            "film_title": film_title.strip(),
            "language": language.strip() or "en",
            "project_status": "intake_required",
            "current_readiness_summary": "Load analysis text to unlock semantic map.",
            "created_at": created_at,
            "updated_at": created_at,
        }
        intake_record = {
            "project_id": project_id,
            "record_id": "intake-record",
            "record_type": "intake_package",
            "primary_analysis_source_reference": None,
            "intake_readiness": "blocked",
            "intake_warnings": ["Analysis text is required for semantic work."],
            "created_at": created_at,
            "updated_at": created_at,
        }
        semantic_review_record = default_review_record(project_id, created_at)

        self._write_project_state(project_dir, manifest, project_record, intake_record, None, semantic_review_record, [], [], [])
        return self.load_project(project_dir)

    def load_project(self, project_dir: Path) -> ProjectSlice:
        manifest = read_json(project_dir / "project.manifest")
        project_record = read_json(project_dir / "records" / "project" / "project.json")
        intake_record = read_json(project_dir / "records" / "intake" / "intake.json")
        analysis_record_path = project_dir / "records" / "intake" / ANALYSIS_RECORD_FILENAME
        legacy_analysis_record_path = project_dir / "records" / "intake" / "analysis.txt.json"
        semantic_record_path = project_dir / "records" / "semantic" / "semantic_blocks.json"
        review_record_path = project_dir / "records" / "review" / REVIEW_RECORD_FILENAME
        matching_prep_asset_path = project_dir / "records" / "matching_prep" / MATCHING_PREP_ASSET_FILENAME
        matching_candidate_path = project_dir / "records" / "matching_prep" / MATCHING_CANDIDATE_FILENAME
        accepted_reference_path = project_dir / "records" / "matching_prep" / ACCEPTED_REFERENCE_FILENAME
        accepted_scene_reference_stub_path = project_dir / "records" / "scene_matching" / ACCEPTED_SCENE_REFERENCE_STUB_FILENAME
        timecode_range_stub_path = project_dir / "records" / "scene_matching" / TIMECODE_RANGE_STUB_FILENAME
        rough_cut_segments_path = project_dir / "records" / "rough_cut" / ROUGH_CUT_SEGMENTS_FILENAME
        packaging_script_bundle_path = project_dir / "records" / "output" / PACKAGING_SCRIPT_BUNDLE_FILENAME
        shorts_reels_script_path = project_dir / "records" / "output" / SHORTS_REELS_SCRIPT_FILENAME
        long_video_script_path = project_dir / "records" / "output" / LONG_VIDEO_SCRIPT_FILENAME

        if analysis_record_path.exists():
            analysis_source_record = read_json(analysis_record_path)
        elif legacy_analysis_record_path.exists():
            analysis_source_record = read_json(legacy_analysis_record_path)
        else:
            analysis_source_record = None

        if review_record_path.exists():
            semantic_review_record = read_json(review_record_path)
        else:
            timestamp = project_record.get("updated_at", utc_now())
            semantic_review_record = default_review_record(manifest["project_id"], timestamp)

        semantic_blocks = read_json(semantic_record_path)["blocks"] if semantic_record_path.exists() else []
        semantic_blocks = normalize_semantic_blocks(semantic_blocks)
        matching_prep_assets = read_json(matching_prep_asset_path)["entries"] if matching_prep_asset_path.exists() else []
        matching_candidate_stubs = read_json(matching_candidate_path)["entries"] if matching_candidate_path.exists() else []
        matching_candidate_stubs = normalize_matching_candidate_stubs(matching_candidate_stubs)
        accepted_reference = normalize_accepted_reference(read_json(accepted_reference_path) if accepted_reference_path.exists() else None)
        accepted_reference = reconcile_accepted_reference(accepted_reference, matching_candidate_stubs, semantic_review_record)
        accepted_scene_reference_stub = normalize_accepted_scene_reference_stub(read_json(accepted_scene_reference_stub_path) if accepted_scene_reference_stub_path.exists() else None)
        accepted_scene_reference_stub = reconcile_accepted_scene_reference_stub(accepted_scene_reference_stub, accepted_reference)
        timecode_range_stub = normalize_timecode_range_stub(read_json(timecode_range_stub_path) if timecode_range_stub_path.exists() else None)
        timecode_range_stub = reconcile_timecode_range_stub(timecode_range_stub, accepted_scene_reference_stub)
        rough_cut_segment_stubs = read_json(rough_cut_segments_path)["entries"] if rough_cut_segments_path.exists() else []
        rough_cut_segment_stubs = normalize_rough_cut_segment_stubs(rough_cut_segment_stubs)
        rough_cut_segment_stubs = reconcile_rough_cut_segment_stubs(rough_cut_segment_stubs, accepted_reference, accepted_scene_reference_stub, timecode_range_stub)
        packaging_script_bundle = normalize_packaging_script_bundle(read_json(packaging_script_bundle_path) if packaging_script_bundle_path.exists() else None)
        packaging_script_bundle = reconcile_packaging_script_bundle(
            packaging_script_bundle,
            rough_cut_segment_stubs,
            accepted_reference,
            accepted_scene_reference_stub,
            timecode_range_stub,
        )
        shorts_reels_script = normalize_shorts_reels_script(read_json(shorts_reels_script_path) if shorts_reels_script_path.exists() else None)
        shorts_reels_script = reconcile_shorts_reels_script(
            shorts_reels_script,
            rough_cut_segment_stubs,
            accepted_reference,
            accepted_scene_reference_stub,
            timecode_range_stub,
        )
        long_video_script = normalize_long_video_script(read_json(long_video_script_path) if long_video_script_path.exists() else None)
        long_video_script = reconcile_long_video_script(
            long_video_script,
            rough_cut_segment_stubs,
            accepted_reference,
            accepted_scene_reference_stub,
            timecode_range_stub,
        )
        return ProjectSlice(
            project_dir=project_dir,
            manifest=manifest,
            project_record=project_record,
            intake_record=intake_record,
            analysis_source_record=analysis_source_record,
            semantic_review_record=semantic_review_record,
            semantic_blocks=semantic_blocks,
            matching_prep_assets=matching_prep_assets,
            matching_candidate_stubs=matching_candidate_stubs,
            accepted_reference=accepted_reference,
            accepted_scene_reference_stub=accepted_scene_reference_stub,
            timecode_range_stub=timecode_range_stub,
            rough_cut_segment_stubs=rough_cut_segment_stubs,
            packaging_script_bundle=packaging_script_bundle,
            shorts_reels_script=shorts_reels_script,
            long_video_script=long_video_script,
        )

    def save_analysis_text(
        self,
        project_dir: Path,
        analysis_text: str,
        source_label: str = "analysis.txt",
    ) -> ProjectSlice:
        normalized_text = analysis_text.lstrip("\ufeff").strip()
        if len(normalized_text) < 40:
            raise ValueError("Analysis text must contain at least 40 non-whitespace characters.")

        project = self.load_project(project_dir)
        now = utc_now()
        source_record_id = "analysis-source"
        analysis_source_record = {
            "project_id": project.manifest["project_id"],
            "record_id": source_record_id,
            "record_type": "analysis_text_source",
            "source_label": source_label,
            "source_classification": "analysis_text",
            "canonical_source": True,
            "readiness": "ready",
            "validity": "accepted",
            "created_at": project.analysis_source_record["created_at"] if project.analysis_source_record else now,
            "updated_at": now,
        }
        semantic_blocks = build_semantic_blocks(project.manifest["project_id"], source_record_id, normalized_text)
        intake_warnings = []
        if not project.project_record.get("film_title"):
            intake_warnings.append("Film title remains optional and is still empty.")

        analysis_record_ref = f"records/intake/{ANALYSIS_RECORD_FILENAME}"
        semantic_blocks = normalize_semantic_blocks(semantic_blocks)
        manifest = dict(project.manifest)
        manifest["primary_analysis_source"] = analysis_record_ref
        manifest["updated_at"] = now

        project_record = dict(project.project_record)
        project_record["updated_at"] = now

        intake_record = dict(project.intake_record)
        intake_record["primary_analysis_source_reference"] = analysis_record_ref
        intake_record["intake_readiness"] = "ready"
        intake_record["intake_warnings"] = intake_warnings
        intake_record["updated_at"] = now

        semantic_review_record = dict(project.semantic_review_record)
        mark_reopened_if_needed(semantic_review_record, REOPEN_SOURCE_REASON)
        semantic_review_record["updated_at"] = now

        apply_project_summary(project_record, intake_record, semantic_blocks, semantic_review_record)
        self._write_project_state(
            project_dir,
            manifest,
            project_record,
            intake_record,
            analysis_source_record,
            semantic_review_record,
            semantic_blocks,
            project.matching_prep_assets,
            project.matching_candidate_stubs,
        )
        (project_dir / "sources" / "analysis").mkdir(parents=True, exist_ok=True)
        (project_dir / "sources" / "analysis" / source_label).write_text(normalized_text + "\n", encoding="utf-8")
        return self.load_project(project_dir)

    def update_semantic_block(
        self,
        project_dir: Path,
        block_id: str,
        title: str,
        semantic_role: str,
        notes: str,
        output_suitability: dict | None = None,
    ) -> ProjectSlice:
        clean_title = title.strip()
        clean_role = semantic_role.strip()
        if not clean_title:
            raise ValueError("Block title is required.")
        if clean_role not in ALLOWED_SEMANTIC_ROLES:
            raise ValueError("Semantic role is invalid for this MVP slice.")
        normalized_suitability = normalize_output_suitability(output_suitability)
        if output_suitability is not None and set(output_suitability) - {"long_video", "shorts_reels", "carousel", "packaging"}:
            raise ValueError("Output suitability keys are invalid for this MVP slice.")

        project = self.load_project(project_dir)
        now = utc_now()
        updated = False
        suitability_changed = False
        metadata_changed = False
        semantic_blocks: list[dict] = []
        for block in project.semantic_blocks:
            current = dict(block)
            if current["record_id"] == block_id:
                if current.get("title") != clean_title or current.get("semantic_role") != clean_role or current.get("notes", "") != notes.strip():
                    metadata_changed = True
                if current.get("output_suitability") != normalized_suitability:
                    suitability_changed = True
                current["title"] = clean_title
                current["semantic_role"] = clean_role
                current["notes"] = notes.strip()
                current["output_suitability"] = normalized_suitability
                updated = True
            semantic_blocks.append(current)

        if not updated:
            raise ValueError("Selected semantic block was not found.")

        reopen_reason = REOPEN_BLOCK_EDIT_REASON
        if suitability_changed and not metadata_changed:
            reopen_reason = REOPEN_SUITABILITY_REASON
        return self._persist_semantic_update(
            project_dir,
            project,
            semantic_blocks,
            now,
            reopen_reason,
        )

    def reorder_semantic_block(self, project_dir: Path, block_id: str, direction: str) -> ProjectSlice:
        clean_direction = direction.strip().lower()
        if clean_direction not in ALLOWED_REORDER_DIRECTIONS:
            raise ValueError("Reorder direction is invalid for this MVP slice.")

        project = self.load_project(project_dir)
        semantic_blocks = [dict(block) for block in project.semantic_blocks]
        if len(semantic_blocks) < 2:
            return project

        current_index = next((index for index, block in enumerate(semantic_blocks) if block["record_id"] == block_id), None)
        if current_index is None:
            raise ValueError("Selected semantic block was not found.")

        target_index = current_index - 1 if clean_direction == "up" else current_index + 1
        if target_index < 0 or target_index >= len(semantic_blocks):
            return project

        semantic_blocks[current_index], semantic_blocks[target_index] = semantic_blocks[target_index], semantic_blocks[current_index]
        resequence_blocks(semantic_blocks)

        return self._persist_semantic_update(
            project_dir,
            project,
            semantic_blocks,
            utc_now(),
            REOPEN_REORDER_REASON,
        )

    def split_semantic_block(self, project_dir: Path, block_id: str, split_after_sentence: int) -> ProjectSlice:
        project = self.load_project(project_dir)
        current_index = next((index for index, block in enumerate(project.semantic_blocks) if block["record_id"] == block_id), None)
        if current_index is None:
            raise ValueError("Selected semantic block was not found.")

        original_block = dict(project.semantic_blocks[current_index])
        sentences = split_sentences(original_block.get("content", ""))
        if len(sentences) < 2:
            raise ValueError("Selected block needs at least two sentences before it can be split.")
        if split_after_sentence < 1 or split_after_sentence >= len(sentences):
            raise ValueError("Split boundary must leave at least one sentence on each side.")

        first_content = " ".join(sentences[:split_after_sentence]).strip()
        second_content = " ".join(sentences[split_after_sentence:]).strip()
        if not first_content or not second_content:
            raise ValueError("Split boundary must leave meaningful content on each side.")

        first_block = dict(original_block)
        first_block["title"] = title_for(first_content)
        first_block["content"] = first_content

        second_block = dict(original_block)
        second_block["record_id"] = next_block_id(project.semantic_blocks)
        second_block["title"] = title_for(second_content)
        second_block["content"] = second_content
        second_block["notes"] = ""

        semantic_blocks = [dict(block) for block in project.semantic_blocks]
        semantic_blocks[current_index: current_index + 1] = [first_block, second_block]
        resequence_blocks(semantic_blocks)

        return self._persist_semantic_update(
            project_dir,
            project,
            semantic_blocks,
            utc_now(),
            REOPEN_STRUCTURE_REASON,
        )

    def merge_semantic_block(self, project_dir: Path, block_id: str, direction: str) -> ProjectSlice:
        clean_direction = direction.strip().lower()
        if clean_direction not in ALLOWED_MERGE_DIRECTIONS:
            raise ValueError("Merge direction is invalid for this MVP slice.")

        project = self.load_project(project_dir)
        semantic_blocks = [dict(block) for block in project.semantic_blocks]
        if len(semantic_blocks) < 2:
            raise ValueError("At least two semantic blocks are required before merge is available.")

        current_index = next((index for index, block in enumerate(semantic_blocks) if block["record_id"] == block_id), None)
        if current_index is None:
            raise ValueError("Selected semantic block was not found.")

        neighbor_index = current_index - 1 if clean_direction == "up" else current_index + 1
        if neighbor_index < 0 or neighbor_index >= len(semantic_blocks):
            raise ValueError("Selected semantic block has no adjacent neighbor in that direction.")

        selected_block = dict(semantic_blocks[current_index])
        neighbor_block = dict(semantic_blocks[neighbor_index])
        if clean_direction == "up":
            combined_content = f"{neighbor_block['content'].strip()}\n\n{selected_block['content'].strip()}"
            insert_index = neighbor_index
        else:
            combined_content = f"{selected_block['content'].strip()}\n\n{neighbor_block['content'].strip()}"
            insert_index = current_index

        merged_block = dict(selected_block)
        merged_block["title"] = title_for(combined_content)
        merged_block["content"] = combined_content

        start = min(current_index, neighbor_index)
        end = max(current_index, neighbor_index)
        semantic_blocks[start : end + 1] = [merged_block]
        if insert_index != start:
            insert_index = start
        resequence_blocks(semantic_blocks)

        return self._persist_semantic_update(
            project_dir,
            project,
            semantic_blocks,
            utc_now(),
            REOPEN_STRUCTURE_REASON,
        )

    def update_semantic_review_status(self, project_dir: Path, review_status: str) -> ProjectSlice:
        clean_status = review_status.strip()
        if clean_status not in ALLOWED_REVIEW_STATES:
            raise ValueError("Review status is invalid for this MVP slice.")

        project = self.load_project(project_dir)
        if not project.semantic_blocks:
            raise ValueError("Semantic review cannot be updated before semantic blocks exist.")

        now = utc_now()
        manifest = dict(project.manifest)
        manifest["updated_at"] = now
        project_record = dict(project.project_record)
        project_record["updated_at"] = now
        intake_record = dict(project.intake_record)
        intake_record["updated_at"] = now
        analysis_source_record = copy_analysis_record(project.analysis_source_record, now)
        semantic_review_record = dict(project.semantic_review_record)
        readiness = approval_readiness_label(project.intake_record, project.semantic_blocks, project.semantic_review_record)
        if clean_status == "approved" and readiness != "ready_for_approval":
            semantic_review_record["approval_block_reason"] = APPROVAL_BLOCK_REASON
            semantic_review_record["approval_transition_message"] = "Approval remains blocked until the map is explicitly ready for review."
            semantic_review_record["updated_at"] = now
            apply_project_summary(project_record, intake_record, project.semantic_blocks, semantic_review_record)
            self._write_project_state(
                project_dir,
                manifest,
                project_record,
                intake_record,
                analysis_source_record,
                semantic_review_record,
                project.semantic_blocks,
                project.matching_prep_assets,
                project.matching_candidate_stubs,
            )
            return self.load_project(project_dir)

        semantic_review_record["review_status"] = clean_status
        semantic_review_record["approved"] = clean_status == "approved"
        semantic_review_record["approval_block_reason"] = ""
        semantic_review_record["approval_transition_message"] = (
            "Semantic map approved."
            if clean_status == "approved"
            else APPROVAL_READY_REASON
            if clean_status == "ready_for_review"
            else "Semantic map remains under edit."
        )
        if clean_status != "approved":
            semantic_review_record["reopened_after_change"] = False
            semantic_review_record["reopen_reason"] = ""
        semantic_review_record["updated_at"] = now

        apply_project_summary(project_record, intake_record, project.semantic_blocks, semantic_review_record)
        self._write_project_state(
            project_dir,
            manifest,
            project_record,
            intake_record,
            analysis_source_record,
            semantic_review_record,
            project.semantic_blocks,
            project.matching_prep_assets,
            project.matching_candidate_stubs,
        )
        return self.load_project(project_dir)

    def add_matching_prep_asset(
        self,
        project_dir: Path,
        asset_label: str,
        asset_type: str,
        reference_value: str = "",
        notes: str = "",
    ) -> ProjectSlice:
        clean_label = asset_label.strip()
        clean_type = asset_type.strip()
        clean_reference = reference_value.strip()
        clean_notes = notes.strip()
        if not clean_label:
            raise ValueError("Asset label is required for Matching Prep registration.")
        if clean_type not in ALLOWED_MATCHING_ASSET_TYPES:
            raise ValueError("Asset type is invalid for this Matching Prep slice.")
        if not clean_reference and not clean_notes:
            raise ValueError("Add either a local path/reference or notes for this Matching Prep entry.")

        project = self.load_project(project_dir)
        now = utc_now()
        entries = [dict(entry) for entry in project.matching_prep_assets]
        entries.append(
            {
                "project_id": project.manifest["project_id"],
                "record_id": f"prep-asset-{len(entries) + 1:03d}",
                "record_type": "matching_prep_asset_reference",
                "asset_label": clean_label,
                "asset_type": clean_type,
                "reference_value": clean_reference,
                "notes": clean_notes,
                "created_at": now,
                "updated_at": now,
            }
        )

        manifest = dict(project.manifest)
        manifest["updated_at"] = now
        project_record = dict(project.project_record)
        project_record["updated_at"] = now
        intake_record = dict(project.intake_record)
        intake_record["updated_at"] = now
        analysis_source_record = copy_analysis_record(project.analysis_source_record, now)
        semantic_review_record = dict(project.semantic_review_record)
        semantic_review_record["updated_at"] = now

        apply_project_summary(project_record, intake_record, project.semantic_blocks, semantic_review_record)
        self._write_project_state(
            project_dir,
            manifest,
            project_record,
            intake_record,
            analysis_source_record,
            semantic_review_record,
            project.semantic_blocks,
            entries,
            project.matching_candidate_stubs,
        )
        return self.load_project(project_dir)

    def add_matching_candidate_stub(
        self,
        project_dir: Path,
        semantic_block_id: str,
        prep_asset_id: str,
        note: str = "",
    ) -> ProjectSlice:
        clean_block_id = semantic_block_id.strip()
        clean_asset_id = prep_asset_id.strip()
        clean_note = note.strip()
        if not clean_block_id:
            raise ValueError("Select one semantic block before creating a manual candidate stub.")
        if not clean_asset_id:
            raise ValueError("Select one registered prep input before creating a manual candidate stub.")

        project = self.load_project(project_dir)
        if project.semantic_review_record.get("review_status") != "approved" or project.semantic_review_record.get("reopened_after_change"):
            raise ValueError("Manual candidate stubs are only available while Matching Prep is open from an approved semantic map.")

        semantic_block = next((block for block in project.semantic_blocks if block["record_id"] == clean_block_id), None)
        if semantic_block is None:
            raise ValueError("Selected semantic block was not found for this manual candidate stub.")
        prep_asset = next((entry for entry in project.matching_prep_assets if entry["record_id"] == clean_asset_id), None)
        if prep_asset is None:
            raise ValueError("Selected prep input was not found for this manual candidate stub.")
        duplicate_entry = next(
            (
                entry
                for entry in project.matching_candidate_stubs
                if entry.get("semantic_block_id") == semantic_block["record_id"]
                and entry.get("prep_asset_id") == prep_asset["record_id"]
            ),
            None,
        )
        if duplicate_entry is not None:
            raise ValueError("This manual candidate stub already exists for the selected semantic block and prep input.")

        now = utc_now()
        entries = [dict(entry) for entry in project.matching_candidate_stubs]
        entries.append(
            {
                "project_id": project.manifest["project_id"],
                "record_id": f"candidate-stub-{len(entries) + 1:03d}",
                "record_type": "manual_match_candidate_stub",
                "semantic_block_id": semantic_block["record_id"],
                "prep_asset_id": prep_asset["record_id"],
                "review_status": "tentative",
                "preferred_rationale": "",
                "note": clean_note,
                "created_at": now,
                "updated_at": now,
            }
        )

        manifest = dict(project.manifest)
        manifest["updated_at"] = now
        project_record = dict(project.project_record)
        project_record["updated_at"] = now
        intake_record = dict(project.intake_record)
        intake_record["updated_at"] = now
        analysis_source_record = copy_analysis_record(project.analysis_source_record, now)
        semantic_review_record = dict(project.semantic_review_record)
        semantic_review_record["updated_at"] = now

        apply_project_summary(project_record, intake_record, project.semantic_blocks, semantic_review_record)
        self._write_project_state(
            project_dir,
            manifest,
            project_record,
            intake_record,
            analysis_source_record,
            semantic_review_record,
            project.semantic_blocks,
            project.matching_prep_assets,
            entries,
        )
        return self.load_project(project_dir)

    def update_matching_candidate_stub_status(
        self,
        project_dir: Path,
        candidate_stub_id: str,
        review_status: str,
    ) -> ProjectSlice:
        clean_stub_id = candidate_stub_id.strip()
        clean_status = review_status.strip()
        if not clean_stub_id:
            raise ValueError("Select one manual candidate stub before saving review status.")
        if clean_status not in ALLOWED_CANDIDATE_REVIEW_STATUSES:
            raise ValueError("Manual candidate stub review status is invalid for this Matching Prep slice.")

        project = self.load_project(project_dir)
        if project.semantic_review_record.get("review_status") != "approved" or project.semantic_review_record.get("reopened_after_change"):
            raise ValueError("Manual candidate review status can only be changed while Matching Prep is open from an approved semantic map.")

        now = utc_now()
        updated = False
        entries: list[dict] = []
        for entry in project.matching_candidate_stubs:
            current = dict(entry)
            if current["record_id"] == clean_stub_id:
                current["review_status"] = clean_status
                current["updated_at"] = now
                updated = True
            entries.append(current)

        if not updated:
            raise ValueError("Selected manual candidate stub was not found for this Matching Prep slice.")

        accepted_reference = reconcile_accepted_reference(project.accepted_reference, entries, project.semantic_review_record)
        manifest = dict(project.manifest)
        manifest["updated_at"] = now
        project_record = dict(project.project_record)
        project_record["updated_at"] = now
        intake_record = dict(project.intake_record)
        intake_record["updated_at"] = now
        analysis_source_record = copy_analysis_record(project.analysis_source_record, now)
        semantic_review_record = dict(project.semantic_review_record)
        semantic_review_record["updated_at"] = now

        apply_project_summary(project_record, intake_record, project.semantic_blocks, semantic_review_record)
        self._write_project_state(
            project_dir,
            manifest,
            project_record,
            intake_record,
            analysis_source_record,
            semantic_review_record,
            project.semantic_blocks,
            project.matching_prep_assets,
            entries,
            accepted_reference,
        )
        return self.load_project(project_dir)

    def save_accepted_scene_reference_stub(
        self,
        project_dir: Path,
        scene_reference_label: str,
    ) -> ProjectSlice:
        clean_label = scene_reference_label.strip()
        if not clean_label:
            raise ValueError("Enter one scene-side reference label before saving the accepted scene reference stub.")

        project = self.load_project(project_dir)
        if project.accepted_reference is None:
            raise ValueError("Accepted scene reference stub creation is blocked until one current accepted prep reference exists.")
        if project.semantic_review_record.get("reopened_after_change"):
            raise ValueError("Accepted scene reference stub creation is only available while Scene Matching is open from the current accepted prep reference.")

        now = utc_now()
        accepted_scene_reference_stub = {
            "project_id": project.manifest["project_id"],
            "record_id": "accepted-scene-reference-current",
            "record_type": "accepted_scene_reference_stub",
            "source_accepted_reference_id": project.accepted_reference["record_id"],
            "source_candidate_stub_id": project.accepted_reference.get("source_candidate_stub_id", ""),
            "semantic_block_id": project.accepted_reference.get("semantic_block_id", ""),
            "prep_asset_id": project.accepted_reference.get("prep_asset_id", ""),
            "scene_reference_label": clean_label,
            "scene_reference_state": "accepted_scene_reference_stub_for_later_timecode_prep_only",
            "created_at": now,
            "updated_at": now,
        }

        manifest = dict(project.manifest)
        manifest["updated_at"] = now
        project_record = dict(project.project_record)
        project_record["updated_at"] = now
        intake_record = dict(project.intake_record)
        intake_record["updated_at"] = now
        analysis_source_record = copy_analysis_record(project.analysis_source_record, now)
        semantic_review_record = dict(project.semantic_review_record)
        semantic_review_record["updated_at"] = now

        apply_project_summary(project_record, intake_record, project.semantic_blocks, semantic_review_record)
        self._write_project_state(
            project_dir,
            manifest,
            project_record,
            intake_record,
            analysis_source_record,
            semantic_review_record,
            project.semantic_blocks,
            project.matching_prep_assets,
            project.matching_candidate_stubs,
            project.accepted_reference,
            accepted_scene_reference_stub,
        )
        return self.load_project(project_dir)

    def save_timecode_range_stub(
        self,
        project_dir: Path,
        start_timecode: str,
        end_timecode: str,
    ) -> ProjectSlice:
        clean_start = start_timecode.strip()
        clean_end = end_timecode.strip()
        if not clean_start:
            raise ValueError("Enter a start timecode before saving the timecode range stub.")
        if not clean_end:
            raise ValueError("Enter an end timecode before saving the timecode range stub.")

        start_seconds = parse_manual_timecode(clean_start)
        if start_seconds is None:
            raise ValueError("Start timecode must use HH:MM:SS format for this Scene Matching slice.")
        end_seconds = parse_manual_timecode(clean_end)
        if end_seconds is None:
            raise ValueError("End timecode must use HH:MM:SS format for this Scene Matching slice.")
        if end_seconds < start_seconds:
            raise ValueError("End timecode must not be earlier than start timecode for this provisional range.")

        project = self.load_project(project_dir)
        if project.accepted_scene_reference_stub is None:
            raise ValueError("Timecode range stub creation is blocked until one current accepted scene reference stub exists.")
        if project.accepted_reference is None or project.semantic_review_record.get("reopened_after_change"):
            raise ValueError("Timecode range stub creation is only available while Scene Matching is open from the current accepted scene reference stub.")

        now = utc_now()
        timecode_range_stub = {
            "project_id": project.manifest["project_id"],
            "record_id": "timecode-range-current",
            "record_type": "timecode_range_stub",
            "source_accepted_scene_reference_stub_id": project.accepted_scene_reference_stub["record_id"],
            "source_candidate_stub_id": project.accepted_scene_reference_stub.get("source_candidate_stub_id", ""),
            "semantic_block_id": project.accepted_scene_reference_stub.get("semantic_block_id", ""),
            "prep_asset_id": project.accepted_scene_reference_stub.get("prep_asset_id", ""),
            "start_timecode": clean_start,
            "end_timecode": clean_end,
            "timecode_state": "provisional_timecode_range_for_later_assembly_only",
            "created_at": now,
            "updated_at": now,
        }

        manifest = dict(project.manifest)
        manifest["updated_at"] = now
        project_record = dict(project.project_record)
        project_record["updated_at"] = now
        intake_record = dict(project.intake_record)
        intake_record["updated_at"] = now
        analysis_source_record = copy_analysis_record(project.analysis_source_record, now)
        semantic_review_record = dict(project.semantic_review_record)
        semantic_review_record["updated_at"] = now

        apply_project_summary(project_record, intake_record, project.semantic_blocks, semantic_review_record)
        self._write_project_state(
            project_dir,
            manifest,
            project_record,
            intake_record,
            analysis_source_record,
            semantic_review_record,
            project.semantic_blocks,
            project.matching_prep_assets,
            project.matching_candidate_stubs,
            project.accepted_reference,
            project.accepted_scene_reference_stub,
            timecode_range_stub,
        )
        return self.load_project(project_dir)

    def save_rough_cut_segment_stub(
        self,
        project_dir: Path,
        segment_label: str,
    ) -> ProjectSlice:
        clean_label = segment_label.strip()
        if not clean_label:
            raise ValueError("Enter one segment label before saving the rough-cut segment stub.")

        project = self.load_project(project_dir)
        if project.accepted_reference is None:
            raise ValueError("Rough-cut segment stub creation is blocked until one current accepted reference exists.")
        if project.accepted_scene_reference_stub is None:
            raise ValueError("Rough-cut segment stub creation is blocked until one current accepted scene reference stub exists.")
        if project.timecode_range_stub is None:
            raise ValueError("Rough-cut segment stub creation is blocked until one current timecode range stub exists.")
        if project.semantic_review_record.get("reopened_after_change"):
            raise ValueError("Rough-cut segment stub creation is only available while Rough Cut is open from the current accepted downstream handoff chain.")

        now = utc_now()
        next_index = 1
        for entry in project.rough_cut_segment_stubs:
            match = re.fullmatch(r"rough-cut-segment-(\d+)", entry.get("record_id", ""))
            if match:
                next_index = max(next_index, int(match.group(1)) + 1)
        rough_cut_segment_entries = [dict(entry) for entry in project.rough_cut_segment_stubs]
        rough_cut_segment_entries.append(
            {
                "project_id": project.manifest["project_id"],
                "record_id": f"rough-cut-segment-{next_index:03d}",
                "record_type": "rough_cut_segment_stub",
                "source_accepted_reference_id": project.accepted_reference["record_id"],
                "source_accepted_scene_reference_stub_id": project.accepted_scene_reference_stub["record_id"],
                "source_timecode_range_stub_id": project.timecode_range_stub["record_id"],
                "source_candidate_stub_id": project.timecode_range_stub.get("source_candidate_stub_id", ""),
                "semantic_block_id": project.timecode_range_stub.get("semantic_block_id", ""),
                "prep_asset_id": project.timecode_range_stub.get("prep_asset_id", ""),
                "start_timecode": project.timecode_range_stub.get("start_timecode", ""),
                "end_timecode": project.timecode_range_stub.get("end_timecode", ""),
                "segment_label": clean_label,
                "sequence": len(rough_cut_segment_entries) + 1,
                "subset_status": ALLOWED_ROUGH_CUT_SUBSET_STATUSES[0],
                "segment_state": "provisional_rough_cut_segment_for_later_assembly_only",
                "created_at": now,
                "updated_at": now,
            }
        )

        manifest = dict(project.manifest)
        manifest["updated_at"] = now
        project_record = dict(project.project_record)
        project_record["updated_at"] = now
        intake_record = dict(project.intake_record)
        intake_record["updated_at"] = now
        analysis_source_record = copy_analysis_record(project.analysis_source_record, now)
        semantic_review_record = dict(project.semantic_review_record)
        semantic_review_record["updated_at"] = now

        apply_project_summary(project_record, intake_record, project.semantic_blocks, semantic_review_record)
        self._write_project_state(
            project_dir,
            manifest,
            project_record,
            intake_record,
            analysis_source_record,
            semantic_review_record,
            project.semantic_blocks,
            project.matching_prep_assets,
            project.matching_candidate_stubs,
            project.accepted_reference,
            project.accepted_scene_reference_stub,
            project.timecode_range_stub,
            rough_cut_segment_entries,
        )
        return self.load_project(project_dir)

    def reorder_rough_cut_segment_stub(
        self,
        project_dir: Path,
        rough_cut_segment_stub_id: str,
        direction: str,
    ) -> ProjectSlice:
        clean_stub_id = rough_cut_segment_stub_id.strip()
        if not clean_stub_id:
            raise ValueError("Select one rough-cut segment stub before reordering it.")
        if direction not in ALLOWED_REORDER_DIRECTIONS:
            raise ValueError("Rough-cut segment reorder direction must be 'up' or 'down'.")

        project = self.load_project(project_dir)
        if project.accepted_reference is None or project.accepted_scene_reference_stub is None or project.timecode_range_stub is None or project.semantic_review_record.get("reopened_after_change"):
            raise ValueError("Rough-cut segment reorder is only available while Rough Cut is open from the current accepted downstream handoff chain.")

        entries = [dict(entry) for entry in project.rough_cut_segment_stubs]
        current_index = next((index for index, entry in enumerate(entries) if entry.get("record_id") == clean_stub_id), None)
        if current_index is None:
            raise ValueError("Selected rough-cut segment stub was not found in the current rough-cut set.")
        target_index = current_index - 1 if direction == "up" else current_index + 1
        if target_index < 0 or target_index >= len(entries):
            return project
        entries[current_index], entries[target_index] = entries[target_index], entries[current_index]
        now = utc_now()
        for index, entry in enumerate(entries, start=1):
            entry["sequence"] = index
            entry["updated_at"] = now

        manifest = dict(project.manifest)
        manifest["updated_at"] = now
        project_record = dict(project.project_record)
        project_record["updated_at"] = now
        intake_record = dict(project.intake_record)
        intake_record["updated_at"] = now
        analysis_source_record = copy_analysis_record(project.analysis_source_record, now)
        semantic_review_record = dict(project.semantic_review_record)
        semantic_review_record["updated_at"] = now

        apply_project_summary(project_record, intake_record, project.semantic_blocks, semantic_review_record)
        self._write_project_state(
            project_dir,
            manifest,
            project_record,
            intake_record,
            analysis_source_record,
            semantic_review_record,
            project.semantic_blocks,
            project.matching_prep_assets,
            project.matching_candidate_stubs,
            project.accepted_reference,
            project.accepted_scene_reference_stub,
            project.timecode_range_stub,
            entries,
        )
        return self.load_project(project_dir)

    def update_rough_cut_segment_subset_status(
        self,
        project_dir: Path,
        rough_cut_segment_stub_id: str,
        subset_status: str,
    ) -> ProjectSlice:
        clean_stub_id = rough_cut_segment_stub_id.strip()
        clean_subset_status = subset_status.strip()
        if not clean_stub_id:
            raise ValueError("Select one rough-cut segment stub before changing its current rough-cut subset status.")
        if clean_subset_status not in ALLOWED_ROUGH_CUT_SUBSET_STATUSES:
            raise ValueError("Rough-cut subset status must be 'saved_only' or 'selected_for_current_rough_cut'.")

        project = self.load_project(project_dir)
        if project.accepted_reference is None or project.accepted_scene_reference_stub is None or project.timecode_range_stub is None or project.semantic_review_record.get("reopened_after_change"):
            raise ValueError("Rough-cut subset status can only be changed while Rough Cut is open from the current accepted downstream handoff chain.")

        now = utc_now()
        updated = False
        entries: list[dict] = []
        for entry in project.rough_cut_segment_stubs:
            current = dict(entry)
            if current.get("record_id") == clean_stub_id:
                current["subset_status"] = clean_subset_status
                current["updated_at"] = now
                updated = True
            entries.append(current)
        if not updated:
            raise ValueError("Selected rough-cut segment stub was not found in the current rough-cut set.")

        manifest = dict(project.manifest)
        manifest["updated_at"] = now
        project_record = dict(project.project_record)
        project_record["updated_at"] = now
        intake_record = dict(project.intake_record)
        intake_record["updated_at"] = now
        analysis_source_record = copy_analysis_record(project.analysis_source_record, now)
        semantic_review_record = dict(project.semantic_review_record)
        semantic_review_record["updated_at"] = now

        apply_project_summary(project_record, intake_record, project.semantic_blocks, semantic_review_record)
        self._write_project_state(
            project_dir,
            manifest,
            project_record,
            intake_record,
            analysis_source_record,
            semantic_review_record,
            project.semantic_blocks,
            project.matching_prep_assets,
            project.matching_candidate_stubs,
            project.accepted_reference,
            project.accepted_scene_reference_stub,
            project.timecode_range_stub,
            entries,
        )
        return self.load_project(project_dir)

    def remove_rough_cut_segment_stub(
        self,
        project_dir: Path,
        rough_cut_segment_stub_id: str,
    ) -> ProjectSlice:
        clean_stub_id = rough_cut_segment_stub_id.strip()
        if not clean_stub_id:
            raise ValueError("Select one rough-cut segment stub before removing it.")

        project = self.load_project(project_dir)
        if project.accepted_reference is None or project.accepted_scene_reference_stub is None or project.timecode_range_stub is None or project.semantic_review_record.get("reopened_after_change"):
            raise ValueError("Rough-cut segment removal is only available while Rough Cut is open from the current accepted downstream handoff chain.")

        now = utc_now()
        removed = False
        entries: list[dict] = []
        for entry in project.rough_cut_segment_stubs:
            if entry.get("record_id") == clean_stub_id:
                removed = True
                continue
            entries.append(dict(entry))
        if not removed:
            raise ValueError("Selected rough-cut segment stub was not found in the current rough-cut set.")

        manifest = dict(project.manifest)
        manifest["updated_at"] = now
        project_record = dict(project.project_record)
        project_record["updated_at"] = now
        intake_record = dict(project.intake_record)
        intake_record["updated_at"] = now
        analysis_source_record = copy_analysis_record(project.analysis_source_record, now)
        semantic_review_record = dict(project.semantic_review_record)
        semantic_review_record["updated_at"] = now

        apply_project_summary(project_record, intake_record, project.semantic_blocks, semantic_review_record)
        self._write_project_state(
            project_dir,
            manifest,
            project_record,
            intake_record,
            analysis_source_record,
            semantic_review_record,
            project.semantic_blocks,
            project.matching_prep_assets,
            project.matching_candidate_stubs,
            project.accepted_reference,
            project.accepted_scene_reference_stub,
            project.timecode_range_stub,
            entries,
        )
        return self.load_project(project_dir)

    def build_packaging_script_bundle(self, project_dir: Path) -> ProjectSlice:
        project = self.load_project(project_dir)
        if project.accepted_reference is None or project.accepted_scene_reference_stub is None or project.timecode_range_stub is None:
            raise ValueError("Packaging bundle build is blocked until the current accepted downstream chain exists.")
        _, source_segments = packaging_bundle_source_segments(project)
        if not source_segments:
            raise ValueError("Packaging bundle build is blocked until at least one rough-cut segment exists.")
        if project.semantic_review_record.get("reopened_after_change"):
            raise ValueError("Packaging bundle build is only available while the current downstream chain remains open.")

        now = utc_now()
        packaging_script_bundle = build_packaging_script_bundle(project, now)
        manifest = dict(project.manifest)
        manifest["updated_at"] = now
        project_record = dict(project.project_record)
        project_record["updated_at"] = now
        project_record["project_status"] = "packaging_script_bundle_ready"
        project_record["current_readiness_summary"] = (
            f"Packaging-ready script bundle built from {packaging_script_bundle['segment_count']} rough-cut segment(s) "
            f"using {packaging_script_bundle['source_focus_mode']}."
        )
        intake_record = dict(project.intake_record)
        intake_record["updated_at"] = now
        analysis_source_record = copy_analysis_record(project.analysis_source_record, now)
        semantic_review_record = dict(project.semantic_review_record)
        semantic_review_record["updated_at"] = now

        self._write_project_state(
            project_dir,
            manifest,
            project_record,
            intake_record,
            analysis_source_record,
            semantic_review_record,
            project.semantic_blocks,
            project.matching_prep_assets,
            project.matching_candidate_stubs,
            project.accepted_reference,
            project.accepted_scene_reference_stub,
            project.timecode_range_stub,
            project.rough_cut_segment_stubs,
            packaging_script_bundle,
            project.shorts_reels_script,
            project.long_video_script,
        )
        return self.load_project(project_dir)

    def build_shorts_reels_script(self, project_dir: Path) -> ProjectSlice:
        project = self.load_project(project_dir)
        if project.accepted_reference is None or project.accepted_scene_reference_stub is None or project.timecode_range_stub is None:
            raise ValueError("Shorts/Reels build is blocked until the current accepted downstream chain exists.")
        _, source_segments = packaging_bundle_source_segments(project)
        if not source_segments:
            raise ValueError("Shorts/Reels build is blocked until at least one rough-cut segment exists.")
        if project.semantic_review_record.get("reopened_after_change"):
            raise ValueError("Shorts/Reels build is only available while the current downstream chain remains open.")

        now = utc_now()
        shorts_reels_script = build_shorts_reels_script(project, now)
        manifest = dict(project.manifest)
        manifest["updated_at"] = now
        project_record = dict(project.project_record)
        project_record["updated_at"] = now
        project_record["project_status"] = "shorts_reels_script_ready"
        project_record["current_readiness_summary"] = (
            f"Shorts/Reels script built from {shorts_reels_script['segment_count']} rough-cut segment(s) "
            f"using {shorts_reels_script['source_focus_mode']}."
        )
        intake_record = dict(project.intake_record)
        intake_record["updated_at"] = now
        analysis_source_record = copy_analysis_record(project.analysis_source_record, now)
        semantic_review_record = dict(project.semantic_review_record)
        semantic_review_record["updated_at"] = now

        self._write_project_state(
            project_dir,
            manifest,
            project_record,
            intake_record,
            analysis_source_record,
            semantic_review_record,
            project.semantic_blocks,
            project.matching_prep_assets,
            project.matching_candidate_stubs,
            project.accepted_reference,
            project.accepted_scene_reference_stub,
            project.timecode_range_stub,
            project.rough_cut_segment_stubs,
            project.packaging_script_bundle,
            shorts_reels_script,
            project.long_video_script,
        )
        return self.load_project(project_dir)

    def build_long_video_script(self, project_dir: Path) -> ProjectSlice:
        project = self.load_project(project_dir)
        if project.accepted_reference is None or project.accepted_scene_reference_stub is None or project.timecode_range_stub is None:
            raise ValueError("Long-video build is blocked until the current accepted downstream chain exists.")
        _, source_segments = packaging_bundle_source_segments(project)
        if not source_segments:
            raise ValueError("Long-video build is blocked until at least one rough-cut segment exists.")
        if project.semantic_review_record.get("reopened_after_change"):
            raise ValueError("Long-video build is only available while the current downstream chain remains open.")

        now = utc_now()
        long_video_script = build_long_video_script(project, now)
        manifest = dict(project.manifest)
        manifest["updated_at"] = now
        project_record = dict(project.project_record)
        project_record["updated_at"] = now
        project_record["project_status"] = "long_video_script_ready"
        project_record["current_readiness_summary"] = (
            f"Long-video script built from {long_video_script['segment_count']} rough-cut segment(s) "
            f"using {long_video_script['source_focus_mode']}."
        )
        intake_record = dict(project.intake_record)
        intake_record["updated_at"] = now
        analysis_source_record = copy_analysis_record(project.analysis_source_record, now)
        semantic_review_record = dict(project.semantic_review_record)
        semantic_review_record["updated_at"] = now

        self._write_project_state(
            project_dir,
            manifest,
            project_record,
            intake_record,
            analysis_source_record,
            semantic_review_record,
            project.semantic_blocks,
            project.matching_prep_assets,
            project.matching_candidate_stubs,
            project.accepted_reference,
            project.accepted_scene_reference_stub,
            project.timecode_range_stub,
            project.rough_cut_segment_stubs,
            project.packaging_script_bundle,
            project.shorts_reels_script,
            long_video_script,
        )
        return self.load_project(project_dir)

    def update_matching_candidate_stub_rationale(
        self,
        project_dir: Path,
        candidate_stub_id: str,
        preferred_rationale: str,
    ) -> ProjectSlice:
        clean_stub_id = candidate_stub_id.strip()
        clean_rationale = preferred_rationale.strip()
        if not clean_stub_id:
            raise ValueError("Select one manual candidate stub before saving preferred rationale.")

        project = self.load_project(project_dir)
        if project.semantic_review_record.get("review_status") != "approved" or project.semantic_review_record.get("reopened_after_change"):
            raise ValueError("Manual candidate preferred rationale can only be changed while Matching Prep is open from an approved semantic map.")

        now = utc_now()
        updated = False
        entries: list[dict] = []
        for entry in project.matching_candidate_stubs:
            current = dict(entry)
            if current["record_id"] == clean_stub_id:
                current["preferred_rationale"] = clean_rationale
                current["updated_at"] = now
                updated = True
            entries.append(current)

        if not updated:
            raise ValueError("Selected manual candidate stub was not found for this Matching Prep slice.")

        manifest = dict(project.manifest)
        manifest["updated_at"] = now
        project_record = dict(project.project_record)
        project_record["updated_at"] = now
        intake_record = dict(project.intake_record)
        intake_record["updated_at"] = now
        analysis_source_record = copy_analysis_record(project.analysis_source_record, now)
        semantic_review_record = dict(project.semantic_review_record)
        semantic_review_record["updated_at"] = now

        apply_project_summary(project_record, intake_record, project.semantic_blocks, semantic_review_record)
        self._write_project_state(
            project_dir,
            manifest,
            project_record,
            intake_record,
            analysis_source_record,
            semantic_review_record,
            project.semantic_blocks,
            project.matching_prep_assets,
            entries,
        )
        return self.load_project(project_dir)

    def promote_matching_candidate_stub_to_accepted_reference(
        self,
        project_dir: Path,
        candidate_stub_id: str,
    ) -> ProjectSlice:
        clean_stub_id = candidate_stub_id.strip()
        if not clean_stub_id:
            raise ValueError("Select one selected manual candidate stub before promoting an accepted reference.")

        project = self.load_project(project_dir)
        if project.semantic_review_record.get("review_status") != "approved" or project.semantic_review_record.get("reopened_after_change"):
            raise ValueError("Accepted reference promotion is only available while Matching Prep is open from an approved semantic map.")

        selected_stub = next((entry for entry in project.matching_candidate_stubs if entry["record_id"] == clean_stub_id), None)
        if selected_stub is None:
            raise ValueError("Selected manual candidate stub was not found for accepted reference promotion.")
        if selected_stub.get("review_status", ALLOWED_CANDIDATE_REVIEW_STATUSES[0]) != "selected":
            raise ValueError("Only selected manual candidate stubs can be promoted to an accepted reference.")

        now = utc_now()
        accepted_reference = {
            "project_id": project.manifest["project_id"],
            "record_id": "accepted-reference-current",
            "record_type": "accepted_scene_reference",
            "source_candidate_stub_id": selected_stub["record_id"],
            "semantic_block_id": selected_stub["semantic_block_id"],
            "prep_asset_id": selected_stub["prep_asset_id"],
            "acceptance_state": "accepted_for_later_matching_work_only",
            "accepted_from_candidate_review_status": "selected",
            "created_at": now,
            "updated_at": now,
        }

        manifest = dict(project.manifest)
        manifest["updated_at"] = now
        project_record = dict(project.project_record)
        project_record["updated_at"] = now
        intake_record = dict(project.intake_record)
        intake_record["updated_at"] = now
        analysis_source_record = copy_analysis_record(project.analysis_source_record, now)
        semantic_review_record = dict(project.semantic_review_record)
        semantic_review_record["updated_at"] = now

        apply_project_summary(project_record, intake_record, project.semantic_blocks, semantic_review_record)
        self._write_project_state(
            project_dir,
            manifest,
            project_record,
            intake_record,
            analysis_source_record,
            semantic_review_record,
            project.semantic_blocks,
            project.matching_prep_assets,
            project.matching_candidate_stubs,
            accepted_reference,
        )
        return self.load_project(project_dir)

    def remove_matching_candidate_stub(
        self,
        project_dir: Path,
        candidate_stub_id: str,
    ) -> ProjectSlice:
        clean_stub_id = candidate_stub_id.strip()
        if not clean_stub_id:
            raise ValueError("Select one manual candidate stub before removing it.")

        project = self.load_project(project_dir)
        if project.semantic_review_record.get("review_status") != "approved" or project.semantic_review_record.get("reopened_after_change"):
            raise ValueError("Manual candidate stubs can only be removed while Matching Prep is open from an approved semantic map.")

        now = utc_now()
        removed = False
        entries: list[dict] = []
        for entry in project.matching_candidate_stubs:
            if entry["record_id"] == clean_stub_id:
                removed = True
                continue
            entries.append(dict(entry))

        if not removed:
            raise ValueError("Selected manual candidate stub was not found for this Matching Prep slice.")

        accepted_reference = reconcile_accepted_reference(project.accepted_reference, entries, project.semantic_review_record)
        manifest = dict(project.manifest)
        manifest["updated_at"] = now
        project_record = dict(project.project_record)
        project_record["updated_at"] = now
        intake_record = dict(project.intake_record)
        intake_record["updated_at"] = now
        analysis_source_record = copy_analysis_record(project.analysis_source_record, now)
        semantic_review_record = dict(project.semantic_review_record)
        semantic_review_record["updated_at"] = now

        apply_project_summary(project_record, intake_record, project.semantic_blocks, semantic_review_record)
        self._write_project_state(
            project_dir,
            manifest,
            project_record,
            intake_record,
            analysis_source_record,
            semantic_review_record,
            project.semantic_blocks,
            project.matching_prep_assets,
            entries,
            accepted_reference,
        )
        return self.load_project(project_dir)

    def _persist_semantic_update(
        self,
        project_dir: Path,
        project: ProjectSlice,
        semantic_blocks: list[dict],
        now: str,
        reopen_reason: str,
    ) -> ProjectSlice:
        manifest = dict(project.manifest)
        manifest["updated_at"] = now
        project_record = dict(project.project_record)
        project_record["updated_at"] = now
        intake_record = dict(project.intake_record)
        intake_record["updated_at"] = now
        analysis_source_record = copy_analysis_record(project.analysis_source_record, now)
        semantic_review_record = dict(project.semantic_review_record)
        mark_reopened_if_needed(semantic_review_record, reopen_reason)
        semantic_review_record["updated_at"] = now

        apply_project_summary(project_record, intake_record, semantic_blocks, semantic_review_record)
        self._write_project_state(
            project_dir,
            manifest,
            project_record,
            intake_record,
            analysis_source_record,
            semantic_review_record,
            semantic_blocks,
            project.matching_prep_assets,
            project.matching_candidate_stubs,
        )
        return self.load_project(project_dir)

    def _copy_analysis_record(self, analysis_source_record: dict | None, now: str) -> dict | None:
        return copy_analysis_record(analysis_source_record, now)

    def _next_block_id(self, semantic_blocks: list[dict]) -> str:
        return next_block_id(semantic_blocks)

    def _resequence_blocks(self, semantic_blocks: list[dict]) -> None:
        resequence_blocks(semantic_blocks)

    def _approval_readiness_label(
        self,
        intake_record: dict,
        semantic_blocks: list[dict],
        semantic_review_record: dict,
    ) -> str:
        return approval_readiness_label(intake_record, semantic_blocks, semantic_review_record)

    def _write_project_state(
        self,
        project_dir: Path,
        manifest: dict,
        project_record: dict,
        intake_record: dict,
        analysis_source_record: dict | None,
        semantic_review_record: dict,
        semantic_blocks: list[dict],
        matching_prep_assets: list[dict],
        matching_candidate_stubs: list[dict],
        accepted_reference: dict | None | object = KEEP_EXISTING,
        accepted_scene_reference_stub: dict | None | object = KEEP_EXISTING,
        timecode_range_stub: dict | None | object = KEEP_EXISTING,
        rough_cut_segment_stubs: list[dict] | object = KEEP_EXISTING,
        packaging_script_bundle: dict | None | object = KEEP_EXISTING,
        shorts_reels_script: dict | None | object = KEEP_EXISTING,
        long_video_script: dict | None | object = KEEP_EXISTING,
    ) -> None:
        semantic_blocks = normalize_semantic_blocks(semantic_blocks)
        accepted_reference_path = project_dir / "records" / "matching_prep" / ACCEPTED_REFERENCE_FILENAME
        accepted_scene_reference_stub_path = project_dir / "records" / "scene_matching" / ACCEPTED_SCENE_REFERENCE_STUB_FILENAME
        timecode_range_stub_path = project_dir / "records" / "scene_matching" / TIMECODE_RANGE_STUB_FILENAME
        rough_cut_segments_path = project_dir / "records" / "rough_cut" / ROUGH_CUT_SEGMENTS_FILENAME
        packaging_script_bundle_path = project_dir / "records" / "output" / PACKAGING_SCRIPT_BUNDLE_FILENAME
        packaging_script_markdown_path = project_dir / "outputs" / "packaging" / "packaging_script_bundle.md"
        shorts_reels_script_path = project_dir / "records" / "output" / SHORTS_REELS_SCRIPT_FILENAME
        shorts_reels_markdown_path = project_dir / "outputs" / "shorts_reels" / "shorts_reels_script.md"
        long_video_script_path = project_dir / "records" / "output" / LONG_VIDEO_SCRIPT_FILENAME
        long_video_markdown_path = project_dir / "outputs" / "long_video" / "long_video_script.md"
        if accepted_reference is KEEP_EXISTING:
            accepted_reference_payload = normalize_accepted_reference(read_json(accepted_reference_path) if accepted_reference_path.exists() else None)
        else:
            accepted_reference_payload = normalize_accepted_reference(accepted_reference if isinstance(accepted_reference, dict) else None)
        accepted_reference_payload = reconcile_accepted_reference(accepted_reference_payload, matching_candidate_stubs, semantic_review_record)
        if accepted_scene_reference_stub is KEEP_EXISTING:
            accepted_scene_reference_stub_payload = normalize_accepted_scene_reference_stub(read_json(accepted_scene_reference_stub_path) if accepted_scene_reference_stub_path.exists() else None)
        else:
            accepted_scene_reference_stub_payload = normalize_accepted_scene_reference_stub(accepted_scene_reference_stub if isinstance(accepted_scene_reference_stub, dict) else None)
        accepted_scene_reference_stub_payload = reconcile_accepted_scene_reference_stub(accepted_scene_reference_stub_payload, accepted_reference_payload)
        if timecode_range_stub is KEEP_EXISTING:
            timecode_range_stub_payload = normalize_timecode_range_stub(read_json(timecode_range_stub_path) if timecode_range_stub_path.exists() else None)
        else:
            timecode_range_stub_payload = normalize_timecode_range_stub(timecode_range_stub if isinstance(timecode_range_stub, dict) else None)
        timecode_range_stub_payload = reconcile_timecode_range_stub(timecode_range_stub_payload, accepted_scene_reference_stub_payload)
        if rough_cut_segment_stubs is KEEP_EXISTING:
            rough_cut_segment_entries = read_json(rough_cut_segments_path)["entries"] if rough_cut_segments_path.exists() else []
        else:
            rough_cut_segment_entries = list(rough_cut_segment_stubs) if isinstance(rough_cut_segment_stubs, list) else []
        rough_cut_segment_entries = reconcile_rough_cut_segment_stubs(rough_cut_segment_entries, accepted_reference_payload, accepted_scene_reference_stub_payload, timecode_range_stub_payload)
        if packaging_script_bundle is KEEP_EXISTING:
            packaging_script_bundle_payload = normalize_packaging_script_bundle(read_json(packaging_script_bundle_path) if packaging_script_bundle_path.exists() else None)
        else:
            packaging_script_bundle_payload = normalize_packaging_script_bundle(packaging_script_bundle if isinstance(packaging_script_bundle, dict) else None)
        packaging_script_bundle_payload = reconcile_packaging_script_bundle(
            packaging_script_bundle_payload,
            rough_cut_segment_entries,
            accepted_reference_payload,
            accepted_scene_reference_stub_payload,
            timecode_range_stub_payload,
        )
        if shorts_reels_script is KEEP_EXISTING:
            shorts_reels_script_payload = normalize_shorts_reels_script(read_json(shorts_reels_script_path) if shorts_reels_script_path.exists() else None)
        else:
            shorts_reels_script_payload = normalize_shorts_reels_script(shorts_reels_script if isinstance(shorts_reels_script, dict) else None)
        shorts_reels_script_payload = reconcile_shorts_reels_script(
            shorts_reels_script_payload,
            rough_cut_segment_entries,
            accepted_reference_payload,
            accepted_scene_reference_stub_payload,
            timecode_range_stub_payload,
        )
        if long_video_script is KEEP_EXISTING:
            long_video_script_payload = normalize_long_video_script(read_json(long_video_script_path) if long_video_script_path.exists() else None)
        else:
            long_video_script_payload = normalize_long_video_script(long_video_script if isinstance(long_video_script, dict) else None)
        long_video_script_payload = reconcile_long_video_script(
            long_video_script_payload,
            rough_cut_segment_entries,
            accepted_reference_payload,
            accepted_scene_reference_stub_payload,
            timecode_range_stub_payload,
        )
        write_json(project_dir / "project.manifest", manifest)
        write_json(
            project_dir / "project.meta" / "status.json",
            status_payload(
                project_record,
                intake_record,
                semantic_review_record,
                semantic_blocks,
                packaging_script_bundle_payload,
                shorts_reels_script_payload,
                long_video_script_payload,
            ),
        )
        write_json(project_dir / "records" / "project" / "project.json", project_record)
        write_json(project_dir / "records" / "intake" / "intake.json", intake_record)
        if analysis_source_record is not None:
            write_json(project_dir / "records" / "intake" / ANALYSIS_RECORD_FILENAME, analysis_source_record)
        write_json(project_dir / "records" / "review" / REVIEW_RECORD_FILENAME, semantic_review_record)
        write_json(project_dir / "records" / "semantic" / "semantic_blocks.json", {"blocks": semantic_blocks})
        write_json(project_dir / "records" / "matching_prep" / MATCHING_PREP_ASSET_FILENAME, {"entries": matching_prep_assets})
        write_json(project_dir / "records" / "matching_prep" / MATCHING_CANDIDATE_FILENAME, {"entries": matching_candidate_stubs})
        if accepted_reference_payload is not None:
            write_json(accepted_reference_path, accepted_reference_payload)
        elif accepted_reference_path.exists():
            accepted_reference_path.unlink()
        if accepted_scene_reference_stub_payload is not None:
            write_json(accepted_scene_reference_stub_path, accepted_scene_reference_stub_payload)
        elif accepted_scene_reference_stub_path.exists():
            accepted_scene_reference_stub_path.unlink()
        if timecode_range_stub_payload is not None:
            write_json(timecode_range_stub_path, timecode_range_stub_payload)
        elif timecode_range_stub_path.exists():
            timecode_range_stub_path.unlink()
        if rough_cut_segment_entries:
            write_json(rough_cut_segments_path, {"entries": rough_cut_segment_entries})
        elif rough_cut_segments_path.exists():
            rough_cut_segments_path.unlink()
        if packaging_script_bundle_payload is not None:
            write_json(packaging_script_bundle_path, packaging_script_bundle_payload)
            packaging_script_markdown_path.parent.mkdir(parents=True, exist_ok=True)
            packaging_script_markdown_path.write_text(packaging_script_bundle_payload.get("markdown_content", ""), encoding="utf-8")
        elif packaging_script_bundle_path.exists():
            packaging_script_bundle_path.unlink()
            if packaging_script_markdown_path.exists():
                packaging_script_markdown_path.unlink()
        if shorts_reels_script_payload is not None:
            write_json(shorts_reels_script_path, shorts_reels_script_payload)
            shorts_reels_markdown_path.parent.mkdir(parents=True, exist_ok=True)
            shorts_reels_markdown_path.write_text(shorts_reels_script_payload.get("markdown_content", ""), encoding="utf-8")
        elif shorts_reels_script_path.exists():
            shorts_reels_script_path.unlink()
            if shorts_reels_markdown_path.exists():
                shorts_reels_markdown_path.unlink()
        if long_video_script_payload is not None:
            write_json(long_video_script_path, long_video_script_payload)
            long_video_markdown_path.parent.mkdir(parents=True, exist_ok=True)
            long_video_markdown_path.write_text(long_video_script_payload.get("markdown_content", ""), encoding="utf-8")
        elif long_video_script_path.exists():
            long_video_script_path.unlink()
            if long_video_markdown_path.exists():
                long_video_markdown_path.unlink()
