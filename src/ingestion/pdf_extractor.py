import pymupdf
import os
from pathlib import Path
import json
import sys

class PDF_Extractor:
    def __init__(self, pdf_path: Path | str):
        self.base_dir = Path(__file__).resolve().parents[2]
        self.pdf_path = Path(pdf_path) if isinstance(pdf_path,str) else pdf_path
        self.pdf_path = self.base_dir/self.pdf_path if self.base_dir != self.pdf_path.parents[2] else self.pdf_path
        self.cache_dir = Path(self.base_dir/"data"/"cache")
        self.raw_text = ""
        self.raw_table=""
        self.docs = pymupdf.open(self.pdf_path)

    def _find_tables(self):
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
    
    def _load_table_cache(self):
        cached = self.cache_dir/"tables.json" 
        if not cached.is_file():
            return []
        if not cached.stat().st_size:
            return []
        with open(cached,'r') as f:
            cache = json.load(f)

        return cache

    def _intersect(self,coords1, coords2):
        x1_1, y1_1, x2_1, y2_1 = coords1
        x1_2, y1_2, x2_2, y2_2 = coords2

        if (x1_1 < x2_2 and x2_1 > x1_2 and
            y1_1 < y2_2 and y2_1 > y1_2):
            return True
        return False
    
    def extract_text(self):
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
        return raw_text

                  
if __name__ == "__main__":
    PE = PDF_Extractor(pdf_path=sys.argv[1])
    print(PE.extract_text())