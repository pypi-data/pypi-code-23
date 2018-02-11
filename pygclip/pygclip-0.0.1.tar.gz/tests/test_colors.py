import pygclip.colors as c


def test_darken_color():
    """Test a few examples of darkening web colors."""
    assert c.darken_color('#000000', 0.5) == '#000000'
    assert c.darken_color('#ffffff', 0.5) == '#7f7f7f'
    assert c.darken_color('#ffffff', 0.8) == '#323232'
