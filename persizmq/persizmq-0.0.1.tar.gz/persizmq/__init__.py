#!/usr/bin/env python3

"""
Provides persistence to zeromq.
"""

import copy
import pathlib
import threading
import time
from typing import List, Optional, Callable, Union  # pylint: disable=unused-import

import zmq


class ThreadedSubscriber:
    """
    Takes a subscriber and listens in a separate thread for messages. Communicates the message to the outside through
    a callback. Locking should be considered by the callback provider.
    """
    def __init__(self,
                 subscriber: zmq.Socket,
                 callback: Callable[[bytes], None],
                 on_exception: Callable[[Exception], None],
                 poll_period: float = 0.001):
        """
        :param subscriber: zeromq subscriber
        :param callback:
            This function is called every time a message is received. Can be accessed and changed later
            through ThreadedSubscriber.callback
        :param on_exception: Is called when an exception occurs during the callback call.
        :param poll_period: waiting time in seconds between two checks for a message on the zeromq
        """
        if isinstance(subscriber, zmq.Socket):
            self.__socket = subscriber
        else:
            raise TypeError("unexpected type of the argument socket: {}".format(subscriber.__class__.__name__))

        self.callback = callback
        self.on_expection = on_exception
        self.poll_period = poll_period

        self.__received_shutdown_signal = False
        self.operational = False

        self.__thread = None  # type: Optional[threading.Thread]

    def __listen(self) -> None:
        """
        Listener thread that listens on the zeromq subscriber
        :return: None
        """
        # pylint: disable=too-many-branches
        while not self.__received_shutdown_signal:
            try:
                msg = self.__socket.recv(zmq.DONTWAIT)  # pylint: disable=no-member
                self.callback(copy.deepcopy(msg))
            except zmq.Again:
                time.sleep(self.poll_period)
            except Exception as err:
                self.on_expection(err)

    def init(self):
        """
        Starts listening on messages in a parallel thread.
        :return: None
        """
        if self.operational:
            return

        self.__thread = threading.Thread(target=self.__listen)
        self.__thread.start()
        self.operational = True

    def shutdown(self) -> None:
        """
        Shuts down the threaded subscriber.
        :return: None
        """
        self.__received_shutdown_signal = True
        self.__thread.join()
        self.operational = False

    def __enter__(self):
        self.init()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.operational:
            self.shutdown()


class PersistentStorage:
    """
    Persists received messages on disk.
    """

    def __init__(self, persistent_dir: Union[str, pathlib.Path]):

        if isinstance(persistent_dir, str):
            self.__persistent_dir = pathlib.Path(persistent_dir)
        elif isinstance(persistent_dir, pathlib.Path):
            self.__persistent_dir = persistent_dir
        else:
            raise TypeError(
                "unexpected type of argument persistent_dir: {}".format(persistent_dir.__class__.__name__))

        self.__persistent_dir.mkdir(exist_ok=True, parents=True)

        self.__mu = threading.Lock()

        self.__first = None  # type: Optional[bytes]
        self.__paths = []  # type: List[pathlib.Path]
        self.__count = 0  # To count messages and name them, so that naming conflicts can be avoided.

        files = sorted(list(self.__persistent_dir.iterdir()))
        for path in files:
            if path.suffix == ".bin":
                self.__paths.append(path)
            elif path.suffix == ".tmp":
                path.unlink()

        if self.__paths:
            stem = self.__paths[-1].stem
            value_err = None  # type: Optional[ValueError]
            try:
                self.__count = int(stem) + 1
            except ValueError as err:
                value_err = err

            if value_err is not None:
                raise ValueError("Failed to reinitialize from the file {!r}. Please make sure nobody else writes files "
                                 "to the persistent directory.".format(self.__paths[-1]))

            pth = self.__paths[0]
            self.__first = pth.read_bytes()

    def front(self) -> Optional[bytes]:
        """
        Makes a copy of the first pending message, but does not remove it from the persistent storage's
        internal queue.

        :return: copy of the first message, or None if no message in the queue
        """
        with self.__mu:  # pylint: disable=not-context-manager
            if self.__first is None:
                return None

            msg = copy.deepcopy(self.__first)
            return msg

    def pop_front(self) -> bool:
        """
        Removes a message from the persistent storage's internal queue.

        :return: True if there was a message in the queue
        """
        with self.__mu:  # pylint: disable=not-context-manager
            if self.__first is None:
                return False

            pth = self.__paths.pop(0)
            pth.unlink()

            if not self.__paths:
                self.__first = None
            else:
                pth = self.__paths[0]
                self.__first = pth.read_bytes()
            return True

    def add_message(self, msg: Optional[bytes]) -> None:
        """
        Adds a message to the persistent storage's internal queue.
        :param msg: message to be added
        """
        if msg is None:
            return

        with self.__mu:  # pylint: disable=not-context-manager

            # Make sure the files can be sorted as strings (which breaks if you have files=[3.bin, 21.bin])
            pth = self.__persistent_dir / "{:030d}.bin".format(self.__count)
            tmp_pth = pth.with_suffix(".tmp")  # type: Optional[pathlib.Path]

            try:
                tmp_pth.write_bytes(msg)
                tmp_pth.rename(pth)
                tmp_pth = None

                self.__paths.append(pth)
                self.__count += 1

                if self.__first is None:
                    self.__first = msg

            finally:
                if tmp_pth is not None and tmp_pth.exists():
                    tmp_pth.unlink()


