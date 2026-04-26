# Variator — Test Bank Variant Generator
## CustomTkinter dasturi uchun AI agentga prompt ketma-ketligi

> **Asosiy g'oya:** V1 wireframe — Sidebar + asosiy maydon, gorizontal stepper bilan
> 5 bosqichli workflow: **Yuklash → Tekshirish → Balans → Generatsiya → Eksport**
>
> **Texnologiya:** Python 3.10+, CustomTkinter 5.2+, python-docx, openpyxl
>
> **Til:** UI matni — o'zbek (lotin)
>
> **Rang palitrasi:** Light tema, Indigo aksent (`#4F46E5`)

---

## 📋 Promptlardan qanday foydalanish

1. Promptlarni **tartib bilan** yuboring — har biri oldingisining ustiga quradi
2. Har bir promptdan keyin agentga kod yozish va sinash uchun vaqt bering
3. Agar xato chiqsa — **Tuzatish promptlari** (oxirida) ni ishlating
4. Bir promptda bir maqsad — bo'lib-bo'lib bersangiz natija sifatli bo'ladi

---

## PROMPT 0 — Loyiha skeleti va arxitekturasi

```
Sen Python ekspertisan. CustomTkinter asosida "Variator" deb nomlanuvchi
desktop dasturni qurmoqchimiz. Bu dastur o'qituvchi uchun .docx fayllardan
test savollarini o'qib, ularni aralashtirib, bir nechta variant yaratib
beradigan vosita.

Birinchi qadamda — faqat loyiha SKELETI ni yarat:

Papka tuzilishi:
variator/
├── main.py                   # Entry point
├── requirements.txt          # customtkinter, python-docx, openpyxl, Pillow
├── app/
│   ├── __init__.py
│   ├── config.py             # Ranglar, shriftlar, konstantalar
│   ├── state.py              # AppState — global holat (singleton)
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── main_window.py    # Asosiy oyna (sidebar + content)
│   │   ├── sidebar.py        # Chap panel
│   │   ├── stepper.py        # Yuqoridagi 5-bosqichli stepper
│   │   ├── footer.py         # Pastki "Orqaga / Davom" panel
│   │   └── pages/
│   │       ├── __init__.py
│   │       ├── page_upload.py     # 1-bosqich
│   │       ├── page_validate.py   # 2-bosqich
│   │       ├── page_balance.py    # 3-bosqich
│   │       ├── page_generate.py   # 4-bosqich
│   │       └── page_export.py     # 5-bosqich
│   ├── core/
│   │   ├── __init__.py
│   │   ├── parser.py         # .docx → Question[] (keyinroq)
│   │   ├── validator.py      # Question[] → ValidationReport (keyinroq)
│   │   ├── generator.py      # Variantlarni yaratish (keyinroq)
│   │   └── exporter.py       # .docx / .xlsx eksport (keyinroq)
│   └── models.py             # Question, Variant, Topic dataclasslari

config.py ichida ushbu konstantalar bo'lsin:
- COLOR_ACCENT = "#4F46E5"
- COLOR_ACCENT_HOVER = "#4338CA"
- COLOR_BG = "#FAFAF7"
- COLOR_BG_2 = "#F3F2EC"
- COLOR_INK = "#1A1A1A"
- COLOR_INK_2 = "#4A4A4A"
- COLOR_INK_3 = "#8A8A8A"
- COLOR_OK = "#15803D"
- COLOR_WARN = "#D97706"
- COLOR_ERR = "#B91C1C"
- FONT_FAMILY = "Inter"   (yoki tizimda mavjud san-serif)
- FONT_SIZE_SM = 12, MD = 14, LG = 16, XL = 20, XXL = 26
- WINDOW_W = 1280, WINDOW_H = 820
- SIDEBAR_W = 240
- STEPS = ["Yuklash", "Tekshirish", "Balans", "Generatsiya", "Eksport"]

main.py:
- ctk.set_appearance_mode("light")
- ctk.set_default_color_theme("blue")  (keyin custom override)
- MainWindow yaratib, mainloop ishga tushadi

models.py — quyidagi dataclasslar:
- Question(id, number, text, options:list[str], correct_index:int|None,
           topic:str, source_file:str, has_code:bool, code_block:str|None,
           validation_status:str, validation_message:str|None)
- Topic(name, source_file, questions:list[Question])
- VariantSpec(title, date, duration_min, count, total_per_variant,
              per_topic:dict[str,int], shuffle_questions:bool,
              shuffle_options:bool, seed:str)
- Variant(number, questions:list[Question], answer_key:list[str])

AppState (singleton):
- topics: list[Topic]
- spec: VariantSpec
- variants: list[Variant]
- current_step: int (1..5)
- subscribers: callable[] (state o'zgarganda chaqiriluvchi)
- methods: add_topic(), set_spec(), set_variants(), notify(), subscribe(fn)

main_window.py:
- Grid layout: 2 ustun (sidebar | content), content ichida 3 qator
  (stepper | page area | footer)
- show_page(step:int) — 5 ta sahifani almashtiradi (PageUpload, PageValidate, ...)
- Har sahifa CTkFrame'dan vorislab oladi va .render() metodiga ega

Hozir ichi bo'sh, lekin ishlaydigan skelet bo'lsin — har sahifa o'rtada
"Sahifa N" deb yozilgan placeholder label ko'rsatsin.
Sidebar ichida loyiha nomi "Variator" + bo'sh joy.
Stepper ichida 5 ta dumaloq raqam + qator nom.
Footer ichida "← Orqaga" va "Davom →" tugmalari.

Tugmalar bosilganda current_step o'zgarib, page almashishi kerak.

Kod toza, type-hint bilan, har bir module 200 qatordan oshmasin.
```

---

## PROMPT 1 — Sidebar (chap panel)

