from src import PDF_Extractor, Text_Cleaner, Structure_Parser

PE = PDF_Extractor("data/raw/eu_mdr_2017-745.pdf")
raw_text, page_starts = PE.extract_text()

SP = Structure_Parser(raw_text, page_starts)
sm = SP.Create_Structure()


TC = Text_Cleaner(Doc_list=sm, raw_text=raw_text)
cleaned_text = TC.Clean()

