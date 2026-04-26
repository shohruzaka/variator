"""Exporter (Word) uchun unit testlar (7-bosqich)."""

import os
from pathlib import Path

import pytest
from docx import Document

from src.exporter_docx import export_variants_to_docx
from src.models import Option, Question, Variant


def _make_sample_variants() -> list[Variant]:
    """Test uchun 2 ta variant yaratadi."""
    q1 = Question(1, "Savol 1", [Option("A", "a1"), Option("B", "b1"), Option("C", "c1", is_correct=True), Option("D", "d1")])
    q2 = Question(2, "Savol 2", [Option("A", "a2"), Option("B", "b2"), Option("C", "c2"), Option("D", "d2", is_correct=True)])
    
    v1 = Variant(number=1, seed=101, questions=[q1, q2])
    
    q3 = Question(1, "Savol 2", [Option("A", "a2"), Option("B", "b2", is_correct=True), Option("C", "c2"), Option("D", "d2")])
    q4 = Question(2, "Savol 1", [Option("A", "a1", is_correct=True), Option("B", "b1"), Option("C", "c1"), Option("D", "d1")])
    
    v2 = Variant(number=2, seed=102, questions=[q3, q4])
    
    return [v1, v2]


def test_export_variants_creates_files(tmp_path: Path):
    """Eksport funksiyasi kutilgan fayllarni ko'rsatilgan papkada yaratishi kerak."""
    variants = _make_sample_variants()
    
    # tmp_path - pytest tomonidan berilgan vaqtinchalik papka
    output_dir = tmp_path / "output"
    
    saved_files = export_variants_to_docx(variants, output_dir)
    
    assert len(saved_files) == 2
    assert output_dir.exists()
    
    file_names = [f.name for f in saved_files]
    assert "Variant_1.docx" in file_names
    assert "Variant_2.docx" in file_names
    
    for f in saved_files:
        assert f.exists()


def test_export_variants_content(tmp_path: Path):
    """Yaratilgan fayllar to'g'ri tarkibga (sarlavha, savollar) ega ekanligini tekshirish."""
    variants = _make_sample_variants()
    output_dir = tmp_path / "output"
    
    saved_files = export_variants_to_docx(variants, output_dir)
    
    # 1-variant faylini ochib tekshiramiz
    doc1_path = next(f for f in saved_files if f.name == "Variant_1.docx")
    doc1 = Document(str(doc1_path))
    
    paragraphs = [p.text for p in doc1.paragraphs if p.text.strip()]

    # Kutilgan tarkib (talaba/guruh qatorlari ham bor, lekin tartib emas,
    # mazmun muhim — moslashuvchan tekshiramiz):
    assert any("1-Variant" in p for p in paragraphs)
    assert any("1. Savol 1" in p for p in paragraphs)
    assert any("A) a1" in p for p in paragraphs)
    assert any("D) d1" in p for p in paragraphs)
    assert any("2. Savol 2" in p for p in paragraphs)


def test_export_empty_variants_list(tmp_path: Path):
    """Bo'sh ro'yxat berilganda xatosiz ishlashi va papka yaratishi kerak."""
    output_dir = tmp_path / "output"
    saved_files = export_variants_to_docx([], output_dir)
    
    assert len(saved_files) == 0
    assert output_dir.exists() # Papka bo'sh bo'lsa ham yaratiladi


def test_export_answers_to_docx(tmp_path: Path):
    """Javoblar kaliti Word faylga to'g'ri yozilishini tekshirish."""
    from src.exporter_docx import export_answers_to_docx
    
    variants = _make_sample_variants()
    out_file = tmp_path / "javoblar.docx"
    
    result_path = export_answers_to_docx(variants, out_file)
    
    assert result_path.exists()
    
    doc = Document(str(result_path))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    
    # Kutilgan format:
    # Javoblar kaliti
    # 1-Variant
    # 1-C, 2-D
    # 2-Variant
    # 1-B, 2-A
    
    assert "Javoblar kaliti" in paragraphs[0]
    assert "1-Variant" in paragraphs[1]
    assert "1-C, 2-D" in paragraphs[2]
    assert "2-Variant" in paragraphs[3]
    assert "1-B, 2-A" in paragraphs[4]
