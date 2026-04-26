"""Generator uchun unit testlar (5-bosqich)."""

import pytest

from src.generator import generate_variants
from src.models import Option, Question


# ---------------------------------------------------------------------------
# Yordamchi: test savollarini yaratish
# ---------------------------------------------------------------------------


def _make_sample_questions() -> list[Question]:
    """Test uchun 3 ta savol yaratadi."""
    return [
        Question(
            number=1,
            text="Birinchi savol?",
            options=[
                Option("A", "1-A"),
                Option("B", "1-B"),
                Option("C", "1-C", is_correct=True),
                Option("D", "1-D"),
            ],
            source_file="test.docx",
        ),
        Question(
            number=2,
            text="Ikkinchi savol?",
            options=[
                Option("A", "2-A", is_correct=True),
                Option("B", "2-B"),
                Option("C", "2-C"),
                Option("D", "2-D"),
            ],
            source_file="test.docx",
        ),
        Question(
            number=3,
            text="Uchinchi savol?",
            options=[
                Option("A", "3-A"),
                Option("B", "3-B"),
                Option("C", "3-C"),
                Option("D", "3-D", is_correct=True),
            ],
            source_file="test.docx",
        ),
    ]


# ---------------------------------------------------------------------------
# Testlar
# ---------------------------------------------------------------------------


def test_generator_variant_soni():
    """Belgilangan miqdorda variantlar yaratilishi kerak."""
    questions = _make_sample_questions()
    variants = generate_variants(questions, count=5)

    assert len(variants) == 5
    for i, v in enumerate(variants):
        assert v.number == i + 1


def test_generator_savollar_soni_saqlanadi():
    """Har bir variantda asl ro'yxatdagi kabi miqdorda savol bo'lishi kerak."""
    questions = _make_sample_questions()
    variants = generate_variants(questions, count=1)
    
    assert len(variants[0].questions) == len(questions)


def test_generator_asl_savollarni_ozgartirmaydi():
    """Generator `pure function` kabi ishlashi, asl savollarga tegmasligi kerak."""
    questions = _make_sample_questions()
    
    # Asl holatni saqlab qo'yamiz
    original_q1_text = questions[0].text
    original_q1_opt_a = questions[0].options[0].text
    
    generate_variants(questions, count=3)
    
    # Asl ro'yxat va uning ob'ektlari o'zgarmaganligini tekshiramiz
    assert questions[0].text == original_q1_text
    assert questions[0].options[0].text == original_q1_opt_a
    assert questions[0].number == 1


def test_generator_savol_raqamlarini_yangilaydi():
    """Variantdagi savollar har doim 1 dan boshlab nomerlanishi kerak."""
    questions = _make_sample_questions()
    # Asl savollar 1, 2, 3 tartibida, ammo aralashtirilganda asl 3-savol 1-o'ringa tushishi mumkin.
    variants = generate_variants(questions, count=2)
    
    for v in variants:
        assert [q.number for q in v.questions] == [1, 2, 3]


def test_generator_variant_harflarini_yangilaydi():
    """Variant ichidagi javob harflari har doim A, B, C, D bo'lishi kerak."""
    questions = _make_sample_questions()
    variants = generate_variants(questions, count=2)
    
    for v in variants:
        for q in v.questions:
            assert [o.letter for o in q.options] == ["A", "B", "C", "D"]


def test_generator_deterministik_natija_beradi():
    """Bir xil seed -> bir xil natija (reproducibility)."""
    questions1 = _make_sample_questions()
    questions2 = _make_sample_questions()
    
    # Ikkala chaqiriq ham bir xil base_seed bilan
    variants1 = generate_variants(questions1, count=3, base_seed=100)
    variants2 = generate_variants(questions2, count=3, base_seed=100)
    
    # 1-variantlarning javob kalitlari mutlaqo bir xil bo'lishi kerak
    assert variants1[0].answer_key == variants2[0].answer_key
    assert variants1[1].answer_key == variants2[1].answer_key
    
    # Savollar ketma-ketligi (asl matni orqali) tekshiriladi
    v1_q1_text = variants1[0].questions[0].text
    v2_q1_text = variants2[0].questions[0].text
    assert v1_q1_text == v2_q1_text


def test_generator_turli_seed_turli_natija_beradi():
    """Turli seed -> har xil natija (yuqori ehtimol bilan)."""
    questions1 = _make_sample_questions()
    questions2 = _make_sample_questions()
    
    variants1 = generate_variants(questions1, count=1, base_seed=42)
    variants2 = generate_variants(questions2, count=1, base_seed=999)
    
    # Savollar tartibi yoki javoblar kaliti farq qilishi kutiladi
    # (Albatta, juda kichik ehtimol bilan bir xil bo'lib qolishi mumkin,
    # lekin 3 ta savol va 4 ta variant (jami 3! * (4!)^3 = 6 * 13824 = 82944 kombinatsiya)
    # bo'lganda bu test amalda doim o'tadi)
    
    is_questions_same = [q.text for q in variants1[0].questions] == [q.text for q in variants2[0].questions]
    is_answers_same = variants1[0].answer_key == variants2[0].answer_key
    
    # Ikkalasidan kamida bittasi farq qilishi kerak
    assert not (is_questions_same and is_answers_same)


