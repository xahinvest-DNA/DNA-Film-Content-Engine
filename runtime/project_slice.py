from __future__ import annotations

import json
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


PROJECT_FORMAT_VERSION = "0.5"
ANALYSIS_RECORD_FILENAME = "analysis_source.json"
REVIEW_RECORD_FILENAME = "semantic_review.json"
MATCHING_PREP_ASSET_FILENAME = "asset_references.json"
MATCHING_CANDIDATE_FILENAME = "candidate_stubs.json"
ACCEPTED_REFERENCE_FILENAME = "accepted_reference.json"
ACCEPTED_SCENE_REFERENCE_STUB_FILENAME = "accepted_scene_reference_stub.json"
TIMECODE_RANGE_STUB_FILENAME = "timecode_range_stub.json"
ROUGH_CUT_SEGMENTS_FILENAME = "rough_cut_segments.json"
ALLOWED_SEMANTIC_ROLES = (
    "claim",
    "insight",
    "mechanism",
    "emotional_beat",
    "transition",
)
ALLOWED_REVIEW_STATES = (
    "under_edit",
    "ready_for_review",
    "approved",
)
ALLOWED_REORDER_DIRECTIONS = ("up", "down")
ALLOWED_MERGE_DIRECTIONS = ("up", "down")
ALLOWED_OUTPUT_SUITABILITY = ("candidate", "strong", "weak", "not_suitable")
ALLOWED_MATCHING_ASSET_TYPES = (
    "film_asset_reference",
    "subtitle_reference",
    "transcript_reference",
    "other_prep_reference",
)
ALLOWED_CANDIDATE_REVIEW_STATUSES = (
    "tentative",
    "selected",
    "rejected",
)
ALLOWED_ROUGH_CUT_SUBSET_STATUSES = (
    "saved_only",
    "selected_for_current_rough_cut",
)


