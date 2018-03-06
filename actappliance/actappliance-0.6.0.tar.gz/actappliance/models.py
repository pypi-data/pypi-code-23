import numbers
import logging
import shlex
import re
from typing import List
from actappliance.act_errors import act_errors, ACTError

"""
This module contains the primary objects that power actappliance.
"""

logger = logging.getLogger('models')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


class ActResponse(dict):
    """Dictionary class that helps parsing and raising errors on public Actifio API responses."""

    def __init__(self, *args, actifio_command=None, **kwargs):
        """

        :param args: dictionary args
        :param actifio_command: Deprecated
        :param kwargs: dictionary kwargs
        """
        self.command = actifio_command
        super(ActResponse, self).__init__(*args, **kwargs)
        self.errorcode = None
        self.errormessage = None

    def raise_for_error(self):
        """Raise ACTError if one occurred"""
        try:
            self.errorcode = self['errorcode']
        except KeyError:
            logger.debug('No errorcode found in ActResponse.')

        try:
            self.errormessage = self['errormessage']
        except KeyError:
            # Handle UI responses
            try:
                self.errormessage = self['msg']
            except KeyError:
                logger.debug('No errormessage found in ActResponse.')

        if self.errorcode or self.errormessage:
            if self.errorcode in act_errors:
                raise act_errors[self.errorcode](self)
            else:
                raise ACTError(self)

    def parse(self, k=None, m_k=None, m_v=None, index=0, warnings=True):
        """
        Takes appliance api response and returns a desired value or dictionary.

        It will first search outside the result for the key. Then it will search inside the result.
        If only a key is given it will return the value of that key from the desired index (default 0).
        If given a match_key and match_value it will search for the first matching dictionary inside the result list
        and return the key from that dictionary.

        Index is ignored without warning if match_key and match_value are provided.

        It is outside the scope of this method to return multiple dictionaries. Parsing multiple outputs shouldn't use
        this method.

        :param self: python object response from appliance api (most commonly json decoded from method cmd)
        :param k: the key; corresponding value will be returned
        :param m_k: match key to find the indexes
        :param m_v: match value to find the indexes
        :param index: index of the list of dictionaries to return
        :param warnings: boolean of whether to raise warning or not
        :return: string if key provided; dictionary if key is not provided
        """
        # Is the result empty?
        try:
            if not self['result']:
                value = self._get_external_value(k)
                if value:
                    logger.info("External value {} found, but will not return from parse.".format(value))
                if warnings:
                    logger.warning('No result found. Returning nothing from parse.')
                return

        # safety net against strange responses
        except (IndexError, TypeError):
            logger.exception('Are you sure you wanted to parse this? You gave no key and there is no result.')
            raise
        except KeyError:
            logger.info('No result dictionary found.')
            return

        # Is the result just an id or response?
        if isinstance(self['result'], (str, numbers.Integral)):
            logger.debug('result looks like an id or name; returning immediately')
            return self['result']

        # Is the result just info on a single object?
        if isinstance(self['result'], dict):
            if k is None:
                return self['result']
            else:
                return self['result'][k]

        # Is the result several objects?
        if isinstance(self['result'], list):
            # get matching indexes
            if m_k is not None and m_v is not None:
                indexes = []
                for i, dictionary in enumerate(self['result']):
                    if dictionary.get(m_k) == m_v:
                        indexes.append(i)
                if not indexes:
                    logger.info('Nothing found matching {} and {}'.format(m_k, m_v))
                    return
                index = indexes[0]
            if k is None:
                # return dictionary
                return self['result'][index]
            else:
                # Return value
                try:
                    return self.get('result')[index][k]
                except IndexError:
                    logger.error("Index {} doesn't exist. If you manually entered an index, try using matching key "
                                 "and value instead.".format(index))
                    raise
                except KeyError:
                    return self._get_external_value(k)

    def _get_external_value(self, k):
        # Is the response outside of result?
        if k is not None:
            if k in self:
                value = self[k]
                if k in ['status', 'result']:
                    logger.info('There is a top level matching key {}. Using this variable is not a supported use of '
                                'parse.'.format(k))
                    logger.debug('Top level key {} is: {}.'.format(k, value))
                    return
                logger.debug("The top level value for {} is: {}".format(k, value))
                return value
        return


