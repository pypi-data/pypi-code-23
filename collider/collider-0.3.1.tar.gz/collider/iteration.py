# -*- author: Dimitri Scheftelowitsch -*-
# -*- coding:utf-8 -*-
from time import time, process_time
from collider import ResultLog, Stage, RunResult, RerunPredicate
from itertools import product
from typing import Dict, Any, Iterable, List
from multiprocessing import Lock, Process, JoinableQueue, cpu_count, Event
from prwlock import RWLock
from os import cpu_count
from logging import getLogger


class StageCallbackData:
    def __init__(self, result: RunResult, stats: Dict[str, Any], predicate: bool):
        self.result = result
        self.stats = stats
        self.predicate = predicate


class Job:
    def __init__(self, index: int, value: Any, stage: Stage, stats: Dict[str, Any]):
        self.index = index
        self.value = value
        self.stage = stage
        self.stats = stats


class StageWorker(Process):
    def __init__(self, task_queue: JoinableQueue,
                 result_queue: JoinableQueue,
                 stages: Iterable[Stage], result_logger: ResultLog,
                 writer_lock: RWLock,
                 predicate: RerunPredicate):
        Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.stages = stages
        self.result_logger = result_logger
        self.writer_lock = writer_lock
        self.predicate = predicate

    def run(self):
        proc_name = self.name
        logger = getLogger("collider")
        logger.info("Worker {0} started…".format(proc_name))
        while True:
            job = self.task_queue.get()
            if job is None:
                logger.info("Worker {0} is done, exiting…".format(proc_name))
                self.task_queue.task_done()
                break
            # assume from here that job is of type Job
            stage = job.stage
            logger.info("Running stage {0}, value {1}".format(stage.name,
                                                              job.value))
            new_result = self.predicate.rerun(stage.name, job.value)
            if new_result:
                t0 = process_time()
                wt0 = time()
                data = stage.execute(job.value, job.stats)
                dt = process_time() - t0
                wdt = time() - wt0
                logger.info("Run stage {2}, value {1}: elapsed time: {0:.4f}s cpu, {3:.4f}s wall".
                            format(dt, job.value, stage.name, wdt))
                data['process_time'] = dt
            else:
                logger.info("Stage {0}, value {1}: Reusing saved result".format(stage.name, job.value))
                self.writer_lock.acquire_read()
                data = self.result_logger.get_data(stage, job.value)
                self.writer_lock.release()
            result = RunResult(stage=stage.name, value=job.value, data=data, index=job.index)
            job.stats[stage.name] = data
            self.result_queue.put(
                StageCallbackData(result, job.stats, new_result))
            self.task_queue.task_done()
        return


class ResultHandler(Process):
    def __init__(self, task_queue: JoinableQueue, result_queue: JoinableQueue, logger_queue: JoinableQueue,
                 stage_order: Iterable[Stage], num_values: int, all_done: Event, stage_groups: List[List[str]]):
        Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.logger_queue = logger_queue
        self.stage_order = stage_order
        self.num_values = num_values
        self.all_done = all_done
        self.stage_groups = stage_groups
        self.stage_order_mapping = {}
        for (i, s) in enumerate(self.stage_order):
            self.stage_order_mapping[s.name] = i
        self.finished = 0

    def run(self):
        proc_name = self.name
        logger = getLogger("collider")
        # launch_memory_usage_server(port=8080)
        while True:
            result = self.result_queue.get()
            if result is None:
                self.result_queue.task_done()
                logger.info("Result handler done, exiting…")
                break
            if result.predicate:
                self.logger_queue.put(result.result)
            stage_id = self.stage_order_mapping[result.result.stage]
            if stage_id < len(self.stage_order) - 1:
                # find the correct stage group
                next_stage = self.stage_order[stage_id + 1]
                self.task_queue.put(Job(index=result.result.index, value=result.result.value, stage=next_stage,
                                        stats=result.stats))
                self.result_queue.task_done()
            else:
                self.result_queue.task_done()
                self.finished += 1
                logger.info("{0}/{1} jobs finished".format(self.finished, self.num_values))
                if self.finished == self.num_values:
                    self.all_done.set()
        return


class ResultWriter(Process):
    def __init__(self, writer_queue: JoinableQueue, result_logger: ResultLog, lock: RWLock, jobs: int):
        Process.__init__(self)
        self.writer_queue = writer_queue
        self.result_logger = result_logger
        self.lock = lock
        self.jobs = jobs
        self.processed_results = {}

    def run(self):
        proc_name = self.name
        logger = getLogger("collider")
        # launch_memory_usage_server(port=8081)
        while True:
            result = self.writer_queue.get()
            if result is None:
                logger.info("Result writer ({0}) done, exiting…".format(proc_name))
                self.lock.acquire_write()
                self.result_logger.save()
                self.result_logger.save_csv()
                self.lock.release()
                self.writer_queue.task_done()
                break
            self.processed_results[result.stage] = 1 + self.processed_results.get(result.stage, 0)
            force_save = (self.processed_results[result.stage] == self.jobs)
            self.lock.acquire_read()
            self.result_logger.put_result(result, force_save=force_save)
            self.lock.release()
            self.writer_queue.task_done()
        return


def run_experiments(values: Dict[str, Iterable], stages: Iterable[Stage], logger: ResultLog, predicate: RerunPredicate,
                    stage_groups: List[List[str]], **kwargs):
    max_processes = cpu_count()
    if 'job_load' in kwargs:
        max_processes = int(cpu_count() / kwargs['job_load'])

    reproducible_value_list = [values[k] for k in sorted(values.keys())]
    value_list = list(product(*reproducible_value_list))

    stats = [{} for _ in value_list]
    printer = getLogger("collider")
    writer_lock = RWLock()

    printer.debug("total inputs: {}".format(len(value_list)))
    # let's do it with queues!
    tasks = JoinableQueue()
    results = JoinableQueue()
    writer_results = JoinableQueue()
    num_workers = min(max_processes, len(value_list))
    num_values = len(value_list)
    all_done = Event()
    workers = [StageWorker(tasks, results, stages,
                           logger, writer_lock, predicate) for _ in range(num_workers)]
    handler = ResultHandler(tasks, results, writer_results, stages, num_values, all_done, stage_groups)
    writer = ResultWriter(writer_results, logger, writer_lock, num_values)

    handler.start()
    writer.start()

    for ((i, v), s) in zip(enumerate(value_list), stats):
        tasks.put(Job(i, v, stages[0], s))

    for w in workers:
        w.start()

    all_done.wait()

    for w in workers:
        tasks.put(None)

    printer.debug("All tasks done, joining queue…")
    tasks.join()
    printer.debug("All tasks done, terminating workers…")
    for w in workers:
        w.join()
    printer.debug("All tasks done, terminating result handler…")

    results.put(None)
    results.join()
    handler.join()

    printer.debug("All tasks done, terminating result writer…")
    writer_results.put(None)

    printer.debug("All tasks done, joining result queue…")
    writer_results.join()

    printer.debug("All tasks done, joining handler processes…")
    writer.join()
