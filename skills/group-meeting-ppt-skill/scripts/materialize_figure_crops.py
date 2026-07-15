"""Turn normalized private crop boxes into real PNG files before PPT composition.

PPT renderers do not always agree on image-crop semantics.  This helper keeps
the deck portable by performing the crop in pixels with Pillow, then embedding
the resulting image as a normal ``contain`` image in the editable PPTX.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from PIL import Image


def resolve(value: str, base: Path) -> Path:
    path = Path(value)
    return path if path.is_absolute() else (base / path).resolve()


def normalized_box(raw: Any) -> tuple[float, float, float, float]:
    if not isinstance(raw, dict):
        raise ValueError("crop_box must be an object")
    values = tuple(float(raw.get(key, 0.0)) for key in ("left", "top", "right", "bottom"))
    if any(value < 0 or value >= 1 for value in values):
        raise ValueError("crop_box values must be in [0, 1)")
    left, top, right, bottom = values
    # A single scientific panel can occupy far less than 20% of a page.  Permit
    # focused crops, but reject degenerate slivers that cannot be meaningful.
    if left + right >= 0.94 or top + bottom >= 0.94:
        raise ValueError("crop_box leaves too little of the source asset")
    return values


def materialize(spec_path: Path, outdir: Path) -> int:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    if not isinstance(spec, dict) or not isinstance(spec.get("slides"), list):
        raise ValueError("deck spec must contain slides")
    outdir.mkdir(parents=True, exist_ok=True)
    written = 0
    for index, slide in enumerate(spec["slides"], start=1):
        if not isinstance(slide, dict) or slide.get("type") != "figure":
            continue
        source = resolve(str(slide.get("asset", "")), spec_path.parent)
        if not source.exists():
            raise FileNotFoundError(f"slide {index}: asset not found: {source}")
        if "crop_box" in slide or "crop" in slide:
            # ``crop`` is accepted here only to migrate pre-v02 private specs.
            # It is removed before validation/composition and never reaches PPT.
            left, top, right, bottom = normalized_box(slide.get("crop_box", slide.get("crop")))
            with Image.open(source) as image:
                width, height = image.size
                crop = (
                    int(width * left),
                    int(height * top),
                    max(int(width * left) + 1, int(width * (1 - right))),
                    max(int(height * top) + 1, int(height * (1 - bottom))),
                )
                destination = outdir / f"slide-{index:02d}-figure.png"
                cropped = image.crop(crop)
                cropped.save(destination, format="PNG")
                slide["image_aspect"] = round(cropped.width / cropped.height, 3)
            slide["asset"] = str(destination.resolve())
            slide.pop("crop_box", None)
            slide.pop("crop", None)
            written += 1
        else:
            with Image.open(source) as image:
                slide["image_aspect"] = round(image.width / image.height, 3)
    spec_path.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", required=True, help="Private deck-spec JSON to update.")
    parser.add_argument("--outdir", required=True, help="Directory for materialized PNG crops.")
    args = parser.parse_args(argv)
    count = materialize(Path(args.spec).resolve(), Path(args.outdir).resolve())
    print(f"Materialized {count} physical figure crop(s) and recorded figure aspect ratios.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