class Act_put:
    """Base class for Act*put i.e. ActInput, ActOutput"""
    _ssh_delim = '|MiLeD|'


class ActInput(Act_put):
    """
    Ephemeral ActInputs handler

    It is important that if there is an 'argument' in the operation that it is the first input.

    Without having outside information on every command it would be impossible for us to know when a switch has no input
    and when it is followed by an argument.

    Example:
      udsfakecommand -some_arg some_value
    In the above is some_arg a 'switch' which means that it is flagging on and some_value is the argument? Or is
    some_arg a key which some_value is the input for? We cannot figure out what parameters are switches and which expect
    a value. However, we can still parse all possible inputs as long as the argument is first.
    """
    parse_op_props = ['http_method', 'base_path', 'action', 'operation_params', 'action']

    def __init__(self, operation, *, conn_object=None, update_cmds: dict=None):
        """

        :param operation: The full operation to be converted, with any argument as the first input
                             example: "udsinfo lshost 1234 -filtervalue some=thing&also=this"
        :param conn_object: The connection object which you will make the call with
        :param update_cmds: Input or update key/value information sent with the command, this always has priority
        """
        self.operation = operation
        self.update_cmds = {} if update_cmds is None else update_cmds
        self.conn_object = conn_object

        for pub_prop in ActInput.parse_op_props:
            setattr(self, '_' + pub_prop, None)
        self._act_method = None

    def parse_operation(self):
        op_part = self.operation.partition(' ')
        self.act_method = op_part[0]
        body = self.operation.partition(' ')[2]
        shlexd_body = shlex.split(body)
        self.action = self._get_action(shlexd_body)
        self.operation_params = self._get_operation_params(shlexd_body)

    @property
    def updated_cmd_inputs(self):
        updated = self.operation_params
        try:
            updated['sessionid'] = self.conn_object.sid
        except AttributeError:
            logger.debug("Connection object doesn't have a sid.")
        return {**self.operation_params, **self.update_cmds}

    @property
    def ssh_command(self):
        """This is the arg for a paramiko exec_command call"""
        ssh_command = self.format_ssh_command()
        logger.debug(f"SSH command: '{ssh_command}'")
        return ssh_command

    @property
    def ssh_kwargs(self):
        """These are the inputs for a paramiko exec_command call"""
        return {'command': self.ssh_command}

    @property
    def rest_kwargs(self):
        """These are the inputs for a Session.request call"""
        request_kwargs = {
            'method': self.http_method,
            'url': self.url,
            'params': self.updated_cmd_inputs
        }
        logger.debug(f"Request inputs: '{request_kwargs}'")
        return request_kwargs

    @property
    def system(self):
        try:
            return self.conn_object.system
        except AttributeError:
            logger.exception("Need a connection object with system to generate input!")
            raise

    @property
    def url(self):
        return "https://" + self.system + "/actifio/api/" + self.base_path + "/" + self.action

    @property
    def cli_method(self):
        return '/act/bin/' + self.act_method

    @staticmethod
    def _kwargs_to_cli(kwargs):
        cli_args = ''
        # add parameters to body
        for k, v in kwargs.items():
            # don't pass None connect_kwargs
            if v is not None:
                # handle special case argument
                if k.lower() == 'argument':
                    cli_args += ' {}'.format(v)
                    continue
                parameter = "-{}".format(k)
                # handle parameterless switches
                if v is True:
                    value = ''
                else:
                    value = shlex.quote(v)
                option = " ".join([parameter, value])
                cli_args += f' {option}'
        return cli_args

    def format_ssh_command(self):
        """
        Takes a functional cli operation and appends rest like inputs.

        ex.
          self.cmd('udsinfo lshost', filtervalue='ostype=Linux')
        returns:
          "/act/bin/udsinfo lshost -filtervalue 'ostype=Linux'"
        """
        cli_args = self._kwargs_to_cli(self.updated_cmd_inputs)

        if self.act_method == 'udsinfo' and self.action.startswith(('ls', 'list')):
            cli_args += " -delim '{}'".format(self._ssh_delim)
        full_operation = " ".join((self.cli_method, self.action, cli_args))
        return full_operation

    @staticmethod
    def _parm_list_to_dict(params_list: List):
        # create param dictionary
        params_dict = {}
        k = None
        v = None

        def multi_arg_catch(arg_value, args=[]):
            if not args:
                args.append(arg_value)
                return arg_value
            logger.debug(f"Multiple argument values '{args + [arg_value]}' found in operation.")
            raise ValueError("Multiple arguments in operation.")

        for i in reversed(params_list):
            if i.startswith('-'):
                k = i[1:]
            else:
                if v is None:
                    v = i
                else:
                    # handle sequential values
                    params_dict['argument'] = multi_arg_catch(v)
                    v = i
            if k:
                if v:
                    params_dict[k] = v
                    k = None
                    v = None
                else:
                    params_dict[k] = 'true'
                    k = None
        # grab the argument if it's the first parameter
        if v is not None:
            params_dict['argument'] = multi_arg_catch(v)
        return params_dict

    @staticmethod
    def _get_action(shlexd_body):
        try:
            action = shlexd_body[0]
        except IndexError:
            logger.exception('Operation provided to convert to cli has no action. ex. "mkhost".')
            raise
        return action

    @staticmethod
    def _get_operation_params(shlexd_body):
        operation_params_list = shlexd_body[1:]
        params = ActInput._parm_list_to_dict(operation_params_list)
        return params

    @property
    def act_method(self):
        if not self._act_method:
            self.parse_operation()
        return self._act_method

    @act_method.setter
    def act_method(self, act_method):
        if act_method == "udsinfo":
            self.http_method = "get"
            self.base_path = "info"
        elif act_method == "udstask":
            self.http_method = "post"
            self.base_path = "task"
        elif act_method == "sainfo":
            self.http_method = "get"
            self.base_path = "shinfo"
        else:
            raise ValueError("Actifio CLI API doesn't support method '{}'".format(act_method))

        self._act_method = act_method

    # Parse operation properties
    # Avoid writing the below a bunch of times:
    # @property
    # def http_method(self):
    #     if not self._http_method:
    #         self.parse_operation()
    #     return self._http_method
    #
    # @http_method.setter
    # def http_method(self, value):
    #     self._http_method = value

    @staticmethod
    def _make_parse_op_prop(prop_name):
        private_var_name = '_' + prop_name

        def fget(self):
            if not getattr(self, private_var_name):
                self.parse_operation()
            return getattr(self, private_var_name)

        def fset(self, value):
            setattr(self, private_var_name, value)

        return property(fget, fset)

    for parse_op_prop in parse_op_props:
        # This relies on cpython's implementation aka PEP558 https://www.python.org/dev/peps/pep-0558/#class-scope
        locals()[parse_op_prop] = _make_parse_op_prop.__func__(parse_op_prop)


