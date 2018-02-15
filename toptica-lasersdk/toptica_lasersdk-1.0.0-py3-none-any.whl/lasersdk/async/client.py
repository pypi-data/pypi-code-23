from base64 import b64decode
from base64 import b64encode

from datetime import datetime

from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from ..decof import AccessLevel

from ..decof import DecofType
from ..decof import DecofMetaType
from ..decof import DecofStreamType
from ..decof import DecofStreamMetaType
from ..decof import DecofError
from ..decof import DecofValueError
from ..decof import DecofCallback

from ..decof import decode_value
from ..decof import encode_value
from ..decof import parse_monitoring_line

from .connection import Connection
from .connection import NetworkConnection
from .connection import SerialConnection
from .connection import DeviceNotFoundError
from .connection import DeviceTimeoutError

__all__ = ['Client', 'Subscription', 'DecofCallback', 'NetworkConnection', 'SerialConnection',

           'DecofError', 'DecofValueError', 'DeviceTimeoutError', 'DeviceNotFoundError',

           'DecofBoolean', 'DecofInteger', 'DecofReal', 'DecofString', 'DecofBinary',
           'MutableDecofBoolean', 'MutableDecofInteger', 'MutableDecofReal', 'MutableDecofString', 'MutableDecofBinary']


class Client:
    """An asynchronous DeCoF client.

    Attributes:
        connection (Connection): A connection that is used to communicate with the device.

    """

    def __init__(self, connection: Connection) -> None:
        self._connection = connection
        self._subscriptions = {}  # type: Dict[str, Tuple[DecofMetaType, List[Subscription]]]

    async def __aenter__(self):
        await self.open()
        return self

    async def __aexit__(self, *args):
        await self.close()

    async def open(self) -> None:
        """Opens a connection to a DeCoF device."""
        self._connection.subscribe_monitoring_line(self._monitoring_line_callback)
        await self._connection.open()

    async def close(self) -> None:
        """Closes the connection to the DeCoF device."""
        subscribers = []

        for _, value in self._subscriptions.values():
            subscribers += value

        for subscriber in subscribers:
            await subscriber.cancel()

        await self._connection.close()
        self._subscriptions = {}

    async def change_ul(self, ul: AccessLevel, password: str) -> AccessLevel:
        """Changes the current user level of the command and monitoring line.

        Args:
            ul (AccessLevel): The requested user level.
            password (str): The password for the requested user level.

        Returns:
            AccessLevel: The new access level or the previous one if the password was incorrect.

        """
        # Empty passwords are only allowed for AccessLevel.NORMAL and AccessLevel.READONLY
        if not password and (ul == AccessLevel.NORMAL or ul == AccessLevel.READONLY):
            return AccessLevel(await self.get('ul', int))

        # Change the user level for the command line
        result = AccessLevel(await self.exec('change-ul', int(ul), password, return_type=int))
        
        # Change the user level for the monitoring line
        if self._connection.monitoring_line_supported and result == ul:
            await self._connection.write_monitoring_line('(change-ul {} "{}")\r\n'.format(int(ul), password))
            
        return result

    async def get(self, param_name: str, *param_types: DecofMetaType) -> DecofType:
        """Returns the current value of a DeCoF parameter.

        Args:
            param_name (str): The name of the DeCoF parameter (e.g. 'laser1:enabled').
            param_types (DecofMetaType): One or more types of the DeCoF parameter.

        Returns:
            DecofType: The current value of the parameter.

        """
        await self._connection.write_command_line("(param-ref '{})\n".format(param_name))
        result = await self._connection.read_command_line()

        if len(param_types) == 1:
            return decode_value(result, param_types[0])
        else:
            values = result[1:-1].split(' ')
            if len(values) == len(param_types):
                return tuple(decode_value(pair[0], pair[1]) for pair in zip(values, param_types))
            else:
                raise DecofError("Invalid type list: '{}' for value '{}'".format(param_types, values))

    async def set(self, param_name: str, *param_values: DecofType) -> None:
        """Set a new value for a DeCoF parameter.

        Args:
            param_name (str): The name of the DeCoF parameter (e.g. 'laser1:enabled').
            param_values (DecofType): One or more parameter values.

        Raises:
            DecofError: If the device returned an error when setting the new value.

        """
        values = [encode_value(x) for x in param_values]

        fmt = "(param-set! '{} {})\n" if len(values) == 1 else "(param-set! '{} '({}))\n"

        await self._connection.write_command_line(fmt.format(param_name, ' '.join(values)))
        result = await self._connection.read_command_line()

        status = decode_value(result, int)
        if status != 0:
            raise DecofError("Setting parameter '{}' to '{}' failed: '{}'".format(param_name, param_values, status))

    async def exec(self, name: str, *args, input_stream: DecofStreamType = None, output_type: DecofStreamMetaType = None, return_type: DecofMetaType = None) -> Optional[DecofType]:
        """Execute a DeCoF command.

        Args:
            name (str): The name of the command.
            *args: The parameters of the command.
            input_stream (DecofStreamType): The input stream data of the command.
            output_type (DecofStreamMetaType): The type of the output stream of the command.
            return_type (DecofMetaType): The type of the optional return value.

        Returns:
            Optional[DecofType]: Either the output stream, the return value or a tuple of both.

        """
        param_list = ''
        for param in args:
            param_list += ' ' + encode_value(param)
        await self._connection.write_command_line("(exec '" + name + param_list + ")\n")

        if input_stream and isinstance(input_stream, str):
            await self._connection.write_command_line(input_stream + '#')

        if input_stream and isinstance(input_stream, bytes):
            await self._connection.write_command_line(b64encode(input_stream).decode('ascii') + '#')

        result = await self._connection.read_command_line()
        if result.lower().startswith('error:'):
            raise DecofError(result)

        lines = str.splitlines(result, keepends=True)

        output_value = None  # type: Tuple[bytes,str]
        return_value = None  # type: DecofType

        if output_type is bytes:
            output_value = b64decode(''.join(lines[:-1]).encode())

        if output_type is str:
            output_value = ''.join(lines[:-1])

        if return_type is not None:
            return_value = decode_value(lines[-1], return_type)

        if output_type is not None and return_type is not None:
            return output_value, return_value
        elif output_type is not None:
            return output_value
        elif return_type is not None:
            return return_value

        return None

    async def subscribe(self, param_name: str, param_type: DecofMetaType, callback: DecofCallback = None) -> 'Subscription':
        """Creates a new subscription to updates of a parameter.

        Args:
            param_name (str): The param_name of the parameter.
            param_type (DecofMetaType): The type of the parameter.
            callback (DecofCallback): The callback that will be invoked on parameter updates.

        Returns:
            Subscription: A subscription to updates of the parameter.

        Raises:
            DecofError: If the current connection doesn't support parameter subscriptions.

        """
        if not self._connection.monitoring_line_supported:
            raise DecofError("Current connection does not support parameter subscriptions")

        subscription = Subscription(self, param_name, callback)

        if param_name in self._subscriptions:
            _, subscribers = self._subscriptions[param_name]
            subscribers.append(subscription)
        else:
            await self._connection.write_monitoring_line("(add '{})\r\n".format(param_name))
            self._subscriptions[param_name] = (param_type, [subscription])

        return subscription

    async def unsubscribe(self, subscription: 'Subscription') -> None:
        """Cancels a subscription for parameter updates.

        Args:
            subscription (Subscription): The subscription to cancel.

        """
        try:
            _, subscribers = self._subscriptions[subscription.name]
            subscribers.remove(subscription)

            if not subscribers:
                await self._connection.write_monitoring_line("(remove '{})\r\n".format(subscription.name))
                self._subscriptions.pop(subscription.name)
        except KeyError:
            pass

    def _monitoring_line_callback(self, message: str) -> None:
        """Routes updates of the monitoring line to subscribed callbacks.

        Args:
            message (str): The update message from the monitoring line.

        """
        timestamp, name, value = parse_monitoring_line(message)

        try:
            value_type, subscribers = self._subscriptions[name]

            if isinstance(value, DecofError):
                for subscriber in subscribers:
                    subscriber.update(timestamp, value_type(), value)
            else:
                result = decode_value(value, value_type)
                for subscriber in subscribers:
                    subscriber.update(timestamp, result, None)
        except KeyError:
            pass


