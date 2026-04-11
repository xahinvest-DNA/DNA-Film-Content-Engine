from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OutputSlotSpec:
    key: str
    label: str
    artifact_attr: str
    summary_name: str
    count_field: str
    count_unit: str
    empty_guidance: str
    identity_field: str | None = None
    identity_label: str | None = None


OUTPUT_SLOT_SPECS: tuple[OutputSlotSpec, ...] = (
    OutputSlotSpec(
        key="packaging",
        label="Packaging",
        artifact_attr="packaging_script_bundle",
        summary_name="Packaging-ready script bundle",
        count_field="segment_count",
        count_unit="segment",
        empty_guidance="Build Packaging-Ready Script Bundle to create the first packaging artifact.",
    ),
    OutputSlotSpec(
        key="shorts_reels",
        label="Shorts/Reels",
        artifact_attr="shorts_reels_script",
        summary_name="Shorts/Reels script",
        count_field="segment_count",
        count_unit="beat",
        empty_guidance="Build Shorts/Reels Script to add the short-form output path.",
        identity_field="hook_line",
        identity_label="hook",
    ),
    OutputSlotSpec(
        key="long_video",
        label="Long Video",
        artifact_attr="long_video_script",
        summary_name="Long-video script",
        count_field="segment_count",
        count_unit="beat",
        empty_guidance="Build Long-Video Script to add the long-form output path.",
        identity_field="working_title",
        identity_label="working title",
    ),
    OutputSlotSpec(
        key="carousel",
        label="Carousel",
        artifact_attr="carousel_script",
        summary_name="Carousel script",
        count_field="slide_count",
        count_unit="slide",
        empty_guidance="Build Carousel Script to add the slide-based output path.",
        identity_field="carousel_angle",
        identity_label="angle",
    ),
)
