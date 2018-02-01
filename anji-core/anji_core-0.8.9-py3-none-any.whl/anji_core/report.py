import urllib.parse
from typing import List

import requests
from dateutil import parser
import trafaret as T
from sarge import Capture, run

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.8.9"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"


class ReportEntity(object):  # pylint: disable=too-few-public-methods,too-many-instance-attributes

    __slots__ = [
        'internal_url',
        'external_url',
        'report_date',
        'report_type',
        'file_url',
        'id',
        'report_group',
        'report_name'
    ]

    def __init__(self, internal_url, external_url, report_date, report_type,
                 file_url, id_, report_group, report_name):
        self.internal_url = internal_url
        self.external_url = external_url
        self.report_date = report_date
        self.report_type = report_type
        self.file_url = file_url
        self.id = id_
        self.report_group = report_group
        self.report_name = report_name

    def build_url(self, internal=False):
        return (self.internal_url if internal else self.external_url) + self.file_url

    def __str__(self):
        return "{} (сгенерирован {}): {}{}".format(
            self.report_name,
            self.report_date.strftime('%Y-%m-%d %H:%M'),
            self.external_url,
            self.file_url
        )


class ReportEngine(object):

    def __init__(self, bot, report_configuration) -> None:
        self.bot = bot
        self.internal_url: str = report_configuration['internal_url']
        self.external_url: str = report_configuration['external_url']

    @staticmethod
    def generate_trafater() -> T.Dict:
        return T.Dict({
            'internal_url': T.String(),
            'external_url': T.String()
        })

    def transform_url(self, report_url: str, to_internal: bool = False) -> str:
        if to_internal:
            return report_url.replace(self.external_url, self.internal_url)
        return report_url.replace(self.internal_url, self.external_url)

    def paste_html_from_file(self, html_file_path: str, report_group: str = 'Anji-tan', report_name: str = 'Anji-tan report') -> str:
        quoted_url = urllib.parse.quote('/paste/html/{}/{}'.format(report_group, report_name))
        curl_process = run(
            'curl {internal_url}{quoted_url} -X POST --data-binary @{file_path}'.format(
                internal_url=self.internal_url,
                quoted_url=quoted_url,
                file_path=html_file_path
            ),
            stdout=Capture()
        )
        exit_code = curl_process.returncode
        if not exit_code:
            return self.transform_url(curl_process.stdout.text)
        return ''

    def paste_html(self, raw_html: str, report_group: str = 'Anji-tan', report_name: str = 'Anji-tan report') -> str:
        result = requests.put(
            '{internal_url}/paste/html/{report_group}/{report_name}'
            .format(
                internal_url=self.internal_url,
                report_group=report_group,
                report_name=report_name
            ), data=raw_html.encode('utf-8')
        )
        external_report_url = self.transform_url(result.text)
        return external_report_url

    def paste_text(self, raw_text: str, report_group: str = 'Anji-tan', report_name: str = 'Anji-tan report') -> str:
        result = requests.put(
            '{internal_url}/paste/text/{report_group}/{report_name}'
            .format(
                internal_url=self.internal_url,
                report_group=report_group,
                report_name=report_name
            ), data=raw_text.encode('utf-8')
        )
        external_report_url = self.transform_url(result.text)
        return external_report_url

    def get_report_list(
            self, group: str = None, name: str = None, limit: int = 20,
            order_by: str = 'report_date', reverse: bool = False) -> List[ReportEntity]:
        base_url = '{}/api/reports'.format(self.internal_url)
        if group:
            base_url += '/' + group
            if name:
                base_url += '/' + name
        request_url = '{base_url}?limit={limit}&order_by={order_by}'.format(
            base_url=base_url,
            limit=limit,
            order_by=order_by
        )
        if reverse:
            request_url += '&reversed=True'
        reports = []
        for report_data in requests.get(request_url).json():
            reports.append(ReportEntity(
                self.internal_url,
                self.external_url,
                parser.parse(report_data['report_date']),
                report_data['report_type'],
                report_data['file_url'],
                report_data['id'],
                report_data['report_group'],
                report_data['report_name']
            ))
        return reports
