import pytest

from crawlster.helpers.extract import ExtractHelper

CONTENT_1 = """<ul>
<li><a href="https://www.reddit.com/user/roddit-list/m/top"><strong>Top</strong></a></li>
<li><a href="https://www.reddit.com/user/roddit-list/m/active">Active</a></li>
<li><a href="https://www.reddit.com/user/roddit-list/m/inactive">Inactive</a></li>
</ul>"""


@pytest.fixture
def helper():
    return ExtractHelper()


def test_content_css_extraction(helper: ExtractHelper):
    """CSS extraction works as expected"""
    ahrefs = helper.css(CONTENT_1, 'li > a')
    assert len(ahrefs) == 3
    hrefs = helper.css(CONTENT_1, 'li > a', attr='href')
    assert len(hrefs) == 3
    for href in hrefs:
        assert href.startswith('http')
    texts = helper.css(CONTENT_1, 'li > a', content=True)
    assert texts == ['Top', 'Active', 'Inactive']
