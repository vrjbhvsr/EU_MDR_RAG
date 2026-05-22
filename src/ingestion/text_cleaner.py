import os
import sys
import re
from src.utils import log, CustomException
from src.ingestion import PDF_Extractor

class Text_Cleaner:
    def __init__(self,raw_text: str):
        self.raw_text = raw_text
        self.header_Regex = r"""\d{1,2}\.\d{1,2}\.\d{4}\s*\nL\s+\d{3}/\d+\s*\nOfficial Journal of the European Union\s*\nEN\s*"""
        self.log = log()

    def _get_unusal_characters(self) -> set:
        try:
            self.log.info("Finding Unsual characters in the text.")
            unusal_chars = [i for i in self.raw_text if ord(i) > 127]
            self.log.info(f"UNUSAL CHARACTERS FOUND: {set(unusal_chars)}")
            return set(unusal_chars)
        except Exception as e:
            self.log.exception("Failed to find unsual characters in the text.")
            raise CustomException(f"Failed to find unsual characters in the text.Error: {str(e), sys}") from e

    def _clean_unusal_characters(self) -> str:
        try:
            self.log.info("Cleaning unusal characters from the text.")
            text = self.raw_text.replace("\xad","")
            self.log.info("Removed soft hyphen characters from the text.")
            text = text.replace("Ε","E")
            self.log.info("Replaced Greek character 'Ε' from the text to English 'E'.")    
            text = text.replace("‑","-")
            self.log.info("Replaced non-breaking hyphen characters from the text to standard hyphen.")
            text = text.replace("‘","'")
            self.log.info("Replaced left single quotation mark characters from the text to standard single quotation mark.")    
            text = text.replace("’","'")
            self.log.info("Replaced right single quotation mark characters from the text to standard single quotation mark.")
            return text
        except Exception as e:
            self.log.exception("Failed to clean unusal characters from the text.")
            raise CustomException(f"Failed to clean unusal characters from the text.Error: {str(e), sys}") from e
        
    def _remove_headers(self, raw_text: str) -> str:
        try:
            self.log.info("Removing Headers from the text and adding the 'Cross-relation' where the footer starts.")
            raw_text = re.sub(self.header_Regex,"Usefull Information to Consider:\n", raw_text)
            self.log.info("Headers removed from the raw data.")
            return raw_text
        except Exception as e:

            raise CustomException(f"Failed to remove Headers from the text. Error: {str(e), sys}") from e
        
    def Clean(self) -> str:
        try:
            self._get_unusal_characters()
            text = self._clean_unusal_characters()
            text = self._remove_headers(text)
            return text

        except Exception as e:
            raise CustomException(f"Failed to clean the text. The Error: {str(e), sys}") from e