import abc

from anji_orm import StringField, DictField
from sarge import run, Capture

from .regular import RegularTask
from ..types import MessageType

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.8.11"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"


class AbstractCartridgeBashScriptTask(RegularTask):

    service_technical_name = StringField(description='Service technical name', definer=True)
    cartridge_config = DictField(description='Configuration from service', displayed=False, definer=True)

    _path_field = 'path'

    @abc.abstractmethod
    def build_execution_command(self):
        pass

    @abc.abstractmethod
    def generate_short_name(self):
        pass

    def task_execute(self):
        process = run(
            f'{self.build_execution_command()} | ansi2html',
            stdout=Capture(),
            cwd=self.cartridge_config[self._path_field]
        )
        raw_html = process.stdout.text
        exit_code = process.returncode
        short_name = self.generate_short_name()
        text_result = 'failed' if exit_code else 'finished successfully'
        report_name = f'{short_name} execution on service {self.service_technical_name} report'
        report_url = self.shared.report.paste_html(raw_html)
        return dict(
            body=f'{short_name} was {text_result}',
            message_type=MessageType.error if exit_code else MessageType.info,
            reports=[(report_name, report_url)]
        )
