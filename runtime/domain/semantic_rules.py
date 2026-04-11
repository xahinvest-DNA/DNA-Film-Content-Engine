from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone


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


def normalize_packaging_script_bundle(packaging_script_bundle: dict | None) -> dict | None:
    if not packaging_script_bundle:
        return None
    current = dict(packaging_script_bundle)
    current["title"] = current.get("title", "").strip()
    current["builder_id"] = current.get("builder_id", "packaging_script_bundle_v1").strip() or "packaging_script_bundle_v1"
    current["source_focus_mode"] = current.get("source_focus_mode", "all_saved_segments").strip() or "all_saved_segments"
    current["source_candidate_stub_id"] = current.get("source_candidate_stub_id", "").strip()
    current["artifact_relative_path"] = current.get("artifact_relative_path", "outputs/packaging/packaging_script_bundle.md").strip() or "outputs/packaging/packaging_script_bundle.md"
    current["markdown_content"] = current.get("markdown_content", "")
    current["source_rough_cut_segment_ids"] = list(current.get("source_rough_cut_segment_ids", []))
    current["segments"] = list(current.get("segments", []))
    current["segment_count"] = len(current["segments"])
    return current


def semantic_completeness(intake_record: dict, semantic_blocks: list[dict]) -> tuple[str, int, int]:
    if intake_record.get("intake_readiness") != "ready" or not semantic_blocks:
        return ("Incomplete", 0, 0)
    issue_count = sum(len(block.get("warning_flags", [])) for block in semantic_blocks)
    blocks_with_issues = sum(1 for block in semantic_blocks if block.get("warning_flags"))
    if issue_count == 0:
        return ("Plausibly ready for review", 0, 0)
    if any(any(flag in SEVERE_WARNING_FLAGS for flag in block.get("warning_flags", [])) for block in semantic_blocks):
        return ("Incomplete", issue_count, blocks_with_issues)
    return ("Needs tightening", issue_count, blocks_with_issues)


def completeness_readiness_hint(completeness_label: str) -> str:
    if completeness_label == "Plausibly ready for review":
        return "plausibly_reasonable"
    if completeness_label == "Needs tightening":
        return "mixed"
    return "premature"


def build_semantic_blocks(project_id: str, source_record_id: str, analysis_text: str) -> list[dict]:
    paragraphs = [paragraph.strip() for paragraph in analysis_text.replace("\r\n", "\n").split("\n\n") if paragraph.strip()]
    blocks: list[dict] = []
    for index, paragraph in enumerate(paragraphs, start=1):
        blocks.append(
            {
                "project_id": project_id,
                "record_id": f"sb-{index:03d}",
                "record_type": "semantic_block",
                "source_record_id": source_record_id,
                "sequence": index,
                "title": title_for(paragraph),
                "semantic_role": semantic_role_for(paragraph),
                "content": paragraph,
                "notes": "",
                "output_suitability": normalize_output_suitability(None),
                "warning_flags": [],
                "semantic_unit_id": str(uuid.uuid4()),
            }
        )
    return normalize_semantic_blocks(blocks)


def copy_analysis_record(analysis_source_record: dict | None, now: str) -> dict | None:
    if analysis_source_record is None:
        return None
    updated = dict(analysis_source_record)
    updated["updated_at"] = now
    return updated


def next_block_id(semantic_blocks: list[dict]) -> str:
    max_seen = 0
    for block in semantic_blocks:
        match = re.fullmatch(r"sb-(\d+)", block.get("record_id", ""))
        if match:
            max_seen = max(max_seen, int(match.group(1)))
    return f"sb-{max_seen + 1:03d}"


def resequence_blocks(semantic_blocks: list[dict]) -> None:
    for index, block in enumerate(semantic_blocks, start=1):
        block["sequence"] = index
