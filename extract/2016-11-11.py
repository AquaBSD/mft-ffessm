from pdfex.document import Document
from pdfex.templates.comic import Comic


Document.to_markdown('./n1.pdf', Comic(
    dedup_headings=True,
    la_overrides={
        '9': dict(
            char_margin=0.3
        )
    }
))
