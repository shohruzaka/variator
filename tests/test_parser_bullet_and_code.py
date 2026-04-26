"""3-bosqich testlari: bulletli format va kod bloklari.

Bu modul quyidagi xususiyatlarni qamrab oladi:
- Word avto-numerlash (numbered list / bullet list) orqali savol boshlanishi
- Ko'p qatorli savol matni (kod bloklari bilan)
- Ko'p qatorli variant matni (uzun javoblar)
- Aralash formatlar (raqamli + numbered list)
- Fixture .docx fayllar orqali integratsiya testlari
"""

from dataclasses import dataclass
from pathlib import Path

import pytest

from src.parser import paragraphs_to_lines, parse_docx, parse_lines


# ---------------------------------------------------------------------------
# Yordamchi: Fake paragraph
# ---------------------------------------------------------------------------

@dataclass
class _FakePara:
    """Test fixture — `paragraphs_to_lines` uchun minimal Paragraph imitatsiyasi."""

    text: str
    numbered: bool = False


def _fake_has_num(p: _FakePara) -> bool:
    return p.numbered


# ---------------------------------------------------------------------------
# Ko'p qatorli savol (kod bloki) — kengaytirilgan testlar
# ---------------------------------------------------------------------------


class TestKodBloklari:
    """Kod bloklari va ko'p qatorli savollar uchun testlar."""

    def test_bir_nechta_qatorli_kod_bloki(self):
        """Savol matni bir nechta kod qatorlarini o'z ichiga oladi."""
        lines = [
            "1. Quyidagi kodning natijasini toping:",
            "x = [1, 2, 3]",
            "y = x.copy()",
            "y.append(4)",
            "print(len(x))",
            "A) 4",
            "B) 3 4",
            "*C) 3",
            "D) xato",
        ]
        questions = parse_lines(lines)
        q = questions[0]

        assert "x = [1, 2, 3]" in q.text
        assert "y = x.copy()" in q.text
        assert "y.append(4)" in q.text
        assert "print(len(x))" in q.text
        assert q.correct_letter == "C"

    def test_kod_blokida_indent_saqlanadi(self):
        """Kod blokidagi indentatsiya (bo'shliqlar) saqlanishi kerak."""
        lines = [
            "1. Quyidagi natijani toping:",
            "def foo():",
            "    x = 10",
            "    return x * 2",
            "A) 10",
            "B) 2",
            "*C) 20",
            "D) xato",
        ]
        questions = parse_lines(lines)
        q = questions[0]

        assert "    x = 10" in q.text
        assert "    return x * 2" in q.text

    def test_kod_blokida_raqamli_qator_yangi_savol_emas(self):
        """Kod ichidagi `2.` yoki `3.` raqamli izohlar yangi savol boshlamaydi."""
        lines = [
            "1. Quyidagi algoritmning bosqichlarini ko'ring:",
            "1. Kiritish",
            "2. Hisoblash",
            "3. Chiqarish",
            "A) 3 bosqich",
            "*B) Chiziqli algoritm",
            "C) Siklik algoritm",
            "D) Tarmoqlanma",
        ]
        questions = parse_lines(lines)

        assert len(questions) == 1
        assert "1. Kiritish" in questions[0].text
        assert "2. Hisoblash" in questions[0].text
        assert "3. Chiqarish" in questions[0].text

    def test_ikki_savol_orasida_kod_bloki(self):
        """Birinchi savolda kod bloki bo'lsa, ikkinchi savol to'g'ri ajralsin."""
        lines = [
            "1. Nima chiqadi?",
            "for i in range(3):",
            "    print(i, end=' ')",
            "A) 1 2 3",
            "*B) 0 1 2",
            "C) 0 1 2 3",
            "D) xato",
            "",
            "2. len('hello') = ?",
            "A) 4",
            "*B) 5",
            "C) 6",
            "D) xato",
        ]
        questions = parse_lines(lines)

        assert len(questions) == 2
        assert questions[0].correct_letter == "B"
        assert questions[1].correct_letter == "B"
        assert questions[1].text == "len('hello') = ?"


# ---------------------------------------------------------------------------
# Ko'p qatorli variantlar
# ---------------------------------------------------------------------------


