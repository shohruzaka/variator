"""Validator uchun unit testlar (4-bosqich).

Har bir validatsiya qoidasi uchun alohida test — xato aniqlanishi va
to'g'ri xabar berilishi tekshiriladi.
"""

import pytest

from src.models import Option, Question
from src.validator import Severity, ValidationError, has_errors, validate


# ---------------------------------------------------------------------------
# Yordamchi: to'g'ri savolni tez yaratish
# ---------------------------------------------------------------------------


def _make_question(
    number: int = 1,
    text: str = "Savol matni bu yerda?",
    options: list[Option] | None = None,
    source_file: str = "test.docx",
) -> Question:
    """To'g'ri shakllangan savol yaratadi (default: 4 variant, bitta to'g'ri)."""
    if options is None:
        options = [
            Option(letter="A", text="birinchi"),
            Option(letter="B", text="ikkinchi"),
            Option(letter="C", text="uchinchi", is_correct=True),
            Option(letter="D", text="to'rtinchi"),
        ]
    return Question(
        number=number,
        text=text,
        options=options,
        source_file=source_file,
    )


# ---------------------------------------------------------------------------
# To'g'ri savol — xato yo'q
# ---------------------------------------------------------------------------


class TestTogriSavol:
    """To'g'ri shakllangan savollar — xato bo'lmasligi kerak."""

    def test_bitta_togri_savol_xatosiz(self):
        """To'g'ri savol — bo'sh xatolar ro'yxati."""
        errors = validate([_make_question()])
        assert errors == []

    def test_bir_nechta_togri_savol_xatosiz(self):
        """Bir nechta to'g'ri savol — xato yo'q."""
        questions = [
            _make_question(number=1, text="Birinchi savol?"),
            _make_question(number=2, text="Ikkinchi savol?"),
            _make_question(number=3, text="Uchinchi savol?"),
        ]
        errors = validate(questions)
        assert errors == []

    def test_bosh_royxat_xatosiz(self):
        """Bo'sh ro'yxat — xato yo'q."""
        errors = validate([])
        assert errors == []


# ---------------------------------------------------------------------------
# Variant soni tekshiruvi
# ---------------------------------------------------------------------------


class TestVariantSoni:
    """Variant soni 4 dan kam yoki ko'p bo'lsa xato."""

    def test_uch_variant_xato(self):
        """3 ta variant — XATO."""
        q = _make_question(options=[
            Option(letter="A", text="bir"),
            Option(letter="B", text="ikki"),
            Option(letter="C", text="uch", is_correct=True),
        ])
        errors = validate([q])

        assert len(errors) == 1
        assert errors[0].severity == Severity.XATO
        assert "3 ta variant topildi" in errors[0].message
        assert "4 ta kerak" in errors[0].message

    def test_besh_variant_xato(self):
        """5 ta variant — XATO."""
        q = _make_question(options=[
            Option(letter="A", text="bir"),
            Option(letter="B", text="ikki"),
            Option(letter="C", text="uch", is_correct=True),
            Option(letter="D", text="to'rt"),
            Option(letter="E", text="besh"),
        ])
        errors = validate([q])

        xato_msgs = [e for e in errors if "5 ta variant topildi" in e.message]
        assert len(xato_msgs) == 1
        assert xato_msgs[0].severity == Severity.XATO

    def test_nol_variant_xato(self):
        """Variantsiz savol — XATO (variant soni va to'g'ri javob yo'qligi)."""
        q = _make_question(options=[])
        errors = validate([q])

        variant_err = [e for e in errors if "variant topildi" in e.message]
        assert len(variant_err) == 1
        assert "0 ta variant" in variant_err[0].message

    def test_tort_variant_xatosiz(self):
        """Aniq 4 ta variant — xato yo'q."""
        errors = validate([_make_question()])
        variant_err = [e for e in errors if "variant topildi" in e.message]
        assert variant_err == []


# ---------------------------------------------------------------------------
# To'g'ri javob tekshiruvi
# ---------------------------------------------------------------------------


