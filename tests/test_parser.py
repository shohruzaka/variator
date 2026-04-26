"""Parser uchun unit testlar (raqamli + bulletli format)."""

from dataclasses import dataclass
from pathlib import Path

import pytest

from src.parser import paragraphs_to_lines, parse_docx, parse_lines


@dataclass
class _FakePara:
    """Test fixture — `paragraphs_to_lines` uchun minimal Paragraph imitatsiyasi."""

    text: str
    numbered: bool = False


def _fake_has_num(p: _FakePara) -> bool:
    return p.numbered


def test_oddiy_savol_4_variant():
    """Eng oddiy holat: bitta savol, 4 ta variant, to'g'ri javob C."""
    lines = [
        "1. 2 + 2 nechiga teng?",
        "A) 3",
        "B) 5",
        "*C) 4",
        "D) 6",
    ]
    questions = parse_lines(lines, source_file="test.docx")

    assert len(questions) == 1
    q = questions[0]
    assert q.number == 1
    assert q.text == "2 + 2 nechiga teng?"
    assert q.source_file == "test.docx"
    assert [o.letter for o in q.options] == ["A", "B", "C", "D"]
    assert q.correct_letter == "C"
    assert q.options[2].text == "4"


@pytest.mark.parametrize(
    "correct_letter,correct_line",
    [
        ("A", "*A) bir"),
        ("B", "*B) ikki"),
        ("C", "*C) uch"),
        ("D", "*D) to'rt"),
    ],
)
def test_to_g_ri_javob_har_xil_pozitsiyada(correct_letter, correct_line):
    """Yulduzcha har qaysi pozitsiyada (A/B/C/D) bo'lishi mumkin."""
    base = ["1. Savol?", "A) 1", "B) 2", "C) 3", "D) 4"]
    idx = "ABCD".index(correct_letter) + 1
    base[idx] = correct_line

    questions = parse_lines(base)

    assert questions[0].correct_letter == correct_letter


def test_bir_nechta_savol_ketma_ket():
    """Bir nechta savol ketma-ket o'qilsin."""
    lines = [
        "1. Birinchi?",
        "A) 1A", "B) 1B", "*C) 1C", "D) 1D",
        "",
        "2. Ikkinchi?",
        "*A) 2A", "B) 2B", "C) 2C", "D) 2D",
        "",
        "3. Uchinchi?",
        "A) 3A", "*B) 3B", "C) 3C", "D) 3D",
    ]
    questions = parse_lines(lines)

    assert [q.number for q in questions] == [1, 2, 3]
    assert [q.correct_letter for q in questions] == ["C", "A", "B"]


def test_savollar_orasida_bosh_qator_majburiy_emas():
    """Savollar orasida bo'sh qator bo'lmasligi ham qabul qilinadi."""
    lines = [
        "1. Bir?",
        "A) a", "B) b", "C) c", "*D) d",
        "2. Ikki?",
        "*A) a", "B) b", "C) c", "D) d",
    ]
    questions = parse_lines(lines)

    assert len(questions) == 2
    assert questions[0].correct_letter == "D"
    assert questions[1].correct_letter == "A"


def test_kop_qatorli_savol_kod_bloki_bilan():
    """Savol matni keyingi qatorlarda davom etishi mumkin (kod bloklari)."""
    lines = [
        "1. Quyidagi kod nima chiqaradi?",
        "for i in range(3):",
        "    print(i)",
        "A) 1 2 3",
        "B) 0 1 2 3",
        "*C) 0 1 2",
        "D) xato",
    ]
    questions = parse_lines(lines)
    q = questions[0]

    assert "Quyidagi kod nima chiqaradi?" in q.text
    assert "for i in range(3):" in q.text
    assert "    print(i)" in q.text
    assert q.correct_letter == "C"
    assert len(q.options) == 4