class TestKopQatorliVariantlar:
    """Ko'p qatorli variant matni testlari."""

    def test_har_bir_variant_kop_qatorli(self):
        """Barcha to'rt variant ham ko'p qatorli bo'lishi mumkin."""
        lines = [
            "1. Qaysi ibora to'g'ri?",
            "A) Python —",
            "statik til",
            "B) Python —",
            "kompilyatsiya qilinadigan til",
            "*C) Python —",
            "dinamik til",
            "D) Python —",
            "assembler tili",
        ]
        questions = parse_lines(lines)
        q = questions[0]

        assert len(q.options) == 4
        assert "Python —\nstatik til" == q.options[0].text
        assert "Python —\ndinamik til" == q.options[2].text
        assert q.correct_letter == "C"

    def test_variant_matni_bosh_qatorsiz(self):
        """Variantning davomi bo'sh qatorsiz bo'lishi kerak."""
        lines = [
            "1. Test?",
            "A) birinchi",
            "qator",
            "B) ikkinchi",
            "*C) uchinchi",
            "D) to'rtinchi",
        ]
        questions = parse_lines(lines)
        q = questions[0]

        assert q.options[0].text == "birinchi\nqator"
        assert q.options[1].text == "ikkinchi"


# ---------------------------------------------------------------------------
# Bulletli format (Word avto-numerlash) — kengaytirilgan
# ---------------------------------------------------------------------------


class TestBulletliFormat:
    """Word avto-numerlash orqali yozilgan savollar uchun testlar."""

    def test_oddiy_numbered_list(self):
        """Numbered list paragraflar synthetic raqam olishi kerak."""
        paras = [
            _FakePara(
                "Python nima?\nA) Til\n*B) Dasturlash tili\nC) OT\nD) Brauzer",
                numbered=True,
            ),
            _FakePara(
                "Java nima?\n*A) Dasturlash tili\nB) Brauzer\nC) OT\nD) Matn muharriri",
                numbered=True,
            ),
        ]
        lines = paragraphs_to_lines(paras, has_numbering_fn=_fake_has_num)
        questions = parse_lines(lines)

        assert len(questions) == 2
        assert questions[0].number == 1
        assert questions[1].number == 2
        assert questions[0].correct_letter == "B"
        assert questions[1].correct_letter == "A"

    def test_numbered_list_savol_va_variant_alohida_paragrafda(self):
        """Ba'zi fayllarda savol matni va variantlar alohida paragraflarda.

        Bu real modul_va_paketlar.docx faylidagi P6/P7 kabi holatdir.
        """
        paras = [
            _FakePara(
                "Quyidagi kod qanday ishlaydi? from math import sqrt",
                numbered=True,
            ),
            _FakePara(
                "A) math modulini o'chiradi\n*B) sqrt ni import qiladi\nC) Faqat pi\nD) Paket yaratadi",
                numbered=False,
            ),
        ]
        lines = paragraphs_to_lines(paras, has_numbering_fn=_fake_has_num)
        questions = parse_lines(lines)

        assert len(questions) == 1
        assert questions[0].correct_letter == "B"
        assert "sqrt" in questions[0].text or "sqrt" in str(questions[0].options)

    def test_numbered_list_bilan_kod_bloki(self):
        """Numbered list savol matni ichida kod bloki."""
        paras = [
            _FakePara(
                "Quyidagi kod natijasini toping?\nx = 5\nprint(x * 2)",
                numbered=True,
            ),
            _FakePara(
                "A) 5\nB) 2\n*C) 10\nD) xato",
                numbered=False,
            ),
        ]
        lines = paragraphs_to_lines(paras, has_numbering_fn=_fake_has_num)
        questions = parse_lines(lines)

        assert len(questions) == 1
        assert "x = 5" in questions[0].text
        assert "print(x * 2)" in questions[0].text
        assert questions[0].correct_letter == "C"

    def test_uch_paragrafli_savol(self):
        """Savol uch paragrafdan iborat: savol + kod + variantlar."""
        paras = [
            _FakePara("Natijani toping?", numbered=True),
            _FakePara("x = [1, 2, 3]", numbered=False),
            _FakePara("A) 1\nB) 2\n*C) 3\nD) xato", numbered=False),
        ]
        lines = paragraphs_to_lines(paras, has_numbering_fn=_fake_has_num)
        questions = parse_lines(lines)

        assert len(questions) == 1
        assert "x = [1, 2, 3]" in questions[0].text

    def test_sequential_start_10_dan_boshlash(self):
        """sequential_start parametri custom raqamdan boshlash imkonini beradi."""
        paras = [
            _FakePara("Birinchi?\nA) a\n*B) b\nC) c\nD) d", numbered=True),
            _FakePara("Ikkinchi?\nA) a\nB) b\nC) c\n*D) d", numbered=True),
        ]
        lines = paragraphs_to_lines(
            paras, sequential_start=10, has_numbering_fn=_fake_has_num,
        )
        questions = parse_lines(lines)

        assert questions[0].number == 10
        assert questions[1].number == 11

    def test_explicit_raqamli_paragraf_ham_numbered(self):
        """Numbered list paragraf matnida '5.' bor — synthetic qo'shilmasin."""
        paras = [
            _FakePara(
                "5. Beshinchi savol?\nA) a\n*B) b\nC) c\nD) d",
                numbered=True,
            ),
        ]
        lines = paragraphs_to_lines(paras, has_numbering_fn=_fake_has_num)
        questions = parse_lines(lines)

        assert questions[0].number == 5


