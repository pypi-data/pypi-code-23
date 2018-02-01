from typing import List

from anji_orm import StringField
from sarge import Capture, run

from .core import AbstractService
from ..types import ServicesStatus

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.8.9"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"


def parse_systemctl_show(lines):
    """
    The output of 'systemctl show' can contain values that span multiple lines. At first glance it
    appears that such values are always surrounded by {}, so the previous version of this code
    assumed that any value starting with { was a multi-line value; it would then consume lines
    until it saw a line that ended with }. However, it is possible to have a single-line value
    that starts with { but does not end with } (this could happen in the value for Description=,
    for example), and the previous version of this code would then consume all remaining lines as
    part of that value. Cryptically, this would lead to Ansible reporting that the service file
    couldn't be found.

    To avoid this issue, the following code only accepts multi-line values for keys whose names
    start with Exec (e.g., ExecStart=), since these are the only keys whose values are known to
    span multiple lines.
    This part of code was taken here: https://github.com/ansible/ansible/blob/devel/lib/ansible/modules/system/systemd.py
    """
    parsed = {}
    multival = []
    k = None
    for line in lines:
        if k is None:
            if '=' in line:
                k, v = line.split('=', 1)
                if k.startswith('Exec') and v.lstrip().startswith('{'):
                    if not v.rstrip().endswith('}'):
                        multival.append(v)
                        continue
                parsed[k] = v.strip()
                k = None
        else:
            multival.append(line)
            if line.rstrip().endswith('}'):
                parsed[k] = '\n'.join(multival).strip()
                multival = []
                k = None
    return parsed


class SystemDService(AbstractService):

    model_subtype = 'systemd'

    unit_name = StringField(description='SystemD unit name', reconfigurable=True)
    active_state = StringField(service=True, default=ServicesStatus.unknown)
    load_state = StringField(service=True)

    def load_unit_data(self):
        systemctl_show_process = run(
            'systemctl show {} --no-pager'.format(self.unit_name),
            stdout=Capture()
        )
        result = parse_systemctl_show(systemctl_show_process.stdout.text.split('\n'))
        self.load_state = result['LoadState']
        self.active_state = result['ActiveState']

    def fetch_unix_processes_pid(self) -> List[int]:
        raise NotImplementedError("Currently not implemented")

    def service_registration(self) -> None:
        raise NotImplementedError("Currently not implemented")

    def is_running(self) -> bool:
        raise NotImplementedError("Currently not implemented")

    def is_exists(self) -> bool:
        raise NotImplementedError("Currently not implemented")

    def start_signal(self):
        run(f'systemctl start {self.unit_name}')

    def stop_signal(self):
        run(f'systemctl stop {self.unit_name}')

    def restart_signal(self):
        run(f'systemctl restart {self.unit_name}')

    def get_status(self):
        self.load_unit_data()
        if self.load_state == 'not-found':
            return ServicesStatus.absent
        elif self.active_state == 'inactive':
            return ServicesStatus.stopped
        if self.active_state == 'active':
            return ServicesStatus.running
        return ServicesStatus.unknown
