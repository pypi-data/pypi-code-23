# -*- coding: utf-8 -*-
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.


# fix mt940/processors/transaction_details_post_processor
import logging
from mt940 import __about__ as mt940_about
from mt940.processors import _parse_mt940_details, _parse_mt940_gvcodes, GVC_KEYS
from mt940.models import Transactions
logger = logging.getLogger(__name__)

def transaction_details_post_processor_fix(transactions, tag, tag_dict, result):
    if not 'transaction_details' in tag_dict.keys():
        # job was done by original 'transaction_details_post_processor()'
        return result

    details = tag_dict['transaction_details']
    details = ''.join(detail.strip('\n\r') for detail in details.splitlines())

    gvc = details[:3]
    # fix: some banks dont send code '?00' (posting text)
    # we also accept code '?20' (purpose line 0)
    if gvc.isdigit() and details[3:6] in ['?00','?20']:
        result.update(_parse_mt940_details(details))

        purpose = result.get('purpose')

        if purpose and purpose[:4] in GVC_KEYS:  # pragma: no branch
            result.update(_parse_mt940_gvcodes(result['purpose']))

        del result['transaction_details']

    return result

# end transaction_details_post_processor_fix


def __init__mt940(self, processors=None):
    self.processors = self.DEFAULT_PROCESSORS.copy()
    if processors:
        self.processors.update(processors)
    self.transactions = []
    self.data = {}
    self.processors['post_transaction_details'].append(transaction_details_post_processor_fix)
# end __init__mt940

if mt940_about.__version__ in ['4.9.0', '4.10.0']:
    logger.warning("fixing Transactions.__init__()...")
    # replace with fixed function
    Transactions.__init__ = __init__mt940
    logger.warning("fixing successful")
else :
    logger.warning("not fixed! mt940-version '%s' not in [4.9.0, 4.10.0]" % mt940_about.__version__)
    
