from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ProjectSlice:
    project_dir: Path
    manifest: dict
    project_record: dict
    intake_record: dict
    analysis_source_record: dict | None
    semantic_review_record: dict
    semantic_blocks: list[dict]
    semantic_bootstrap_artifact: dict | None
    status_record: dict
