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
    matching_prep_assets: list[dict]
    matching_candidate_stubs: list[dict]
    accepted_reference: dict | None
    accepted_scene_reference_stub: dict | None
    timecode_range_stub: dict | None
    rough_cut_segment_stubs: list[dict]
    packaging_script_bundle: dict | None
    shorts_reels_script: dict | None
    long_video_script: dict | None
    carousel_script: dict | None
