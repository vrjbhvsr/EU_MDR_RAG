from config.settings import get_settings
from src.vector_store import VectorStore
from src.retrieval import Retriever
from src.retrieval import BM25_retriever

class Hybrid_Retriever:
    def __init__(self, chunks: list[dict]):
        self.settings = get_settings()
        self.config = self.settings.retriver
        self.chunks = chunks
        vs = VectorStore()
        ef = vs.embedding_function(self.settings.embedding.model_name)
        collection = vs.get_collection(embedding_function=ef, collection_name=self.settings.DB.collection_name)
        self.retriever = Retriever(collection=collection)
        self.bm = BM25_retriever(chunks)


    def _RRF(self, combined_results: list[list]):
        rrf_scores = {}
        by_id = {}
        #print([y.get('chunk_id') for x in combined_results for y in x])
        for list in combined_results:
            for rank, doc in enumerate(list, start=1): 
                doc_id = doc.get('chunk_id')
                if doc_id not in rrf_scores:
                    rrf_scores[doc_id] = 0.0
                rrf_scores[doc_id] += 1.0/(self.config.constant_k+rank)
                
        sorted_docs = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_docs[:self.config.top_k-1]


    def retrieve(self,query: str):
        dense_results = self.retriever.retrieve(query)
        bm_results = self.bm.retrieve(query)
        by_id = {r["chunk_id"]: r for r in dense_results + bm_results}
        scored_results = self._RRF(combined_results=[dense_results,bm_results])
        return [
            {
        "chunk_id": by_id[cid]["chunk_id"],
        "page_content": by_id[cid]["page_content"],
        "metadata": by_id[cid]["metadata"],
        "score": float(sc),
            }
            for cid, sc in scored_results
        ]

