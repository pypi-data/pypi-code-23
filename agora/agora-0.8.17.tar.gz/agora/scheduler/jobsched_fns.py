###############################################################################
#
#   Agora Portfolio & Risk Management System
#
#   Copyright 2015 Carlo Sbraccia
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
###############################################################################
"""
Scheduling functions and request handlers implementing a RESTful API.
"""
from apscheduler.schedulers.tornado import TornadoScheduler

import apscheduler.jobstores.base
import tornado.web
import importlib
import json
import shlex

__all__ = [
    "SchedulerError",
    "IndexHandler",
    "JobsHandler",
    "SchedulingServer"
]


# -----------------------------------------------------------------------------
def run_job(mod_name, args, kwds):
    module = importlib.import_module(mod_name)
    module.run(*args, **kwds)


# -----------------------------------------------------------------------------
def arg_split(arg):
    key, value = arg.split("=")
    # --- cast boolean strings to proper datatype
    if value.upper() == "TRUE":
        value = True
    elif value.upper() == "FALSE":
        value = False
    return key.lstrip("-"), value


# -----------------------------------------------------------------------------
def arg_combine(option, value):
    return "--{0:s}={1:s}".format(option, shlex.quote(str(value)))


###############################################################################
class SchedulerError(Exception):
    pass


###############################################################################
class IndexHandler(tornado.web.RequestHandler):
    # -------------------------------------------------------------------------
    def initialize(self, index_file):
        self.index_file = index_file

    # -------------------------------------------------------------------------
    def get(self):
        with open(self.index_file, "r") as index_file:
            self.write(index_file.read())


###############################################################################
class JobsHandler(tornado.web.RequestHandler):
    # -------------------------------------------------------------------------
    def get(self, job_id=None):
        self.set_header("Content-Type", "application/json")
        self.set_header("Access-Control-Allow-Origin", "*")

        self.application.logger.info("GET: job_id is {0!s}".format(job_id))

        response = []
        for job in self.application.scheduler.get_jobs():

            if job_id is not None and job.id != job_id:
                continue

            if job.next_run_time is None:
                next_run_time = "paused"
            else:
                next_run_time = job.next_run_time.isoformat()

            response.append({
                "name": job.name,
                "kwds": " ".join([arg_combine(k, v)
                                  for k, v in job.kwargs["kwds"].items()]),
                "id": job.id,
                "executor": job.executor,
                "next_run_time": next_run_time,
                "trigger": {field.name: str(field)
                            for field in job.trigger.fields},
            })

        self.set_status(200)
        self.write(json.dumps(response))

    # -------------------------------------------------------------------------
    def put(self, job_id=None):
        self.set_header("Access-Control-Allow-Origin", "*")

        app = self.application
        app.logger.info("PUT: job_id is {0!s}".format(job_id))

        if job_id is None:
            app.logger.error("cannot modify a job without knowing the job.id")
            self.set_status(404)
            return

        for job in app.scheduler.get_jobs():
            if job.id == job_id:
                break
        else:
            app.logger.error("Job {0:s} not fount".format(job_id))
            self.set_status(404)
            return

        changes = json.loads(self.request.body.decode("utf-8"))
        trigger_args = changes.pop("trigger", None)
        job_status = changes.pop("next_run_time", None)

        if job_status == "pause":
            app.paused.add(job_id)
            app.scheduler.pause_job(job_id)
            app.logger.info("PUT: job was paused")

        elif job_status == "resume":
            if job_id in app.paused:
                app.scheduler.resume_job(job_id)
                app.paused.remove(job_id)
                app.logger.info("PUT: job was resumed")

        else:
            kwds = changes.pop("kwds", "")
            kwargs = job.kwargs
            kwargs["kwds"] = dict([arg_split(arg)
                                   for arg in shlex.split(kwds)])
            changes["kwargs"] = kwargs
            try:
                app.scheduler.modify_job(job_id, **changes)
                if trigger_args is not None:
                    app.scheduler.reschedule_job(job_id,
                                                 trigger="cron",
                                                 **trigger_args)
                    app.logger.info("PUT: job was rescheduled")

            except apscheduler.jobstores.base.JobLookupError as err:
                self.set_status(404)
                self.write("{0!s}\n".format(err))

    # -------------------------------------------------------------------------
    def delete(self, job_id=None):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.application.logger.info("DELETE: job_id is {0!s}".format(job_id))
        if job_id is None:
            self.set_status(404)
            return

        try:
            self.application.scheduler.remove_job(job_id)
        except apscheduler.jobstores.base.JobLookupError as err:
            self.set_status(404)
            self.write("{0!s}\n".format(err))

    # -------------------------------------------------------------------------
    def post(self, job_id=None):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.application.logger.info("POST: job_id is {0!s}".format(job_id))

        if job_id is None:
            # --- adding new job
            job_parms = json.loads(self.request.body.decode("utf-8"))
            try:
                self.application.schedule_job({
                    "module": job_parms["name"],
                    "trigger": job_parms["trigger"],
                    "executor": job_parms["executor"],
                    "kwds": dict([arg_split(arg)
                                  for arg in shlex.split(job_parms["kwds"])]),
                })
                self.set_status(201)
            except SchedulerError as err:
                self.application.logger.error(err, exc_info=True)
                self.set_status(400)
                self.write("{0!s}\n".format(err))

        else:
            # --- running an existing job now as a one-ff
            job = self.application.scheduler.get_job(job_id)
            self.application.scheduler.add_job(job.func,
                                               args=job.args,
                                               kwargs=job.kwargs)

    # -------------------------------------------------------------------------
    def options(self, job_id=None):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE")
        self.set_header("Access-Control-Allow-Headers",
                        "Content-Type,Authorization,accept,x-requested-with")
        self.set_status(200)


###############################################################################
class SchedulingServer(tornado.web.Application):
    # -------------------------------------------------------------------------
    def __init__(self, logger, jobstores, executors, handlers=None, **kwds):
        super().__init__(handlers, **kwds)

        self.logger = logger
        self.scheduler = TornadoScheduler(logger=logger,
                                          jobstores=jobstores,
                                          executors=executors)
        self.scheduler.start()

        self.paused = set()
        for job in self.scheduler.get_jobs():
            if job.next_run_time is None:
                self.paused.add(job.id)

    # -------------------------------------------------------------------------
    def schedule_job(self, job):
        mod_name = job["module"]

        # --- is the module importable and does it expose a run function?
        try:
            module = importlib.import_module(mod_name)
        except (ImportError, SystemError) as err:
            raise SchedulerError("{0!s}".format(err))

        if not hasattr(module, "run"):
            raise SchedulerError("{0:s} doesn't expose a run "
                                 "function".format(job["module"]))

        kwargs = {
            "mod_name": mod_name,
            "args": job.get("args", []),
            "kwds": job.get("kwds", {}),
        }

        # --- each job is scheduled using a wrapper
        return self.scheduler.add_job(run_job, kwargs=kwargs,
                                      trigger="cron",
                                      executor=job["executor"],
                                      name=job["module"],
                                      replace_existing=True, **job["trigger"])