```
Endi sidebar.py ni to'liq yoz.

V1 wireframe asosida sidebar ichida (yuqoridan pastga):

1. Logo bloki:
   - 22×22 px indigo kvadrat ichida oq "V" harf
   - Yonida "Variator" sarlavha (FONT_XL bold)

2. "＋ Yangi loyiha" — to'liq enga keng tugma (primary, indigo fon, oq matn)

3. "LOYIHALAR" sarlavha (uppercase, FONT_SM, kulrang)
   Keyin loyihalar ro'yxati. Har biri:
   - Yashil/sariq/qizil status nuqtasi (8×8 doira)
   - Loyiha nomi (FONT_MD)
   - O'ng tomonda — savollar soni (kulrang FONT_SM)
   - Bosilganda highlight (indigo soft fon: #E0E7FF)
   Hozircha mock data:
     [("Ingliz tili — 1-kurs", 50, "ok", True),
      ("Pedagogika asoslari", 32, "warn", False),
      ("Informatika", 78, "ok", False)]

4. "MANBALAR (.DOCX)" sarlavha
   Faollashgan loyihaning fayllari ro'yxati (indent bilan):
   - 📄 ikon + fayl nomi (FONT_SM)
   Hozircha mock: ["lugatlar.docx", "modullar.docx", "grammatika.docx"]

5. Pastida (bottom-anchored):
   - Foydalanuvchi avatar (20×20 doira, ko'k fon) + ismi "U. Karimova"

Sidebar fon rangi: COLOR_BG_2 (#F3F2EC).
O'ng tomonda 1.25px qora chiziq (border).

AppState ga "active_project_id" qo'sh va loyiha bosilganda u o'zgaradi.
Sidebarni AppState.subscribe orqali avtomatik yangilanadigan qil.

Tugma yoki list itemlar bosilganda hozircha faqat console'ga print qil
("Project clicked: Ingliz tili").
```

---

## PROMPT 2 — Stepper (yuqori navigatsiya)

```
stepper.py ni to'liq yoz.

V1 dagi gorizontal 5-bosqichli stepper:

5 ta bosqich: Yuklash, Tekshirish, Balans, Generatsiya, Eksport.

Har bosqich ko'rinishi (3 holat):
- DONE (allaqachon o'tilgan): yashil 36×36 doira ichida ✓ belgisi, ostida nom (oddiy matn)
- ACTIVE (hozirgi): indigo 36×36 doira ichida raqam (oq), ostida nom (BOLD, qora)
- TODO (kelajak): oq doira, kulrang chegara, kulrang raqam, ostida nom (kulrang)

Bosqichlar orasida — ulovchi chiziq:
- DONE va ACTIVE oralig'ida: qora to'liq chiziq
- ACTIVE va TODO oralig'ida: kulrang DASHED chiziq

Stepper joylashuvi:
- Padding: 14px 24px
- Pastida 1.25px qora chiziq (border-bottom)
- Fon: COLOR_BG (#FAFAF7)
- Bosqichlar tartibida joylashtirilgan, oralig'ida flexible spacer (chiziq)

Implementatsiya:
- Stepper(parent, app_state) klassi CTkFrame'dan vorislaydi
- __init__ da 5 ta StepBubble komponent yaratadi (ichki klass)
- StepBubble: doira (CTkLabel + circular shape) + nom labeli
- update() metodi — current_step ga qarab ranglarni qayta hisoblaydi
- AppState ga subscribe bo'lib, current_step o'zgarganda update() chaqiriladi

Bosqich raqamiga bosish bilan o'tish IXTIYORIY (DONE bosqichlarga qaytish mumkin,
TODO bosqichlarga emas — current_step+1 dan oshib o'ta olmaydi).

Esda tut: CustomTkinter da haqiqiy doira chizish uchun CTkCanvas ishlat
yoki yumaloqlik effektini berish uchun yumshoq trick — CTkFrame ga corner_radius=18
beruv (kvadrat 36×36 → doira). Ikkinchisi soddaroq.
```

---

## PROMPT 3 — Footer (pastki navigatsiya)

```
footer.py ni yoz.

V1 dagi pastki panel:
- Padding: 12px 24px
- Yuqorida 1.25px qora chiziq (border-top)
- Fon: COLOR_BG_2

3 ta element gorizontal:
1. CHAP: "← Orqaga" — ghost tugma (chegara qora, fon shaffof, soya yo'q)
2. O'RTA: status matni — kulrang FONT_SM, AppState dan o'qiladi
   Misol: "3 fayl · 50 savol tayyor"
3. O'NG: "Davom →" — primary tugma (indigo)

Bosqichlarga qarab tugmalar matni o'zgaradi:
- 1-bosqich: "← Orqaga" disabled, "Tekshirishga o'tish →"
- 2-bosqich: "← Orqaga" enabled, "Balansga o'tish →"
- 3-bosqich: "← Orqaga" enabled, "Generatsiyani boshlash →"
- 4-bosqich: "← Orqaga" disabled (jarayon davom etadi), "Variantlarni ko'rish →" (faqat tugagach)
- 5-bosqich: "← Orqaga" enabled, "Yangi loyiha" (primary, asosiy oynani reset qiladi)

Status matni har bosqich uchun:
- 1: "{n} fayl · {m} savol topildi"
- 2: "{n} yaroqli savol generatsiyaga tayyor"
- 3: "{count} variant · {per_variant} savoldan · seed: {seed}"
- 4: "{progress}% bajarildi"
- 5: "{count} variant tayyor · {file_count} fayl"

Footer ham AppState'ga subscribe bo'lib, har o'zgarishda yangilanadi.
```

---

## PROMPT 4 — Sahifa 1: Yuklash (Drag & Drop)

