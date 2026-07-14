import io
import re
import os
import tempfile
import subprocess
import fitz  # PyMuPDF
import pdfplumber

class PDFExtractor:
    """Извлекает текст и структурированные таблицы. Автоматически конвертирует .doc/.docx в PDF."""

    def __init__(self, source: str | bytes) -> None:
        self.source = source
        self.paragraphs = []
        self.tables = []
        self.raw_text = ""
        
        self.artifacts_to_remove = [
            "microsoft word - документ1",
            "microsoft word - document1",
            "untitled",
            "copyright",
            "all rights reserved"
        ]

    def _clean_text(self, text: str) -> str:
        if not text:
            return ""
            
        clean_text = text
        clean_text = re.sub(r"http\S+|www\.\S+", "", clean_text)
        clean_text = re.sub(r"<[^>]+>", " ", clean_text) 
        clean_text = re.sub(r"[¶•→←]", " ", clean_text)
        clean_text = re.sub(r"={3,}|-{3,}|\*{3,}", " ", clean_text)
        clean_text = re.sub(r"[ \t]+", " ", clean_text)
        
        for artifact in self.artifacts_to_remove:
            clean_text = re.compile(re.escape(artifact), re.IGNORECASE).sub("", clean_text)
            
        return clean_text.strip()

    def _convert_to_pdf(self, input_path: str) -> bytes:
        """
        Конвертирует файл в PDF с помощью LibreOffice и возвращает его байты.
        """
        soffice_path = ""
        if not os.path.exists(soffice_path):
             soffice_path = "soffice"

        with tempfile.TemporaryDirectory() as tmp_dir:
            print(f"[i] Конвертируем {os.path.basename(input_path)} в PDF...")
            # Вызываем LibreOffice в фоновом режиме (headless)
            process = subprocess.run(
                [soffice_path, "--headless", "--convert-to", "pdf", input_path, "--outdir", tmp_dir],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            if process.returncode != 0:
                raise RuntimeError(f"Ошибка конвертации: {process.stderr.decode('utf-8')}")

            # Ищем созданный PDF в нашей временной директории
            pdf_filename = os.path.splitext(os.path.basename(input_path))[0] + ".pdf"
            pdf_path = os.path.join(tmp_dir, pdf_filename)
            
            if not os.path.exists(pdf_path):
                raise FileNotFoundError("LibreOffice отработал, но PDF не был создан.")
                
            # Читаем байты готового PDF
            with open(pdf_path, "rb") as f:
                return f.read()

    def _ensure_pdf_bytes(self) -> bytes:
        """Определяет формат и при необходимости конвертирует в PDF."""
        if isinstance(self.source, bytes):
            return self.source
            
        if isinstance(self.source, str):
            if not os.path.exists(self.source):
                raise FileNotFoundError(f"Файл не найден: {self.source}")
                
            ext = self.source.lower().endswith
            if ext('.doc') or ext('.docx'):
                return self._convert_to_pdf(self.source)
            elif ext('.pdf'):
                with open(self.source, "rb") as f:
                    return f.read()
            else:
                raise ValueError("Поддерживаются только форматы .pdf, .doc, .docx")
                
        raise ValueError("Источник должен быть строкой (путь) или байтами!")

    def load(self) -> dict:
        """Парсинг PDF с очисткой и сохранением табличной структуры."""
        
        # Получаем гарантированные байты PDF
        file_bytes = self._ensure_pdf_bytes()

        # 1. Извлечение текста (PyMuPDF)
        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
            for page in doc:
                text = page.get_text("text")
                cleaned_text = self._clean_text(text)
                
                if cleaned_text:
                    paras = [p.strip() for p in cleaned_text.split('\n') if p.strip()]
                    self.paragraphs.extend(paras)
                    self.raw_text += cleaned_text + "\n"

        # 2. Извлечение таблиц (pdfplumber)
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_tables = page.extract_tables()
                
                for table_data in page_tables:
                    cleaned_table = []
                    for row in table_data:
                        cleaned_row = [
                            self._clean_text(cell.replace('\n', ' ')) if cell else "" 
                            for cell in row
                        ]
                        if any(cleaned_row):
                            cleaned_table.append(cleaned_row)

                    if cleaned_table:
                        self.tables.append({
                            "headers": cleaned_table[0] if len(cleaned_table) > 0 else [],
                            "rows": cleaned_table[1:] if len(cleaned_table) > 1 else []
                        })

        return {
            "paragraphs": self.paragraphs,
            "tables": self.tables,
            "raw_text": self.raw_text
        }