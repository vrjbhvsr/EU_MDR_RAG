from config.settings import RetrieverConfig
from typing import List

class Retriever:
    def __init__(self, vector_store, cfg: RetrieverConfig):
        self.config = cfg
        self.collection = vector_store

    def retrieve(self,
                  question: str
                  ) -> List:

        results = self.collection.query(
            query_texts = [question],
            n_results = self.config.top_k
        )

        return results