"""Loyiha bo'ylab ishlatiladigan konstantalar.

Magic number'lar o'rniga shu yerdan import qilinadi.
"""

# Har bir savolda bo'lishi kerak bo'lgan variant soni.
REQUIRED_OPTIONS_COUNT: int = 4

# Ruxsat etilgan variant harflari.
VALID_OPTION_LETTERS: frozenset[str] = frozenset({"A", "B", "C", "D"})

# Savol matni minimal uzunligi — bundan qisqa bo'lsa,
# ehtimoliy parsing xatosi deb ogohlantirish beriladi.
MIN_QUESTION_TEXT_LENGTH: int = 5
