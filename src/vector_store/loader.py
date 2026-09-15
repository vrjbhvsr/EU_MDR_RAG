import chromadb
from typing import List
from config.settings import DBConfig
from src.vector_store import VectorStore
from src.utils import log, CustomException

class Loader:
    def __init__(self, chunks: List[dict], cfg: DBConfig):
        self.chunks = chunks
        self.config = cfg
        self.vec_store = VectorStore(self.config)
        self.log = log()
99
    def _get_chunk_data(self):
        ids, metadatas, page_contents = [], [], []
        for chunk in self.chunks:
            page_contents.append(chunk.get('page_content'))
            metadatas.append(chunk.get('metadata'))
            ids.append(chunk.get("chunk_id"))

        return ids, metadatas, page_contents

    def add_to_collection(self, collection_name):
        client = self.vec_store.create_or_get_client()
        if collection_name in [c.name for c in client.list_collections()]:
            client.delete_collection(name = collection_name)
            collection = self.vec_store.create_collection(collection_name)
            ids, metadatas, page_contents = self._get_chunk_data()
            if len(ids) == len(set(ids)):
                collection.add(ids=ids,
                               documents = page_contents,
                               metadatas = metadatas)

            