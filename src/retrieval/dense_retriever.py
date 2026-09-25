from config.settings import get_settings
from typing import List

class Retriever:
    def __init__(self, collection):
        self.settings = get_settings()
        self.config = self.settings.retriver
        self.collection = collection

    def retrieve(self) -> List:

        results = self.collection.query(
            query_texts = [self.settings.main.query],
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