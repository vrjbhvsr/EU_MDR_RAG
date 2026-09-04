import json
from typing import List
from pathlib import Path
from sentence_transformers import SentenceTransformer
from config import get_settings

settings = get_settings()
print(next(settings.ingestion.processed_data_dir.glob("*.json")))

class Chunker:
    def __init__(self, tokenizer, cleaned_docs: Path, max_chunk_size: int) -> List:
        """Split parser output into <=max_tokens chunks, packed within each structural unit.

        Args:
            docs: cleaned section-wise docs from ingestion (page_content + metadata).
            cfg: ChunkingConfig (max_tokens, over_512_policy).
            tokenizer: a HF tokenizer with .encode(); injected, never module-global.

        Returns:
            Chunks as {"page_content": str, "metadata": dict}. No file I/O.

        Raises:
            ValueError: if docs is empty.
        """
        self.tokenizer = tokenizer
        doc_path = next(cleaned_docs.glob("*.json"))
        with open(doc_path, 'r') as f:
            self.docs = json.load(f)
        pass
