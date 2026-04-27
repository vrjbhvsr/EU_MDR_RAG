"""METADATA SCHEMA
===============
- document_name:    type: str,       nullable: No,   example: "eu_mdr_2017-745"
- document_type:    type: str,       nullable: No,   example: "regulation"
- chapter:          type: str,       nullable: Yes,  example: "Chapter II"
- article_number:   type: str,       nullable: Yes,  example: "Article 10"
- article_title:    type: str,       nullable: Yes,  example: "General obligations of manufacturers"
- annex:            type: str,       nullable: Yes,  example: "Annex VIII"
- section_header:   type: str,       nullable: Yes,  example: "Classification Rules"
- paragraph_number: type: str,       nullable: Yes,  example: "(3)(a)"
- page_number:      type: int,       nullable: No,   example: 31
- cross_references: type: list[str], nullable: Yes,  example: ["Article 10(3)", "Annex XIV"]"""