class TestTogriJavob:
    """To'g'ri javob mavjudligi va yagonaligi."""

    def test_togri_javob_yoq_xato(self):
        """Hech bir variant * bilan belgilanmagan — XATO."""
        q = _make_question(options=[
            Option(letter="A", text="bir"),
            Option(letter="B", text="ikki"),
            Option(letter="C", text="uch"),
            Option(letter="D", text="to'rt"),
        ])
        errors = validate([q])

        javob_err = [e for e in errors if "To'g'ri javob belgilanmagan" in e.message]
        assert len(javob_err) == 1
        assert javob_err[0].severity == Severity.XATO
        assert "* belgisi yo'q" in javob_err[0].message

    def test_ikki_togri_javob_xato(self):
        """Ikki variant * bilan belgilangan — XATO."""
        q = _make_question(options=[
            Option(letter="A", text="bir", is_correct=True),
            Option(letter="B", text="ikki", is_correct=True),
            Option(letter="C", text="uch"),
            Option(letter="D", text="to'rt"),
        ])
        errors = validate([q])

        javob_err = [e for e in errors if "Bir nechta to'g'ri javob" in e.message]
        assert len(javob_err) == 1
        assert javob_err[0].severity == Severity.XATO
        assert "2 ta" in javob_err[0].message

    def test_uch_togri_javob_xato(self):
        """Uchta to'g'ri javob — xato xabarida '3 ta' ko'rsatilsin."""
        q = _make_question(options=[
            Option(letter="A", text="bir", is_correct=True),
            Option(letter="B", text="ikki", is_correct=True),
            Option(letter="C", text="uch", is_correct=True),
            Option(letter="D", text="to'rt"),
        ])
        errors = validate([q])

        javob_err = [e for e in errors if "Bir nechta to'g'ri javob" in e.message]
        assert len(javob_err) == 1
        assert "3 ta" in javob_err[0].message

    def test_bitta_togri_javob_xatosiz(self):
        """Aniq bitta to'g'ri javob — xato yo'q."""
        errors = validate([_make_question()])
        javob_err = [
            e for e in errors
            if "To'g'ri javob" in e.message or "to'g'ri javob" in e.message
        ]
        assert javob_err == []


# ---------------------------------------------------------------------------
# Variant harflari tekshiruvi
# ---------------------------------------------------------------------------


class TestVariantHarflari:
    """Variant harflari faqat A, B, C, D bo'lishi kerak."""

    def test_notogri_harf_e_xato(self):
        """'E' harfi — XATO."""
        q = _make_question(options=[
            Option(letter="A", text="bir"),
            Option(letter="B", text="ikki"),
            Option(letter="C", text="uch", is_correct=True),
            Option(letter="E", text="besh"),
        ])
        errors = validate([q])

        harf_err = [e for e in errors if "Noto'g'ri variant harfi" in e.message]
        assert len(harf_err) == 1
        assert "'E'" in harf_err[0].message

    def test_kichik_harf_xato(self):
        """'a' (kichik harf) — XATO. Parser katta harfga keltirishi kerak."""
        q = _make_question(options=[
            Option(letter="a", text="bir"),
            Option(letter="B", text="ikki"),
            Option(letter="C", text="uch", is_correct=True),
            Option(letter="D", text="to'rt"),
        ])
        errors = validate([q])

        harf_err = [e for e in errors if "Noto'g'ri variant harfi" in e.message]
        assert len(harf_err) == 1
        assert "'a'" in harf_err[0].message

    def test_togri_harflar_xatosiz(self):
        """A, B, C, D — xato yo'q."""
        errors = validate([_make_question()])
        harf_err = [e for e in errors if "variant harfi" in e.message]
        assert harf_err == []


# ---------------------------------------------------------------------------
# Takror savollar tekshiruvi
# ---------------------------------------------------------------------------


class TestTakrorSavollar:
    """Bir xil savol matnli savollar — XATO."""

    def test_ikki_bir_xil_savol_xato(self):
        """Ikki savol bir xil matnga ega — ikkinchisida XATO."""
        questions = [
            _make_question(number=1, text="Python nima?"),
            _make_question(number=5, text="Python nima?"),
        ]
        errors = validate(questions)

        takror_err = [e for e in errors if "Takror savol" in e.message]
        assert len(takror_err) == 1
        assert takror_err[0].question_number == 5
        assert "savol #1" in takror_err[0].message

    def test_takror_savol_katta_kichik_harf_farqsiz(self):
        """Katta/kichik harf farqi — baribir takror deb hisoblanadi."""
        questions = [
            _make_question(number=1, text="Python nima?"),
            _make_question(number=2, text="python nima?"),
        ]
        errors = validate(questions)

        takror_err = [e for e in errors if "Takror savol" in e.message]
        assert len(takror_err) == 1

    def test_takror_savol_bosh_qator_farqsiz(self):
        """Bo'sh qatorlar atrofida farq — baribir takror."""
        questions = [
            _make_question(number=1, text="Python nima?"),
            _make_question(number=2, text="  Python nima?  "),
        ]
        errors = validate(questions)

        takror_err = [e for e in errors if "Takror savol" in e.message]
        assert len(takror_err) == 1

    def test_uch_bir_xil_savol_ikki_xato(self):
        """Uchta bir xil savol — ikkinchi va uchinchida XATO."""
        questions = [
            _make_question(number=1, text="Python nima?"),
            _make_question(number=2, text="Python nima?"),
            _make_question(number=3, text="Python nima?"),
        ]
        errors = validate(questions)

        takror_err = [e for e in errors if "Takror savol" in e.message]
        assert len(takror_err) == 2
        assert {e.question_number for e in takror_err} == {2, 3}

    def test_har_xil_savollar_xatosiz(self):
        """Turli savollar — takror xatosi yo'q."""
        questions = [
            _make_question(number=1, text="Python nima?"),
            _make_question(number=2, text="Java nima?"),
        ]
        errors = validate(questions)

        takror_err = [e for e in errors if "Takror savol" in e.message]
        assert takror_err == []


