from base10.exceptions import Base10Error


class TestExceptions:
    def test_base10_error(self):
        assert isinstance(Base10Error(), Exception)
