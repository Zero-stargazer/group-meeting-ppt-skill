"""Validate the private evidence deck specification before PPT composition."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ALLOWED_TYPES = {"title", "narrative", "method", "figure", "synthesis", "questions"}
BANNED_VISIBLE_COPY = ("这一页目的", "你应该讲", "建议画面", "放图位置", "请用户补充", "请用户自己完成")


def load(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("deck spec must be a JSON object")
    return data


def visible_text(slide: dict[str, Any]) -> str:
    fields = [slide.get("section", ""), slide.get("title", ""), slide.get("body", ""), slide.get("caveat", "")]
    bullets = slide.get("bullets", [])
    if isinstance(bullets, list):
        fields.extend(bullets)
    return "\n".join(str(value) for value in fields)


def validate(spec: dict[str, Any], base_dir: Path) -> list[str]:
    errors: list[str] = []
    paper = spec.get("paper")
    meeting = spec.get("meeting")
    slides = spec.get("slides")
    if not isinstance(paper, dict) or not str(paper.get("title", "")).strip():
        errors.append("paper.title is required")
    if not isinstance(paper, dict) or not str(paper.get("citation", "")).strip():
        errors.append("paper.citation is required; copy it from the supplied PDF in this run")
    if not isinstance(meeting, dict) or not isinstance(meeting.get("duration_minutes"), (int, float)):
        errors.append("meeting.duration_minutes is required")
    elif meeting["duration_minutes"] <= 0:
        errors.append("meeting.duration_minutes must be positive")
    if not isinstance(meeting, dict) or not isinstance(meeting.get("target_seconds"), (int, float)):
        errors.append("meeting.target_seconds is required")
    elif meeting["target_seconds"] <= 0:
        errors.append("meeting.target_seconds must be positive")
    elif isinstance(meeting.get("duration_minutes"), (int, float)):
        requested_seconds = float(meeting["duration_minutes"]) * 60
        target_seconds = float(meeting["target_seconds"])
        if not requested_seconds * 0.70 <= target_seconds <= requested_seconds * 1.05:
            errors.append(
                "meeting.target_seconds must use 70%–105% of requested duration "
                "(leave only a small opening / transition buffer)"
            )
    if not isinstance(slides, list) or len(slides) < 6:
        errors.append("slides must contain at least six audience-facing slides")
        return errors

    kinds: list[str] = []
    estimated_seconds_total = 0.0
    for index, raw in enumerate(slides, start=1):
        if not isinstance(raw, dict):
            errors.append(f"slide {index} is not an object")
            continue
        kind = str(raw.get("type", "")).strip()
        kinds.append(kind)
        if kind not in ALLOWED_TYPES:
            errors.append(f"slide {index}: unsupported type {kind!r}")
        if not str(raw.get("title", "")).strip():
            errors.append(f"slide {index}: title is required")
        if not str(raw.get("source", "")).strip():
            errors.append(f"slide {index}: source is required")
        elif "et al." in str(raw.get("source", "")).lower():
            errors.append(
                f"slide {index}: source must be a PDF locator only; "
                "the composer adds paper.citation from the current run"
            )
        seconds = raw.get("estimated_seconds")
        if not isinstance(seconds, (int, float)) or not 10 <= seconds <= 120:
            errors.append(f"slide {index}: estimated_seconds must be between 10 and 120")
        else:
            estimated_seconds_total += float(seconds)
        bullets = raw.get("bullets", [])
        if bullets and (not isinstance(bullets, list) or len(bullets) > 3):
            errors.append(f"slide {index}: bullets must contain at most three items")
        if isinstance(bullets, list) and kind == "figure":
            for bullet_index, item in enumerate(bullets, start=1):
                if len(str(item).strip()) > 58:
                    errors.append(
                        f"slide {index}: figure bullet {bullet_index} is too long; "
                        "keep audience evidence bullets concise"
                    )
        for phrase in BANNED_VISIBLE_COPY:
            if phrase in visible_text(raw):
                errors.append(f"slide {index}: forbidden internal copy {phrase!r}")
        if kind == "figure":
            asset = str(raw.get("asset", "")).strip()
            if not asset:
                errors.append(f"slide {index}: figure asset is required")
            elif not (Path(asset) if Path(asset).is_absolute() else base_dir / asset).exists():
                errors.append(f"slide {index}: figure asset does not exist: {asset}")
            for key in ("figure_label", "panel_scope", "pdf_page", "caveat"):
                if not raw.get(key):
                    errors.append(f"slide {index}: figure slide requires {key}")
            if len(str(raw.get("caveat", "")).strip()) > 96:
                errors.append(f"slide {index}: figure caveat is too long; keep the evidence boundary concise")
            crop_review = raw.get("crop_review")
            if not isinstance(crop_review, dict):
                errors.append(f"slide {index}: figure slide requires crop_review")
            else:
                for key in ("named_panel_matches", "axes_and_legend_legible", "article_prose_removed"):
                    if crop_review.get(key) is not True:
                        errors.append(f"slide {index}: crop_review.{key} must be true")
            image_aspect = raw.get("image_aspect")
            if not isinstance(image_aspect, (int, float)) or image_aspect <= 0:
                errors.append(
                    f"slide {index}: image_aspect is required after "
                    "materialize_figure_crops.py"
                )
            crop_box = raw.get("crop_box")
            if crop_box is not None:
                if not isinstance(crop_box, dict):
                    errors.append(f"slide {index}: crop_box must be an object")
                else:
                    try:
                        margins = [float(crop_box.get(key, 0.0)) for key in ("left", "top", "right", "bottom")]
                    except (TypeError, ValueError):
                        errors.append(f"slide {index}: crop_box values must be numeric")
                    else:
                        if any(value < 0 or value >= 1 for value in margins):
                            errors.append(f"slide {index}: crop_box values must be in [0, 1)")
                        elif margins[0] + margins[2] >= 0.94 or margins[1] + margins[3] >= 0.94:
                            errors.append(f"slide {index}: crop_box leaves too little of the source asset")
            if "crop" in raw:
                errors.append(f"slide {index}: use crop_box then materialize_figure_crops.py; live PPT crop is forbidden")

    if "title" not in kinds or "figure" not in kinds or "synthesis" not in kinds or "questions" not in kinds:
        errors.append("spec must include title, figure, synthesis and questions slides")
    if isinstance(meeting, dict) and isinstance(meeting.get("target_seconds"), (int, float)):
        target_seconds = float(meeting["target_seconds"])
        if not target_seconds * 0.85 <= estimated_seconds_total <= target_seconds * 1.10:
            errors.append(
                "slide estimated_seconds total must fit meeting.target_seconds "
                f"(planned {estimated_seconds_total:.0f}s; target {target_seconds:.0f}s)"
            )
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", required=True, help="Path to private deck-spec JSON.")
    args = parser.parse_args(argv)
    path = Path(args.spec).resolve()
    errors = validate(load(path), path.parent)
    if errors:
        print("Deck spec rejected:")
        for error in errors:
            print(f"- {error}")
        return 2
    print("Deck spec is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
