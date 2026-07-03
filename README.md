# group-meeting-ppt-skill

<p align="center">
  <img src="media/group_meeting_ppt_skill_one_page_bright_20260703.png" alt="group-meeting-ppt-skill 项目示意图：输入 PDF，输出组会 PPT 初稿" width="760">
</p>

> Turn a paper PDF into a 10-slide Chinese group-meeting PPTX draft, with an intermediate notes JSON for review and revision.

`group-meeting-ppt-skill` is a Codex Skill for Chinese academic group meetings, journal clubs, literature reports, and early-stage research presentations. It helps convert a paper PDF or structured paper notes into a first-pass presentation package.

The generated deck is a draft, not a final academic deliverable. All extracted facts, numbers, figure captions, methods, and conclusions should be checked against the original paper before presentation.

## What it generates

- A structured notes JSON extracted from a PDF.
- A 10-slide editable `.pptx` draft.
- A Markdown meeting outline.
- A slide-by-slide speaking plan.
- A list of likely advisor questions.
- An academic-integrity checklist.

## Who it is for

- First-year graduate students preparing their first literature group meeting.
- Master's and PhD students who need a reusable paper-reading-to-slides workflow.
- Undergraduate students preparing literature reports, thesis presentations, or course presentations.
- Researchers who want a transparent draft-generation workflow instead of a black-box slide generator.

## What it does not do

- It does not write papers for the user.
- It does not fabricate experimental data, results, citations, or conclusions.
- It does not guarantee that a teacher, advisor, or reviewer will approve the generated slides.
- It does not replace careful reading of the original paper.
- It does not treat AI-generated explanations as verified paper facts.

## Project structure

```text
group-meeting-ppt-skill/
  README.md
  LICENSE
  skills/
    group-meeting-ppt-skill/
      SKILL.md
      agents/openai.yaml
      references/
      scripts/
        paper_pdf_to_notes.py
        create_pptx_from_pdf.py
        create_meeting_pack.py
        create_meeting_pptx.py
  examples/
    sample-paper.pdf
    sample-paper-input.json
    sample-output/
  media/
    group_meeting_ppt_skill_one_page_bright_20260703.png
  tests/
    test_create_meeting_pack.py
    test_create_meeting_pptx.py
    test_create_pptx_from_pdf.py
```

## Quick start: PDF to PPTX

From the project root:

```powershell
& 'C:\Users\xieni\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  skills/group-meeting-ppt-skill/scripts/create_pptx_from_pdf.py `
  --pdf examples/sample-paper.pdf `
  --out examples/sample-output/from_pdf_draft_group_meeting.pptx `
  --notes-json examples/sample-output/from_pdf_notes.json `
  --pack-outdir examples/sample-output/from-pdf-pack `
  --research-direction "数字微流控与多重核酸检测"
```

This creates:

```text
examples/sample-output/
  from_pdf_notes.json
  from_pdf_draft_group_meeting.pptx
  from-pdf-pack/
```

Recommended workflow:

1. Run the PDF-to-PPTX command.
2. Open `from_pdf_notes.json`.
3. Check extracted claims against the original PDF.
4. Edit the notes JSON if needed.
5. Regenerate the PPTX from the corrected notes.

## Generate PPTX from existing structured notes

If you already have structured paper notes:

```powershell
& 'C:\Users\xieni\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' `
  skills/group-meeting-ppt-skill/scripts/create_meeting_pptx.py `
  --input examples/sample-paper-input.json `
  --out examples/sample-output/draft_group_meeting.pptx
```

## Generate Markdown meeting pack

```powershell
python skills/group-meeting-ppt-skill/scripts/create_meeting_pack.py `
  --input examples/sample-paper-input.json `
  --outdir examples/sample-output
```

This creates:

```text
examples/sample-output/
  meeting_outline.md
  slide_plan.md
  advisor_questions.md
  integrity_checklist.md
```

## Install as a Codex Skill

Copy this folder into your Codex skills directory:

```text
skills/group-meeting-ppt-skill
```

Then ask Codex to use `group-meeting-ppt-skill` on a paper PDF or structured paper notes.

## Dependencies

The full PDF-to-PPTX workflow uses:

- `pdfplumber`
- `python-pptx`
- `reportlab` for tests only
- `Pillow` for optional image assets

The bundled Codex Python runtime used during development already includes these packages. If you use another Python environment, install the missing packages manually.

## Tests

```powershell
python -m unittest discover -s tests -v
```

For full PDF and PPTX test coverage, use a Python environment with `pdfplumber`, `python-pptx`, and `reportlab` installed.

## Academic integrity

The generated files are draft materials. Before using them in a real meeting:

- Check every number, unit, sample size, threshold, and statistical result against the paper.
- Verify all figure captions and interpretations.
- Mark uncertain points instead of presenting them as facts.
- Revise the deck according to your own research context and audience.

## License

MIT License. See [LICENSE](LICENSE).
