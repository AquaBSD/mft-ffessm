import os

from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator

from .element import Element


class Document(object):

    def __init__(self, filename):
        self.file = open(filename, 'rb')

        rsrcmgr = PDFResourceManager()
        self.device = PDFPageAggregator(rsrcmgr)
        self.interpreter = PDFPageInterpreter(rsrcmgr, self.device)

    def extract(self):
        pages = {}

        for page in PDFPage.get_pages(self.file):
            self.interpreter.process_page(page)
            layout = self.device.get_result()
            pages[layout.pageid] = layout

        return pages

    @staticmethod
    def to_markdown(path, template):
        doc = Document(path)
        out = os.path.splitext(path)[0] + '.md'

        with open(out, 'w') as output:
            for page_num, page in doc.extract().items():
                page_element = Element()
                for element in page_element.parse(page, page_num, template):
                    output.write(template.to_markdown(element).encode('utf-8'))