```
page_upload.py ni to'liq yoz.

Wireframe asosida 1-bosqich sahifasi:

[Sarlavha]  "1-qadam — Test bankini yuklash" (FONT_XXL, bold)
[Sub]        "Bir yoki bir nechta .docx faylni quyidagi sohaga tashlang.
              Mavzu nomi fayl nomidan avtomatik aniqlanadi." (FONT_MD, kulrang)

[Drop zone] — Asosiy maydon, balandligi flexible:
- Chegara: 2px DASHED qora
- Fon: oq + diagonal striped pattern (light indigo, juda yengil)
- Markazda:
  * Katta strelka ↓ (FONT 64, indigo)
  * "Fayllarni shu yerga tashlang" (FONT_XXL bold)
  * "yoki" (kulrang)
  * "📁 Faylni tanlash" (primary tugma, kattaroq)
  * Pastida — qo'llab-quvvatlash matni (kulrang, kichik):
    "Qo'llab-quvvatlanadi: .docx · raqamli savollar (1., 2.) ·
     bulletlar (-, •) · **bold** belgilari · *A) marker · 'Aniq Javob: C'"

CustomTkinter da haqiqiy DRAG & DROP uchun `tkinterdnd2` paketidan foydalan
(requirements.txt ga qo'sh: tkinterdnd2). Agar mavjud bo'lmasa, fallback —
faqat "Faylni tanlash" tugmasi orqali tkinter.filedialog.askopenfilenames.

Tugma yoki drop bilan fayl(lar) qo'shilganda:
1. self.parser dan parse_docx(filepath) chaqiriladi (hozircha mock — random
   sondagi Question'lar qaytaradi)
2. Topic obyekti yaratiladi (mavzu = fayl nomidan kengaytmasiz, masalan
   "lugatlar.docx" → "Lug'atlar")
3. AppState.add_topic(topic) chaqiriladi
4. Quyidagi "Yuklangan fayllar" qismi yangilanadi

[Yuklangan fayllar] qismi (drop zone tagida):
- Sarlavha: "Yuklangan fayllar (N)" (FONT_LG, bold)
- O'ngda: "Jami: M savol topildi" (kulrang)
- Quyida — kartochkalar gridi (3 ustun):
  Har karta:
   - 240×kichik
   - 📄 ikon + fayl nomi (bold) + "Mavzu: X" (kulrang FONT_SM)
   - O'ng yuqorida — pill: yashil/sariq nuqta + savollar soni
- Oxirida — dashed chegarali "＋ Yana fayl qo'shish" karta

Chiroyli ko'rinish uchun har karta CTkFrame, corner_radius=6, border_width=1.25.
```

---

## PROMPT 5 — Parser (.docx o'qish)

```
core/parser.py ni to'liq yoz. Bu — eng muhim modul.

Vazifa: .docx fayldan Question obyektlari ro'yxatini chiqarib olish.

INPUT FORMAT (real fayllarda uchraydigan):

Variant A — raqamli savollar:
    1. What is the past tense of "go"?
    A) goed
    *B) went
    C) gone
    D) going

Variant B — bulletli:
    - Choose the correct article: "___ apple a day."
      A) a
      B) an
      C) the
      Aniq Javob: B

Variant C — bold belgilari:
    **3.** Quyidagi kod nima qaytaradi?
    ```
    def f(x):
        return x * 2
    print(f(5))
    ```
    A) 5
    *B) 10
    C) 25

PARSER QOIDALARI:

1. python-docx orqali .docx faylni o'qiy. Har paragrafni qatoriga ajrat.
2. Shovqin qatorlarni filtrla:
   - "Конец формы", "Начало формы"
   - Faqat bo'sh joy yoki tab
   - Faqat "—" yoki "..."
3. **...** belgilari paragraf ichida bo'lsa, * larni avtomatik tozala.
4. SAVOL BOSHLANISHI ni aniqlash regex bilan:
   - r"^(\*\*)?(\d+)[\.\)]\s+(.+)" — raqamli (1., 2., 3.))
   - r"^[-•]\s+(.+)" — bulletli
   "Savol matni" — birinchi qatordan keyingi qatorlar HAM savol matni bo'lishi mumkin
   (kod bloklari yoki ko'p qatorli matn) toki birinchi VARIANT (A), B), ...) uchragunicha.
5. KOD BLOKLARI: agar savol va variantlar oralig'ida ``` bilan o'ralgan blok bo'lsa,
   uni Question.code_block ga saqla, has_code=True qil. ``` belgilarini olib tashla.
6. VARIANTLAR ni aniqlash:
   - r"^(\*?)([A-EА-Я])[\)\.]?\s+(.+)" — *B) yoki A. yoki С) ham mumkin
   - * bor-yo'qligi → correct_index ni belgilaydi
   - Variant matni keyingi qatorga ham cho'zilishi mumkin (kod variantlar uchun)
7. JAVOB MARKERI: agar variantlar ichida * yo'q bo'lsa, "Aniq Javob: C" qatori
   r"^Aniq\s+Javob[:\s]+([A-E])" bilan qidir → correct_index ni o'rnat.
8. Topic.name fayl nomidan: filename.docx → "Filename" (kapitalize)
9. Question.id — UUID, Question.number — savol tartibi (1-dan boshlab)

OUTPUT: parse_docx(filepath:str) -> tuple[Topic, list[str]]
  - Topic: o'qilgan savollar bilan
  - list[str]: parsing davomida uchragan ogohlantirishlar
    (masalan: "11-qator: variant marker yo'q, o'tib ketildi")

VALIDATION FLAGSlar parser ichida emas, validator.py da tekshiriladi.
Lekin parser har Question.validation_status ni "unknown" qilib qo'yadi.

Kodga keng test qatorlari yoz — bir nechta dummy .docx (yoki test stringlar)
ustida ishlashini ko'rsat.
```

---

## PROMPT 6 — Sahifa 2: Tekshirish (Validation)

