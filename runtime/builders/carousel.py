from __future__ import annotations

from runtime.builders.common import current_output_source_segments
from runtime.domain.project_types import ProjectSlice


def build_carousel_script(project: ProjectSlice, built_at: str) -> dict:
    source_focus_mode, source_segments = current_output_source_segments(project)
    if not source_segments:
        raise ValueError("Carousel build is blocked until at least one rough-cut segment exists.")
    if project.accepted_reference is None:
        raise ValueError("Carousel build is blocked until one current accepted reference exists.")
    if project.accepted_scene_reference_stub is None:
        raise ValueError("Carousel build is blocked until one current accepted scene reference stub exists.")
    if project.timecode_range_stub is None:
        raise ValueError("Carousel build is blocked until one current timecode range stub exists.")

    block_lookup = {block["record_id"]: block for block in project.semantic_blocks}
    candidate_lookup = {entry["record_id"]: entry for entry in project.matching_candidate_stubs}
    accepted_reference = project.accepted_reference
    accepted_scene_reference_stub = project.accepted_scene_reference_stub
    source_candidate = candidate_lookup.get(accepted_reference.get("source_candidate_stub_id", ""))
    source_rationale = source_candidate.get("preferred_rationale", "").strip() if source_candidate else ""
    source_note = source_candidate.get("note", "").strip() if source_candidate else ""

    segment_payloads: list[dict] = []
    slide_sections: list[str] = []
    continuity_lines: list[str] = []
    cover_slide = ""
    closing_slide = ""

    for index, segment in enumerate(source_segments, start=1):
        block = block_lookup.get(segment.get("semantic_block_id", ""))
        block_title = block.get("title", "Untitled semantic block") if block else "Untitled semantic block"
        block_role = block.get("semantic_role", "claim") if block else "claim"
        block_notes = block.get("notes", "").strip() if block else ""
        block_content = block.get("content", "").strip() if block else ""
        segment_label = segment.get("segment_label", "").strip() or block_title
        slide_idea = block_notes or block_content or segment_label
        slide_heading = block_title if index > 1 else f"{segment_label} as the opening carousel hook"
        flow_line = (
            f"Carry the reader from slide {index:02d} into slide {index + 1:02d} by escalating the {block_role.replace('_', ' ')} beat."
            if index < len(source_segments)
            else f"Land the final slide back on {accepted_scene_reference_stub.get('scene_reference_label', '').strip() or 'the selected scene reference'} with a clear takeaway."
        )
        if not cover_slide:
            cover_slide = source_rationale or source_note or f"Open with {segment_label} as the cover-slide hook for the carousel."
        closing_slide = f"Close by turning {segment_label} into a final takeaway slide with a concise CTA or reflection."
        slide_sections.extend(
            [
                f"### Slide {index + 1:02d} - {slide_heading}",
                f"- Segment label: {segment_label}",
                f"- Timecode span: {segment.get('start_timecode', '').strip()} -> {segment.get('end_timecode', '').strip()}",
                f"- Semantic unit: {block_title} [{block_role}]",
                f"- Core idea: {slide_idea}",
                f"- Reading flow: {flow_line}",
                "",
            ]
        )
        continuity_lines.append(f"{index}. {flow_line}")
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
                "cover_hook": cover_slide if index == 1 else "",
                "slide_heading": slide_heading,
                "slide_idea": slide_idea,
                "reading_flow": flow_line,
            }
        )

    project_title = project.project_record.get("title", "DNA Film Content Engine Project")
    film_title = project.project_record.get("film_title", "").strip() or "Film title optional"
    carousel_angle = source_rationale or source_note or "Use the current rough-cut truth as a slide-by-slide carousel argument."
    slide_count = len(segment_payloads) + 2
    markdown_content = "\n".join(
        [
            f"# {project_title} - Carousel Script",
            "",
            f"- Carousel angle: {carousel_angle}",
            f"- Project: {project_title}",
            f"- Film: {film_title}",
            f"- Built at: {built_at}",
            f"- Source focus: {source_focus_mode}",
            f"- Slide count: {slide_count}",
            "",
            "## Cover slide / first-slide hook",
            cover_slide,
            "",
            "## Slide-by-slide progression",
            *slide_sections,
            "## Reading continuity",
            "\n".join(continuity_lines),
            "",
            "## Final slide / CTA",
            closing_slide,
            "",
        ]
    ).rstrip() + "\n"

    return {
        "project_id": project.manifest["project_id"],
        "record_id": "carousel-script-current",
        "record_type": "carousel_script",
        "builder_id": "carousel_script_v1",
        "output_family": "carousel",
        "title": f"{project_title} - Carousel Script",
        "carousel_angle": carousel_angle,
        "built_at": built_at,
        "source_focus_mode": source_focus_mode,
        "source_candidate_stub_id": accepted_reference.get("source_candidate_stub_id", "").strip(),
        "source_rough_cut_segment_ids": [segment["record_id"] for segment in source_segments],
        "segment_count": len(segment_payloads),
        "slide_count": slide_count,
        "cover_slide": cover_slide,
        "closing_slide": closing_slide,
        "artifact_relative_path": "outputs/carousel/carousel_script.md",
        "markdown_content": markdown_content,
        "segments": segment_payloads,
    }
