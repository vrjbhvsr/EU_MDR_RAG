## built the BM25 index in memory at startup rather than persisting it. At a few hundred chunks the tokenization is tens of milliseconds, one-time — persisting would mean a second on-disk artifact to keep in sync with the vector store, so rebuild-at-startup is both simpler and eliminates a drift risk. It's O(N) per boot, so past ~100K chunks I'd switch to a persistent BM25 backend like OpenSearch."

from typing import List
#from config.settings import BM_Config
import re

class BM25_Retriever:
    def __init__(self, chunks: List[dict], cfg: any = None):
        self.chunks = chunks
        self.config = cfg

    def _tokenizer(self, text) -> List:
        return re.findall(r'\w+', text.lower())

    def _label(self, number, title):
        if title:
            return f"{number} ({title})"
        return number

    def create_source(self, metadata: dict):
        article= metadata.get('article', "").strip()
        annex = metadata.get("annex","").strip()
        chapter = str(metadata.get('chapter',"")).strip()
        chapter_title = metadata.get("chapter_title", "").strip()
        annex_title = metadata.get("annex_title","").strip()
        article_title = metadata.get("article_title", "").strip()
        section = metadata.get("section","").strip()
        section_title = metadata.get("section_title").strip()

        if chapter == "0" and chapter_title == "preamble":
            source = "EU MDR Preamble"
        
        elif article:
            parts = []
            if chapter: parts.append(self._label(chapter, chapter_title))
            if section: parts.append(self._label(section,section_title))
            parts.append(self._label(article, article_title))
            source =  ", ".join(parts)

        elif annex:
            parts = [self._label(annex, annex_title)]
            if chapter: parts.append(self._label(chapter, chapter_title))
            source =  ", ".join(parts)

        return source

    def _tokenizable_chunk(self, chunk:dict):
        pc = chunk.get("page_content")
        metadata = chunk.get('metadata')
        source = self.create_source(metadata)
        return source + " " + pc


    def BM_tokenizer(self, chunk: dict|None = None, query: str|None = None) -> List:
        if chunk:
            with_source = self._tokenizable_chunk(chunk)
            return self._tokenizer(with_source)
        if query:
            return self._tokenizer(query)
    