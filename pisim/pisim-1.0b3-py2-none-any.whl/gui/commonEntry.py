# -*- coding: utf-8 -*-

"""Definition of extended widgets.

These extended widgets incorporate a subclass of the Tkinter string
control variable - holding the widget's content - and inherit
the :py:class:`.Node` class to be able to receive/send signals and process
them - likely to set their enabled/disabled state accordingly.

Module's content
================

"""

import ttk
from datetime import datetime
import signals


class ConvertedStringVar(ttk.Tkinter.StringVar):
    """Tkinter string control variable sublcass.

    This special control variable allows the used to specify
    conversion procedures for both set and get operations.
    """

    def __init__(self, setConvF=None, getConvF=None, **kwargs):
        """Constructor.

        :param func setConvF: conversion procedure for variable set.
            Procedure must accept a value and return a string
            containing the value's converted version.
        :param func getConvF: conversion procedure for variable get.
            Procedure must accept the widget's content - in form of
            string - and return the value's converted version.
        :param dict kwargs: additional parameters to be passed to
            the Tkinter variable's constructor.
        """
        ttk.Tkinter.StringVar.__init__(self, **kwargs)
        self._setConvF = setConvF
        self._getConvF = getConvF

    def read(self):
        """Return the converted widget's content."""
        retVal = ttk.Tkinter.StringVar.get(self)
        if self._getConvF:
            retVal = self._getConvF(retVal)
        return retVal

    def write(self, value):
        """Convert value and set the widget's content."""
        tmpVal = value
        if self._setConvF:
            tmpVal = self._setConvF(value)
        ttk.Tkinter.StringVar.set(self, tmpVal)


class TrackedWidget(signals.Node):
    """Extented widget base class.

    This class enables continuous tracking of any widget content,
    its validation and updating of a specific, output signal.
    No input signals are allowed.
    """

    @staticmethod
    def _getArgs(kwargs, args):
        tmp1 = {k: kwargs[k] for k in args if k in kwargs}
        tmp2 = {k: kwargs[k] for k in kwargs if k not in tmp1}
        return tmp1, tmp2

    @staticmethod
    def _voidVarChangeCallback(*args):
        return

        # Handling of 'invalid' state and related style is
        # a little bit convoluted here
        # requires continous tracking of tracked variable and continuous
        # assessment of state
        # because validity check on entry's lost focus event doesn't work
        # because it seems that 'invalid' state does not persist through focus
        # events
        # See explanation and solution (adopted here) here:
        # https://stackoverflow.com/questions/30337351/how-can-i-ensure-my-ttk-entrys-invalid-state-isnt-cleared-when-it-loses-focus

    def __init__(self, master, name='', description='',
                 setConvF=None, getConvF=None):
        """Constructor.

        :param object master: Widget's master widget.
        :param str name: User-defined widget name.
        :param str description: Widget's description.
        :param func setConvF: Conversion-on-write function passed to
            internal :py:class:`ConvertedStringVar` instance.
        :param func getConvF: Conversion-on-read function passed to
            internal :py:class:`ConvertedStringVar` instance.
        """
        signals.Node.__init__(self)

        self.master = master
        self.name = name
        self.description = description
        self._varChangeCallback = TrackedWidget._voidVarChangeCallback

        #: Widget's internal control variable, storing the content.
        #: May be accessed from the outside to read/write its content
        #: by using :py:class:`ConvertedStringVar` APIs.
        self.var = ConvertedStringVar(setConvF, getConvF)
        self.var.trace('w', self._tracedVarWCallback)

    def _tracedVarWCallback(self, *args):
        self._varChangeCallback(args)
        self.state(['!invalid' if self._validateEntry() else 'invalid'])

    def _validateEntry(self):
        """Check widget's content validity at focus change event.

        To be used as ``validatecommand`` parameter in the child widget
        constructor, with ``focus`` as validate mode.
        """
        currState = self._checkValue()
        for s in self._outSignals:
            s.state = currState
        return currState

    def traceVarChange(self, callback):
        """Enable internal control variable tracking on change.

        :param func callback: User-provided function that will be called
            whenever the widget's content changes. It must accept the
            same input parameters as standard Tkinter control variable
            tracking function.
        """
        self._varChangeCallback = callback

    def _checkValue(self):
        """Check if the widget's content is valid or not.

        It's called whenever the widget's content change. It can
        be redefined by subclasses.

        :returns: ``True`` if the widget's content is valid, ``False``
            otherwise.
        """
        return True

    def _checkInSignal(self, signal):
        return False

    def _checkOutSignal(self, signal):
        return len(self._outSignals) == 0

    def _procRxSignals(self, *args):
        pass


