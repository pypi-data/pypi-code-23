import logging
import os
from csv import DictReader
from io import StringIO

from .models import LAU, NUTS

try:
    # python3
    from urllib.request import urlopen
except ImportError:
    # python2
    from urllib import urlopen


logger = logging.getLogger(__name__)

NUTS_URL = os.environ.get(
    'NUTS_URL',
    'http://ec.europa.eu/eurostat/ramon/nomenclatures/index.cfm'
    '?TargetUrl=ACT_OTH_CLS_DLD&StrNom=NUTS_2016L&StrFormat=CSV&StrLanguageCode=EN&IntKey=&IntLevel=&bExport='
)

LAU_URL = os.environ.get(
    'LAU_URL',
    'http://ec.europa.eu/eurostat/documents/345175/501971/EU-28_LAU_2017_NUTS_2016.xlsx',
)


def load_nuts(base_code=None):
    with urlopen(NUTS_URL) as response:
        content = response.read().replace(b'\r', b'\n').decode('utf-8')
    nuts = {n.code: n for n in NUTS.objects.iterator()}
    created, updated = 0, 0
    for record in sorted(DictReader(StringIO(content), delimiter=';'), key=lambda r: r['NUTS-Code']):
        code = record['NUTS-Code']
        level = len(code) - 2
        name = record['Description']

        # skip records not matching base_code and records containing NUTS in the name
        if base_code and not code.startswith(base_code) or 'NUTS' in name:
            continue

        if code in nuts:
            if nuts[code].name != name:
                nuts[code].name = name
                nuts[code].save()
                updated += 1
        else:
            nuts[code] = NUTS.objects.create(code=code, name=name, level=level)
            created += 1
    logger.info('Created %d NUTS, updated %d', created, updated)


def load_lau(base_code=None):
    data = get_remote_data(LAU_URL)
    nuts = {n.code: n for n in NUTS.objects.iterator()}
    created, updated = 0, 0
    for code, sheet in data.items():

        # skip sheets not matching base_code and metadata sheets
        if base_code and code != base_code[:2] or len(code) != 2:
            continue

        laus = {l.code: l for l in LAU.objects.filter(nuts__code__startswith=code).select_related('nuts').iterator()}
        for row in sheet[1:]:
            nuts_code, code, local_name, name = row[:4]
            code = int(code)
            if code in laus:
                lau = laus[code]
                if not lau.nuts_id.startswith(nuts_code) or lau.name != name or lau.local_name != local_name:
                    if not lau.nuts_id.startswith(nuts_code):
                        lau.nuts2 = nuts[nuts_code]
                    lau.name = name
                    lau.local_name = local_name
                    lau.save()
                    updated += 1
            else:
                laus[code] = LAU.objects.create(nuts=nuts[nuts_code], code=code, name=name, local_name=local_name)
                created += 1
    logger.info('Created %d LAU, updated %d', created, updated)


def get_remote_data(url, suffix='.xlsx'):
    from pyexcel_xls import get_data
    from tempfile import NamedTemporaryFile

    with NamedTemporaryFile(suffix=suffix) as f:
        with urlopen(url) as response:
            f.write(response.read())
            f.flush()
        return get_data(f.name)
