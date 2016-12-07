import os
import sys
import urllib
import urlparse
import urllib2

from io import BytesIO

import yaml

from pdfex.document import Document
from pdfex.element import Element
from pdfex.templates.comic import Comic


def url_fix(s):
    scheme, netloc, path, qs, anchor = urlparse.urlsplit(s)
    path = urllib.quote(path, '/%')
    qs = urllib.quote_plus(qs, ':&=')
    return urlparse.urlunsplit((scheme, netloc, path, qs, anchor))

if len(sys.argv) != 2:
    print 'usage: extract.py <yaml-file>'
    sys.exit(1)

try:
    with open(sys.argv[1]) as f:
        config = yaml.load(f)

except IOError:
    print '{}: no such YAML file'.format(sys.argv[1])
    sys.exit(1)

except yaml.scanner.ScannerError:
    print '{}: invalid YAML file'.format(sys.argv[1])
    sys.exit(1)

dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
out_path = os.path.join(dir_path, 'documents')

for document in config.get('documents', []):
    url = document.get('url').encode('utf-8')
    path = urlparse.urlsplit(url).path.split('/')[-1]
    name = os.path.splitext(path)[0]

    print 'Working on {}'.format(name)

    data = BytesIO()

    response = urllib2.urlopen(url_fix(url))
    data.write(response.read())

    print '    [+] Downloaded'

    template = Comic(
        dedup_headings=True,
        la_overrides=document.get('la_overrides')
    )

    doc = Document(data)
    markdown_filename = os.path.join(out_path, '{}.md'.format(name))

    with open(markdown_filename, 'w') as output:
        for page_num, page in doc.extract().items():
            page_element = Element()
            for element in page_element.parse(page, page_num, template):
                output.write(template.to_markdown(element).encode('utf-8'))

    print '    [+] Extracted'
    print
