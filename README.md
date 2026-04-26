# Test Variant Generator

Bu dastur o'qituvchilar uchun mo'ljallangan bo'lib, Word (`.docx`) formatidagi test banklaridan (savollar to'plamidan) tasodifiy aralashtirilgan ko'p variantli testlarni generatsiya qiladi. Shuningdek, dastur barcha yaratilgan variantlarning to'g'ri javoblari kalitini Word va Excel formatlarida avtomatik ravishda tayyorlab beradi.

## Xususiyatlari

- **Formatlarni avtomatik aniqlash:** "1. Savol" kabi raqamli yoki Word avto-numerlash (bullet list) orqali kiritilgan savollarni o'qiydi.
- **Qat'iy validatsiya:** Formatdagi xatoliklarni (masalan, to'g'ri javob belgilanmaganligi yoki noto'g'ri variant harflari ishlatilganligini) aniq savol raqami va fayl nomi bilan ko'rsatadi.
- **Stratified Sampling:** Bir nechta test fayllari kiritilganda, har bir fayldan mutanosib ravishda savollarni tanlab oladi.
- **Takrorlanuvchanlik (Reproducibility):** Aralashtirish algoritmi `seed` orqali ishlaydi, bir xil kiruvchi ma'lumotlar bilan har doim bir xil variantlarni olasiz.
- **Javoblar kaliti:** Word va chiroyli Excel formatida javoblar generatsiya qilinadi.

## O'rnatish

Dasturni ishga tushirish uchun Python 3.10 yoki undan yuqori versiyasi o'rnatilgan bo'lishi kerak.

1. Loyihani yuklab oling va papkaga kiring:
   ```bash
   cd test_generator
   ```

2. Virtual muhit (venv) yarating va faollashtiring:
   ```bash
   python -m venv .venv
   # Windows uchun:
   .venv\Scripts\activate
   # macOS/Linux uchun:
   source .venv/bin/activate
   ```

3. Kerakli kutubxonalarni o'rnating:
   ```bash
   pip install -r requirements.txt
   ```

## Test bankini tayyorlash

Dastur faqatgina `.docx` (Word) fayllarini o'qiydi. Fayldagi har bir savol quyidagi formatda yozilgan bo'lishi shart:

```text
1. Python nima?
A) Operatsion tizim
*B) Dasturlash tili
C) O'yin
D) Brauzer
```

**Qoidalar:**
- Har bir savolda aniq 4 ta variant (A, B, C, D) bo'lishi shart.
- To'g'ri javob `*` (yulduzcha) belgisi bilan ko'rsatilishi kerak (A, B, C yoki D ning oldidan).
- Savollar oddiy matn orqali (masalan: `1. `) yoki Word avto-numerlash xususiyati orqali terilishi mumkin.
- Ko'p qatorli savollar (kod bloklari) qo'llab-quvvatlanadi.

## Ishlatish (Grafik interfeys — GUI)

Eng oson usul — grafik oynani ishga tushirish. Buyruq qatorini bilmasangiz ham ishlatishingiz mumkin:

```bash
python -m src.gui
```

Oynada:

1. **"+ Qo'shish"** tugmasi orqali bir yoki bir nechta `.docx` test bankini tanlang.
2. Sozlamalarni kiriting: variantlar soni, har variantdagi savollar soni (bo'sh qoldirsangiz — barchasi), shrift o'lchami.
3. Yaratish usulini tanlang:
   - **🚀 Alohida fayllarga** — har bir variant alohida `Variant_1.docx`, `Variant_2.docx` ... ko'rinishida.
   - **📄 Bitta faylga** — barcha variantlar bitta `Barcha_Variantlar.docx` ichida (har biri yangi sahifadan).
4. Validatsiya xatolari topilsa, alohida oynada savol raqamlari bilan ko'rsatiladi.
5. Tugagandan so'ng natijalar papkasini ochish taklif qilinadi.

> **Eslatma:** Natijalar papkasi `config.yaml` dagi `output_dir` qiymatidan olinadi (standart: `output/`). GUI orqali papkani har safar qayta tanlash imkoni hozircha yo'q — boshqa papka kerak bo'lsa, `config.yaml` ni tahrirlang.

## Ishlatish (Buyruq qatori)

Dasturni eng oddiy ko'rinishda quyidagicha ishga tushirish mumkin:

```bash
python -m src test_banks/mavzu_1.docx
```

Bir nechta fayllardan variantlar generatsiya qilish:

```bash
python -m src test_banks/mavzu_1.docx test_banks/mavzu_2.docx
```

### Qo'shimcha sozlamalar (Bayroqlar)

- `-c, --count`: Nechta variant generatsiya qilinishi (Standart: 5).
- `-q, --questions-per-variant`: Har bir variantda nechta savol bo'lishi (Kiritilmasa, barcha savollar aralashtiriladi).
- `-s, --seed`: Tasodifiylikni boshqarish uchun boshlang'ich raqam (Standart: 42).
- `-o, --output-dir`: Natijalar qaysi papkada saqlanishi (Standart: `output/`).

**Misol:** 10 ta variant yaratish, har bir variantda 20 tadan savol bo'lishi va natijani `mening_variantlarim` papkasiga saqlash:

```bash
python -m src test_banks/mavzu_1.docx -c 10 -q 20 -o mening_variantlarim
```

## config.yaml

Doimiy ishlatiladigan sozlamalarni har safar buyruq qatorida yozmaslik uchun `config.yaml` faylini tahrirlashingiz mumkin:

```yaml
variants_count: 10
questions_per_variant: 25
base_seed: 42
output_dir: "output"
```
