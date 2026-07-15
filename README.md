# group-meeting-ppt-skill

> 输入论文 PDF 与汇报时长，自动生成一份可直接用于组会汇报、可编辑的中文 PPTX。

`group-meeting-ppt-skill` 是一个面向中文组会、文献汇报和 journal club 的 Codex Skill。它会读取论文全文与主图，组织研究问题、方法、证据链、结论和讨论问题，并生成一份已填充的可编辑 PPTX。

## 你会得到什么

- 一份已填充、可编辑的 `.pptx`；页数由论文图表链与汇报时长决定。
- 论文原始图表或可读的关键图表区域，均保留图号与来源。
- 结论、证据边界与讨论问题均已写入 PPT。
- 一份简短的事实核对清单。

整个证据提取、图表选择、页数规划、PPT 排版与视觉检查都在 Skill 内部完成：

```text
论文 PDF + 汇报时长
  → 读取全文与主图
  → 按证据链组织汇报
  → 已填充、可编辑的 PPTX
  → 简短事实核对清单
```

用户得到的是可编辑 PPTX 与简短事实核对清单，而不是需要自行拼装的提纲、占位页或制作说明。

## 页数由内容决定

本项目不把“10 页”当作统一答案。

- 从研究问题、主图、回答不同问题的图表面板与汇报时长出发组织页面。
- 密集主图可以拆成多页；短汇报可以合并证据，不用空白页凑页数。
- 不把多个关键图硬塞到同一张不可读的页面中。

## 最快体验

把论文 PDF 与汇报时长交给 Codex，例如：

```text
用 group-meeting-ppt-skill 把这篇 PDF 做成 12 分钟中文文献组会 PPT。
```

正常交付为：

```text
group_meeting_draft.pptx
verify_checklist.md
```

内部的证据规格、图表地图与渲染记录用于追溯和质量检查；汇报者不需要据此重新搭建 PPT。

## 与 paper-triage-skill 的交接

```text
候选论文
  → paper-triage-skill
  → handoff_to_group_meeting.json / .md
  → group-meeting-ppt-skill
  → 可编辑的组会 PPTX
```

交接文件可以包含：入选原因、建议优先读的章节/图表、待核对主张与可能的讨论问题。

## 环境自检与回归测试

这部分只用于验证仓库环境和回归测试；它不是用户交付路径。

```powershell
python skills/group-meeting-ppt-skill/scripts/check_env.py
python -m unittest discover -s tests -v
```

完整的 PDF 成品路径在 Codex 的 presentation workspace 中使用 `@oai/artifact-tool` 生成 PPTX。公开版本不把旧式 JSON→固定页数 PPT 辅助脚本当作使用入口。

## 项目结构

```text
group-meeting-ppt-skill/
  README.md
  LICENSE
  skills/group-meeting-ppt-skill/
    SKILL.md
    agents/openai.yaml
    references/
    scripts/
      check_env.py
      render_pdf_figure_assets.py
      materialize_figure_crops.py
      validate_deck_spec.py
      compose_evidence_deck.mjs
  examples/
    README.md
  tests/
```

## 使用前的事实核对

正式汇报前请核对数字、单位、样本量、统计单位、图注、相关性和因果边界是否与原文一致。Skill 不伪造数据、引用或结论，也不会承诺导师认可或成绩结果。

## 2026-07 更新

- 图表改为面板级实图裁切；图中不得夹带论文正文或整段图注。
- 页脚引用统一从本次 PDF 的论文记录生成，避免旧论文信息残留。
- 每份成品在交付前需通过规格校验、全页渲染检查和溢出检测。

## License

MIT License. See [LICENSE](LICENSE).
