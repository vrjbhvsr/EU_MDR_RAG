import os
import sys
import re
import bisect
from pathlib import Path
from src.utils import log, CustomException
from src.ingestion import PDF_Extractor, Text_Cleaner

class Structure_Parser:
    def __init__(self, raw_text: str):
        """Initialize the Structure_Parser class with the raw text extracted from a PDF document.
        This method sets up the necessary attributes for parsing the structure of the document, including the raw text and a logger for tracking the parsing process. The raw text is expected to be a string containing the entire content of the PDF document, which will be processed to identify sections, subsections, and other structural elements.
        Args:
            raw_text (str): The raw text extracted from the PDF document. This should be a single string containing all the text content of the document, which will be analyzed to determine its structure.
        Returns:
            Object: An instance of the Structure_Parser class initialized with the provided raw text and ready for parsing the document's structure.
        """
        self.raw_text = raw_text
        self.log = log()

    def _get_title_markers(self):

