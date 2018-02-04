# cronster tests
import subprocess


def test_import():
    import cronster
    assert cronster


def test_crawler_cli():
    proc = subprocess.Popen('cronster_crawler', shell=True)
    proc.kill()


def test_scheduler_cli():
    proc = subprocess.Popen('cronster_scheduler', shell=True)
    proc.kill()
