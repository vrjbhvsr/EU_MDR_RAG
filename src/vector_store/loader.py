import sys
from typing import List
from config.settings import DBConfig
from src.vector_store import VectorStore
from src.utils import log, CustomException

class Loader:
    def __init__(self, chunks: List[dict], cfg: DBConfig):
        """
        Initialize the Loader class.
        Args:
            chunks (List[dict]): List of chunk dictionaries containing page content and metadata.
            cfg (DBConfig): Configuration for the database.
        """
        self.chunks = chunks
        self.config = cfg
        self.vec_store = VectorStore(self.config)
        self.log = log()

    def _get_chunk_data(self) -> tuple[List[str], List[dict], List[str]]:
        """
        Extract data from chunks.
        Returns:
            tuple: A tuple containing three lists - ids, metadatas, and page_contents.
        """
        ids, metadatas, page_contents = [], [], []
        for chunk in self.chunks:
            page_contents.append(chunk.get('page_content'))
            metadatas.append(chunk.get('metadata'))
            ids.append(chunk.get("metadata").get("chunk_id"))

        return ids, metadatas, page_contents

    def add_to_collection(self,embedding_function, collection_name):
        """
        Add chunks to a collection.
        Args:
            embedding_function: The embedding function to use.
            collection_name (str): The name of the collection to add chunks to.
        """
        try:
            client = self.vec_store.create_or_get_client()
            if collection_name in [c.name for c in client.list_collections()]:
                collection = client.get_collection(name = collection_name)
            else:
                collection = self.vec_store.create_collection(embedding_function, collection_name)
            ids, metadatas, page_contents = self._get_chunk_data()
            print(ids[:5])
            if len(ids) != len(set(ids)):
                raise CustomException("Duplicate chunk_ids — aborting insert", sys)
            collection.add(ids=ids,
                            documents = page_contents,
                            metadatas = metadatas)
            self.log.info(f"Successfully added {len(ids)} chunks to collection '{collection_name}'.")
        except Exception as e:
            self.log.error(f"Failed to add chunks to collection: {e}")
            raise CustomException(f"Failed to add chunks to collection: {e}", sys)