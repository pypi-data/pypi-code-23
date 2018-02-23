# coding=utf-8


def test_env_config(dummy_config):
    with open(f'.env', 'w') as stream:
        stream.write('''
DEBUG=true
STRING=some string
INTEGER=1
NAMESPACE_KEY=value
''')
    cfg = dummy_config('test')
    print(cfg._config)
    assert cfg.debug is True
    assert cfg.string == 'some string'
    assert cfg.integer is 1
    assert cfg.namespace_key == 'value'
