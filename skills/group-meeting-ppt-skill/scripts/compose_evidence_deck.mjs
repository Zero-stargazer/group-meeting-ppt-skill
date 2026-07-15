/* Compose an editable, evidence-driven group-meeting deck from deck-spec.json. */

import fs from "node:fs/promises";
import path from "node:path";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const argPairs = process.argv.slice(2);
const args = {};
for (let i = 0; i < argPairs.length; i += 2) {
  if (argPairs[i]?.startsWith("--") && argPairs[i + 1]) args[argPairs[i].slice(2)] = argPairs[i + 1];
}
if (!args.spec || !args.out) throw new Error("Usage: node compose_evidence_deck.mjs --spec deck-spec.json --out group_meeting_draft.pptx [--verify verify_checklist.md]");

const specPath = path.resolve(args.spec);
const specDir = path.dirname(specPath);
const spec = JSON.parse(await fs.readFile(specPath, "utf8"));
const paper = spec.paper || {};
const meeting = spec.meeting || {};
const slides = Array.isArray(spec.slides) ? spec.slides : [];

const W = 1280, H = 720, M = 72, FONT = "Microsoft YaHei";
const C = { bg: "#F7F9F6", ink: "#17372F", body: "#263732", muted: "#62736C", green: "#2D6B5B", light: "#E5EFE9", line: "#C9D8D0", amber: "#F6D676", amberText: "#705717", amberBg: "#FFF9E5" };

function clean(value, fallback = "") { return String(value ?? fallback).replace(/\s+/g, " ").trim() || fallback; }
function compactFont(value, base, minimum, comfortableLength) {
  const length = Array.from(clean(value)).length;
  if (length <= comfortableLength) return base;
  return Math.max(minimum, base - Math.ceil((length - comfortableLength) / 8));
}
function resolveAsset(value) { return path.isAbsolute(value) ? value : path.resolve(specDir, value); }
async function bytes(file) { const data = await fs.readFile(file); return data.buffer.slice(data.byteOffset, data.byteOffset + data.byteLength); }
function shape(slide, geometry, left, top, width, height, fill = "none", line = "none") { return slide.shapes.add({ geometry, position: { left, top, width, height }, fill, line: { style: "solid", fill: line, width: line === "none" ? 0 : 1 } }); }
function text(slide, content, left, top, width, height, options = {}) {
  const optionsWithDefaults = { size: 20, color: C.body, bold: false, align: "left", ...options };
  const box = shape(slide, "textbox", left, top, width, height);
  box.text = clean(content);
  box.text.style = { fontFace: FONT, fontSize: optionsWithDefaults.size, color: optionsWithDefaults.color, bold: optionsWithDefaults.bold, alignment: optionsWithDefaults.align, marginLeft: 0, marginRight: 0, marginTop: 0, marginBottom: 0 };
  return box;
}
function rule(slide, top, left = M, width = W - 2 * M) { shape(slide, "rect", left, top, width, 1, C.line, C.line); }
function header(slide, page, section, title) {
  text(slide, String(page).padStart(2, "0"), M, 36, 34, 18, { size: 12, color: C.green, bold: true });
  text(slide, section || "论文组会", 126, 36, 300, 18, { size: 12, color: C.muted, bold: true });
  text(slide, title, M, 64, 1120, 36, { size: compactFont(title, 29, 22, 30), color: C.ink, bold: true });
  rule(slide, 104);
}
function footer(slide, source) { rule(slide, 672); text(slide, source, M, 685, W - 2 * M, 16, { size: 10, color: C.muted }); }
function badge(slide, label, left, top, width = 112) { shape(slide, "rect", left, top, width, 26, C.light, C.light); text(slide, label, left + 12, top + 5, width - 24, 16, { size: 11, color: C.green, bold: true }); }
function bullet(slide, content, left, top, width, height = 62, size = 19) { shape(slide, "ellipse", left, top + 10, 7, 7, C.green, C.green); text(slide, content, left + 22, top, width - 22, height, { size: compactFont(content, size, Math.max(14, size - 4), 32), color: C.body }); }
function sourceFooter(slide, locator, fallback) {
  // The paper citation comes from the current PDF's paper record exactly once.
  // `locator` is only a page / figure location, so a stale author string copied
  // from a previous run cannot silently become a visible footer.
  footer(slide, `${clean(paper.citation, "Source paper PDF")} · ${clean(locator, fallback)}`);
}
function bodyText(slide, body, bullets) {
  if (body) text(slide, body, M, 165, 1080, 120, { size: compactFont(body, 28, 20, 46), color: C.ink, bold: true });
  const start = body ? 348 : 188;
  (bullets || []).slice(0, 3).forEach((item, index) => bullet(slide, item, M, start + index * 102, 1060, 70, 22));
}
function figureSlide(slide, page, input) {
  header(slide, page, input.section || "原文主图", input.title);
  const assetPath = resolveAsset(clean(input.asset));
  const image = input._image;
  if (Number(input.image_aspect || 0) >= 1.45) return wideFigureSlide(slide, page, input, assetPath, image);
  // Figure crops are materialized into real PNGs before composition. Keeping
  // this as a normal contain image avoids renderer-specific black blocks.
  slide.images.add({ blob: image, contentType: "image/png", alt: `${input.figure_label} from source PDF`, fit: "contain", position: { left: 72, top: 136, width: 628, height: 440 }, geometry: "rect" });
  shape(slide, "rect", 72, 136, 628, 440, "none", C.line);
  text(slide, `${clean(input.figure_label)} · PDF p. ${input.pdf_page}`, 72, 590, 628, 16, { size: 10, color: C.muted, align: "center" });
  badge(slide, "本文证据", 770, 150);
  (input.bullets || []).slice(0, 3).forEach((item, index) => bullet(slide, item, 770, 212 + index * 88, 430, 58, 18));
  shape(slide, "rect", 770, 500, 438, 76, C.amberBg, C.amber);
  text(slide, clean(input.caveat), 790, 516, 398, 44, { size: 16, color: C.amberText, bold: true });
  sourceFooter(slide, input.source, `${input.figure_label} · PDF p. ${input.pdf_page}`);
  return assetPath;
}
function wideFigureSlide(slide, page, input, assetPath, image) {
  slide.images.add({ blob: image, contentType: "image/png", alt: `${input.figure_label} from source PDF`, fit: "contain", position: { left: 72, top: 132, width: 1136, height: 336 }, geometry: "rect" });
  shape(slide, "rect", 72, 132, 1136, 336, "none", C.line);
  text(slide, `${clean(input.figure_label)} · PDF p. ${input.pdf_page}`, 72, 474, 1136, 16, { size: 10, color: C.muted, align: "center" });
  badge(slide, "本文证据", 72, 500);
  (input.bullets || []).slice(0, 3).forEach((item, index) => bullet(slide, item, 72, 534 + index * 29, 1128, 28, 17));
  shape(slide, "rect", 72, 625, 1136, 39, C.amberBg, C.amber);
  text(slide, clean(input.caveat), 90, 635, 1098, 20, { size: 14, color: C.amberText, bold: true });
  sourceFooter(slide, input.source, `${input.figure_label} · PDF p. ${input.pdf_page}`);
  return assetPath;
}

