from src.ingestion import PDF_Extractor, Text_Cleaner, Structure_Parser
from src.utils import log, CustomException
import json
from pathlib import Path
import os
import sys

class Document_Ingestor:
    def __init__(self, raw_dir: str, processed_dir: str):
        """Initializes the Document_Ingestor with the specified raw and processed directories.
        Args:
            raw_dir (str): The directory path where the raw PDF documents are located.
            processed_dir (str): The directory path where the processed cleaned text will be saved.
        """
        self.raw_dir = raw_dir
        self.processed_dir = processed_dir
        self.log = log()
    
    def ingest(self):
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
                print("Working")
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