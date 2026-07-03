#!/usr/bin/env python
"""Create a Chinese group-meeting pack from structured paper notes.

This helper is intentionally deterministic. It does not replace the agent's
paper-reading work; it packages already-extracted paper facts into a reusable
meeting outline, slide plan, advisor-question list, and integrity checklist.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise SystemExit("Input JSON must be an object.")
    return data


def as_list(data: dict[str, Any], key: str) -> list[Any]:
    value = data.get(key, [])
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def text(data: dict[str, Any], key: str, fallback: str = "") -> str:
    value = data.get(key, fallback)
    if value is None:
        return fallback
    stripped = str(value).strip()
    return stripped or fallback


def figure_label_text(figures: list[Any]) -> str:
    labels: list[str] = []
    for fig in figures:
        if isinstance(fig, dict) and fig.get("label"):
            labels.append(str(fig["label"]).strip())
    return "、".join(labels) or "论文中最能说明方法和结果的图"


def bullet_lines(items: list[Any], empty: str = "待根据原文补充。") -> str:
    if not items:
        return f"- {empty}"

    lines: list[str] = []
    for item in items:
        if isinstance(item, dict):
            label = str(item.get("label", "")).strip() or "图表"
            why = str(item.get("why_use", "")).strip()
            say = str(item.get("what_to_say", "")).strip()
            merged = "；".join(part for part in [why, say] if part)
            lines.append(f"- **{label}**：{merged or empty}")
        else:
            lines.append(f"- {str(item).strip()}")
    return "\n".join(lines)


def slide_plan(data: dict[str, Any]) -> list[tuple[str, str, str, str]]:
    title = text(data, "paper_title_zh", text(data, "paper_title_en", "论文标题需要回原文核对"))
    problem = text(data, "research_problem", "先用一句话说明作者要解决的核心问题。")
    summary = text(data, "one_sentence_summary", "用一句话总结论文主张。")
    route = as_list(data, "method_route")
    findings = as_list(data, "key_findings")
    figures = as_list(data, "figures_to_discuss")
    limitations = as_list(data, "limitations")
    relation = text(data, "relation_to_my_topic", "说明这篇论文和自己课题的关系。")
    figure_labels = figure_label_text(figures)

    return [
        ("Slide 01", "论文一句话", f"用一句话讲清楚：{title}", summary),
        ("Slide 02", "为什么要读这篇", "说明问题背景和研究动机。", problem),
        (
            "Slide 03",
            "作者的核心思路",
            "把论文方法路线拆成 3—5 步。",
            " → ".join(map(str, route)) if route else "方法路线需要回原文核对。",
        ),
        (
            "Slide 04",
            "实验/系统流程",
            "用流程图或关键示意图讲清楚从输入到输出。",
            f"建议优先使用：{figure_labels}。",
        ),
        (
            "Slide 05",
            "关键图 1",
            "选择最能说明整体框架的图。",
            "讲图之前先说：这张图回答了什么问题。",
        ),
        (
            "Slide 06",
            "关键图 2",
            "选择最能说明方法有效性的图。",
            "不要只翻译 caption，要解释它支持了哪个结论。",
        ),
        (
            "Slide 07",
            "关键结果",
            "总结作者最重要的发现。",
            "；".join(map(str, findings)) if findings else "关键结果需要回原文核对。",
        ),
        (
            "Slide 08",
            "局限和风险",
            "主动说出论文不够强的地方。",
            "；".join(map(str, limitations)) if limitations else "局限需要回原文核对。",
        ),
        ("Slide 09", "和我课题的关系", "把论文价值拉回自己的方向。", relation),
        (
            "Slide 10",
            "老师可能追问",
            "提前准备 3—5 个追问和回答方向。",
            "方法可靠性、样本量、对照实验、泛化能力、和自己课题的关联。",
        ),
    ]


def render_meeting_outline(data: dict[str, Any]) -> str:
    title_zh = text(data, "paper_title_zh", "论文标题需要回原文核对")
    title_en = text(data, "paper_title_en", "")
    direction = text(data, "research_direction", "研究方向需要用户说明")
    duration = text(data, "duration_minutes", "15")
    meeting_type = text(data, "meeting_type", "文献组会")

    return f"""# 10页组会PPT大纲

## 基本信息

