# Copyright 2017 Zdenek Kraus <zdenek.kraus@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re

REFORMAT_PATTERN = '(?:%{([a-zA-Z0-9_]+)(?:\|([^}|]*))?(?:\|([^}|]*))?})|([^%]+|%)'
"""Regular expression searches for reformat notation "%{NAME [| POSITIVE] [| NEGATIVE]}", and other strings"""
REFORMAT_REX = re.compile(REFORMAT_PATTERN)


def get_subs_list(pattern):
    items = REFORMAT_REX.findall(pattern)
    # (var_name, positive_pattern, negative_pattern, plain_string)
    return items


def reformat(pattern, data, default=''):
    items = get_subs_list(pattern)

    if data is None:
        return pattern

    if not isinstance(data, dict):
        raise TypeError('input data must be dict or None')

    out_list = []
    for item, pt, ptn, string in items:
        # plain string do not reformat
        if string:
            out_list.append(string)
        # pattern do reformat
        else:
            present = item in data
            # if selected item is present but None in value, behave like
            # item is not present
            i_data = data.get(item)
            if i_data is None:
                i_data = default
                present = False

            # convert data to format-able string
            i_data = str(i_data)
            if present:
                if pt:
                    try:
                        tmp = pt % (i_data,)  # format positive pattern
                    except TypeError:
                        tmp = pt  # pattern cannot be formatted, it will become output
                else:
                    tmp = i_data  # no included pattern available, just plain replace
            elif not present and ptn:
                try:
                    tmp = ptn % (i_data,)  # format negative pattern
                except TypeError:
                    tmp = ptn  # pattern cannot be formatted, it will become output
            else:
                tmp = ''
            out_list.append(tmp)
    result = "".join(out_list)
    return result
