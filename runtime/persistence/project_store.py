from __future__ import annotations

import uuid
from pathlib import Path

from runtime.domain.project_types import ProjectSlice
from runtime.domain.semantic_rules import (
    ALLOWED_OUTPUT_SUITABILITY,
    ALLOWED_REVIEW_STATES,
    ALLOWED_SEMANTIC_ROLES,
    BOOTSTRAP_STRATEGY,
    build_semantic_blocks,
    normalize_output_suitability,
    normalize_text,
    slugify,
    utc_now,
)
from runtime.domain.workflow_rules import (
    apply_project_summary,
    default_review_record,
    mark_review_under_edit,
    normalize_review_status,
    status_payload,
)
from runtime.persistence.json_store import read_json, write_json


PROJECT_FORMAT_VERSION = "0.1"
PROJECT_RECORD_FILENAME = "project.json"
INTAKE_RECORD_FILENAME = "intake.json"
ANALYSIS_RECORD_FILENAME = "analysis_source.json"
SEMANTIC_BLOCKS_FILENAME = "semantic_blocks.json"
REVIEW_RECORD_FILENAME = "semantic_review.json"
BOOTSTRAP_FILENAME = "provisional_bootstrap.json"
STATUS_FILENAME = "status.json"
KEEP_EXISTING = object()


