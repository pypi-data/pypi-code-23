import pytest
from elixr import AttrDict, Coordinates



class TestAttrDict(object):
    def test_is_instance_of_dict(self):
        attrd = AttrDict()
        assert isinstance(attrd, dict) == True
    
    def test_can_element_using_dot_notation(self):
        foo = AttrDict()
        foo['bar'] = 'egg-whl'
        assert 'egg-whl' == foo.bar
    
    def test_access_using_unknown_member_returns_None(self):
        attrd = AttrDict()
        assert None == attrd.bar
    
    def test_access_using_missing_key_returns_None(self):
        attrd = AttrDict()
        assert None == attrd['bar']

    def test_has_friendly_string_repr(self):
        attrd = AttrDict(bar='egg-whl')
        assert repr(attrd).startswith('<AttrDict')
    
    def test_make_not_given_dict_or_sequence_fails(self):
        with pytest.raises(ValueError):
            AttrDict.make('foo')
    
    def test_can_make_attr_dict_from_dict(self):
        foo = AttrDict.make(dict(bar='egg-whl'))
        assert isinstance(foo, AttrDict) \
           and 'egg-whl' == foo.bar
    
    def test_can_make_attr_dict_from_nested_dict(self):
        attrd = AttrDict.make(dict(
            conf = dict(
                name = 'norf',
                meta = dict(name='simple.conf', path=r'c:\path\to\conf')
            )
        ))
        assert isinstance(attrd, AttrDict) \
           and isinstance(attrd.conf, AttrDict) \
           and isinstance(attrd.conf.meta, AttrDict)


class TestCoordinates(object):
    
    def test_creation_requires_lng_lat(self):
        coords = Coordinates(lng=11.9976, lat=8.5086)
        assert coords \
           and coords.lng == 11.9976 \
           and coords.lat == 8.5086 \
           and coords.alt == None \
           and coords.error == None
    
    def test_exists_as_four_element_tuple(self):
        coords = Coordinates(lng=11.9976, lat=8.5086)
        assert 4 == len(coords) \
           and (11.9976, 8.5086, None, None) == coords \
           and coords[0] == 11.9976 \
           and coords[1] == 8.5086 \
           and coords[2] == None \
           and coords[3] == None
    
    @pytest.mark.parametrize("lng, lat", [(None, 8.5086), (11.9976, None)])
    def test_creation_fails_without_lng_or_lat(self, lng, lat):
        with pytest.raises(ValueError):
            Coordinates(lng=lng, lat=lat)
    
    @pytest.mark.parametrize("lng, lat", [(None, 8.5086), (11.9976, None)])
    def test_creation_fails_without_lng_or_lat2(self, lng, lat):
        with pytest.raises(TypeError):
            if lng == None:
                Coordinates(lat=lat)
            elif lat == None:
                Coordinates(lng=lng)
    
    def test_lite_version_exist_as_two_element_tuple(self):
        coords = Coordinates(lng=11.9976, lat=8.5086).lite
        assert 2 == len(coords) \
           and (11.9976, 8.5086) == coords \
           and coords[0] == 11.9976 \
           and coords[1] == 8.5086
    
    @pytest.mark.parametrize("lng, lat, alt, error", [
        (1.1, 2.2, 3.3, 'a'), (1.1, 2.2, 'b', 4), (1.1, 'c', 3.3, 4),
        ('d', 2.2, 3.3, 4)
    ])
    def test_ensure_all_elements_are_numeric(self, lng, lat, alt, error):
        with pytest.raises(ValueError):
            Coordinates(lng=lng, lat=lat, alt=alt, error=error)
    
    @pytest.mark.parametrize("lng, lat, alt, error", [
        ('1.1', 2.2, 3.3, 4), (1.1, '2.2', 3.3, 4), (1.1, 2.2, '3.3', 4),
        (1.1, 2.2, 3.3, '4'), ('1.1', '2.2', '3.3', '4')
    ])
    def test_numeric_strings_acceptable_as_element(self, lng, lat, alt, error):
        coords = Coordinates(lng=lng, lat=lat, alt=alt, error=error)
        assert coords and 4 == len(coords) \
           and coords.lng == 1.1 \
           and coords.lat == 2.2 \
           and coords.alt == 3.3 \
           and coords.error == 4