# ---------------------------------------------------------------------------
# Qisqa savol matni (ogohlantirish)
# ---------------------------------------------------------------------------


class TestQisqaSavolMatni:
    """Savol matni juda qisqa — OGOHLANTIRISH (XATO emas)."""

    def test_qisqa_matn_ogohlantirish(self):
        """4 belgili savol — OGOHLANTIRISH."""
        q = _make_question(text="Ha?")
        errors = validate([q])

        qisqa_err = [e for e in errors if "juda qisqa" in e.message]
        assert len(qisqa_err) == 1
        assert qisqa_err[0].severity == Severity.OGOHLANTIRISH

    def test_bosh_matn_ogohlantirish(self):
        """Bo'sh savol matni — OGOHLANTIRISH."""
        q = _make_question(text="")
        errors = validate([q])

        qisqa_err = [e for e in errors if "juda qisqa" in e.message]
        assert len(qisqa_err) == 1
        assert qisqa_err[0].severity == Severity.OGOHLANTIRISH

    def test_yetarli_uzunlik_xatosiz(self):
        """5 belgili savol — ogohlantirish yo'q."""
        q = _make_question(text="12345")
        errors = validate([q])

        qisqa_err = [e for e in errors if "juda qisqa" in e.message]
        assert qisqa_err == []

    def test_ogohlantirish_generatsiyani_toxtatmaydi(self):
        """Faqat OGOHLANTIRISH bo'lsa, has_errors() False qaytarsin."""
        q = _make_question(text="Ha?")
        errors = validate([q])

        assert not has_errors(errors)


# ---------------------------------------------------------------------------
# has_errors() funksiyasi
# ---------------------------------------------------------------------------


class TestHasErrors:
    """has_errors() yordamchi funksiyasi testlari."""

    def test_xato_bor(self):
        """XATO darajali xato bor — True."""
        errors = [ValidationError(
            source_file="test.docx",
            question_number=1,
            message="test",
            severity=Severity.XATO,
        )]
        assert has_errors(errors) is True

    def test_faqat_ogohlantirish(self):
        """Faqat OGOHLANTIRISH — False."""
        errors = [ValidationError(
            source_file="test.docx",
            question_number=1,
            message="test",
            severity=Severity.OGOHLANTIRISH,
        )]
        assert has_errors(errors) is False

    def test_bosh_royxat(self):
        """Bo'sh ro'yxat — False."""
        assert has_errors([]) is False

    def test_xato_va_ogohlantirish_aralash(self):
        """Aralash — XATO bor, demak True."""
        errors = [
            ValidationError("f.docx", 1, "xato", Severity.XATO),
            ValidationError("f.docx", 2, "ogoh", Severity.OGOHLANTIRISH),
        ]
        assert has_errors(errors) is True


# ---------------------------------------------------------------------------
# ValidationError.format() metodi
# ---------------------------------------------------------------------------


class TestValidationErrorFormat:
    """Xato xabarini formatlash testlari."""

    def test_xato_formati(self):
        """XATO formati: [XATO] fayl.docx, savol #14: xabar."""
        err = ValidationError(
            source_file="python_lugat.docx",
            question_number=14,
            message="To'g'ri javob belgilanmagan (* belgisi yo'q)",
        )
        expected = (
            "[XATO] python_lugat.docx, savol #14: "
            "To'g'ri javob belgilanmagan (* belgisi yo'q)"
        )
        assert err.format() == expected

    def test_ogohlantirish_formati(self):
        """OGOHLANTIRISH formati."""
        err = ValidationError(
            source_file="bank.docx",
            question_number=22,
            message="Savol matni juda qisqa, parsing xatosi bo'lishi mumkin",
            severity=Severity.OGOHLANTIRISH,
        )
        expected = (
            "[OGOHLANTIRISH] bank.docx, savol #22: "
            "Savol matni juda qisqa, parsing xatosi bo'lishi mumkin"
        )
        assert err.format() == expected


# ---------------------------------------------------------------------------
# Source file va savol raqami tekshiruvi
# ---------------------------------------------------------------------------


