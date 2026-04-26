"""Word fayldan test bankini o'qish.

Bu modul faqat parse qiladi va `Question` ro'yxati qaytaradi.
Validatsiya `validator.py` da bajariladi (4-bosqichda qo'shiladi).

Qo'llab-quvvatlanadigan formatlar:
- **Raqamli format**: paragraf matnida "1. Savol?" prefiksi mavjud.
- **Bulletli format**: Word'ning avto-numerlash (numbered list) xususiyati
  ishlatilgan; matnda "N." yo'q, parser numerlashni paragraflar tartibidan
  tiklaydi (synthetic counter).

Paragraflar ichida soft break (`\\n`) bo'lishi mumkin — bu kod bloklari va
ba'zan bir paragrafga ikki savol joylashishi uchun. `paragraphs_to_lines`
shu hodisalarni hisobga oladi.
"""

import os
import re
from pathlib import Path
from typing import Callable

from docx import Document
from docx.oxml.ns import qn

from src.models import Option, Question

# "1. Savol matni" yoki "1." ni topadi.
# `\.` dan keyin bo'shliq talab qilinadi (yoki qator oxiri) — bu "12.3"
# kabi raqamlarni savol sarlavhasi sifatida talqin qilmaslik uchun.
_QUESTION_HEADER_RE = re.compile(r"^\s*(\d+)\.(?:\s+(.*?))?\s*$")

# "A) matn", "*A) matn", "*A)matn" ni topadi.
# Kichik harf (a/b/c/d) ham qabul qilinadi va keyin katta harfga keltiriladi.
_OPTION_RE = re.compile(r"^\s*(\*?)([A-Da-d])\)\s*(.*?)\s*$")


def _clean_text(text: str) -> str:
    """Bitta qator matnini tozalaydi.

    - Markdown bold (`**...**`) belgilarini olib tashlaydi.
    - Trailing bo'shliqlarni tozalaydi (leading bo'shliqni saqlaydi —
      bu kod bloklari uchun zarur).
    """
    return text.replace("**", "").rstrip()


def parse_lines(lines: list[str], source_file: str = "") -> list[Question]:
    """Matn qatorlardan savollar ro'yxatini parse qiladi.

    Bu sof funksiya — fayl o'qimaydi, faqat berilgan qatorlardan savol
    obyektlarini shakllantiradi. Validatsiya qilmaydi: noto'g'ri formatdagi
    savollar (3 ta variantli, to'g'ri javobsiz) ham qaytariladi va keyinroq
    validator tomonidan tekshiriladi.

    Args:
        lines: Word paragraflarining matn qatorlari.
        source_file: Manba fayl nomi (har bir Question.source_file ga yoziladi).

    Returns:
        Topilgan savollar ro'yxati. Validatsiya qilinmagan.
    """
    questions: list[Question] = []

    current_q: Question | None = None
    q_text_buf: list[str] = []
    current_letter: str | None = None
    option_text_buf: list[str] = []
    is_correct = False

    def flush_option() -> None:
        """Joriy variantni current_q ga qo'shadi va buferlarni tozalaydi."""
        nonlocal current_letter, option_text_buf, is_correct
        if current_q is not None and current_letter is not None:
            text = "\n".join(option_text_buf).strip()
            current_q.options.append(
                Option(letter=current_letter, text=text, is_correct=is_correct)
            )
        current_letter = None
        option_text_buf = []
        is_correct = False

    def flush_question() -> None:
        """Joriy savolni questions ga qo'shadi va buferlarni tozalaydi."""
        nonlocal current_q, q_text_buf
        flush_option()
        if current_q is not None:
            current_q.text = "\n".join(q_text_buf).strip()
            questions.append(current_q)
        current_q = None
        q_text_buf = []

    for raw in lines:
        line = _clean_text(raw)

        # Bo'sh qatorlarni o'tkazib yuboramiz: ular savollar orasida ham,
        # ichida ham faqat ko'rinish uchun ishlatiladi.
        if not line.strip():
            continue

        m_header = _QUESTION_HEADER_RE.match(line)
        m_option = _OPTION_RE.match(line)

        # Yangi savol qachon boshlanishi mumkin:
        # - hozircha hech qaysi savol o'qilmagan, yoki
        # - oldingi savolning oxirgi (D) varianti o'qib bo'lingan.
        # Bu chegara savol matni ichidagi "2. ..." kabi raqamli qatorlar
        # noto'g'ri talqin qilinmasligi uchun zarur (kod bloklari, izohlar).
        can_start_new_q = current_q is None or current_letter == "D"

        if m_header and not m_option and can_start_new_q:
            flush_question()
            number = int(m_header.group(1))
            current_q = Question(
                number=number,
                text="",
                options=[],
                source_file=source_file,
            )
            first_line = (m_header.group(2) or "").strip()
            if first_line:
                q_text_buf.append(first_line)
            continue

        if m_option and current_q is not None:
            flush_option()
            star = m_option.group(1)
            current_letter = m_option.group(2).upper()
            is_correct = bool(star)
            rest = m_option.group(3).strip()
            if rest:
                option_text_buf.append(rest)
            continue

        # Davomiy matn qatori.
        if current_q is None:
            # Birinchi savoldan oldingi sarlavha/izohlarni o'tkazib yubor.
            continue
        if current_letter is None:
            # Hali savol matnini o'qiyapmiz (A) gacha).
            q_text_buf.append(line)
        else:
            # Joriy variant matnini davom ettiryapmiz.
            option_text_buf.append(line)

    flush_question()
    return questions


