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

from onyx.core import Date, GetObj, ObjNamesByType, ObjNotFound
from onyx.core import ObjDbClient, UseDatabase, TsDbClient, TsDbUseDatabase
from onyx.core import GetVal, IsInstance, UseGraph
from onyx.core import load_system_configuration
from onyx.core.database.ufo_base import custom_encoder

from concurrent import futures

import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.escape

import contextlib
import getpass
import functools
import traceback
import json
import logging

__all__ = [
    "return_exceptions_as_str",
    "get_all_books",
    "get_all_portfolios",
    "ObjectNamesByTypeHandler",
    "GetValHandler",
    "RiskMonitorBase"
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)-15s %(levelname)-8s %(name)-32s %(message)s"
)
logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
def return_exceptions_as_str(func):
    """
    Description:
        Decorator used to catch any exceptions and return the traceback info
        as a string.
    Returns:
        A decorator
    """
    @functools.wraps(func)
    def wrapper(*args, **kwds):
        try:
            return func(*args, **kwds), 200
        except ObjNotFound:
            return traceback.format_exc(), 404
        except:
            return traceback.format_exc(), 500

    return wrapper


# -----------------------------------------------------------------------------
def get_all_books():
    """
    Description:
        Return all books that are children of one of the existing funds.
    Returns:
        A set
    """
    funds = ObjNamesByType("Fund")
    books = set()
    for fund in funds:
        fund = GetObj(fund, refresh=True)
        port = GetObj(fund.Portfolio, refresh=True)
        books.update(port.Books)
    return books


# -----------------------------------------------------------------------------
def get_all_portfolios(port):
    """
    Description:
        Return all sub-portfolios that are children of an input portfolio.
    Inputs:
        port - the name of the top portfolio
    Yields:
        A generator
    """
    port = GetObj(port, refresh=True)
    for kid in port.Children:
        if IsInstance(kid, "Portfolio"):
            yield from get_all_portfolios(kid)
    yield port.Name


# -----------------------------------------------------------------------------
@return_exceptions_as_str
def obj_names_by_type(obj_type):
    return ObjNamesByType(obj_type)


# -----------------------------------------------------------------------------
@return_exceptions_as_str
def get_val(security, vt, *args):
    with UseGraph():
        return GetVal(security, vt, *args)


###############################################################################
class ObjectNamesByTypeHandler(tornado.web.RequestHandler):
    # -------------------------------------------------------------------------
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, obj_type=None):
        self.set_header("Content-Type", "application/json")
        self.set_header("Access-Control-Allow-Origin", "*")

        app = self.application
        res, status = yield tornado.gen.Task(app.thrd_async,
                                             obj_names_by_type, obj_type)

        self.set_status(status)
        self.write(json.dumps(res))

    # -------------------------------------------------------------------------
    def options(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Methods", "GET")
        self.set_header("Access-Control-Allow-Headers",
                        "Content-Type,Authorization,Cache-Control")


###############################################################################
class GetValHandler(tornado.web.RequestHandler):
    """
    This handler manages requests to the specified value type.
    """
    # -------------------------------------------------------------------------
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        self.set_header("Content-Type", "application/json")
        self.set_header("Access-Control-Allow-Origin", "*")

        sec = self.get_argument("security")
        vt = self.get_argument("vt")
        args = tuple(self.get_arguments("args"))
        app = self.application

        res, status = yield tornado.gen.Task(app.thrd_async,
                                             get_val, sec, vt, *args)

        self.set_status(status)
        self.write(json.dumps(res, cls=custom_encoder))

    # -------------------------------------------------------------------------
    def options(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Methods", "GET")
        self.set_header("Access-Control-Allow-Headers",
                        "Content-Type,Authorization,Cache-Control")


###############################################################################
class RiskMonitorBase(tornado.web.Application):
    """
    Typical use will be as follows:

        app = RiskMonitorBase(handlers=[
            (r"/objects$", ObjectNamesByTypeHandler),
            (r"/objects/(\w+$)", ObjectNamesByTypeHandler),
            (r"/valuetypes/(.+)", ValueTypeHandler),
        ])

        http_server = tornado.httpserver.HTTPServer(app)
        http_server.listen(port, address="127.0.0.1")
        tornado.ioloop.IOLoop.instance().start()
    """
    # -------------------------------------------------------------------------
    def __init__(self, stop_at, handlers=None, nprocs=4, nthreads=4, **kwds):
        super().__init__(handlers, **kwds)

        # --- pre-load configuration settings
        self.config = load_system_configuration()

        # --- stopping time
        self.stop_at = stop_at

        # --- check periodically if the scheduler needs to be stopped
        tornado.ioloop.PeriodicCallback(self.check_stop, 60000).start()

        self.proc_exec = futures.ProcessPoolExecutor(max_workers=nprocs)
        self.thrd_exec = futures.ThreadPoolExecutor(max_workers=nthreads)

    # -------------------------------------------------------------------------
    def wrap_callback(self, callback):
        def wrapped(f):
            err = f.exception()
            if err is None:
                return callback(f.result())
            else:
                return callback(err)

        return wrapped

    # -------------------------------------------------------------------------
    def proc_async(self, func, *args, **kwds):
        callback = kwds.pop("callback", None)
        future = self.proc_exec.submit(func, *args, **kwds)

        if callback is not None:
            future.add_done_callback(self.wrap_callback(callback))

        return future

    # -------------------------------------------------------------------------
    def thrd_async(self, func, *args, **kwds):
        callback = kwds.pop("callback", None)
        future = self.thrd_exec.submit(func, *args, **kwds)

        if callback is not None:
            future.add_done_callback(self.wrap_callback(callback))

        return future

    # -------------------------------------------------------------------------
    def start(self, port, user):
        objdb = self.config.get("database", "objdb", fallback="ProdDb")
        tsdb = self.config.get("database", "tsdb", fallback="TsDb")
        user = self.config.get("database", "user", fallback=getpass.getuser())
        host = self.config.get("database", "host", fallback=None)

        stack = contextlib.ExitStack()
        stack.enter_context(UseDatabase(ObjDbClient(objdb, user, host)))
        stack.enter_context(TsDbUseDatabase(TsDbClient(tsdb, user, host)))

        with stack:
            http_server = tornado.httpserver.HTTPServer(self)
            http_server.listen(port)

            try:
                tornado.ioloop.IOLoop.instance().start()
            finally:
                self.cleanup()

    # -------------------------------------------------------------------------
    def cleanup(self):
        logger.info("shutting down process pool")
        self.proc_exec.shutdown()
        self.thrd_exec.shutdown()

    # -------------------------------------------------------------------------
    def check_stop(self):
        if Date.now() > self.stop_at:
            tornado.ioloop.IOLoop.instance().stop()
            logger.info("server is being stopped")
