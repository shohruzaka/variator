"""Savollarni tekshirish (validatsiya).

Bu modul `list[Question]` ni oladi va `list[ValidationError]` qaytaradi.
Hech narsa yozmaydi va chop etmaydi — faqat xatolar ro'yxatini qaytaradi.
Xatolarni foydalanuvchiga ko'rsatish CLI modulining vazifasi.
"""

from dataclasses import dataclass
from enum import Enum

from src.constants import (
    MIN_QUESTION_TEXT_LENGTH,
    REQUIRED_OPTIONS_COUNT,
    VALID_OPTION_LETTERS,
)
from src.models import Question


class Severity(Enum):
    """Xato darajasi.

    XATO — generatsiyani to'xtatadi.
    OGOHLANTIRISH — faqat ogohlantirish, generatsiya davom etishi mumkin.
    """

    XATO = "XATO"
    OGOHLANTIRISH = "OGOHLANTIRISH"


@dataclass(frozen=True)
class ValidationError:
    """Bitta validatsiya xatosi.

    Atributlar:
        source_file: Manba fayl nomi.
        question_number: Savol raqami (asl manbadagi).
        message: Xato tavsifi (o'zbekcha).
        severity: Xato darajasi — XATO yoki OGOHLANTIRISH.
    """

    source_file: str
    question_number: int
    message: str
    severity: Severity = Severity.XATO

    def format(self) -> str:
        """Xatoni formatlangan qator sifatida qaytaradi.

        Format: [XATO] fayl.docx, savol #14: Xato tavsifi
        """
        return (
            f"[{self.severity.value}] {self.source_file}, "
            f"savol #{self.question_number}: {self.message}"
        )


def validate(questions: list[Question]) -> list[ValidationError]:
    """Savollar ro'yxatini tekshiradi va xatolar ro'yxatini qaytaradi.

    Tekshiriladigan qoidalar:
    1. Har bir savolda aniq 4 ta variant bo'lishi kerak.
    2. Har bir savolda aniq bitta to'g'ri javob (`*`) belgilangan bo'lishi kerak.
    3. Bir nechta variant `*` bilan belgilanmagan bo'lishi kerak.
    4. Variant harflari faqat A, B, C, D bo'lishi kerak.
    5. Bir xil savol matnli takror savollar bo'lmasligi kerak.
    6. Savol matni juda qisqa bo'lmasligi kerak (ogohlantirish).

    Args:
        questions: Parser tomonidan qaytarilgan savollar ro'yxati.

    Returns:
        Topilgan xatolar ro'yxati. Bo'sh ro'yxat — xato yo'q.
    """
    errors: list[ValidationError] = []
    seen_texts: dict[str, tuple[str, int]] = {}

    for q in questions:
        errors.extend(_validate_single(q))
        errors.extend(_check_duplicate(q, seen_texts))

    return errors


def has_errors(validation_errors: list[ValidationError]) -> bool:
    """Xatolar ichida kamida bitta XATO darajali bor-yo'qligini tekshiradi.

    OGOHLANTIRISH'lar generatsiyani to'xtatmaydi — faqat XATO'lar to'xtatadi.
    """
    return any(e.severity == Severity.XATO for e in validation_errors)


def _validate_single(q: Question) -> list[ValidationError]:
    """Bitta savolni tekshiradi (takrorlik tekshiruvisiz).

    Qaytaradi:
        Shu savol uchun topilgan xatolar ro'yxati.
    """
    errors: list[ValidationError] = []

    # 1. Variant soni tekshiruvi.
    if len(q.options) != REQUIRED_OPTIONS_COUNT:
        errors.append(ValidationError(
            source_file=q.source_file,
            question_number=q.number,
            message=(
                f"Faqat {len(q.options)} ta variant topildi "
                f"({REQUIRED_OPTIONS_COUNT} ta kerak)"
            ),
        ))

    # 2–3. To'g'ri javob soni tekshiruvi.
    correct_count = sum(1 for o in q.options if o.is_correct)
    if correct_count == 0:
        errors.append(ValidationError(
            source_file=q.source_file,
            question_number=q.number,
            message="To'g'ri javob belgilanmagan (* belgisi yo'q)",
        ))
    elif correct_count > 1:
        errors.append(ValidationError(
            source_file=q.source_file,
            question_number=q.number,
            message=(
                f"Bir nechta to'g'ri javob belgilangan "
                f"({correct_count} ta * belgisi topildi)"
            ),
        ))

    # 4. Variant harflari tekshiruvi.
    for o in q.options:
        if o.letter not in VALID_OPTION_LETTERS:
            errors.append(ValidationError(
                source_file=q.source_file,
                question_number=q.number,
                message=(
                    f"Noto'g'ri variant harfi: '{o.letter}' "
                    f"(faqat {', '.join(sorted(VALID_OPTION_LETTERS))} ruxsat etilgan)"
                ),
            ))

    # 6. Savol matni uzunligi tekshiruvi (ogohlantirish).
    if len(q.text.strip()) < MIN_QUESTION_TEXT_LENGTH:
        errors.append(ValidationError(
            source_file=q.source_file,
            question_number=q.number,
            message="Savol matni juda qisqa, parsing xatosi bo'lishi mumkin",
            severity=Severity.OGOHLANTIRISH,
        ))

    return errors


def _check_duplicate(
    q: Question, seen_texts: dict[str, tuple[str, int]]
) -> list[ValidationError]:
    """Savol matnining takrorligini tekshiradi.

    `seen_texts` lug'ati normallashtirilgan matn → (manba fayl, savol raqami)
    juftliklarini saqlaydi. Agar shu matn allaqachon uchragan bo'lsa,
    xato qaytariladi.

    Args:
        q: Tekshirilayotgan savol.
        seen_texts: Oldin uchragan savollar lug'ati (in-place yangilanadi).

    Returns:
        Takror savol topilsa — bitta xato, aks holda bo'sh ro'yxat.
    """
    normalized = " ".join(q.text.strip().lower().split())

    if normalized in seen_texts:
        first_file, first_number = seen_texts[normalized]
        return [ValidationError(
            source_file=q.source_file,
            question_number=q.number,
            message=(
                f"Takror savol matni ({first_file} faylidagi savol #{first_number} bilan bir xil)"
            ),
        )]

    seen_texts[normalized] = (q.source_file, q.number)
    return []
