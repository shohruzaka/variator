"""Test variantlarini generatsiya qilish (5-bosqich).

Savollar ro'yxatidan belgilangan miqdorda aralashtirilgan variantlar yaratadi.
Har bir variant takrorlanuvchanlik (reproducibility) uchun o'ziga xos seed
orqali generatsiya qilinadi.
"""

import copy
import random

from src.constants import VALID_OPTION_LETTERS
from src.models import Option, Question, Variant


def _shuffle_question(q: Question, rng: random.Random, new_number: int) -> Question:
    """Bitta savolning nusxasini yaratib, variantlarini aralashtiradi.

    Asl savol obyektini o'zgartirmaydi (pure function yondashuvi).
    Yangi savol obyektida `number` atributi `new_number` ga o'rnatiladi va
    variantlar (options) aralashtirilib, harflari ("A", "B", "C", "D") yangilanadi.

    Args:
        q: Asl savol obyekti.
        rng: Random raqamlar generatori (deterministik natija uchun).
        new_number: Variantdagi yangi savol raqami.

    Returns:
        Variantlari aralashtirilgan yangi Question obyekti.
    """
    # Asl obyektni o'zgartirmaslik uchun deepcopy qilamiz
    new_q = copy.deepcopy(q)
    new_q.number = new_number

    # Variantlarni aralashtirish
    rng.shuffle(new_q.options)

    # Variantlarga yangi harflarni berib chiqish ("A", "B", "C", "D")
    letters = sorted(list(VALID_OPTION_LETTERS))
    for i, opt in enumerate(new_q.options):
        opt.letter = letters[i]

    return new_q


from collections import defaultdict

def _stratified_sample(questions: list[Question], k: int, rng: random.Random) -> list[Question]:
    """Bir nechta manbadan (mavzudan) proporsional ravishda savollarni tanlaydi.
    
    Agar so'ralgan k miqdor umumiy savollar sonidan katta yoki teng bo'lsa,
    barcha savollar olinadi. Aks holda, har bir source_file dan o'zining
    ulushiga mos ravishda (Largest Remainder Method orqali) savollar olinadi.
    """
    if k >= len(questions):
        return list(questions)
        
    # Manbalar bo'yicha guruhlash
    groups: dict[str, list[Question]] = defaultdict(list)
    for q in questions:
        groups[q.source_file].append(q)
        
    total_q = len(questions)
    
    # Har bir manba uchun kvotani hisoblash (butun va qoldiq qism)
    quotients = {}
    for src, group in groups.items():
        quotients[src] = (len(group) / total_q) * k
        
    allocations = {src: int(q) for src, q in quotients.items()}
    remainder = k - sum(allocations.values())
    
    # Qoldiqni eng katta qoldiqqa ega manbalarga tarqatish
    if remainder > 0:
        remainders = {src: q - int(q) for src, q in quotients.items()}
        # Qoldig'i kattalarini oldinga chiqarish
        sorted_srcs = sorted(remainders.keys(), key=lambda x: remainders[x], reverse=True)
        for i in range(remainder):
            allocations[sorted_srcs[i]] += 1
            
    # Har bir manbadan kerakli miqdorda savol tanlash
    sampled: list[Question] = []
    for src, group in groups.items():
        count = allocations[src]
        if count > 0:
            # Asl ro'yxatni o'zgartirmaslik uchun nusxasini aralashtiramiz
            group_copy = list(group)
            rng.shuffle(group_copy)
            sampled.extend(group_copy[:count])
            
    return sampled


def generate_variants(
    questions: list[Question], 
    count: int, 
    base_seed: int = 42,
    questions_per_variant: int | None = None
) -> list[Variant]:
    """Belgilangan miqdorda test variantlarini generatsiya qiladi.

    Args:
        questions: Validatsiyadan o'tgan savollar ro'yxati.
        count: Nechta variant yaratish kerakligi.
        base_seed: Reproducibility uchun boshlang'ich seed.
        questions_per_variant: Har bir variantda nechta savol bo'lishi kerak.
            Agar None bo'lsa, barcha savollar olinadi. Agar qiymat berilsa,
            manbalar (source_file) bo'yicha proporsional stratified sampling qilinadi.

    Returns:
        Yaratilgan Variant obyektlari ro'yxati.
    """
    variants: list[Variant] = []

    for i in range(count):
        variant_number = i + 1
        # Har bir variant o'ziga xos va takrorlanuvchi seed oladi
        seed = base_seed + variant_number
        rng = random.Random(seed)

        # Savollarni tanlash
        if questions_per_variant is not None:
            # Stratified sampling orqali kerakli miqdorda tanlab olamiz
            selected_questions = _stratified_sample(questions, questions_per_variant, rng)
        else:
            selected_questions = list(questions)

        # Savollar tartibini aralashtirish
        rng.shuffle(selected_questions)

        # Har bir savolning o'zini (variantlarini) aralashtirib, yangi ob'ekt yaratamiz
        variant_questions = []
        for q_idx, q in enumerate(selected_questions):
            new_q = _shuffle_question(q, rng, new_number=q_idx + 1)
            variant_questions.append(new_q)

        variants.append(
            Variant(
                number=variant_number,
                seed=seed,
                questions=variant_questions,
            )
        )

    return variants