class PersistentLatestStorage:
    """
    Persists only the latest received message.
    """

    def __init__(self, persistent_dir: Union[str, pathlib.Path]):
        if isinstance(persistent_dir, str):
            self.__persistent_dir = pathlib.Path(persistent_dir)
        elif isinstance(persistent_dir, pathlib.Path):
            self.__persistent_dir = persistent_dir
        else:
            raise TypeError(
                "unexpected type of argument persistent_dir: {}".format(persistent_dir.__class__.__name__))

        self.__persistent_dir.mkdir(exist_ok=True, parents=True)

        self.__mu = threading.Lock()

        self.__message = None  # type: Optional[bytes]
        self.__persistent_file = self.__persistent_dir / "persistent_message.bin"
        self.new_message = False

        if self.__persistent_file.exists():
            self.__message = self.__persistent_file.read_bytes()
            self.new_message = True

    def add_message(self, msg: Optional[bytes]) -> None:
        """
        Replaces the latest message in the internal storage.
        :param msg: new message
        """
        if msg is None:
            return

        with self.__mu:
            tmp_pth = self.__persistent_file.with_suffix(".tmp")
            try:
                tmp_pth.write_bytes(msg)
                tmp_pth.rename(self.__persistent_file)

                self.new_message = True
                self.__message = msg
            finally:
                if tmp_pth.exists():
                    tmp_pth.unlink()

    def message(self) -> Optional[bytes]:
        """
        Get the latest message. Use PersistentLatestStorage.newmessage to check if a new one has arrived.
        :return: latest message or None, if no message so far.
        """
        with self.__mu:
            self.new_message = False
            return copy.deepcopy(self.__message)


class PersistentPublisher:
    """
    Stores any message to disk prior to publishing it. If there is a persisted message on the disk, it is (re-)published
    at the initialization. Once the message was successfully published, it is removed from the disk.
    """
    def __init__(self, persistent_dir: Union[str, pathlib.Path], publisher: zmq.Socket):
        if isinstance(persistent_dir, str):
            self.__persistent_file = pathlib.Path(persistent_dir) / "persistent_message.bin"
        elif isinstance(persistent_dir, pathlib.Path):
            self.__persistent_file = persistent_dir / "persistent_message.bin"
        else:
            raise TypeError("unexpected type of argument persistent_dir: {}".format(persistent_dir.__class__.__name__))

        if isinstance(publisher, zmq.Socket):
            self.__socket = publisher
        else:
            raise TypeError("unexpected type of argument publisher: {}".format(publisher.__class__.__name__))

        self.operational = False

    def init(self) -> None:
        """
        Initialize
        """
        if self.__persistent_file.exists():
            self.__socket.send(self.__persistent_file.read_bytes())
            self.__persistent_file.unlink()

        if not pathlib.Path(self.__persistent_file.parent).exists():
            pathlib.Path(self.__persistent_file.parent).mkdir(parents=True)

        self.operational = True

    def send(self, msg: bytes) -> None:
        """
        Send message
        :param msg:
        """
        if not self.operational:
            raise RuntimeError("not initialized")

        tmp_pth = self.__persistent_file.with_suffix(".tmp")

        try:
            tmp_pth.write_bytes(msg)
            tmp_pth.rename(self.__persistent_file)

            self.__socket.send(msg)
            self.__persistent_file.unlink()
        finally:
            if tmp_pth.exists():
                tmp_pth.unlink()

    def send_string(self, msg: str):
        """
        Send string
        :param msg:
        """
        self.send(msg.encode())
