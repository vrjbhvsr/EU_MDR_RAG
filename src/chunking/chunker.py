import json
import sys
import re
from typing import List
from pathlib import Path
from config.settings import ChunkingConfig
from src.utils import log, CustomException


class Chunker:
    def __init__(self, tokenizer, cleaned_docs: list[dict], cfg:ChunkingConfig):
        """Split parser output into <=max_tokens chunks, packed within each structural unit.

        Args:
            docs: cleaned section-wise docs from ingestion (page_content + metadata).
            cfg: ChunkingConfig (max_tokens, over_512_policy).
            tokenizer: a HF tokenizer with .encode(); injected, never module-global.

        Returns:
            Chunks as {"page_content": str, "metadata": dict}. No file I/O.

        Raises:
            Exception: if docs is empty.
        """
        
        if not cleaned_docs:
            raise CustomException("docs is empty, Nothing to chunk",sys)
        self.tokenizer = tokenizer
        self.docs = cleaned_docs
        self.config = cfg
        self.log = log()

    def _token_length(self, page_content: str) -> int:
        """
        Return the token length of the passed docs.

        Args:
            page_content: page_content from the docs

        Return:
            token length.
        """
        return len(self.tokenizer.encode(page_content))

    def _get_split_levels(self, page_content: str) -> List[str]:
        """
        Determine the split levels for the given page content based on the configured patterns.
        It checks the levels in order of priority and returns a list of matching split levels.
        it divides the page_content based on 1. 1.1, 1.1.1, Part (a), (1), —, etc. patterns in the config.

        Args:
            page_content: The content of the page to analyze.

        Returns:
            List[str]: A list of split levels that match the patterns in the configuration.
        """
        split_levels = []
    
        #self.log.info("Starting split level determination for the given page content.")
        if self._token_length(page_content) <= self.config.max_tokens:
            #self.log.info("Page content is within token limit, no splitting required.")
            return ['no_split']
        else:
            #self.log.info("Page content exceeds token limit, checking for split patterns. Token length: {}".format(self._token_length(page_content)))
            pass

        if re.search(self.config.patterns['part'], page_content):
            split_levels.append("part")

        if re.search(self.config.patterns['simple'], page_content):
            split_levels.append("simple")

        if re.search(self.config.patterns['decimal'], page_content):
            split_levels.append("decimal")

        if re.search(self.config.patterns['triple'], page_content):
            split_levels.append("triple")

        if re.search(self.config.patterns['paren_letter'], page_content):
            split_levels.append("paren_letter")

        if re.search(self.config.patterns['paren_num'], page_content):
            split_levels.append("paren_num")

        if re.search(self.config.patterns['bullet'], page_content):
            split_levels.append("bullet")

        #self.log.info(f"Split levels determined successfully: {split_levels}")

        return split_levels
        
       

    def _get_text_pieces(self, pattern: any, text: str) -> List[str]:
        """
        Split the text into pieces based on the provided patterns.

        This function take a single regex pattern and splits the text into pieces based on that pattern. It collects the matched pieces along with their start and end positions, and returns a list of text pieces obtained after splitting.

        Args:
            patterns: A list of regex patterns to split the text.
            text: The text to be split.

        Returns:
            List[str]: A list of text pieces obtained after splitting.
        """
        matches = []   # collect the matched pieces abd their start and end positions
        pieces = []    # collect the text pieces

        # regex's finditer returns an iterator yielding match objects over all non-overlapping matches for the RE pattern in string.

        search = re.finditer(pattern, text, re.M)

        for match in search:
            matches.append((match.start(), match.group()))

        if not matches:
            return [text]

        if matches and matches[0][0] > 0:
            matches.insert(0, text[0:matches[0][0]])  # if the first match doesn't start at the beginning of the text, add the text before the first match as a piece


        # iterate through matches and use their start postions to slice the text into pieces
        for i, mark in enumerate(matches):
            if isinstance(mark, tuple):
                if i < len(matches) - 1:
                    pieces.append(text[mark[0]:matches[i + 1][0]])
                else:
                    pieces.append(text[mark[0]:])  # add the last piece from the last match to the end of the text

        return pieces
        

    def _create_chunk(self, text: str, metadata: dict) -> dict:
        """
        Create a chunk with the given text and metadata.

        Args:
            text: The text content of the chunk.
            metadata: The metadata associated with the chunk.

        Returns:
            dict: A dictionary representing the chunk with 'page_content' and 'metadata'.
        """
        return {"page_content": text, "metadata": metadata}

    def _pack(self, sub_chunks: List[dict], max_tokens: int) -> List[dict]:
        """
        Pack sub-chunks into larger chunks without exceeding the max_tokens limit.
        This function takes the list of sub-chunks and iteratively adds them to a buffer until adding another sub-chunk would exceed the max_tokens limit. When that happens, it flushes the buffer into a packed chunk and starts a new buffer.

        Args:
            sub_chunks: List of sub-chunk dictionaries to be packed.
            max_tokens: Maximum number of tokens allowed in a packed chunk. 
        """

        packed_chunks = []
        buffer_chunk = ""
        buffer_metadata = dict()

        def flush():
            """
            Flush the buffer and add the current chunk to the packed chunks. This function is called when the buffer exceeds the max_tokens limit or when all sub-chunks have been processed. It creates a new chunk with the current buffer content and metadata, calculates its token length, and appends it to the packed_chunks list. After flushing, it resets the buffer and metadata for the next set of sub-chunks.
            """
            buffer_metadata['token_length'] = self._token_length(buffer_chunk)
            packed_chunks.append(self._create_chunk(buffer_chunk, buffer_metadata.copy()))

        for i, chunk in enumerate(sub_chunks):
            candidate_chunk = buffer_chunk + "\n" + chunk.get("page_content") if buffer_chunk else chunk.get("page_content")

            if self._token_length(candidate_chunk) > max_tokens and buffer_chunk:
                flush()
                buffer_chunk = chunk.get("page_content")
                buffer_metadata = chunk.get("metadata").copy()

            else:
                if not buffer_chunk:
                    buffer_metadata = chunk.get("metadata").copy()
                buffer_chunk = candidate_chunk

        if buffer_chunk:
            flush()

        total = len(packed_chunks)
        #self.log.info(f"Packed {len(sub_chunks)} sub-chunks into {total} chunks with max_tokens={max_tokens}.")
        for number, c in (enumerate(packed_chunks, start = 1)):
            c['metadata']['subchunk_id'] = number
            c['metadata']['total_subchunks'] = total

        return packed_chunks

    def _break_the_docs(self, page_content: str, metadata: dict, split_levels: List[str], prefix: str = "",) -> List[dict]:
        """
        Break the page content into smaller chunks based on the configured split levels and patterns.
        This function first determines the appropriate split levels for the given page content. It then iteratively splits the content based on the identified patterns, creating sub-chunks. If any sub-chunk exceeds the maximum token limit, it is further split into smaller chunks. Finally, all sub-chunks are packed into larger chunks without exceeding the max_tokens limit.

        Basically, if the strucutral unit is over and chunk length is less than max_tokens, it is returned as is. If the strucutral unit is over and chunk length is more than max_tokens, it is split into smaller chunks based on the configured patterns. 

        Args:
            page_content: The content of the page to be broken into chunks.
            metadata: The metadata associated with the page content.
            split_levels: The levels at which to split the page content.
            prefix: An optional prefix to be added to the metadata of each chunk.

        Returns:
            List[dict]: A list of chunk dictionaries, each containing 'page_content' and 'metadata'.
        """
        
        #split_levels = self._get_split_levels(page_content)         # Get the split levels for the page content based on the configured patterns.


        # If the page content is within the max_tokens limit, return it as a single chunk with the provided prefix (if any) and updated metadata.
        if self._token_length(page_content) <= self.config.max_tokens:
            if prefix:
                final_content = f"{prefix}\n{page_content}"
            else:
                final_content = page_content

            new_metadata = metadata.copy()
            new_metadata['token_length'] = self._token_length(final_content)
            #self.log.info("Page content is within token limit, returning as a single chunk.")
            return [self._create_chunk(final_content, new_metadata)]

        # If no split levels are found, return the entire page content as a single chunk with the provided prefix (if any) and updated metadata.
        if not split_levels:
            if prefix:
                final_content = f"{prefix}\n{page_content}"
            else:
                final_content = page_content

            new_metadata = metadata.copy()
            new_metadata['token_length'] = self._token_length(final_content)
            #self.log.info("No split levels found, returning as a single chunk.")
            return [self._create_chunk(final_content, new_metadata)]

        # If split levels are found, iteratively split the page content based on the identified patterns. For each split level, the content is divided into sub-chunks. If any sub-chunk exceeds the maximum token limit, it is further split into smaller chunks. Finally, all sub-chunks are packed into larger chunks without exceeding the max_tokens limit.

        current_level = split_levels[0]
        remaining_levels = split_levels[1:]

        text_pieces = self._get_text_pieces(pattern= self.config.patterns[current_level], text= page_content)
        if not text_pieces:
            text_pieces = [page_content]

        sub_chunks = []

        for piece in text_pieces:
            # If the current split level has a corresponding pattern, attempt to match it in the piece. If a match is found, extract the header and create a new prefix by appending the header to the existing prefix. This helps to describe the context of the chunk for the model.
            match = re.match(self.config.patterns[current_level], piece)
            if match:
                header = match.group()
                new_prefix = prefix + "-" + header if prefix else header
                piece = piece.replace(header, "")

            else:
                new_prefix = prefix
    
            sub_chunks.extend(self._break_the_docs(piece, metadata, remaining_levels, prefix=new_prefix))
        return self._pack(sub_chunks, max_tokens=self.config.max_tokens)
            
        #self.log.info("Finished breaking the docs into chunks successfully.")
  
    def chunk_docs(self) -> List[dict]:
        """
        Chunk the cleaned documents into smaller pieces based on the configured split levels and patterns.
        This function iterates through each document in the cleaned_docs list, breaking the page content into smaller chunks using the _break_the_docs method. It collects all the resulting chunks and returns them as a list.

        Returns:
            List[dict]: A list of chunk dictionaries, each containing 'page_content' and 'metadata'.
        """
        try:    
            all_chunks = []
            for doc in self.docs:
                page_content = doc.get("page_content")
                metadata = doc.get("metadata")
                split_levels = self._get_split_levels(page_content)
                chunks = self._break_the_docs(page_content, metadata, split_levels)
                all_chunks.extend(chunks)

            over_512_chunks = [chunk for chunk in all_chunks if chunk['metadata']['token_length'] > 512]
            if over_512_chunks:
                self.log.warning(f"Found {len(over_512_chunks)} chunks with token length > 512.")
            self.log.info(f"Successfully chunked {len(self.docs)} documents into {len(all_chunks)} total chunks.")
            docs = [doc for doc in all_chunks if not self._is_header_only(doc)]
            self.log.info(f"Removed {len(all_chunks) - len(docs)} header-only documents, leaving {len(docs)} documents for chunking.")
            return docs
        except Exception as e:
            self.log.exception(f"An error occurred while chunking documents: {str(e)}")
            raise CustomException(f"An error occurred while chunking documents: {str(e)}",sys) from e

    def _norm(self, s):
        return " ".join(str(s or "").split())

    def _is_header_only(self, doc: dict) -> bool:
        """
        Check if the given text consists only of a header based on the configured patterns.
        This function checks if the provided text matches any of the configured header patterns. If a match is found, it indicates that the text is likely a header and returns True; otherwise, it returns False.

        Args:
            doc: The document dictionary containing the text to be checked for header-only content.

        Returns:
            bool: True if the text is header-only, False otherwise.
        """
        body = self._norm(doc.get("page_content"))
        metadata = doc.get("metadata")

        def field(key):
                v = metadata.get(key, '')
                return str(v) if v is not None else ''
        
        candidates = []
        for mk, tk in (('section', 'section_title'),
                        ('chapter', 'chapter_title'),
                        ('annex',   'annex_title')):
            marker, title = field(mk), field(tk)
            if marker or title:
                candidates.append(self._norm(marker + " " + title))
                candidates.append(self._norm(marker + title))
        title_only = body in candidates
    
        bare = re.fullmatch(
            r'(?:(?:Article\s+\d+|ANNEX\s+[IVXLC]+|CHAPTER\s+[IVXLC]+|SECTION\s+\d+)\s+)*'  # leading noise
            r'(?:SECTION\s+\d+|CHAPTER\s+[IVXLC]+|ANNEX\s+[IVXLC]+)\s+'                     # real marker
            r'[A-Z][A-Za-z0-9 ,()&/\'’\-–]+',                                              # title, no periods
            body
        )
        return bool(title_only or bare)
    
    