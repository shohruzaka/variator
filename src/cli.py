"""Buyruq qatori (CLI) interfeysi (9-bosqich).

Bu modul dasturning asosiy kirish nuqtasi bo'lib, foydalanuvchi buyruqlarini
qabul qiladi, `config.yaml` bilan birlashtiradi va barcha modullarni ishlashini
boshqaradi. O'qituvchilar (texnik bo'lmagan foydalanuvchilar) uchun qulay va
tushunarli o'zbekcha xabarlar chiqaradi.
"""

import sys
from pathlib import Path

import click

from src.config import Config
from src.exporter_docx import export_answers_to_docx, export_variants_to_docx
from src.exporter_xlsx import export_answers_to_xlsx
from src.generator import generate_variants
from src.models import Question
from src.parser import parse_docx
from src.validator import Severity, has_errors, validate


@click.command()
@click.argument(
    "files",
    nargs=-1,
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path),
)
@click.option(
    "--count",
    "-c",
    type=int,
    help="Generatsiya qilinadigan variantlar soni (standart qiymat config'dan olinadi).",
)
@click.option(
    "--questions-per-variant",
    "-q",
    type=int,
    help="Har bir variantda nechta savol bo'lishi kerakligi (agar kiritilmasa, barcha savollar olinadi).",
)
@click.option(
    "--seed",
    "-s",
    type=int,
    help="Aralashtirish uchun boshlang'ich raqam (takrorlanuvchanlik uchun).",
)
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    help="Natijalar saqlanadigan papka.",
)
def main(
    files: tuple[Path, ...],
    count: int | None,
    questions_per_variant: int | None,
    seed: int | None,
    output_dir: Path | None,
):
    """Test Variant Generatori.

    Word (.docx) formatdagi test banklaridan ko'p variantli testlar va
    ularning javoblar kalitini yaratadi.
    """
    if not files:
        click.secho(
            "XATO: Hech qanday test fayli ko'rsatilmadi. Kamida bitta .docx fayl bering.",
            fg="red",
            bold=True,
        )
        sys.exit(1)

    # 1. Sozlamalarni o'qish va CLI argumentlari bilan birlashtirish
    cfg = Config.load()
    
    final_count = count if count is not None else cfg.variants_count
    final_qpv = questions_per_variant if questions_per_variant is not None else cfg.questions_per_variant
    final_seed = seed if seed is not None else cfg.base_seed
    final_outdir = output_dir if output_dir is not None else Path(cfg.output_dir)

    click.secho("--- Test Variant Generatori ---", fg="cyan", bold=True)
    click.echo(f"O'qilayotgan fayllar: {', '.join(f.name for f in files)}")

    # 2. Fayllarni o'qish (Parsing)
    all_questions: list[Question] = []
    for file_path in files:
        try:
            qs = parse_docx(file_path)
            all_questions.extend(qs)
        except Exception as e:
            click.secho(
                f"XATO: '{file_path.name}' faylini o'qishda xatolik yuz berdi: {e}",
                fg="red",
            )
            sys.exit(1)

    if not all_questions:
        click.secho("XATO: Kiritilgan fayllardan hech qanday savol topilmadi.", fg="red")
        sys.exit(1)

    click.echo(f"Jami savollar soni: {len(all_questions)}")

    # 3. Validatsiya
    errors = validate(all_questions)
    
    if errors:
        click.echo("\nFayllarni tekshirish natijalari:")
        for err in errors:
            color = "red" if err.severity == Severity.XATO else "yellow"
            click.secho(err.format(), fg=color)
            
        if has_errors(errors):
            click.secho(
                "\n[XATO] Fayllarda xatolar topildi. Iltimos, avval ularni to'g'rilang, "
                "so'ngra qaytadan ishga tushiring. Generatsiya to'xtatildi.",
                fg="red",
                bold=True,
            )
            sys.exit(1)
        else:
            click.secho(
                "\nOgohlantirishlar topildi, lekin ular jarayonni to'xtatmaydi. Davom etyapmiz...",
                fg="yellow",
            )

    # 4. Generatsiya
    click.echo(f"\nVariantlar generatsiya qilinmoqda ({final_count} ta)...")
    variants = generate_variants(
        all_questions,
        count=final_count,
        base_seed=final_seed,
        questions_per_variant=final_qpv,
    )

    # 5. Eksport (Word variantlar va Javoblar)
    click.echo("Fayllarga yozilmoqda...")
    try:
        saved_variants = export_variants_to_docx(variants, final_outdir)
        ans_docx = export_answers_to_docx(variants, final_outdir / "Javoblar.docx")
        ans_xlsx = export_answers_to_xlsx(variants, final_outdir / "Javoblar.xlsx")
    except Exception as e:
        click.secho(f"[XATO] Fayllarni saqlashda xatolik yuz berdi: {e}", fg="red")
        sys.exit(1)

    # Natija
    click.secho(f"\nMUVAFFAQIYATLI YAKUNLANDI! 🎉", fg="green", bold=True)
    click.echo(f"Yaratilgan fayllar ({final_outdir} papkasida):")
    for f in saved_variants:
        click.echo(f"  - {f.name}")
    click.echo(f"  - {ans_docx.name} (Javoblar Word formatida)")
    click.echo(f"  - {ans_xlsx.name} (Javoblar Excel formatida)")


if __name__ == "__main__":
    main()
