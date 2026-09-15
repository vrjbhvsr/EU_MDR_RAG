### Future reminder: I want to sepearte the indexing and generation pipeline. so plann accordingly.
###  Main.py must contain only generation pipeline

from scripts.ingest_documents import Document_Ingestor
from src.chunking import Chunker
from config import get_settings
from transformers import AutoTokenizer 
from src.vector_store import VectorStore, Loader


settings = get_settings()
tokenizer = AutoTokenizer.from_pretrained(settings.embedding.model_name)
raw_dir = settings.ingestion.raw_data_dir
processed_dir = settings.ingestion.processed_data_dir
embedding_model = settings.embedding.model_name


ingestor = Document_Ingestor(raw_dir, processed_dir)
cleaned_text = ingestor.ingest()
#print("raw: \n", cleaned_text[0:2])


chunker = Chunker(tokenizer, cleaned_text, settings.chunking)
chunks = chunker.chunk_docs()


ef = VectorStore(settings.DB).embedding_function(model_name=settings.embedding.model_name)
loader = Loader(chunks, settings.DB)
loader.add_to_collection(embedding_function=ef, collection_name="Testing")