def _has_word_numbering(paragraph) -> bool:
    """Paragraf Word avto-numerlash (numbered list) ostida joylashganini tekshiradi.

    Word `numId` ni `w:pPr/w:numPr` XML elementida saqlaydi. Agar shu element
    mavjud bo'lsa, paragraf bullet/numbered list elementi hisoblanadi va
    odatda matnda "N." prefiksi ko'rinmaydi.
    """
    pPr = paragraph._p.find(qn("w:pPr"))
    if pPr is None:
        return False
    return pPr.find(qn("w:numPr")) is not None


def paragraphs_to_lines(
    paragraphs,
    *,
    sequential_start: int = 1,
    has_numbering_fn: Callable = _has_word_numbering,
) -> list[str]:
    """Word paragraflarini `parse_lines` uchun logical qatorlarga aylantiradi.

    Bajariladigan ish:
    - Har bir paragraf matnini `\\n` (soft break) bo'yicha bo'ladi.
    - Agar paragrafda Word avto-numerlash bor (numId) va matni "N." bilan
      boshlanmasa, birinchi qatorga synthetic ``f"{counter}. "`` prefiksi
      qo'shiladi. Counter `sequential_start` dan boshlanadi va shu turdagi
      har bir paragrafda 1 ga o'sadi.

    Args:
        paragraphs: python-docx `Paragraph` obyektlari (yoki testlar uchun
            mos atributli fake obyektlar). `.text` atributi va
            `has_numbering_fn` kerak.
        sequential_start: Synthetic counter boshlang'ich qiymati.
        has_numbering_fn: Paragrafda Word numberlash borligini aniqlash
            funksiyasi. Default — `_has_word_numbering` (XML inspeksiyasi).

    Returns:
        Logical qatorlar ro'yxati. `parse_lines` ga to'g'ridan-to'g'ri uzatish
        mumkin.
    """
    lines: list[str] = []
    counter = sequential_start - 1

    for p in paragraphs:
        text = p.text or ""
        if not text.strip():
            continue

        first_line = text.split("\n", 1)[0]
        starts_with_number = (
            _QUESTION_HEADER_RE.match(_clean_text(first_line)) is not None
        )

        if has_numbering_fn(p) and not starts_with_number:
            counter += 1
            if "\n" in text:
                first, rest = text.split("\n", 1)
                text = f"{counter}. {first}\n{rest}"
            else:
                text = f"{counter}. {text}"

        lines.extend(text.split("\n"))

    return lines


def parse_docx(path: str | Path) -> list[Question]:
    """Word fayldan savollar ro'yxatini parse qiladi.

    Raqamli va bulletli formatlarni avtomatik aniqlaydi: paragraflar
    `paragraphs_to_lines` orqali normallashtirilib, keyin `parse_lines`
    ga uzatiladi.

    Args:
        path: `.docx` fayl manzili.

    Returns:
        Topilgan savollar ro'yxati. Validatsiya qilinmagan — keyingi bosqichda
        `validator.validate()` orqali tekshirilishi kerak.
    """
    doc = Document(str(path))
    lines = paragraphs_to_lines(doc.paragraphs)
    return parse_lines(lines, source_file=os.path.basename(str(path)))
