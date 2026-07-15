# Evidence-Grounded Deck Workflow

This is an internal execution reference for the Skill. It prevents the “outline disguised as a PPT” failure mode.

## Input

- Original paper PDF or a legal open-access copy.
- Meeting duration and audience.
- Optional research direction and triage / deep-reading handoff.

## Execution

1. Read the title, abstract, methods/results structure, figure captions, and every main figure page.
2. Create a private figure map: `figure → scientific question → supported takeaway → source page → caveat`.
3. Choose slide count from that map. One main figure gets one slide by default; split only when a figure contains separate questions.
4. Render or crop readable original figure regions. For a panel crop, retain its axes / legend / necessary labels and remove surrounding article prose and caption paragraphs. Preserve `Fig. N` and a source footer.
5. Compose audience-facing slides. A visible slide contains a specific takeaway, a readable original figure or data table, and only the evidence needed to understand it.
6. Add a concise final verification checklist for sample size, experimental unit, statistics, figure caption, and causal scope.
7. Render every slide and inspect at full size. Fix clipping, placeholder blocks, unreadable whole-page screenshots, and internal planning language.

## Forbidden visible text

- “这一页目的”
- “你应该讲”
- “建议画面”
- “放论文图 / 流程 / 表格”
- any prompt, scoring rule, production note, or instruction to the user to build the slide.

## Minimum finished-deck standard

- Every main claim maps to a concrete paper figure, table, method, or stated result.
- The visible figure has a figure number and source.
- The deck covers the paper's actual central figure chain rather than just one attractive figure.
- The user can open the PPTX and revise it directly; they do not need to turn an outline into slides.
