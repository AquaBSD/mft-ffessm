import sys

from pdfex.document import Document
from pdfex.element import Element
from pdfex.templates.comic import Comic


if __name__ == '__main__':
    doc = Document(sys.argv[1])

    template = Comic(dedup_headings=True)

    for page_num, page in doc.extract().items():
        page_element = Element()
        for element in page_element.parse(page, template.footer_break):
            print template.to_markdown(element).encode('utf-8')
