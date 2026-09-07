import json
import sys
import re
from typing import List
from pathlib import Path
from config.settings import ChunkingConfig
from src.utils import log, CustomException


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

    def _token_length(self, page_content: str) -> int:
        """
        Return the token length of the passed docs.

        Args:
            page_content: page_content from the docs

        Return:
            token length.
        """
        return len(self.tokenizer.encode(page_content))

    def get_split_levels(self, page_content: str) -> List[str]:
        """
        Determine the split levels for the given page content based on the configured patterns.
        It checks the levels in order of priority and returns a list of matching split levels.
        it divides the page_content based on 1. 1.1, 1.1.1, Part (a), (1), —, etc. patterns in the config.

        Args:
            page_content: The content of the page to analyze.

        Returns:
            List[str]: A list of split levels that match the patterns in the configuration.
        """
        split_levels = []
        try:
            self.log.info("Starting split level determination for the given page content.")
            if self._token_length(page_content) <= self.config.max_tokens:
                return ['no_split']

            if re.search(self.config.patterns['part'], page_content):
                split_levels.append("part")
            if re.search(self.config.patterns['simple'], page_content):
                split_levels.append("simple")
            if re.search(self.config.patterns['decimal'], page_content):
                split_levels.append("decimal")
            if re.search(self.config.patterns['triple'], page_content):
                split_levels.append("triple")
            if re.search(self.config.patterns['paren_letter'], page_content):
                split_levels.append("paren_letter")
            if re.search(self.config.patterns['paren_num'], page_content):
                split_levels.append("paren_num")
            if re.search(self.config.patterns['bullet'], page_content):
                split_levels.append("bullet")
            self.log.info(f"Split levels determined successfully: {split_levels}")
            return split_levels
        except Exception as e:
            self.log.exception(f"An error occurred while determining split levels: {str(e)}")
            raise CustomException(f"An error occurred while determining split levels: {str(e), sys}") from e
