from pdfminer.layout import (
    LTFigure, LTTextBox, LTTextLine, LTTextBoxHorizontal,
    LTTextLineHorizontal, LTLine, LTRect, LTImage, LTCurve,
    LTChar, LTLine, LAParams
)


class Element(object):

    def __init__(self, search_distance=1.0):
        self.search_distance = search_distance

        self.verticals = []
        self.horizontals = []
        self.texts = []

    def __repr__(self):
        return 'Element (type={}, vert={}, horiz={}, texts={})'.format(
            self.get_type(),
            len(self.verticals),
            len(self.horizontals),
            len(self.texts),
        )

    def parse(self, page, page_num, template):
        if template.la_overrides and str(page_num) in template.la_overrides:
            laparams = LAParams(**template.la_overrides[str(page_num)])
        else:
            laparams = LAParams()

        page.analyze(laparams)
        items = list(reversed(list(page)))

        while items:
            item = items.pop()

            if template.footer_break and template.footer_break > item.y1:
                continue

            if type(item) in [LTFigure, LTTextBox, LTTextLine, LTTextBoxHorizontal]:
                items.extend(reversed(list(item)))

            elif type(item) == LTTextLineHorizontal:
                self.texts.append(item)

            elif type(item) == LTRect:
                if item.width < 1.0:
                    self._adjust_to_close(item, self.verticals, 'x0')
                    self.verticals.append(item)
                elif item.height < 1.0:
                    self._adjust_to_close(item, self.horizontals, 'y0')
                    self.horizontals.append(item)

            else:
                continue

        return self._split()

    def get_type(self):
        if self.verticals:
            return 'table'

        return 'paragraph'

    def _split(self):
        tables = self._find_tables()
        paragraphs = self._find_paragraphs(tables)

        def get_anything(x):
            if x.texts:
                return x.texts[0]

            if x.verticals:
                return x.verticals[0]

        return sorted(
            (item for item in
            tables + paragraphs
            if get_anything(item)),
            reverse=True,
            key=lambda x: get_anything(x).y0
        )

    def _adjust_to_close(self, obj, lines, attr):
        obj_coor = getattr(obj, attr)
        close = None
        for line in lines:
            line_coor = getattr(line, attr)
            if abs(obj_coor - line_coor) < self.search_distance:
                close = line
                break

        if not close:
            return

        if attr == 'x0':
            new_bbox = (close.bbox[0], obj.bbox[1], close.bbox[2], obj.bbox[3])
        elif attr == 'y0':
            new_bbox = (obj.bbox[0], close.bbox[1], obj.bbox[2], close.bbox[3])
        else:
            raise Exception('No such attr')
        obj.set_bbox(new_bbox)

    def _find_tables(self):
        tables = []
        visited = set()
        for vertical in self.verticals:
            if vertical in visited:
                continue

            near_verticals = self._find_near_verticals(
                vertical, self.verticals)
            top, bottom = self._calc_top_bottom(near_verticals)
            included_horizontals = self._find_included(
                top, bottom, self.horizontals)
            included_texts = self._find_included(top, bottom, self.texts)

            table = Element()
            table.verticals = near_verticals
            table.horizontals = included_horizontals
            table.texts = included_texts

            tables.append(table)
            visited.update(near_verticals)

        return tables

    def _find_paragraphs(self, tables):
        tops = []
        for table in tables:
            top, bottom = self._calc_top_bottom(table.verticals)
            tops.append(top)

        tops.append(float('-inf'))  # for the last part of paragraph

        all_table_texts = set()
        for table in tables:
            all_table_texts.update(table.texts)

        num_slots = len(tables) + 1
        paragraphs = [Element() for idx in range(num_slots)]

        for text in self.texts:
            if text in all_table_texts:
                continue
            for idx, top in enumerate(tops):
                if text.y0 > top:
                    paragraphs[idx].texts.append(text)
                    break

        paragraphs = filter(None, paragraphs)

        return paragraphs

    def _is_overlap(self, top, bottom, obj):
        assert top > bottom
        return (bottom - self.search_distance) <= obj.y0 <= (top + self.search_distance) or \
            (bottom - self.search_distance) <= obj.y1 <= (top + self.search_distance)

    def _find_near_verticals(self, start, verticals):
        near_verticals = [start]
        top = start.y1
        bottom = start.y0

        for vertical in verticals:
            if vertical == start:
                continue
            if self._is_overlap(top, bottom, vertical):
                near_verticals.append(vertical)
                top, bottom = self._calc_top_bottom(near_verticals)

        return near_verticals

    def _calc_top_bottom(self, objects):
        top = float('-inf')
        bottom = float('inf')

        for obj in objects:
            top = max(top, obj.y1)
            bottom = min(bottom, obj.y0)

        return top, bottom


    def _find_included(self, top, bottom, objects):
        included = []
        for obj in objects:
            if self._is_overlap(top, bottom, obj):
                included.append(obj)
        return included


    def find_cell_texts(self, left, top, right, bottom):
        texts = []
        for text in self.texts:
            if self._in_range(left, top, right, bottom, text):
                texts.append(text)
        return texts

    def _in_range(self, left, top, right, bottom, obj):
        return (left - self.search_distance) <= obj.x0 < obj.x1 <= (right + self.search_distance) and \
            (bottom - self.search_distance) <= obj.y0 < obj.y1 <= (top + self.search_distance)
