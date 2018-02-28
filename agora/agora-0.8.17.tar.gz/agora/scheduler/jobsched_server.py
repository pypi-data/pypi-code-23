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

from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

import agora.scheduler.jobsched_fns

import tornado.httpserver
import tornado.ioloop
import tornado.web

import argh
import logging
import os

LOG_FMT = "%(asctime)-15s %(levelname)-8s %(name)-38s %(message)s"

logging.basicConfig(level=logging.INFO, format=LOG_FMT)


# -----------------------------------------------------------------------------
def run(port=9100, sqlite_path=None):

    sqlite_base = os.getenv("HOME", "./")
    sqlite_path = sqlite_path or os.path.join(sqlite_base, ".jobs.sqlite")
    sqlite_url = "sqlite:///{0:s}".format(sqlite_path)

    jobs_logger = logging.getLogger(__name__)

    jobs_stores = {
        "default": SQLAlchemyJobStore(url=sqlite_url),
    }

    jobs_executors = {
        "default": ThreadPoolExecutor(5),
        "processpool": ProcessPoolExecutor(2),
    }

    handlers = [
        (r"/jobs$", agora.scheduler.jobsched_fns.JobsHandler),
        (r"/jobs/(\w+$)", agora.scheduler.jobsched_fns.JobsHandler),
    ]

    app = agora.scheduler.jobsched_fns.SchedulingServer(
        jobs_logger,
        jobs_stores,
        jobs_executors,
        handlers,
        job_defaults={"misfire_grace_time": 5*60},  # set to 5 minutes
    )

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(port)
    tornado.ioloop.IOLoop.instance().start()


# -----------------------------------------------------------------------------
def main():
    argh.dispatch_command(run)


# -----------------------------------------------------------------------------
if __name__ == "__main__":
    run()
