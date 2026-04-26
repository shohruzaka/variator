"""Dasturning grafik interfeysi (GUI) asosiy oynasi."""

import os
import sys
import threading
import tkinter as tk
from dataclasses import dataclass, field
from tkinter import messagebox
from pathlib import Path

from src.config import Config
from src.exporter_docx import export_answers_to_docx, export_variants_to_docx, export_all_variants_to_single_docx
from src.exporter_xlsx import export_answers_to_xlsx
from src.generator import generate_variants
from src.models import Question
from src.parser import parse_docx
from src.validator import Severity, ValidationError, has_errors, validate

import customtkinter as ctk


@dataclass
class FileAnalysis:
    """Bitta fayl tahlili: parse natijasi va validatsiya xatolari."""

    questions: list[Question] = field(default_factory=list)
    errors: list[ValidationError] = field(default_factory=list)
    parse_error: str | None = None

    @property
    def xato_count(self) -> int:
        return sum(1 for e in self.errors if e.severity == Severity.XATO)

    @property
    def warning_count(self) -> int:
        return sum(1 for e in self.errors if e.severity == Severity.OGOHLANTIRISH)

    @property
    def has_problem(self) -> bool:
        """True bo'lsa generatsiya to'xtatilishi kerak."""
        return self.parse_error is not None or self.xato_count > 0

# Asosiy mavzu va rang sozlamalari
ctk.set_appearance_mode("System")  # Yorug' va Qorong'u rejimlarni avtomatik qabul qiladi
ctk.set_default_color_theme("blue")

class VariatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Oyna sozlamalari
        self.title("Variator v1.0")
        self.geometry("1050x650")
        self.minsize(650, 550)

        # Oynani ishga tushganda maksimal o'lchamda (maximized) ochish
        try:
            if sys.platform == "win32":
                self.state("zoomed")
            else:
                self.attributes("-zoomed", True)
        except Exception:
            pass  # MacOS kabi ba'zi muhitlarda xato bermasligi uchun

        self.configure(fg_color=("#F5F7FA", "#1E1F25"))  # Asosiy orqa fon (Light, Dark)

        # Tanlangan fayllar ro'yxatini saqlash uchun
        self.selected_files: list[Path] = []
        # Har bir fayl uchun parse + validatsiya natijalarining keshi
        self.file_analysis: dict[Path, FileAnalysis] = {}

        # Generatsiya qilinuvchi papkani saqlash uchun
        self.output_dir: Path | None = None

        # Faqat raqam kiritilishini ta'minlovchi validator
        self.vcmd = (self.register(self._validate_int), '%P')

        # UI qismlarini qurish
        self._setup_ui()

    def _validate_int(self, P: str) -> bool:
        """Faqat raqam va bo'sh satr kiritilishiga ruxsat beradi."""
        return P == "" or P.isdigit()

    def _setup_ui(self):
        # Asosiy Grid sozlamalari (2 ta ustun, 2 ta qator)
        self.grid_columnconfigure(0, weight=3)  # Fayl hududi (kengroq)
        self.grid_columnconfigure(1, weight=2)  # Sozlamalar hududi (torroq)
        self.grid_rowconfigure(0, weight=1)  # Asosiy hudud (kengayuvchan)
        self.grid_rowconfigure(1, weight=0)  # Tugma hududi

        # ==================== 1. Fayl tanlash hududi ====================
        self.file_frame = ctk.CTkFrame(self, fg_color=("#FFFFFF", "#2A2B32"), border_color=("#E5E7EB", "#3F3F46"), border_width=1, corner_radius=16)
        self.file_frame.grid(row=0, column=0, rowspan=2, padx=(30, 15), pady=30, sticky="nsew")
        self.file_frame.grid_columnconfigure(0, weight=1)
        self.file_frame.grid_rowconfigure(1, weight=1)  # Ro'yxat cho'zilishi uchun

        # Sarlavha va tugmalar uchun yordamchi frame
        self.file_header = ctk.CTkFrame(self.file_frame, fg_color="transparent")
        self.file_header.grid(row=0, column=0, padx=24, pady=(24, 12), sticky="ew")
        self.file_header.grid_columnconfigure(0, weight=1)

        self.file_label = ctk.CTkLabel(self.file_header, text="Test fayllarini tanlang (.docx)", font=("Inter", 20, "bold"), text_color=("#1A1B1E", "#F1F3F5"))
        self.file_label.grid(row=0, column=0, sticky="w")

        self.btn_group = ctk.CTkFrame(self.file_header, fg_color="transparent")
        self.btn_group.grid(row=0, column=1, sticky="e")

        self.select_btn = ctk.CTkButton(self.btn_group, text="Qo'shish", width=130, height=36, command=self.select_files, fg_color=("#4C6EF5", "#7C9CFF"), hover_color=("#3B5BDB", "#5C7CFA"), text_color="#FFFFFF", font=("Inter", 14, "bold"), corner_radius=12)
        self.select_btn.pack(side="left", padx=(0, 12))

        self.clear_btn = ctk.CTkButton(self.btn_group, text="Tozalash", width=110, height=36, fg_color=("#EF4444", "#E03131"), hover_color=("#DC2626", "#C92A2A"), text_color="#FFFFFF", font=("Inter", 14, "bold"), corner_radius=12, command=self.clear_files)
        self.clear_btn.pack(side="left")

        self.file_listbox = ctk.CTkScrollableFrame(self.file_frame, fg_color="transparent", corner_radius=0)
        self.file_listbox.grid(row=1, column=0, padx=24, pady=(0, 24), sticky="nsew")

        # ==================== Statistika paneli ====================
        self.stats_frame = ctk.CTkFrame(self.file_frame, fg_color=("#F3F4F6", "#374151"), corner_radius=10)
        self.stats_frame.grid(row=2, column=0, padx=24, pady=(0, 24), sticky="ew")
        self.stats_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.stat_files_lbl = ctk.CTkLabel(self.stats_frame, text="Jami fayllar: 0", font=("Inter", 13, "bold"), text_color=("#374151", "#D1D5DB"))
        self.stat_files_lbl.grid(row=0, column=0, pady=12, padx=10)

        self.stat_qs_lbl = ctk.CTkLabel(self.stats_frame, text="Jami savollar: 0", font=("Inter", 13, "bold"), text_color=("#374151", "#D1D5DB"))
        self.stat_qs_lbl.grid(row=0, column=1, pady=12, padx=10)

        self.stat_err_lbl = ctk.CTkLabel(self.stats_frame, text="Xatoliklar: 0", font=("Inter", 13, "bold"), text_color=("#10B981", "#34D399"))
        self.stat_err_lbl.grid(row=0, column=2, pady=12, padx=10)

        self._update_file_listbox()

        # ==================== 2. Sozlamalar paneli ====================
        self.settings_frame = ctk.CTkFrame(self, fg_color=("#FFFFFF", "#2A2B32"), border_color=("#E5E7EB", "#3F3F46"), border_width=1, corner_radius=16)
        self.settings_frame.grid(row=0, column=1, padx=(15, 30), pady=(30, 15), sticky="nsew")
        self.settings_frame.grid_columnconfigure(0, weight=1)

        self.settings_title = ctk.CTkLabel(self.settings_frame, text="Generatsiya sozlamalari", font=("Inter", 18, "bold"), text_color=("#1A1B1E", "#F1F3F5"))
        self.settings_title.grid(row=0, column=0, padx=24, pady=(24, 16), sticky="w")

        self.count_label = ctk.CTkLabel(self.settings_frame, text="Variantlar soni:", text_color=("#6B7280", "#A1A1AA"), font=("Inter", 14))
        self.count_label.grid(row=1, column=0, padx=24, pady=(4, 4), sticky="w")
        self.count_entry = ctk.CTkEntry(self.settings_frame, fg_color=("#F5F7FA", "#1E1F25"), border_color=("#E5E7EB", "#3F3F46"), text_color=("#1A1B1E", "#F1F3F5"), height=36, font=("Inter", 14), corner_radius=8, validate="key", validatecommand=self.vcmd)
        self.count_entry.insert(0, "5")
        self.count_entry.grid(row=2, column=0, padx=24, pady=(0, 16), sticky="ew")

        self.q_label = ctk.CTkLabel(self.settings_frame, text="Savollar soni (bo'sh = barchasi):", text_color=("#6B7280", "#A1A1AA"), font=("Inter", 14))
        self.q_label.grid(row=3, column=0, padx=24, pady=(4, 4), sticky="w")
        self.q_entry = ctk.CTkEntry(self.settings_frame, fg_color=("#F5F7FA", "#1E1F25"), border_color=("#E5E7EB", "#3F3F46"), text_color=("#1A1B1E", "#F1F3F5"), height=36, font=("Inter", 14), corner_radius=8, validate="key", validatecommand=self.vcmd)
        self.q_entry.insert(0, "20")
        self.q_entry.grid(row=4, column=0, padx=24, pady=(0, 16), sticky="ew")

        self.font_label = ctk.CTkLabel(self.settings_frame, text="Shrift o'lchami:", text_color=("#6B7280", "#A1A1AA"), font=("Inter", 14))
        self.font_label.grid(row=5, column=0, padx=24, pady=(4, 4), sticky="w")
        self.font_entry = ctk.CTkEntry(self.settings_frame, fg_color=("#F5F7FA", "#1E1F25"), border_color=("#E5E7EB", "#3F3F46"), text_color=("#1A1B1E", "#F1F3F5"), height=36, font=("Inter", 14), corner_radius=8, validate="key", validatecommand=self.vcmd)
        self.font_entry.insert(0, "12")
        self.font_entry.grid(row=6, column=0, padx=24, pady=(0, 16), sticky="ew")

        self.out_label = ctk.CTkLabel(self.settings_frame, text="Saqlash papkasi:", text_color=("#6B7280", "#A1A1AA"), font=("Inter", 14))
        self.out_label.grid(row=7, column=0, padx=24, pady=(4, 4), sticky="w")
        
        self.out_frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        self.out_frame.grid(row=8, column=0, padx=24, pady=(0, 24), sticky="ew")
        self.out_frame.grid_columnconfigure(0, weight=1)
        
        self.out_entry = ctk.CTkEntry(self.out_frame, fg_color=("#F5F7FA", "#1E1F25"), border_color=("#E5E7EB", "#3F3F46"), text_color=("#1A1B1E", "#F1F3F5"), height=36, font=("Inter", 12), corner_radius=8)
        self.out_entry.insert(0, "Standart (Natijalar papkasi)")
        self.out_entry.configure(state="readonly")
        self.out_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        
        self.out_btn = ctk.CTkButton(self.out_frame, text="Tanlash", width=70, height=36, corner_radius=8, fg_color=("#4C6EF5", "#7C9CFF"), hover_color=("#3B5BDB", "#5C7CFA"), text_color="#FFFFFF", font=("Inter", 13, "bold"), command=self.select_output_dir)
        self.out_btn.grid(row=0, column=1)

        # ==================== 3. Harakat (Action) hududi ====================
        self.action_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.action_frame.grid(row=1, column=1, padx=(15, 30), pady=(0, 30), sticky="ew")
        self.action_frame.grid_columnconfigure(0, weight=1)

        self.generate_btn = ctk.CTkButton(self.action_frame, text="Alohida fayllarga", font=("Inter", 16, "bold"), height=48, corner_radius=14, fg_color=("#4C6EF5", "#7C9CFF"), hover_color=("#3B5BDB", "#5C7CFA"), text_color="#FFFFFF", command=lambda: self.start_generation(single_file=False))
        self.generate_btn.grid(row=0, column=0, pady=(0, 12), sticky="ew")

        self.generate_single_btn = ctk.CTkButton(self.action_frame, text="Bitta faylga", font=("Inter", 16, "bold"), height=48, corner_radius=14, fg_color=("#4C6EF5", "#7C9CFF"), hover_color=("#3B5BDB", "#5C7CFA"), text_color="#FFFFFF", command=lambda: self.start_generation(single_file=True))
        self.generate_single_btn.grid(row=1, column=0, pady=(0, 12), sticky="ew")

        self.progress_bar = ctk.CTkProgressBar(self.action_frame, mode="determinate", fg_color=("#E5E7EB", "#3F3F46"), progress_color=("#4C6EF5", "#7C9CFF"), height=6)
        self.progress_bar.grid(row=2, column=0, pady=(8, 0), sticky="ew")
        self.progress_bar.set(0)
        self.progress_bar.grid_remove()  # Boshida yashirin turadi

    def select_files(self):
        filenames = ctk.filedialog.askopenfilenames(
            title="Test banklarini tanlang",
            filetypes=[("Word fayllar", "*.docx")]
        )
        if filenames:
            for f in filenames:
                path_obj = Path(f)
                if path_obj not in self.selected_files:
                    self.selected_files.append(path_obj)
                    self.file_analysis[path_obj] = self._analyze_file(path_obj)
            self._update_file_listbox()

    def select_output_dir(self):
        folder = ctk.filedialog.askdirectory(title="Saqlash papkasini tanlang")
        if folder:
            self.output_dir = Path(folder)
            self.out_entry.configure(state="normal")
            self.out_entry.delete(0, "end")
            self.out_entry.insert(0, str(self.output_dir.resolve()))
            self.out_entry.configure(state="readonly")

    def _analyze_file(self, path: Path) -> FileAnalysis:
        """Faylni parse qiladi va validatsiya qiladi.

        Parse paytida xatolik bo'lsa, `parse_error` to'ldiriladi va
        bo'sh savollar ro'yxati qaytariladi. UI bu holatni alohida
        ko'rsatishi mumkin.
        """
        try:
            questions = parse_docx(path)
        except Exception as exc:  # docx fayli buzilgan yoki o'qib bo'lmasa
            return FileAnalysis(parse_error=str(exc))
        errors = validate(questions)
        return FileAnalysis(questions=questions, errors=errors)

    def _update_file_listbox(self):
        # Avvalgi ro'yxatni tozalash
        for widget in self.file_listbox.winfo_children():
            widget.destroy()

        if not self.selected_files:
            lbl = ctk.CTkLabel(self.file_listbox, text="Fayllar ro'yxati bo'sh. Yuqoridagi 'Qo'shish' tugmasini bosing.", text_color=("#6B7280", "#A1A1AA"), font=("Inter", 14))
            lbl.pack(pady=40)
            self._update_statistics()
            return

        for f in self.selected_files:
            self._build_file_card(f)
            
        self._update_statistics()

    def _update_statistics(self):
        """Statistika panelini joriy ma'lumotlar bilan yangilaydi."""
        total_files = len(self.selected_files)
        total_questions = sum(len(a.questions) for a in self.file_analysis.values() if a.parse_error is None)
        parse_errors = sum(1 for a in self.file_analysis.values() if a.parse_error is not None)
        validation_errors = sum(a.xato_count for a in self.file_analysis.values() if a.parse_error is None)
        total_errors = parse_errors + validation_errors

        self.stat_files_lbl.configure(text=f"Jami fayllar: {total_files}")
        self.stat_qs_lbl.configure(text=f"Jami savollar: {total_questions}")

        if total_errors > 0:
            self.stat_err_lbl.configure(text=f"Xatoliklar: {total_errors}", text_color=("#EF4444", "#F87171"))
        else:
            self.stat_err_lbl.configure(text=f"Xatoliklar: 0", text_color=("#10B981", "#34D399"))

    def _build_file_card(self, f: Path) -> None:
        """Bitta fayl uchun card yaratadi: holatga qarab yashil/qizil chegara."""
        analysis = self.file_analysis.get(f) or FileAnalysis()
        is_bad = analysis.has_problem
        border_color = ("#EF4444", "#F87171") if is_bad else ("#E5E7EB", "#3F3F46")
        status_text, status_color = self._status_for(analysis)
        clickable = bool(analysis.errors) or analysis.parse_error is not None

        card = ctk.CTkFrame(
            self.file_listbox,
            fg_color=("#FFFFFF", "#2A2B32"),
            border_color=border_color,
            border_width=1,
            corner_radius=12,
        )
        card.pack(fill="x", pady=3, padx=8, ipady=2)
        card.grid_columnconfigure(1, weight=1)

        info = ctk.CTkFrame(card, fg_color="transparent")
        info.grid(row=0, column=0, sticky="ew", padx=(16, 0), pady=4)
        info.grid_columnconfigure(0, weight=1)

        name_lbl = ctk.CTkLabel(
            info,
            text=f.name,
            font=("Inter", 15, "bold"),
            text_color=("#1A1B1E", "#F1F3F5"),
            anchor="w",
            height=20,
        )
        name_lbl.grid(row=0, column=0, sticky="w", pady=(2, 0))

        status_lbl = ctk.CTkLabel(
            info,
            text=status_text,
            font=("Inter", 11),
            text_color=status_color,
            anchor="w",
            height=16,
        )
        status_lbl.grid(row=1, column=0, sticky="w", pady=(0, 2))

        del_btn = ctk.CTkButton(
            card,
            text="O'chirish",
            width=70,
            height=28,
            font=("Inter", 12, "bold"),
            corner_radius=8,
            fg_color="transparent",
            border_width=1,
            border_color=("#E5E7EB", "#3F3F46"),
            hover_color=("#F5F7FA", "#3F3F46"),
            text_color=("#6B7280", "#A1A1AA"),
            command=lambda p=f: self.remove_file(p),
        )
        del_btn.grid(row=0, column=2, padx=(10, 14), pady=4)

        if clickable:
            handler = lambda _e, p=f: self._show_file_errors(p)
            for w in (card, info, name_lbl, status_lbl):
                w.bind("<Button-1>", handler)
                try:
                    w.configure(cursor="hand2")
                except (tk.TclError, ValueError):
                    pass

    def _status_for(self, analysis: FileAnalysis) -> tuple[str, tuple[str, str]]:
        """Card pastki qatorida ko'rsatiladigan matn va rangni qaytaradi."""
        if analysis.parse_error is not None:
            return ("Faylni o'qib bo'lmadi", ("#EF4444", "#F87171"))
        xato = analysis.xato_count
        if xato > 0:
            return (f"{xato} ta xatolik (ko'rish uchun bosing)", ("#EF4444", "#F87171"))
        warnings = analysis.warning_count
        question_count = len(analysis.questions)
        if warnings > 0:
            return (
                f"{question_count} ta savol · {warnings} ta ogohlantirish",
                ("#F59E0B", "#FBBF24"),
            )
        return (f"{question_count} ta savol", ("#10B981", "#34D399"))

    def _show_file_errors(self, path: Path) -> None:
        """Faylga tegishli xatolar va ogohlantirishlarni alohida oynada ko'rsatadi."""
        analysis = self.file_analysis.get(path)
        if analysis is None:
            return
        if analysis.parse_error is not None:
            messagebox.showerror(
                "Faylni o'qib bo'lmadi",
                f"{path.name}\n\n{analysis.parse_error}",
            )
            return
        if not analysis.errors:
            return
        self._show_validation_errors(analysis.errors)

    def remove_file(self, file_path: Path):
        if file_path in self.selected_files:
            self.selected_files.remove(file_path)
            self.file_analysis.pop(file_path, None)
            self._update_file_listbox()

    def clear_files(self):
        self.selected_files.clear()
        self.file_analysis.clear()
        self._update_file_listbox()

    def start_generation(self, single_file: bool = False):
        # 1. Tanlangan fayllarni tekshirish
        if not self.selected_files:
            messagebox.showwarning("Ogohlantirish", "Iltimos, kamida bitta test faylini tanlang!")
            return

        # Fayllar tahlilida xato bormi? Bo'lsa, generatsiyani boshlamaymiz.
        bad_files = [f for f in self.selected_files
                     if (a := self.file_analysis.get(f)) and a.has_problem]
        if bad_files:
            names = ", ".join(f.name for f in bad_files)
            messagebox.showerror(
                "Xato",
                "Quyidagi fayllarda xatolik bor — avval tuzating yoki ro'yxatdan olib tashlang:\n\n"
                f"{names}",
            )
            return

        # 2. Sozlamalarni tekshirish
        try:
            count = int(self.count_entry.get())
        except ValueError:
            messagebox.showerror("Xato", "Variantlar soni butun son bo'lishi kerak!")
            return

        q_text = self.q_entry.get().strip()
        qpv = None
        if q_text:
            try:
                qpv = int(q_text)
            except ValueError:
                messagebox.showerror("Xato", "Savollar soni butun son bo'lishi kerak!")
                return
                
        try:
            font_size = int(self.font_entry.get())
        except ValueError:
            messagebox.showerror("Xato", "Shrift o'lchami butun son bo'lishi kerak!")
            return

        # 3. Tugmani bloklash va jarayonni fonda boshlash
        self.generate_btn.configure(state="disabled", text="Tayyorlanmoqda... 0%")
        self.generate_single_btn.configure(state="disabled", text="Tayyorlanmoqda... 0%")
        self.progress_bar.grid()  # Progress barni ko'rsatish
        self.progress_bar.set(0)
        threading.Thread(target=self._run_generation_task, args=(count, qpv, font_size, single_file), daemon=True).start()

    def _update_progress(self, percent: int):
        """Generatsiya foizini yangilaydi."""
        text = f"Tayyorlanmoqda... {percent}%"
        self.generate_btn.configure(text=text)
        self.generate_single_btn.configure(text=text)
        self.progress_bar.set(percent / 100.0)

    def _run_generation_task(self, count: int, qpv: int | None, font_size: int, single_file: bool):
        """Generatsiyani alohida thread'da bajaradi."""
        try:
            self.after(0, lambda: self._update_progress(5))
            cfg = Config.load()
            output_dir = self.output_dir if self.output_dir else Path(cfg.output_dir)

            # Parsing — fayl qo'shilganda allaqachon bajarilgan, keshdan olamiz.
            all_questions: list[Question] = []
            for f in self.selected_files:
                analysis = self.file_analysis.get(f)
                if analysis is None or analysis.parse_error is not None:
                    # Yangidan tahlil qilamiz (ehtiyot uchun).
                    analysis = self._analyze_file(f)
                    self.file_analysis[f] = analysis
                if analysis.parse_error is not None:
                    self.after(0, lambda p=f, err=analysis.parse_error:
                               messagebox.showerror("Faylni o'qib bo'lmadi",
                                                    f"{p.name}\n\n{err}"))
                    return
                all_questions.extend(analysis.questions)

            self.after(0, lambda: self._update_progress(15))

            if not all_questions:
                self.after(0, lambda: messagebox.showerror("Xato", "Kiritilgan fayllardan hech qanday savol topilmadi."))
                return

            # Yakuniy validatsiya — fayllararo takrorlanishni ham tutadi.
            errors = validate(all_questions)
            if has_errors(errors):
                self.after(0, lambda: self._show_validation_errors(errors))
                return

            self.after(0, lambda: self._update_progress(25))

            # Generatsiya
            variants = generate_variants(
                all_questions,
                count=count,
                base_seed=cfg.base_seed,
                questions_per_variant=qpv
            )

            self.after(0, lambda: self._update_progress(35))

            def progress_cb(current: int, total: int):
                pct = 35 + int((current / total) * 55) # 35% dan 90% gacha dinamik yangilash
                self.after(0, lambda: self._update_progress(pct))

            # Eksport
            if single_file:
                export_all_variants_to_single_docx(variants, output_dir, font_size=font_size, progress_cb=progress_cb)
            else:
                export_variants_to_docx(variants, output_dir, font_size=font_size, progress_cb=progress_cb)
            
            self.after(0, lambda: self._update_progress(95))
            export_answers_to_docx(variants, output_dir / "Javoblar.docx")
            export_answers_to_xlsx(variants, output_dir / "Javoblar.xlsx")
            self.after(0, lambda: self._update_progress(100))

            # Muvaffaqiyat xabari
            self.after(0, lambda: self._show_success(output_dir))

        except Exception as e:
            self.after(0, lambda err=e: messagebox.showerror("Kutilmagan xato", str(err)))
        finally:
            # UI ni asliga qaytarish
            self.after(0, self._reset_action_ui)

    def _reset_action_ui(self):
        self.progress_bar.grid_remove()
        self.generate_btn.configure(state="normal", text="Alohida fayllarga")
        self.generate_single_btn.configure(state="normal", text="Bitta faylga")

    def _show_validation_errors(self, errors):
        err_window = ctk.CTkToplevel(self)
        err_window.title("Fayllarda xatolik topildi")
        err_window.geometry("750x550")
        err_window.minsize(600, 450)
        err_window.grab_set()  # Oynani modal qilish (faqat shu oynaga bosish mumkin)
        err_window.configure(fg_color=("#F5F7FA", "#1E1F25"))

        # Sarlavha hududi
        header_frame = ctk.CTkFrame(err_window, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(30, 15))

        title_lbl = ctk.CTkLabel(header_frame, text="Xatoliklar aniqlandi", font=("Inter", 22, "bold"), text_color=("#EF4444", "#F87171"))
        title_lbl.pack(anchor="w")

        sub_lbl = ctk.CTkLabel(header_frame, text="Generatsiyani davom ettirish uchun avval quyidagi xatolarni Word faylida to'g'rilang.", font=("Inter", 14), text_color=("#6B7280", "#A1A1AA"))
        sub_lbl.pack(anchor="w", pady=(5, 0))

        # Xatolar ro'yxati (Scrollable Frame)
        scroll_frame = ctk.CTkScrollableFrame(err_window, fg_color="transparent", corner_radius=0)
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        for err in errors:
            is_fatal = err.severity == Severity.XATO
            
            # Darajaga qarab ranglarni tanlash
            bg_color = ("#FFFFFF", "#2A2B32")
            border_color = ("#FCA5A5", "#EF4444") if is_fatal else ("#FDE68A", "#F59E0B")
            badge_bg = ("#FEE2E2", "#7F1D1D") if is_fatal else ("#FEF3C7", "#78350F")
            badge_fg = ("#991B1B", "#FECACA") if is_fatal else ("#92400E", "#FDE68A")
            badge_text = " XATO " if is_fatal else " OGOHLANTIRISH "

            # Har bir xato uchun alohida Card
            card = ctk.CTkFrame(scroll_frame, fg_color=bg_color, border_color=border_color, border_width=1, corner_radius=12)
            card.pack(fill="x", padx=10, pady=6)

            # Card'ning tepa qismi: Fayl nomi va Savol raqami
            top_layout = ctk.CTkFrame(card, fg_color="transparent")
            top_layout.pack(fill="x", padx=16, pady=(12, 4))

            file_lbl = ctk.CTkLabel(top_layout, text=f"{err.source_file}   •   Savol #{err.question_number}", font=("Inter", 13, "bold"), text_color=("#6B7280", "#A1A1AA"))
            file_lbl.pack(side="left")

            badge = ctk.CTkLabel(top_layout, text=badge_text, font=("Inter", 11, "bold"), fg_color=badge_bg, text_color=badge_fg, corner_radius=6, height=24)
            badge.pack(side="right")

            # Asosiy xato xabari (Wraplength uzun matnni ekranga sig'diradi)
            msg_lbl = ctk.CTkLabel(card, text=err.message, font=("Inter", 15), text_color=("#1A1B1E", "#F1F3F5"), justify="left", wraplength=600)
            msg_lbl.pack(anchor="w", padx=16, pady=(0, 12))
            
        # Yopish tugmasi
        btn_frame = ctk.CTkFrame(err_window, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=(0, 30))

        ok_btn = ctk.CTkButton(btn_frame, text="Tushunarli", font=("Inter", 15, "bold"), height=44, corner_radius=12, fg_color=("#4C6EF5", "#7C9CFF"), hover_color=("#3B5BDB", "#5C7CFA"), text_color="#FFFFFF", command=err_window.destroy)
        ok_btn.pack(side="right")

    def _show_success(self, output_dir: Path):
        """CustomTkinter uslubidagi chiroyli muvaffaqiyat oynasi."""
        succ_window = ctk.CTkToplevel(self)
        succ_window.title("Muvaffaqiyatli")
        succ_window.geometry("450x220")
        succ_window.resizable(False, False)
        succ_window.grab_set()
        succ_window.configure(fg_color=("#FFFFFF", "#2A2B32"))

        msg_lbl = ctk.CTkLabel(succ_window, text="Variantlar muvaffaqiyatli yaratildi!", font=("Inter", 16, "bold"), text_color=("#10B981", "#34D399"))
        msg_lbl.pack(pady=(40, 0))

        sub_lbl = ctk.CTkLabel(succ_window, text="Natijalar saqlangan papkani ochishni xohlaysizmi?", font=("Inter", 13), text_color=("#6B7280", "#A1A1AA"))
        sub_lbl.pack(pady=(5, 20))

        btn_frame = ctk.CTkFrame(succ_window, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=(0, 20))
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        def on_yes():
            succ_window.destroy()
            if sys.platform == "win32":
                os.startfile(output_dir)
            elif sys.platform == "darwin":
                import subprocess
                subprocess.Popen(["open", str(output_dir)])
            else:
                import subprocess
                subprocess.Popen(["xdg-open", str(output_dir)])

        no_btn = ctk.CTkButton(btn_frame, text="Yo'q", width=120, height=36, corner_radius=8, fg_color=("#F3F4F6", "#374151"), hover_color=("#E5E7EB", "#4B5563"), text_color=("#374151", "#D1D5DB"), font=("Inter", 14), command=succ_window.destroy)
        no_btn.grid(row=0, column=0, padx=10, sticky="e")

        yes_btn = ctk.CTkButton(btn_frame, text="Ochish", width=120, height=36, corner_radius=8, fg_color=("#10B981", "#059669"), hover_color=("#059669", "#047857"), text_color="#FFFFFF", font=("Inter", 14, "bold"), command=on_yes)
        yes_btn.grid(row=0, column=1, padx=10, sticky="w")

if __name__ == "__main__":
    app = VariatorApp()
    app.mainloop()