def test_kop_qatorli_variant():
    """Variant matni keyingi qatorlarda davom etishi mumkin."""
    lines = [
        "1. Savol?",
        "A) Birinchi qator",
        "ikkinchi qator A uchun",
        "B) B variant",
        "*C) C variant",
        "uchinchi qator C uchun",
        "D) D variant",
    ]
    questions = parse_lines(lines)
    q = questions[0]

    assert "Birinchi qator" in q.options[0].text
    assert "ikkinchi qator A uchun" in q.options[0].text
    assert "C variant" in q.options[2].text
    assert "uchinchi qator C uchun" in q.options[2].text


def test_kod_blok_ichida_raqam_yangi_savol_boshlamaydi():
    """Savol matni ichidagi 'N.' qatori yangi savol sifatida talqin qilinmasin.

    Faqat oxirgi (D) variantdan keyingi raqamli sarlavha yangi savol hisoblanadi.
    """
    lines = [
        "1. Quyidagi izohlardan qaysi biri to'g'ri?",
        "Misol uchun, x = 10 bo'lsa:",
        "2. x ning qiymati 10 ga teng",
        "3. x ning qiymati o'zgarmaydi",
        "A) faqat 2",
        "B) faqat 3",
        "*C) 2 va 3",
        "D) ikkalasi ham noto'g'ri",
    ]
    questions = parse_lines(lines)

    assert len(questions) == 1, "Kod ichidagi '2.', '3.' qatorlari yangi savol yaratmasligi kerak"
    assert "2. x ning qiymati 10 ga teng" in questions[0].text
    assert questions[0].correct_letter == "C"


def test_markdown_bold_tozalanadi():
    """Word'dan kelgan ** belgilarini parser tozalasin."""
    lines = [
        "**1. Bold savol?**",
        "**A)** bold variant",
        "B) oddiy",
        "*C) **bold** to'g'ri",
        "D) yana",
    ]
    questions = parse_lines(lines)
    q = questions[0]

    assert "**" not in q.text
    assert q.text == "1. Bold savol?".replace("1. ", "")  # = "Bold savol?"
    for opt in q.options:
        assert "**" not in opt.text
    assert q.correct_letter == "C"


def test_kichik_harfli_variantlar_qabul_qilinadi():
    """a) b) c) d) ham qabul qilinsin va katta harfga keltirilsin."""
    lines = [
        "1. Savol?",
        "a) bir",
        "b) ikki",
        "*c) uch",
        "d) to'rt",
    ]
    questions = parse_lines(lines)
    q = questions[0]

    assert [o.letter for o in q.options] == ["A", "B", "C", "D"]
    assert q.correct_letter == "C"


def test_bo_sh_kirish():
    """Bo'sh ro'yxat va faqat bo'sh qatorlardan iborat ro'yxat — bo'sh natija."""
    assert parse_lines([]) == []
    assert parse_lines(["", "  ", "\t"]) == []


def test_savoldan_oldingi_matn_otkazib_yuboriladi():
    """Birinchi savoldan oldingi izohlar e'tiborga olinmaydi."""
    lines = [
        "Test banki: Algoritmlar",
        "Mavzu: tartiblash",
        "",
        "1. Saralash algoritmlari qaysilar?",
        "A) bubble", "B) quick", "C) merge", "*D) hammasi",
    ]
    questions = parse_lines(lines)

    assert len(questions) == 1
    assert questions[0].text == "Saralash algoritmlari qaysilar?"


def test_source_file_savolga_yoziladi():
    """Manba fayl nomi har bir savolga yoziladi."""
    lines = ["1. q?", "A) a", "B) b", "*C) c", "D) d"]
    questions = parse_lines(lines, source_file="bank.docx")

    assert questions[0].source_file == "bank.docx"


def test_atrof_bo_shliqlari_tozalanadi():
    """Variant va savol matnlari atrof bo'shliqlardan tozalanadi."""
    lines = [
        "  1.   Savol?  ",
        "  A)   bir  ",
        "  B)   ikki  ",
        "  *C)   uch  ",
        "  D)   to'rt  ",
    ]
    questions = parse_lines(lines)
    q = questions[0]

    assert q.text == "Savol?"
    assert q.options[0].text == "bir"
    assert q.correct_letter == "C"


