import re

FIELD_PATTERNS = {
    "annex":   r"ANNEX [IVXL]+",
    "chapter": r"CHAPTER [IVXL]+",
    "section": r"SECTION \d+",
    "article": r"Article \d+",
    "page_no": r"page no:\s*(\d+(?:-\d+)?)",
}

def _extract(text):
    """Pull all identifier fields out of one string."""
    out = {}
    for field, pat in FIELD_PATTERNS.items():
        m = re.search(pat, text)
        if m:
            out[field] = m.group(1) if m.groups() else m.group()
    return out


def _format(src):
    """Build a clean citation from a source dict."""
    parts = [src[k] for k in ("article", "annex", "chapter") if src.get(k)]
    return f"[{' '.join(parts)}, page no: {src.get('page_no', '')}]"


def citation_validator(answer, chunks, sep="-" * 120):
    sources = [_extract(c.split("</CHUNK_SOURCE")[0]) for c in chunks.split(sep)]
    by_page = {s["page_no"]: s for s in sources if "page_no" in s}   # O(1) lookup

    results = []
    for cited in re.findall(r"\[([^\]]+)\]", answer):
        c = _extract(cited)

        # tier 1: full agreement with some source
        match = next((s for s in sources if all(c[k] == s.get(k) for k in c)), None)
        # tier 2: page is the trusted anchor
        match = match or by_page.get(c.get("page_no"))

        results.append(_format(match) if match else f"[Unverified: {cited}]")
    return results