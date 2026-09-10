"""
Main Application - PDF Scanner dengan Rekap SKU.
UI menggunakan CustomTkinter.
"""
import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path
import threading

from app.pdf_reader import read_pdf_text, pdf_has_text
from app.ocr_engine import ocr_pdf
from app.parser import parse_auto
from app.rekap import rekap_to_dataframe
from app.export import export_to_excel
from config import PDF_READ_MODE


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Rekap SKU PDF Scanner v2.1.3")
        self.geometry("950x700")
        self.minsize(850, 600)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.pdf_path = None
        self.raw_data = []
        self.rekap_data = []

        self._build_ui()

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 5))

        ctk.CTkLabel(
            header,
            text="Rekap SKU PDF Scanner",
            font=ctk.CTkFont(size=22, weight="bold"),
        ).pack(side="left")

        ctk.CTkLabel(
            header,
            text="v2.1.0",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        ).pack(side="left", padx=10)

        # File selection frame
        file_frame = ctk.CTkFrame(self)
        file_frame.pack(fill="x", padx=20, pady=10)

        self.file_label = ctk.CTkLabel(
            file_frame,
            text="Belum ada file dipilih",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        )
        self.file_label.pack(side="left", padx=10, pady=10, expand=True)

        ctk.CTkButton(
            file_frame,
            text="Pilih PDF",
            command=self._select_file,
            width=120,
        ).pack(side="right", padx=10, pady=10)

        # Read mode selection
        mode_frame = ctk.CTkFrame(self, fg_color="transparent")
        mode_frame.pack(fill="x", padx=20, pady=(0, 5))

        ctk.CTkLabel(mode_frame, text="Mode Baca:").pack(side="left")
        self.mode_var = ctk.StringVar(value=PDF_READ_MODE)
        ctk.CTkOptionMenu(
            mode_frame,
            variable=self.mode_var,
            values=["auto", "text", "ocr"],
            width=100,
        ).pack(side="left", padx=5)

        # Process button
        self.process_btn = ctk.CTkButton(
            self,
            text="Proses PDF",
            command=self._process_pdf,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            state="disabled",
        )
        self.process_btn.pack(fill="x", padx=20, pady=10)

        # Status label
        self.status_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="gray",
        )
        self.status_label.pack(padx=20, anchor="w")

        # Progress bar
        self.progress = ctk.CTkProgressBar(self)
        self.progress.pack(fill="x", padx=20, pady=(0, 10))
        self.progress.set(0)

        # Results table
        results_frame = ctk.CTkFrame(self)
        results_frame.pack(fill="both", expand=True, padx=20, pady=(0, 5))

        # Table header
        table_header = ctk.CTkFrame(results_frame, fg_color="#2B5797")
        table_header.pack(fill="x", padx=1, pady=(1, 0))

        ctk.CTkLabel(table_header, text="No", width=50, anchor="center",
                      font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(table_header, text="SKU / Nama Produk", width=450, anchor="w",
                      font=ctk.CTkFont(weight="bold")).pack(side="left", padx=5)
        ctk.CTkLabel(table_header, text="Jumlah", width=120, anchor="e",
                      font=ctk.CTkFont(weight="bold")).pack(side="right", padx=5)

        # Scrollable results
        self.results_scroll = ctk.CTkScrollableFrame(results_frame)
        self.results_scroll.pack(fill="both", expand=True, padx=1, pady=1)

        # Summary frame
        self.summary_frame = ctk.CTkFrame(self, fg_color="#1a1a2e")
        self.summary_frame.pack(fill="x", padx=20, pady=(0, 5))

        self.summary_label = ctk.CTkLabel(
            self.summary_frame,
            text="",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w",
        )
        self.summary_label.pack(padx=10, pady=8, anchor="w")

        # Export button
        export_frame = ctk.CTkFrame(self, fg_color="transparent")
        export_frame.pack(fill="x", padx=20, pady=(0, 15))

        self.export_btn = ctk.CTkButton(
            export_frame,
            text="Export ke Excel",
            command=self._export_excel,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#28a745",
            hover_color="#218838",
            state="disabled",
        )
        self.export_btn.pack(side="right")

        self.export_label = ctk.CTkLabel(
            export_frame,
            text="",
            font=ctk.CTkFont(size=11),
        )
        self.export_label.pack(side="right", padx=10)

    def _select_file(self):
        path = filedialog.askopenfilename(
            title="Pilih File PDF",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")],
        )
        if path:
            self.pdf_path = path
            filename = Path(path).name
            self.file_label.configure(text=filename, text_color="white")
            self.process_btn.configure(state="normal")
            self.status_label.configure(text="")
            self.export_btn.configure(state="disabled")
            self.export_label.configure(text="")
            self.summary_label.configure(text="")
            self._clear_results()

    def _clear_results(self):
        for widget in self.results_scroll.winfo_children():
            widget.destroy()
        self.raw_data = []
        self.rekap_data = []

    def _process_pdf(self):
        if not self.pdf_path:
            return

        self.process_btn.configure(state="disabled", text="Memproses...")
        self.status_label.configure(text="Membaca PDF...")
        self.progress.set(0.1)

        thread = threading.Thread(target=self._do_process, daemon=True)
        thread.start()

    def _do_process(self):
        try:
            mode = self.mode_var.get()
            text = ""

            self.after(0, lambda: self.status_label.configure(text="Membaca PDF..."))
            self.after(0, lambda: self.progress.set(0.2))

            if mode == "ocr":
                text = ocr_pdf(self.pdf_path)
            elif mode == "text":
                text = read_pdf_text(self.pdf_path)
            else:
                if pdf_has_text(self.pdf_path):
                    text = read_pdf_text(self.pdf_path)
                else:
                    self.after(0, lambda: self.status_label.configure(
                        text="Tidak ada teks ditemukan, menggunakan OCR..."))
                    text = ocr_pdf(self.pdf_path)

            if not text.strip():
                self.after(0, lambda: self._show_error("Tidak ada teks yang bisa dibaca dari PDF."))
                return

            self.after(0, lambda: self.status_label.configure(text="Mengekstrak data..."))
            self.after(0, lambda: self.progress.set(0.5))

            raw_data = parse_auto(text)

            if not raw_data:
                self.after(0, lambda: self._show_error(
                    "Tidak ada data SKU yang ditemukan.\n"
                    "Coba sesuaikan regex pattern di config.py."))
                return

            self.raw_data = raw_data

            self.after(0, lambda: self.status_label.configure(text="Mengelompokkan SKU..."))
            self.after(0, lambda: self.progress.set(0.7))

            df = rekap_to_dataframe(raw_data, split_bundles=True)
            self.rekap_data = df.to_dict("records")

            self.after(0, lambda: self._display_results(df))
            self.after(0, lambda: self.progress.set(1.0))
            self.after(0, lambda: self.status_label.configure(
                text=f"Selesai! {len(self.rekap_data)} produk ditemukan."))

        except Exception as e:
            self.after(0, lambda: self._show_error(f"Error: {str(e)}"))
        finally:
            self.after(0, lambda: self.process_btn.configure(state="normal", text="Proses PDF"))

    def _display_results(self, df):
        self._clear_results()

        total_qty = 0
        alt_colors = ["#1a1a2e", "#16213e"]

        for idx, (_, row) in enumerate(df.iterrows()):
            bg_color = alt_colors[idx % 2]
            row_frame = ctk.CTkFrame(self.results_scroll, fg_color=bg_color)
            row_frame.pack(fill="x", pady=1)

            # No
            ctk.CTkLabel(row_frame, text=str(idx + 1), width=50, anchor="center",
                          font=ctk.CTkFont(size=12), text_color="gray").pack(side="left", padx=5)
            # SKU
            ctk.CTkLabel(row_frame, text=row["SKU"], width=450, anchor="w",
                          font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=5)
            # Qty
            qty = row["Total Quantity"]
            total_qty += qty
            ctk.CTkLabel(row_frame, text=str(qty), width=120, anchor="e",
                          font=ctk.CTkFont(size=13, weight="bold"),
                          text_color="#28a745").pack(side="right", padx=5)

        # Summary
        self.summary_label.configure(
            text=f"Total: {len(df)} produk  |  {total_qty} unit keseluruhan"
        )

        self.export_btn.configure(state="normal")

    def _export_excel(self):
        if not self.rekap_data:
            return

        path = filedialog.asksaveasfilename(
            title="Simpan Hasil Rekap",
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx")],
            initialfile="hasil_rekap.xlsx",
        )

        if path:
            try:
                result_path = export_to_excel(self.rekap_data, output_path=path)
                self.export_label.configure(text=f"Tersimpan: {result_path}", text_color="#28a745")
                messagebox.showinfo("Export Berhasil", f"File tersimpan di:\n{result_path}")
            except Exception as e:
                messagebox.showerror("Export Gagal", f"Error: {str(e)}")

    def _show_error(self, message):
        self.status_label.configure(text=message, text_color="#dc3545")
        self.progress.set(0)


def run():
    app = App()
    app.mainloop()
