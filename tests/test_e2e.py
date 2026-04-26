"""End-to-end integratsiya testlari (10-bosqich)."""

import os
from pathlib import Path

from click.testing import CliRunner

from src.cli import main


def test_e2e_full_workflow(tmp_path: Path):
    """Real fayllar bilan to'liq dastur ishlashini tekshirish."""
    # Test fayllari mavjudligini tekshiramiz
    docx_file = Path("test_banks/modul_va_paketlar.docx")
    if not docx_file.exists():
        import pytest
        pytest.skip(f"Test fayli topilmadi: {docx_file}")

    runner = CliRunner()
    
    # 2 ta variant va 5 tadan savol generatsiya qilamiz
    result = runner.invoke(main, [
        str(docx_file),
        "--count", "2",
        "--questions-per-variant", "5",
        "--output-dir", str(tmp_path)
    ])
    
    assert result.exit_code == 0
    assert "MUVAFFAQIYATLI YAKUNLANDI" in result.output
    
    # Fayllar yaratilganligini tekshiramiz
    assert (tmp_path / "Variant_1.docx").exists()
    assert (tmp_path / "Variant_2.docx").exists()
    assert (tmp_path / "Javoblar.docx").exists()
    assert (tmp_path / "Javoblar.xlsx").exists()
