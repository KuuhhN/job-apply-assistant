#!/usr/bin/env python3
"""中文简历 PDF 渲染引擎 v2（初版模板风格 + 照片支持）

用法:
  python tools/resume_render.py --data resume.json --photo photo_circle.png --output 简历.pdf

v2 版式（对齐中文简历模板惯例）:
  - 顶部 Table：姓名+联系信息（居中）｜右侧圆形照片
  - 蓝色加粗区块标题 + 蓝色横线分隔
  - 正文缩进、留白充足
resume.json 结构见 references/resume-json-schema.md；可选字段 "photo": 路径。
"""
import argparse
import json
import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Paragraph, SimpleDocTemplate, Table, TableStyle,
                                HRFlowable, Image as RLImage)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER

# 中文字体候选（Windows 优先，macOS 兜底）
FONT_CANDIDATES = [
    (r"C:\Windows\Fonts\msyh.ttc", 0, "MSYaHei"),
    (r"C:\Windows\Fonts\msyh.ttc", 1, "MSYaHei-Bold"),
    (r"C:\Windows\Fonts\simsun.ttc", 0, "SimSun"),
    (r"C:\Windows\Fonts\simhei.ttf", 0, "SimHei"),
    ("/System/Library/Fonts/STHeiti Medium.ttc", 0, "STHeiti-Medium"),
    ("/System/Library/Fonts/Hiragino Sans GB.ttc", 0, "HiraginoSansGB"),
]
ACCENT = colors.HexColor("#1a5fb4")   # 主题蓝
GRAY = colors.HexColor("#555555")
DARKGRAY = colors.HexColor("#444444")


def register_font() -> tuple:
    """注册可用中文字体,返回 (normal, bold) 字体名"""
    normal = bold = None
    for path, subfont, name in FONT_CANDIDATES:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont(name, path, subfontIndex=subfont))
                if subfont == 0 and normal is None:
                    normal = name
                if subfont == 1 and bold is None:
                    bold = name
            except Exception as e:
                print(f"[font] {path} (subfont {subfont}) failed: {e}")
    if normal is None:
        raise RuntimeError("no usable CJK font found")
    if bold is None:
        bold = normal
    pdfmetrics.registerFontFamily(normal, normal=normal, bold=bold,
                                  italic=normal, boldItalic=bold)
    print(f"[font] normal='{normal}' bold='{bold}'")
    return normal, bold


def _entry_paragraphs(entry: dict, styles: dict, font: str) -> list:
    out = []
    head = entry.get("title", "")
    if entry.get("date"):
        head += f"　　{entry['date']}"
    out.append(Paragraph(head, styles["entry"]))
    for b in entry.get("bullets") or []:
        out.append(Paragraph(f"• {b}", styles["bullet"]))
    return out


def render(data: dict, output: str, photo: str = "") -> None:
    font, bold = register_font()
    doc = SimpleDocTemplate(
        output, pagesize=A4,
        leftMargin=16 * mm, rightMargin=16 * mm,
        topMargin=12 * mm, bottomMargin=14 * mm,
        title=data.get("name", "简历"),
    )
    styles = {
        "name": ParagraphStyle("name", fontName=bold, fontSize=22, leading=28,
                               alignment=TA_CENTER, spaceAfter=2),
        "contact": ParagraphStyle("contact", fontName=font, fontSize=9.5, leading=15.5,
                                  alignment=TA_CENTER, textColor=GRAY, spaceAfter=3),
        "summary": ParagraphStyle("summary", fontName=font, fontSize=10, leading=15,
                                  alignment=TA_CENTER, textColor=DARKGRAY,
                                  spaceBefore=4, spaceAfter=2),
        "section": ParagraphStyle("section", fontName=bold, fontSize=12.5, leading=16,
                                  spaceBefore=9, spaceAfter=1, textColor=ACCENT),
        "body": ParagraphStyle("body", fontName=font, fontSize=10, leading=15,
                               alignment=TA_LEFT, leftIndent=6, rightIndent=6),
        "entry": ParagraphStyle("entry", fontName=bold, fontSize=10.5, leading=15,
                                spaceBefore=3, spaceAfter=1, leftIndent=2),
        "bullet": ParagraphStyle("bullet", fontName=font, fontSize=10, leading=14.5,
                                 leftIndent=14, bulletIndent=0, spaceAfter=1,
                                 rightIndent=4),
    }
    story = []
    # ---- 顶部：姓名/联系（左） + 照片（右） ----
    title_line = data.get("name", "")
    if data.get("title"):
        title_line += f"  ·  {data['title']}"
    left_flow = [Paragraph(title_line, styles["name"])]
    contact_parts = []
    for k in ("email", "phone", "location", "github"):
        if data.get(k):
            contact_parts.append(str(data[k]))
    if contact_parts:
        left_flow.append(Paragraph("  |  ".join(contact_parts), styles["contact"]))
    if data.get("summary"):
        left_flow.append(Paragraph(data["summary"], styles["summary"]))

    photo_flow = []
    if photo and os.path.exists(photo):
        try:
            img = RLImage(photo, width=64, height=64)
            img.hAlign = "RIGHT"
            photo_flow.append(img)
        except Exception as e:
            print(f"[photo] 加载失败: {e}")

    if photo_flow:
        header = Table([[left_flow, photo_flow]], colWidths=[None, 80])
        header.setStyle(TableStyle([
            ("VALIGN", (0, 0), (0, 0), "MIDDLE"),
            ("VALIGN", (1, 0), (1, 0), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))
        story.append(header)
    else:
        story.append(Paragraph(title_line, styles["name"]))
        if contact_parts:
            story.append(Paragraph("  |  ".join(contact_parts), styles["contact"]))
        if data.get("summary"):
            story.append(Paragraph(data["summary"], styles["summary"]))

    # ---- 技能 ----
    if data.get("skills"):
        story.append(Paragraph("技能专长", styles["section"]))
        story.append(HRFlowable(width="100%", thickness=1.1, color=ACCENT,
                                spaceBefore=2, spaceAfter=5))
        story.append(Paragraph(" · ".join(data["skills"]), styles["body"]))

    # ---- 自定义区块 ----
    for section_title, content in (data.get("sections") or {}).items():
        story.append(Paragraph(section_title, styles["section"]))
        story.append(HRFlowable(width="100%", thickness=1.1, color=ACCENT,
                                spaceBefore=2, spaceAfter=5))
        if isinstance(content, list):
            if content and isinstance(content[0], dict):
                for item in content:
                    story.extend(_entry_paragraphs(item, styles, font))
            else:
                for line in content:
                    story.append(Paragraph(str(line), styles["body"]))
        else:
            for line in str(content).split("\n"):
                story.append(Paragraph(line, styles["body"]))

    doc.build(story)
    print(f"[render] OK -> {output} ({os.path.getsize(output)} bytes)")


def main():
    ap = argparse.ArgumentParser(description="中文简历 PDF 渲染 v2")
    ap.add_argument("--data", default="", help="resume.json 路径")
    ap.add_argument("--photo", default="", help="照片路径（PNG，圆形效果最佳）")
    ap.add_argument("--output", default="out/resume.pdf")
    args = ap.parse_args()
    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)
    photo = args.photo or data.get("photo", "")
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    render(data, args.output, photo)


if __name__ == "__main__":
    main()
