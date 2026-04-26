"""Domain modellari: Option, Question, Variant.

Bu modulda faqat dataclass'lar va ularning sof metodlari bo'ladi.
Hech qanday I/O (fayl o'qish/yozish, chop etish) shu yerda yozilmaydi.
"""

from dataclasses import dataclass, field


@dataclass
class Option:
    """Test savolining bitta variant javobi.

    Atributlar:
        letter: Variant harfi ("A", "B", "C" yoki "D").
        text: Variantning matn qismi.
        is_correct: Shu variant to'g'ri javobmi.
    """

    letter: str
    text: str
    is_correct: bool = False


@dataclass
class Question:
    """Test banki savol.

    Atributlar:
        number: Asl manbadagi savol raqami (xato xabarlari uchun).
        text: Savol matni (ko'p qatorli bo'lishi mumkin).
        options: To'rtta variant javob ro'yxati.
        source_file: Savol qaysi fayldan kelgan (xato xabarlari uchun).
    """

    number: int
    text: str
    options: list[Option] = field(default_factory=list)
    source_file: str = ""

    @property
    def correct_option(self) -> Option:
        """To'g'ri javobni qaytaradi.

        Agar to'g'ri javob belgilanmagan bo'lsa yoki bittadan ko'p bo'lsa,
        ValueError ko'taradi. Bu validatsiyadan keyin chaqirilishi kerak.
        """
        correct = [o for o in self.options if o.is_correct]
        if len(correct) != 1:
            raise ValueError(
                f"Savol #{self.number}: aniq bitta to'g'ri javob bo'lishi kerak, "
                f"topildi: {len(correct)}"
            )
        return correct[0]

    @property
    def correct_letter(self) -> str:
        """To'g'ri javobning harfini qaytaradi (masalan, 'C')."""
        return self.correct_option.letter


@dataclass
class Variant:
    """Bir o'quvchi uchun yaratilgan test varianti.

    Atributlar:
        number: Variant tartib raqami (1, 2, 3, ...).
        seed: Reproducibility uchun ishlatilgan random seed.
        questions: Aralashtirilgan tartibdagi savollar (variantlar ham
            qayta harflangan bo'lishi mumkin).
    """

    number: int
    seed: int
    questions: list[Question] = field(default_factory=list)

    @property
    def answer_key(self) -> list[str]:
        """Har bir savol uchun to'g'ri javob harfi ro'yxati.

        Tartib `questions` ro'yxatidagi tartibga mos keladi.
        """
        return [q.correct_letter for q in self.questions]
