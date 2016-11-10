import tabulate

from pdfminer.layout import LAParams, LTChar


class Template(object):

    def __init__(self, footer_break=None, dedup_headings=False):
        self.footer_break = footer_break
        self.dedup_headings = dedup_headings

        self.headings = {}

    def to_markdown(self, element):
        element_type = element.get_type()

        if element_type == 'paragraph':
            return self._generate_paragraph(element)
        elif element_type == 'table':
            return self._generate_table(element)
        else:
            raise Exception('Unsupported markdown type')

    def handle_font(self, text, content):
        offset = 0
        start_bold = -1
        start_italic = -1

        def not_space(idx):
            return not content[idx].isspace()

        for index, char in enumerate(text):
            if type(char) == LTChar:
                bold = self.is_bold(char)
                italic = self.is_italic(char)
                good = not_space(index + offset)

                if bold and good and start_bold == -1:
                    start_bold = index
                    content = content[:index + offset] + \
                        u'**' + content[index + offset:]
                    offset += 2

                if start_bold > -1 and not bold:
                    i = index + offset
                    while not not_space(i):
                        i -= 1

                    content = content[:i + 1] + u'**' + content[i + 1:]
                    offset += 2
                    start_bold = -1

                if italic and good and start_italic == -1:
                    start_italic = index
                    content = content[:index + offset] + \
                        u'*' + content[index + offset:]
                    offset += 1

                if start_italic > -1 and not italic:
                    i = index + offset
                    while not not_space(i):
                        i -= 1

                    content = content[:i + 1] + u'*' + content[i + 1:]
                    offset += 1
                    start_italic = -1

        else:
            if start_bold > -1:
                i = index + offset
                while not not_space(i):
                    i -= 1

                content = content[:i + 1] + u'**' + content[i + 1:]
                offset += 2

            if start_italic > -1:
                i = index + offset
                while not not_space(i):
                    i -= 1

                content = content[:i + 1] + u'*' + content[i + 1:]
                offset += 1

        return content

    def cleanup(self, content):
        return content

    def handle_heading(self, text):
        return 0

    def handle_indent(self, text):
        return (0, False)

    def handle_ignored(self, content, in_table):
        return False

    def is_bold(self, char):
        fontname = char.fontname.lower()
        return fontname.find('bold') > -1

    def is_italic(self, char):
        fontname = char.fontname.lower()
        return fontname.find('italic') > -1

    def _generate_text(self, text, in_table=False):
        content = self.cleanup(text.get_text())
        heading = self.handle_heading(text)

        ignored = self.handle_ignored(content, in_table)

        if ignored:
            return u''

        if heading:
            if not self.dedup_headings or content not in self.headings.values():
                self.headings[heading] = content
                return u'{} {}'.format(u'#' * heading, content)
            else:
                return u''

        else:
            content = self.handle_font(text, content)

            if not in_table:
                indent, in_list = self.handle_indent(text, content)

                if in_list:
                    content = u'- ' + content

                content = indent * u'  ' + content

        return content

    def _generate_paragraph(self, element):
        markdown = ''

        for text in element.texts:
            markdown += self._generate_text(text)

        return markdown

    def _generate_table(self, element):
        vertical_coor = self._calc_coordinates(element.verticals, 'x0', False)
        horizontal_coor = self._calc_coordinates(
            element.horizontals, 'y0', True)
        num_rows = len(horizontal_coor) - 1
        num_cols = len(vertical_coor) - 1

        intermediate = [[] for idx in range(num_rows)]
        for row_idx in range(num_rows):
            for col_idx in range(num_cols):
                left = vertical_coor[col_idx]
                top = horizontal_coor[row_idx]
                right = vertical_coor[col_idx + 1]
                bottom = horizontal_coor[row_idx + 1]

                cell = ' '.join(
                    self._generate_text(x, in_table=True).replace(u'\n', u'<br>')
                    for x in element.find_cell_texts(left, top, right, bottom)
                )

                intermediate[row_idx].append(cell)

        return tabulate.tabulate(intermediate, tablefmt="pipe", headers="firstrow")

    def _calc_coordinates(self, axes, attr, reverse):
        coor_set = set()

        for axis in axes:
            coor_set.add(getattr(axis, attr))

        coor_list = list(coor_set)
        coor_list.sort(reverse=reverse)
        return coor_list
