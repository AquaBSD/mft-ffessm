from .template import Template


class Comic(Template):

    def __init__(self, dedup_headings=False, la_overrides=None):
        super(Comic, self).__init__(
            dedup_headings=dedup_headings,
            la_overrides=la_overrides
        )

        self.footer_break = 50.0

    def cleanup(self, content):
        return content.strip().replace('(cid:1)', '-')

    def handle_heading(self, text):
        if 15.0 < text.height < 16.0:
            return 1

        if 11.03 < text.height < 11.04:
            return 2

        return 0

    def handle_indent(self, text, content):
        if 113.0 < text.x0:
            return (1, len(content) and content[0].isupper())

        return (0, False)

    def handle_ignored(self, content, in_table):
        if not in_table:
            return content.strip() in [
                u'(suite)',
                u'-'
            ]

        return False

    def handle_newline(self, content, in_table):
        if in_table:
            return content.startswith(u'- ') \
                or content.endswith(u'.')    \
                or content.endswith(u':')

        return False

    def handle_linebreaks(self, content, in_table):
        return not in_table and len(content)
