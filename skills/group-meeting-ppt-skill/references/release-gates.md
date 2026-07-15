# Release gates

Do not present a deck as ready for group meeting until all gates pass.

1. **Evidence and citation:** every visible numerical claim, causal claim and figure title is traceable to the supplied PDF. The title-page authors, journal, year, DOI and every slide source footer must be checked against this PDF in the current run; copied metadata from any earlier paper is a hard failure.
2. **Figures:** every selected main figure is a real paper figure. The visible panel must directly support the slide title, be readable at full-slide render, and carry figure/page/source labels. Do not use a full paper page, an accidental sliver, a crop that shows a different panel than the stated result, or a crop that leaves article-body prose / figure-caption paragraphs underneath the data panel. Citation belongs in the slide footer, not inside a paper-page screenshot.
3. **Narrative:** the deck answers research question → method → evidence → conclusion → limitation/discussion without filler pages.
4. **Duration:** page count and information density match the requested meeting duration; no universal page target is used.
5. **Visual QA:** render all slides, inspect every rendered slide, then fix clipping, overlap, unreadably small figures, duplicate content and internal production copy.
6. **Output:** deliver only `group_meeting_draft.pptx` and `verify_checklist.md`; retain spec, source renderings and QA notes internally.

If a PDF cannot support these gates, return a clearly named evidence brief rather than a fake finished deck.