```
core/validator.py va page_validate.py ni yoz.

=== validator.py ===

validate_topics(topics:list[Topic]) -> ValidationReport ni yoz.

Tekshirishlar:
1. NO_OPTIONS — savolda 2 tadan kam variant → "err" status
2. NO_CORRECT — correct_index None → "err" status
3. FEW_OPTIONS — 4 tadan kam variant (lekin 2+) → "warn"
4. DUPLICATE — savol matni boshqa savol bilan deyarli bir xil
   (case-insensitive trim → set, takror topilsa har ikkalasini "warn" qil)
5. EMPTY_OPTION — variantlardan biri bo'sh → "warn"
6. Hech narsa topilmasa → "ok"

Question.validation_status va validation_message ga yoz.

ValidationReport — dataclass:
- total: int
- ok: int, warn: int, err: int
- duplicates: int
- by_topic: dict[str, dict] — har mavzu bo'yicha statistika

=== page_validate.py ===

V1 wireframe 2-bosqich asosida.

Layout — 2 ustun:
[CHAP 70%] — Savollar ro'yxati
[O'NG 30%] — Statistika va filtrlar paneli (fon: COLOR_BG_2)

CHAP qism:

Yuqori qator:
- "Savollar (50)" sarlavha
- 3 ta pill: yashil "47 yaroqli", sariq "2 ogohlantirish", qizil "1 xato"
- O'ngda — qidiruv inputi (CTkEntry, "🔍 qidirish...")

Tablar (mavzular bo'yicha):
- "Hammasi" | "Lug'atlar (18)" | "Modullar (22)" | "Grammatika (10)"
- Faol tab — oq fon, qora chegara, bold
- Tugmalar tarzida (CTkSegmentedButton ham mumkin, lekin matn customlash kerak)

Savollar ro'yxati (CTkScrollableFrame ichida):
Har savol — alohida CTkFrame karta, padding 12px:
- Yuqori: "#1" (indigo, FONT-LG hand-style) | savol matni (bold) | mavzu pill
- Agar status="warn" — chegara va fon sariq tonda (#FEF3C7)
- Agar status="err" — qizil tonda (#FEE2E2)
- Variantlar ro'yxati (indent 22px):
   * To'g'ri javob — yashil bold "★ B) went" + kulrang sub "— to'g'ri javob"
   * Qolganlari — oddiy
- Kod bloki bo'lsa, monospace (Courier) fon va dashed chegara
- WARN/ERR savollarda alohida xato xabari (qizil/sariq matnli)

Mock data:
[
  {n:1, q:'What is the past tense of "go"?',
   opts:['goed','went','gone','going'], correct:1, topic:"Lug'atlar", status:'ok'},
  {n:14, q:'Quyidagi kod nima qaytaradi?',
   opts:['5','10','25','xato'], correct:1, topic:'Modullar', status:'ok',
   code:'def f(x):\n    return x * 2\nprint(f(5))'},
  {n:23, q:'Present perfect qachon ishlatiladi?',
   opts:["o'tgan zamon","natija hozir","kelajak"], correct:1,
   topic:"Grammatika", status:'warn',
   message:'Faqat 3 ta variant topildi (kamida 4 ta kerak).'},
  {n:41, q:'If I ___ rich, I would buy a house.',
   opts:['am','was','were','be'], correct:None, topic:"Grammatika", status:'err',
   message:"To'g'ri javob belgilanmagan."},
]

O'NG qism (statistika paneli):

Sarlavha "Statistika" (FONT_XL bold)
5 ta qator (har biri kichkina karta):
- "Jami o'qilgan" → 50 (yashil pill)
- "Yaroqli" → 47 (yashil)
- "Variant yetishmaydi" → 2 (sariq)
- "Javob belgilanmagan" → 1 (qizil)
- "Takror" → 0 (yashil)

Ajratuvchi chiziq.

Sarlavha "Filtrlar":
- ☑ Faqat yaroqli ko'rsat
- ☐ Xatolarni birinchi
- ☐ Kod bloklarini ajrat

Pastda — moviy sticky-note ko'rinishidagi maslahat:
"💡 Xatolarni tuzatmasdan ham generatsiya qilish mumkin —
   bunda faqat yaroqli savollar ishlatiladi."

CTkScrollableFrame uchun: scrollbar customlanishi qiyin, default qoldir.
```

---

## PROMPT 7 — Sahifa 3: Mavzular bo'yicha balans + sozlash

```
page_balance.py ni yoz.

V1 wireframe 3-bosqich.

Layout — 2 ustun:
[CHAP 60%] — Mavzular balansi
[O'NG 40%] — Variant sozlamalari

=== CHAP qism ===

Sarlavha: "Mavzular bo'yicha balans" (FONT_XXL bold)
Sub: "Har mavzudan necha savol olishni belgilang. Yig'indi → variant hajmi."

Asosiy karta (CTkFrame, padding 16):
Yuqori qator:
- "Variant hajmi: 25 savol" (sarlavha, "25 savol" indigo rangda)
- O'ngda — 2 tugma: "Auto-balans" va "Reset" (pill ko'rinishida)

Har mavzu uchun (AppState.topics dan):
1. Qator yuqorisi:
   - Rangli nuqta (mavzu rangi — har mavzuga unique color berib chiq)
   - Mavzu nomi (FONT_MD bold)
   - Kulrang "/ jami {avail}" matn
   - O'ng tomonda: kichkina input (faqat raqam) + "savol" matni
2. Slider: CTkSlider, 0 dan jami_savol gacha
   - Slider rangi mavzu rangi bilan bog'lanadi
   - Slider qiymati input bilan ikki tomonlama bog'lanadi (callback bilan)

Mavzu ranglari (3 mavzudan ortiq bo'lsa loop qilib):
["#4F46E5", "#0EA5E9", "#F59E0B", "#10B981", "#A855F7", "#DC2626"]

Pastda — ajratuvchi chiziq + jami:
- "Jami:" (chap) | "25 / 50 savol" (o'ng, FONT_XL indigo bold)

Eng pastda — gorizontal proporsional bar (stacked):
- Har mavzu rangi bilan, kengligi proportsional ulushga
- Pastida har segment uchun foiz va nomi (kulrang FONT_SM)

Pastda — sariq sticky-note maslahat:
"Misol: «Lug'atlardan 10 + Modullardan 10 + Grammatikadan 5 = 25 savolli variant»"

=== O'NG qism (Variant sozlamalari) ===

Sarlavha: "Variant sozlamalari" (FONT_LG bold)

Karta ichida (CTkFrame padding 12, gap 12):

1. "Variantlar soni"
   - Input (60×26) + 4 ta preset pill: 4, 10, 30, 50
   - Pill bosilsa input qiymati o'zgaradi

2. "Aralashtirish":
   - ☑ Savollar tartibini aralashtirish
   - ☑ A/B/C/D tartibini aralashtirish
   - ☐ Bir xil savollar variantlar bo'ylab

3. "Reproducibility (seed)"
   - Input (read-only ko'rinish, lekin tahrir mumkin)
   - 🔒 ikon + bugungi sana shabloni "2026-04-26"
   - Pastida kichik kulrang sub: "Bir xil seed → bir xil variantlar"

4. "Sarlavha" (input)
   Default: "Test — Yakuniy nazorat"

5. "Sana" + "Davomiylik" (qator, 2 input)
   Default: bugun + 90 daqiqa

Pastda — moviy sticky-note:
"⚙ Sozlamalar saqlanadi — keyingi safar shablon sifatida ishlatish mumkin."

Hamma o'zgarishlar AppState.spec ga yoziladi (callback orqali).

VAJIB: input bo'sh yoki noto'g'ri formatda bo'lsa, "Davom" tugmasini disable qil.
```