class Subscription:
    """A subscription to updates of a parameter.

    Attributes:
        client (Client): A DeCoF client that is used to access the parameter on a device.
        name (str): The fully qualified name of the parameter (e.g. 'laser1:amp:ontime').
        callback (DecofCallback): A callback that will be invoked when the value of the parameter has changed.

    """

    def __init__(self, client: Client, name: str, callback: DecofCallback = None) -> None:
        self._client = client
        self._name = name
        self._callback = callback

    def __aenter__(self):
        return self

    def __aexit__(self, *args):
        if self._client is not None:
            self.cancel()

    def update(self, timestamp: datetime, value: DecofType, exc: DecofError = None) -> None:
        """Invokes the callback with an updated parameter value.

        Args:
            timestamp (datetime): The timestamp of the parameter update.
            value (DecofType): The updated parameter value.
            exc (DecofError): An optional exception that may have occurred.

        """
        if self._callback is not None:
            self._callback(timestamp, self._name, value, exc)

    async def cancel(self) -> None:
        """Cancels the subscription for parameter updates."""
        await self._client.unsubscribe(self)
        self._name = self._client = self._callback = None

    @property
    def name(self) -> str:
        """Returns the name of the parameter this subscription is bound to."""
        return self._name


class DecofBoolean:
    """A read-only DeCoF boolean parameter.

    Attributes:
        client (Client): A DeCoF client that is used to access the parameter on a device.
        name (str): The fully qualified name of the parameter (e.g. 'laser1:amp:ontime').

    """

    def __init__(self, client: Client, name: str) -> None:
        self._client = client
        self._name = name

    @property
    def name(self) -> str:
        """str: The fully qualified name of the parameter."""
        return self._name

    async def get(self) -> bool:
        """Returns the current value of the parameter.

        Returns:
            bool: The current value of the parameter.

        """
        result = await self._client.get(self._name, bool)
        assert isinstance(result, bool)
        return result

    async def subscribe(self, callback: DecofCallback = None) -> 'Subscription':
        """Creates a subscription to updates of the parameter.

        Args:
            callback (DecofCallback): A callback that will be invoked when the value of the parameter has changed.

        Returns:
            Subscription: A subscription to updates of the parameter.

        """
        return await self._client.subscribe(self._name, bool, callback)