class ProjectSliceStore:
    def __init__(self, workspace_root: Path) -> None:
        self.workspace_root = workspace_root

    def create_project(self, title: str, film_title: str = "", language: str = "en") -> ProjectSlice:
        clean_title = title.strip()
        if not clean_title:
            raise ValueError("Project title is required.")

        project_id = f"project-{uuid.uuid4().hex[:8]}"
        folder_name = f"{slugify(clean_title)}-{project_id[-4:]}"
        project_dir = self.workspace_root / folder_name
        project_dir.mkdir(parents=True, exist_ok=False)
        self._ensure_package_dirs(project_dir)

        created_at = utc_now()
        manifest = {
            "project_id": project_id,
            "project_format_version": PROJECT_FORMAT_VERSION,
            "project_title": clean_title,
            "created_at": created_at,
            "updated_at": created_at,
            "primary_project_record": f"records/project/{PROJECT_RECORD_FILENAME}",
            "primary_intake_record": f"records/intake/{INTAKE_RECORD_FILENAME}",
            "primary_analysis_source_record": None,
            "primary_semantic_record_set": f"records/semantic/{SEMANTIC_BLOCKS_FILENAME}",
            "primary_review_record": f"records/review/{REVIEW_RECORD_FILENAME}",
        }
        project_record = {
            "project_id": project_id,
            "record_id": "project-record",
            "record_type": "project",
            "title": clean_title,
            "film_title": film_title.strip(),
            "language": language.strip() or "en",
            "project_status": "project_created",
            "current_readiness_summary": "Project created. Load primary analysis text to generate the semantic map.",
            "created_at": created_at,
            "updated_at": created_at,
        }
        intake_record = {
            "project_id": project_id,
            "record_id": "intake-record",
            "record_type": "intake_package",
            "primary_analysis_source_reference": None,
            "attached_source_references": [],
            "intake_readiness": "blocked",
            "intake_warnings": ["Primary analysis text has not been loaded yet."],
            "created_at": created_at,
            "updated_at": created_at,
        }
        review_record = default_review_record(project_id, created_at)

        self._write_project_state(
            project_dir,
            manifest,
            project_record,
            intake_record,
            None,
            review_record,
            [],
            None,
        )
        return self.load_project(project_dir)

    def load_project(self, project_dir: Path) -> ProjectSlice:
        manifest_path = project_dir / "project.manifest"
        project_record_path = project_dir / "records" / "project" / PROJECT_RECORD_FILENAME
        intake_record_path = project_dir / "records" / "intake" / INTAKE_RECORD_FILENAME
        review_record_path = project_dir / "records" / "review" / REVIEW_RECORD_FILENAME
        semantic_blocks_path = project_dir / "records" / "semantic" / SEMANTIC_BLOCKS_FILENAME

        if not manifest_path.exists() or not project_record_path.exists() or not intake_record_path.exists():
            raise FileNotFoundError("Selected folder does not look like a DNA project package.")

        manifest = read_json(manifest_path)
        project_record = read_json(project_record_path)
        intake_record = read_json(intake_record_path)
        semantic_review_record = read_json(review_record_path) if review_record_path.exists() else default_review_record(
            manifest["project_id"],
            project_record.get("updated_at", utc_now()),
        )
        analysis_path = project_dir / "records" / "intake" / ANALYSIS_RECORD_FILENAME
        bootstrap_path = project_dir / "derived" / "semantic" / BOOTSTRAP_FILENAME
        status_path = project_dir / "project.meta" / STATUS_FILENAME

        analysis_source_record = read_json(analysis_path) if analysis_path.exists() else None
        semantic_blocks_payload = read_json(semantic_blocks_path) if semantic_blocks_path.exists() else {"blocks": []}
        semantic_blocks = list(semantic_blocks_payload.get("blocks", []))
        semantic_bootstrap_artifact = read_json(bootstrap_path) if bootstrap_path.exists() else None

        apply_project_summary(project_record, intake_record, analysis_source_record, semantic_blocks, semantic_review_record)
        expected_status = status_payload(
            project_record,
            intake_record,
            analysis_source_record,
            semantic_blocks,
            semantic_review_record,
        )
        current_status = read_json(status_path) if status_path.exists() else None
        if current_status != expected_status:
            self._write_project_state(
                project_dir,
                manifest,
                project_record,
                intake_record,
                analysis_source_record,
                semantic_review_record,
                semantic_blocks,
                semantic_bootstrap_artifact,
            )
            current_status = expected_status
        else:
            current_status = expected_status

        return ProjectSlice(
            project_dir=project_dir,
            manifest=manifest,
            project_record=project_record,
            intake_record=intake_record,
            analysis_source_record=analysis_source_record,
            semantic_review_record=semantic_review_record,
            semantic_blocks=semantic_blocks,
            semantic_bootstrap_artifact=semantic_bootstrap_artifact,
            status_record=current_status,
        )

    def save_analysis_text(self, project_dir: Path, analysis_text: str, source_label: str = "analysis.txt") -> ProjectSlice:
        normalized_text = normalize_text(analysis_text)
        if len(normalized_text) < 40:
            raise ValueError("Analysis text must contain at least 40 non-whitespace characters.")

        project = self.load_project(project_dir)
        now = utc_now()
        clean_source_label = Path(source_label).name or "analysis.txt"
        source_record = {
            "project_id": project.manifest["project_id"],
            "record_id": "analysis-source-primary",
            "record_type": "analysis_text_source",
            "source_label": clean_source_label,
            "source_classification": "analysis_text",
            "canonical_source": True,
            "text_file_path": f"sources/analysis/{clean_source_label}",
            "text_char_count": len(normalized_text),
            "text_line_count": len(normalized_text.splitlines()) or 1,
            "created_at": (project.analysis_source_record or {}).get("created_at", now),
            "updated_at": now,
        }
        semantic_blocks = build_semantic_blocks(
            project.manifest["project_id"],
            source_record["record_id"],
            normalized_text,
            now,
        )
        bootstrap_artifact = {
            "project_id": project.manifest["project_id"],
            "artifact_id": "semantic-bootstrap-primary",
            "artifact_type": "provisional_semantic_bootstrap",
            "source_record_id": source_record["record_id"],
            "bootstrap_strategy": BOOTSTRAP_STRATEGY,
            "generated_block_ids": [block["record_id"] for block in semantic_blocks],
            "semantic_block_count": len(semantic_blocks),
            "created_at": now,
            "updated_at": now,
        }

        manifest = dict(project.manifest)
        manifest["primary_analysis_source_record"] = f"records/intake/{ANALYSIS_RECORD_FILENAME}"
        manifest["updated_at"] = now

        project_record = dict(project.project_record)
        project_record["updated_at"] = now

        intake_record = dict(project.intake_record)
        intake_record["primary_analysis_source_reference"] = manifest["primary_analysis_source_record"]
        intake_record["attached_source_references"] = [manifest["primary_analysis_source_record"]]
        intake_record["intake_readiness"] = "ready"
        intake_record["intake_warnings"] = []
        intake_record["updated_at"] = now

        review_record = dict(project.semantic_review_record)
        mark_review_under_edit(
            review_record,
            now,
            "Provisional semantic blocks were regenerated from the current analysis source.",
        )

        apply_project_summary(project_record, intake_record, source_record, semantic_blocks, review_record)
        self._write_project_state(
            project_dir,
            manifest,
            project_record,
            intake_record,
            source_record,
            review_record,
            semantic_blocks,
            bootstrap_artifact,
        )
        source_path = project_dir / "sources" / "analysis" / clean_source_label
        source_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.write_text(normalized_text + "\n", encoding="utf-8")
        return self.load_project(project_dir)

    def update_semantic_block(
        self,
        project_dir: Path,
        block_id: str,
        title: str,
        semantic_role: str,
        notes: str,
        output_suitability: str | None = None,
    ) -> ProjectSlice:
        clean_title = title.strip()
        clean_role = semantic_role.strip()
        if not clean_title:
            raise ValueError("Block title is required.")
        if clean_role not in ALLOWED_SEMANTIC_ROLES:
            raise ValueError("Semantic role is invalid for this F-006A slice.")
        clean_suitability = "candidate" if output_suitability is None else normalize_output_suitability(output_suitability)

        project = self.load_project(project_dir)
        now = utc_now()
        updated_blocks: list[dict] = []
        found = False
        for block in project.semantic_blocks:
            current = dict(block)
            if current["record_id"] == block_id:
                current["title"] = clean_title
                current["semantic_role"] = clean_role
                current["notes"] = notes.strip()
                current["output_suitability"] = clean_suitability
                current["review_state"] = "under_edit"
                current["updated_at"] = now
                found = True
            updated_blocks.append(current)
        if not found:
            raise ValueError("Selected semantic block was not found.")

        manifest = dict(project.manifest)
        manifest["updated_at"] = now
        project_record = dict(project.project_record)
        project_record["updated_at"] = now
        intake_record = dict(project.intake_record)
        intake_record["updated_at"] = now
        review_record = dict(project.semantic_review_record)
        mark_review_under_edit(review_record, now, "Semantic blocks are currently being edited.")

        apply_project_summary(project_record, intake_record, project.analysis_source_record, updated_blocks, review_record)
        self._write_project_state(
            project_dir,
            manifest,
            project_record,
            intake_record,
            self._copy_analysis_record(project.analysis_source_record, now),
            review_record,
            updated_blocks,
            project.semantic_bootstrap_artifact,
        )
        return self.load_project(project_dir)

    def update_semantic_review_status(self, project_dir: Path, review_status: str) -> ProjectSlice:
        clean_status = normalize_review_status(review_status)
        project = self.load_project(project_dir)
        if not project.semantic_blocks:
            raise ValueError("Semantic review state cannot be changed before semantic blocks exist.")

        now = utc_now()
        manifest = dict(project.manifest)
        manifest["updated_at"] = now
        project_record = dict(project.project_record)
        project_record["updated_at"] = now
        intake_record = dict(project.intake_record)
        intake_record["updated_at"] = now
        review_record = dict(project.semantic_review_record)
        review_record["review_status"] = clean_status
        review_record["approval_state"] = clean_status
        review_record["approved"] = clean_status == "approved"
        review_record["editor_state"] = "under_edit" if clean_status == "under_edit" else "stable"
        if clean_status == "approved":
            review_record["issue_summary"] = "Semantic map approved for the current MVP slice."
        elif clean_status == "ready_for_review":
            review_record["issue_summary"] = "Semantic map marked ready for review."
        else:
            review_record["issue_summary"] = "Semantic blocks are currently being edited."
        review_record["updated_at"] = now

        apply_project_summary(project_record, intake_record, project.analysis_source_record, project.semantic_blocks, review_record)
        self._write_project_state(
            project_dir,
            manifest,
            project_record,
            intake_record,
            self._copy_analysis_record(project.analysis_source_record, now),
            review_record,
            project.semantic_blocks,
            project.semantic_bootstrap_artifact,
        )
        return self.load_project(project_dir)

    def read_analysis_text(self, project_dir: Path) -> str:
        project = self.load_project(project_dir)
        if project.analysis_source_record is None:
            return ""
        source_path = project_dir / project.analysis_source_record["text_file_path"]
        if not source_path.exists():
            return ""
        return source_path.read_text(encoding="utf-8")

    def _copy_analysis_record(self, analysis_source_record: dict | None, now: str) -> dict | None:
        if analysis_source_record is None:
            return None
        copied = dict(analysis_source_record)
        copied["updated_at"] = now
        return copied

    def _ensure_package_dirs(self, project_dir: Path) -> None:
        required_dirs = (
            project_dir / "project.meta",
            project_dir / "sources" / "analysis",
            project_dir / "records" / "project",
            project_dir / "records" / "intake",
            project_dir / "records" / "semantic",
            project_dir / "records" / "review",
            project_dir / "derived" / "semantic",
            project_dir / "outputs",
        )
        for path in required_dirs:
            path.mkdir(parents=True, exist_ok=True)

    def _write_project_state(
        self,
        project_dir: Path,
        manifest: dict,
        project_record: dict,
        intake_record: dict,
        analysis_source_record: dict | None,
        semantic_review_record: dict,
        semantic_blocks: list[dict],
        semantic_bootstrap_artifact: dict | None | object = KEEP_EXISTING,
    ) -> None:
        self._ensure_package_dirs(project_dir)
        manifest = dict(manifest)
        project_record = dict(project_record)
        intake_record = dict(intake_record)
        semantic_review_record = dict(semantic_review_record)
        semantic_blocks = [dict(block) for block in semantic_blocks]
        bootstrap_path = project_dir / "derived" / "semantic" / BOOTSTRAP_FILENAME
        if semantic_bootstrap_artifact is KEEP_EXISTING:
            bootstrap_payload = read_json(bootstrap_path) if bootstrap_path.exists() else None
        else:
            bootstrap_payload = dict(semantic_bootstrap_artifact) if isinstance(semantic_bootstrap_artifact, dict) else None

        write_json(project_dir / "project.manifest", manifest)
        write_json(project_dir / "records" / "project" / PROJECT_RECORD_FILENAME, project_record)
        write_json(project_dir / "records" / "intake" / INTAKE_RECORD_FILENAME, intake_record)
        if analysis_source_record is not None:
            write_json(project_dir / "records" / "intake" / ANALYSIS_RECORD_FILENAME, analysis_source_record)
        else:
            analysis_path = project_dir / "records" / "intake" / ANALYSIS_RECORD_FILENAME
            if analysis_path.exists():
                analysis_path.unlink()
        write_json(project_dir / "records" / "review" / REVIEW_RECORD_FILENAME, semantic_review_record)
        write_json(project_dir / "records" / "semantic" / SEMANTIC_BLOCKS_FILENAME, {"blocks": semantic_blocks})
        if bootstrap_payload is not None:
            write_json(bootstrap_path, bootstrap_payload)
        elif bootstrap_path.exists():
            bootstrap_path.unlink()
        write_json(
            project_dir / "project.meta" / STATUS_FILENAME,
            status_payload(
                project_record,
                intake_record,
                analysis_source_record,
                semantic_blocks,
                semantic_review_record,
            ),
        )
