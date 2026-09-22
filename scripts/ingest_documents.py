from src.ingestion import PDF_Extractor, Text_Cleaner, Structure_Parser
from src.utils import log, CustomException
import json
from pathlib import Path
import os
import sys
from src.chunking import Chunker
from config.settings import get_settings
from transformers import AutoTokenizer 
from src.vector_store import VectorStore, Loader


class Document_Ingestor:
    def __init__(self):
        """Initializes the Document_Ingestor with the specified raw and processed directories.
        Args:
            raw_dir (str): The directory path where the raw PDF documents are located.
            processed_dir (str): The directory path where the processed cleaned text will be saved.
        """
        
        self.settings = get_settings()
        self.raw_dir = self.settings.ingestion.raw_data_dir
        self.processed_dir = self.settings.ingestion.processed_data_dir
        self.tokenizer = AutoTokenizer.from_pretrained(self.settings.embedding.model_name)
        self.log = log()
    
    def _text_preprocessing(self):
        """Ingests documents from the raw directory, processes them, and saves the cleaned text to the processed directory.
        Returns:
            cleaned_text (dict): A dictionary containing the cleaned text extracted from the PDF.
        Raises:
            CustomException: If any error occurs during the ingestion process, a CustomException is raised with the error details.
        """
        try:
            for filename in os.listdir(self.raw_dir):
                self.log.info(f"Starting ingestion process for file: {filename}")
                PE = PDF_Extractor(pdf_path = filename)
                raw_text, page_starts = PE.extract_text()
                self.log.info("PDF text extraction completed successfully.")
                
                SP = Structure_Parser(raw_text, page_starts)
                sm = SP.Create_Structure()
                self.log.info("Structure parsing completed successfully.")
                
                TC = Text_Cleaner(Doc_list=sm, raw_text=raw_text)
                cleaned_text = TC.Clean()
                self.log.info("Text cleaning completed successfully.")
            
            output_path = Path(self.processed_dir) / f"cleaned_{filename.replace('.pdf', '.json')}"
            with open(output_path, 'w') as f:
                json.dump(cleaned_text, f, indent=4)
            self.log.info(f"Cleaned text saved successfully to {output_path}")
            return cleaned_text
        except Exception as e:
            self.log.exception(f"An error occurred during the ingestion process: {str(e)}")
            raise CustomException(f"An error occurred during the ingestion process: {str(e), sys}") from e

    def _context_aware_chunking(self):
        cleaned_text = self._text_preprocessing()
        chunker = Chunker(self.tokenizer, cleaned_text, self.settings.chunking)
        chunks = chunker.chunk_docs()
        return chunks
        

    def _poppulate_vecstore(self):
        chunks = self._context_aware_chunking()
        ef = VectorStore(self.settings.DB).embedding_function(model_name=self.settings.embedding.model_name)
        loader = Loader(chunks, self.settings.DB)
        loader.add_to_collection(embedding_function=ef, collection_name=self.settings.DB.collection_name)

        #collection = VectorStore(settings.DB).get_collection(ef, settings.DB.collection_name)

    def ingest(self):
        self._poppulate_vecstore()

DI = Document_Ingestor().ingest()