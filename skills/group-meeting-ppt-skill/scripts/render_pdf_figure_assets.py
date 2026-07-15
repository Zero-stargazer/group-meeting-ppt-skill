"""Render the PDF pages that contain the figures selected for a meeting deck.

This is an internal asset-preparation utility.  It makes the source-paper
pages available to the filled-deck composer so a PDF-backed PPTX never has to
fall back to empty figure placeholders.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

try:
    import pdfplumber
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Missing dependency: pdfplumber") from exc

try:
    from PIL import Image
except ImportError as exc:  # pragma: no cover
    raise SystemExit("Missing dependency: pillow") from exc


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit("Notes JSON must contain an object.")
    return data


def figure_number(label: str) -> str | None:
    match = re.search(r"(?:fig(?:ure)?\.?|图)\s*([A-Za-z0-9]+)", label, re.I)
    return match.group(1) if match else None


def candidate_pattern(label: str) -> re.Pattern[str] | None:
    number = figure_number(label)
    if not number:
        return None
    # Figure captions start with the figure label.  A free-text search would
    # incorrectly choose an earlier paragraph that merely cites “Fig. 2”.
    return re.compile(rf"^\s*fig(?:ure)?\.?\s*{re.escape(number)}\s*(?:[|.:]|$)", re.I)


def find_figure_page(pdf, label: str) -> int | None:
    pattern = candidate_pattern(label)
    if pattern is None:
        return None
    for index, page in enumerate(pdf.pages, start=1):
        page_text = page.extract_text() or ""
        if any(pattern.search(line) for line in page_text.splitlines()):
            # Some journal layouts place a full-page figure immediately before
            # its caption. Prefer that preceding visual page when the caption
            # page itself is ordinary text.
            current_visual_weight = len(page.images) * 10 + len(page.rects)
            if index > 1:
                previous = pdf.pages[index - 2]
                previous_visual_weight = len(previous.images) * 10 + len(previous.rects)
                if current_visual_weight < 20 and previous_visual_weight >= 20:
                    return index - 1
            return index
    return None


def render_page(page, destination: Path, resolution: int) -> None:
    image = page.to_image(resolution=resolution)
    image.save(str(destination), format="PNG")


def caption_top(page, label: str) -> float | None:
    """Return the y-coordinate of a figure caption when it is on this page."""
    number = figure_number(label)
    if not number:
        return None
    pattern = re.compile(rf"^fig(?:ure)?\.?{re.escape(number)}(?:[|.:]|$)", re.I)
    for word in page.extract_words():
        token = str(word.get("text", "")).replace(" ", "")
        if pattern.search(token):
            return float(word["top"])
    return None


def make_figure_crop(page, source: Path, destination: Path, label: str) -> None:
    """Crop a rendered paper page so the scientific figure stays readable.

    A source PDF commonly puts the figure caption below the panels.  When the
    caption is available, it gives us a safe lower bound.  When a caption is on
    the following page, retain the upper 84% of the visual page.  The original
    page PNG is kept separately for traceability.
    """
    top = caption_top(page, label)
    bottom_ratio = min(0.90, (top / float(page.height)) + 0.035) if top else 0.84
    with Image.open(source) as image:
        width, height = image.size
        left = int(width * 0.025)
        right = int(width * 0.975)
        upper = int(height * 0.02)
        lower = max(upper + 1, int(height * bottom_ratio))
        image.crop((left, upper, right, lower)).save(destination, format="PNG")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", required=True, help="Source paper PDF.")
    parser.add_argument("--notes", required=True, help="Structured paper notes JSON.")
    parser.add_argument("--outdir", required=True, help="Destination directory for rendered PNG files.")
    parser.add_argument(
        "--resolution",
        type=int,
        default=300,
        help="Raster resolution in DPI (300 by default so panel-level crops remain legible on a meeting-room screen).",
    )
    parser.add_argument("--manifest", default="", help="Optional manifest JSON path.")
    args = parser.parse_args(argv)

    pdf_path = Path(args.pdf).resolve()
    notes_path = Path(args.notes).resolve()
    outdir = Path(args.outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    notes = read_json(notes_path)
    figures = notes.get("figures_to_discuss", [])
    if not isinstance(figures, list) or not figures:
        raise SystemExit("No figures_to_discuss in notes JSON.")

    rendered: dict[int, str] = {}
    manifest_figures: list[dict[str, Any]] = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for position, raw in enumerate(figures, start=1):
            figure = raw if isinstance(raw, dict) else {"label": str(raw)}
            label = str(figure.get("label", f"Fig. {position}")).strip()
            pdf_page = find_figure_page(pdf, label)
            if pdf_page is None:
                continue
            if pdf_page not in rendered:
                filename = f"paper-page-{pdf_page:02d}.png"
                render_page(pdf.pages[pdf_page - 1], outdir / filename, args.resolution)
                rendered[pdf_page] = filename
            record = dict(figure)
            record["pdf_page"] = pdf_page
            source_asset = outdir / rendered[pdf_page]
            safe_label = re.sub(r"[^A-Za-z0-9]+", "-", label).strip("-").lower() or f"figure-{position}"
            crop_asset = outdir / f"{safe_label}-p{pdf_page:02d}.png"
            make_figure_crop(pdf.pages[pdf_page - 1], source_asset, crop_asset, label)
            record["asset"] = str(crop_asset.resolve())
            record["source_page_asset"] = str(source_asset.resolve())
            manifest_figures.append(record)

    manifest = {
        "source_pdf": str(pdf_path),
        "notes": str(notes_path),
        "figure_assets": manifest_figures,
        "unresolved_figure_labels": [
            str(item.get("label", ""))
            for item in figures
            if isinstance(item, dict)
            and str(item.get("label", ""))
            and str(item.get("label", "")) not in {str(found.get("label", "")) for found in manifest_figures}
        ],
    }
    manifest_path = Path(args.manifest).resolve() if args.manifest else outdir / "figure-assets.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Rendered {len(rendered)} source pages for {len(manifest_figures)} selected figures.")
    print(f"Wrote asset manifest to {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
