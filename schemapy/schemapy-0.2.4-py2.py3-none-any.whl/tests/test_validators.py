class TestIsOf:
    def test_success(self, isof):
        _, err = isof('test')
        assert err is None

    def test_fail(self, isof):
        _, err = isof(42)
        assert err is not None


class TestIsGreaterThan:
    def test_success(self, isgt):
        _, err = isgt(43)
        assert err is None

    def test_fail(self, isgt):
        _, err = isgt(41)
        assert err is not None


class TestIsGreaterThanOrEqual:
    def test_success(self, isgte):
        _, err = isgte(43)
        assert err is None
        _, err = isgte(42)
        assert err is None

    def test_fail(self, isgte):
        _, err = isgte(41)
        assert err is not None


class TestIsLessThan:
    def test_success(self, islt):
        _, err = islt(41)
        assert err is None

    def test_fail(self, islt):
        _, err = islt(43)
        assert err is not None


class TestIsLessThanOrEqual:
    def test_success(self, islte):
        _, err = islte(41)
        assert err is None
        _, err = islte(42)
        assert err is None

    def test_fail(self, islte):
        _, err = islte(43)
        assert err is not None


class TestIsInRange:
    def test_success(self, is_in_range):
        _, err = is_in_range(30)
        assert err is None

    def test_fail(self, is_in_range):
        _, err = is_in_range(43)
        assert err is not None


class TestIsLength:
    def test_success(self, is_length):
        _, err = is_length('hello')
        assert err is None

    def test_fail(self, is_length):
        _, err = is_length('hello world')
        assert err is not None
