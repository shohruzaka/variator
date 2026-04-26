"""Excel (xlsx) formatda javoblar kalitini eksport qilish (8-bosqich)."""

from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font

from src.models import Variant


def export_answers_to_xlsx(variants: list[Variant], output_path: str | Path) -> Path:
    """Barcha variantlarning javoblarini bitta Excel fayliga yozadi.

    Jadval tuzilishi:
    Qatorlar: Variant raqamlari
    Ustunlar: Variant No, 1-savol, 2-savol, ...

    Args:
        variants: Generatsiya qilingan test variantlari ro'yxati.
        output_path: Saqlanadigan Excel faylining to'liq manzili.

    Returns:
        Yaratilgan faylning manzili.
    """
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    wb = Workbook()
    ws = wb.active
    ws.title = "Javoblar kaliti"

    if not variants:
        wb.save(out_path)
        return out_path

    # Maksimal savollar sonini aniqlash (ustunlar uchun)
    max_questions = max(len(v.questions) for v in variants)

    # 1. Sarlavha qatorini yozish
    header = ["Variant"] + [str(i + 1) for i in range(max_questions)]
    ws.append(header)

    # Sarlavha dizayni (Qalin harf va markazlashtirilgan)
    header_font = Font(bold=True)
    header_align = Alignment(horizontal="center", vertical="center")
    
    for cell in ws[1]:
        cell.font = header_font
        cell.alignment = header_align

    # 2. Har bir variant javoblarini yozish
    for variant in variants:
        row_data = [f"{variant.number}-Variant"] + variant.answer_key
        ws.append(row_data)

    # Hujayralarni markazlashtirish (Variant nomidan tashqari)
    for row in ws.iter_rows(min_row=2, max_col=max_questions + 1):
        for cell in row[1:]:
            cell.alignment = Alignment(horizontal="center")

    # Ustunlar kengligini to'g'rilash
    ws.column_dimensions["A"].width = 15
    for i in range(2, max_questions + 2):
        col_letter = ws.cell(row=1, column=i).column_letter
        ws.column_dimensions[col_letter].width = 5

    wb.save(out_path)
    return out_path
