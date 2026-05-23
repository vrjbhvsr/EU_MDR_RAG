import os
import sys
import re
import bisect
from pathlib import Path
from src.utils import log, CustomException
from src.ingestion import PDF_Extractor, Text_Cleaner

class Structure_Parser:
    def __init__(self, raw_text: str, page_starts: list[int]):
        """Initialize the Structure_Parser class with the raw text extracted from a PDF document.
        This method sets up the necessary attributes for parsing the structure of the document, including the raw text and a logger for tracking the parsing process. 
        The raw text is expected to be a string containing the entire content of the PDF document, which will be processed to identify sections, subsections, and other structural elements.
        Args:
            raw_text (str): The raw text extracted from the PDF document. This should be a single string containing all the text content of the document, which will be analyzed to determine its structure.
        Returns:
            Object: An instance of the Structure_Parser class initialized with the provided raw text and ready for parsing the document's structure.
        """
        self.raw_text = raw_text
        self.page_list = page_starts
        self.Annex_Regex = "^(ANNEX [IVX]+) \n(.+)"
        self.Chapter_Regex = "^(CHAPTER [IVX]+) \n(.+)"
        self.Section_Regex = "^(SECTION [0-9]+) \n(.+)"
        self.Article_Regex = "^(Article [0-9]+) \n(?!Article)(?!— )(.+)"
        self.markers = list()
        self.log = log()

    def _get_title_markers(self):
        """
        Identify and extract structural markers from the raw text of a PDF document. 
        This method uses regular expressions to search for specific patterns that indicate the presence of structural elements such as annexes, chapters, sections, and articles. 
        The identified markers are stored in a list for further processing.
        The method iterates through the raw text, applying the defined regular expressions to find matches for each type of structural element. 
        When a match is found, the corresponding marker (e.g., "ANNEX I", "CHAPTER II", "SECTION 3", "Article 4") is extracted and added to the list of markers. 
        This process helps in organizing the content of the document based on its structure, which can be useful for tasks such as summarization, indexing, or information retrieval.
        Returns:
            List[str]: A list of strings representing the identified structural markers in the document. Each marker corresponds to a specific section or element within the document's hierarchy.
        """
        try:
            self.log.info("Extracting title markers from raw text.")
            for reg in [self.Annex_Regex, self.Article_Regex, self.Chapter_Regex, self.Section_Regex]:
                iterator = re.finditer(reg, self.raw_text, re.M)           # Use re.finditer to find all matches of the regular expression in the raw text, allowing for multiline matching with the re.M flag.                                                                                                                                                                                                                                                                                                      
                for match in iterator:
                    if reg == self.Annex_Regex:
                        self.markers.append((match.start(), "Annex", match.group(), match.end()))
                    if reg == self.Chapter_Regex:
                        self.markers.append((match.start(), "Chapter", match.group(), match.end()))
                    if reg == self.Section_Regex:
                        self.markers.append((match.start(), "Section", match.group(), match.end()))
                    if reg == self.Article_Regex:
                        self.markers.append((match.start(), "Article", match.group(), match.end()))
            sorted_markers = sorted(self.markers)
            self.log.info(f"The List of sorted markers: {sorted_markers[:3]}, Total Markers are : {len(sorted_markers)}")
            return sorted_markers
        except Exception as e:
            self.log.exception("Failed to get all the markers.")
            raise CustomException(f"Failed to Get the markers due to the Error: {str(e),sys}") from e

    def Create_Structure(self):
        """Create a structured representation of the document based on the identified markers. This method organizes the content of the document into a hierarchical structure, such as a tree or nested dictionary, using the markers extracted from the raw text. The structure allows for easy navigation and retrieval of specific sections or elements within the document.
        The method processes the list of markers, determining their relationships (e.g., which sections belong to which chapters) and building a structured representation accordingly. This can involve creating nodes for each marker and linking them based on their positions in the document. The resulting structure can be used for various applications, such as generating summaries, creating an index, or facilitating information retrieval.
        Returns:
            Object: A structured representation of the document, such as a tree or nested dictionary, that organizes the content based on the identified markers. This structure allows for efficient navigation and access to specific sections or elements within the document.
        """
        markers = self._get_title_markers()  # Get the list of markers to use for structuring the document.
        print(f"Total Markers: {len(markers)}")  # Print the total number of markers identified for debugging purposes.
        Documents = []   # Collect all the documents with metadata for next process
        current_text = ""  # Initiate with empty string, Used to hold the content between markers. Resets when hit next marker.
        chapter = ""    # Initiate chapter as empty string, when hits chapter marker holds temporary, resets when hits next chapter marker.
        section = ""   # Initiate section as empty string, when hits section marker holds temporary, resets when hits next section marker.
        section_title = ""  # Initiate section header as empty string, when hits section marker holds temporary, resets when hits next section marker.
        end_loc = markers[-1][-1]  # Get the end location of the last marker to capture any remaining text after the last marker.
        metadata = {"document_name": "eu_mdr_2017-745.pdf", "document_type": "Regulations", "chapter": "", "chapter_title": "", "article": "", "article_title": "", "annex": "","annex_title": "", "section": "", "section_title": "", "page_number": "", "cross_references": ""}
        
        Page_cont = self.raw_text[0:markers[0][0]]  # Capture any text before the first marker as page content.
        meta_copy = metadata.copy()  # Create a copy of the metadata dictionary to modify for each document.
        meta_copy['chapter'] = 0 # Set the chapter metadata to 0 for the content before the first marker, indicating that it does not belong to any chapter.
        meta_copy['chapter_title'] = 'preamble'  # Set the chapter title metadata to 'preamble' for the content before the first marker.
        meta_copy['page_number'] = bisect.bisect(self.page_list, markers[0][0]-1)  # Determine the page number for the content before the first marker using the page starts list.
        Documents.append({"page_content":Page_cont,"metadata": meta_copy})  # Append the content before the first marker
        try:
            self.log.info("Creating a structured representation of the document based on the identified markers.")
            for i, marker in enumerate(markers):   # Iterate through the list of markers to build the structured representation of the document.
                if i < len(markers) - 1:
                    current_text = self.raw_text[marker[0]:markers[i+1][0]]  # Extract the text between the current marker and the next marker.
                else:
                    current_text = self.raw_text[marker[0]:]  # For the last marker, extract the text from the marker's position to the end of the document.
                new_metadata = metadata.copy()          # Create a copy of the metadata dictionary to modify for the current marker.
                if marker[1] == "Annex":                # If the marker indicates an annex, extract the annex number and title, determine the page number, and update the metadata accordingly.
                    Annex = marker[2].split('\n')[0]
                    Annex_title = marker[2].split('\n')[1]
                    Annex_location = marker[0]
                    page_num = bisect.bisect(self.page_list, Annex_location)
                    new_metadata['page_number'] = page_num
                    new_metadata['annex'] = Annex
                    new_metadata['annex_title'] = Annex_title
                    metadata.update(new_metadata)
                    Documents.append({"page_content": current_text, "metadata": new_metadata})

                    # Reset chapter, article, and section metadata for the content within the annex, as they reset every new annex.
                    metadata['chapter'] = ""
                    metadata['chapter_title'] = ""
                    metadata['article'] = ""
                    metadata['article_title'] = ""
                    metadata['section'] = ""
                    metadata['section_title'] = ""

                elif marker[1] == "Chapter":            # If the marker indicates a chapter, extract the chapter number and title, determine the page number, and update the metadata accordingly.
                    chapter = marker[2].split("\n")[0]
                    chapter_title = marker[2].split('\n')[1]
                    chapter_location = marker[0]
                    page_num = bisect.bisect(self.page_list, chapter_location)
                    new_metadata['page_number'] = page_num
                    new_metadata['chapter'] = chapter
                    new_metadata['chapter_title'] = chapter_title
                    metadata.update(new_metadata)
                    Documents.append({"page_content": current_text, "metadata": new_metadata})
                    metadata['section'] = ""
                    metadata['section_title'] = ""
                
                elif marker[1] == "Section":            # If the marker indicates a section, extract the section number and title, determine the page number, and update the metadata accordingly.
                    section = marker[2].split("\n")[0]
                    section_title = marker[2].split("\n")[1]
                    new_metadata['section'] = section
                    new_metadata['section_title'] = section_title
                    sec_location = marker[0]
                    page_num = bisect.bisect(self.page_list,sec_location)
                    new_metadata['page_number'] = page_num
                    metadata.update(new_metadata)
                    Documents.append({"page_content": current_text, "metadata": new_metadata})
                
                elif marker[1] == "Article":            # If the marker indicates an article, extract the article number and title, determine the page number, and update the metadata accordingly.
                    article = marker[2].split("\n")[0]
                    article_title = marker[2].split("\n")[1]
                    new_metadata['article'] = article
                    new_metadata['article_title'] = article_title
                    art_location = marker[0]
                    page_num = bisect.bisect(self.page_list,art_location)
                    new_metadata['page_number'] = page_num
                    metadata.update(new_metadata)
                    Documents.append({"page_content": current_text, "metadata": new_metadata})

            return Documents
        except Exception as e:
            self.log.exception("Failed to create the structure.")
            raise CustomException(f"Failed to Create the structure due to the Error: {str(e),sys}") from e              
        

