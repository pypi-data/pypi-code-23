# Copyright (C) 2018 Allen Li
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Sitemap generator.

http://www.sitemaps.org/protocol.html
"""

import io
from typing import NamedTuple
import warnings
import xml.etree.ElementTree as ET

__version__ = '1.1.0'


class URL(NamedTuple):
    loc: str
    lastmod: 'Optional[datetime.date]' = None
    changefreq: 'Optional[str]' = None
    priority: 'Optional[numbers.Real]' = None

    def to_etree(self):
        """Return etree XML representation of the URL."""
        entry = ET.Element('url')
        ET.SubElement(entry, 'loc').text = self.loc
        if self.lastmod is not None:
            ET.SubElement(entry, 'lastmod').text = self.lastmod.isoformat()
        if self.changefreq is not None:
            ET.SubElement(entry, 'changefreq').text = self.changefreq
        if self.priority is not None:
            ET.SubElement(entry, 'priority').text = str(self.priority)
        return entry


def write_urlset(file: io.TextIOBase, urls):
    """Write sitemap urlset to a file.

    urls is an iterable of URL instances.  file is a text file for writing.
    """
    urlset = ET.Element('urlset', {
        'xmlns': 'http://www.sitemaps.org/schemas/sitemap/0.9',
        'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        'xsi:schemaLocation': ' '.join((
            'http://www.sitemaps.org/schemas/sitemap/0.9',
            'http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd')),
    })
    urlset.extend(url.to_etree() for url in urls)
    document = ET.ElementTree(urlset)
    document.write(file, encoding='unicode', xml_declaration=True)


def write_sitemap_urlset(file, urls):
    warnings.warn('write_sitemap_urlset is deprecated', DeprecationWarning)
    return write_urlset(file, urls)
