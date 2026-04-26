"""Dasturning grafik interfeysi (GUI) asosiy oynasi."""

import os
import sys
import threading
import tkinter as tk
from tkinter import messagebox
from pathlib import Path

from src.config import Config
from src.exporter_docx import export_answers_to_docx, export_variants_to_docx, export_all_variants_to_single_docx
from src.exporter_xlsx import export_answers_to_xlsx
from src.generator import generate_variants
from src.parser import parse_docx
from src.validator import has_errors, validate

import customtkinter as ctk

# Asosiy mavzu va rang sozlamalari
ctk.set_appearance_mode("Dark")  # Doimiy Dark Mode (Zamonaviy palitra uchun)
ctk.set_default_color_theme("blue")

class VariatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Oyna sozlamalari
        self.title("Test Variant Generatori")
        self.geometry("750x650")
        self.minsize(650, 550)

        self.configure(fg_color="#0F0F0F")  # Asosiy qora fon

        # Tanlangan fayllar ro'yxatini saqlash uchun
        self.selected_files: list[Path] = []

        # UI qismlarini qurish
        self._setup_ui()

    def _setup_ui(self):
        # Asosiy Grid sozlamalari (1 ta ustun, 3 ta qator)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)  # Fayl hududi (kengayuvchan)
        self.grid_rowconfigure(1, weight=0)  # Sozlamalar hududi
        self.grid_rowconfigure(2, weight=0)  # Tugma hududi

        # ==================== 1. Fayl tanlash hududi ====================
        self.file_frame = ctk.CTkFrame(self, fg_color="#1E1E1E", border_color="#333333", border_width=1, corner_radius=12)
        self.file_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="nsew")
        self.file_frame.grid_columnconfigure(0, weight=1)
        self.file_frame.grid_rowconfigure(1, weight=1)  # Ro'yxat cho'zilishi uchun

        # Sarlavha va tugmalar uchun yordamchi frame
        self.file_header = ctk.CTkFrame(self.file_frame, fg_color="transparent")
        self.file_header.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        self.file_header.grid_columnconfigure(0, weight=1)

        self.file_label = ctk.CTkLabel(self.file_header, text="📁 Test fayllarini tanlang (.docx)", font=("Inter", 18, "bold"), text_color="#00A8FF")
        self.file_label.grid(row=0, column=0, sticky="w")

        self.btn_group = ctk.CTkFrame(self.file_header, fg_color="transparent")
        self.btn_group.grid(row=0, column=1, sticky="e")

        self.select_btn = ctk.CTkButton(self.btn_group, text="+ Qo'shish", width=120, command=self.select_files, fg_color="#00A8FF", hover_color="#007BFF", text_color="#FFFFFF", font=("Inter", 14, "bold"), corner_radius=8)
        self.select_btn.pack(side="left", padx=(0, 10))

        self.clear_btn = ctk.CTkButton(self.btn_group, text="🗑 Tozalash", width=100, fg_color="#EF4444", hover_color="#D32F2F", text_color="#FFFFFF", font=("Inter", 14, "bold"), corner_radius=8, command=self.clear_files)
        self.clear_btn.pack(side="left")

        self.file_listbox = ctk.CTkScrollableFrame(self.file_frame, fg_color="#252525", corner_radius=8)
        self.file_listbox.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self._update_file_listbox()

        # ==================== 2. Sozlamalar paneli ====================
        self.settings_frame = ctk.CTkFrame(self, fg_color="#1E1E1E", border_color="#333333", border_width=1, corner_radius=12)
        self.settings_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.settings_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.settings_title = ctk.CTkLabel(self.settings_frame, text="⚙️ Generatsiya sozlamalari", font=("Inter", 16, "bold"), text_color="#FFFFFF")
        self.settings_title.grid(row=0, column=0, columnspan=2, padx=20, pady=(15, 5), sticky="w")

        self.count_label = ctk.CTkLabel(self.settings_frame, text="Variantlar soni:", text_color="#CCCCCC", font=("Inter", 13))
        self.count_label.grid(row=1, column=0, padx=20, pady=(5, 0), sticky="w")
        self.count_entry = ctk.CTkEntry(self.settings_frame, fg_color="#252525", border_color="#333333", text_color="#FFFFFF", height=35, corner_radius=8)
        self.count_entry.insert(0, "5")
        self.count_entry.grid(row=2, column=0, padx=20, pady=(5, 20), sticky="ew")

        self.q_label = ctk.CTkLabel(self.settings_frame, text="Savollar soni (bo'sh = barchasi):", text_color="#CCCCCC", font=("Inter", 13))
        self.q_label.grid(row=1, column=1, padx=20, pady=(5, 0), sticky="w")
        self.q_entry = ctk.CTkEntry(self.settings_frame, fg_color="#252525", border_color="#333333", text_color="#FFFFFF", height=35, corner_radius=8)
        self.q_entry.grid(row=2, column=1, padx=20, pady=(5, 20), sticky="ew")

        self.font_label = ctk.CTkLabel(self.settings_frame, text="Shrift o'lchami:", text_color="#CCCCCC", font=("Inter", 13))
        self.font_label.grid(row=1, column=2, padx=20, pady=(5, 0), sticky="w")
        self.font_entry = ctk.CTkEntry(self.settings_frame, fg_color="#252525", border_color="#333333", text_color="#FFFFFF", height=35, corner_radius=8)
        self.font_entry.insert(0, "12")
        self.font_entry.grid(row=2, column=2, padx=20, pady=(5, 20), sticky="ew")

        # ==================== 3. Harakat (Action) hududi ====================
        self.action_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.action_frame.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="ew")
        self.action_frame.grid_columnconfigure((0, 1), weight=1)

        self.generate_btn = ctk.CTkButton(self.action_frame, text="🚀 Alohida fayllarga", font=("Inter", 16, "bold"), height=55, corner_radius=12, fg_color="#00D26A", hover_color="#00AA55", text_color="#FFFFFF", command=lambda: self.start_generation(single_file=False))
        self.generate_btn.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        self.generate_single_btn = ctk.CTkButton(self.action_frame, text="📄 Bitta faylga", font=("Inter", 16, "bold"), height=55, corner_radius=12, fg_color="#00A8FF", hover_color="#007BFF", text_color="#FFFFFF", command=lambda: self.start_generation(single_file=True))
        self.generate_single_btn.grid(row=0, column=1, padx=(10, 0), sticky="ew")

        self.progress_bar = ctk.CTkProgressBar(self.action_frame, mode="indeterminate", fg_color="#252525", progress_color="#00A8FF", height=6)
        self.progress_bar.grid(row=1, column=0, columnspan=2, pady=(15, 0), sticky="ew")
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
            self._update_file_listbox()

    def _update_file_listbox(self):
        # Avvalgi ro'yxatni tozalash
        for widget in self.file_listbox.winfo_children():
            widget.destroy()

        if not self.selected_files:
            lbl = ctk.CTkLabel(self.file_listbox, text="📥 Fayllar ro'yxati bo'sh. Yuqoridagi '+ Qo'shish' tugmasini bosing.", text_color="#777777", font=("Inter", 14))
            lbl.pack(pady=40)
        else:
            for i, f in enumerate(self.selected_files, 1):
                row_frame = ctk.CTkFrame(self.file_listbox, fg_color="#1E1E1E", corner_radius=6)
                row_frame.pack(fill="x", pady=4, padx=5)
                
                lbl = ctk.CTkLabel(row_frame, text=f"📄 {i}. {f.name}", anchor="w", text_color="#FFFFFF", font=("Inter", 13))
                lbl.pack(side="left", padx=10, pady=8, fill="x", expand=True)
                
                btn = ctk.CTkButton(row_frame, text="✕", width=30, height=30, corner_radius=6, fg_color="#EF4444", hover_color="#D32F2F", text_color="#FFFFFF", command=lambda p=f: self.remove_file(p))
                btn.pack(side="right", padx=10)

    def remove_file(self, file_path: Path):
        if file_path in self.selected_files:
            self.selected_files.remove(file_path)
            self._update_file_listbox()

    def clear_files(self):
        self.selected_files.clear()
        self._update_file_listbox()

    def start_generation(self, single_file: bool = False):
        # 1. Tanlangan fayllarni tekshirish
        if not self.selected_files:
            messagebox.showwarning("Ogohlantirish", "Iltimos, kamida bitta test faylini tanlang!")
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
        self.generate_btn.configure(state="disabled", text="Kuting...")
        self.generate_single_btn.configure(state="disabled", text="Kuting...")
        self.progress_bar.grid()  # Progress barni ko'rsatish
        self.progress_bar.start() # Animatsiyani boshlash
        threading.Thread(target=self._run_generation_task, args=(count, qpv, font_size, single_file), daemon=True).start()

    def _run_generation_task(self, count: int, qpv: int | None, font_size: int, single_file: bool):
        """Generatsiyani alohida thread'da bajaradi."""
        try:
            cfg = Config.load()
            output_dir = Path(cfg.output_dir)

            # Parsing
            all_questions = []
            for f in self.selected_files:
                all_questions.extend(parse_docx(f))

            if not all_questions:
                self.after(0, lambda: messagebox.showerror("Xato", "Kiritilgan fayllardan hech qanday savol topilmadi."))
                return

            # Validatsiya
            errors = validate(all_questions)
            if has_errors(errors):
                self.after(0, lambda: self._show_validation_errors(errors))
                return

            # Generatsiya
            variants = generate_variants(
                all_questions,
                count=count,
                base_seed=cfg.base_seed,
                questions_per_variant=qpv
            )

            # Eksport
            if single_file:
                export_all_variants_to_single_docx(variants, output_dir, font_size=font_size)
            else:
                export_variants_to_docx(variants, output_dir, font_size=font_size)
            export_answers_to_docx(variants, output_dir / "Javoblar.docx")
            export_answers_to_xlsx(variants, output_dir / "Javoblar.xlsx")

            # Muvaffaqiyat xabari
            self.after(0, lambda: self._show_success(output_dir))

        except Exception as e:
            self.after(0, lambda err=e: messagebox.showerror("Kutilmagan xato", str(err)))
        finally:
            # UI ni asliga qaytarish
            self.after(0, self._reset_action_ui)

    def _reset_action_ui(self):
        self.progress_bar.stop()
        self.progress_bar.grid_remove()
        self.generate_btn.configure(state="normal", text="🚀 Alohida fayllarga")
        self.generate_single_btn.configure(state="normal", text="📄 Bitta faylga")

    def _show_validation_errors(self, errors):
        err_window = ctk.CTkToplevel(self)
        err_window.title("Fayllarda xatolik topildi")
        err_window.geometry("650x400")
        err_window.grab_set()  # Oynani modal qilish (faqat shu oynaga bosish mumkin)
        err_window.configure(fg_color="#0F0F0F")

        lbl = ctk.CTkLabel(err_window, text="Iltimos, avval quyidagi xatolarni Word faylda to'g'rilang:", text_color="red", font=("Inter", 14, "bold"))
        lbl.pack(pady=10)

        textbox = ctk.CTkTextbox(err_window, width=600, height=300, fg_color="#1E1E1E", border_color="#333333", border_width=1, text_color="#FFFFFF")
        textbox.pack(padx=20, pady=10)

        for err in errors:
            textbox.insert(tk.END, err.format() + "\n\n")
        textbox.configure(state="disabled")

    def _show_success(self, output_dir: Path):
        javob = messagebox.askyesno("Muvaffaqiyatli", "Variantlar muvaffaqiyatli yaratildi!\n\nNatijalar papkasini ochamizmi?")
        if javob:
            if sys.platform == "win32":
                os.startfile(output_dir)
            elif sys.platform == "darwin":
                import subprocess
                subprocess.Popen(["open", str(output_dir)])
            else:
                import subprocess
                subprocess.Popen(["xdg-open", str(output_dir)])

if __name__ == "__main__":
    app = VariatorApp()
    app.mainloop()