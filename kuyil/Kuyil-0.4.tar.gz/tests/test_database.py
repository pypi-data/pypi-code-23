from Kuyil.database import *
import Kuyil.api as Kuyil


def test_initial_url_value():
    assert url == "mysql://root:root@54.153.107.17:3306/kuyil"


def test_url_after_conf_load():
    Kuyil.init("config.json")
    from Kuyil.database import url
    assert url == "mysql://root:root@localhost:3306/db"


def test_url_after_test_conf_load():
    test_init()
    from Kuyil.database import url
    assert url == "sqlite:///foo.db"


def test_engine_after_test_conf_load():
    test_init()
    from Kuyil.database import engine
    assert str(engine.url) == "sqlite:///foo.db"

