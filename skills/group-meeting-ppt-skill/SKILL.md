---
name: group-meeting-ppt-skill
description: "Turn an academic paper PDF into a Chinese, editable group-meeting PPTX that is ready to present: read the paper, select and crop its real figures, build a duration-aware evidence narrative, compose the slides, and visually verify the finished deck. Use when a user supplies a paper PDF and asks for a journal-club, literature-report, lab-meeting, or paper-to-PPT presentation; do not use for outline-only requests unless no PDF is available."
---

# PDF → 可直接汇报的组会 PPT

## Non-negotiable outcome

For a supplied PDF, deliver exactly:

```text
group_meeting_draft.pptx
verify_checklist.md
```

The user supplies the paper PDF and, optionally, meeting duration / audience / research direction. Default to a 12-minute literature group meeting when duration is missing. Do the reading, figure selection, page planning, slide composition and QA internally. Do not give the user an outline, a page-by-page worksheet, a JSON file, placeholders, or production instructions as a substitute for the deck.

Read `references/lazy-delivery-contract.md`, `references/evidence-deck-spec.md`, and `references/release-gates.md` before starting.

## Required workflow

1. Inspect the PDF: title, abstract, methods, results/discussion, all main-figure pages, captions, and relevant tables.
   - Copy the title-page bibliographic metadata from the supplied PDF into the private paper record before writing any slide. Never reuse an author, journal, year, DOI or source footer from an earlier paper run.
2. Establish the narrative: research question → method / comparison → main evidence chain → conclusion → evidence boundary → discussion.
3. Decide page count from requested duration and the actual figure chain. Do not use a fixed page count. Select, consolidate, or split figures before composition.
4. Build a private `deck-spec.json` following `references/evidence-deck-spec.md`.
   - Use direct, audience-facing takeaway titles.
   - Record `target_seconds` and `estimated_seconds` for every slide. The total must fit the requested duration; duration changes must change selection, consolidation or splitting of evidence slides.
   - Ground every number and claim in the PDF.
   - Give each figure slide a real source asset, figure label, panel scope, PDF page, evidence bullets, caveat, and source.
   - Use a readable figure crop for multi-panel figures; split panels only when they answer distinct questions. When a panel crop is needed, write `crop_box` in the private spec and run `scripts/materialize_figure_crops.py` before composition; do not pass live crop instructions to the PPT renderer.
   - Visually inspect every materialized crop before composition. The crop must contain the named panel plus its necessary axes / legend / labels, but **must not** retain surrounding article prose or a figure-caption paragraph merely because it was on the same PDF page. Put citation information in the PPT source footer instead.
5. Generate source page assets with `scripts/render_pdf_figure_assets.py` (default 300 DPI). Correct its figure map when caption detection is weak; never keep an unreadable whole-page screenshot just because the helper found it.
6. Materialize every panel-level crop into a real image, then validate the spec before composing:

```powershell
python scripts/materialize_figure_crops.py --spec deck-spec.json --outdir figure-crops
python scripts/validate_deck_spec.py --spec deck-spec.json
```

7. Create the deck with `scripts/compose_evidence_deck.mjs` in an initialized `@oai/artifact-tool` presentation workspace. Keep temporary workspaces, virtual environments and dependency installs outside the final output directory. Do not use `create_meeting_pptx.py` or `create_pptx_from_pdf.py` as the normal PDF-to-finished-deck path; they are legacy deterministic helpers.
8. Render every slide and inspect each full-size image. Compare the deck title-page citation and every source footer against the supplied PDF. Fix clipped text, partial panel labels, overlap, small figures, duplicate points, incorrect figure/panel references, stale citations, generic filler, and internal production copy.
9. Pass every gate in `references/release-gates.md`. If a gate fails, repair internally and rerender. If the PDF cannot support a finished deck, return a clearly named evidence brief instead of a fake PPTX.

## Composition requirements

- Use the original paper's figures, not invented charts or decorative AI illustrations.
- Keep titles and bullets editable. Paper figures may remain embedded images.
- Keep source labels on every figure slide and concise sources on non-figure slides.
- Use evidence boundaries as scientific content, not generic disclaimers.
- Do not present unsupported causality, sample numbers, metrics, or paper conclusions as facts.
- Do not place any of the following on audience-facing slides: internal paths, prompts, scoring rules, planning notes, or instructions to the presenter.

## Acceptance standard

The deck is acceptable only when a graduate student can open it and start rehearsing immediately: the paper's central evidence chain is present, figures are legible, titles say what the evidence means, page count fits the meeting, and the only remaining work is factual verification plus the presenter's own delivery choices.

## No-PDF fallback

When no original PDF or legal open-access copy is available, produce an evidence brief and request the PDF for a finished deck. Never label a text-only outline as a finished group-meeting PPT.
