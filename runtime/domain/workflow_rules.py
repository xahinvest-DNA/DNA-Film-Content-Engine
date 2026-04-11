from __future__ import annotations

from pathlib import Path

from runtime.builders.packaging import packaging_bundle_source_segments
from runtime.domain.project_types import ProjectSlice
from runtime.domain.semantic_rules import (
    ALLOWED_CANDIDATE_REVIEW_STATUSES,
    APPROVAL_BLOCK_REASON,
    completeness_readiness_hint,
    normalize_accepted_reference,
    normalize_accepted_scene_reference_stub,
    normalize_packaging_script_bundle,
    normalize_rough_cut_segment_stubs,
    normalize_timecode_range_stub,
    semantic_completeness,
)


def reconcile_accepted_reference(
    accepted_reference: dict | None,
    matching_candidate_stubs: list[dict],
    semantic_review_record: dict,
) -> dict | None:
    if semantic_review_record.get("review_status") != "approved" or semantic_review_record.get("reopened_after_change"):
        return None
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


def reconcile_accepted_scene_reference_stub(
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


def builder_gate(project: ProjectSlice) -> tuple[str, str]:
    if project.accepted_reference is None:
        return ("blocked", "no accepted reference available yet")
    if project.accepted_scene_reference_stub is None:
        return ("blocked", "no accepted scene reference stub available yet")
    if project.timecode_range_stub is None:
        return ("blocked", "no timecode range stub available yet")
    if not project.rough_cut_segment_stubs:
        return ("blocked", "no rough-cut segment set available yet")
    return ("ready", "rough-cut handoff can now produce a packaging-ready script bundle")


def reconcile_timecode_range_stub(
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


def reconcile_rough_cut_segment_stubs(
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


def reconcile_packaging_script_bundle(
    packaging_script_bundle: dict | None,
    rough_cut_segment_stubs: list[dict],
    accepted_reference: dict | None,
    accepted_scene_reference_stub: dict | None,
    timecode_range_stub: dict | None,
) -> dict | None:
    normalized_bundle = normalize_packaging_script_bundle(packaging_script_bundle)
    if normalized_bundle is None:
        return None
    if accepted_reference is None or accepted_scene_reference_stub is None or timecode_range_stub is None:
        return None
    if normalized_bundle.get("source_candidate_stub_id", "").strip() != accepted_reference.get("source_candidate_stub_id", "").strip():
        return None

    current_project = ProjectSlice(
        project_dir=Path(),
        manifest={},
        project_record={},
        intake_record={},
        analysis_source_record=None,
        semantic_review_record={},
        semantic_blocks=[],
        matching_prep_assets=[],
        matching_candidate_stubs=[],
        accepted_reference=accepted_reference,
        accepted_scene_reference_stub=accepted_scene_reference_stub,
        timecode_range_stub=timecode_range_stub,
        rough_cut_segment_stubs=rough_cut_segment_stubs,
        packaging_script_bundle=None,
    )
    current_focus_mode, current_segments = packaging_bundle_source_segments(current_project)
    current_segment_ids = [entry["record_id"] for entry in current_segments]
    if normalized_bundle.get("source_focus_mode", "") != current_focus_mode:
        return None
    if normalized_bundle.get("source_rough_cut_segment_ids", []) != current_segment_ids:
        return None
    normalized_bundle["segment_count"] = len(normalized_bundle.get("segments", []))
    return normalized_bundle


def status_payload(
    project_record: dict,
    intake_record: dict,
    semantic_review_record: dict,
    semantic_blocks: list[dict],
    packaging_script_bundle: dict | None = None,
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
        "approval_readiness": approval_readiness_label(intake_record, semantic_blocks, semantic_review_record),
        "approval_block_reason": semantic_review_record.get("approval_block_reason", ""),
        "approval_transition_message": semantic_review_record.get("approval_transition_message", ""),
        "reopened_after_change": semantic_review_record.get("reopened_after_change", False),
        "reopen_reason": semantic_review_record.get("reopen_reason", ""),
        "packaging_script_bundle_ready": packaging_script_bundle is not None,
        "updated_at": project_record["updated_at"],
    }


def apply_project_summary(
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
    readiness = approval_readiness_label(intake_record, semantic_blocks, semantic_review_record)
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


def approval_readiness_label(
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


def mark_reopened_if_needed(semantic_review_record: dict, reopen_reason: str) -> None:
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


def default_review_record(project_id: str, timestamp: str) -> dict:
    return {
        "project_id": project_id,
        "record_id": "semantic-review-record",
        "record_type": "semantic_review_state",
        "review_status": "under_edit",
        "approved": False,
        "approval_ready": False,
        "approval_transition_message": "Semantic map remains under edit.",
        "approval_block_reason": APPROVAL_BLOCK_REASON,
        "reopened_after_change": False,
        "reopen_reason": "",
        "created_at": timestamp,
        "updated_at": timestamp,
    }
