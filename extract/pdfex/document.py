from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator


class Document(object):

    def __init__(self, filename):
        self.file = open(filename, 'rb')

        rsrcmgr = PDFResourceManager()
        self.device = PDFPageAggregator(rsrcmgr, laparams=LAParams())
        self.interpreter = PDFPageInterpreter(rsrcmgr, self.device)

    def extract(self):
        pages = {}

        for page in PDFPage.get_pages(self.file):
            self.interpreter.process_page(page)
            layout = self.device.get_result()
            pages[layout.pageid] = layout

        return pages
