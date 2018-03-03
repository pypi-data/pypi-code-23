"""
Test DuckDuckGo class
"""

import jw.websearch.duckduckgo
import jw.websearch.filemare

def test10():
    search = jw.websearch.duckduckgo.Search()
    result = list(search.search('color'))
    assert len(result) > 0

def test20():
    search = jw.websearch.filemare.Search()
    result = list(search.search('jdk-8u92-linux-x64.tar.gz'))
    assert len(result) > 0
