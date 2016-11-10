import os
import sys

from pdfex.document import Document
from pdfex.element import Element
from pdfex.templates.comic import Comic


def pdf_to_markdown(path, template):
    doc = Document(path)
    out = os.path.splitext(path)[0] + '.md'

    with open(out, 'w') as output:
        for page_num, page in doc.extract().items():
            page_element = Element()
            for element in page_element.parse(page, page_num, template):
                output.write(template.to_markdown(element).encode('utf-8'))


if __name__ == '__main__':
    pdf_to_markdown('./n1.pdf', Comic(
        dedup_headings=True,
        la_overrides={
            '9': dict(
                char_margin=0.3
            )
        }
    ))
