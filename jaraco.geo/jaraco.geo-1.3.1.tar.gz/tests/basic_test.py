import pytest

from jaraco.geo.geotrans import initialize_engine, get_datum_index


pytestmark = pytest.mark.xfail("sys.version_info > (3,)")


def test_get_index():
	initialize_engine()
	print(get_datum_index('WGE'))


if __name__ == '__main__':
	test_get_index()
