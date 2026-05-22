from src import PDF_Extractor, Text_Cleaner

PE = PDF_Extractor("data/raw/eu_mdr_2017-745.pdf")
raw_text = PE.extract_text()

TC = Text_Cleaner(raw_text)
cleaned_text = TC.Clean()