class EnhEntryBase(TrackedWidget, ttk.Entry):
    """Extended ttk.Entry widget."""

    def __init__(self, master, **kwargs):
        """Constructor.

        :param object master: Widget's parent widget.
        :param dict kwargs: Any other initialization parameter.
            ``name``, ``description``, ``setConvF``, ``getConvF`` are given to
            :py:class:`TrackedWidget`, everything else to the widget's
            constructor.
        """
        tmp, kwargs = TrackedWidget._getArgs(
            kwargs, ['name', 'description', 'setConvF', 'getConvF'])

        if 'justify' not in kwargs:
            kwargs['justify'] = ttk.Tkinter.LEFT

        TrackedWidget.__init__(self, master, **tmp)
        ttk.Entry.__init__(
            self,
            master,
            textvariable=self.var,
            style='valid.TEntry',
            validate='focus',
            validatecommand=master.register(self._validateEntry),
            **kwargs)


class DescriptorNameEntry(EnhEntryBase):
    """Tracked widget for showing/entering descriptor's name.

    It verifies that the used characters are from a predefined set.
    """

    def _checkValue(self, *args):
        currVal = self.var.get()
        if not currVal:
            return False
        else:
            return set(
                ('abcdefghijklmnopqrstuvwxyz'
                 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                 '0123456789-_.')).issuperset(self.var.get())


class EnhOptionMenu(TrackedWidget, ttk.OptionMenu):
    """Extended ttk.OptionMenu, tracking the id of the selected item.

    The internal :py:data:`TrackedWidget.var` tracks the id of the selected
    item in the provided list of values instead the item itself.
    """

    def __init__(self, master, values, defaultId=None, **kwargs):
        """Constructor.

        :param object master: Widget's parent widget.
        :param list(str) values: Widget's list ov values.
        :param int defaultId: Starting selected item (id in ``values`` list.).
        :param dict kwargs: Any other initialization parameter.
            ``name``, ``description``, ``setConvF``, ``getConvF`` are given to
            :py:class:`TrackedWidget`, everything else to the widget's
            constructor.
        """
        tmp, kwargs = TrackedWidget._getArgs(
            kwargs, ['name', 'description', 'setConvF', 'getConvF'])

        TrackedWidget.__init__(self, master, **tmp)

        # From:
        # https://stackoverflow.com/questions/19138534/tkinter-optionmenu-first-option-vanishes
        # ttk.OptionMenu.__init__ signature is the following:
        # def __init__(self, master, variable, default=None,
        #              *values, **kwargs):

        ttk.OptionMenu.__init__(
            self,
            master,
            self.var,
            None,
            *values,
            **kwargs)
        if defaultId is not None:
            self.var.set(values[defaultId])


class DateEntry(EnhEntryBase):
    """Extended widget to handle date values with "dd/mm/aaaa" format."""

    def __init__(self, master, **kwargs):
        """Constructor.

        :param object master: Widget's parent widget.
        :param dict kwargs: Any other initialization parameter, given to
            :py:class:`EnhEntryBase` constructor.
        """
        EnhEntryBase.__init__(
            self,
            master,
            getConvF=lambda x: datetime.strptime(x, "%d/%m/%Y").date(),
            setConvF=lambda x: x.strftime("%d/%m/%Y") if x else x,
            **kwargs)

    def _checkValue(self, *args):
        try:
            datetime.strptime(self.var.get(), '%d/%m/%Y')
            return True
        except ValueError:
            return False


class FloatEntry(EnhEntryBase):
    """Extended widget for float values."""

    def _checkValue(self, *args):
        try:
            float(self.var.get())
            return True
        except ValueError:
            return False


class FloatPositiveEntry(EnhEntryBase):
    """Extended widget for positive float values."""

    def __init__(self, master, **kwargs):
        """Constructor.

        :param object master: Widget's parent widget.
        :param dict kwargs: Any other initialization parameter, given to
            :py:class:`EnhEntryBase` constructor.
        """
        EnhEntryBase.__init__(
            self,
            master,
            getConvF=self._getConvF,
            **kwargs)

    def _checkValue(self, *args):
        try:
            val = float(self.var.get())
            return val > 0
        except ValueError:
            return False

    def _getConvF(self, text):
        try:
            return float(text)
        except ValueError:
            return None


class PercentageEntry(FloatEntry):
    """Extended widget for percentage float values.

    Widget is given values float values which are converted into percentage
    when shown (multiplied to 100) /read (divided by 100).
    """

    def __init__(self, master, *args, **kwargs):
        """Constructor.

        :param object master: Widget's parent widget.
        :param dict kwargs: Any other initialization parameter, given to
            :py:class:`FloatEntry` constructor.
        """
        FloatEntry.__init__(
            self,
            master,
            setConvF=lambda x: float(x)*100.0 if x != '' else x,
            getConvF=lambda x: float(x)/100.0,
            *args, **kwargs)