def test_yulduzcha_bilan_va_bosh_liq_oraliq_uchratilmaydi():
    """`*` belgisi va variant harfi orasida bo'shliq bo'lmasin."""
    # `* A)` format qo'llab-quvvatlanmaydi — to'g'ri javob aniqlanmaydi.
    lines = [
        "1. Savol?",
        "A) bir",
        "* B) ikki",   # noto'g'ri format — `*` dan keyin bo'shliq
        "C) uch",
        "D) to'rt",
    ]
    questions = parse_lines(lines)
    q = questions[0]
    # B variant `*` siz tanilsin (to'g'ri javob deb hisoblanmaydi).
    # Validatsiya bosqichida xato bo'ladi (to'g'ri javob yo'q).
    assert all(not o.is_correct for o in q.options)


def test_parse_docx_haqiqiy_fayldan(tmp_path: Path):
    """Word fayldan o'qish: uchidan-uchiga integratsiya testi."""
    pytest.importorskip("docx")
    from docx import Document

    doc_path = tmp_path / "namuna.docx"
    doc = Document()
    for line in [
        "1. Quyidagi kod natijasini toping?",
        "x = 5",
        "y = 3",
        "print(x + y)",
        "A) 53",
        "B) xato",
        "*C) 8",
        "D) 15",
        "",
        "2. Ikkinchi savol?",
        "*A) bir",
        "B) ikki",
        "C) uch",
        "D) to'rt",
    ]:
        doc.add_paragraph(line)
    doc.save(str(doc_path))

    questions = parse_docx(doc_path)

    assert len(questions) == 2
    assert questions[0].correct_letter == "C"
    assert "x = 5" in questions[0].text
    assert questions[1].correct_letter == "A"
    assert questions[0].source_file == "namuna.docx"


# ---------------------------------------------------------------------------
# paragraphs_to_lines — paragraf → logical lines konvertatsiyasi
# ---------------------------------------------------------------------------


def test_paragraphs_to_lines_soft_break_bo_yicha_bo_linadi():
    """Paragraf ichidagi `\\n` (soft break) alohida qatorlarga ajratiladi."""
    paras = [_FakePara("1. Q?\nA) a\nB) b\n*C) c\nD) d")]

    lines = paragraphs_to_lines(paras, has_numbering_fn=_fake_has_num)

    assert lines == ["1. Q?", "A) a", "B) b", "*C) c", "D) d"]


def test_paragraphs_to_lines_bir_paragrafda_ikki_savol():
    """Bitta paragrafda ikki savol joylashgan bo'lsa, ikkalasi ham parse qilinsin."""
    text = (
        "17. Birinchi?\nA) a\nB) b\n*C) c\nD) d\n"
        "18. Ikkinchi?\n*A) a\nB) b\nC) c\nD) d"
    )
    paras = [_FakePara(text)]

    lines = paragraphs_to_lines(paras, has_numbering_fn=_fake_has_num)
    questions = parse_lines(lines)

    assert [q.number for q in questions] == [17, 18]
    assert [q.correct_letter for q in questions] == ["C", "A"]


def test_paragraphs_to_lines_word_numbering_synthetic_prefiks_qoshadi():
    """Paragrafda numPr bor va matn 'N.' bilan boshlanmasa, synthetic prefiks qo'shilsin."""
    paras = [
        _FakePara("Birinchi savol?\nA) a\n*B) b\nC) c\nD) d", numbered=True),
        _FakePara("Ikkinchi savol?\n*A) a\nB) b\nC) c\nD) d", numbered=True),
    ]

    lines = paragraphs_to_lines(paras, has_numbering_fn=_fake_has_num)
    questions = parse_lines(lines)

    assert lines[0] == "1. Birinchi savol?"
    assert "2. Ikkinchi savol?" in lines
    assert [q.number for q in questions] == [1, 2]
    assert [q.correct_letter for q in questions] == ["B", "A"]


