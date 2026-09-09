from scripts.ingest_documents import Document_Ingestor
from src.chunking import Chunker
from config import get_settings
from transformers import AutoTokenizer 

settings = get_settings()
tokenizer = AutoTokenizer.from_pretrained(settings.embedding.model_name)


raw_dir = settings.ingestion.raw_data_dir
processed_dir = settings.ingestion.processed_data_dir
embedding_model = settings.embedding.model_name



ingestor = Document_Ingestor(raw_dir, processed_dir)
cleaned_text = ingestor.ingest()

chunker = Chunker(tokenizer, cleaned_text, settings.chunking)
chunks = chunker.chunk_docs()

