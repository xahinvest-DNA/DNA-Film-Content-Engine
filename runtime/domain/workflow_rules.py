from __future__ import annotations

from runtime.domain.semantic_rules import ALLOWED_REVIEW_STATES


def default_review_record(project_id: str, timestamp: str) -> dict:
    return {
        "project_id": project_id,
        "record_id": "semantic-review-record",
        "record_type": "semantic_review_state",
        "review_status": "under_edit",
        "approval_state": "under_edit",
        "approved": False,
        "editor_state": "under_edit",
        "issue_summary": "Analysis source has not been loaded yet.",
        "created_at": timestamp,
        "updated_at": timestamp,
    }


def mark_review_under_edit(review_record: dict, timestamp: str, issue_summary: str) -> None:
    review_record["review_status"] = "under_edit"
    review_record["approval_state"] = "under_edit"
    review_record["approved"] = False
    review_record["editor_state"] = "under_edit"
    review_record["issue_summary"] = issue_summary
    review_record["updated_at"] = timestamp


def apply_project_summary(
    project_record: dict,
    intake_record: dict,
    analysis_source_record: dict | None,
    semantic_blocks: list[dict],
    semantic_review_record: dict,
) -> None:
    if analysis_source_record is None or intake_record.get("intake_readiness") != "ready":
        project_record["project_status"] = "project_created"
        project_record["current_readiness_summary"] = "Project created. Load primary analysis text to generate the semantic map."
        return

    block_count = len(semantic_blocks)
    review_status = semantic_review_record["review_status"]
    if review_status == "approved":
        project_record["project_status"] = "semantic_map_approved"
        project_record["current_readiness_summary"] = f"{block_count} semantic blocks saved locally and approved for the current MVP slice."
    elif review_status == "ready_for_review":
        project_record["project_status"] = "semantic_map_ready_for_review"
        project_record["current_readiness_summary"] = f"{block_count} semantic blocks saved locally and marked ready for review."
    else:
        project_record["project_status"] = "semantic_map_under_edit"
        project_record["current_readiness_summary"] = f"{block_count} semantic blocks saved locally and currently under edit in the Semantic Map Workspace."


def status_payload(
    project_record: dict,
    intake_record: dict,
    analysis_source_record: dict | None,
    semantic_blocks: list[dict],
    semantic_review_record: dict,
) -> dict:
    return {
        "project_created": True,
        "project_status": project_record["project_status"],
        "source_loaded": analysis_source_record is not None,
        "source_record_id": (analysis_source_record or {}).get("record_id"),
        "semantic_blocks_created": bool(semantic_blocks),
        "semantic_block_count": len(semantic_blocks),
        "current_approval_state": semantic_review_record["review_status"],
        "current_edit_state": semantic_review_record.get("editor_state", "under_edit"),
        "intake_readiness": intake_record["intake_readiness"],
        "last_saved_at": project_record["updated_at"],
        "status_message": project_record["current_readiness_summary"],
    }


def normalize_review_status(value: str) -> str:
    clean_value = value.strip()
    if clean_value not in ALLOWED_REVIEW_STATES:
        raise ValueError("Review status is invalid for this F-006A slice.")
    return clean_value
