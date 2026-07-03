---
name: group-meeting-ppt-skill
description: Use when a user provides a scientific paper PDF, abstract, DOI notes, or structured paper notes and needs a Chinese group-meeting or journal-club deliverable: PDF-to-PPTX draft, 10-slide outline, slide plan, speaker notes, advisor questions, figure-use plan, academic-integrity checklist, or structured paper notes JSON.
---

# Group Meeting PPT Skill

## Core Principle

Help the user get from “paper is unreadable / PPT is blank” to a credible group-meeting draft. Do not fabricate data, conclusions, figures, impact factors, author affiliations, or advisor-ready answers.

## Choose the Mode

Use **PDF-to-PPTX Mode** when the user provides a PDF and wants a PowerPoint draft. Use **Rescue Outline Mode** when the user has pasted excerpts or needs a fast text outline. Use **Packaging Mode** when the user already has structured notes or wants reproducible Markdown files. Use **PPTX Draft Mode** when the user already has structured JSON and wants a PowerPoint file.

| Mode | Use when | Output |
|---|---|---|
| PDF-to-PPTX | User provides a paper PDF and asks for PPT, slides, or a group-meeting draft | `*.notes.json` plus `draft_group_meeting.pptx` |
| Rescue Outline | User has a paper, abstract, notes, or pasted excerpt and needs help fast | 10-slide outline, what to say on each slide, figures to use, advisor questions |
| Packaging | User has structured JSON-like facts and wants files | `meeting_outline.md`, `slide_plan.md`, `advisor_questions.md`, `integrity_checklist.md` |
| PPTX Draft | User wants a directly editable PPTX draft | `draft_group_meeting.pptx`, with 10 passable slides and figure placeholders |

## PDF-to-PPTX Workflow

When the user provides a PDF and wants a PPT draft:

1. Run the PDF pipeline:

   ```powershell
   python skills/group-meeting-ppt-skill/scripts/create_pptx_from_pdf.py `
     --pdf path/to/paper.pdf `
     --out path/to/draft_group_meeting.pptx `
     --notes-json path/to/paper.notes.json `
     --research-direction "用户的研究方向"
   ```

2. Treat the generated `paper.notes.json` as a first-pass extraction, not verified truth.
3. If the PDF extraction is weak, read the PDF directly, correct `paper.notes.json`, then rerun `create_meeting_pptx.py`.
4. Tell the user which parts need original-paper verification, especially numbers, figure captions, experimental conditions, and conclusions.
5. Never claim the deck is final, teacher-approved, or sufficient without human revision.

## Rescue Outline Workflow

1. Identify the meeting context: audience, duration, research direction, and whether this is first-year journal club, thesis group meeting, or project-related reading.
2. Extract only supported facts from the paper material the user provided. Mark unknowns as “需要回原文核对”.
3. Read `references/meeting-outline-rubric.md` before producing the slide plan.
4. Read `references/question-bank.md` before producing advisor questions.
5. Read `references/academic-integrity.md` before finalizing boundaries.
6. Produce sections in this order:
   - one-sentence paper summary;
   - 10-slide meeting outline;
   - figure-use plan;
   - advisor questions;
   - what the presenter must verify in the original paper.

## Output Contract

For a normal user request, return:

```markdown
# 组会PPT救急稿

## 一句话总结

## 10页组会PPT大纲

## 每页应该讲什么

## 建议重点放哪些图

## 老师可能追问

## 汇报前必须核对
```

Keep the tone practical and direct. The user wants something they can revise, not a lecture about AI.

## Packaging Script

When the user provides structured paper notes, optionally run:

```powershell
python skills/group-meeting-ppt-skill/scripts/create_meeting_pack.py `
  --input examples/sample-paper-input.json `
  --outdir examples/sample-output
```

The script is deterministic and only packages supplied facts. It does not read PDFs or call an LLM.

## PPTX Draft Script

When the user wants a `.pptx`, run:

```powershell
python skills/group-meeting-ppt-skill/scripts/create_meeting_pptx.py `
  --input examples/sample-paper-input.json `
  --out examples/sample-output/draft_group_meeting.pptx
```

The deck should be treated as a first draft:

- keep all data grounded in the input notes;
- use figure placeholders when the actual paper figures are not provided;
- remind the user to verify all numbers, figure captions, and conclusions against the original paper;
- do not claim the PPT is final, teacher-approved, or submission-ready.

## PDF Notes Script

When only the structured notes JSON is needed, run:

```powershell
python skills/group-meeting-ppt-skill/scripts/paper_pdf_to_notes.py `
  --pdf path/to/paper.pdf `
  --out path/to/paper.notes.json `
  --research-direction "用户的研究方向"
```

This script extracts a rough title, abstract summary, problem, method route, findings, figure/table captions, limitations, and relation-to-topic field. It is deliberately conservative and includes warnings when content must be checked manually.

## Refusal and Boundary Rules

- Do not write fabricated results or invented figure interpretations.
- Do not claim the generated outline is sufficient for submission or final presentation.
- Do not provide “guaranteed teacher-approved” answers.
- If the user asks for direct代写 or fake data, refuse and offer a structure, checklist, or review workflow instead.
- If the user asks for impact factor, author school, or journal metrics, require current verification before stating them.

## Common Mistakes

- Starting with a generic background slide instead of the paper’s specific research problem.
- Translating captions sentence by sentence without explaining what each figure proves.
- Putting too many multi-panel figures on one unreadable slide.
- Hiding limitations; good group meetings usually mention them before the advisor asks.
- Letting AI turn a weak paper into a stronger story than the evidence supports.
