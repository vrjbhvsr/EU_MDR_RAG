import chromadb
import os
import torch
from pathlib import Path
from src.utils import log, CustomException
from config.settings import DBConfig, EmbeddingConfig
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction


# Define vector store class
class VectorStore:
    def __init__(self, database_path: Path|str, model_name: str, cfg: DBConfig):
        self.path = database_path
        self.model_name = model_name
        self.config = cfg
        if isinstance(self.path, str):
            self.path = Path(self.path)

        if not self.path.is_dir():
            os.makedirs(self.path, exist_ok=True)

    # create a persistent client where we store the database
    def _create_client(self) -> chromadb.api.client.Client:
        client = chromadb.PersistentClient(path=self.path)
        return client

    # Check whether cuda is available
    def _is_cuda_available(self) -> bool:
        if torch.cuda.is_available():
            return True
        return False

    def _embedding_function(self):
        if self._is_cuda_available:
            return SentenceTransformerEmbeddingFunction(self.model_name, device="cuda")
        return SentenceTransformerEmbeddingFunction(self.model_name)

    def create_collection(self, collection_name: str):
        client = self._create_client()
        return client.create_collection(name = collection_name,
                                        embedding_function= self._embedding_function(),
                                     configuration= self.config.collection_config)

    def get_collection(self, collection_name: str):
        client = self._create_client()
        return client.get_collection(name = collection_name,
                                        embedding_function= self._embedding_function(),
                                     configuration= self.config.collection_config)
        


    