---

## PROMPT 8 — Sahifa 4: Generatsiya jarayoni

```
core/generator.py va page_generate.py ni yoz.

=== generator.py ===

generate_variants(topics:list[Topic], spec:VariantSpec,
                  progress_cb:callable=None) -> list[Variant]

Algoritm:
1. random.Random(spec.seed) — reproducibility
2. Har mavzudan spec.per_topic[topic.name] tasdan random.sample qilib ol
   (faqat status="ok" yoki "warn" lar)
3. spec.count marta variant yarat:
   a. Har variant uchun ALOHIDA seed: f"{spec.seed}-{i}"
   b. Bu seed bilan yangi Random
   c. Mavzu bo'yicha tanlangan savollarni shuffle qil
      (agar shuffle_questions=True)
   d. Har savol nusxasi (deepcopy) — chunki variantlarni aralashtirish kerak,
      asl savolga zarar yetmasin
   e. Agar shuffle_options=True — variantlarda options listni shuffle qil
      (correct_index ni ham yangilab qo'y!)
   f. answer_key listini hisobla — har savol uchun "A","B","C","D" harf
4. Har 5% da progress_cb(percent, message) chaqir

Variant.number 1 dan boshlab.

=== page_generate.py ===

V1 wireframe 4-bosqich.

Layout — markazlashgan, max-width 720:

[Markazda]
- 56px ⚙ ikon (yoki spinner — animatsion)
- "Variantlar yaratilmoqda..." (FONT_XXL bold)
- "Iltimos, kuting. Bu odatda 5-15 sekund davom etadi." (FONT_MD kulrang)

Progress qismi:
- Yuqori qatorda chap: "**19** / 30 variant tayyor"
  o'ng: "~ 4 sekund qoldi" (kulrang)
- Quyida progress bar (CTkProgressBar)
  - Custom rangli — diagonal striped indigo (CTkProgressBar default ham bo'lsa
    OK, lekin balandligi 12px, corner_radius 6px)

Ish bosqichlari (checklist) — CTkFrame ichida:
6 ta qator (har biri):
- ✓ ikon (yashil doira) yoki spinner (loading) yoki bo'sh doira (kutilmoqda)
- Bosqich nomi (mos rangda)
- O'ngda count/holat

Bosqichlar:
1. "Savollarni o'qish (3 fayldan)" → "50/50"
2. "Validatsiya" → "47 yaroqli"
3. "Mavzular bo'yicha tanlash" → "25/variant"
4. "Aralashtirish (seed: 2026-04-26)" → "✓"
5. "Variant fayllarini yaratish" → "19/30"  (active)
6. "Javoblar kalitini yaratish" → "kutilmoqda"

Pastda — "⏸ Bekor qilish" (ghost tugma).

JARAYON THREADING:
- generate_variants ni alohida threading.Thread da ishga tushir
  (UI bloklanmasligi kerak)
- progress_cb dan UI yangilanishi uchun — main thread'ga `after()` orqali
  uzat (CTk thread-safe emas)
- Tugagach AppState.set_variants(...) → 5-sahifaga avtomatik o'tish

Tugagach — bir necha soniya ko'rsatib turib, "Variantlarni ko'rish →"
tugmasi paydo bo'ladi (yoki avtomatik o'tish).
```

---

## PROMPT 9 — Sahifa 5: Variantlar ro'yxati va preview

