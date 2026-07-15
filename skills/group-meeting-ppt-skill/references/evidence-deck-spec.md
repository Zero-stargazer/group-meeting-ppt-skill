# Evidence deck specification

`deck-spec.json` is the private contract between paper reading and PPT composition. It is not shown to the user.

```json
{
  "paper": {"title": "…", "citation": "…", "doi": "…", "source_pdf": "…"},
  "meeting": {
    "duration_minutes": 12,
    "target_seconds": 660,
    "type": "文献组会"
  },
  "slides": [
    {
      "type": "title | narrative | method | figure | synthesis | questions",
      "estimated_seconds": 45,
      "section": "研究问题",
      "title": "一句能直接讲出口的结论",
      "body": "可选的两三句解释",
      "bullets": ["不超过三条证据"],
      "source": "Abstract · PDF p. 1"
    },
    {
      "type": "figure",
      "estimated_seconds": 55,
      "section": "原文主图",
      "title": "Fig. 2｜本文条件下的体内标记信号更高",
      "asset": "C:/…/fig-2-p04.png",
      "crop_box": {"left": 0.04, "top": 0.07, "right": 0.04, "bottom": 0.40},
      "figure_label": "Fig. 2a–c",
      "panel_scope": "Fig. 2a–c：体内标记信号与对照比较",
      "pdf_page": 4,
      "bullets": ["结果 1", "结果 2"],
      "caveat": "统计单位和对照条件以图注与方法为准。",
      "crop_review": {
        "named_panel_matches": true,
        "axes_and_legend_legible": true,
        "article_prose_removed": true
      },
      "source": "Yin et al. (2024), Fig. 2 · PDF p. 4"
    }
  ]
}
```

Rules:

- `paper.citation` and `paper.doi` are copied from the supplied PDF's current title page / metadata, never from a prior run. Each slide's `source` is only a locator such as `Fig. 2d · PDF p. 5` or `Abstract · PDF p. 1`; do not repeat authors there. The composer adds the current `paper.citation` uniformly to every footer. `slides` is the complete page plan. The composer must not insert generic filler pages.
- `meeting.target_seconds` is the planned speaking time, excluding only a small buffer for opening, page turns and questions. It must be derived from the requested duration, not a fixed page count.
- Every slide has an internal `estimated_seconds` value. The sum must plausibly fit `target_seconds`; this is how the planner proves that a 6-minute and a 20-minute meeting do not receive the same deck.
- Every `figure` slide needs an existing `asset`, `figure_label`, `panel_scope`, `pdf_page`, `crop_review`, and `source`.
- If a page needs a panel-level crop, use an internal normalized `crop_box`; run `scripts/materialize_figure_crops.py` before composition. Prefer the smallest crop that contains the named panel, its axes/legend and directly relevant labels; do not preserve adjacent panels merely to make a crop larger. Remove article-body prose and figure-caption paragraphs from the visual crop. The composer receives a real PNG crop, never renderer-specific crop instructions.
- `crop_review` records the visual inspection after materialization. All three checks must be true: the named panel matches the slide, axes/legend are readable, and surrounding article prose / caption text has been removed. This is a release trace, not audience-facing content.
- The crop materializer writes an internal `image_aspect` value. Very wide evidence panels automatically use a full-width figure layout so the data stay legible instead of being squeezed into a narrow left column.
- Use original paper figure assets or readable figure crops, never a blank placeholder.
- Make titles state the conclusion of the current slide, not a section label or production note.
- Keep `bullets` to three evidence-backed statements. On figure slides, each bullet is at most 58 characters and `caveat` is at most 96 characters, so rendered figures never lose space to a paragraph of commentary.
- Include at least one opening/problem slide, one method/context slide, one figure slide, one synthesis slide, and one discussion/questions slide.
- Match page count to the requested duration. Select and consolidate figures before writing the spec; do not delete random slides after composition just to hit a count.