const prs = Presentation.create({ slideSize: { width: W, height: H } });
const usedFigures = [];
for (let index = 0; index < slides.length; index += 1) {
  const item = slides[index];
  const page = index + 1;
  const slide = prs.slides.add();
  slide.background.fill = C.bg;
  if (item.type === "title") {
    text(slide, clean(meeting.type, "文献组会"), M, 48, 320, 18, { size: 13, color: C.green, bold: true });
    text(slide, item.title || paper.title, M, 116, 940, 106, { size: compactFont(item.title || paper.title, 38, 26, 32), color: C.ink, bold: true });
    if (item.body || paper.citation) text(slide, item.body || paper.citation, M, 250, 920, 46, { size: 17, color: C.muted });
    if (item.bullets?.[0]) text(slide, item.bullets[0], M, 360, 960, 74, { size: 23, color: C.body });
    sourceFooter(slide, item.source, "Title page · PDF p. 1");
  } else if (item.type === "figure") {
    item._image = await bytes(resolveAsset(item.asset));
    usedFigures.push({ label: item.figure_label, page: item.pdf_page });
    figureSlide(slide, page, item);
  } else {
    header(slide, page, item.section || "论文组会", item.title);
    bodyText(slide, item.body, item.bullets);
    sourceFooter(slide, item.source, "Source paper PDF");
  }
}

const outputPath = path.resolve(args.out);
const pptx = await PresentationFile.exportPptx(prs);
await pptx.save(outputPath);
const verifyPath = path.resolve(args.verify || path.join(path.dirname(outputPath), `${path.basename(outputPath, path.extname(outputPath))}.verify_checklist.md`));
const figureList = usedFigures.map((figure) => `${figure.label}（PDF p. ${figure.page}）`).join("、") || "无图表页";
await fs.writeFile(verifyPath, `# 汇报前核对\n\n- 论文：${clean(paper.citation, paper.title || "Source paper PDF")}\n- 本次使用的原文主图：${figureList}\n- 数值、样本量、时间点、统计单位和图注与原文一致。\n- 相关性、动态推断和因果结论的边界与原文一致。\n- 每张图保留图号与来源信息。\n`, "utf8");
console.log(`Wrote ${slides.length}-slide evidence deck to ${outputPath}`);
console.log(`Wrote verification checklist to ${verifyPath}`);
