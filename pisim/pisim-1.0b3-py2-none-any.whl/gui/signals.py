# -*- coding: utf-8 -*-

"""Facilities to convey and combine widget's valid/non valid status.

Many GUI elements are enabled/disabled according to the content of other
widgets (typically those where the user can put values) and their combinations.
For instance, a save button can be made enabled only if two textboxes
(both of them) contain a valid value - where 'valid' definition is up to
the app implementer.

Classes in this module provide the fundamental building blocks to enable
such type of widgets interactions. Widget classes are sublcassed in
:py:mod:`.commonEntry` to embed this functionality.

Module's content
================

"""

import ttk


class SignalsErrorBase(Exception):
    """Module's base exception, doing nothing."""

    pass


class SignalNameExistingError(SignalsErrorBase):
    """Raised when a user defined signal name is already existing."""

    def __init___(self, node, sName):
        """Constructor.

        :param object node: :py:class:`Node` instance.
        :param str sName: duplicate signal name.
        """
        self._node = node
        self._sName = sName

    def __str__(self):
        """Error message."""
        return "Nome segnale '{}' già esistente per nodo '{}'".format(
            self._sName, self._node._internalName)


class Signal(object):
    """Class implementing the valid/invalid signal.

    This signal is meant to be originated by a widget (as user inserts or
    modifies the content), travel towards the intended sink
    - likely be combined (in a boolean sense) with other signals -
    and eventually change the status of a destination widget like a button.

    Class is basically a wrapper around a Tkinter boolean control variable.
    The variable may be accessed from the outside and written - thus
    setting the signal's value. The class traces the write operations on such
    a variable, and if the signal's state change a user-provided callback
    is fired.
    """

    #: Class-level data member used in giving internal Tkinter control
    #: variables a unique name.
    _prefixCnt = 0

    def __init__(self, name, fromNode, toNode, callback=None,
                 initialState=False):
        """Constructor.

        :param str name: user-defined signal name.
        :param object fromNode: :py:class:`Node` instance, source of the
            signal.
        :param object toNode: :py:class:`Node` instance, destination of the
            signal.
        :param function callback: User-defined callback to be fired when
            the signal changes state; it's given in input the signal instance
            that has fired it.
        :param bool initialState: The signal's initial state.
        """
        # self._internalName is used for the control variabile.
        # For this reason is must be unique
        # (otherwise all variables with the same name will be triggered).
        # That's why an internal name is built in that way.

        #: Tkinter variable name.
        self._internalName = "SIG{:d}".format(Signal._prefixCnt)

        #: Signal's user defined name.
        self._userName = name
        Signal._prefixCnt += 1

        #: Tkinter control variable.
        self._inSignal = ttk.Tkinter.BooleanVar(name=self._internalName)
        if initialState is not None:
            self._inSignal.set(initialState)
        self._inSignal.trace('w', self._process)

        #: Signal's destination node.
        self._toNode = toNode
        #: Signal's originating node.
        self._fromNode = fromNode

        #: Signal's current state.
        self._currentState = initialState

        #: User-provided callback:.
        self._callback = callback

    def _process(self, *args):
        """Private method called when :py:data:`_inSignal` value is written."""
        if self._currentState != self._inSignal.get():
            self._currentState = self._inSignal.get()
            if self._callback:
                self._callback(self)

    @property
    def fromNode(self):
        """Return :py:data:`_fromNode`."""
        return self._fromNode

    @property
    def toNode(self):
        """Return :py:data:`_toNode`."""
        return self._toNode

    @property
    def state(self):
        """Return :py:data:`_currentState`."""
        return self._currentState

    @state.setter
    def state(self, value):
        """Set :py:data:`_inSignal` value.

        :param bool value: New Tkinter control variable value.
        """
        self._inSignal.set(value)

    @property
    def userName(self):
        """Return :py:data:`_userName`."""
        return self._userName

    @property
    def stateChangeCallback(self):
        """Return the callback fired when the signal's state changes."""
        return self._callback

    @stateChangeCallback.setter
    def stateChangeCallback(self, callback):
        """Set the callback fired when the signal's state changes.

        :param func callback: Callback name.
        """
        self._callback = callback


