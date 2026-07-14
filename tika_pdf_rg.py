from tika import parser
import io
import re
from langchain_text_splitters import RecursiveCharacterTextSplitter

class DocumentLoader:
    """A class for loading a document and splitting it into chunks."""

    def __init__(
            self,
            source: str | bytes,
            chunk_size: int = 750, #было 2000
            chunk_overlap: int = 200,
            add_start_index: bool = True) -> None:
        """Initializes the document processor with a source and text chunking configuration."""
        self.source = source
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.add_start_index = add_start_index
        self.text = ""
        self.chunks = []
        self.rows = []

    def load_text(self) -> str:
        """Text parsing with tika."""

        artifacts_to_remove = [
        "microsoft word - документ1",
        "microsoft word - document1",
        "untitled",
        ]

        if isinstance(self.source, str):
            parsed_text = parser.from_file(self.source)
        elif isinstance(self.source, bytes):
            parsed_text = parser.from_buffer(io.BytesIO(self.source))
        else:
            raise ValueError("Источник должен быть строкой, путем или байтами!")

        raw_text = parsed_text.get("content", "")
        if not raw_text.strip():
            raise ValueError("Не удалось извлечь текст из источника")

        clean_text = re.sub(r"http\S+|www\.\S+", "", raw_text) # ссылки
        clean_text = re.sub(r"<[^>]+>", " ", clean_text) #html аттрибуты

        clean_text = re.sub(r"[¶•→←]", " ", clean_text) #sphinx / markdown артефакты

        clean_text = re.sub(r"={3,}|-{3,}|\*{3,}", " ", clean_text)
        clean_text = re.sub(r"\s+", " ", clean_text) # заменяем множественные пробелы и переносы на один пробел
        clean_text = re.sub(r"[ \t]+", " ", clean_text)
        clean_text = re.sub(r"\n{3,}", "\n\n", clean_text)
        #clean_text = re.sub(r'[^\w\s,.:!?-]', '', clean_text)
        clean_text = clean_text.lower()
        clean_text = re.sub(r"(previous|next|copyright|all rights reserved|built with sphinx|read the docs).*", " ", clean_text, flags=re.IGNORECASE)
        for artifact in artifacts_to_remove:
            clean_text = clean_text.replace(artifact, "")
        self.text = clean_text
        return self.text

    def split_text(self) -> list[str]:
        """Breaking parsed text into chunks."""
        splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            encoding_name="cl100k_base",
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )
        self.chunks = splitter.split_text(self.text)
        print(f"Разбили на {len(self.chunks)} чанков")
        return self.chunks