"""CLI va Config uchun unit testlar (9-bosqich)."""

import yaml
from click.testing import CliRunner

from src.cli import main
from src.config import Config


def test_config_load_default(tmp_path):
    """Fayl yo'q bo'lsa, standart sozlamalar o'qilishi kerak."""
    cfg = Config.load(tmp_path / "not_exist.yaml")
    
    assert cfg.variants_count == 5
    assert cfg.base_seed == 42
    assert cfg.output_dir == "output"
    assert cfg.questions_per_variant is None


def test_config_load_from_file(tmp_path):
    """YAML fayldan ma'lumotlar to'g'ri o'qilishi kerak."""
    cfg_file = tmp_path / "config.yaml"
    with open(cfg_file, "w") as f:
        yaml.dump({
            "variants_count": 10,
            "questions_per_variant": 15,
            "base_seed": 99,
            "output_dir": "custom_out"
        }, f)
        
    cfg = Config.load(cfg_file)
    assert cfg.variants_count == 10
    assert cfg.questions_per_variant == 15
    assert cfg.base_seed == 99
    assert cfg.output_dir == "custom_out"


def test_cli_no_files_error():
    """Fayl berilmasa, xato berishi kerak."""
    runner = CliRunner()
    result = runner.invoke(main, [])
    
    assert result.exit_code == 1
    assert "Hech qanday test fayli ko'rsatilmadi" in result.output


def test_cli_invalid_file():
    """Mavjud bo'lmagan fayl berilsa, click o'zi xato beradi."""
    runner = CliRunner()
    result = runner.invoke(main, ["not_found.docx"])
    
    assert result.exit_code == 2
    assert "does not exist" in result.output or "not_found.docx" in result.output


def test_cli_valid_run_end_to_end(tmp_path, monkeypatch):
    """To'liq muvaffaqiyatli ishga tushirish testi (Mock orqali)."""
    # Test uchun haqiqiy Word fayl yasash kerak emas, ichki funksiyalarni mock qilamiz
    from src.models import Question, Option, Variant
    
    q1 = Question(1, "Q1", [Option("A", "a", True), Option("B", "b"), Option("C", "c"), Option("D", "d")])
    v1 = Variant(1, 42, [q1])
    
    monkeypatch.setattr("src.cli.parse_docx", lambda *a, **kw: [q1])
    monkeypatch.setattr("src.cli.validate", lambda *a, **kw: [])
    monkeypatch.setattr("src.cli.generate_variants", lambda *a, **kw: [v1])
    monkeypatch.setattr("src.cli.export_variants_to_docx", lambda *a, **kw: [tmp_path / "1-variant.docx"])
    monkeypatch.setattr("src.cli.export_answers_to_docx", lambda *a, **kw: tmp_path / "Javoblar.docx")
    monkeypatch.setattr("src.cli.export_answers_to_xlsx", lambda *a, **kw: tmp_path / "Javoblar.xlsx")
    
    # Fayl mavjudligini mock qila olmaymiz (click.Path tekshiradi), shuning uchun
    # haqiqiy vaqtinchalik fayl yaratamiz
    dummy_file = tmp_path / "test.docx"
    dummy_file.touch()
    
    runner = CliRunner()
    result = runner.invoke(main, [str(dummy_file), "--count", "1", "--output-dir", str(tmp_path)])
    
    assert result.exit_code == 0
    assert "MUVAFFAQIYATLI YAKUNLANDI" in result.output
    assert "1-variant.docx" in result.output


def test_cli_validation_error_stops_execution(tmp_path, monkeypatch):
    """Xato topilganda dastur ishlashdan to'xtashi kerak."""
    from src.models import Question
    from src.validator import ValidationError, Severity
    
    monkeypatch.setattr("src.cli.parse_docx", lambda *a, **kw: [Question(1, "Q1")])
    monkeypatch.setattr("src.cli.validate", lambda *a, **kw: [
        ValidationError("test.docx", 1, "Katta xato", Severity.XATO)
    ])
    
    dummy_file = tmp_path / "test.docx"
    dummy_file.touch()
    
    runner = CliRunner()
    result = runner.invoke(main, [str(dummy_file)])
    
    assert result.exit_code == 1
    assert "[XATO] Fayllarda xatolar topildi" in result.output
