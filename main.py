from config.settings import DBConfig, EmbeddingConfig, RetrieverConfig, get_settings
from src.vector_store import VectorStore
from scripts.Indexing import poppulate_vecstore
from src.retrieval import Retriever


settings = get_settings()

vs = VectorStore(settings.DB)
ef = vs.embedding_function(settings.embedding.model_name)
collection = vs.get_collection(embedding_function=ef, collection_name=settings.DB.collection_name)

if not collection.count() == 366:
    poppulate_vecstore()

retriever = Retriever(vector_store=collection, cfg= settings.retriver)
r = retriever.retrieve("What are the requirements mentioned in Article 62 for conformity of devices?")
print(r)