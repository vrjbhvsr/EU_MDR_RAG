import json
import sys
from typing import List
from pathlib import Path
from config.settings import ChunkingConfig
from utils import log, CustomException


class Chunker:
    def __init__(self, tokenizer, cleaned_docs: list[dict], cfg:ChunkingConfig):
        """Split parser output into <=max_tokens chunks, packed within each structural unit.

        Args:
            docs: cleaned section-wise docs from ingestion (page_content + metadata).
            cfg: ChunkingConfig (max_tokens, over_512_policy).
            tokenizer: a HF tokenizer with .encode(); injected, never module-global.

        Returns:
            Chunks as {"page_content": str, "metadata": dict}. No file I/O.

        Raises:
            Exception: if docs is empty.
        """
        
        if not cleaned_docs:
            raise CustomException("docs is empty, Nothing to chunk",sys)
        self.tokenizer = tokenizer
        self.docs = cleaned_docs
        self.config = cfg
        self.log = log()