class MutableDecofBoolean:
    """A read/write DeCoF boolean parameter.

    Attributes:
        client (Client): A DeCoF client that is used to access the parameter on a device.
        name (str): The fully qualified name of the parameter (e.g. 'laser1:amp:ontime').

    """

    def __init__(self, client: Client, name: str) -> None:
        self._client = client
        self._name = name

    @property
    def name(self) -> str:
        """str: The fully qualified name of the parameter."""
        return self._name

    async def get(self) -> bool:
        """Returns the current value of the parameter.

        Returns:
            bool: The current value of the parameter.

        """
        result = await self._client.get(self._name, bool)
        assert isinstance(result, bool)
        return result

    async def set(self, value: bool) -> None:
        """Updates the value of the parameter.

        Args:
            value (bool): The new value of the parameter.

        """
        assert isinstance(value, bool), "expected type 'bool' for 'value', got '{}'".format(type(value))
        self._client.set(self._name, value)

    async def subscribe(self, callback: DecofCallback = None) -> 'Subscription':
        """Creates a subscription to updates of the parameter.

        Args:
            callback (DecofCallback): A callback that will be invoked when the value of the parameter has changed.

        Returns:
            Subscription: A subscription to updates of the parameter.

        """
        return await self._client.subscribe(self._name, bool, callback)


class DecofInteger:
    """A read-only DeCoF integer parameter.

    Attributes:
        client (Client): A DeCoF client that is used to access the parameter on a device.
        name (str): The fully qualified name of the parameter (e.g. 'laser1:amp:ontime').

    """

    def __init__(self, client: Client, name: str) -> None:
        self._client = client
        self._name = name

    @property
    def name(self) -> str:
        """str: The fully qualified name of the parameter."""
        return self._name

    async def get(self) -> int:
        """Returns the current value of the parameter.

        Returns:
            int: The current value of the parameter.

        """
        result = await self._client.get(self._name, int)
        assert isinstance(result, int)
        return result

    async def subscribe(self, callback: DecofCallback = None) -> 'Subscription':
        """Creates a subscription to updates of the parameter.

        Args:
            callback (DecofCallback): A callback that will be invoked when the value of the parameter has changed.

        Returns:
            Subscription: A subscription to updates of the parameter.

        """
        return await self._client.subscribe(self._name, int, callback)


