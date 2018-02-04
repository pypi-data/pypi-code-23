# cronster tests
import pytest


@pytest.fixture
def scheduler():
    from cronster.scheduler import CronsterScheduler
    scheduler = CronsterScheduler(
        cache_host='localhost',
        cache_port=6379)
    assert scheduler
    return scheduler


@pytest.fixture
def scheduler_with_jobs(scheduler):
    from cronster.scheduler import CronsterJob
    job = CronsterJob(
        job_name='test_job',
        job_cmd='echo "Hello, World!"',
        job_schedule='* * * * *',
        job_path='/',
        job_hash='dc8a776c99d9b8ab97550e87c857dc959a857c5b')
    scheduler.jobs.append(job)
    return scheduler


def test_scheduler_running(scheduler):
    scheduler.stop()
    assert not scheduler.running
    scheduler.start()
    assert scheduler.running


def test_scheduler_status(scheduler):
    metadata, headers, job_data = scheduler.status()
    assert isinstance(metadata, list)
    assert isinstance(headers, list)
    assert isinstance(job_data, list)
    assert metadata
    assert headers
    assert job_data == []


def test_scheduler_clear(scheduler_with_jobs):
    assert len(scheduler_with_jobs.jobs) == 1
    scheduler_with_jobs.clear()
    assert len(scheduler_with_jobs.jobs) == 0


def test_job_properties(scheduler_with_jobs):
    assert scheduler_with_jobs.jobs[0].name == 'test_job'
    assert scheduler_with_jobs.jobs[0].cmd == 'echo "Hello, World!"'
    assert scheduler_with_jobs.jobs[0].cron == '* * * * *'
    assert scheduler_with_jobs.jobs[0].path == '/'
    assert scheduler_with_jobs.jobs[0].hash == \
        'dc8a776c99d9b8ab97550e87c857dc959a857c5b'
    assert scheduler_with_jobs.jobs[0].status
    scheduler_with_jobs.jobs[0].status = False
    assert not scheduler_with_jobs.jobs[0].status
    scheduler_with_jobs.jobs[0].status = True
    assert scheduler_with_jobs.jobs[0].status
    assert isinstance(scheduler_with_jobs.jobs[0].is_due, bool)
    assert not scheduler_with_jobs.jobs[0].is_due

