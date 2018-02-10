#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtNetwork
from .const import Spec
from .reply import Reply
from .message import Message
from .utils import qdelay


class Qonnection(QtCore.QObject):
    sigConnectedToSpec = QtCore.pyqtSignal()
    sigSpecReplyArrived = QtCore.pyqtSignal(object, object)
    sigError = QtCore.pyqtSignal(str)
    DelayAbort = 100  # ms
    StartingReconnectDelay = 500  # ms
    MaxReconnectDelay = 64000  # ms

    def __init__(self, address, *, reconnect=True):
        """
        Spec address should be a tuple in one of the following form:
        (spec_host, tcp_port)  <- (str, int)
        (spec_host, spec_name) <- (str, str)
        """
        super().__init__()
        self._address = address
        self._aborting = False
        self._reconnecting = False
        self._searching = False
        self._name = ''
        self._last_packet = b''
        self._reconnect_delay = self.StartingReconnectDelay
        self._reconnect = reconnect
        self._sock = QtNetwork.QTcpSocket()
        self._connect()

    def _connect(self):
        host, port = self._address
        self._host = host
        try:
            self._port = int(port)
        except ValueError:
            self._searching = True
            self._port = Spec.MinPort
            self._name = port
        else:
            self._name = ''
            self._searching = False
        self._connectToSpec()

    def _connectToSpec(self):
        self._message = Message()
        self._reply = Reply()
        self._setSocket()
        self._connectSignals()
        self._sock.connectToHost(self._host, self._port)

    def send(self, message):
        state = self._sock.state()
        if state == self._sock.ConnectedState:
            self._sock.write(message)
        elif state == self._sock.UnconnectedState and not self._searching:
            if self._reconnect:
                self._last_packet = message
                self.reconnect()
            else:
                self.sigError.emit(f'Lost connection to {self._name} at {self._host}:{self._port}')
        else:
            self.sigError.emit(f'Trying to send messages without established connection to {self._name}')

    def _setSocket(self):
        self._sock.close()
        self._sock = QtNetwork.QTcpSocket(self)
        self._sock.setProxy(QtNetwork.QNetworkProxy(QtNetwork.QNetworkProxy.NoProxy))

    # noinspection PyUnresolvedReferences
    def _connectSignals(self):
        self._sock.connected.connect(self._sayHello)
        self._sock.readyRead.connect(self._readResponse)
        self._sock.disconnected.connect(self._disconnected)
        self._sock.error.connect(self._serverHasError)

    def _sayHello(self):
        self._reconnecting = False
        self.send(self._message.hello())

    def _checkLastPacket(self):
        self._reconnect_delay = self.StartingReconnectDelay
        if self._last_packet:
            self.send(self._last_packet)
            self._last_packet = b''

    def _setConnected(self, answer):
        if self._searching and answer == self._name:
            self._searching = False
            self._address = self._host, self._port
            self._checkLastPacket()
            return True
        if not self._searching:
            self._name = answer
            self._checkLastPacket()
            return True
        return False

    def _searchNextPort(self):
        self._port += 1
        if self._port > Spec.MaxPort:
            self.sigError.emit(f'Count not find {self._name} on the host {self._host}. '
                               f'Probably spec is not running at all. Stop connecting...')
            self.close()
        else:
            self._connectToSpec()

    def _readResponse(self):
        buf = bytes(self._sock.readAll())
        for header, answer in self._reply.unpack(buf):
            if header.cmd == Spec.HelloReply:
                if self._setConnected(answer):
                    self.sigConnectedToSpec.emit()
                else:
                    self._searchNextPort()
            self.sigSpecReplyArrived.emit(header, answer)

    def _disconnected(self):
        if not self._searching and self._port <= Spec.MaxPort:
            self.sigError.emit(f'The connection to {self._name} at {self._host}:{self._port} has been stopped')
            self.reconnect()

    def reconnect(self):
        if self._port <= Spec.MaxPort:
            QtCore.QTimer.singleShot(0, self._tryReconnect)

    def _tryReconnect(self):
        if self._reconnect and not self._reconnecting:
            self._reconnecting = True
            if self._reconnect_delay < self.MaxReconnectDelay:
                self._reconnect_delay *= 2
            self.sigError.emit(f'Trying to reconnect in {self._reconnect_delay // 1000} seconds...')
            QtCore.QTimer.singleShot(self._reconnect_delay, self._connectToSpec)

    def _serverHasError(self):
        if self._searching:
            self._searchNextPort()
        else:
            self.sigError.emit(f'The server {self._name} at {self._host}:{self._port} has an error: '
                               f'{self._sock.errorString()}')
            self.reconnect()

    def close(self):
        self._searching = False
        self._reconnecting = False
        self._disconnected()
        self._sock.close()

    def __repr__(self):
        return f'<Qt SpecConnection to {self._name} running at {self._host}:{self._port}>'

    @property
    def connected(self):
        return self._sock.ConnectedState == self._sock.state() and not self._searching

    @property
    def name(self):
        return self._name

    @property
    def message(self):
        return self._message

    @property
    def address(self):
        return self._address

    def abort(self):
        if not self._aborting:
            self._aborting = True
            self.send(self._message.abort())
            qdelay(self.DelayAbort)
            self._aborting = False
