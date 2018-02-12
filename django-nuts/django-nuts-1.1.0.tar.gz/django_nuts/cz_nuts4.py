import logging
import os

from .loaders import get_remote_data
from .models import LAU, NUTS

logger = logging.getLogger(__name__)

CZ_NUTS4_URL = os.environ.get(
    'CZ_NUTS4_URL',
    'https://www.czso.cz/documents/10180/23208674/struktura_uzemi_cr_1_1_2016_az_1_1_2018.xlsx',
)


def load_cz_nuts4():
    data = get_remote_data(CZ_NUTS4_URL)

    # take last sheet
    sheet = data[list(data.keys())[-1]]

    nuts = {n.code: n for n in NUTS.objects.filter(code__startswith='CZ').iterator()}
    laus = {l.code: l for l in LAU.objects.filter(code__startswith='CZ').iterator()}
    nuts_created, nuts_updated, lau_created, lau_updated = 0, 0, 0, 0
    for row in sheet[2:]:
        lau_code, lau_name = row[0:2]
        nuts4_code, nuts4_name = row[7:9]
        lau_code = 'CZ%s' % lau_code
        if nuts4_code not in nuts:
            nuts[nuts4_code] = NUTS.objects.create(
                code=nuts4_code,
                name=nuts4_name,
                level=4,
            )
            nuts_created += 1
        elif nuts[nuts4_code].name != nuts4_name:
            nuts[nuts4_code].name = nuts4_name
            nuts[nuts4_code].save()
            nuts_updated += 1
        if lau_code not in laus:
            laus[lau_code] = LAU.objects.create(
                code=lau_code,
                name=lau_name,
                local_name=lau_name,
                nuts=nuts[nuts4_code],
            )
            lau_created += 1
        else:
            lau = laus[lau_code]
            if lau.name != lau_name or lau.local_name != lau_name or lau.nuts_id != nuts4_code:
                lau.name = lau_name
                lau.local_name = lau_name
                lau.nuts = nuts[nuts4_code]
                lau.save()
                lau_updated += 1
    logger.info(
        '%d NUTS created, %d updated, %d LAU created, %d updated',
        nuts_created, nuts_updated, lau_created, lau_updated,
    )