class MutableDecofInteger:
    """A read/write DeCoF integer parameter.

    Attributes:
        client (Client): A DeCoF client that is used to access the parameter on a device.
        name (str): The fully qualified name of the parameter (e.g. 'laser1:amp:ontime').

    """

    def __init__(self, client: Client, name: str) -> None:
        self._client = client
        self._name = name

    @property
    def name(self) -> str:
        """str: The fully qualified name of the parameter."""
        return self._name

    async def get(self) -> int:
        """Returns the current value of the parameter.

        Returns:
            int: The current value of the parameter.

        """
        result = await self._client.get(self._name, int)
        assert isinstance(result, int)
        return result

    async def set(self, value: int):
        """Updates the value of the parameter.

        Args:
            value (bool): The new value of the parameter.

        """
        assert isinstance(value, int), "expected type 'int' for 'value', got '{}'".format(type(value))
        await self._client.set(self._name, value)

    async def subscribe(self, callback: DecofCallback = None) -> 'Subscription':
        """Creates a subscription to updates of the parameter.

        Args:
            callback (DecofCallback): A callback that will be invoked when the value of the parameter has changed.

        Returns:
            Subscription: A subscription to updates of the parameter.

        """
        return await self._client.subscribe(self._name, int, callback)


class DecofReal:
    """A read-only DeCoF floating point parameter.

    Attributes:
        client (Client): A DeCoF client that is used to access the parameter on a device.
        name (str): The fully qualified name of the parameter (e.g. 'laser1:amp:ontime').

    """

    def __init__(self, client: Client, name: str) -> None:
        self._client = client
        self._name = name

    @property
    def name(self) -> str:
        """str: The fully qualified name of the parameter."""
        return self._name

    async def get(self) -> float:
        """Returns the current value of the parameter.

        Returns:
            float: The current value of the parameter.

        """
        result = await self._client.get(self._name, float)
        assert isinstance(result, float)
        return result

    async def subscribe(self, callback: DecofCallback = None) -> 'Subscription':
        """Creates a subscription to updates of the parameter.

        Args:
            callback (DecofCallback): A callback that will be invoked when the value of the parameter has changed.

        Returns:
            Subscription: A subscription to updates of the parameter.

        """
        return await self._client.subscribe(self._name, float, callback)


class MutableDecofReal:
    """A read/write DeCoF floating point parameter.

    Attributes:
        client (Client): A DeCoF client that is used to access the parameter on a device.
        name (str): The fully qualified name of the parameter (e.g. 'laser1:amp:ontime').

    """

    def __init__(self, client: Client, name: str) -> None:
        self._client = client
        self._name = name

    @property
    def name(self) -> str:
        """str: The fully qualified name of the parameter."""
        return self._name

    async def get(self) -> float:
        """Returns the current value of the parameter.

        Returns:
            float: The current value of the parameter.

        """
        result = await self._client.get(self._name, float)
        assert isinstance(result, float)
        return result

    async def set(self, value: float) -> None:
        """Updates the value of the parameter.

        Args:
            value (float): The new value of the parameter.

        """
        assert isinstance(value, float), "expected type 'float' for 'value', got '{}'".format(type(value))
        await self._client.set(self._name, value)

    async def subscribe(self, callback: DecofCallback = None) -> 'Subscription':
        """Creates a subscription to updates of the parameter.

        Args:
            callback (DecofCallback): A callback that will be invoked when the value of the parameter has changed.

        Returns:
            Subscription: A subscription to updates of the parameter.

        """
        return await self._client.subscribe(self._name, float, callback)


