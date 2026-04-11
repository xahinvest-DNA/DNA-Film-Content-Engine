from __future__ import annotations

from runtime.builders.common import current_output_source_segments
from runtime.domain.project_types import ProjectSlice


def build_long_video_script(project: ProjectSlice, built_at: str) -> dict:
    source_focus_mode, source_segments = current_output_source_segments(project)
    if not source_segments:
        raise ValueError("Long-video build is blocked until at least one rough-cut segment exists.")
    if project.accepted_reference is None:
        raise ValueError("Long-video build is blocked until one current accepted reference exists.")
    if project.accepted_scene_reference_stub is None:
        raise ValueError("Long-video build is blocked until one current accepted scene reference stub exists.")
    if project.timecode_range_stub is None:
        raise ValueError("Long-video build is blocked until one current timecode range stub exists.")

    block_lookup = {block["record_id"]: block for block in project.semantic_blocks}
    asset_lookup = {asset["record_id"]: asset for asset in project.matching_prep_assets}
    candidate_lookup = {entry["record_id"]: entry for entry in project.matching_candidate_stubs}
    accepted_reference = project.accepted_reference
    accepted_scene_reference_stub = project.accepted_scene_reference_stub
    source_candidate = candidate_lookup.get(accepted_reference.get("source_candidate_stub_id", ""))
    source_rationale = source_candidate.get("preferred_rationale", "").strip() if source_candidate else ""
    source_note = source_candidate.get("note", "").strip() if source_candidate else ""

    segment_payloads: list[dict] = []
    progression_sections: list[str] = []
    continuity_lines: list[str] = []
    voiceover_sections: list[str] = []
    opening_setup = ""
    ending_direction = ""

    for index, segment in enumerate(source_segments, start=1):
        block = block_lookup.get(segment.get("semantic_block_id", ""))
        asset = asset_lookup.get(segment.get("prep_asset_id", ""))
        block_title = block.get("title", "Untitled semantic block") if block else "Untitled semantic block"
        block_role = block.get("semantic_role", "claim") if block else "claim"
        block_notes = block.get("notes", "").strip() if block else ""
        block_content = block.get("content", "").strip() if block else ""
        prep_asset_label = asset.get("asset_label", "Unknown prep input") if asset else "Unknown prep input"
        prep_asset_type = asset.get("asset_type", "unknown") if asset else "unknown"
        segment_label = segment.get("segment_label", "").strip() or block_title
        voiceover_guidance = block_notes or block_content or segment_label
        transition_line = (
            f"Bridge from '{segment_label}' into the next beat by carrying forward the {block_role.replace('_', ' ')} tension."
            if index < len(source_segments)
            else f"Land the final beat back on {accepted_scene_reference_stub.get('scene_reference_label', '').strip() or 'the chosen scene reference'} with a clear payoff."
        )
        if not opening_setup:
            opening_setup = source_rationale or source_note or f"Open by framing {segment_label} as the central setup for the long-form narrative."
        ending_direction = (
            f"Close by resolving the long-form thread around {segment_label} and clarify the broader takeaway for the viewer."
        )
        progression_sections.extend(
            [
                f"### Beat {index:02d} - {segment_label}",
                f"- Timecode span: {segment.get('start_timecode', '').strip()} -> {segment.get('end_timecode', '').strip()}",
                f"- Semantic unit: {block_title} [{block_role}]",
                f"- Film-side source: {prep_asset_label} [{prep_asset_type}]",
                f"- Narrative function: {voiceover_guidance}",
                "",
            ]
        )
        continuity_lines.append(f"{index}. {transition_line}")
        voiceover_sections.extend(
            [
                f"Beat {index:02d}: {voiceover_guidance}",
                "",
            ]
        )
        segment_payloads.append(
            {
                "sequence": index,
                "source_rough_cut_segment_id": segment["record_id"],
                "segment_label": segment_label,
                "start_timecode": segment.get("start_timecode", "").strip(),
                "end_timecode": segment.get("end_timecode", "").strip(),
                "semantic_block_id": segment.get("semantic_block_id", ""),
                "semantic_title": block_title,
                "semantic_role": block_role,
                "scene_reference_label": accepted_scene_reference_stub.get("scene_reference_label", "").strip(),
                "prep_asset_label": prep_asset_label,
                "prep_asset_type": prep_asset_type,
                "voiceover_guidance": voiceover_guidance,
                "transition_guidance": transition_line,
            }
        )

    working_title = (
        source_rationale
        or f"{project.project_record.get('title', 'DNA Film Content Engine Project')} - Long Video Script"
    )
    project_title = project.project_record.get("title", "DNA Film Content Engine Project")
    film_title = project.project_record.get("film_title", "").strip() or "Film title optional"
    continuity_preview = "\n".join(continuity_lines)
    markdown_content = "\n".join(
        [
            f"# {project_title} - Long Video Script",
            "",
            f"- Working title: {working_title}",
            f"- Project: {project_title}",
            f"- Film: {film_title}",
            f"- Built at: {built_at}",
            f"- Source focus: {source_focus_mode}",
            f"- Beat count: {len(segment_payloads)}",
            "",
            "## Editorial angle",
            source_rationale or source_note or "Use the current accepted reference as the spine for a deeper long-form script pass.",
            "",
            "## Opening setup",
            opening_setup,
            "",
            "## Main progression",
            *progression_sections,
            "## Expanded voiceover spine",
            *voiceover_sections,
            "## Continuity / transitions",
            continuity_preview,
            "",
            "## Ending / closure direction",
            ending_direction,
            "",
        ]
    ).rstrip() + "\n"

    return {
        "project_id": project.manifest["project_id"],
        "record_id": "long-video-script-current",
        "record_type": "long_video_script",
        "builder_id": "long_video_script_v1",
        "output_family": "long_video",
        "title": f"{project_title} - Long Video Script",
        "working_title": working_title,
        "built_at": built_at,
        "source_focus_mode": source_focus_mode,
        "source_candidate_stub_id": accepted_reference.get("source_candidate_stub_id", "").strip(),
        "source_rough_cut_segment_ids": [segment["record_id"] for segment in source_segments],
        "segment_count": len(segment_payloads),
        "opening_setup": opening_setup,
        "ending_direction": ending_direction,
        "artifact_relative_path": "outputs/long_video/long_video_script.md",
        "markdown_content": markdown_content,
        "segments": segment_payloads,
    }