class PercentagePositiveEntry(EnhEntryBase):
    """Extended widget for positive percentage values."""

    def __init__(self, master, *args, **kwargs):
        """Constructor.

        :param object master: Widget's parent widget.
        :param list args: Any other initialization parameter, given to
            :py:class:`EnhEntryBase` constructor.
        :param dict kwargs: Any other initialization parameter, given to
            :py:class:`EnhEntryBase` constructor.
        """
        EnhEntryBase.__init__(
            self,
            master,
            setConvF=self._setConvF,
            getConvF=self._getConvF,
            *args, **kwargs)

    def _checkValue(self, *args):
        try:
            return float(self.var.get()) > 0 and float(self.var.get()) <= 100
        except ValueError:
            return False

    def _getConvF(self, text):
        try:
            return float(text)/100.0
        except ValueError:
            return None

    def _setConvF(self, value):
        try:
            return value*100.0
        except (ValueError, TypeError):
            return ''


class PercentageNotNegativeEntry(EnhEntryBase):
    """Extended widget for not negative percentage values."""

    def __init__(self, master, *args, **kwargs):
        """Constructor.

        :param object master: Widget's parent widget.
        :param list args: Any other initialization parameter, given to
            :py:class:`EnhEntryBase` constructor.
        :param dict kwargs: Any other initialization parameter, given to
            :py:class:`EnhEntryBase` constructor.
        """
        EnhEntryBase.__init__(
            self,
            master,
            setConvF=self._setConvF,
            getConvF=self._getConvF,
            *args, **kwargs)

    def _checkValue(self, *args):
        try:
            return float(self.var.get()) >= 0 and float(self.var.get()) <= 100
        except ValueError:
            return False

    def _getConvF(self, text):
        try:
            return float(text)/100.0
        except ValueError:
            return None

    def _setConvF(self, value):
        try:
            return value*100.0
        except (ValueError, TypeError):
            return ''


class FloatNotNegativeEntry(EnhEntryBase):
    """Extended widget for not negative float values."""

    def __init__(self, master, **kwargs):
        """Constructor.

        :param object master: Widget's parent widget.
        :param dict kwargs: Any other initialization parameter, given to
            :py:class:`EnhEntryBase` constructor.
        """
        EnhEntryBase.__init__(
            self,
            master,
            getConvF=self._getConvF,
            **kwargs)

    def _checkValue(self, *args):
        try:
            val = float(self.var.get())
            return val >= 0
        except ValueError:
            return False

    def _getConvF(self, text):
        try:
            return float(text)
        except ValueError:
            return None


class IntEntry(EnhEntryBase):
    """Extended widget for integer values."""

    def __init__(self, master, **kwargs):
        """Constructor.

        :param object master: Widget's parent widget.
        :param dict kwargs: Any other initialization parameter, given to
            :py:class:`EnhEntryBase` constructor.
        """
        EnhEntryBase.__init__(
            self,
            master,
            getConvF=self._getConvF,
            **kwargs)

    def _checkValue(self, *args):
        try:
            int(self.var.get())
            return True
        except ValueError:
            return False

    def _getConvF(self, text):
        try:
            return int(text)
        except ValueError:
            return None


class IntPositiveEntry(EnhEntryBase):
    """Extended widget for positive integer values."""

    def __init__(self, master, **kwargs):
        """Constructor.

        :param object master: Widget's parent widget.
        :param dict kwargs: Any other initialization parameter, given to
            :py:class:`EnhEntryBase` constructor.
        """
        EnhEntryBase.__init__(
            self,
            master,
            getConvF=self._getConvF,
            **kwargs)

    def _checkValue(self, *args):
        try:
            val = int(self.var.get())
            return val > 0
        except ValueError:
            return False

    def _getConvF(self, text):
        try:
            return int(text)
        except ValueError:
            return None


class RemotelyEnabledButton(ttk.Button, signals.Sink):
    """Extended ttk.Button widget, being remotely disabled using a signal.

    Being a :py:class:`.Sink` subclass, this widget may be connected to
    another :py:class.`.Node` instance to receive its signal. In this way,
    also considering the possibility of setting up a network of nodes,
    it's possible to automatically set the buttons's enable/disable status
    by a combination of extended widgets' validity statuses.
    """

    def __init__(self, master, *args, **kwargs):
        """Constructor.

        :param object master: Widget's parent widget.
        :param dict args: Any other initialization parameter, given to
            ``ttk.Button`` constructor.
        :param dict kwargs: Any other initialization parameter, given to
            ``ttk.Button`` constructor.
        """
        ttk.Button.__init__(self, master, *args, **kwargs)
        signals.Sink.__init__(self, self._enableDisableCallback)

    def _enableDisableCallback(self, s):
        self['state'] = \
            (ttk.Tkinter.NORMAL if s.state else ttk.Tkinter.DISABLED)
