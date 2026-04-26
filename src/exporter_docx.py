"""Word (docx) fayllarga eksport qilish (7-bosqich).

Bu modul `Variant` obyektlarini o'qib, ularni foydalanuvchiga taqdim
etishga tayyor `.docx` fayllarga aylantiradi va `output/` papkasiga saqlaydi.
Faqat fayl yozish bilan shug'ullanadi.
"""

import os
from pathlib import Path

from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_ORIENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from src.models import Variant


def _setup_document_format(doc: Document, font_size: int = 12):
    """Hujjatni albom ko'rinishiga, 3 kalonkaga va belgilangan shriftga o'tkazadi."""
    style = doc.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(font_size)
    style.paragraph_format.space_after = Pt(0)  # Paragraflar orasidagi standart bo'shliqni olib tashlash
    style.paragraph_format.line_spacing = 1.0   # Qatorlar orasini (line spacing) 1.0 qilib zichlash
    
    for section in doc.sections:
        # Hujjatni Albom (Landscape) ko'rinishiga o'tkazish
        new_width, new_height = section.page_height, section.page_width
        section.orientation = WD_ORIENT.LANDSCAPE
        section.page_width = new_width
        section.page_height = new_height
        
        # Hoshiyalarni (margin) qisqartirish
        section.top_margin = Inches(0.5)
        section.bottom_margin = Inches(0.5)
        section.left_margin = Inches(0.5)
        section.right_margin = Inches(0.5)
        
        # 3 ta ustunga (kalonka) ajratish
        sectPr = section._sectPr
        cols = sectPr.xpath('./w:cols')
        if not cols:
            cols = OxmlElement('w:cols')
            sectPr.append(cols)
        else:
            cols = cols[0]
            
        cols.set(qn('w:num'), '3')
        cols.set(qn('w:space'), '720')


