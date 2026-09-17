from config.settings import DBConfig, EmbeddingConfig, RetrieverConfig, get_settings
from src.vector_store import VectorStore
from scripts.Indexing import poppulate_vecstore
from src.retrieval import Retriever
from src.evaluation import evaluate_retriever


settings = get_settings()

vs = VectorStore(settings.DB)
ef = vs.embedding_function(settings.embedding.model_name)
collection = vs.get_collection(embedding_function=ef, collection_name=settings.DB.collection_name)

retriever = Retriever(collection=collection, cfg= settings.retriver)

recall_at_5, MRR = evaluate_retriever(evaluation_set="data/evaluation/test_questions_updated.json",
                                      retriever=retriever,
                                      top_k= settings.retriver.top_k)

print(recall_at_5, MRR)