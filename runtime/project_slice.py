from __future__ import annotations

import json
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


PROJECT_FORMAT_VERSION = "0.1"
ANALYSIS_RECORD_FILENAME = "analysis_source.json"


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

        self._write_project_state(project_dir, manifest, project_record, intake_record, None, [])
        return self.load_project(project_dir)

    def load_project(self, project_dir: Path) -> ProjectSlice:
        manifest = read_json(project_dir / "project.manifest")
        project_record = read_json(project_dir / "records" / "project" / "project.json")
        intake_record = read_json(project_dir / "records" / "intake" / "intake.json")
        analysis_record_path = project_dir / "records" / "intake" / ANALYSIS_RECORD_FILENAME
        legacy_analysis_record_path = project_dir / "records" / "intake" / "analysis.txt.json"
        semantic_record_path = project_dir / "records" / "semantic" / "semantic_blocks.json"
        if analysis_record_path.exists():
            analysis_source_record = read_json(analysis_record_path)
        elif legacy_analysis_record_path.exists():
            analysis_source_record = read_json(legacy_analysis_record_path)
        else:
            analysis_source_record = None
        semantic_blocks = read_json(semantic_record_path)["blocks"] if semantic_record_path.exists() else []
        return ProjectSlice(
            project_dir=project_dir,
            manifest=manifest,
            project_record=project_record,
            intake_record=intake_record,
            analysis_source_record=analysis_source_record,
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
        project_record["project_status"] = "semantic_map_ready"
        project_record["current_readiness_summary"] = f"{len(semantic_blocks)} semantic blocks ready for review."
        project_record["updated_at"] = now

        intake_record = dict(project.intake_record)
        intake_record["primary_analysis_source_reference"] = analysis_record_ref
        intake_record["intake_readiness"] = "ready"
        intake_record["intake_warnings"] = intake_warnings
        intake_record["updated_at"] = now

        self._write_project_state(project_dir, manifest, project_record, intake_record, analysis_source_record, semantic_blocks)
        (project_dir / "sources" / "analysis").mkdir(parents=True, exist_ok=True)
        (project_dir / "sources" / "analysis" / source_label).write_text(normalized_text + "\n", encoding="utf-8")
        return self.load_project(project_dir)

    def _write_project_state(
        self,
        project_dir: Path,
        manifest: dict,
        project_record: dict,
        intake_record: dict,
        analysis_source_record: dict | None,
        semantic_blocks: list[dict],
    ) -> None:
        write_json(project_dir / "project.manifest", manifest)
        write_json(project_dir / "project.meta" / "status.json", self._status_payload(project_record, intake_record, semantic_blocks))
        write_json(project_dir / "records" / "project" / "project.json", project_record)
        write_json(project_dir / "records" / "intake" / "intake.json", intake_record)
        if analysis_source_record is not None:
            write_json(project_dir / "records" / "intake" / ANALYSIS_RECORD_FILENAME, analysis_source_record)
        write_json(project_dir / "records" / "semantic" / "semantic_blocks.json", {"blocks": semantic_blocks})

    def _status_payload(self, project_record: dict, intake_record: dict, semantic_blocks: list[dict]) -> dict:
        return {
            "project_status": project_record["project_status"],
            "current_readiness_summary": project_record["current_readiness_summary"],
            "intake_readiness": intake_record["intake_readiness"],
            "semantic_block_count": len(semantic_blocks),
            "semantic_map_status": "ready" if semantic_blocks else "empty",
            "updated_at": project_record["updated_at"],
        }
