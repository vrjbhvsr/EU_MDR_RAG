from scripts.ingest_documents import Document_Ingestor
from config import get_settings
from transformers import AutoTokenizer 

settings = get_settings()
tokenizer = AutoTokenizer.from_pretrained(settings.chunking.model_name)


raw_dir = settings.ingestion.raw_data_dir
processed_dir = settings.ingestion.processed_data_dir
embedding_model = settings.chunking.model_name



ingestor = Document_Ingestor(raw_dir, processed_dir)
cleaned_text = ingestor.ingest()

