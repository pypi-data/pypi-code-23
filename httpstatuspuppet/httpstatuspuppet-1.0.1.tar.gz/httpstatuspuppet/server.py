from wsgiref.simple_server import make_server

from http_status import Status, InvalidHttpCode
from threading import Thread
from typing import Callable, Dict, List

from httpstatuspuppet.common import HttpStatusPuppetError

DEFAULT_HTTP_STATUS = 200
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8000


class ServerNotStartedError(HttpStatusPuppetError):
    """
    Server not started error.
    """


class InvalidStatusCodeError(HttpStatusPuppetError):
    """
    Invalid status code error.
    """


def _code_and_description(status: Status) -> str:
    """
    Generates "{code} {description}" string from the given status.
    :param status: status to generate code and description string from
    :return: generated string
    """
    return f"{status.code} {status.description}"


class Server:
    """
    Basic authentication server.
    """
    @staticmethod
    def _endpoint(environment: Dict, start_response: Callable) -> List[bytes]:
        """
        Endpoint handler.
        :param environment: environment of call
        :param start_response: header handler
        :return: body
        """
        path = environment["PATH_INFO"][1:]
        try:
            raw_status = int(path)
        except ValueError:
            return Server._generate_error(f"Unknown status code: \"{path}\"", start_response)
        try:
            status_information = Status(raw_status)
        except InvalidHttpCode:
            return Server._generate_error(f"Invalid status code: {raw_status}", start_response)

        code_and_description = _code_and_description(status_information)
        start_response(code_and_description, [])
        return [f"{code_and_description}".encode("utf-8")]

    @staticmethod
    def _generate_error(error_message: str, start_response: Callable) -> List[bytes]:
        """
        Generates an error.
        :param error_message: error message
        :param start_response: header handler
        :return: error body
        """
        start_response(_code_and_description(Status(400)), [])
        return [error_message.encode("utf-8")]

    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}"

    def __init__(self, host: str=DEFAULT_HOST, port: int=DEFAULT_PORT):
        """
        Constructor.
        :param host: where to bind server to
        :param port: port to run server on
        """
        self.status_code = DEFAULT_HTTP_STATUS
        self.host = host
        self.port = port
        self._app = Server._endpoint
        self._server = make_server(self.host, self.port, self._app)
        self._running = False

    def start(self):
        """
        Starts the server (non-blocking).
        """
        if not self._running:
            Thread(target=self.run).start()

    def run(self):
        """
        Runs the server (blocking).
        """
        if not self._running:
            self._running = True
            self._server.serve_forever()

    def stop(self):
        """
        Stops the server if running.
        """
        if self._running:
            self._running = False
            self._server.shutdown()
