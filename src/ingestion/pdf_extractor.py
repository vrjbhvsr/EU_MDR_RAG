import pymupdf
import os
from pathlib import Path
import json
import sys
from src.utils import log, CustomException

class PDF_Extractor:

    def __init__(self, pdf_path: Path | str):
        """Initialize the PDF_Extractor class with the path to the PDF document.
        This method sets up the necessary attributes for the PDF extraction process, including the base directory, PDF path, cache directory, and initializes the raw text and table content. It also opens the PDF document using pymupdf for further processing.
        Args:
            pdf_path (Path | str): The path to the PDF document to be extracted. This can be provided as a string or a Path object.
        Returns:
            Object: An instance of the PDF_Extractor class initialized with the specified PDF document and ready for text extraction.
            """
        self.base_dir = Path(__file__).resolve().parents[2]
        self.pdf_path = Path(pdf_path) if isinstance(pdf_path,str) else pdf_path
        self.pdf_path = self.base_dir/self.pdf_path if self.base_dir != self.pdf_path.parents[2] else self.pdf_path
        self.cache_dir = Path(self.base_dir/"data"/"cache")
        self.raw_text = ""
        self.raw_table=""
        self.log = log()
        try:
            self.docs = pymupdf.open(self.pdf_path)
            self.log.info(f"PDF document '{self.pdf_path}' opened successfully.")
        except Exception as e:
            self.log.exception(f"Failed to open PDF document '{self.pdf_path}'. Error: {str(e)}")
            raise CustomException(f"Failed to open PDF document '{self.pdf_path}'. Error: {str(e),sys}") from e

    def _find_tables(self):
        """Find tables in the PDF and cache their content and coordinates.
        This method iterates through each page of the PDF, identifies tables, and stores their content and coordinates in a cache file (tables.json) for later use during text extraction.
        The cache file is structured as a list of dictionaries, where each dictionary contains the page number, table ID, table content in markdown format, and the coordinates of the table on the page.
        The method ensures that the cache directory exists before attempting to write the cache file. If the cache file already exists, it will be overwritten with the new table information.
        
        Returns:
            None"""
        try:
            self.log.info("Starting table extraction and caching process.")
            if not self.cache_dir.is_dir():
                self.cache_dir.mkdir(parents=True)
            table_cache = self.cache_dir/"tables.json"
            page_tables =[]
            for i, page in enumerate(self.docs):
                tables = page.find_tables().tables

                if tables:
                    for j,table in enumerate(tables):
                        page_tables.append(                    
                        {
                            "page_number": i+1,
                            "table_id": j,
                            "table_content":table.to_markdown(),
                            "table_coordinates": table.bbox, 
                        } 
                        )
            with open(table_cache, 'w') as f:
                json.dump(page_tables,f,indent=4)
            self.log.info("Table extraction and caching process completed successfully.")

        except Exception as e:
            self.log.exception(f"Failed to extract and cache tables from PDF document '{self.pdf_path}'. Error: {str(e)}")
            raise CustomException(f"Failed to extract and cache tables from PDF document '{self.pdf_path}'. Error: {str(e)}") from e
    
    def _load_table_cache(self) -> list[dict]:
        """Load the cached table information from the cache file (tables.json).
        This method checks for the existence of the cache file and loads its content if it exists and
        is not empty.
        Returns:
            list: A list of dictionaries containing the cached table information, or an empty list if the cache file does not exist or is empty."""
        cached = self.cache_dir/"tables.json" 
        try:
            if not cached.is_file():
                return []
            if not cached.stat().st_size:
                return []
            with open(cached,'r') as f:
                cache = json.load(f)
            self.log.info(f"Table cache loaded successfully from '{cached}'.")
            return cache
        except Exception as e:
            self.log.exception(f"Failed to load table cache from '{cached}'. Error: {str(e)}")
            raise CustomException(f"Failed to load table cache from '{cached}'. Error: {str(e)}",sys) from e

    def _intersect(self,coords1, coords2) -> bool:
        """Check if two rectangles defined by their coordinates intersect.
        This method takes the coordinates of two rectangles (defined by their top-left and bottom-right corners
        and checks if they intersect. The coordinates are expected to be in the format (x1, y1, x2, y2), where (x1, y1) represents the top-left corner and (x2, y2) represents the bottom-right corner of the rectangle.
        The method returns True if the rectangles intersect and False otherwise.
        Args:
            coords1 (tuple): A tuple containing the coordinates of the first rectangle (x1, y1, x2, y2).
            coords2 (tuple): A tuple containing the coordinates of the second rectangle (x1, y1, x2, y2).   
        
        Returns:
            bool: True if the rectangles intersect, False otherwise."""
        
        try:
            x1_1, y1_1, x2_1, y2_1 = coords1
            x1_2, y1_2, x2_2, y2_2 = coords2

            if (x1_1 < x2_2 and x2_1 > x1_2 and
                y1_1 < y2_2 and y2_1 > y1_2):
                return True
            
            return False
        except Exception as e:
            self.log.exception(f"Failed to check intersection between coordinates {coords1} and {coords2}. Error: {str(e)}")
            raise CustomException(f"Failed to check intersection between coordinates {coords1} and {coords2}. Error: {str(e)}",sys) from e
    
    def extract_text(self) -> str:
        """Extract text from the PDF while excluding text that is part of tables.
        This method first checks if the table cache is available and loads it. If the cache is
        not available, it calls the _find_tables method to populate the cache. Then, it iterates through each page of the PDF and checks if there are any tables on that page based on the cached information. If tables are present, it checks each text block on the page against the coordinates of the tables to determine if the text block is part of a table or not. If a text block does not intersect with any table coordinates, it is considered as text outside the table and is added to the raw_text string. If there are no tables on the page, all text from that page is added to raw_text. Finally, the method returns the extracted text as a single string.
        Returns:
            str: The extracted text from the PDF, excluding text that is part of tables.
        """
        try:
            self.log.info(f"Starting text extraction from PDF document '{self.pdf_path}'.")
            if not self._load_table_cache():
                self._find_tables()
            cache = self._load_table_cache()
            raw_text = ""
            table_pages = [i['page_number'] for i in cache]
            for page_num, page in enumerate(self.docs):
                p = page_num + 1
                if cache:
                    if p in table_pages:
                        current_page_coords = [i['table_coordinates'] 
                                                for i in cache 
                                                if i['page_number'] == p]
                        
                        # if the coordinates of the text block do not intersect with the table coordinates, then we can consider it as text outside the table
                        for i in page.get_text('blocks'):
                            x1,y1,x2,y2 = i[:4]
                            if not any(self._intersect((x1,y1,x2,y2),table_coord) for table_coord in current_page_coords):
                                text = i[4]
                                raw_text += text + "\n"
                    else:
                        text = str(page.get_text())
                        raw_text += text + "\n"
                else:
                    raw_text += str(page.get_text()) + "\n"
            self.log.info(f"Text extraction from PDF document '{self.pdf_path}' completed successfully.")
            return raw_text
        except Exception as e:
            self.log.exception(f"Failed to extract text from PDF document '{self.pdf_path}'. Error: {str(e)}")
            raise CustomException(f"Failed to extract text from PDF document '{self.pdf_path}'. Error: {str(e)}", sys) from e
                  