class Node():
    """Generic signal producer/consumer.

    Any instance of such a class may have whatever number of input signals
    and whatever number of output signals. By sublcassing the user define the
    node's behavior in terms of changing output signals status upon
    a status change on an input signal.

    This class has to be subclassed to define:

    * If/when a new input signal may be added;
    * If/when a new output signal may be added;
    * Actual processing when any input signal changes its state.

    Methods the user shall define in subclasses are:

    * :py:meth:`_procRxSignals`
    * :py:meth:`_checkInSignal`
    * :py:meth:`_checkOutSignal`
    """

    #: Class-level data member used in giving class instance's internal name
    #: an unique value.
    _prefixCnt = 0

    def __init__(self):
        """Constructor."""
        #: Node's internal name.
        self._internalName = "NODE{:d}".format(Node._prefixCnt)
        Node._prefixCnt += 1

        #: List of input signals.
        self._inSignals = []
        #: List of output signals.
        self._outSignals = []
        #: Dictionary of user-added output signals.
        #: This is an helper to sublcasses to allow them easily retrieving
        #: such a type of signals - e.g. because an internal event needs
        #: to be signaled to the outside by changing the state of a signal.
        self._userDefinedOutSignals = {}

    def _procRxSignals(self, *args):
        """Process the set of input signals.

        It's called when an input signal is triggered.

        To be redefined by subclasses.

        :raises NotImplementedError:
        """
        raise NotImplementedError

    def _checkInSignal(self, signal):
        """Define if a new input signal has to be accepted or not.

        To be implemented by children.

        :param Signal signal: Signal whose inclusion in the input set
            has to be decided.
        :returns: If the new input signal is accepted or not.
        :rtype: bool

        :raises NotImplementedError:
        """
        raise NotImplementedError

    def _checkOutSignal(self, signal):
        """Define if a out input signal has to be accepted or not.

        To be implemented by children.

        :param Signal signal: Signal whose inclusion in the output set
            has to be decided.
        :returns: If the new out signal is accepted or not.
        :rtype: bool

        :raises NotImplementedError:
        """
        raise NotImplementedError

    def _addIn(self, signal):
        """Private method to add a new input signal.

        Signal insertion is done only if :py:meth:`_checkInSignal`
        returns ``True``.
        """
        if signal in self._inSignals:
            return
        if self._checkInSignal(signal):
            signal.stateChangeCallback = self._procRxSignals
            self._inSignals.append(signal)

    def _addOut(self, signal, userDefined):
        """Private method to add a new output signal.

        Signal insertion is done only if :py:meth:`_checkOutSignal`
        returns ``True``.

        :param bool userDefined: Set to ``True`` makes the signal reference
            be added to the :py:data:`_userDefinedOutSignals` dictionary.
        """
        if self._checkOutSignal(signal):
            self._outSignals.append(signal)
            if userDefined:
                self._userDefinedOutSignals[signal.userName] = signal

    def join(self, toNode, signalName=None):
        """Create a connection to another node using a signal.

        The signal connecting the two nodes is here allocated and stored in
        this node's :py:data:`_addOut` and toNode's
        :py:data:`_inSignals`.

        :param object toNode: Node's instance being the destination of
            the connection.
        :param str signalNode: Optional. If provided, reference to the
            allocated signal is stored in the :py:data:`_userDefinedOutSignals`
            dictionary, ``signalNode`` being the key. In such a situation,
            however, nodes will be connected only if a signal with the same
            name hasn't been stored yet; if so, an exception is raised.
        """
        if not signalName:
            s = Signal(name='undef', toNode=toNode, fromNode=self)
        elif signalName not in self._userDefinedOutSignals:
            s = Signal(name=signalName, toNode=toNode, fromNode=self)
        else:
            raise SignalNameExistingError(self, signalName)
        self._addOut(s, userDefined=(signalName is not None))
        toNode._addIn(s)


class Dup(Node):
    """Duplication Node.

    it takes the value of the input signal (only one allowed) and replicates
    it to all the output signals.
    """

    def _procRxSignals(self, *args):
        for s in self._outSignals:
            s.state = self._inSignals[0].state

    def _checkInSignal(self, signal):
        return len(self._inSignals) == 0

    def _checkOutSignal(self, signal):
        return True


class And(Node):
    """AND boolean operation Node.

    It takes the value of all the input signals and put their AND
    to the output signal (only one allowed.)
    """

    def _procRxSignals(self, s):
        res = False
        if s.state:
            res = False not in [ins.state for ins in self._inSignals]
        try:
            self._outSignals[0].state = res
        except IndexError:
            pass

    def _checkInSignal(self, signal):
        return True

    def _checkOutSignal(self, signal):
        return len(self._outSignals) == 0


class Or(Node):
    """OR boolean operation Node.

    It takes the value of all the input signals and put their OR
    to the output signal (only one allowed.)
    """

    def _procRxSignals(self, s):
        res = True in [ins.state for ins in self._inSignals]
        try:
            self._outSignals[0].state = res
        except IndexError:
            pass

    def _checkInSignal(self, signal):
        return True

    def _checkOutSignal(self, signal):
        return len(self._outSignals) == 0


class Sink(Node):
    """Sink Node.

    It fires a user-provided callback whenever an input signal (many allowed)
    changes its state. No output signal allowed.
    """

    def __init__(self, signalRxCallback):
        """Constructor.

        :param func signalRxCallback: reference to a user-defined procedure,
            which will be called whenever an input signal (passed to the
            callback as input parameter) changes its state.
        """
        Node.__init__(self)
        self._signalRxCallback = signalRxCallback
        pass

    def _procRxSignals(self, *args):
        self._signalRxCallback(*args)

    def _checkInSignal(self, signal):
        return True

    def _checkOutSignal(self, signal):
        return False