def _add_answer_table(doc: Document, num_questions: int):
    """Variant oxirida javoblarni belgilash uchun jadval qo'shadi."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run("Javoblar:")
    run.bold = True
    run.font.name = 'Times New Roman'
    
    chunk_size = 10  # Kalonkaga (ustunga) chiroyli sig'ishi uchun 10 tadan bo'lamiz
    for i in range(0, num_questions, chunk_size):
        chunk = min(chunk_size, num_questions - i)
        table = doc.add_table(rows=2, cols=chunk)
        table.style = 'Table Grid'
        
        for j in range(chunk):
            q_num = i + j + 1
            cell_top = table.cell(0, j)
            cell_top.text = str(q_num)
            cell_top.paragraphs[0].runs[0].font.name = 'Times New Roman'
            cell_top.paragraphs[0].runs[0].font.size = Pt(10)
            cell_top.paragraphs[0].runs[0].bold = True
            cell_top.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            cell_bottom = table.cell(1, j)
            cell_bottom.text = " "
            cell_bottom.paragraphs[0].runs[0].font.size = Pt(10)
            cell_bottom.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        p_space = doc.add_paragraph()
        p_space.paragraph_format.space_after = Pt(6)

def export_variants_to_docx(variants: list[Variant], output_dir: str | Path, font_size: int = 12) -> list[Path]:
    """Variantlarni alohida Word fayllariga yozadi.

    Args:
        variants: Generatsiya qilingan test variantlari ro'yxati.
        output_dir: Fayllar saqlanadigan papka manzili.
        font_size: Word hujjatining shrift o'lchami (standart 12).

    Returns:
        Yaratilgan fayllarning to'liq manzillari ro'yxati.
    """
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    
    saved_files: list[Path] = []

    for variant in variants:
        doc = Document()
        
        # Formatni qo'llash (Albom, 3 ta kalonka, belgilangan shrift)
        _setup_document_format(doc, font_size)
        
        # Sarlavha
        heading = doc.add_heading(f"{variant.number}-variant", level=1)
        heading.style.font.name = 'Times New Roman'
        heading.paragraph_format.space_before = Pt(0)
        heading.paragraph_format.space_after = Pt(0)
        
        # Talaba ma'lumotlari uchun joy
        doc.add_paragraph("Talaba: ___________________________")
        p_info = doc.add_paragraph("Guruh: ______________")
        p_info.paragraph_format.space_after = Pt(12)  # To'liq bo'sh qator o'rniga biroz joy qoldirish
        
        # Har bir savolni yozish
        for q in variant.questions:
            # Savol matni (q.number bilan)
            p_q = doc.add_paragraph(f"{q.number}. {q.text}")
            p_q.paragraph_format.space_after = Pt(2)  # Savol va uning variantlari orasini yanada yaqinlashtirish
            
            # Variantlarni yozish
            for i, opt in enumerate(q.options):
                p_opt = doc.add_paragraph(f"{opt.letter}) {opt.text}")
                
                # Agar bu oxirgi variant (D) bo'lsa, keyingi savoldan ajralib turishi uchun ozroq bo'shliq tashlaymiz
                if i == len(q.options) - 1:
                    p_opt.paragraph_format.space_after = Pt(8)
                else:
                    p_opt.paragraph_format.space_after = Pt(0)
            
        # Jadval qo'shish
        _add_answer_table(doc, len(variant.questions))
        
        file_name = f"{variant.number}-variant.docx"
        file_path = out_path / file_name
        doc.save(str(file_path))
        saved_files.append(file_path)

    return saved_files


def export_all_variants_to_single_docx(variants: list[Variant], output_dir: str | Path, font_size: int = 12) -> Path:
    """Barcha variantlarni bitta Word fayliga yozadi (har biri yangi varaqdan boshlanadi).

    Args:
        variants: Generatsiya qilingan test variantlari ro'yxati.
        output_dir: Fayl saqlanadigan papka manzili.
        font_size: Word hujjatining shrift o'lchami (standart 12).

    Returns:
        Yaratilgan faylning to'liq manzili.
    """
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    
    doc = Document()
    
    # Formatni qo'llash (Albom, 3 ta kalonka, belgilangan shrift)
    _setup_document_format(doc, font_size)

    for idx, variant in enumerate(variants):
        heading = doc.add_heading(f"{variant.number}-variant", level=1)
        heading.style.font.name = 'Times New Roman'
        heading.paragraph_format.space_before = Pt(0)
        heading.paragraph_format.space_after = Pt(0)
        
        doc.add_paragraph("Talaba: ___________________________")
        p_info = doc.add_paragraph("Guruh: ______________")
        p_info.paragraph_format.space_after = Pt(12)
        
        for q in variant.questions:
            p_q = doc.add_paragraph(f"{q.number}. {q.text}")
            p_q.paragraph_format.space_after = Pt(2)
            for i, opt in enumerate(q.options):
                p_opt = doc.add_paragraph(f"{opt.letter}) {opt.text}")
                p_opt.paragraph_format.space_after = Pt(8) if i == len(q.options) - 1 else Pt(0)
                
        # Jadval qo'shish
        _add_answer_table(doc, len(variant.questions))
        
        if idx < len(variants) - 1:
            doc.add_page_break()  # Keyingi variantni yangi sahifadan boshlash
            
    file_path = out_path / "Barcha_variantlar.docx"
    doc.save(str(file_path))
    return file_path


def export_answers_to_docx(variants: list[Variant], output_path: str | Path) -> Path:
    """Barcha variantlarning javoblarini bitta Word fayliga yozadi.

    Args:
        variants: Generatsiya qilingan test variantlari ro'yxati.
        output_path: Saqlanadigan Word faylining to'liq manzili.

    Returns:
        Yaratilgan faylning manzili.
    """
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    doc = Document()
    title = doc.add_heading("Javoblar kaliti", level=1)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    for variant in variants:
        h2 = doc.add_heading(f"{variant.number}-variant", level=2)
        h2.paragraph_format.space_before = Pt(16)
        h2.paragraph_format.space_after = Pt(8)
        
        chunk_size = 10
        ans_len = len(variant.answer_key)
        
        for i in range(0, ans_len, chunk_size):
            chunk = min(chunk_size, ans_len - i)
            table = doc.add_table(rows=2, cols=chunk)
            table.style = 'Table Grid'
            
            for j in range(chunk):
                q_num = i + j + 1
                ans = variant.answer_key[i + j]
                
                cell_top = table.cell(0, j)
                cell_top.text = str(q_num)
                cell_top.paragraphs[0].runs[0].bold = True
                cell_top.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
                
                cell_bottom = table.cell(1, j)
                cell_bottom.text = ans
                cell_bottom.paragraphs[0].runs[0].bold = True
                cell_bottom.paragraphs[0].runs[0].font.color.rgb = RGBColor(0, 112, 192) # Ko'k rangda
                cell_bottom.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            doc.add_paragraph().paragraph_format.space_after = Pt(4)

    doc.save(str(out_path))
    return out_path
