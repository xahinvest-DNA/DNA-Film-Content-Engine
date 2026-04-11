from __future__ import annotations

from runtime.domain.project_types import ProjectSlice


def packaging_bundle_source_segments(project: ProjectSlice) -> tuple[str, list[dict]]:
    preferred_segments = [
        entry for entry in project.rough_cut_segment_stubs if entry.get("subset_status", "saved_only") == "selected_for_current_rough_cut"
    ]
    if preferred_segments:
        return ("preferred_subset_only", preferred_segments)
    return ("all_saved_segments", list(project.rough_cut_segment_stubs))


def build_packaging_script_bundle(project: ProjectSlice, built_at: str) -> dict:
    source_focus_mode, source_segments = packaging_bundle_source_segments(project)
    if not source_segments:
        raise ValueError("Packaging bundle build is blocked until at least one rough-cut segment exists.")
    if project.accepted_reference is None:
        raise ValueError("Packaging bundle build is blocked until one current accepted reference exists.")
    if project.accepted_scene_reference_stub is None:
        raise ValueError("Packaging bundle build is blocked until one current accepted scene reference stub exists.")
    if project.timecode_range_stub is None:
        raise ValueError("Packaging bundle build is blocked until one current timecode range stub exists.")

    block_lookup = {block["record_id"]: block for block in project.semantic_blocks}
    asset_lookup = {asset["record_id"]: asset for asset in project.matching_prep_assets}
    candidate_lookup = {entry["record_id"]: entry for entry in project.matching_candidate_stubs}
    accepted_reference = project.accepted_reference
    accepted_scene_reference_stub = project.accepted_scene_reference_stub
    source_candidate = candidate_lookup.get(accepted_reference.get("source_candidate_stub_id", ""))

    segment_payloads: list[dict] = []
    markdown_sections: list[str] = []
    for index, segment in enumerate(source_segments, start=1):
        block = block_lookup.get(segment.get("semantic_block_id", ""))
        asset = asset_lookup.get(segment.get("prep_asset_id", ""))
        block_title = block.get("title", "Untitled semantic block") if block else "Untitled semantic block"
        block_role = block.get("semantic_role", "claim") if block else "claim"
        block_notes = block.get("notes", "").strip() if block else ""
        block_content = block.get("content", "").strip() if block else ""
        prep_asset_label = asset.get("asset_label", "Unknown prep input") if asset else "Unknown prep input"
        prep_asset_type = asset.get("asset_type", "unknown") if asset else "unknown"
        candidate_rationale = source_candidate.get("preferred_rationale", "").strip() if source_candidate else ""
        candidate_note = source_candidate.get("note", "").strip() if source_candidate else ""
        voiceover_beat = block_notes or block_content or segment.get("segment_label", "").strip()
        packaging_angle = candidate_rationale or candidate_note or f"Use the '{block_title}' meaning beat as the packaging spine."
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
                "prep_asset_type": prep_asset_type,
                "voiceover_beat": voiceover_beat,
                "packaging_angle": packaging_angle,
            }
        )
        markdown_sections.extend(
            [
                f"## Segment {index:02d} - {segment.get('segment_label', '').strip() or block_title}",
                f"- Timecode: {segment.get('start_timecode', '').strip()} -> {segment.get('end_timecode', '').strip()}",
                f"- Semantic unit: {block_title} [{block_role}]",
                f"- Scene reference: {accepted_scene_reference_stub.get('scene_reference_label', '').strip() or 'none'}",
                f"- Film-side source: {prep_asset_label} [{prep_asset_type}]",
                f"- Packaging angle: {packaging_angle}",
                "",
                "Voiceover beat",
                voiceover_beat or "No voiceover beat available.",
                "",
            ]
        )

    project_title = project.project_record.get("title", "DNA Film Content Engine Project")
    film_title = project.project_record.get("film_title", "").strip() or "Film title optional"
    bundle_title = f"{project_title} - Packaging Script Bundle"
    markdown_content = "\n".join(
        [
            f"# {bundle_title}",
            "",
            f"- Project: {project_title}",
            f"- Film: {film_title}",
            f"- Built at: {built_at}",
            f"- Source focus: {source_focus_mode}",
            f"- Segment count: {len(segment_payloads)}",
            "",
            "## Editorial summary",
            "This bundle turns the current rough-cut structure into a packaging-ready script handoff that can be edited, narrated, or passed into downstream publishing prep.",
            "",
            *markdown_sections,
        ]
    ).rstrip() + "\n"

    return {
        "project_id": project.manifest["project_id"],
        "record_id": "packaging-script-bundle-current",
        "record_type": "packaging_script_bundle",
        "builder_id": "packaging_script_bundle_v1",
        "output_family": "packaging",
        "title": bundle_title,
        "built_at": built_at,
        "source_focus_mode": source_focus_mode,
        "source_candidate_stub_id": accepted_reference.get("source_candidate_stub_id", "").strip(),
        "source_rough_cut_segment_ids": [segment["record_id"] for segment in source_segments],
        "segment_count": len(segment_payloads),
        "artifact_relative_path": "outputs/packaging/packaging_script_bundle.md",
        "markdown_content": markdown_content,
        "segments": segment_payloads,
    }
