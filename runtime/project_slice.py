from __future__ import annotations

import json
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


PROJECT_FORMAT_VERSION = "0.3"
ANALYSIS_RECORD_FILENAME = "analysis_source.json"
REVIEW_RECORD_FILENAME = "semantic_review.json"
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
    return blocks


@dataclass
class ProjectSlice:
    project_dir: Path
    manifest: dict
    project_record: dict
    intake_record: dict
    analysis_source_record: dict | None
    semantic_review_record: dict
    semantic_blocks: list[dict]


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

        self._write_project_state(project_dir, manifest, project_record, intake_record, None, semantic_review_record, [])
        return self.load_project(project_dir)

    def load_project(self, project_dir: Path) -> ProjectSlice:
        manifest = read_json(project_dir / "project.manifest")
        project_record = read_json(project_dir / "records" / "project" / "project.json")
        intake_record = read_json(project_dir / "records" / "intake" / "intake.json")
        analysis_record_path = project_dir / "records" / "intake" / ANALYSIS_RECORD_FILENAME
        legacy_analysis_record_path = project_dir / "records" / "intake" / "analysis.txt.json"
        semantic_record_path = project_dir / "records" / "semantic" / "semantic_blocks.json"
        review_record_path = project_dir / "records" / "review" / REVIEW_RECORD_FILENAME

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
        return ProjectSlice(
            project_dir=project_dir,
            manifest=manifest,
            project_record=project_record,
            intake_record=intake_record,
            analysis_source_record=analysis_source_record,
            semantic_review_record=semantic_review_record,
            semantic_blocks=semantic_blocks,
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
        semantic_review_record["review_status"] = "under_edit"
        semantic_review_record["approved"] = False
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
    ) -> ProjectSlice:
        clean_title = title.strip()
        clean_role = semantic_role.strip()
        if not clean_title:
            raise ValueError("Block title is required.")
        if clean_role not in ALLOWED_SEMANTIC_ROLES:
            raise ValueError("Semantic role is invalid for this MVP slice.")

        project = self.load_project(project_dir)
        now = utc_now()
        updated = False
        semantic_blocks: list[dict] = []
        for block in project.semantic_blocks:
            current = dict(block)
            if current["record_id"] == block_id:
                current["title"] = clean_title
                current["semantic_role"] = clean_role
                current["notes"] = notes.strip()
                updated = True
            semantic_blocks.append(current)

        if not updated:
            raise ValueError("Selected semantic block was not found.")

        manifest = dict(project.manifest)
        manifest["updated_at"] = now
        project_record = dict(project.project_record)
        project_record["updated_at"] = now
        intake_record = dict(project.intake_record)
        intake_record["updated_at"] = now
        analysis_source_record = project.analysis_source_record
        if analysis_source_record is not None:
            analysis_source_record = dict(analysis_source_record)
            analysis_source_record["updated_at"] = now

        semantic_review_record = dict(project.semantic_review_record)
        if semantic_review_record["review_status"] == "approved":
            semantic_review_record["review_status"] = "under_edit"
            semantic_review_record["approved"] = False
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
        )
        return self.load_project(project_dir)

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
        for index, block in enumerate(semantic_blocks, start=1):
            block["sequence"] = index

        now = utc_now()
        manifest = dict(project.manifest)
        manifest["updated_at"] = now
        project_record = dict(project.project_record)
        project_record["updated_at"] = now
        intake_record = dict(project.intake_record)
        intake_record["updated_at"] = now
        analysis_source_record = project.analysis_source_record
        if analysis_source_record is not None:
            analysis_source_record = dict(analysis_source_record)
            analysis_source_record["updated_at"] = now

        semantic_review_record = dict(project.semantic_review_record)
        if semantic_review_record["review_status"] == "approved":
            semantic_review_record["review_status"] = "under_edit"
            semantic_review_record["approved"] = False
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
        )
        return self.load_project(project_dir)

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
        analysis_source_record = project.analysis_source_record
        if analysis_source_record is not None:
            analysis_source_record = dict(analysis_source_record)
            analysis_source_record["updated_at"] = now
        semantic_review_record = dict(project.semantic_review_record)
        semantic_review_record["review_status"] = clean_status
        semantic_review_record["approved"] = clean_status == "approved"
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
        )
        return self.load_project(project_dir)

    def _write_project_state(
        self,
        project_dir: Path,
        manifest: dict,
        project_record: dict,
        intake_record: dict,
        analysis_source_record: dict | None,
        semantic_review_record: dict,
        semantic_blocks: list[dict],
    ) -> None:
        write_json(project_dir / "project.manifest", manifest)
        write_json(project_dir / "project.meta" / "status.json", self._status_payload(project_record, intake_record, semantic_review_record, semantic_blocks))
        write_json(project_dir / "records" / "project" / "project.json", project_record)
        write_json(project_dir / "records" / "intake" / "intake.json", intake_record)
        if analysis_source_record is not None:
            write_json(project_dir / "records" / "intake" / ANALYSIS_RECORD_FILENAME, analysis_source_record)
        write_json(project_dir / "records" / "review" / REVIEW_RECORD_FILENAME, semantic_review_record)
        write_json(project_dir / "records" / "semantic" / "semantic_blocks.json", {"blocks": semantic_blocks})

    def _status_payload(
        self,
        project_record: dict,
        intake_record: dict,
        semantic_review_record: dict,
        semantic_blocks: list[dict],
    ) -> dict:
        return {
            "project_status": project_record["project_status"],
            "current_readiness_summary": project_record["current_readiness_summary"],
            "intake_readiness": intake_record["intake_readiness"],
            "semantic_block_count": len(semantic_blocks),
            "semantic_map_status": semantic_review_record["review_status"],
            "semantic_review_approved": semantic_review_record["approved"],
            "approval_readiness": self._approval_readiness_label(intake_record, semantic_blocks, semantic_review_record),
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
        readiness = self._approval_readiness_label(intake_record, semantic_blocks, semantic_review_record)
        if review_status == "approved":
            project_record["project_status"] = "semantic_map_approved"
            project_record["current_readiness_summary"] = f"{block_count} semantic blocks approved for later matching prep."
        elif review_status == "ready_for_review":
            project_record["project_status"] = "semantic_map_ready_for_review"
            project_record["current_readiness_summary"] = f"{block_count} semantic blocks ready for approval review. Readiness: {readiness}."
        else:
            project_record["project_status"] = "semantic_map_under_edit"
            project_record["current_readiness_summary"] = f"{block_count} semantic blocks under edit in Semantic Map Workspace. Readiness: {readiness}."

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
        complete_blocks = all(block.get("title", "").strip() and block.get("semantic_role", "").strip() for block in semantic_blocks)
        if complete_blocks:
            return "editable_but_complete"
        return "under_edit"

    def _default_review_record(self, project_id: str, timestamp: str) -> dict:
        return {
            "project_id": project_id,
            "record_id": "semantic-review-record",
            "record_type": "semantic_review_state",
            "review_status": "under_edit",
            "approved": False,
            "created_at": timestamp,
            "updated_at": timestamp,
        }