```
page_variants.py va page_export.py ni alohida yoz.

V1 wireframe 5-bosqichi DOIM 2 ekrandan iborat:
A) Variantlar ro'yxati + preview (page_variants)
B) Eksport opsiyalari (page_export)

5-bosqichda foydalanuvchi tabbar orqali bularni almashtiradi.

Yoki: bir CTkTabview ichida 2 ta tab:
- "Variantlar" (preview)
- "Eksport" (formatlar)

=== A — page_variants.py (Variantlar tab) ===

Layout — 2 ustun:
[CHAP 240px] — Variantlar ro'yxati (CTkScrollableFrame)
[O'NG flex] — Tanlangan variantning preview

CHAP qism:
Yuqorida: "30 variant" (FONT_LG bold) + yashil "tayyor" pill
Quyida — har variant uchun qator:
- 26×26 doira ichida raqam (oq fon, qora chegara)
- "Variant №NN" (bold) + sub "25 savol · seed-N"
- O'ng tomonda 📄 ikon
- Bosilganda highlight (active state)
- Active: indigo soft fon

O'NG qism:
Yuqorida (toolbar):
- "Variant №03 — preview" (FONT_LG bold) + "25 savol" pill
- O'ngda 3 tugma: "📄 .docx ko'rinishida", "🔑 Javoblar", "↓ Yuklab olish" (primary)

Asosiy maydon (kulrang fon #E8E6DF, padding 24):
Markazda — "qog'oz" effekti:
- Oq fon, soft soya (CTkFrame border 1.5 + manual shadow trick yoki rasm)
- max-width 640, padding 36
- Ichki kontent (tinder/document tarzida):
  * Yuqorida "O'ZBEKISTON RESPUBLIKASI OLIY TA'LIM VAZIRLIGI" (kichik bold)
  * "____________ universiteti"
  * "Ingliz tili — Yakuniy nazorat" (FONT_XL bold)
  * "Variant №03 · 26.04.2026 · 90 daqiqa"
  * "F.I.Sh: ______________________________"
  * Ajratuvchi chiziq
  * Birinchi 2-3 ta savol full ko'rinishi (kod bloklari ham)
  * "... 23 ta savol davomi ..." (italic kulrang)

CustomTkinter da haqiqiy "qog'oz" effekti — CTkFrame, fon oq, bg outer kulrang.
Soya — manual chizish kerak (Canvas trick) yoki shunchaki border bilan
qoniqarli ko'rinish bersa bo'ladi.

CHAP'da variant tanlanganda — O'NG'dagi preview yangilanadi.

=== B — page_export.py (Eksport tab) ===

V1 wireframe 6-bosqich (eksport):

Layout — vertikal:

Sarlavha: "Eksport opsiyalari" (FONT_XXL bold)
Sub: "Variantlar tayyor. Qaysi formatda yuklab olishni tanlang." (kulrang)

4 ta katta kartochka (gridda 2×2 yoki 4×1):

Karta 1 — "Variantlar (.docx)" (TAVSIYA — yashil "tavsiya" pill yuqorida o'ng burchakda)
- 32px 📄 ikon
- "30 ta alohida fayl" (sub kulrang)
- Tavsif: "Har bir variant: variant_01.docx ... variant_30.docx"
- 3 ta xususiyat ✓ bilan: "Sarlavha + F.I.Sh maydon", "Sahifa raqamlari", "Kod bloklari Courier New"
- Pastida: ☑ Tanlash | "👁 ko'rish" (ghost)
- Chegara: indigo (TAVSIYA bo'lgani uchun), border 2px

Karta 2 — "Javoblar (alohida)" — 🔑
- "30 ta .docx fayl"
- "variant_01_javoblar.docx ... har bir variant uchun"
- ✓ "Savol № → to'g'ri javob"
- ✓ "O'qituvchi uchun"

Karta 3 — "Umumiy javoblar (.docx)" — 📋
- "1 ta jadval"
- "barcha_javoblar.docx — barcha 30 variant bir jadvalda"
- ✓ "Jadval ko'rinishida", ✓ "Tezkor tekshirish"

Karta 4 — "Excel javoblar (.xlsx)" — 📊
- "1 ta fayl"
- "barcha_javoblar.xlsx — filtrlash va saralash mumkin"
- ✓ "Auto-tekshirish formulalari", ✓ "Statistika"

Pastida — "Yakuniy paket" katta banner:
- Indigo soft fon (#E0E7FF), indigo chegara
- 32px 📦 ikon (chap)
- O'rta: "Yakuniy paket" (bold) + "4 ta format · jami 62 fayl · ~4.2 MB · ZIP"
- O'ng: "↓ Hammasini yuklab olish" (primary, kattaroq)

Tugma bosilganda — filedialog.askdirectory() bilan papka so'rab,
exporter.py orqali fayllar yoziladi va progress dialog ko'rsatadi.
```

---

## PROMPT 10 — Eksport (.docx va .xlsx yozish)

```
core/exporter.py ni to'liq yoz.

4 ta funksiya:

1. export_variant_docx(variant:Variant, spec:VariantSpec, filepath:str)
   python-docx ishlatib variant_NN.docx yarat:
   - Sarlavha (markaz, bold, 14pt):
     "O'ZBEKISTON RESPUBLIKASI OLIY TA'LIM VAZIRLIGI"
     "____________ universiteti"
   - Bo'sh qator
   - Variant sarlavhasi (markaz, bold, 18pt): spec.title
   - Meta qator: "Variant №03   ·   26.04.2026   ·   90 daqiqa"
   - "F.I.Sh: ______________________________"
   - Bo'sh qator
   - Ajratuvchi chiziq
   - Har savol uchun:
     * "1. Savol matni" (bold)
     * Agar code_block bor — Courier New 10pt fon kulrang
     * Variantlar (indent 0.5cm): "A) ...", "B) ..." va h.k.
     * Bo'sh qator (savollar oralig'ida)
   - Footer: sahifa raqami (header section orqali)

2. export_answer_key_docx(variant:Variant, spec:VariantSpec, filepath:str)
   variant_NN_javoblar.docx — yagona jadval:
   - Sarlavha: "Variant №NN — Javoblar kaliti"
   - 5 ustunli jadval: # | Savol qisqacha | To'g'ri javob | Mavzu | Manba
   - Har qator — bitta savol

3. export_all_answers_docx(variants:list[Variant], spec:VariantSpec, filepath:str)
   barcha_javoblar.docx — bitta katta jadval:
   - 1-ustun: "Variant"
   - 2..N-ustun: "Q1", "Q2", ..., "QM" (har savolga ustun)
   - Har qator: variant raqami + javoblar A/B/C/D ketma-ketligi
   - Sahifa landscape, kichikroq font (8-9pt)

4. export_all_answers_xlsx(variants:list[Variant], spec:VariantSpec, filepath:str)
   openpyxl ishlatib:
   - Birinchi sheet: "Javoblar" — yuqoridagi jadval
   - 1-qator (header) — bold, fon kulrang
   - Conditional formatting:
     A → ko'k, B → yashil, C → sariq, D → pushti (juda yengil tonlarda)
   - Avtomatik filtrlar
   - Ikkinchi sheet: "Statistika" — har savol uchun A/B/C/D tarqalishi
   - Auto-fit kengliklar

Yuqoridagi formatlash uchun yordamchi:

```python
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

def add_centered(doc, text, bold=False, size=14):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    run.bold = bold
    run.font.size = Pt(size)

def add_code_block(doc, code:str):
    p = doc.add_paragraph()
    run = p.add_run(code)
    run.font.name = 'Courier New'
    run.font.size = Pt(10)
    # background — XML hack bilan (opsional)
```

Eksport jarayonida progress callback orqali UI'ga yangilanishlarni uzat.

Yakuniy paket uchun — ZIP qilib yig'ish:

5. export_zip_package(variants, spec, output_dir:str) -> str
   - Vaqtinchalik papkada barcha fayllarni yarat
   - zipfile bilan archive qil
   - Final .zip fayl yo'lini qaytar
```

