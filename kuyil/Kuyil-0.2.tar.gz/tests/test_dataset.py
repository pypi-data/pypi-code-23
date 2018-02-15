from Kuyil.api.dataset import Dataset
import Kuyil.api as Kuyil
from Kuyil.database import session_factory
from Kuyil.database import test_init
from Kuyil.models.repository_entity import RepositoryEntity
from Kuyil.utils.date_time_util import Util
from sqlalchemy_utils import drop_database


def test_dataset_instance():
    dataset = Dataset("class", "instance", "label", "repository", None, None,
                       Util.current_time_millis(), Util.current_time_millis())
    assert dataset.dataset_class == "class"
    assert dataset.instance == "instance"
    assert dataset.label == "label"
    assert dataset.repository == "repository"


def test_dataset_created_time():
    time = Util.current_time_millis()
    dataset1 = Dataset("class1", "instance", "label", "repository", None, None,
                       Util.current_time_millis(), Util.current_time_millis())
    assert dataset1.dataset_created_ts <= Util.current_time_millis()
    assert dataset1.dataset_created_ts >= time


def test_dataset_modifies_time():
    time = Util.current_time_millis()
    dataset = Dataset("class1", "instance", "label", "repository", None, None,
                       Util.current_time_millis(), Util.current_time_millis())
    assert dataset.dataset_modified_ts <= Util.current_time_millis()
    assert dataset.dataset_modified_ts >= time


def test_create_dataset():
    test_init()
    session = session_factory()
    config = '{"aws_access_key":"","aws_secret_access_key":"","bucket":"scale-testing","prefix":"test-folder"}'
    repo = RepositoryEntity("s3-us-east", config)
    session.add(repo)
    session.commit()
    dataset = Kuyil.create_dataset("class", "instance", "label", "s3-us-east")
    assert dataset


def test_write_lock():
    test_init()
    from Kuyil.database import engine
    drop_database(engine.url)
    session = session_factory()
    config = '{"aws_access_key":"","aws_secret_access_key":"","bucket":"scale-testing","prefix":"test-folder"}'
    repo = RepositoryEntity("s3-us-east", config)
    session.add(repo)
    session.commit()
    dataset = Kuyil.create_dataset("class", "instance", "label", "s3-us-east")
    time = dataset.get_write_lock_if_write_read_or_idle(1)
    assert time
    assert time > Util.current_time_millis()
    assert (time - Util.lock_time_millis()) < 100


def test_get_write_lock_with_same_pid():
    test_init()
    session = session_factory()
    config = '{"aws_access_key":"","aws_secret_access_key":"","bucket":"scale-testing","prefix":"test-folder"}'
    repo = RepositoryEntity("s3-us-east", config)
    session.add(repo)
    session.commit()
    dataset = Kuyil.create_dataset("class", "instance", "label", "s3-us-east")
    time = dataset.get_write_lock_if_write_read_or_idle(2)
    time2 = dataset.get_write_lock_if_write_read_or_idle(2)
    assert time
    assert not time2


def test_write_success():
    test_init()
    from Kuyil.database import engine
    drop_database(engine.url)
    session = session_factory()
    config = '{"aws_access_key":"","aws_secret_access_key":"","bucket":"scale-testing","prefix":"test-folder"}'
    repo = RepositoryEntity("s3-us-east", config)
    session.add(repo)
    session.commit()
    dataset = Kuyil.create_dataset("class", "instance", "label", "s3-us-east")
    dataset.get_write_lock_if_write_read_or_idle(1)
    assert dataset.write_success(1, "Finished")


def test_write_failed():
    test_init()
    from Kuyil.database import engine
    drop_database(engine.url)
    session = session_factory()
    config = '{"aws_access_key":"","aws_secret_access_key":"","bucket":"scale-testing","prefix":"test-folder"}'
    repo = RepositoryEntity("s3-us-east", config)
    session.add(repo)
    session.commit()
    dataset = Kuyil.create_dataset("class", "instance", "label", "s3-us-east")
    dataset.get_write_lock_if_write_read_or_idle(1)
    assert dataset.write_failed(1, "Finished")

