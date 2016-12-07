from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator


class Document(object):
    def __init__(self, f):
        self.file = f

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
