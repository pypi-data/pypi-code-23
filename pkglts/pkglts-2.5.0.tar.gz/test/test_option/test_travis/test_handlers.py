from pkglts.config_management import Config


def test_badge():
    cfg = Config(dict(travis={},
                      doc={'fmt': 'rst'},
                      github={'owner': "moi", 'project': "project"}))
    cfg.load_extra()
    assert ".. image:" in cfg._env.globals['travis'].badge