APPROVAL_READY_REASON = "Semantic map is ready for approval."
APPROVAL_BLOCK_REASON = "Approve is blocked until semantic review is moved to ready_for_review."
REOPEN_BLOCK_EDIT_REASON = "Approval was reopened because a semantic block changed after approval."
REOPEN_REORDER_REASON = "Approval was reopened because semantic block order changed after approval."
REOPEN_SOURCE_REASON = "Approval was reopened because the analysis source was replaced after approval."
REOPEN_STRUCTURE_REASON = "Approval was reopened because semantic block boundaries changed after approval."
REOPEN_SUITABILITY_REASON = "Approval was reopened because output suitability changed after approval."
SEVERE_WARNING_FLAGS = {"missing_title", "missing_semantic_role", "very_short_content"}
KEEP_EXISTING = object()
MANUAL_TIMECODE_PATTERN = re.compile(r"^(\d{2}):(\d{2}):(\d{2})$")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def slugify(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return normalized or "dna-project"


def parse_manual_timecode(value: str) -> int | None:
    match = MANUAL_TIMECODE_PATTERN.fullmatch(value)
    if match is None:
        return None
    hours, minutes, seconds = (int(part) for part in match.groups())
    if minutes >= 60 or seconds >= 60:
        return None
    return (hours * 3600) + (minutes * 60) + seconds


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def semantic_role_for(paragraph: str) -> str:
    lowered = paragraph.lower()
    if any(token in lowered for token in ("because", "therefore", "so that", "reveals how")):
        return "mechanism"
    if any(token in lowered for token in ("feel", "emotion", "fear", "love", "grief", "hope")):
        return "emotional_beat"
    if any(token in lowered for token in ("however", "but", "meanwhile", "then", "finally")):
        return "transition"
    if any(token in lowered for token in ("shows", "argues", "suggests", "demonstrates", "means")):
        return "insight"
    return "claim"


def title_for(paragraph: str) -> str:
    words = paragraph.split()
    return " ".join(words[:8]).strip(" .,;:") or "Untitled block"


def split_sentences(content: str) -> list[str]:
    normalized = re.sub(r"\s+", " ", content.strip())
    if not normalized:
        return []
    sentences = [chunk.strip() for chunk in re.split(r"(?<=[.!?])\s+", normalized) if chunk.strip()]
    return sentences or [normalized]


def describe_warning_flags(flags: list[str]) -> list[str]:
    labels = {
        "missing_title": "missing title",
        "weak_title": "weak title",
        "missing_semantic_role": "missing semantic role",
        "very_short_content": "very short content",
        "notes_recommended": "notes recommended",
    }
    return [labels.get(flag, flag.replace("_", " ")) for flag in flags]


def normalize_output_suitability(output_suitability: dict | None) -> dict:
    base = {
        "long_video": "candidate",
        "shorts_reels": "candidate",
        "carousel": "candidate",
        "packaging": "candidate",
    }
    if not output_suitability:
        return base
    normalized = dict(base)
    for key, value in output_suitability.items():
        if key in normalized and value in ALLOWED_OUTPUT_SUITABILITY:
            normalized[key] = value
    return normalized


def derive_warning_flags(block: dict) -> list[str]:
    flags: list[str] = []
    title = block.get("title", "").strip()
    role = block.get("semantic_role", "").strip()
    content = block.get("content", "").strip()
    notes = block.get("notes", "").strip()
    content_words = len(content.split())

    if not title:
        flags.append("missing_title")
    elif title.lower() == "untitled block" or len(title.split()) < 3:
        flags.append("weak_title")

    if not role:
        flags.append("missing_semantic_role")

    if content_words < 12:
        flags.append("very_short_content")

    if not notes and content_words >= 12:
        flags.append("notes_recommended")

    return flags


def normalize_semantic_blocks(semantic_blocks: list[dict]) -> list[dict]:
    normalized: list[dict] = []
    for index, block in enumerate(semantic_blocks, start=1):
        current = dict(block)
        current["sequence"] = index
        current["output_suitability"] = normalize_output_suitability(current.get("output_suitability"))
        current["warning_flags"] = derive_warning_flags(current)
        normalized.append(current)
    return normalized


def normalize_matching_candidate_stubs(matching_candidate_stubs: list[dict]) -> list[dict]:
    normalized: list[dict] = []
    for entry in matching_candidate_stubs:
        current = dict(entry)
        if current.get("review_status") not in ALLOWED_CANDIDATE_REVIEW_STATUSES:
            current["review_status"] = "tentative"
        current["preferred_rationale"] = current.get("preferred_rationale", "").strip()
        normalized.append(current)
    return normalized


def normalize_accepted_reference(accepted_reference: dict | None) -> dict | None:
    if not accepted_reference:
        return None
    current = dict(accepted_reference)
    current["acceptance_state"] = current.get("acceptance_state", "accepted_for_later_matching_work_only").strip() or "accepted_for_later_matching_work_only"
    current["accepted_from_candidate_review_status"] = current.get("accepted_from_candidate_review_status", "selected").strip() or "selected"
    return current


def normalize_accepted_scene_reference_stub(accepted_scene_reference_stub: dict | None) -> dict | None:
    if not accepted_scene_reference_stub:
        return None
    current = dict(accepted_scene_reference_stub)
    current["scene_reference_label"] = current.get("scene_reference_label", "").strip()
    current["scene_reference_state"] = current.get("scene_reference_state", "accepted_scene_reference_stub_for_later_timecode_prep_only").strip() or "accepted_scene_reference_stub_for_later_timecode_prep_only"
    return current


def normalize_timecode_range_stub(timecode_range_stub: dict | None) -> dict | None:
    if not timecode_range_stub:
        return None
    current = dict(timecode_range_stub)
    current["start_timecode"] = current.get("start_timecode", "").strip()
    current["end_timecode"] = current.get("end_timecode", "").strip()
    current["timecode_state"] = current.get("timecode_state", "provisional_timecode_range_for_later_assembly_only").strip() or "provisional_timecode_range_for_later_assembly_only"
    return current


def normalize_rough_cut_segment_stubs(rough_cut_segment_stubs: list[dict]) -> list[dict]:
    normalized: list[dict] = []
    for index, entry in enumerate(rough_cut_segment_stubs, start=1):
        current = dict(entry)
        current["segment_label"] = current.get("segment_label", "").strip()
        current["start_timecode"] = current.get("start_timecode", "").strip()
        current["end_timecode"] = current.get("end_timecode", "").strip()
        current["segment_state"] = current.get("segment_state", "provisional_rough_cut_segment_for_later_assembly_only").strip() or "provisional_rough_cut_segment_for_later_assembly_only"
        subset_status = current.get("subset_status", ALLOWED_ROUGH_CUT_SUBSET_STATUSES[0])
        if subset_status not in ALLOWED_ROUGH_CUT_SUBSET_STATUSES:
            subset_status = ALLOWED_ROUGH_CUT_SUBSET_STATUSES[0]
        current["subset_status"] = subset_status
        current["sequence"] = index
        normalized.append(current)
    return normalized


def semantic_completeness(intake_record: dict, semantic_blocks: list[dict]) -> tuple[str, int, int]:
    if intake_record.get("intake_readiness") != "ready" or not semantic_blocks:
        return ("Incomplete", 0, 0)
    issue_count = sum(len(block.get("warning_flags", [])) for block in semantic_blocks)
    blocks_with_issues = sum(1 for block in semantic_blocks if block.get("warning_flags"))
    has_severe = any(any(flag in SEVERE_WARNING_FLAGS for flag in block.get("warning_flags", [])) for block in semantic_blocks)
    if has_severe:
        return ("Incomplete", issue_count, blocks_with_issues)
    if issue_count:
        return ("Mixed", issue_count, blocks_with_issues)
    return ("Plausibly ready for review", 0, 0)


def completeness_readiness_hint(completeness_label: str) -> str:
    if completeness_label == "Incomplete":
        return "premature"
    if completeness_label == "Mixed":
        return "mixed"
    return "plausibly_reasonable"


def build_semantic_blocks(project_id: str, source_record_id: str, analysis_text: str) -> list[dict]:
    paragraphs = [chunk.strip() for chunk in re.split(r"\n\s*\n", analysis_text) if chunk.strip()]
    blocks: list[dict] = []
    for index, paragraph in enumerate(paragraphs, start=1):
        block_id = f"sb-{index:03d}"
        blocks.append(
            {
                "project_id": project_id,
                "record_id": block_id,
                "record_type": "semantic_block",
                "source_record_id": source_record_id,
                "sequence": index,
                "title": title_for(paragraph),
                "content": paragraph,
                "semantic_role": semantic_role_for(paragraph),
                "output_suitability": {
                    "long_video": "candidate",
                    "shorts_reels": "candidate",
                    "carousel": "candidate",
                    "packaging": "candidate",
                },
                "notes": "",
                "review_state": "proposed",
                "warning_flags": [],
            }
        )
    return normalize_semantic_blocks(blocks)


@dataclass
class ProjectSlice:
    project_dir: Path
    manifest: dict
    project_record: dict
    intake_record: dict
    analysis_source_record: dict | None
    semantic_review_record: dict
    semantic_blocks: list[dict]
    matching_prep_assets: list[dict]
    matching_candidate_stubs: list[dict]
    accepted_reference: dict | None
    accepted_scene_reference_stub: dict | None
    timecode_range_stub: dict | None
    rough_cut_segment_stubs: list[dict]


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
        semantic_review_record = self._default_review_record(project_id, created_at)

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
            semantic_review_record = self._default_review_record(manifest["project_id"], timestamp)

        semantic_blocks = read_json(semantic_record_path)["blocks"] if semantic_record_path.exists() else []
        semantic_blocks = normalize_semantic_blocks(semantic_blocks)
        matching_prep_assets = read_json(matching_prep_asset_path)["entries"] if matching_prep_asset_path.exists() else []
        matching_candidate_stubs = read_json(matching_candidate_path)["entries"] if matching_candidate_path.exists() else []
        matching_candidate_stubs = normalize_matching_candidate_stubs(matching_candidate_stubs)
        accepted_reference = normalize_accepted_reference(read_json(accepted_reference_path) if accepted_reference_path.exists() else None)
        accepted_scene_reference_stub = normalize_accepted_scene_reference_stub(read_json(accepted_scene_reference_stub_path) if accepted_scene_reference_stub_path.exists() else None)
        accepted_scene_reference_stub = self._reconcile_accepted_scene_reference_stub(accepted_scene_reference_stub, accepted_reference)
        timecode_range_stub = normalize_timecode_range_stub(read_json(timecode_range_stub_path) if timecode_range_stub_path.exists() else None)
        timecode_range_stub = self._reconcile_timecode_range_stub(timecode_range_stub, accepted_scene_reference_stub)
        rough_cut_segment_stubs = read_json(rough_cut_segments_path)["entries"] if rough_cut_segments_path.exists() else []
        rough_cut_segment_stubs = normalize_rough_cut_segment_stubs(rough_cut_segment_stubs)
        rough_cut_segment_stubs = self._reconcile_rough_cut_segment_stubs(rough_cut_segment_stubs, accepted_reference, accepted_scene_reference_stub, timecode_range_stub)
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
        self._mark_reopened_if_needed(semantic_review_record, REOPEN_SOURCE_REASON)
        semantic_review_record["updated_at"] = now

        self._apply_project_summary(project_record, intake_record, semantic_blocks, semantic_review_record)
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
        self._resequence_blocks(semantic_blocks)

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
        second_block["record_id"] = self._next_block_id(project.semantic_blocks)
        second_block["title"] = title_for(second_content)
        second_block["content"] = second_content
        second_block["notes"] = ""

        semantic_blocks = [dict(block) for block in project.semantic_blocks]
        semantic_blocks[current_index: current_index + 1] = [first_block, second_block]
        self._resequence_blocks(semantic_blocks)

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
        self._resequence_blocks(semantic_blocks)

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
        analysis_source_record = self._copy_analysis_record(project.analysis_source_record, now)
        semantic_review_record = dict(project.semantic_review_record)
        readiness = self._approval_readiness_label(project.intake_record, project.semantic_blocks, project.semantic_review_record)
        if clean_status == "approved" and readiness != "ready_for_approval":
            semantic_review_record["approval_block_reason"] = APPROVAL_BLOCK_REASON
            semantic_review_record["approval_transition_message"] = "Approval remains blocked until the map is explicitly ready for review."
            semantic_review_record["updated_at"] = now
            self._apply_project_summary(project_record, intake_record, project.semantic_blocks, semantic_review_record)
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

        self._apply_project_summary(project_record, intake_record, project.semantic_blocks, semantic_review_record)
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
        analysis_source_record = self._copy_analysis_record(project.analysis_source_record, now)
        semantic_review_record = dict(project.semantic_review_record)
        semantic_review_record["updated_at"] = now

        self._apply_project_summary(project_record, intake_record, project.semantic_blocks, semantic_review_record)
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
        analysis_source_record = self._copy_analysis_record(project.analysis_source_record, now)
        semantic_review_record = dict(project.semantic_review_record)
        semantic_review_record["updated_at"] = now

        self._apply_project_summary(project_record, intake_record, project.semantic_blocks, semantic_review_record)
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

        accepted_reference = self._reconcile_accepted_reference(project.accepted_reference, entries)
        manifest = dict(project.manifest)
        manifest["updated_at"] = now
        project_record = dict(project.project_record)
        project_record["updated_at"] = now
        intake_record = dict(project.intake_record)
        intake_record["updated_at"] = now
        analysis_source_record = self._copy_analysis_record(project.analysis_source_record, now)
        semantic_review_record = dict(project.semantic_review_record)
        semantic_review_record["updated_at"] = now

        self._apply_project_summary(project_record, intake_record, project.semantic_blocks, semantic_review_record)
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
        analysis_source_record = self._copy_analysis_record(project.analysis_source_record, now)
        semantic_review_record = dict(project.semantic_review_record)
        semantic_review_record["updated_at"] = now

        self._apply_project_summary(project_record, intake_record, project.semantic_blocks, semantic_review_record)
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
        analysis_source_record = self._copy_analysis_record(project.analysis_source_record, now)
        semantic_review_record = dict(project.semantic_review_record)
        semantic_review_record["updated_at"] = now

        self._apply_project_summary(project_record, intake_record, project.semantic_blocks, semantic_review_record)
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
        analysis_source_record = self._copy_analysis_record(project.analysis_source_record, now)
        semantic_review_record = dict(project.semantic_review_record)
        semantic_review_record["updated_at"] = now

        self._apply_project_summary(project_record, intake_record, project.semantic_blocks, semantic_review_record)
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
        analysis_source_record = self._copy_analysis_record(project.analysis_source_record, now)
        semantic_review_record = dict(project.semantic_review_record)
        semantic_review_record["updated_at"] = now

        self._apply_project_summary(project_record, intake_record, project.semantic_blocks, semantic_review_record)
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
        analysis_source_record = self._copy_analysis_record(project.analysis_source_record, now)
        semantic_review_record = dict(project.semantic_review_record)
        semantic_review_record["updated_at"] = now

        self._apply_project_summary(project_record, intake_record, project.semantic_blocks, semantic_review_record)
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
        analysis_source_record = self._copy_analysis_record(project.analysis_source_record, now)
        semantic_review_record = dict(project.semantic_review_record)
        semantic_review_record["updated_at"] = now

        self._apply_project_summary(project_record, intake_record, project.semantic_blocks, semantic_review_record)
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
        analysis_source_record = self._copy_analysis_record(project.analysis_source_record, now)
        semantic_review_record = dict(project.semantic_review_record)
        semantic_review_record["updated_at"] = now

        self._apply_project_summary(project_record, intake_record, project.semantic_blocks, semantic_review_record)
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

        accepted_reference = self._reconcile_accepted_reference(project.accepted_reference, entries)
        manifest = dict(project.manifest)
        manifest["updated_at"] = now
        project_record = dict(project.project_record)
        project_record["updated_at"] = now
        intake_record = dict(project.intake_record)
        intake_record["updated_at"] = now
        analysis_source_record = self._copy_analysis_record(project.analysis_source_record, now)
        semantic_review_record = dict(project.semantic_review_record)
        semantic_review_record["updated_at"] = now

        self._apply_project_summary(project_record, intake_record, project.semantic_blocks, semantic_review_record)
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

    def _reconcile_accepted_reference(
        self,
        accepted_reference: dict | None,
        matching_candidate_stubs: list[dict],
    ) -> dict | None:
        normalized_reference = normalize_accepted_reference(accepted_reference)
        if normalized_reference is None:
            return None
        source_candidate_stub_id = normalized_reference.get("source_candidate_stub_id", "").strip()
        if not source_candidate_stub_id:
            return None
        source_candidate = next((entry for entry in matching_candidate_stubs if entry.get("record_id") == source_candidate_stub_id), None)
        if source_candidate is None:
            return None
        if source_candidate.get("review_status", ALLOWED_CANDIDATE_REVIEW_STATUSES[0]) != "selected":
            return None
        updated_reference = dict(normalized_reference)
        updated_reference["semantic_block_id"] = source_candidate.get("semantic_block_id", "")
        updated_reference["prep_asset_id"] = source_candidate.get("prep_asset_id", "")
        return updated_reference

    def _reconcile_accepted_scene_reference_stub(
        self,
        accepted_scene_reference_stub: dict | None,
        accepted_reference: dict | None,
    ) -> dict | None:
        normalized_stub = normalize_accepted_scene_reference_stub(accepted_scene_reference_stub)
        if normalized_stub is None:
            return None
        normalized_reference = normalize_accepted_reference(accepted_reference)
        if normalized_reference is None:
            return None
        if normalized_stub.get("source_candidate_stub_id", "").strip() != normalized_reference.get("source_candidate_stub_id", "").strip():
            return None
        updated_stub = dict(normalized_stub)
        updated_stub["source_accepted_reference_id"] = normalized_reference.get("record_id", "")
        updated_stub["semantic_block_id"] = normalized_reference.get("semantic_block_id", "")
        updated_stub["prep_asset_id"] = normalized_reference.get("prep_asset_id", "")
        return updated_stub

    def _reconcile_timecode_range_stub(
        self,
        timecode_range_stub: dict | None,
        accepted_scene_reference_stub: dict | None,
    ) -> dict | None:
        normalized_stub = normalize_timecode_range_stub(timecode_range_stub)
        if normalized_stub is None:
            return None
        normalized_scene_reference_stub = normalize_accepted_scene_reference_stub(accepted_scene_reference_stub)
        if normalized_scene_reference_stub is None:
            return None
        if normalized_stub.get("source_candidate_stub_id", "").strip() != normalized_scene_reference_stub.get("source_candidate_stub_id", "").strip():
            return None
        updated_stub = dict(normalized_stub)
        updated_stub["source_accepted_scene_reference_stub_id"] = normalized_scene_reference_stub.get("record_id", "")
        updated_stub["semantic_block_id"] = normalized_scene_reference_stub.get("semantic_block_id", "")
        updated_stub["prep_asset_id"] = normalized_scene_reference_stub.get("prep_asset_id", "")
        return updated_stub

    def _reconcile_rough_cut_segment_stubs(
        self,
        rough_cut_segment_stubs: list[dict],
        accepted_reference: dict | None,
        accepted_scene_reference_stub: dict | None,
        timecode_range_stub: dict | None,
    ) -> list[dict]:
        normalized_reference = normalize_accepted_reference(accepted_reference)
        normalized_scene_reference_stub = normalize_accepted_scene_reference_stub(accepted_scene_reference_stub)
        normalized_timecode_range_stub = normalize_timecode_range_stub(timecode_range_stub)
        if normalized_reference is None or normalized_scene_reference_stub is None or normalized_timecode_range_stub is None:
            return []
        current_source_candidate_stub_id = normalized_reference.get("source_candidate_stub_id", "").strip()
        if not current_source_candidate_stub_id:
            return []
        reconciled: list[dict] = []
        for entry in normalize_rough_cut_segment_stubs(rough_cut_segment_stubs):
            if entry.get("source_candidate_stub_id", "").strip() != current_source_candidate_stub_id:
                continue
            if entry.get("source_timecode_range_stub_id", "").strip() and entry.get("source_timecode_range_stub_id", "").strip() != normalized_timecode_range_stub.get("record_id", "").strip():
                continue
            updated_entry = dict(entry)
            updated_entry["source_accepted_reference_id"] = normalized_reference.get("record_id", "")
            updated_entry["source_accepted_scene_reference_stub_id"] = normalized_scene_reference_stub.get("record_id", "")
            updated_entry["source_timecode_range_stub_id"] = normalized_timecode_range_stub.get("record_id", "")
            updated_entry["source_candidate_stub_id"] = current_source_candidate_stub_id
            updated_entry["semantic_block_id"] = normalized_reference.get("semantic_block_id", "")
            updated_entry["prep_asset_id"] = normalized_reference.get("prep_asset_id", "")
            updated_entry["start_timecode"] = normalized_timecode_range_stub.get("start_timecode", "")
            updated_entry["end_timecode"] = normalized_timecode_range_stub.get("end_timecode", "")
            reconciled.append(updated_entry)
        return normalize_rough_cut_segment_stubs(reconciled)

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
        analysis_source_record = self._copy_analysis_record(project.analysis_source_record, now)
        semantic_review_record = dict(project.semantic_review_record)
        self._mark_reopened_if_needed(semantic_review_record, reopen_reason)
        semantic_review_record["updated_at"] = now

        self._apply_project_summary(project_record, intake_record, semantic_blocks, semantic_review_record)
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
        if analysis_source_record is None:
            return None
        updated = dict(analysis_source_record)
        updated["updated_at"] = now
        return updated

    def _next_block_id(self, semantic_blocks: list[dict]) -> str:
        max_seen = 0
        for block in semantic_blocks:
            match = re.fullmatch(r"sb-(\d+)", block.get("record_id", ""))
            if match:
                max_seen = max(max_seen, int(match.group(1)))
        return f"sb-{max_seen + 1:03d}"

    def _resequence_blocks(self, semantic_blocks: list[dict]) -> None:
        for index, block in enumerate(semantic_blocks, start=1):
            block["sequence"] = index

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
    ) -> None:
        semantic_blocks = normalize_semantic_blocks(semantic_blocks)
        accepted_reference_path = project_dir / "records" / "matching_prep" / ACCEPTED_REFERENCE_FILENAME
        accepted_scene_reference_stub_path = project_dir / "records" / "scene_matching" / ACCEPTED_SCENE_REFERENCE_STUB_FILENAME
        timecode_range_stub_path = project_dir / "records" / "scene_matching" / TIMECODE_RANGE_STUB_FILENAME
        rough_cut_segments_path = project_dir / "records" / "rough_cut" / ROUGH_CUT_SEGMENTS_FILENAME
        if accepted_reference is KEEP_EXISTING:
            accepted_reference_payload = normalize_accepted_reference(read_json(accepted_reference_path) if accepted_reference_path.exists() else None)
        else:
            accepted_reference_payload = normalize_accepted_reference(accepted_reference if isinstance(accepted_reference, dict) else None)
        if accepted_scene_reference_stub is KEEP_EXISTING:
            accepted_scene_reference_stub_payload = normalize_accepted_scene_reference_stub(read_json(accepted_scene_reference_stub_path) if accepted_scene_reference_stub_path.exists() else None)
        else:
            accepted_scene_reference_stub_payload = normalize_accepted_scene_reference_stub(accepted_scene_reference_stub if isinstance(accepted_scene_reference_stub, dict) else None)
        accepted_scene_reference_stub_payload = self._reconcile_accepted_scene_reference_stub(accepted_scene_reference_stub_payload, accepted_reference_payload)
        if timecode_range_stub is KEEP_EXISTING:
            timecode_range_stub_payload = normalize_timecode_range_stub(read_json(timecode_range_stub_path) if timecode_range_stub_path.exists() else None)
        else:
            timecode_range_stub_payload = normalize_timecode_range_stub(timecode_range_stub if isinstance(timecode_range_stub, dict) else None)
        timecode_range_stub_payload = self._reconcile_timecode_range_stub(timecode_range_stub_payload, accepted_scene_reference_stub_payload)
        if rough_cut_segment_stubs is KEEP_EXISTING:
            rough_cut_segment_entries = read_json(rough_cut_segments_path)["entries"] if rough_cut_segments_path.exists() else []
        else:
            rough_cut_segment_entries = list(rough_cut_segment_stubs) if isinstance(rough_cut_segment_stubs, list) else []
        rough_cut_segment_entries = self._reconcile_rough_cut_segment_stubs(rough_cut_segment_entries, accepted_reference_payload, accepted_scene_reference_stub_payload, timecode_range_stub_payload)
        write_json(project_dir / "project.manifest", manifest)
        write_json(project_dir / "project.meta" / "status.json", self._status_payload(project_record, intake_record, semantic_review_record, semantic_blocks))
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

    def _status_payload(
        self,
        project_record: dict,
        intake_record: dict,
        semantic_review_record: dict,
        semantic_blocks: list[dict],
    ) -> dict:
        completeness_label, issue_count, blocks_with_issues = semantic_completeness(intake_record, semantic_blocks)
        return {
            "project_status": project_record["project_status"],
            "current_readiness_summary": project_record["current_readiness_summary"],
            "intake_readiness": intake_record["intake_readiness"],
            "semantic_block_count": len(semantic_blocks),
            "semantic_map_status": semantic_review_record["review_status"],
            "semantic_review_approved": semantic_review_record["approved"],
            "semantic_completeness": completeness_label,
            "semantic_issue_count": issue_count,
            "blocks_with_issues": blocks_with_issues,
            "approval_readiness": self._approval_readiness_label(intake_record, semantic_blocks, semantic_review_record),
            "approval_block_reason": semantic_review_record.get("approval_block_reason", ""),
            "approval_transition_message": semantic_review_record.get("approval_transition_message", ""),
            "reopened_after_change": semantic_review_record.get("reopened_after_change", False),
            "reopen_reason": semantic_review_record.get("reopen_reason", ""),
            "updated_at": project_record["updated_at"],
        }

    def _apply_project_summary(
        self,
        project_record: dict,
        intake_record: dict,
        semantic_blocks: list[dict],
        semantic_review_record: dict,
    ) -> None:
        if intake_record["intake_readiness"] != "ready" or not semantic_blocks:
            project_record["project_status"] = "intake_required"
            project_record["current_readiness_summary"] = "Load analysis text to unlock semantic map."
            return

        review_status = semantic_review_record["review_status"]
        block_count = len(semantic_blocks)
        completeness_label, issue_count, blocks_with_issues = semantic_completeness(intake_record, semantic_blocks)
        readiness = self._approval_readiness_label(intake_record, semantic_blocks, semantic_review_record)
        issue_summary = f"Completeness: {completeness_label}. Issues: {issue_count} across {blocks_with_issues} block(s)."
        if review_status == "approved":
            project_record["project_status"] = "semantic_map_approved"
            project_record["current_readiness_summary"] = f"{block_count} semantic blocks approved for later matching prep. {issue_summary}"
        elif semantic_review_record.get("reopened_after_change"):
            project_record["project_status"] = "semantic_map_reopened"
            project_record["current_readiness_summary"] = f"{block_count} semantic blocks reopened after change. Readiness: {readiness}. {issue_summary}"
        elif review_status == "ready_for_review":
            project_record["project_status"] = "semantic_map_ready_for_review"
            project_record["current_readiness_summary"] = f"{block_count} semantic blocks ready for approval review. Readiness: {readiness}. {issue_summary}"
        else:
            project_record["project_status"] = "semantic_map_under_edit"
            project_record["current_readiness_summary"] = f"{block_count} semantic blocks under edit in Semantic Map Workspace. Readiness: {readiness}. {issue_summary}"

    def _approval_readiness_label(
        self,
        intake_record: dict,
        semantic_blocks: list[dict],
        semantic_review_record: dict,
    ) -> str:
        if intake_record["intake_readiness"] != "ready" or not semantic_blocks:
            return "not_ready"
        if semantic_review_record["review_status"] == "approved":
            return "approved"
        if semantic_review_record["review_status"] == "ready_for_review":
            return "ready_for_approval"
        if semantic_review_record.get("reopened_after_change"):
            return "reopened_after_change"
        completeness_label, _, _ = semantic_completeness(intake_record, semantic_blocks)
        return completeness_readiness_hint(completeness_label)

    def _mark_reopened_if_needed(self, semantic_review_record: dict, reopen_reason: str) -> None:
        if semantic_review_record.get("review_status") == "approved":
            semantic_review_record["review_status"] = "under_edit"
            semantic_review_record["approved"] = False
            semantic_review_record["reopened_after_change"] = True
            semantic_review_record["reopen_reason"] = reopen_reason
            semantic_review_record["approval_transition_message"] = "Semantic approval was reopened after a change."
            semantic_review_record["approval_block_reason"] = APPROVAL_BLOCK_REASON
        else:
            semantic_review_record.setdefault("reopened_after_change", False)
            semantic_review_record.setdefault("reopen_reason", "")
            if semantic_review_record.get("review_status") == "under_edit":
                semantic_review_record["approval_transition_message"] = semantic_review_record.get("approval_transition_message") or "Semantic map remains under edit."

    def _default_review_record(self, project_id: str, timestamp: str) -> dict:
        return {
            "project_id": project_id,
            "record_id": "semantic-review-record",
            "record_type": "semantic_review_state",
            "review_status": "under_edit",
            "approved": False,
            "approval_block_reason": APPROVAL_BLOCK_REASON,
            "approval_transition_message": "Semantic map remains under edit.",
            "reopened_after_change": False,
            "reopen_reason": "",
            "created_at": timestamp,
            "updated_at": timestamp,
        }