class ActOutput(Act_put):
    def __init__(self):
        self._result = {}
        self._stdout = self._stderr = self._sshout = None

    @property
    def result(self):
        """
        The result in a dictionary how a RESTful request would respond.

        We remove 'result' to fix the case where stdout was loaded before stderr and we didn't know at parse time if the
        response was empty or an error.

        Without this handling we would receive:
        `{'errorcode': 010010, 'errormessage': 'invalid option: k', 'result': []}`
        Instead of the correct response:
        `{'errormessage': 'invalid option: k', 'errorcode': 10010}`
        """
        if {'result', 'errorcode', 'errormessage'} <= self._result.keys():
            empty_result = self._result.pop('result')
            logger.debug(f"Removed empty result from ActOutput with error. {empty_result}")
        return self._result

    @result.setter
    def result(self, value):
        # TODO: Make result setter smarter; allow a switch based on conn_object to fill in result or stdout and stderr
        self._result = value

    @property
    def response(self):
        ar = ActResponse(self.result)
        logger.debug(f"Actifio response:\n{ar}")
        return ar

    @property
    def sshout(self):
        return self._sshout

    @sshout.setter
    def sshout(self, ssh_out):
        self.stderr = ssh_out.err
        self.stdout = ssh_out.out

    @property
    def stdout(self):
        return self._stdout

    @stdout.setter
    def stdout(self, stdout):
        self._stdout = stdout
        if not self.stderr:
            self.result.update(self._parse_ssh_stdout(stdout))

    @property
    def stderr(self):
        return self._stderr

    @stderr.setter
    def stderr(self, stderr):
        self._stderr = stderr
        self.result.update(self._parse_ssh_stderr(stderr))

    @staticmethod
    def _parse_ssh_stderr(stderr):
        error_dict = {}
        if stderr:
            error_code = re.match("(?:ACTERR-)(\d+)", stderr[0]).group(1)
            error_message = re.match("(?:ACTERR-\d+ )(.+)", stderr[0]).group(1)
            error_dict['errorcode'] = int(error_code)
            error_dict['errormessage'] = error_message

        return error_dict

    def _parse_ssh_stdout(self, stdout):
        result_dict = {}
        try:
            # Handle udsinfo commands that start with ls
            if self._ssh_delim in stdout[0]:
                logger.info('Ssh operation contains delim, grabbing header.')
                headers = stdout[0].split(self._ssh_delim)
                values = [row.split(self._ssh_delim) for row in stdout[1:]]
                # Make the result list like JSON response
                result_list = []
                for row in values:
                    result_list.append(dict(zip(headers, row)))
                    result_dict['result'] = result_list
            else:
                # Handle all other udsinfo commands
                # only return a list if there is more than one item, else return a string (see exception)
                if stdout[1]:
                    result_dict = {'result': stdout}
                # TODO Do we need ssh_deliming on any results that match "udsinfo -h | egrep -v '^\s*ls|*list'"
        except IndexError:
            try:
                # return single item response as a string
                result_dict['result'] = stdout[0]
            except IndexError:
                # return "[]" if stdout was empty, matching standard rest response
                result_dict['result'] = stdout

        return result_dict

    def convert_ssh_output(self, stdout, stderr):
        logger.debug('Parsing stdout: {}'.format(stdout))
        rest_like_result = {}
        # first add error info if present
        rest_like_result.update(self._parse_ssh_stderr(stderr))
        # Now format stdout
        rest_like_result.update(self._parse_ssh_stdout(stdout))
        logger.debug("Converted cli result: {}".format(rest_like_result))
        return rest_like_result


class ActCmd:
    """Abstract single CLI API command"""
    def __init__(self, conn_object=None):
        self.input = None
        self.output = ActOutput()
        self.conn_object = conn_object
        logger.debug("Actifio command started with {a} {conn} connection".format(
            a='an' if self.conn_type == 'ssh' else 'a', conn=self.conn_type)
        )

    def cmd_input(self, operation, **update_cmds):
        self.input = ActInput(operation, conn_object=self.conn_object, update_cmds=update_cmds)

    @property
    def call_kwargs(self):
        return getattr(self.input, self.conn_type + '_kwargs')

    @property
    def conn_type(self):
        from actappliance.connections import ApplianceRest, ApplianceSsh
        if isinstance(self.conn_object, ApplianceSsh):
            return 'ssh'
        elif isinstance(self.conn_object, ApplianceRest):
            return 'rest'

    @property
    def response(self):
        act_response = self.output.response
        act_response.inputs = self.input
        return act_response
