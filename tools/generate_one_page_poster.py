#!/usr/bin/env python
"""Generate a bright one-page poster for the group-meeting PPT skill."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


W, H = 1080, 1440
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "media" / "group_meeting_ppt_skill_one_page_bright_20260703.png"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    bold_candidates = [
        Path(r"C:\Windows\Fonts\simhei.ttf"),
        Path(r"C:\Windows\Fonts\msyhbd.ttc"),
        Path(r"C:\Windows\Fonts\Dengb.ttf"),
        Path(r"C:\Windows\Fonts\NotoSansSC-VF.ttf"),
    ]
    regular_candidates = [
        Path(r"C:\Windows\Fonts\msyh.ttc"),
        Path(r"C:\Windows\Fonts\Deng.ttf"),
        Path(r"C:\Windows\Fonts\NotoSansSC-VF.ttf"),
        Path(r"C:\Windows\Fonts\simsun.ttc"),
    ]
    for path in bold_candidates if bold else regular_candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


F = {
    "small": font(28),
    "small_b": font(28, True),
    "body": font(34),
    "body_b": font(34, True),
    "mid": font(42, True),
    "title": font(74, True),
}

BLUE = (42, 109, 255)
BLUE_2 = (84, 154, 255)
CYAN = (36, 205, 220)
PURPLE = (132, 94, 247)
NAVY = (33, 46, 78)
TEXT = (39, 52, 86)
MUTED = (97, 112, 145)
LINE = (212, 224, 247)
WHITE = (255, 255, 255)
ORANGE = (255, 179, 84)


def build() -> Image.Image:
    img = Image.new("RGB", (W, H), (252, 249, 240))
    draw = ImageDraw.Draw(img)

    for y in range(H):
        t = y / H
        r = int(252 * (1 - t) + 232 * t)
        g = int(249 * (1 - t) + 244 * t)
        b = int(240 * (1 - t) + 255 * t)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    blob = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    blob_draw = ImageDraw.Draw(blob)
    blob_draw.ellipse((-160, 40, 360, 560), fill=(62, 172, 255, 38))
    blob_draw.ellipse((720, -130, 1240, 390), fill=(132, 94, 247, 33))
    blob_draw.ellipse((710, 1030, 1220, 1540), fill=(36, 205, 220, 36))
    blob = blob.filter(ImageFilter.GaussianBlur(8))
    img = Image.alpha_composite(img.convert("RGBA"), blob).convert("RGB")
    draw = ImageDraw.Draw(img)

    def rounded(xy, radius, fill, outline=None, width=1):
        draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)

    def shadow_card(xy, radius=28, fill=WHITE, shadow=(70, 95, 140, 32), offset=(0, 10), blur=18, outline=None):
        nonlocal img, draw
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(layer)
        x1, y1, x2, y2 = xy
        ox, oy = offset
        shadow_draw.rounded_rectangle((x1 + ox, y1 + oy, x2 + ox, y2 + oy), radius=radius, fill=shadow)
        layer = layer.filter(ImageFilter.GaussianBlur(blur))
        img = Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline or LINE, width=2)

    def text_box(xy, value, fnt, fill=TEXT, spacing=8, max_width=None, align="left"):
        x, y = xy
        if max_width is None:
            draw.multiline_text((x, y), value, font=fnt, fill=fill, spacing=spacing, align=align)
            return
        lines = []
        for para in value.split("\n"):
            cur = ""
            for ch in para:
                candidate = cur + ch
                if draw.textlength(candidate, font=fnt) <= max_width or not cur:
                    cur = candidate
                else:
                    lines.append(cur)
                    cur = ch
            lines.append(cur)
        draw.multiline_text((x, y), "\n".join(lines), font=fnt, fill=fill, spacing=spacing, align=align)

    def pill(x, y, w, h, label, fill, fg=WHITE, fnt=None):
        rounded((x, y, x + w, y + h), h // 2, fill)
        fnt = fnt or F["small_b"]
        tw = draw.textlength(label, font=fnt)
        bbox = draw.textbbox((0, 0), label, font=fnt)
        th = bbox[3] - bbox[1]
        draw.text((x + (w - tw) / 2, y + (h - th) / 2 - 2), label, font=fnt, fill=fg)

    pill(68, 58, 430, 56, "给研一 / 硕博的 AI 组会救急包", (235, 243, 255), BLUE, F["small_b"])
    pill(765, 58, 245, 56, "可编辑 PPTX", (241, 232, 255), PURPLE, F["small_b"])

    text_box((68, 150), "把一篇PDF", F["title"], NAVY)
    text_box((68, 235), "变成 10 页", F["title"], NAVY)
    highlight_y = 320
    rounded((63, highlight_y - 3, 710, highlight_y + 92), 28, (227, 239, 255))
    draw.text((86, highlight_y), "组会PPT草稿", font=F["title"], fill=BLUE)
    text_box(
        (72, 430),
        "不是代写，也不是空泛提示词。\n它先帮你搭好“能拿去改”的汇报骨架。",
        F["body"],
        MUTED,
        spacing=10,
        max_width=900,
    )

    shadow_card((58, 555, 1022, 950), radius=34, fill=WHITE, outline=(219, 230, 250))
    pill(86, 585, 168, 48, "工作流", BLUE, WHITE, F["small_b"])
    draw.text((280, 588), "输入 PDF，输出组会草稿", font=F["body_b"], fill=NAVY)

    nodes = [
        (92, 670, 330, 830, "输入", ["PDF论文", "研究方向", "汇报时长"]),
        (430, 665, 650, 835, "Skill", ["提取notes", "自动拆结构", "按组会逻辑"]),
        (760, 670, 1002, 830, "输出", ["10页PPTX", "每页讲什么", "老师追问清单"]),
    ]
    for x1, y1, x2, y2, head, items in nodes:
        fill = (239, 247, 255) if head != "Skill" else (235, 251, 252)
        outline = (175, 205, 255) if head != "Skill" else (142, 224, 229)
        rounded((x1, y1, x2, y2), 26, fill, outline, 2)
        draw.text((x1 + 24, y1 + 22), head, font=F["mid"], fill=BLUE if head != "Skill" else (0, 151, 166))
        yy = y1 + 82
        for item in items:
            draw.text((x1 + 24, yy), "• " + item, font=F["small"], fill=TEXT)
            yy += 38
    for sx, ex in [(350, 410), (670, 740)]:
        draw.line((sx, 750, ex, 750), fill=BLUE_2, width=8)
        draw.polygon([(ex, 750), (ex - 22, 736), (ex - 22, 764)], fill=BLUE_2)

    rounded((92, 866, 988, 920), 22, (255, 248, 233), (255, 217, 153), 2)
    draw.text((124, 877), "还会提醒：哪些数据、图注、结论必须回原文核对", font=F["small_b"], fill=(143, 91, 24))

    shadow_card((58, 1000, 500, 1282), radius=32, fill=WHITE, outline=(219, 230, 250))
    pill(90, 1030, 156, 46, "PPT预览", PURPLE, WHITE, F["small_b"])
    rounded((96, 1092, 462, 1244), 18, (246, 250, 255), (201, 219, 250), 2)
    draw.text((122, 1118), "Slide 01｜论文一句话", font=F["small_b"], fill=BLUE)
    draw.rounded_rectangle((122, 1168, 430, 1186), radius=8, fill=(203, 225, 255))
    draw.rounded_rectangle((122, 1200, 375, 1217), radius=8, fill=(224, 235, 253))
    draw.rounded_rectangle((122, 1228, 320, 1240), radius=6, fill=(224, 235, 253))

    shadow_card((538, 1000, 1022, 1282), radius=32, fill=WHITE, outline=(219, 230, 250))
    pill(570, 1030, 178, 46, "你拿到的", CYAN, WHITE, F["small_b"])
    items = ["10页文献汇报PPT", "每页讲法和画面建议", "老师可能追问清单", "学术诚信自查清单"]
    y = 1098
    for i, item in enumerate(items):
        color = [BLUE, PURPLE, (0, 154, 169), ORANGE][i]
        draw.ellipse((576, y + 8, 600, y + 32), fill=color)
        draw.text((618, y), item, font=F["body_b"], fill=TEXT)
        y += 44

    shadow_card((58, 1322, 1022, 1400), radius=28, fill=(35, 93, 255), shadow=(35, 93, 255, 38), outline=(35, 93, 255))
    draw.text((90, 1342), "评论 / 私信：组会", font=F["mid"], fill=WHITE)
    draw.text((470, 1348), "领取 group-meeting-ppt-skill", font=F["body_b"], fill=(229, 245, 255))
    return img


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    img = build()
    img.save(OUT, quality=95)
    print(OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
