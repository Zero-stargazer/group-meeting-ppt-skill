#!/usr/bin/env python
"""Extract rough structured paper notes from a PDF.

This script is intentionally conservative. It creates a usable first-pass JSON
for group-meeting PPT generation, but every extracted claim should still be
checked against the original PDF.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

try:
    import pdfplumber
except ImportError as exc:  # pragma: no cover - exercised by CLI users
    raise SystemExit(
        "Missing dependency: pdfplumber. "
        "Use the Codex bundled Python or install it with: python -m pip install pdfplumber"
    ) from exc


SECTION_HEADINGS = [
    "abstract",
    "keywords",
    "introduction",
    "background",
    "related work",
    "materials and methods",
    "methods",
    "method",
    "experimental",
    "experiments",
    "results",
    "discussion",
    "limitations",
    "conclusion",
    "conclusions",
    "references",
]


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def split_sentences(value: str) -> list[str]:
    value = normalize_space(value)
    if not value:
        return []
    pieces = re.split(r"(?<=[.!?。！？])\s+", value)
    return [piece.strip() for piece in pieces if len(piece.strip()) > 20]


def short(value: str, limit: int = 220) -> str:
    value = normalize_space(value)
    if len(value) <= limit:
        return value
    return value[: limit - 1].rstrip() + "…"


def extract_pdf_text(pdf_path: Path, max_pages: int | None = None) -> tuple[str, list[str]]:
    pages: list[str] = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        selected = pdf.pages[:max_pages] if max_pages else pdf.pages
        for page in selected:
            pages.append(page.extract_text() or "")
    full_text = "\n".join(pages)
    lines = [line.strip() for line in full_text.splitlines() if line.strip()]
    return full_text, lines


def guess_title(lines: list[str]) -> str:
    skip_words = {
        "abstract",
        "keywords",
        "introduction",
        "methods",
        "results",
        "discussion",
        "references",
    }
    for line in lines[:25]:
        clean = normalize_space(line)
        lower = clean.lower().strip(":")
        if lower in skip_words:
            continue
        if len(clean) < 10 or len(clean) > 180:
            continue
        if re.search(r"\bdoi\b|www\.|@|copyright|received|accepted|journal|volume|issue", lower):
            continue
        if re.fullmatch(r"[\d\s\W]+", clean):
            continue
        return clean
    return "PDF论文标题待回原文核对"


def heading_regex(heading: str) -> re.Pattern[str]:
    escaped = re.escape(heading).replace(r"\ ", r"\s+")
    return re.compile(rf"(?im)^\s*(?:\d+(?:\.\d+)*\.?\s*)?{escaped}\s*:?\s*$")


def find_section(full_text: str, names: list[str]) -> str:
    starts: list[tuple[int, int, str]] = []
    for name in names:
        match = heading_regex(name).search(full_text)
        if match:
            starts.append((match.start(), match.end(), name))
    if not starts:
        return ""

    _, body_start, _ = min(starts, key=lambda item: item[0])
    end = len(full_text)
    for heading in SECTION_HEADINGS:
        match = heading_regex(heading).search(full_text, body_start)
        if match and match.start() > body_start:
            end = min(end, match.start())
    return full_text[body_start:end].strip()


def extract_captions(lines: list[str]) -> list[dict[str, str]]:
    captions: list[dict[str, str]] = []
    pattern = re.compile(r"^(?P<kind>fig(?:ure)?\.?|table)\s*(?P<num>[A-Za-z0-9\-]+)\s*[\.:：]\s*(?P<caption>.+)$", re.I)
    for line in lines:
        match = pattern.match(line.strip())
        if not match:
            continue
        kind = match.group("kind")
        num = match.group("num")
        label = f"{'Table' if kind.lower().startswith('table') else 'Fig.'} {num}"
        caption = short(match.group("caption"), 180)
        captions.append(
            {
                "label": label,
                "why_use": "PDF中自动识别到的图表说明，适合回原文核对后决定是否放入PPT。",
                "what_to_say": caption,
            }
        )
        if len(captions) >= 5:
            break
    return captions


def method_steps(methods_text: str, abstract_text: str) -> list[str]:
    source = methods_text or abstract_text
    sentences = split_sentences(source)
    steps: list[str] = []
    for sentence in sentences[:3]:
        clauses = re.split(r",\s+|;\s+|\s+and\s+", sentence)
        for clause in clauses:
            clean = short(clause, 120)
            if len(clean) >= 18:
                steps.append(clean)
            if len(steps) >= 4:
                return steps
    return steps or ["PDF自动提取未识别出清晰方法步骤，需要回原文核对 Methods 部分。"]


def finding_sentences(results_text: str, discussion_text: str, abstract_text: str) -> list[str]:
    source = results_text or discussion_text or abstract_text
    candidates = split_sentences(source)
    priority_words = re.compile(r"\b(show|shows|shown|demonstrate|demonstrates|found|result|improve|reduce|increase|distinguish|validate|work|works|achieve|achieves)\b", re.I)
    ranked = [s for s in candidates if priority_words.search(s)]
    selected = ranked[:3] or candidates[:3]
    return [short(s, 160) for s in selected] or ["PDF自动提取未识别出关键结果，需要回原文核对 Results 部分。"]


def limitation_sentences(limitations_text: str, discussion_text: str) -> list[str]:
    source = limitations_text or discussion_text
    candidates = split_sentences(source)
    priority_words = re.compile(r"\b(limit|limited|limitation|however|future|further|small|bias|generalization|validate|validation)\b", re.I)
    selected = [s for s in candidates if priority_words.search(s)][:3]
    return [short(s, 160) for s in selected] or ["PDF自动提取未明确识别局限，需要从样本量、对照、泛化和统计方法角度回原文核对。"]


def extract_notes_from_pdf(
    pdf_path: Path,
    *,
    research_direction: str = "",
    meeting_type: str = "文献组会",
    duration_minutes: int = 15,
    max_pages: int | None = None,
) -> dict[str, Any]:
    full_text, lines = extract_pdf_text(pdf_path, max_pages=max_pages)
    title = guess_title(lines)
    abstract = find_section(full_text, ["abstract"])
    introduction = find_section(full_text, ["introduction", "background"])
    methods = find_section(full_text, ["materials and methods", "methods", "method", "experimental", "experiments"])
    results = find_section(full_text, ["results"])
    discussion = find_section(full_text, ["discussion", "conclusion", "conclusions"])
    limitations = find_section(full_text, ["limitations"])
    captions = extract_captions(lines)

    abstract_sentences = split_sentences(abstract)
    intro_sentences = split_sentences(introduction)
    one_sentence = (
        short(abstract_sentences[0], 180)
        if abstract_sentences
        else "PDF自动提取未识别出摘要主旨，需要回原文核对。"
    )
    problem = (
        short(intro_sentences[0], 180)
        if intro_sentences
        else "PDF自动提取未识别出清晰研究问题，需要回原文核对 Introduction 部分。"
    )

    warnings: list[str] = [
        "这是从PDF自动抽取的第一版结构化 notes，不等同于原文事实核定。",
        "所有数字、图注、实验条件和结论必须回到PDF原文核对。",
    ]
    if not abstract:
        warnings.append("未识别到 Abstract 标题，摘要相关内容可能不完整。")
    if not captions:
        warnings.append("未识别到 Figure/Table caption，PPT 中会使用图表占位。")

    return {
        "source_pdf": str(pdf_path),
        "paper_title_zh": title,
        "paper_title_en": title,
        "research_direction": research_direction or "研究方向待补充",
        "meeting_type": meeting_type,
        "duration_minutes": duration_minutes,
        "one_sentence_summary": one_sentence,
        "research_problem": problem,
        "method_route": method_steps(methods, abstract),
        "key_findings": finding_sentences(results, discussion, abstract),
        "figures_to_discuss": captions
        or [
            {
                "label": "Figure/Table 待选择",
                "why_use": "PDF自动提取未识别到清晰图题，需要人工回到原文选择关键图。",
                "what_to_say": "优先选择能说明研究问题、方法路线和关键结果的图。",
            }
        ],
        "limitations": limitation_sentences(limitations, discussion),
        "relation_to_my_topic": (
            f"这篇论文可能与“{research_direction}”相关，建议结合自己的课题从方法、数据、图表展示和后续实验设计四个角度筛选可复用内容。"
            if research_direction
            else "需要补充自己的研究方向后，再判断这篇论文与课题的关系。"
        ),
        "extraction_warnings": warnings,
    }


def write_notes(data: dict[str, Any], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", required=True, help="Input paper PDF path.")
    parser.add_argument("--out", required=True, help="Output structured notes JSON path.")
    parser.add_argument("--research-direction", default="", help="Your research direction, used for relation-to-topic notes.")
    parser.add_argument("--meeting-type", default="文献组会", help="Meeting type shown in the generated notes.")
    parser.add_argument("--duration-minutes", type=int, default=15, help="Target presentation duration.")
    parser.add_argument("--max-pages", type=int, default=0, help="Only read the first N pages; 0 means all pages.")
    args = parser.parse_args(argv)

    data = extract_notes_from_pdf(
        Path(args.pdf),
        research_direction=args.research_direction,
        meeting_type=args.meeting_type,
        duration_minutes=args.duration_minutes,
        max_pages=args.max_pages or None,
    )
    write_notes(data, Path(args.out))
    print(f"Wrote notes JSON to {Path(args.out).resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
