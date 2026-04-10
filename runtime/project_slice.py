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


APPROVAL_READY_REASON = "Semantic map is ready for approval."
APPROVAL_BLOCK_REASON = "Approve is blocked until semantic review is moved to ready_for_review."
REOPEN_BLOCK_EDIT_REASON = "Approval was reopened because a semantic block changed after approval."
REOPEN_REORDER_REASON = "Approval was reopened because semantic block order changed after approval."
REOPEN_SOURCE_REASON = "Approval was reopened because the analysis source was replaced after approval."
REOPEN_STRUCTURE_REASON = "Approval was reopened because semantic block boundaries changed after approval."
REOPEN_SUITABILITY_REASON = "Approval was reopened because output suitability changed after approval."
SEVERE_WARNING_FLAGS = {"missing_title", "missing_semantic_role", "very_short_content"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def slugify(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return normalized or "dna-project"


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
    ) -> None:
        semantic_blocks = normalize_semantic_blocks(semantic_blocks)
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
