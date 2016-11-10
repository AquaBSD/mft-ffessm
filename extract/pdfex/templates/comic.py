import re

from template import Template

class Comic(Template):
    def __init__(self, *args, **kwargs):
        super(Comic, self).__init__(args, kwargs)

        self.footer_break = 50.0

    def cleanup(self, content):
        return content.replace('(cid:1)', '-')

    def handle_heading(self, text):
        if 15.0 < text.height < 16.0:
            return 1

        if 11.03 < text.height < 11.04:
            return 2

        return 0
