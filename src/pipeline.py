from src.utils import log, CustomException
from src.generation import Prompt_Configuration, Generate_Answer
from src.retrieval import Hybrid_Retriever
from src.vector_store import VectorStore
from config.settings import get_settings
import json

class Build_Pipeline:
    def __init__(self):
        self.settings = get_settings()
        chunk = json.load(open('data/processed/chunks/chunks_from_script.json'))
        self.chroma = VectorStore()
        vs = VectorStore()
        ef = vs.embedding_function(self.settings.embedding.model_name)
        collection = vs.get_collection(embedding_function=ef, collection_name=self.settings.DB.collection_name)
        self.hr = Hybrid_Retriever(collection,chunk)
        self.prompt_config = Prompt_Configuration()
        self.generation = Generate_Answer()

    def build(self):
        prompt = self.prompt_config.create_prompt(retriever=self.hr)
        answer = self.generation.response(prompt=prompt)
        return answer