def test_paragraphs_to_lines_word_numbering_lekin_matn_explicit_raqamli():
    """numPr bor, ammo matn allaqachon 'N.' bilan boshlansa — synthetic qo'shilmaydi."""
    paras = [_FakePara("5. Beshinchi?\nA) a\nB) b\n*C) c\nD) d", numbered=True)]

    lines = paragraphs_to_lines(paras, has_numbering_fn=_fake_has_num)
    questions = parse_lines(lines)

    assert lines[0] == "5. Beshinchi?"
    assert questions[0].number == 5


def test_paragraphs_to_lines_continuation_paragraf_numbering_yoq():
    """Numbered savol paragrafidan keyin numbering siz paragraf — variant ro'yxati."""
    paras = [
        _FakePara("Quyidagi kod natijasini toping?\nx = 5\nprint(x)", numbered=True),
        _FakePara("A) 5\nB) 0\n*C) 5", numbered=False),
        _FakePara("D) xato", numbered=False),
    ]

    lines = paragraphs_to_lines(paras, has_numbering_fn=_fake_has_num)
    questions = parse_lines(lines)

    assert len(questions) == 1
    assert questions[0].correct_letter == "C"
    assert "x = 5" in questions[0].text
    assert "print(x)" in questions[0].text


def test_paragraphs_to_lines_bo_sh_paragraflar_otkazib_yuboriladi():
    """Bo'sh va whitespace-only paragraflar e'tiborga olinmaydi."""
    paras = [
        _FakePara(""),
        _FakePara("   "),
        _FakePara("1. Q?\nA) a\nB) b\n*C) c\nD) d"),
        _FakePara("\t\n"),
    ]

    lines = paragraphs_to_lines(paras, has_numbering_fn=_fake_has_num)

    assert lines == ["1. Q?", "A) a", "B) b", "*C) c", "D) d"]


def test_paragraphs_to_lines_synthetic_counter_sequential_start():
    """`sequential_start` argumenti synthetic counter boshlang'ich qiymatini belgilaydi."""
    paras = [
        _FakePara("Birinchi?\nA) a\n*B) b\nC) c\nD) d", numbered=True),
        _FakePara("Ikkinchi?\n*A) a\nB) b\nC) c\nD) d", numbered=True),
    ]

    lines = paragraphs_to_lines(
        paras, sequential_start=10, has_numbering_fn=_fake_has_num
    )
    questions = parse_lines(lines)

    assert [q.number for q in questions] == [10, 11]


# ---------------------------------------------------------------------------
# Real fayllar ustida smoke testlar (test_banks/ ga bog'liq)
# ---------------------------------------------------------------------------


def test_smoke_python_lugat_raqamli_format():
    """Real raqamli fayl: kamida 28 ta savol topilsin va Q1 to'g'ri parse qilinsin."""
    path = Path("test_banks/python_lugat.docx")
    if not path.exists():
        pytest.skip("test_banks/python_lugat.docx mavjud emas")

    questions = parse_docx(path)

    assert len(questions) >= 28, f"Topilgan: {len(questions)}"

    q1 = next((q for q in questions if q.number == 1), None)
    assert q1 is not None, "Q1 topilmadi"
    assert len(q1.options) == 4
    assert q1.correct_letter == "C"

    well_formed = sum(
        1
        for q in questions
        if len(q.options) == 4 and any(o.is_correct for o in q.options)
    )
    assert well_formed >= 25, f"To'g'ri shakllangan savollar: {well_formed}"


def test_smoke_modul_va_paketlar_bulletli_format():
    """Real bulletli fayl (Word avto-numerlash): kamida 28 ta savol va Q1 to'g'ri."""
    path = Path("test_banks/modul_va_paketlar.docx")
    if not path.exists():
        pytest.skip("test_banks/modul_va_paketlar.docx mavjud emas")

    questions = parse_docx(path)

    assert len(questions) >= 28, f"Topilgan: {len(questions)}"

    q1 = next((q for q in questions if q.number == 1), None)
    assert q1 is not None, "Q1 topilmadi"
    assert len(q1.options) == 4
    assert q1.correct_letter == "C"

    well_formed = sum(
        1
        for q in questions
        if len(q.options) == 4 and any(o.is_correct for o in q.options)
    )
    assert well_formed >= 25, f"To'g'ri shakllangan savollar: {well_formed}"
