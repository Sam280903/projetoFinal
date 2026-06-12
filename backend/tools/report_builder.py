import io
import re
import unicodedata
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
    Table, TableStyle, PageBreak, KeepTogether,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import Frame, PageTemplate
from reportlab.pdfgen import canvas as pdfcanvas

# ── Paleta ────────────────────────────────────────────────────────────────────
INDIGO     = colors.HexColor("#6366f1")
INDIGO_L   = colors.HexColor("#e0e7ff")
PURPLE     = colors.HexColor("#8b5cf6")
DARK       = colors.HexColor("#111827")
GRAY_700   = colors.HexColor("#374151")
GRAY_500   = colors.HexColor("#6b7280")
GRAY_200   = colors.HexColor("#e5e7eb")
GRAY_50    = colors.HexColor("#f9fafb")
WHITE      = colors.HexColor("#ffffff")
GREEN      = colors.HexColor("#16a34a")
YELLOW     = colors.HexColor("#ca8a04")
RED        = colors.HexColor("#dc2626")


def _score_color(v: int):
    if v >= 70: return GREEN
    if v >= 50: return YELLOW
    return RED


def _clean(text: str) -> str:
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*',     r'\1', text)
    text = re.sub(r'`(.+?)`',       r'\1', text)
    text = re.sub(r'```[\s\S]*?```', '',   text)
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    return text.strip()


def _page_footer(canvas, doc):
    """Rodapé com número de página em todas as páginas."""
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(GRAY_500)
    canvas.drawString(2 * cm, 1.2 * cm, "PitchIQ · Sistema multi-agente de validação estratégica")
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Página {doc.page}")
    canvas.setStrokeColor(GRAY_200)
    canvas.setLineWidth(0.5)
    canvas.line(2 * cm, 1.5 * cm, A4[0] - 2 * cm, 1.5 * cm)
    canvas.restoreState()


