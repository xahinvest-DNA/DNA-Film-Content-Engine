from __future__ import annotations

from runtime.domain.project_types import ProjectSlice


def current_output_source_segments(project: ProjectSlice) -> tuple[str, list[dict]]:
    preferred_segments = [
        entry for entry in project.rough_cut_segment_stubs if entry.get("subset_status", "saved_only") == "selected_for_current_rough_cut"
    ]
    if preferred_segments:
        return ("preferred_subset_only", preferred_segments)
    return ("all_saved_segments", list(project.rough_cut_segment_stubs))
