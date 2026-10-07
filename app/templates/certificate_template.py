from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


def _wrap_text(text: str, font_name: str, font_size: int, max_width: float) -> list[str]:
    lines: list[str] = []
    current_line = ""
    for word in text.split():
        candidate = f"{current_line} {word}".strip()
        if current_line and stringWidth(candidate, font_name, font_size) > max_width:
            lines.append(current_line)
            current_line = word
        else:
            current_line = candidate
    if current_line:
        lines.append(current_line)
    return lines


def _draw_centered_text(
    pdf: canvas.Canvas,
    text: str,
    center_x: float,
    baseline_y: float,
    font_name: str,
    font_size: int,
    max_width: float,
    color: HexColor,
    leading: float,
) -> float:
    lines = _wrap_text(text, font_name, font_size, max_width)
    while len(lines) > 2 and font_size > 16:
        font_size -= 1
        leading -= 1
        lines = _wrap_text(text, font_name, font_size, max_width)

    pdf.setFillColor(color)
    pdf.setFont(font_name, font_size)
    for line in lines:
        pdf.drawCentredString(center_x, baseline_y, line)
        baseline_y -= leading
    return baseline_y


def generate_certificate(
    output_path: Path,
    recipient_name: str,
    event_name: str,
    event_date: str,
) -> None:
    """Generate a landscape certificate PDF with the standard design."""
    pdf = canvas.Canvas(str(output_path), pagesize=landscape(A4))
    pdf.setTitle(f"Certificate - {recipient_name}")
    pdf.setAuthor("Bulk Certificate Generator")

    width, height = landscape(A4)
    center_x = width / 2
    evergreen = HexColor("#173F35")
    gold = HexColor("#B58A43")
    ink = HexColor("#26332F")
    muted = HexColor("#68736D")
    paper = HexColor("#FBFAF6")
    pale_green = HexColor("#E9EFEA")

    pdf.setFillColor(paper)
    pdf.rect(0, 0, width, height, fill=1, stroke=0)

    pdf.setStrokeColor(evergreen)
    pdf.setLineWidth(1.7)
    pdf.rect(12 * mm, 12 * mm, width - 24 * mm, height - 24 * mm)
    pdf.setStrokeColor(gold)
    pdf.setLineWidth(0.65)
    pdf.rect(15 * mm, 15 * mm, width - 30 * mm, height - 30 * mm)

    # Corner details keep the frame decorative without crowding the content.
    corner = 9 * mm
    inset = 19 * mm
    pdf.setStrokeColor(gold)
    pdf.setLineWidth(1.2)
    for x_direction in (1, -1):
        for y_direction in (1, -1):
            x = inset if x_direction == 1 else width - inset
            y = inset if y_direction == 1 else height - inset
            pdf.line(x, y, x + x_direction * corner, y)
            pdf.line(x, y, x, y + y_direction * corner)

    pdf.setFillColor(evergreen)
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawCentredString(center_x, height - 30 * mm, "BULK CERTIFICATE GENERATOR")

    pdf.setFillColor(gold)
    pdf.setFont("Helvetica-Bold", 27)
    pdf.drawCentredString(center_x, height - 48 * mm, "CERTIFICATE")
    pdf.setFillColor(evergreen)
    pdf.setFont("Helvetica", 12)
    pdf.drawCentredString(center_x, height - 57 * mm, "OF COMPLETION")

    divider_y = height - 66 * mm
    pdf.setStrokeColor(gold)
    pdf.setLineWidth(0.8)
    pdf.line(center_x - 48 * mm, divider_y, center_x - 4 * mm, divider_y)
    pdf.line(center_x + 4 * mm, divider_y, center_x + 48 * mm, divider_y)
    pdf.setFillColor(gold)
    pdf.saveState()
    pdf.translate(center_x, divider_y)
    pdf.rotate(45)
    pdf.rect(-2 * mm, -2 * mm, 4 * mm, 4 * mm, fill=1, stroke=0)
    pdf.restoreState()

    pdf.setFillColor(muted)
    pdf.setFont("Helvetica", 11)
    pdf.drawCentredString(center_x, height - 81 * mm, "THIS CERTIFICATE IS PRESENTED TO")

    _draw_centered_text(
        pdf,
        recipient_name,
        center_x,
        height - 98 * mm,
        "Helvetica-Bold",
        27,
        width - 100 * mm,
        evergreen,
        10 * mm,
    )

    pdf.setFillColor(ink)
    pdf.setFont("Helvetica", 11)
    pdf.drawCentredString(center_x, height - 119 * mm, "For successfully completing")
    _draw_centered_text(
        pdf,
        event_name,
        center_x,
        height - 130 * mm,
        "Helvetica-Bold",
        16,
        width - 100 * mm,
        ink,
        7 * mm,
    )

    pdf.setFillColor(muted)
    pdf.setFont("Helvetica", 10)
    pdf.drawCentredString(center_x, height - 150 * mm, f"ISSUED {event_date}")

    footer_y = 30 * mm
    pdf.setStrokeColor(gold)
    pdf.setLineWidth(0.8)
    pdf.line(48 * mm, footer_y + 8 * mm, 102 * mm, footer_y + 8 * mm)
    pdf.setFillColor(ink)
    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawCentredString(75 * mm, footer_y + 3 * mm, "PROGRAM DIRECTOR")
    pdf.setFillColor(muted)
    pdf.setFont("Helvetica", 7)
    pdf.drawCentredString(75 * mm, footer_y - 2 * mm, "AUTHORIZED SIGNATURE")

    seal_x = width - 55 * mm
    seal_y = footer_y + 10 * mm
    pdf.setFillColor(pale_green)
    pdf.circle(seal_x, seal_y, 16 * mm, fill=1, stroke=0)
    pdf.setStrokeColor(evergreen)
    pdf.setLineWidth(1.1)
    pdf.circle(seal_x, seal_y, 13 * mm, fill=0, stroke=1)
    pdf.setFillColor(evergreen)
    pdf.setFont("Helvetica-Bold", 7)
    pdf.drawCentredString(seal_x, seal_y + 2 * mm, "COMPLETION")
    pdf.setFillColor(gold)
    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawCentredString(seal_x, seal_y - 3 * mm, "CERTIFIED")

    pdf.save()