---

## PROMPT 11 — Vizual sayqallash va animatsiyalar

```
Hozir asosiy funksionallik tayyor. Endi UI'ni sayqallash bilan shug'ullan:

1. STEPPER ANIMATSIYALARI:
   - Bosqichdan bosqichga o'tganda doira rangini smooth o'zgartir
     (CTk to'g'ridan-to'g'ri animatsiyani qo'llab-quvvatlamaydi, lekin
      after() bilan har 16ms da rangni interpolyatsiya qilish mumkin)
   - Yangi DONE bosqichda ✓ ikoni "ko'tarilib" chiqadi (3-4 frame)

2. SAHIFA O'TISHLARI:
   - show_page chaqirilganda eski sahifa fade-out (alpha 100→0)
     keyin yangisi fade-in
   - CustomTkinter da alpha qo'llab-quvvatlanmaydi, alternativ:
     widget'ni grid_remove va keyin grid (smooth bo'lmaydi).
     Yoki — joy bo'ldirib qo'yib, asta-sekin almashtirish

3. PROGRESS BAR:
   - Indeterminate animatsiya (generatsiya boshlanganda)
   - CTkProgressBar.start() / .stop() ishlatish

4. TUGMA HOVER:
   - Hozir avtomatik. Lekin ko'rinishini moslashtirish:
     primary tugma hover'da indigo dark (#4338CA)
     ghost tugma hover'da fon ozgina kulrangroq

5. KARTOCHKA HOVER:
   - Yuklash sahifasidagi fayl kartochkalari
   - Eksport sahifasidagi format kartochkalari
   - Hover'da: chegara qoraroq, soya kuchliroq

6. STATUS PILL'LAR:
   - 8×8 dotda CSS-style yumaloqlik
   - Pastel fon + qoraroq matn

7. QO'SHIMCHA — DARK MODE:
   - config.py da APPEARANCE = "light" | "dark" o'zgaruvchisi
   - Sidebar yuqorisida ☀/🌙 tugma — almashtiradi
   - Dark mode uchun barcha COLOR_* qiymatlari uchun MUQOBIL palitra
     (DARK_COLOR_BG = "#1F1D18", DARK_COLOR_INK = "#ECE9DF" va h.k.)
   - ctk.set_appearance_mode() ham almashadi

8. SHRIFTLAR:
   - Inter Variable yoki Inter (mavjud bo'lsa) ishlatish
   - Agar tizimda yo'q — Segoe UI / SF Pro / system default fallback
   - app/assets/fonts/ ga shriftlarni qo'yish va ctk.FontManager bilan ro'yxatga olish

9. IKONLAR:
   - Hozir emoji ishlatilyapti (📄 🔑 ✓). Keyinroq SVG/PNG ikonlar bilan
     almashtirish mumkin (CTkImage orqali)
   - Hozircha emoji qoladi

10. WINDOW MIN-SIZE:
    - main_window'da minsize(1100, 700) belgila — kichikroq bo'lib ketmasin
```

---

## PROMPT 12 — Xato tutish va foydalanuvchi tajribasi

```
Hozir asosiy oqim ishlaydi. Endi error handling va UX qo'shamiz:

1. PARSING XATOLARI:
   - parse_docx ichida try/except — har xatolikni log + report ga qo'sh
   - Foydalanuvchi noto'g'ri formatdagi .docx tashlasa, tushunarli xabar:
     "Bu fayl formatini o'qiy olmadim. Iltimos, namunadagi formatda
      tayyorlangan .docx faylni tashlang. Format namunasini ko'rishni
      istaysizmi?"
   - Modal dialog (CTkToplevel) bilan namuna ko'rsat

2. BO'SH HOLATLAR (empty states):
   - Hech qanday fayl yuklanmaganda — Tekshirish/Balans tablar disable
   - Variantlar generatsiya qilinmaganda — Variantlar tab placeholder:
     "Hali variantlar yaratilmagan. 4-bosqichdan generatsiyani boshlang."

3. XAVFLI HARAKATLAR:
   - "Yangi loyiha" tugmasi (5-bosqichda) — confirm dialog:
     "Joriy loyiha tozalanadi. Davom etamizmi?"
   - "Reset" balansi — confirm

4. UNDO / SAQLASH:
   - Loyihaning joriy holatini avtomatik .json ga saqla:
     ~/.variator/projects/{project_id}.json
   - Dasturi qayta ishga tushganda — oxirgi loyihani tikla
   - "Loyihani saqlash" / "Loyihani ochish" — File menu (yoki sidebar tugma)

5. KEYBOARD SHORTCUTS:
   - Ctrl+O — fayl ochish
   - Ctrl+S — loyihani saqlash
   - Ctrl+G — generatsiya boshlash
   - Ctrl+E — eksport
   - F1 — yordam (modal)
   - Esc — modal yopish

6. TOOLTIP:
   - Bosqich raqamlariga hover qilganda — tushuntirish
   - "Seed" inputiga tooltip: "Bir xil seed → bir xil variantlar"
   - CTk'da rasmiy tooltip yo'q, manual qil:
     CTkLabel bilan toplevel oyna, mouse enter/leave bilan boshqar

7. STATUS BAR:
   - Footer'ning yon tarafida (yoki window bottom'da) global status:
     "Bajarildi: 5 ta savol o'qildi"
     "Xato: fayl topilmadi"
   - 3-4 sek dan keyin avtomatik o'chadi

8. VALIDATION REAL-TIME:
   - Balance sahifasida sliderlar yig'indisi 0 bo'lsa — "Davom" disable
   - Variantlar soni 0 bo'lsa — "Davom" disable
   - Sarlavha bo'sh bo'lsa — input chegarasi qizil + xato matn

9. BREADCRUMBS UCHUN — joriy loyiha nomi window title'da:
   "Variator — Ingliz tili 1-kurs"

10. ABOUT DIALOG:
    - Sidebar pastida "ⓘ Dastur haqida" linki
    - Modal: versiya, mualliflar, lisenziya, link
```

