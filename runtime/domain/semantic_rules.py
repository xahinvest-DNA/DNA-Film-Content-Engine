from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone


ALLOWED_SEMANTIC_ROLES = (
    "claim",
    "insight",
    "mechanism",
    "emotional_beat",
    "transition",
    "context",
)
ALLOWED_OUTPUT_SUITABILITY = ("candidate", "strong", "weak", "not_suitable")
ALLOWED_REVIEW_STATES = ("under_edit", "ready_for_review", "approved")
BOOTSTRAP_STRATEGY = "blank_line_groups_with_heading_sensitivity"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def slugify(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return normalized or "dna-project"


def normalize_output_suitability(value: str) -> str:
    clean_value = value.strip()
    if clean_value not in ALLOWED_OUTPUT_SUITABILITY:
        raise ValueError("Output suitability is invalid for this F-006A slice.")
    return clean_value


def normalize_text(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n").lstrip("\ufeff").strip()
    return re.sub(r"\n{3,}", "\n\n", normalized)


def split_semantic_groups(text: str) -> list[str]:
    normalized = normalize_text(text)
    if not normalized:
        return []
    return [chunk.strip() for chunk in re.split(r"\n\s*\n+", normalized) if chunk.strip()]


def is_heading_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if stripped.startswith("#"):
        return True
    if stripped.endswith(":") and len(stripped.split()) <= 12:
        return True
    return bool(re.fullmatch(r"[A-Z0-9 \-]{4,80}", stripped))


def clean_heading(line: str) -> str:
    return line.lstrip("#").strip(" \t:-") or "Untitled block"


def semantic_role_for(content: str) -> str:
    lowered = content.lower()
    if any(token in lowered for token in ("because", "therefore", "so that", "reveals how", "leads to")):
        return "mechanism"
    if any(token in lowered for token in ("feel", "emotion", "fear", "love", "grief", "hope")):
        return "emotional_beat"
    if any(token in lowered for token in ("however", "meanwhile", "then", "finally", "afterward")):
        return "transition"
    if any(token in lowered for token in ("shows", "argues", "suggests", "demonstrates", "means")):
        return "insight"
    if any(token in lowered for token in ("background", "context", "situation", "world", "setting")):
        return "context"
    return "claim"


def title_for(group: str) -> str:
    lines = [line.strip() for line in group.splitlines() if line.strip()]
    if lines and is_heading_line(lines[0]):
        return clean_heading(lines[0])
    sentence = re.split(r"(?<=[.!?])\s+", group.strip(), maxsplit=1)[0].strip()
    words = sentence.split()
    if not words:
        return "Untitled block"
    return " ".join(words[:8]).strip(" .,;:") or "Untitled block"


def block_origin_for(group: str) -> str:
    lines = [line.strip() for line in group.splitlines() if line.strip()]
    if lines and is_heading_line(lines[0]):
        return "heading_group"
    return "blank_line_group"


def build_semantic_blocks(project_id: str, source_record_id: str, analysis_text: str, timestamp: str | None = None) -> list[dict]:
    created_at = timestamp or utc_now()
    groups = split_semantic_groups(analysis_text)
    blocks: list[dict] = []
    for index, group in enumerate(groups, start=1):
        content = group.strip()
        blocks.append(
            {
                "project_id": project_id,
                "record_id": f"sb-{index:03d}",
                "record_type": "semantic_block",
                "source_record_id": source_record_id,
                "sequence": index,
                "title": title_for(content),
                "semantic_role": semantic_role_for(content),
                "content": content,
                "notes": "",
                "output_suitability": "candidate",
                "review_state": "under_edit",
                "provisional": True,
                "bootstrap_origin": block_origin_for(content),
                "semantic_unit_id": f"sem-{uuid.uuid4().hex[:10]}",
                "created_at": created_at,
                "updated_at": created_at,
            }
        )
    return blocks
