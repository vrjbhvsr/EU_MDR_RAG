from scripts.ingest_documents import Document_Ingestor
from config import get_settings

settings = get_settings()


raw_dir = settings.ingestion.raw_data_dir
processed_dir = settings.ingestion.processed_data_dir
embedding_model = settings.chunking.model_name



ingestor = Document_Ingestor(raw_dir, processed_dir)
ingestor.ingest()