- 中文题目：{title_zh}
- 英文题目：{title_en or "未提供"}
- 汇报类型：{meeting_type}
- 汇报时长：{duration} 分钟
- 我的研究方向：{direction}

## 一句话总结

{text(data, "one_sentence_summary", "待根据原文补充一句话总结。")}

## 研究问题

{text(data, "research_problem", "待根据原文补充作者要解决的问题。")}

## 方法路线

{bullet_lines(as_list(data, "method_route"))}

## 关键发现

{bullet_lines(as_list(data, "key_findings"))}

## 建议重点讲的图

{bullet_lines(as_list(data, "figures_to_discuss"))}

## 局限与风险

{bullet_lines(as_list(data, "limitations"))}

## 和我课题的关系

{text(data, "relation_to_my_topic", "这篇论文和自己课题的关系需要用户结合课题说明。")}

"""


def render_slide_plan(data: dict[str, Any]) -> str:
    rows = slide_plan(data)
    lines = ["# Slide Plan｜10页组会PPT大纲", ""]
    for slide_id, title, goal, notes in rows:
        lines.extend(
            [
                f"## {slide_id}｜{title}",
                "",
                f"- 这一页目的：{goal}",
                f"- 你应该讲：{notes}",
                "- 建议画面：标题 + 1个核心图/流程/表格 + 2—3行解释。",
                "",
            ]
        )
    return "\n".join(lines)


def render_advisor_questions(data: dict[str, Any]) -> str:
    direction = text(data, "research_direction", "你的研究方向")
    limitations = as_list(data, "limitations")
    limitation_block = bullet_lines(
        limitations,
        "如果原文没有明确局限，必须自己从样本量、对照、泛化和统计方法角度补充。",
    )

    return f"""# 老师可能追问清单

## 方法可靠性

- 这个方法为什么可靠？
- 作者用了哪些对照证明不是偶然结果？
- 如果换一批样本或换一个实验条件，结论还成立吗？

## 数据与统计

- 样本量是否足够？
- 误差线、显著性检验和重复次数是否清晰？
- 是否存在只展示成功案例、不展示失败案例的问题？

## 图表解释

- 这张图到底支持了哪个结论？
- 图里的坐标、单位、阈值和颜色编码是什么意思？
- 如果删掉这张图，论文主结论还站得住吗？

## 和自己课题的关系

- 这篇论文对“{direction}”有什么直接启发？
- 你能复用的是方法、材料、分析方式，还是展示逻辑？
- 如果你要借鉴它，第一步实验应该怎么设计？

## 你应该主动承认的局限

{limitation_block}

"""


def render_integrity_checklist() -> str:
    return """# 学术诚信与汇报自查清单

## 必须做到

- 不编造论文没有的数据、实验和结论。
- 不把 AI 生成的解释当成原文事实。
- 关键数据必须回到原文核对，包括样本量、单位、P 值、浓度、时间和实验条件。
- 每张图都要说清楚它支持哪一个结论，不能只复述 caption。
- 不确定的内容要标注“我还需要回原文确认”。

## 不应该做

- 不用 AI 替你编实验结果。
- 不用 AI 替你写老师问答的“标准答案”。
- 不用 AI 把论文包装成比原文更强的结论。
- 不把模板输出直接交上去，必须按你的课题和原文修改。

## 汇报前最后检查

- 我能用一句话说清楚这篇论文解决什么问题吗？
- 我知道每张关键图为什么放进 PPT 吗？
- 我准备好了至少 3 个老师可能追问的问题吗？
- 我标出了哪些内容是原文事实，哪些是我的理解吗？
"""


def write_outputs(data: dict[str, Any], outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    files = {
        "meeting_outline.md": render_meeting_outline(data),
        "slide_plan.md": render_slide_plan(data),
        "advisor_questions.md": render_advisor_questions(data),
        "integrity_checklist.md": render_integrity_checklist(),
    }
    for name, content in files.items():
        (outdir / name).write_text(content, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Structured paper-note JSON file.")
    parser.add_argument("--outdir", required=True, help="Output directory for generated Markdown files.")
    args = parser.parse_args(argv)

    data = read_json(Path(args.input))
    write_outputs(data, Path(args.outdir))
    print(f"Wrote meeting pack to {Path(args.outdir).resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
