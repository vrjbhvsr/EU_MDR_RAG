## built the BM25 index in memory at startup rather than persisting it. At a few hundred chunks the tokenization is tens of milliseconds, one-time — persisting would mean a second on-disk artifact to keep in sync with the vector store, so rebuild-at-startup is both simpler and eliminates a drift risk. It's O(N) per boot, so past ~100K chunks I'd switch to a persistent BM25 backend like OpenSearch."

from typing import List
import re
from rank_bm25 import BM25Okapi
import numpy as np
from config.settings import get_settings

class BM25:
    def __init__(self, chunks: List[dict]):
        self.chunks =  chunks
        #self.config = cfg

    def _tokenizer(self, text) -> List:
        return re.findall(r'\w+', text.lower())

    def _chunk_source(self, metadata:dict) -> str:
        def label(number, title):
            if title:
                return f"{number} ({title})"
            return number
        article= metadata.get('article', "").strip()
        annex = metadata.get("annex","").strip()
        chapter = str(metadata.get('chapter',"")).strip()
        chapter_title = metadata.get("chapter_title", "").strip()
        annex_title = metadata.get("annex_title","").strip()
        article_title = metadata.get("article_title", "").strip()
        section = metadata.get("section","").strip()
        section_title = metadata.get("section_title", "").strip()

        if chapter == "0" and chapter_title == "preamble":
            source = "EU MDR Preamble"
        
        elif article:
            parts = []
            if chapter: parts.append(label(chapter, chapter_title))
            if section: parts.append(label(section,section_title))
            parts.append(label(article, article_title))
            source =  ", ".join(parts)

        elif annex:
            parts = [label(annex, annex_title)]
            if chapter: parts.append(label(chapter, chapter_title))
            source =  ", ".join(parts)

        return source

    def tokenize(self):
        metadatas = []
        ids = []
        corpus = []
        pcs = []

        for chunk in self.chunks:
            metadata = chunk.get('metadata')
            final_chunk = self._chunk_source(metadata) + " " + chunk.get("page_content")
            corpus.append(self._tokenizer(final_chunk))
            metadatas.append(metadata)
            ids.append(metadata.get("chunk_id"))
            pcs.append(chunk.get('page_content'))

        return corpus, ids, metadatas, pcs


class BM25_retriever:
    def __init__(self, chunks: List[dict]):
        self.chunks = chunks
        self.bm25 = BM25(chunks)
        self.corpus, self.ids, self.metadatas, self.page_contents = self.bm25.tokenize()
        self.bm = BM25Okapi(corpus=self.corpus)
        self.settings = get_settings()
        self.config = self.settings.retriver

    def _get_scores(self,query: str) -> List:
        tokenized_query = self.bm25._tokenizer(query)
        scores = self.bm.get_scores(tokenized_query)
        return list(scores)


    def retrieve(self,query: str) ->List[tuple]:
        scores = self._get_scores(query)
        top_k_indexes = np.argsort(scores)[::-1][:self.config.top_k]
        top_scores = [scores[x] for x in top_k_indexes]
        top_k_docs = [self.chunks[k] for k in top_k_indexes]
        metadatas = [m.get('metadata') for m in top_k_docs]
        chunk_ids = [id.get('chunk_id') for id in metadatas]
        page_contents = [pc.get('page_content') for pc in top_k_docs]

        return [
                {"chunk_id": id_, "page_content": doc, "metadata": meta, "score": float(scr)}
                for id_, doc, meta, scr in zip(
                    chunk_ids, page_contents, metadatas, top_scores
                )
            ]