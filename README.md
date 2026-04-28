# Test Variant Generator

Bu dastur o'qituvchilar uchun mo'ljallangan bo'lib, Word (`.docx`) formatidagi test banklaridan (savollar to'plamidan) tasodifiy aralashtirilgan ko'p variantli testlarni generatsiya qiladi. Shuningdek, dastur barcha yaratilgan variantlarning to'g'ri javoblari kalitini Word va Excel formatlarida avtomatik ravishda tayyorlab beradi.

## Xususiyatlari

- **Formatlarni avtomatik aniqlash:** "1. Savol" kabi raqamli yoki Word avto-numerlash (bullet list) orqali kiritilgan savollarni o'qiydi.
- **Qat'iy validatsiya:** Formatdagi xatoliklarni (masalan, to'g'ri javob belgilanmaganligi yoki noto'g'ri variant harflari ishlatilganligini) aniq savol raqami va fayl nomi bilan ko'rsatadi.
- **Stratified Sampling:** Bir nechta test fayllari kiritilganda, har bir fayldan mutanosib ravishda savollarni tanlab oladi.
- **Har safar yangi variantlar:** Har "Variantlarni yaratish" bosilganda yangi tasodifiy aralashtirish ishlatiladi — bir xil fayllar yuklansa ham har gal turlicha variantlar chiqadi.
- **Javoblar kaliti:** Word va chiroyli Excel formatida javoblar generatsiya qilinadi.

## O'rnatish

Dasturni ishga tushirish uchun Python 3.10 yoki undan yuqori versiyasi o'rnatilgan bo'lishi kerak.

1. Loyihani yuklab oling va papkaga kiring:
   ```bash
   cd variator
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

## Ishlatish

Dastur grafik interfeys (GUI) orqali ishlaydi. Buyruq qatorini bilish shart emas:

```bash
python -m src.gui
```

Oynada:

1. **"Tanlash"** tugmasi orqali bir yoki bir nechta `.docx` test bankini tanlang (yoki fayllarni drop-zonaga tashlang).
2. Sozlamalarni kiriting: variantlar soni, har variantdagi savollar soni (bo'sh qoldirsangiz — barchasi), shrift o'lchami, fan nomi, nazorat turi.
3. Saqlash papkasini tanlang (yoki `config.yaml` dagi standart `output/` ishlatiladi).
4. **"Variantlarni yaratish"** tugmasini bosing — barcha variantlar bitta `Barcha_variantlar.docx` fayliga (har biri yangi sahifadan) yoziladi. Yonida `Javoblar.docx` va `Javoblar.xlsx` ham yaratiladi.
5. Validatsiya xatolari topilsa, alohida oynada savol raqamlari bilan ko'rsatiladi.
6. Tugagandan so'ng natijalar papkasini ochish taklif qilinadi.

## config.yaml

Doimiy ishlatiladigan standart sozlamalarni `config.yaml` faylidan o'qib olinadi:

```yaml
variants_count: 5
# questions_per_variant: 30
output_dir: "output"
```

GUI'dagi maydonlar bu qiymatlardan ustun turadi — `config.yaml` faqat dastur birinchi marta ishga tushganda standart qiymatlarni belgilaydi.
