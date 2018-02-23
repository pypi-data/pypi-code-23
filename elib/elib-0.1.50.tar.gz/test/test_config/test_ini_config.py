# coding=utf-8


def test_ini_config_file(dummy_config):
    with open('test.ini', 'w') as stream:
        stream.write('''
[main]
debug=true
string=some string
integer=1

[namespace]
key=value
''')
    cfg = dummy_config('test')
    assert cfg.debug is True
    assert cfg.string == 'some string'
    assert cfg.integer is 1
    assert cfg.namespace_key == 'value'