# ---------------------------------------------------------------------------
# Aralash format testlari
# ---------------------------------------------------------------------------


class TestAralashFormat:
    """Raqamli va numbered list aralash bo'lgan holatlar."""

    def test_raqamli_va_numbered_aralash(self):
        """Birinchi savol raqamli, keyingilari numbered list."""
        paras = [
            _FakePara("1. Birinchi?\nA) a\n*B) b\nC) c\nD) d", numbered=False),
            _FakePara("Ikkinchi?\n*A) a\nB) b\nC) c\nD) d", numbered=True),
        ]
        lines = paragraphs_to_lines(paras, has_numbering_fn=_fake_has_num)
        questions = parse_lines(lines)

        assert len(questions) == 2
        assert questions[0].number == 1
        assert questions[0].correct_letter == "B"
        assert questions[1].correct_letter == "A"

    def test_savoldan_oldingi_sarlavha_paragraflar(self):
        """Savoldan oldingi matnli paragraflar (sarlavha, izoh) e'tiborga olinmasin."""
        paras = [
            _FakePara("Mavzu: Python", numbered=False),
            _FakePara("Qiyinlik darajasi: oson", numbered=False),
            _FakePara("Birinchi?\nA) a\nB) b\n*C) c\nD) d", numbered=True),
        ]
        lines = paragraphs_to_lines(paras, has_numbering_fn=_fake_has_num)
        questions = parse_lines(lines)

        assert len(questions) == 1
        assert questions[0].number == 1


# ---------------------------------------------------------------------------
# Fixture .docx fayllar bilan integratsiya testlari
# ---------------------------------------------------------------------------

FIXTURES = Path("tests/fixtures")