class TestXatoMetadatasi:
    """Xato xabarida fayl nomi va savol raqami to'g'ri ko'rsatilishi."""

    def test_source_file_xatoda_korinadi(self):
        """Xatoda manba fayl nomi ko'rsatilsin."""
        q = _make_question(
            number=7,
            source_file="modul_va_paketlar.docx",
            options=[
                Option(letter="A", text="bir"),
                Option(letter="B", text="ikki"),
                Option(letter="C", text="uch"),
            ],
        )
        errors = validate([q])

        assert any(e.source_file == "modul_va_paketlar.docx" for e in errors)

    def test_savol_raqami_xatoda_korinadi(self):
        """Xatoda savol raqami to'g'ri ko'rsatilsin."""
        q = _make_question(
            number=42,
            options=[
                Option(letter="A", text="bir"),
                Option(letter="B", text="ikki"),
                Option(letter="C", text="uch", is_correct=True),
            ],
        )
        errors = validate([q])

        assert any(e.question_number == 42 for e in errors)


# ---------------------------------------------------------------------------
# Bir savolda bir nechta xato
# ---------------------------------------------------------------------------


class TestKopXato:
    """Bitta savolda bir nechta xato bir vaqtda topilishi mumkin."""

    def test_variant_soni_va_togri_javob_yoq(self):
        """3 ta variant va to'g'ri javob yo'q — ikkita XATO."""
        q = _make_question(options=[
            Option(letter="A", text="bir"),
            Option(letter="B", text="ikki"),
            Option(letter="C", text="uch"),
        ])
        errors = validate([q])

        assert len([e for e in errors if e.severity == Severity.XATO]) >= 2
        msgs = [e.message for e in errors]
        assert any("variant topildi" in m for m in msgs)
        assert any("To'g'ri javob belgilanmagan" in m for m in msgs)

    def test_notogri_harf_va_qisqa_matn(self):
        """Noto'g'ri harf + qisqa matn — XATO va OGOHLANTIRISH."""
        q = _make_question(
            text="Q?",
            options=[
                Option(letter="A", text="bir"),
                Option(letter="B", text="ikki"),
                Option(letter="C", text="uch", is_correct=True),
                Option(letter="X", text="noto'g'ri"),
            ],
        )
        errors = validate([q])

        assert any(e.severity == Severity.XATO for e in errors)
        assert any(e.severity == Severity.OGOHLANTIRISH for e in errors)


# ---------------------------------------------------------------------------
# Real fayllar bilan integratsiya (parser + validator)
# ---------------------------------------------------------------------------


class TestRealFayllar:
    """Real test_banks/ fayllarini parse qilib, validatsiya tekshiruvi."""

    def test_python_lugat_validatsiya(self):
        """python_lugat.docx — faqat ma'lum xatolar bo'lishi kutiladi.

        Savol #29 da 'Javob: C' formati ishlatilgan — bu qo'llab-quvvatlanmaydi
        (CLAUDE.md: '`Javob: X` kabi alohida marker QO'LLAB-QUVVATLANMAYDI').
        Validator shu savolda to'g'ri xato berishi kerak.
        """
        from pathlib import Path
        from src.parser import parse_docx

        path = Path("test_banks/python_lugat.docx")
        if not path.exists():
            pytest.skip("test_banks/python_lugat.docx mavjud emas")

        questions = parse_docx(path)
        errors = validate(questions)

        xato_errors = [e for e in errors if e.severity == Severity.XATO]

        # Savol #29 xatosi kutiladi (Javob: C formati ishlatilgan).
        q29_errors = [e for e in xato_errors if e.question_number == 29]
        assert len(q29_errors) == 1, "Savol #29 da aniq bitta xato kutiladi"
        assert "To'g'ri javob belgilanmagan" in q29_errors[0].message

        # Boshqa savollarida xato bo'lmasligi kerak.
        other_errors = [e for e in xato_errors if e.question_number != 29]
        assert other_errors == [], (
            f"python_lugat.docx da kutilmagan {len(other_errors)} ta xato:\n"
            + "\n".join(e.format() for e in other_errors)
        )

    def test_modul_va_paketlar_validatsiya(self):
        """modul_va_paketlar.docx — xato bo'lmasligi kerak."""
        from pathlib import Path
        from src.parser import parse_docx

        path = Path("test_banks/modul_va_paketlar.docx")
        if not path.exists():
            pytest.skip("test_banks/modul_va_paketlar.docx mavjud emas")

        questions = parse_docx(path)
        errors = validate(questions)

        xato_errors = [e for e in errors if e.severity == Severity.XATO]
        assert xato_errors == [], (
            f"modul_va_paketlar.docx da {len(xato_errors)} ta xato:\n"
            + "\n".join(e.format() for e in xato_errors)
        )
