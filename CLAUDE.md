# CLAUDE.md

Bu fayl Claude Code uchun loyiha bo'yicha asosiy ko'rsatmalarni saqlaydi. Loyiha bo'yicha har qanday vazifa bajarilishidan oldin shu fayl o'qib chiqilishi shart.

## Loyiha haqida

**Nomi:** Test Variant Generator
**Maqsadi:** O'qituvchilar uchun mo'ljallangan dastur. Word formatdagi test banklaridan ko'p variantli testlar generatsiya qiladi va har bir variant uchun javoblar kalitini tayyorlaydi.

**Foydalanuvchi:** O'qituvchi (texnik bo'lmagan foydalanuvchi). Buyruq qatori (CLI) orqali ishlatadi, lekin xato xabarlari aniq va tushunarli bo'lishi kerak.

**Asosiy oqim:**
1. O'qituvchi bir yoki bir nechta `.docx` test banki faylini beradi
2. Dastur savollarni o'qiydi va validatsiya qiladi
3. Belgilangan sondagi variantlarni generatsiya qiladi (savollar va A/B/C/D tartibini aralashtirib)
4. Har bir variantni alohida `.docx` faylga yozadi
5. Javoblar kalitini Word va Excel formatda tayyorlaydi

## Texnologiyalar

- **Python 3.10+** (dataclass'lar, type hints uchun)
- **python-docx** — Word fayllar bilan ishlash
- **openpyxl** — Excel javoblar jadvali uchun
- **click** — CLI interfeys
- **pyyaml** — config fayli
- **pytest** — unit testlar

Boshqa kutubxonalardan foydalanmang. Yangi dependency qo'shish kerak bo'lsa, avval foydalanuvchi bilan kelishing.

## Kodlash standartlari

- **Til:** Kod ichidagi izohlar, docstring'lar va xato xabarlari **o'zbek tilida** (lotin alifbosi). O'zgaruvchi va funksiya nomlari ingliz tilida.
- **Type hints majburiy** — barcha funksiya signature'larida.
- **Docstring'lar** — har bir public funksiya/sinf uchun, qisqa o'zbekcha tavsif.
- **Dataclass'lardan foydalaning** — domain modellar uchun (`Question`, `Option`, `Variant`).
- **Pure funksiyalarni afzal ko'ring** — parser, generator, validator side effect'siz ishlasin. Faylga yozish faqat exporter modulida.
- **Erta xato (fail fast)** — noto'g'ri ma'lumot kelsa, jim turish o'rniga aniq xato bering.
- **Magic number'larsiz** — `config.py` yoki `constants.py` da konstantalarni saqlang.

## Test banki formati (QAT'IY STANDART)

Bu format dastur tomonidan qo'llab-quvvatlanadigan **yagona** format. Boshqa formatlarni qo'llab-quvvatlamang — buning o'rniga validator aniq xato xabarini bersin.

### Savol formati

Savol shakli:

**1-shakl: Raqamli**
```
1. Savol matni shu yerda?
A) Birinchi variant
B) Ikkinchi variant
*C) Uchinchi variant (to'g'ri javob)
D) To'rtinchi variant
```

### Format qoidalari

1. **Variantlar har doim `A) B) C) D)` formatida** — to'rttadan kam yoki ko'p emas.
2. **To'g'ri javob `*` belgisi bilan boshlanadi:** `*A)`, `*B)`, `*C)` yoki `*D)`. Har bir savolda **aniq bitta** to'g'ri javob bo'lishi shart.
3. **`Javob: X` kabi alohida marker QO'LLAB-QUVVATLANMAYDI.** Agar parser bunday qatorni topsa yoki `*` belgisi yo'q bo'lsa, validator xato bersin va savol raqamini ko'rsatsin.
4. **Markdown bold (`**...**`)** — Word'dan kelishi mumkin, parser ularni avtomatik tozalaydi. Ammo `**` ni format qoidasi sifatida talab qilmang.
5. **Bo'sh qatorlar** — savollar orasida bo'sh qator bo'lishi tavsiya etiladi, lekin majburiy emas.
6. **Ko'p qatorli savollar** (kod bloklari bilan) qo'llab-quvvatlanadi: savol matnidan keyin variantlar (`A)`) boshlanguncha barcha qatorlar savol qismi hisoblanadi.
7. **Ko'p qatorli variantlar** ham qo'llab-quvvatlanadi: variant qatoridan keyingi keyingi `A)`/`B)`/`C)`/`D)` yoki yangi savol boshlanguncha hammasi shu variantning qismi.

### Misol fayllar

`test_banks/` papkasida ikkita haqiqiy misol fayl mavjud:
- `python_lugat.docx` — raqamli format, kod bloklari bor
- `modul_va_paketlar.docx` — bulletli format

`tests/fixtures/` papkasida unit testlar uchun kichik misollar bo'lishi kerak.

## Validatsiya talablari

Validator quyidagi xatolarni aniqlab, **savol raqami va fayl nomi bilan** bildirsin:

- Variantlari to'rttadan kam yoki ko'p
- To'g'ri javob belgilanmagan (`*` yo'q)
- Bir nechta variant `*` bilan belgilangan
- Variant belgisi A, B, C, D dan boshqa
- Bir xil savol matnli takror savollar
- Savol matni juda qisqa (masalan, 5 belgidan kam) — ehtimoliy parsing xatosi

Xato xabarining namunasi:
```
[XATO] python_lugat.docx, savol #14: To'g'ri javob belgilanmagan (* belgisi yo'q)
[XATO] modul_va_paketlar.docx, savol #7: Faqat 3 ta variant topildi (4 ta kerak)
[OGOHLANTIRISH] python_lugat.docx, savol #22: Savol matni juda qisqa, parsing xatosi bo'lishi mumkin
```

Validatsiya bosqichida xato bo'lsa, generatsiya **boshlanmasin**. Foydalanuvchi avval Word faylni tuzatishi kerak.

## Loyiha tuzilmasi

```
test_generator/
├── CLAUDE.md                    # Bu fayl
├── README.md                    # Foydalanuvchi uchun yo'riqnoma
├── requirements.txt
├── config.yaml                  # Standart sozlamalar
├── .gitignore
│
├── src/
│   ├── __init__.py
│   ├── models.py                # Question, Option, Variant
│   ├── parser.py                # Word fayldan o'qish
│   ├── validator.py             # Savollarni tekshirish
│   ├── generator.py             # Aralashtirish, variant yaratish
│   ├── exporter_docx.py         # Word fayl yaratish
│   ├── exporter_xlsx.py         # Excel javoblar jadvali
│   ├── config.py                # config.yaml ni o'qish
│   ├── constants.py             # Konstantalar
│   └── cli.py                   # CLI buyruqlari
│
├── tests/
│   ├── __init__.py
│   ├── test_parser.py
│   ├── test_validator.py
│   ├── test_generator.py
│   └── fixtures/                # Kichik test fayllar
│
├── test_banks/                  # Foydalanuvchining haqiqiy fayllari
│
└── output/                      # Generatsiya qilingan variantlar (gitignore)
```

## Modullarning mas'uliyat sohasi

- **`models.py`** — Faqat dataclass'lar va ularning metodlari. Hech qanday I/O.
- **`parser.py`** — `.docx` fayldan o'qib, `list[Question]` qaytaradi. Validatsiya qilmaydi, faqat parse qiladi.
- **`validator.py`** — `list[Question]` ni oladi va `list[ValidationError]` qaytaradi. Hech narsa yozmaydi/chop etmaydi (faqat qaytaradi).
- **`generator.py`** — Pure funksiyalar: `list[Question]` → `list[Variant]`. `random.Random(seed)` ishlatadi.
- **`exporter_docx.py`** / **`exporter_xlsx.py`** — Faqat fayl yozish bilan shug'ullanadi.
- **`cli.py`** — Foydalanuvchi bilan muloqot, modullarni birlashtirish, xato xabarlarini chiqarish.

Bu chegaralarni buzmang — masalan, parser ichida `print()` ishlatmang yoki validator ichida fayl yozmang.

## Reproducibility

- Generator har doim `random.Random(seed)` ishlatadi (global `random` emas).
- Birinchi variant `seed = base_seed + 1`, ikkinchisi `seed = base_seed + 2`, va h.k.
- `base_seed` CLI'dan beriladi (default: 42).
- Bir xil seed va bir xil input → har doim bir xil natija.

## Test yozish bo'yicha ko'rsatmalar

- Har bir parser xususiyati uchun fixture fayl + unit test bo'lsin.
- Validator testlari turli xato turlari uchun alohida bo'lsin.
- Generator testlari `seed` orqali deterministik bo'lsin.
- Test fayllari kichik (3-5 savol) — tezkor ishlash uchun.

## Bosqichma-bosqich yo'l xaritasi

Loyiha quyidagi tartibda quriladi. Har bosqichni alohida prompt orqali bajaring:

1. **Skeleton** — papkalar tuzilmasi, `requirements.txt`, virtual muhit, `models.py`
2. **Parser (raqamli format)** — `1. ...` formatini o'qish + unit testlar
3. **Parser (bulletli format va kod bloklari)** — `-` formati va ko'p qatorli savollar
4. **Validator** — barcha xato turlari + xato xabarlari
5. **Generator** — savollar va variantlarni aralashtirish, bir nechta variant
6. **Stratified sampling** — bir nechta mavzudan balansli olish
7. **Exporter (Word)** — variant fayllarini yozish
8. **Exporter (javoblar)** — Word va Excel javoblar fayli
9. **CLI** — `click` orqali buyruqlar, `config.yaml`
10. **Sayqal** — README, logging, end-to-end test

Har bosqichdan keyin git commit qiling.

## Muhim eslatmalar

- **Foydalanuvchi tilini hurmat qiling:** xato xabarlari va README o'zbek tilida bo'lsin.
- **Sodda yechimlarni afzal ko'ring** — bu o'qituvchi uchun vosita, "enterprise" arxitekturaga ehtiyoj yo'q.
- **Format qoidalarini o'zgartirmang** — yuqoridagi format yagona standart. Yangi formatga moslashish o'rniga validator xato bersin.
- **Avval test, keyin kod** (TDD) — ayniqsa parser va validator uchun.
