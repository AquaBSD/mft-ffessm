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

    def handle_indent(self, text):
        if 113.0 < text.x0:
            first_char = text.get_text()[0]
            return (1, first_char and first_char.isupper())

        return (0, False)

    def handle_ignored(self, content, in_table):
        if not in_table:
            return content in [
                '- \n'
            ]

        return False
