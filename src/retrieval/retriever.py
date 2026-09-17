from config.settings import RetrieverConfig
from typing import List

class Retriever:
    def __init__(self, collection, cfg: RetrieverConfig):
        self.config = cfg
        self.collection = collection

    def retrieve(self,
                  question: str
                  ) -> List:

        results = self.collection.query(
            query_texts = [question],
            n_results = self.config.top_k,
            where = self.config.filter
        )

        return [
                {"chunk_id": id_, "page_content": doc, "metadata": meta, "distance": dist}
                for id_, doc, meta, dist in zip(
                    results["ids"][0], results["documents"][0],
                    results["metadatas"][0], results["distances"][0],
                )
            ]