def test_generator_answer_key_togri_ishlaydi():
    """`answer_key` to'g'ri javoblarning harflarini qaytarishi kerak."""
    questions = _make_sample_questions()
    variants = generate_variants(questions, count=1, base_seed=123)
    
    variant = variants[0]
    ans_key = variant.answer_key
    
    assert len(ans_key) == len(questions)
    
    # Har bir savol uchun javob harfi to'g'riligini tekshiramiz
    for q, correct_letter in zip(variant.questions, ans_key):
        correct_opt = next(o for o in q.options if o.letter == correct_letter)
        assert correct_opt.is_correct is True


# ---------------------------------------------------------------------------
# Stratified Sampling (6-bosqich) Testlari
# ---------------------------------------------------------------------------

def _make_stratified_questions() -> list[Question]:
    """Ikki xil manbadan iborat savollar ro'yxati (10 ta A, 5 ta B)."""
    questions = []
    # Manba A: 10 ta savol
    for i in range(10):
        questions.append(
            Question(
                number=i+1,
                text=f"A mavzu savoli {i+1}",
                options=[Option("A", "a", is_correct=True), Option("B", "b"), Option("C", "c"), Option("D", "d")],
                source_file="mavzu_A.docx"
            )
        )
    # Manba B: 5 ta savol
    for i in range(5):
        questions.append(
            Question(
                number=i+11,
                text=f"B mavzu savoli {i+1}",
                options=[Option("A", "a", is_correct=True), Option("B", "b"), Option("C", "c"), Option("D", "d")],
                source_file="mavzu_B.docx"
            )
        )
    return questions


def test_stratified_sampling_k_katta_bolsa():
    """So'ralgan savollar soni umumiy sonidan ko'p bo'lsa, barchasini olishi kerak."""
    questions = _make_stratified_questions() # Jami 15 ta
    variants = generate_variants(questions, count=1, questions_per_variant=20)
    
    assert len(variants[0].questions) == 15


def test_stratified_sampling_proporsional_olish():
    """Manbalardan o'z ulushiga mos ravishda (proporsional) olishi kerak."""
    questions = _make_stratified_questions() # 10 ta A (66.6%), 5 ta B (33.3%)
    
    # 6 ta savol so'rasak: 4 ta A dan, 2 ta B dan kelishi kerak
    variants = generate_variants(questions, count=1, questions_per_variant=6)
    sampled = variants[0].questions
    
    assert len(sampled) == 6
    
    count_A = sum(1 for q in sampled if q.source_file == "mavzu_A.docx")
    count_B = sum(1 for q in sampled if q.source_file == "mavzu_B.docx")
    
    assert count_A == 4
    assert count_B == 2


def test_stratified_sampling_yaxlitlash_largest_remainder():
    """Qoldiqlar qolganda 'Largest Remainder' metodi to'g'ri ishlashi kerak."""
    questions = []
    # A: 4 ta, B: 4 ta, C: 4 ta -> Toplam 12 ta
    for src in ["A", "B", "C"]:
        for i in range(4):
            questions.append(
                Question(
                    number=len(questions)+1,
                    text=f"{src} mavzu savoli",
                    options=[Option("A", "a", is_correct=True), Option("B", "b"), Option("C", "c"), Option("D", "d")],
                    source_file=f"{src}.docx"
                )
            )
    
    # Jami 12 ta savol. Biz 5 ta so'raymiz.
    # Har bir manbaning ulushi: (4/12) * 5 = 1.666...
    # Int qismi = 1, jami int qismlar yig'indisi = 3. Qoldiq = 2.
    # Qoldiqlar hammasida 0.666... bir xil. Ikkita manba +1 (ya'ni 2) oladi, bittasi 1 oladi.
    variants = generate_variants(questions, count=1, questions_per_variant=5)
    sampled = variants[0].questions
    
    assert len(sampled) == 5
    counts = {
        "A.docx": sum(1 for q in sampled if q.source_file == "A.docx"),
        "B.docx": sum(1 for q in sampled if q.source_file == "B.docx"),
        "C.docx": sum(1 for q in sampled if q.source_file == "C.docx"),
    }
    
    # Qiymatlar 2, 2, 1 (qaysi manba nechi olishi muhim emas, yig'indi 5 bo'lishi va ulashish to'g'ri bo'lishi kerak)
    values = sorted(counts.values())
    assert values == [1, 2, 2]
