import chromadb
import os
import torch
import sys
from pathlib import Path
from src.utils import log, CustomException
from config.settings import DBConfig
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction


# Define vector store class
class VectorStore:
    def __init__(self,cfg: DBConfig):
        """
        Initialize the VectorStore class.
        Args:
            database_path (str): Path to the database directory.
            model_name (str): Name of the embedding model to use.
            cfg (DBConfig): Configuration for the database.
        """

        self.config = cfg
        self.path = self.config.database_path
        self.log = log()

        if not os.path.isdir(self.path):
            os.makedirs(self.path, exist_ok=True)

    # create a persistent client where we store the database
    def create_or_get_client(self) -> chromadb.api.client.Client:
        """
        Create a persistent ChromaDB client.
        
        Returns:
            chromadb.api.client.Client: An instance of the ChromaDB client.
        """
        try:
            client = chromadb.PersistentClient(path=self.path)
            return client
        except Exception as e:
            log.error(f"Failed to create ChromaDB client: {e}")
            raise CustomException(f"Failed to create ChromaDB client: {e}",sys)

    # Check whether cuda is available
    def _is_cuda_available(self) -> bool:
        """
        Check if CUDA is available for GPU acceleration.
        
        Returns:
            bool: True if CUDA is available, False otherwise.
        """
        if torch.cuda.is_available():
            return True
        return False

    def _embedding_function(self, model_name):
        """
        Create an embedding function based on CUDA availability.
       
        Returns:
            SentenceTransformerEmbeddingFunction: An instance of the embedding function.
        """
        if self._is_cuda_available():
            return SentenceTransformerEmbeddingFunction(model_name, device="cuda")
        return SentenceTransformerEmbeddingFunction(model_name)

    def create_collection(self, collection_name: str):
        """
        Create a new collection in the vector store.
        Args:
            collection_name (str): Name of the collection to create.
        Returns:
            Collection: An instance of the created collection.
        """
        try:

            client = self._create_client()
            return client.create_collection(name = collection_name,
                                            embedding_function= self._embedding_function(),
                                        configuration= self.config.collection_config)
        except Exception as e:
            log.error(f"Failed to create collection '{collection_name}': {e}")
            raise CustomException(f"Failed to create collection '{collection_name}': {e}", sys)
        
    def get_collection(self, collection_name: str):
        """
        Get an existing collection from the vector store.
        Args:
            collection_name (str): Name of the collection to retrieve.
        Returns:
            Collection: An instance of the retrieved collection.
        """
        try:
            client = self._create_client()
            return client.get_collection(name = collection_name,
                                            embedding_function= self._embedding_function(),
                                        configuration= self.config.collection_config)
        except Exception as e:
            log.error(f"Collection '{collection_name}' not found — run the indexing script first.")
            raise CustomException(f"Failed to get collection '{collection_name}': {e}", sys)