def generate_pdf(idea: str, report: str, score: dict | None = None) -> bytes:
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2.2 * cm,
        leftMargin=2.2 * cm,
        topMargin=2.5 * cm,
        bottomMargin=2.5 * cm,
        onFirstPage=_page_footer,
        onLaterPages=_page_footer,
    )

    W = A4[0] - 4.4 * cm  # largura útil

    # ── Estilos ───────────────────────────────────────────────────────────────
    s = getSampleStyleSheet()

    title_st = ParagraphStyle("PT", parent=s["Normal"],
        fontSize=30, fontName="Helvetica-Bold",
        textColor=INDIGO, alignment=TA_CENTER, spaceAfter=2)

    sub_st = ParagraphStyle("PS", parent=s["Normal"],
        fontSize=11, textColor=GRAY_500,
        alignment=TA_CENTER, spaceAfter=10)

    idea_st = ParagraphStyle("PI", parent=s["Normal"],
        fontSize=11, textColor=GRAY_700, fontName="Helvetica-Oblique",
        alignment=TA_CENTER, spaceAfter=0,
        borderPad=10, leading=16)

    sec_title_st = ParagraphStyle("ST", parent=s["Normal"],
        fontSize=12, fontName="Helvetica-Bold",
        textColor=INDIGO, spaceBefore=4, spaceAfter=6)

    body_st = ParagraphStyle("B", parent=s["Normal"],
        fontSize=10, textColor=DARK,
        leading=16, spaceAfter=4)

    bullet_st = ParagraphStyle("BU", parent=s["Normal"],
        fontSize=10, textColor=DARK,
        leading=16, spaceAfter=3,
        leftIndent=12, firstLineIndent=-8)

    num_st = ParagraphStyle("NU", parent=s["Normal"],
        fontSize=10, textColor=DARK,
        leading=16, spaceAfter=3,
        leftIndent=14, firstLineIndent=-14)

    label_st = ParagraphStyle("LB", parent=s["Normal"],
        fontSize=9, textColor=GRAY_500,
        alignment=TA_CENTER)

    score_big_st = ParagraphStyle("SB", parent=s["Normal"],
        fontSize=48, fontName="Helvetica-Bold",
        alignment=TA_CENTER, spaceAfter=0)

    score_label_st = ParagraphStyle("SL", parent=s["Normal"],
        fontSize=10, textColor=GRAY_500,
        alignment=TA_CENTER, spaceAfter=0)

    story = []

    # ── CAPA ──────────────────────────────────────────────────────────────────
    # Barra colorida no topo via tabela
    header_table = Table(
        [[ Paragraph("<b>PitchIQ</b>", ParagraphStyle("HT", parent=s["Normal"],
            fontSize=28, fontName="Helvetica-Bold",
            textColor=WHITE, alignment=TA_CENTER)) ]],
        colWidths=[W], rowHeights=[1.8 * cm],
    )
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), INDIGO),
        ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 14),
        ("BOTTOMPADDING", (0,0), (-1,-1), 14),
        ("ROUNDEDCORNERS", [6, 6, 6, 6]),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("Relatório de Validação Estratégica", sub_st))

    # Caixa da ideia
    idea_box = Table(
        [[ Paragraph(f'&quot;{_clean(idea)}&quot;', idea_st) ]],
        colWidths=[W],
    )
    idea_box.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), GRAY_50),
        ("BOX",           (0,0), (-1,-1), 1, GRAY_200),
        ("TOPPADDING",    (0,0), (-1,-1), 12),
        ("BOTTOMPADDING", (0,0), (-1,-1), 12),
        ("LEFTPADDING",   (0,0), (-1,-1), 14),
        ("RIGHTPADDING",  (0,0), (-1,-1), 14),
        ("ROUNDEDCORNERS", [4, 4, 4, 4]),
    ]))
    story.append(idea_box)
    story.append(Spacer(1, 0.5 * cm))

    # ── SCORE ─────────────────────────────────────────────────────────────────
    if score:
        overall = score.get("overall", 0)
        dims    = score.get("dimensions", {})
        LABELS  = {
            "mercado":     "Mercado",
            "competicao":  "Competição",
            "execucao":    "Execução",
            "timing":      "Timing",
            "monetizacao": "Monetização",
            "inovacao":    "Inovação",
        }

        # Score geral — bloco único centralizado
        c_score = _score_color(overall)
        score_section = Table([
            [Paragraph("Score de Viabilidade", ParagraphStyle("SL2", parent=s["Normal"],
                fontSize=9, textColor=GRAY_500, alignment=TA_CENTER))],
            [Paragraph(
                f'<font size="52" name="Helvetica-Bold" color="{c_score.hexval()}">{overall}</font>'
                f'<font size="18" color="#6b7280"> /100</font>',
                ParagraphStyle("SN2", parent=s["Normal"],
                    alignment=TA_CENTER, leading=58, spaceAfter=0))],
            [Paragraph("✓ &nbsp;9 agentes de IA · Pesquisa + Debate + Síntese",
                ParagraphStyle("META", parent=s["Normal"],
                fontSize=8, textColor=GRAY_500, alignment=TA_CENTER))],
        ], colWidths=[W], rowHeights=[0.45 * cm, 1.8 * cm, 0.45 * cm])
        score_section.setStyle(TableStyle([
            ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
            ("ALIGN",         (0,0), (-1,-1), "CENTER"),
            ("BACKGROUND",    (0,0), (-1,-1), GRAY_50),
            ("BOX",           (0,0), (-1,-1), 1, GRAY_200),
            ("TOPPADDING",    (0,0), (-1,-1), 8),
            ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ]))
        story.append(score_section)
        story.append(Spacer(1, 0.3 * cm))

        # Grid de dimensões 3x2
        if dims:
            dim_items = list(dims.items())
            rows = []
            for i in range(0, len(dim_items), 3):
                chunk = dim_items[i:i+3]
                while len(chunk) < 3:
                    chunk.append(("", 0))
                row = []
                for key, val in chunk:
                    if not key:
                        row.append("")
                        continue
                    cell = Table([
                        [Paragraph(str(val), ParagraphStyle("DV", parent=s["Normal"],
                            fontSize=20, fontName="Helvetica-Bold",
                            textColor=_score_color(val), alignment=TA_CENTER))],
                        [Paragraph(LABELS.get(key, key), ParagraphStyle("DL", parent=s["Normal"],
                            fontSize=8, textColor=GRAY_500, alignment=TA_CENTER))],
                    ], colWidths=[W / 3 - 0.2 * cm])
                    cell.setStyle(TableStyle([
                        ("ALIGN",         (0,0), (-1,-1), "CENTER"),
                        ("TOPPADDING",    (0,0), (-1,-1), 8),
                        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
                    ]))
                    row.append(cell)
                rows.append(row)

            grid = Table(rows, colWidths=[W/3] * 3)
            grid.setStyle(TableStyle([
                ("BACKGROUND",    (0,0), (-1,-1), WHITE),
                ("BOX",           (0,0), (-1,-1), 1, GRAY_200),
                ("INNERGRID",     (0,0), (-1,-1), 0.5, GRAY_200),
                ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
                ("TOPPADDING",    (0,0), (-1,-1), 4),
                ("BOTTOMPADDING", (0,0), (-1,-1), 4),
            ]))
            story.append(grid)

        story.append(Spacer(1, 0.5 * cm))

    story.append(HRFlowable(width="100%", thickness=1, color=INDIGO, spaceAfter=6))

    # ── SEÇÕES DO RELATÓRIO ───────────────────────────────────────────────────
    clean_report = re.sub(r'```json[\s\S]*?```', '', report).strip()
    sections = re.split(r'(?=^#{1,3} )', clean_report, flags=re.MULTILINE)

    num_re    = re.compile(r'^\d+\.\s+')
    bullet_re = re.compile(r'^[-*]\s+')

    for section in sections:
        if not section.strip():
            continue

        lines      = section.strip().split("\n")
        header     = lines[0]
        body_lines = [l for l in lines[1:]]
        title_text = re.sub(r'^#+\s*\d*\.?\s*', '', header).strip()

        if not title_text:
            continue

        block = []

        # Título com barra lateral indigo
        title_row = Table(
            [[ "", Paragraph(_clean(title_text), sec_title_st) ]],
            colWidths=[0.25 * cm, W - 0.25 * cm],
        )
        title_row.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (0,-1), INDIGO),
            ("TOPPADDING",    (0,0), (-1,-1), 4),
            ("BOTTOMPADDING", (0,0), (-1,-1), 4),
            ("LEFTPADDING",   (1,0), (1,-1), 8),
            ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ]))
        block.append(title_row)
        block.append(Spacer(1, 0.1 * cm))

        for line in body_lines:
            stripped = line.strip()
            if not stripped:
                block.append(Spacer(1, 0.1 * cm))
                continue

            if bullet_re.match(stripped):
                text = bullet_re.sub('', stripped)
                block.append(Paragraph(f"• {_clean(text)}", bullet_st))
            elif num_re.match(stripped):
                m    = num_re.match(stripped)
                num  = m.group().strip()
                text = stripped[m.end():]
                block.append(Paragraph(f"<b>{num}</b> {_clean(text)}", num_st))
            else:
                block.append(Paragraph(_clean(stripped), body_st))

        block.append(Spacer(1, 0.35 * cm))
        # Mantém título + primeira linha juntos (evita título órfão no fim da página)
        story.append(KeepTogether(block[:3]))
        story.extend(block[3:])

    doc.build(story)
    buffer.seek(0)
    return buffer.read()
