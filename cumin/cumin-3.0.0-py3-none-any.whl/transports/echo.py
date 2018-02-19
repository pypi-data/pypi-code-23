"""Transport Echo: a dummy transport to just print the list of hosts in different ways."""
from ClusterShell.NodeSet import expand

from cumin.transports import BaseWorker, WorkerError


class EchoWorker(BaseWorker):
    """Worker interface to be extended by concrete workers."""

    allowed_commands = ('expand', 'group', 'shuffle', 'sort')

    def execute(self):
        """Execute the task as configured.

        :Parameters:
            according to parent :py:meth:`cumin.transports.BaseWorker.execute`.
        """
        if not self.commands:
            operations = ['group', 'sort']  # Set defaults
        else:
            operations = []

        for command in self.commands:
            if command not in self.allowed_commands:
                raise WorkerError('Command {command} is not allowed. Expected one of: {commands}'.format(
                    command=command, commands=','.join(self.allowed_commands)))

            operations.append(command)

        hosts = self.target.hosts
        for operation in operations:
            hosts = getattr(self, 'op_{operation}'.format(operation=operation))(hosts)

        for host in hosts:
            print(hosts)

        return 0

    def get_results(self):
        """Iterate over the results (`generator`). The EchoWorker doesn't have any results to iterate.

        :Parameters:
            according to parent :py:meth:`cumin.transports.BaseWorker.get_results`.
        """
        iter(())

    @property
    def handler(self):
        """Get and set the `handler` for the current execution. The EchoWorker does not accept any handler.

        :Parameters:
            according to parent :py:attr:`cumin.transports.BaseWorker.handler`.
        """
        # raise NotImplementedError('The EchoWorker does not accept any handler')

    @handler.setter
    def handler(self, value):
        """Setter for the `handler` property. The relative documentation is in the getter."""
        # raise NotImplementedError('The EchoWorker does not accept any handler')

    def op_expand(self, hosts):
        return expand(hosts)

    def op_group(self, hosts):
        return [hosts]

    def op_shuffle(self, hosts):
        return hosts

    def op_sort(self, hosts):
        return hosts


worker_class = EchoWorker  # pylint: disable=invalid-name
"""Required by the transport auto-loader in :py:meth:`cumin.transport.Transport.new`."""
