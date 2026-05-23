import os
import sys
import re
from src.utils import log, CustomException
from src.ingestion import PDF_Extractor

class Text_Cleaner:
    def __init__(self,Doc_list: list, raw_text: str):
        """Initialize the Text_Cleaner class with the raw text extracted from a PDF document.
        This method sets up the necessary attributes for cleaning the extracted text, including the raw text and
        a logger for tracking the cleaning process. The raw text is expected to be a string containing the entire content of the PDF document, which will be processed to remove unwanted characters, headers, and other elements that may interfere with further analysis or processing.
        Args:
            raw_text (str): The raw text extracted from the PDF document. This should be a single string containing all the text content of the document, which will be cleaned to produce a more refined version suitable for analysis or other downstream tasks.
        Returns:
            Object: An instance of the Text_Cleaner class initialized with the provided raw text and ready for cleaning the text content.
        """
        self.Doc_list = Doc_list
        self.raw_text = raw_text    
        self.header_Regex = r"""\d{1,2}\.\d{1,2}\.\d{4}\s*\nL\s+\d{3}/\d+\s*\nOfficial Journal of the European Union\s*\nEN\s*"""
        self.log = log()

    def _get_unusal_characters(self) -> set:
        """Identify and return a set of unusual characters present in the raw text.
        This method scans through the raw text and collects characters that have an ASCII value greater than
        127, which are considered unusual or non-standard in the context of typical English text. The method returns a set of these unusual characters, which can be used for further analysis or cleaning processes to ensure that the text is in a more standard format for downstream tasks.
        Returns:
            set: A set of unusual characters found in the raw text. Each character in the set is a unique character that has an ASCII value greater than 127, indicating that it may be a non-standard character that could potentially interfere with text processing or analysis.
        """
        try:
            self.log.info("Finding Unsual characters in the text.")
            unusal_chars = [i for i in self.raw_text if ord(i) > 127]
            self.log.info(f"UNUSAL CHARACTERS FOUND: {set(unusal_chars)}")
            return set(unusal_chars)
        except Exception as e:
            self.log.exception("Failed to find unsual characters in the text.")
            raise CustomException(f"Failed to find unsual characters in the text.Error: {str(e), sys}") from e

    def _clean_unusal_characters(self) -> str:
        """Clean the raw text by replacing or removing unusual characters.
        This method takes the raw text and performs a series of replacements to clean it from unusual characters
        that may interfere with text processing. The method replaces specific unusual characters with more standard equivalents, such as replacing soft hyphens, Greek characters, non-breaking hyphens, and different types of quotation marks with their standard counterparts. The cleaned text is then returned as a string, which should be more suitable for analysis or other downstream tasks.
        Returns:
            str: The cleaned text after replacing or removing unusual characters. The returned string should have all the specified unusual characters replaced with their standard equivalents, resulting in a cleaner version of the original raw text that is more suitable for further processing or analysis.
        """
        try:
            Docs = []
            for doc in self.Doc_list:
                raw_text = doc.get('page_content')
                text = raw_text.replace("\xad","")
                text = text.replace("Ε","E") 
                text = text.replace("‑","-")
                text = text.replace("‘","'")
                text = text.replace("’","'")

                doc['page_content'] = text
                Docs.append(doc)
                
            return Docs
        except Exception as e:
            self.log.exception("Failed to clean unusal characters from the text.")
            raise CustomException(f"Failed to clean unusal characters from the text.Error: {str(e), sys}") from e
        
    def _remove_headers(self, Doc_list: list) -> list:
        """Remove headers from the raw text and add a 'Cross-relation' marker where the footer starts.
        This method uses a regular expression to identify and remove headers from the raw text. The headers are replaced with a specific marker ("Usefull Information to Consider:\n") to indicate where the footer starts. This helps in distinguishing the main content of the text from the header and footer sections, making it easier for further analysis or processing of the cleaned text.
        Args:
            raw_text (str): The raw text from which headers need to be removed. This should be a string containing the entire content of the PDF document, including any headers that may be present. The method will process this text to remove the headers and return a cleaned version of the text.
        Returns:
            str: The cleaned text after removing headers and adding a 'Cross-relation' marker. The returned string should have the headers removed and replaced with the specified marker, making it easier to identify the main content of the text for further analysis or processing.
        """
        try:
            self.log.info("Removing Headers from the text and adding the 'Cross-relation' where the footer starts.")
            Docs = []
            for doc in Doc_list:
                raw_text = doc.get('page_content')
                raw_text = re.sub(self.header_Regex,"Usefull Information to Consider:\n", raw_text)
                doc['page_content'] = raw_text
                Docs.append(doc)
            self.log.info("Headers removed from the raw data.")
            return Docs
        except Exception as e:
            self.log.exception("Failed to remove Headers from the text.")
            raise CustomException(f"Failed to remove Headers from the text. Error: {str(e), sys}") from e
        
    def Clean(self) -> str:
        """Clean the raw text by performing a series of cleaning operations, including removing unusual characters and headers.
        This method orchestrates the cleaning process by first identifying and cleaning unusual characters from the raw text
        and then removing headers while adding a 'Cross-relation' marker to indicate where the footer starts. The method returns the fully cleaned text, which should be more suitable for analysis or other downstream tasks.
        Returns:
            str: The fully cleaned text after performing all cleaning operations. The returned string should have all unusual characters replaced or removed, and headers removed with a 'Cross-relation' marker added to indicate where the footer starts. This cleaned text should be in a more standard format, making it easier for further processing or analysis.
        """
        try:
            self._get_unusal_characters()
            text = self._clean_unusal_characters()
            text = self._remove_headers(text)
            return text

        except Exception as e:
            raise CustomException(f"Failed to clean the text. The Error: {str(e), sys}") from e