class DecofString:
    """A read-only DeCoF string parameter.

    Attributes:
        client (Client): A DeCoF client that is used to access the parameter on a device
        name (str): The fully qualified name of the parameter (e.g. 'laser1:amp:ontime')

    """

    def __init__(self, client: Client, name: str) -> None:
        self._client = client
        self._name = name

    @property
    def name(self) -> str:
        """str: The fully qualified name of the parameter."""
        return self._name

    async def get(self) -> str:
        """Returns the current value of the parameter.

        Returns:
            str: The current value of the parameter.

        """
        result = await self._client.get(self._name, str)
        assert isinstance(result, str)
        return result

    async def subscribe(self, callback: DecofCallback = None) -> 'Subscription':
        """Creates a subscription to updates of the parameter.

        Args:
            callback (DecofCallback): A callback that will be invoked when the value of the parameter has changed.

        Returns:
            Subscription: A subscription to updates of the parameter.

        """
        return await self._client.subscribe(self._name, str, callback)


class MutableDecofString:
    """A read/write DeCoF string parameter.

    Attributes:
        client (Client): A DeCoF client that is used to access the parameter on a device
        name (str): The fully qualified name of the parameter (e.g. 'laser1:amp:ontime')

    """

    def __init__(self, client: Client, name: str) -> None:
        self._client = client
        self._name = name

    @property
    def name(self) -> str:
        """str: The fully qualified name of the parameter."""
        return self._name

    async def get(self) -> str:
        """Returns the current value of the parameter.

        Returns:
            str: The current value of the parameter.

        """
        result = await self._client.get(self._name, str)
        assert isinstance(result, str)
        return result

    async def set(self, value: str) -> None:
        """Updates the value of the parameter.

        Args:
            value (str): The new value of the parameter.

        """
        assert isinstance(value, str), "expected type 'str' for 'value', got '{}'".format(type(value))
        await self._client.set(self._name, value)

    async def subscribe(self, callback: DecofCallback = None) -> 'Subscription':
        """Creates a subscription to updates of the parameter.

        Args:
            callback (DecofCallback): A callback that will be invoked when the value of the parameter has changed.

        Returns:
            Subscription: A subscription to updates of the parameter.

        """
        return await self._client.subscribe(self._name, str, callback)


class DecofBinary:
    """A read-only DeCoF binary parameter.

    Attributes:
        client (Client): A DeCoF client that is used to access the parameter on a device
        name (str): The fully qualified name of the parameter (e.g. 'laser1:amp:ontime')

    """

    def __init__(self, client: Client, name: str) -> None:
        self._client = client
        self._name = name

    @property
    def name(self) -> str:
        """str: The fully qualified name of the parameter."""
        return self._name

    async def get(self) -> bytes:
        """Returns the current value of the parameter.

        Returns:
            bytes: The current value of the parameter.

        """
        result = await self._client.get(self._name, bytes)
        assert isinstance(result, bytes)
        return result

    async def subscribe(self, callback: DecofCallback = None) -> 'Subscription':
        """Creates a subscription to updates of the parameter.

        Args:
            callback (DecofCallback): A callback that will be invoked when the value of the parameter has changed.

        Returns:
            Subscription: A subscription to updates of the parameter.

        """
        return await self._client.subscribe(self._name, bytes, callback)


class MutableDecofBinary:
    """A read/write DeCoF binary parameter.

    Attributes:
        client (Client): A DeCoF client that is used to access the parameter on a device
        name (str): The fully qualified name of the parameter (e.g. 'laser1:amp:ontime')

    """

    def __init__(self, client: Client, name: str) -> None:
        self._client = client
        self._name = name

    @property
    def name(self) -> str:
        """str: The fully qualified name of the parameter."""
        return self._name

    async def get(self) -> bytes:
        """Returns the current value of the parameter.

        Returns:
            bytes: The current value of the parameter.

        """
        result = await self._client.get(self._name, bytes)
        assert isinstance(result, bytes)
        return result

    async def set(self, value: bytes) -> None:
        """Updates the value of the parameter.

        Args:
            value (bytes): The new value of the parameter.

        """
        assert isinstance(value, bytes), "expected type 'bytes' for 'value', got '{}'".format(type(value))
        await self._client.set(self._name, value)

    async def subscribe(self, callback: DecofCallback = None) -> 'Subscription':
        """Creates a subscription to updates of the parameter.

        Args:
            callback (DecofCallback): A callback that will be invoked when the value of the parameter has changed.

        Returns:
            Subscription: A subscription to updates of the parameter.

        """
        return await self._client.subscribe(self._name, bytes, callback)
