from __future__ import annotations

from runtime.builders.common import current_output_source_segments
from runtime.domain.project_types import ProjectSlice


def build_shorts_reels_script(project: ProjectSlice, built_at: str) -> dict:
    source_focus_mode, source_segments = current_output_source_segments(project)
    if not source_segments:
        raise ValueError("Shorts/Reels build is blocked until at least one rough-cut segment exists.")
    if project.accepted_reference is None:
        raise ValueError("Shorts/Reels build is blocked until one current accepted reference exists.")
    if project.accepted_scene_reference_stub is None:
        raise ValueError("Shorts/Reels build is blocked until one current accepted scene reference stub exists.")
    if project.timecode_range_stub is None:
        raise ValueError("Shorts/Reels build is blocked until one current timecode range stub exists.")

    block_lookup = {block["record_id"]: block for block in project.semantic_blocks}
    asset_lookup = {asset["record_id"]: asset for asset in project.matching_prep_assets}
    candidate_lookup = {entry["record_id"]: entry for entry in project.matching_candidate_stubs}
    accepted_reference = project.accepted_reference
    accepted_scene_reference_stub = project.accepted_scene_reference_stub
    source_candidate = candidate_lookup.get(accepted_reference.get("source_candidate_stub_id", ""))

    segment_payloads: list[dict] = []
    hook_text = ""
    progression_lines: list[str] = []
    for index, segment in enumerate(source_segments, start=1):
        block = block_lookup.get(segment.get("semantic_block_id", ""))
        asset = asset_lookup.get(segment.get("prep_asset_id", ""))
        block_title = block.get("title", "Untitled semantic block") if block else "Untitled semantic block"
        block_role = block.get("semantic_role", "claim") if block else "claim"
        block_notes = block.get("notes", "").strip() if block else ""
        block_content = block.get("content", "").strip() if block else ""
        prep_asset_label = asset.get("asset_label", "Unknown prep input") if asset else "Unknown prep input"
        source_note = source_candidate.get("note", "").strip() if source_candidate else ""
        source_rationale = source_candidate.get("preferred_rationale", "").strip() if source_candidate else ""
        beat_text = block_notes or block_content or segment.get("segment_label", "").strip() or block_title
        condensed_line = f"{block_title}: {beat_text}"
        if not hook_text:
            hook_text = source_rationale or source_note or condensed_line
        progression_lines.append(condensed_line)
        segment_payloads.append(
            {
                "sequence": index,
                "source_rough_cut_segment_id": segment["record_id"],
                "segment_label": segment.get("segment_label", "").strip(),
                "start_timecode": segment.get("start_timecode", "").strip(),
                "end_timecode": segment.get("end_timecode", "").strip(),
                "semantic_block_id": segment.get("semantic_block_id", ""),
                "semantic_title": block_title,
                "semantic_role": block_role,
                "scene_reference_label": accepted_scene_reference_stub.get("scene_reference_label", "").strip(),
                "prep_asset_label": prep_asset_label,
                "hook_line": hook_text if index == 1 else "",
                "compressed_voiceover": beat_text,
                "progression_line": condensed_line,
            }
        )

    if not hook_text:
        hook_text = "Lead with the strongest visual idea from the current rough-cut selection."

    progression_count = len(progression_lines)
    progression_preview = "\n".join(f"{index}. {line}" for index, line in enumerate(progression_lines, start=1))
    closure_line = (
        f"Close by returning to {accepted_scene_reference_stub.get('scene_reference_label', '').strip() or 'the selected scene reference'} "
        "and land a short-form takeaway or CTA."
    )
    compressed_voiceover = " ".join(line.split(": ", 1)[1] if ": " in line else line for line in progression_lines).strip()

    project_title = project.project_record.get("title", "DNA Film Content Engine Project")
    film_title = project.project_record.get("film_title", "").strip() or "Film title optional"
    script_title = f"{project_title} - Shorts Reels Script"
    markdown_content = "\n".join(
        [
            f"# {script_title}",
            "",
            f"- Project: {project_title}",
            f"- Film: {film_title}",
            f"- Built at: {built_at}",
            f"- Source focus: {source_focus_mode}",
            f"- Beat count: {progression_count}",
            "",
            "## Hook / Opening angle",
            hook_text,
            "",
            "## Short progression",
            progression_preview,
            "",
            "## Compressed voiceover spine",
            compressed_voiceover or "No compressed voiceover spine available.",
            "",
            "## CTA / Closure",
            closure_line,
            "",
        ]
    ).rstrip() + "\n"

    return {
        "project_id": project.manifest["project_id"],
        "record_id": "shorts-reels-script-current",
        "record_type": "shorts_reels_script",
        "builder_id": "shorts_reels_script_v1",
        "output_family": "shorts_reels",
        "title": script_title,
        "built_at": built_at,
        "source_focus_mode": source_focus_mode,
        "source_candidate_stub_id": accepted_reference.get("source_candidate_stub_id", "").strip(),
        "source_rough_cut_segment_ids": [segment["record_id"] for segment in source_segments],
        "segment_count": len(segment_payloads),
        "hook_line": hook_text,
        "progression_count": progression_count,
        "closure_line": closure_line,
        "artifact_relative_path": "outputs/shorts_reels/shorts_reels_script.md",
        "markdown_content": markdown_content,
        "segments": segment_payloads,
    }
