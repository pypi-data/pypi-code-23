import logging
import os
from csv import DictReader
from io import StringIO

from ..models import LAU, NUTS

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

NUTS_OTHER_URL = os.environ.get(
    'NUTS_OTHER_URL',
    'http://ec.europa.eu/eurostat/documents/345175/7773495/Statistical-Regions.xlsx',
)

LAU_URL = os.environ.get(
    'LAU_URL',
    'http://ec.europa.eu/eurostat/documents/345175/501971/EU-28_LAU_2017_NUTS_2016.xlsx',
)


def load_nuts(*country_codes):
    with urlopen(NUTS_URL) as response:
        content = response.read().replace(b'\r', b'\n').decode('utf-8')
    nuts = {n.code: n for n in NUTS.objects.iterator()}
    created, updated = 0, 0
    for record in sorted(DictReader(StringIO(content), delimiter=';'), key=lambda r: r['NUTS-Code']):
        code = record['NUTS-Code']
        level = len(code) - 2
        name = record['Description']

        # skip records not matching country_codes and records containing NUTS in the name
        if country_codes and code[:2] not in country_codes or 'NUTS' in name:
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


def load_other_nuts(*country_codes):
    data = get_remote_data(NUTS_OTHER_URL)

    nuts = dict()
    created, updated = 0, 0
    for row in data['SR'][1:]:
        try:
            code, name = row[1:3]
        except ValueError:
            continue

        country_code = code[:2]

        # skip records not matching country_codes
        if country_codes and country_code not in country_codes:
            continue

        # get existing NUTS
        if country_code not in nuts:
            nuts[country_code] = {n.code: n for n in NUTS.objects.filter(code__startswith=country_code).iterator()}

        if code in nuts[country_code]:
            if nuts[country_code][code].name != name:
                nuts[country_code][code].name = name
                nuts[country_code][code].save()
                updated += 1
        else:
            nuts[country_code][code] = NUTS.objects.create(code=code, name=name, level=len(code) - 2)
            created += 1
    logger.info('Created %d NUTS, updated %d', created, updated)


def load_lau(*country_codes):
    data = get_remote_data(LAU_URL)
    if not country_codes:
        country_codes = (key for key in data.keys() if len(key) == 2)
    for country_code in country_codes:
        sheet = data[country_code]
        nuts = {n.code: n for n in NUTS.objects.filter(code__startswith=country_code).iterator()}
        laus = {l.code: l for l in LAU.objects.filter(code__startswith=country_code).iterator()}
        created, updated = 0, 0
        for row in sheet[1:]:
            # handle exceptions in data
            try:
                nuts_code, lau_code, local_name, name = row[:4]
                if not local_name:
                    local_name = name
                if not name:
                    name = local_name
            except ValueError:
                nuts_code, lau_code, local_name = row[:3]
                name = local_name
            if not all((nuts_code, lau_code, local_name, name)) or len(row[:4]) < 3:
                logger.warning('Incomplete row in %s: %s', country_code, row[:4])
                continue
            if nuts_code[-3:] == 'ZZZ':
                continue
            if nuts_code not in nuts:
                logger.warning('Unknown NUTS-3 code: %s', nuts_code)
                continue
            # store data
            code = '%s%s' % (country_code, lau_code)
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
                laus[code] = LAU.objects.create(
                    code=code,
                    name=name,
                    local_name=local_name,
                    nuts=nuts[nuts_code],
                )
                created += 1
        logger.info('Created %d LAU, updated %d in %s', created, updated, country_code)


def get_remote_data(url, suffix='.xlsx'):
    from pyexcel_xls import get_data
    from tempfile import NamedTemporaryFile

    with NamedTemporaryFile(suffix=suffix) as f:
        with urlopen(url) as response:
            f.write(response.read())
            f.flush()
        return get_data(f.name)