---

## PROMPT 13 — Sinov, tarqatish va paketlash

```
Loyihaning oxirgi bosqichi — testlash va paketlash:

1. UNIT TESTLAR (pytest):
   tests/
   ├── test_parser.py        # 10+ test, har xil .docx formatlar
   ├── test_validator.py     # har validation qoidasi alohida
   ├── test_generator.py     # reproducibility, balance, shuffle
   └── test_exporter.py      # docx va xlsx yozish

   Test fixtures: tests/fixtures/ ichida sample.docx fayllari

2. SAMPLE DATA:
   examples/ papkasida 3-4 ta namuna .docx fayl tayyorla:
   - examples/lugatlar.docx (raqamli format)
   - examples/modullar.docx (kod bloklari bilan)
   - examples/grammatika.docx (bulletli)
   - examples/aralash.docx (har xil format aralash)

3. README.md:
   - Loyihaning maqsadi
   - O'rnatish (pip install -r requirements.txt)
   - Ishga tushirish (python main.py)
   - Foydalanish bo'yicha qisqa qo'llanma (skrinshotlar bilan)
   - Format namunasi (kodda)
   - Hissa qo'shish

4. PYINSTALLER bilan paketlash:
   build.spec faylini tayyorla:
   - One-file executable (.exe Windows uchun, bin Linux/Mac)
   - Ikon: app/assets/icon.ico
   - --windowed (konsol oynasi yo'q)
   - --add-data app/assets/* (resurslar)
   - Yakuniy nom: variator-{platform}.exe

   Komanda: pyinstaller build.spec

5. CI/CD (GitHub Actions):
   .github/workflows/build.yml:
   - Push da pytest run
   - Tag (v*.*.*) da PyInstaller bilan 3 platform uchun build
     (Windows, macOS, Linux)
   - Artifact'larni Release ga upload

6. QO'LLANMA HUJJAT:
   docs/ papkasida:
   - foydalanuvchi-qollanmasi.md (skrinshotlar bilan)
   - format-namunasi.md (.docx qanday ko'rinishi kerakligini batafsil)
   - savol-javob.md (FAQ)

7. KEYINGI YO'NALISHLAR:
   - Cloud sync (loyihalarni serverga saqlash)
   - PDF eksport (printerga to'g'ridan-to'g'ri)
   - Bulk import (papkadan barcha .docx larni avto-yuklash)
   - Question editor (savolni dasturda tahrir qilish)
   - Statistika dashboardi (ko'p loyihalar bo'yicha)
   - Plug-in tizimi (boshqa formatlar uchun parserlar)
```

---

## 🛠 TUZATISH PROMPTLARI

Agar agent xato qilsa yoki noto'g'ri natija bersa:

### A — Layout buzilgan bo'lsa:
```
Sahifa N da elementlar to'g'ri joylashmagan. Wireframe'ga qarab
qaytadan ko'rib chiq:
- [Aniq muammoni ayt: masalan "stepper bosqichlari ustma-ust"]
- [Yoki "kartochkalar gridda emas, qatorda"]

Eslab qol:
- Grid (.grid) layout asosiy. Pack ishlatma.
- columnconfigure va rowconfigure bilan flex (weight=1) sozla.
- CTkFrame'lar nested bo'lganda har birining .grid_propagate(False) muhim.
```

### B — Ranglar noto'g'ri bo'lsa:
```
config.py'dagi ranglarni ishlatayotganingni tekshir.
Hech qanday inline rang yozma — har doim COLOR_* dan foydalan.
Wireframe'da:
- Asosiy fon — COLOR_BG (#FAFAF7) — qog'oz tonida
- Sidebar — COLOR_BG_2 (#F3F2EC) — ozgina to'qroq
- Aksent — COLOR_ACCENT (#4F46E5) — indigo
- Matn — COLOR_INK (#1A1A1A)
```

### C — Threading muammosi:
```
UI thread bloklanmasligi uchun:
- Og'ir operatsiyalar (parse, generate, export) — alohida thread
- threading.Thread(target=fn, daemon=True).start()
- UI yangilash — main thread'ga `self.after(0, lambda: ...)` orqali
- Thread ichida CTk widget metodlarini chaqirma!
```

### D — python-docx muammosi:
```
.docx o'qish/yozishda:
- Document(path) — ochish
- doc.paragraphs — qatorlar (lekin jadval ichidagi bilan ehtiyot bo'l)
- doc.element.body — XML darajasida (kerak bo'lsa)
- Saqlash: doc.save(path)

Run formatlash:
- run.bold, run.italic, run.font.name, run.font.size = Pt(N)
- run.font.color.rgb = RGBColor(0xRR, 0xGG, 0xBB)
```

---

## ✅ Yakuniy tekshiruv

Loyiha tugagach quyidagilarni sinab ko'r:

- [ ] 3 ta namuna .docx faylni yuklash → 50 savol topiladi
- [ ] Tekshirish sahifasida 1-2 ta xato/ogohlantirish to'g'ri ko'rsatiladi
- [ ] Balans sahifasida sliderlar mos ravishda jami 25 ga teng bo'ladi
- [ ] Generatsiya 30 ta variant 5 sekund ichida tayyor bo'ladi
- [ ] Bir xil seed → 2 marta ishga tushirsa, AYNAN bir xil natija
- [ ] Eksport: 30 .docx + 30 javob + 1 umumiy + 1 xlsx fayl yaratiladi
- [ ] Word'da ochib variantni ko'r — sahifa raqamlari va F.I.Sh joyida bormi?
- [ ] Excel'da ochib javoblar jadvalini ko'r — formatlash to'g'rimi?
- [ ] Yangi loyiha yaratish → eski tozalanadimi?
- [ ] Dasturni yopib qayta ochish → oxirgi loyiha tiklanadimi?

---

**Eslatma:** Bu promptlarni AI agentga ketma-ket ber. Har biri tugagach
natijani sinab ko'r va keyingisiga o't. Agent kontekstida muammo bo'lsa,
"oldingi promptga qaytib, X ni qo'shimcha qil" deb so'rasang ham bo'ladi.