class TestFixtureDocxFayllar:
    """Fixture .docx fayllar orqali uchidan-uchiga integratsiya testlari."""

    def test_fixture_bullet_format(self):
        """bullet_format.docx: 3 ta savol, Word numbered list orqali."""
        path = FIXTURES / "bullet_format.docx"
        if not path.exists():
            pytest.skip("Fixture fayl mavjud emas")

        questions = parse_docx(path)

        assert len(questions) == 3
        assert questions[0].correct_letter == "C"
        assert questions[1].correct_letter == "A"
        assert questions[2].correct_letter == "C"
        for q in questions:
            assert len(q.options) == 4
            assert q.source_file == "bullet_format.docx"

    def test_fixture_code_blocks(self):
        """code_blocks.docx: 3 ta savol, kod bloklari va ko'p qatorli variantlar."""
        path = FIXTURES / "code_blocks.docx"
        if not path.exists():
            pytest.skip("Fixture fayl mavjud emas")

        questions = parse_docx(path)

        assert len(questions) == 3

        # Savol 1: Kod bloki
        q1 = questions[0]
        assert "x = [1, 2, 3]" in q1.text
        assert "print(len(x))" in q1.text
        assert q1.correct_letter == "C"

        # Savol 2: Ko'p qatorli variantlar
        q2 = questions[1]
        assert q2.correct_letter == "B"
        assert len(q2.options) == 4
        # Har bir variant ikki qatordan iborat
        for opt in q2.options:
            assert "\n" in opt.text, f"{opt.letter}) varianti ko'p qatorli bo'lishi kerak"

        # Savol 3: Oddiy
        q3 = questions[2]
        assert q3.correct_letter == "C"

    def test_fixture_simple_numbered(self):
        """simple_numbered.docx: 2 ta oddiy raqamli savol."""
        path = FIXTURES / "simple_numbered.docx"
        if not path.exists():
            pytest.skip("Fixture fayl mavjud emas")

        questions = parse_docx(path)

        assert len(questions) == 2
        assert questions[0].number == 1
        assert questions[1].number == 2
        assert questions[0].correct_letter == "B"
        assert questions[1].correct_letter == "D"

    def test_fixture_mixed_format(self):
        """mixed_format.docx: raqamli va numbered list aralash."""
        path = FIXTURES / "mixed_format.docx"
        if not path.exists():
            pytest.skip("Fixture fayl mavjud emas")

        questions = parse_docx(path)

        assert len(questions) == 3
        # Birinchi — raqamli
        assert questions[0].correct_letter == "B"
        # Ikkinchi — numbered list
        assert questions[1].correct_letter == "C"
        # Uchinchi — raqamli
        assert questions[2].correct_letter == "A"

        # Barcha savollar 4 ta variantli
        for q in questions:
            assert len(q.options) == 4


# ---------------------------------------------------------------------------
# Edge case'lar
# ---------------------------------------------------------------------------


class TestEdgeCases:
    """Noodatiy va chegaraviy holatlar."""

    def test_bosh_paragraflar_arasinida_savol(self):
        """Bo'sh paragraflar orasidagi savol to'g'ri topilsin."""
        paras = [
            _FakePara(""),
            _FakePara("   "),
            _FakePara("Savol?\nA) a\nB) b\n*C) c\nD) d", numbered=True),
            _FakePara(""),
            _FakePara("  \t  "),
        ]
        lines = paragraphs_to_lines(paras, has_numbering_fn=_fake_has_num)
        questions = parse_lines(lines)

        assert len(questions) == 1
        assert questions[0].correct_letter == "C"

    def test_soft_break_bilan_bitta_paragrafda_ikki_savol(self):
        """Bitta paragraf ichida \\n orqali ikki savol."""
        paras = [
            _FakePara(
                "1. Birinchi?\nA) a\nB) b\n*C) c\nD) d\n"
                "2. Ikkinchi?\n*A) a\nB) b\nC) c\nD) d"
            ),
        ]
        lines = paragraphs_to_lines(paras, has_numbering_fn=_fake_has_num)
        questions = parse_lines(lines)

        assert len(questions) == 2
        assert questions[0].correct_letter == "C"
        assert questions[1].correct_letter == "A"

    def test_faqat_bosh_qatorlar(self):
        """Bo'sh paragraflar — savol topilmasin."""
        paras = [
            _FakePara(""),
            _FakePara("   "),
            _FakePara("\t\n\n"),
        ]
        lines = paragraphs_to_lines(paras, has_numbering_fn=_fake_has_num)
        questions = parse_lines(lines)

        assert questions == []

    def test_uzun_savol_matni_kod_bilan(self):
        """Uzun savol matni ko'p qatorli bo'lib, to'g'ri o'qilsin."""
        lines = [
            "1. Quyidagi Python dasturida nima sodir bo'ladi?",
            "Dastur foydalanuvchidan ism so'raydi",
            "va salom beradi:",
            "name = input('Ismingiz: ')",
            "print(f'Salom, {name}!')",
            "",
            "Natijani toping:",
            "A) Xato beradi",
            "B) Hech narsa chiqarmaydi",
            "*C) Ism so'rab, salom beradi",
            "D) Cheksiz sikl",
        ]
        questions = parse_lines(lines)
        q = questions[0]

        assert "Quyidagi Python dasturida nima sodir bo'ladi?" in q.text
        assert "name = input" in q.text
        assert q.correct_letter == "C"
        assert len(q.options) == 4
