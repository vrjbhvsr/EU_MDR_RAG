from src.utils import log, CustomException
from config.settings import get_settings



class prompt_Configuration:
    def __init__(self):
        settings = get_settings()
        self.config = settings.generation
        self.log = log()

    def _chunk_source(self, metadata:dict) -> str:
            def label(number, title):
                if title:
                    return f"{number} ({title})"
                return number
            article= metadata.get('article', "").strip()
            annex = metadata.get("annex","").strip()
            chapter = str(metadata.get('chapter',"")).strip()
            chapter_title = metadata.get("chapter_title", "").strip()
            annex_title = metadata.get("annex_title","").strip()
            article_title = metadata.get("article_title", "").strip()
            section = metadata.get("section","").strip()
            section_title = metadata.get("section_title", "").strip()
            page_range = "page no: " + str(metadata.get("page_number"))
    
            if chapter == "0" and chapter_title == "preamble":
                parts = []
                if page_range: parts.append(page_range)
                source = "EU MDR Preamble, ".join(parts)
            
            elif article:
                parts = []
                if chapter: parts.append(label(chapter, chapter_title))
                if section: parts.append(label(section,section_title))
                parts.append(label(article, article_title))
                if page_range: parts.append(page_range)
                source =  ", ".join(parts)
    
            elif annex:
                parts = [label(annex, annex_title)]
                if page_range: parts.append(page_range)
                if chapter: parts.append(label(chapter, chapter_title))
                source =  ", ".join(parts)
    
            return source

    def _create_model_context(self,retrieved_chunks: list[dict]):
        list_of_chunks = []
        page_content= retrieved_chunks['page_content']
        metadata = retrieved_chunks['metadata']
        for content, meta in zip(page_content, metadata):
            source = self._chunk_source(metadata=metadata)
            page_c = "<CHUNK_SOURCE: " + source + "</CHUNK_SOURCE>\n" + content + "</CHUNK>"
            list_of_chunks.append(page_c)

        context = (f"\n"+"-"*120 + "\n").join(list_of_chunks)
        return context

    def create_prompt(self,tokenizer, question: str, retriever):
        results = retriever.retrieve(question)
        model_context= self._create_model_context(retrieved_chunks=results)
        with open(self.config.prompt_file, 'r') as f:
            prompt = f.readlines()

        prompt.insert(prompt.index("# Final instruction\n"), f"<SOURCES:>\n{model_context} \n</SOURCES>\n")
        prompt.insert(prompt.index("# Final instruction\n"), f"<QUESTION:>\n{question} \n</QUESTION>\n")
        log.info(f"The token length of the model input: {len(tokenizer.encode(''.join(prompt)))}")

        return "".join(prompt)

