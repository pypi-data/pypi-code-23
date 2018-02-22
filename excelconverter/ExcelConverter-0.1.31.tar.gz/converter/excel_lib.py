"""
Python equivalents of various excel functions
"""

import math
import re
import numpy as np
from datetime import datetime
from math import log
from decimal import Decimal, ROUND_HALF_UP
from converter.excel_util import flatten, is_number, is_collection, date_from_int, normalize_year, is_leap_year, \
    find_corresponding_index, is_nr, ERR_NA, ERR_DIV, ERR_VALUE, ERROR_VALUES, rankdata, split_range, split_address, \
    col2num, num2col, evaluate_spreadsheet, to_values, is_valid, iterate_cells, get_range, safe_str as util_safe_str, \
    correct_numbers

# #####################################################################################
# A dictionary that maps excel function names onto python equivalents. You should
# only add an entry to this map if the python name is different to the excel name
# (which it may need to be to prevent conflicts with existing python functions
# with that name, e.g., max).

# So if excel defines a function foobar(), all you have to do is add a function
# called foobar to this module.  You only need to add it to the function map,
# if you want to use a different name in the python code. 

# Note: some functions (if, pi, atan2, and, or, array, ...) are already taken care of
# in the FunctionNode code, so adding them here will have no effect.
# Only add functions that have a different name in this file then the one in excel.
FUNCTION_MAP = {
    "ln": "xlog",
    "min": "xmin",
    "max": "xmax",
    "sum": "xsum",
    "gammaln": "lgamma",
    "round": "xround",
    "rank.eq": "rank_eq",
}

######################################################################################
# List of excel equivalent functions
# TODO: needs unit testing
######################################################################################
def greater_then(val1, val2, equals):
    # Excel seems to treat "None" value's like if they are '0'
    if val1 is None or isinstance(val1, str) and len(val1) == 0:
        val1 = 0
    if val2 is None or isinstance(val2, str) and len(val2) == 0:
        val2 = 0

    if val1 in ERROR_VALUES:
        return val1
    if val2 in ERROR_VALUES:
        return val2

    if isinstance(val1, str) or isinstance(val2, str):
        val1 = str(val1)
        val2 = str(val2)

    return val1 >= val2 if equals else val1 > val2

def less_then(val1, val2, equals):
    # Excel seems to treat "None" value's like if they are '0'
    if val1 is None or isinstance(val1, str) and len(val1) == 0:
        val1 = 0
    if val2 is None or isinstance(val2, str) and len(val2) == 0:
        val2 = 0

    if val1 in ERROR_VALUES:
        return val1
    if val2 in ERROR_VALUES:
        return val2

    if isinstance(val1, str) or isinstance(val2, str):
        val1 = str(val1)
        val2 = str(val2)

    return val1 <= val2 if equals else val1 < val2

def minus(val1, val2):
    if val1 in ERROR_VALUES:
        return val1
    if val2 in ERROR_VALUES:
        return val2
    val1, val2 = correct_numbers(val1, val2)

    return val1 - val2 if val1 is not None and val2 is not None else val1 if val1 is not None else val2

def plus(val1, val2):
    if val1 in ERROR_VALUES:
        return val1
    if val2 in ERROR_VALUES:
        return val2
    val1, val2 = correct_numbers(val1, val2)

    return val1 + val2 if val1 is not None and val2 is not None else val1 if val1 is not None else val2

def multiply(val1, val2):
    if val1 in ERROR_VALUES:
        return val1
    if val2 in ERROR_VALUES:
        return val2
    val1, val2 = correct_numbers(val1, val2)
    if val1 is None or val2 is None:
        return ERR_VALUE
    return val1 * val2 if val1 is not None and val2 is not None else 0

def divide(val1, val2):
    if val1 in ERROR_VALUES:
        return val1
    if val2 in ERROR_VALUES:
        return val2
    val1, val2 = correct_numbers(val1, val2)
    return val1 / val2 if val1 is not None and val2 is not None else 0 if val1 is None else ERR_DIV

def safe_str(value):
    return util_safe_str(value)

def sin(val1, args):
    if not is_nr(val1) or val1 == 0:
        raise Exception("The value must be a Number [%s]" % val1)
    else:
        return math.sin(val1)

def row(address):
    col, row = [_f for _f in re.split('([A-Z $]+)', address) if _f]
    return int(row)

def sumproduct(spreadsheet, main_address, *args):
    result = 0
    if len(args) > 1:
        # Not sure exactly how it works with more then 1 array in args (2 or more in total)
        raise Exception("Currently we don't support more then 2 arrays in total. Address: [%s]" % main_address)

    rng = get_range(spreadsheet, main_address)
    sheet, start, end = split_range(rng)
    sh, start_col, start_row = split_address(start)
    start_col_nr = col2num(start_col)

    def process(col_nr, row_nr, value):
        if value is not None:
            nonlocal result
            if len(args):
                for ar in args:
                    sheet, start, end = split_range(ar)
                    sh, start_cl, start_rw = split_address(start)
                    try:
                        val = evaluate_spreadsheet(spreadsheet, sheet,
                                                   num2col(col2num(start_cl) + col_nr - start_col_nr),
                                                   int(start_rw) + row_nr - int(start_row))
                        if val is not None:
                            result += value * val
                    except:
                        result = ERR_VALUE
                        return False
            else:
                if value is not None:
                    result += value
        return True

    iterate_cells(spreadsheet, rng, process)
    return result

def substitute(spreadsheet, source, old, new, nth=None):
    if nth == 0:
        return ERR_VALUE

    if nth is not None:  # not allowed to b
        find = source.find(old)
        # if find is not p1 we have found at least one match for the substring
        i = find != -1
        # loop util we find the nth or we find no match
        while find != -1 and i != nth:
            # find + 1 means we start at the last match start index + 1
            find = source.find(old, find + 1)
            i += 1
        # if i is equal to nth we found nth matches so replace
        if i == nth:
            return source[:find] + new + source[find + len(old):]
        return source
    else:
        return source.replace(old, new)

def xlog(a):
    if isinstance(a, (list, tuple, np.ndarray)):
        return [log(x) for x in flatten(a)]
    else:
        return log(a)

def xmax(spreadsheet, *args):
    result = None
    if is_collection(args) is not None:
        items = [x for x in args if is_nr(x)]
        if len(items):  # it concerns a collection of numbers
            return max(items)

        else:  # it concerns a nested range, collection,...
            for arg in args:
                sub = xmax_single(spreadsheet, arg)
                if is_nr(sub):
                    result = min(result, sub) if is_nr(result) else sub
    else:
        result = xmax_single(spreadsheet, args)
    return result if result is not None else ERR_NA

def xmax_single(spreadsheet, arg):
    result = None
    if is_nr(arg):
        result = max(result, arg) if is_nr(result) else arg
    elif isinstance(arg, str):
        def process(col_nr, row_nr, value):
            nonlocal result
            if is_nr(value) and (result is None or value > result):
                result = value
            return True

        rng = get_range(spreadsheet, arg)
        iterate_cells(spreadsheet, rng, process)
    else:
        return ERR_VALUE

    return result if result is not None else ERR_NA

def xmin(spreadsheet, *args):
    result = None
    if is_collection(args):
        items = [x for x in args if is_nr(x)]
        if len(items):  # it concerns a collection of numbers
            return min(items)

        else:  # it concerns a nested range, collection,...
            for arg in args:
                sub = xmin_single(spreadsheet, arg)
                if is_nr(sub):
                    result = min(result, sub) if is_nr(result) else sub
    else:
        result = xmin_single(spreadsheet, args)
    return result if result is not None else ERR_NA

def xmin_single(spreadsheet, arg):
    result = None
    if is_nr(arg):
        result = min(result, arg) if is_nr(result) else arg
    elif isinstance(arg, str):
        def process(col_nr, row_nr, value):
            nonlocal result
            if is_nr(value) and (result is None or value < result):
                result = value
            return True

        rng = get_range(spreadsheet, arg)
        iterate_cells(spreadsheet, rng, process)
    else:
        return ERR_VALUE

    return result if result is not None else ERR_NA

def xsum(spreadsheet, *args):
    result = 0
    if args in ERROR_VALUES:
        return args

    def process(col_nr, row_nr, value):
        nonlocal result
        if value is not None and is_nr(value):
            result += value
        return True

    if is_nr(args):
        return args

    # Ensure to use the exact range
    rng = None
    if is_collection(args):
        rng = []
        for ad in args:
            if is_nr(ad):
                result += ad
            else:
                rng.append(get_range(spreadsheet, ad))
    else:
        rng = args
    if is_collection(args):
        iterate_cells(spreadsheet, rng, process)
    # result = to_values(spreadsheet, rng, True, is_nr);
    return result

"""
    Ref: https://support.office.com/en-us/article/SUMIF-function-169b8c99-c05c-4483-a712-1697a653039b
"""
def sumif(spreadsheet, cell_address, criteria, sum_range=None):
    rng = get_range(spreadsheet, cell_address)

    def is_valid_cell(value):
        return is_valid(value, criteria)

    return sum(to_values(spreadsheet, rng, True, is_valid_cell))

def average(spreadsheet, cell_address):
    result = 0
    counter = 0

    def process(col_nr, row_nr, value):
        nonlocal result, counter
        if value is not None and not is_nr(value):
            return ERR_NA
        else:
            result += value
            counter += 1
        return True

    # Ensure to use the exact range
    rng = get_range(spreadsheet, cell_address)
    iterate_cells(spreadsheet, rng, process)
    return result / counter

def right(spreadsheet, text, n):
    if isinstance(text, str) or isinstance(text, str):
        return text[-n:]
    else:
        # TODO: get rid of the decimal
        return str(int(text))[-n:]

"""
Ref: https://support.office.com/en-us/article/INDEX-function-a5dcf0dd-996d-40a4-a822-b56b061328bd
"""
def index(spreadsheet, cell_address, row_nr=None, col_nr=None):
    try:
        return index_inter(spreadsheet, cell_address, row_nr, col_nr)
    except Exception as ex:
        raise Exception(
            "Error in index function, cell_address: [%s], row_nr: [%s], col_nr: [%s]" % (cell_address, row_nr, col_nr))

def index_inter(spreadsheet, cell_address, row_nr=None, col_nr=None):
    if row_nr is None and col_nr is None or row_nr is not None and row_nr == 0 or col_nr is not None and col_nr == 0:
        return ERR_VALUE
    elif row_nr in ERROR_VALUES:
        return row_nr

    rng = get_range(spreadsheet, cell_address)
    sheet, start, end = split_range(rng)
    sh, start_col, start_row = split_address(start)
    if row_nr is not None and col_nr is not None:
        col = num2col(col2num(start_col) + col_nr - 1)
        row = int(start_row) + int(row_nr - 1)
    elif row_nr is not None:
        sh, end_col, end_row = split_address(end)
        if start_col == end_col:  # it concerns a vertical array
            col = start_col
            row = int(start_row) + int(row_nr) - 1
        elif start_row == end_row:  # it concerns a horizontal array
            col = num2col(col2num(start_col) + row_nr - 1)
            row = int(start_row)
        else:
            raise Exception(
                "Multi dimension array not allowed with only row or column, cell_address: [%s], col_nr: [%s], row_nr: [%s]" % (
                    cell_address, col_nr, row_nr))
    else:
        return ERR_VALUE
        # raise Exception("Both row_nr and col_nr are missing, cell_address: [%s]" % (cell_address))
    return evaluate_spreadsheet(spreadsheet, sheet, col, int(row))

"""
Ref: https://support.office.com/en-us/article/RANK-EQ-function-284858ce-8ef6-450e-b662-26245be04a40
"""
def rank_eq(spreadsheet, item, cell_address, mode):
    rng = get_range(spreadsheet, cell_address)
    sheet, start, end = split_range(rng)
    sh, start_col, start_row = split_address(start)
    sh, end_col, end_row = split_address(end)
    start_col_nr, start_row_nr = col2num(start_col), int(start_row)
    end_row_nr = int(end_row)
    if not item or item == ERR_NA:
        return ERR_NA
    if start_col != end_col:
        raise Exception("The start and end column are expected to be the same")

    items = []
    for row_nr in range(start_row_nr, end_row_nr + 1):
        value = evaluate_spreadsheet(spreadsheet, sheet, num2col(start_col_nr), row_nr)
        if value is not None:
            items.append(value)
    if mode == 1:
        return rankdata(items, 'min')[items.index(item)]
    else:
        raise Exception("Mode isn't supported yet, mode: [%s], item: [%s]" % (mode, item))

def lookup(value, lookup_range, result_range):
    if not is_nr(value):
        raise Exception("Non numeric lookups (%s) not supported" % value)

    # TODO: note, may return the last equal value

    # index of the last numeric value
    lastnum = -1
    for i, v in enumerate(lookup_range):
        if isinstance(v, (int, float)):
            if v > value:
                break
            else:
                lastnum = i

    if lastnum < 0:
        raise Exception("No numeric data found in the lookup range")
    else:
        if i == 0:
            raise Exception("All values in the lookup range are bigger than %s" % value)
        else:
            if i >= len(lookup_range) - 1:
                # return the biggest number smaller than value
                return result_range[lastnum]
            else:
                return result_range[i - 1]

"""
The VLOOKUP function performs a vertical lookup by searching for a value in the first column of a table and 
returning the value in the same row in the index_number position.
Ref: https://www.techonthenet.com/excel/formulas/vlookup.php
"""
def vlookup(spreadsheet, item, cell_address, col_index_nr, approximate_match=False):
    if not item or item == ERR_NA:
        return ERR_NA

    if approximate_match and not isinstance(item, (float, int)):
        raise Exception("Item must be a number: [%s], row_index_nr: [%s]" % (item, col_index_nr))

    # We assume the range has been correctly Removed.
    # we can't find it in the cellmap as we changed the cell address to overcome conflict with other cells using
    # the same range
    # rng = get_range(spreadsheet, cell_address)
    rng = cell_address
    item = str(item).lower()
    sheet, start, end = split_range(rng)
    sh, start_col, start_row = split_address(start)
    sh, end_col, end_row = split_address(end)
    search_index = num2col(col2num(start_col) + col_index_nr - 1)
    previous = None
    ln = int(end_row) - int(start_row) + 1
    for row_nr in range(int(start_row), int(end_row) + 1):
        value = evaluate_spreadsheet(spreadsheet, sheet, start_col, row_nr)
        if value is None:  # we skip empty cells/columns
            continue
        value = str(value).lower()
        if approximate_match and previous is not None and int(previous) > int(value):
            raise Exception(
                "Items not in ascending order. previous: [%s], current: [%s], item: [%s], row_index_r: [%s]"
                % (previous, value, item, col_index_nr))

        if value == item or approximate_match and (
                ln - 1 == row_nr and value < item or previous and value > item > previous):
            return evaluate_spreadsheet(spreadsheet, sheet, search_index, row_nr)
        previous = value
    return ERR_NA

"""
The Excel HLOOKUP function performs a horizontal lookup by searching for a value in the top row of the table and 
returning the value in the same column based on the index_number.
Ref: https://www.techonthenet.com/excel/formulas/hlookup.php
"""
def hlookup(spreadsheet, item, cell_address, row_index_nr, approximate_match=False):
    if not item or item == ERR_NA:
        return ERR_NA
    if approximate_match and not isinstance(item, (float, int)):
        raise Exception("Item must be a number: [%s], row_index_nr: [%s]" % (item, row_index_nr))

    # We assume the range has already been correctly Removed.
    # we can't find it in the cellmap as we changed the cell address to overcome conflict with other cells using
    # the same range
    rng = cell_address
    # rng = get_range(spreadsheet, cell_address)
    item = str(item).lower()
    sheet, start, end = split_range(rng)
    sh, start_col, start_row = split_address(start)
    sh, end_col, end_row = split_address(end)
    start_col_nr, end_col_nr = col2num(start_col), col2num(end_col)
    ln = end_col_nr - start_col_nr + 1
    previous = None
    for col_nr in range(start_col_nr, end_col_nr + 1):
        value = evaluate_spreadsheet(spreadsheet, sheet, num2col(col_nr), start_row)
        if value is None:  # we skip empty cells/columns
            continue

        value = str(value).lower()
        if approximate_match and previous is not None and float(previous) > float(value):

            raise Exception(
                "Items not in ascending order. previous: [%s], current: [%s], item: [%s], row_index_r: [%s]"
                % (previous, value, item, row_index_nr))

        if value == item or approximate_match and (
                ln - 1 == col_nr and value < item or previous is not None and value > item > previous):
            return evaluate_spreadsheet(spreadsheet, sheet, num2col(col_nr), int(start_row) + int(row_index_nr - 1))

        previous = value
    return ERR_NA

# needs unit testing
def linest(*args, **kwargs):
    y = args[0]
    x = args[1]

    if len(args) == 3:
        const = args[2]
        if isinstance(const, str):
            const = (const.lower() == "true")
    else:
        const = True

    degree = kwargs.get('degree', 1)
    # build the vandermonde matrix
    a = np.vander(x, degree + 1)

    if not const:
        # force the intercept to zero
        a[:, -1] = np.zeros((1, len(x)))

    # perform the fit
    (coefs, residuals, rank, sing_vals) = np.linalg.lstsq(a, y)
    return coefs

# needs unit testing
def npv(*args):
    discount_rate = args[0]
    cashflow = args[1]
    return sum([float(x) * (1 + discount_rate) ** -(i + 1) for (i, x) in enumerate(cashflow)])

def match_type_convert(value):
    if type(value) == str:
        value = value.lower()
    elif type(value) == int:
        value = float(value)
    return value

# Ref: https://www.techonthenet.com/excel/formulas/match.php
def match(spreadsheet, item, cell_address, match_type=1):
    if not item or item == ERR_NA:
        return ERR_NA

    previous = None
    result = None
    item = match_type_convert(item)

    def process(col_nr, row_nr, value):
        nonlocal previous, result, match_type, use_col
        if match_type == 1:
            value = match_type_convert(value)
            if previous is not None and value < previous:
                raise Exception(
                    "Array must be in ascending order for match type 1, previous: "
                    "[%s], next: [%s], lookup value: [%s], range: [%s]" % (
                        previous, next, item, rng))
            if item == value:
                result = col_nr if use_col else row_nr
                return False
            if not result:
                result = 0
            elif item < value and previous is not None > previous:
                result -= 1
                return False
        elif match_type == 0:
            if item == match_type_convert(value):
                result = col_nr if use_col else row_nr
                return False

        elif match_type == -1:
            if not result:
                result = 0
            if previous is not None and value > previous:
                raise Exception(
                    "Array must be in descending order for match type 1, previous: [%s], next: [%s], "
                    "lookup_value: [%s, range: [%s]" % (
                        previous, next, item, rng))
            if item == value:
                result = col_nr if use_col else row_nr
                return True
            elif item < value:
                result = col_nr if use_col else row_nr
            elif value > item and previous is not None and item < previous:
                result += 1
                return True
            elif item < value and previous is not None > previous:
                result -= 1
                return False
        else:
            raise Exception('Not a valid match_type, valid match_types are (1, 0 ,-1)')

        previous = value
        return True

    rng = get_range(spreadsheet, cell_address)
    sheet, start, end = split_range(rng)
    sh, start_col, start_row = split_address(start)
    sh, end_col, end_row = split_address(end)
    if start_col == end_col:
        use_col = False
    elif start_row == end_row:
        use_col = True
    else:
        raise Exception("Match only supports a single search row or column. Address: [%s]", rng)
    iterate_cells(spreadsheet, rng, process)
    if result is not None:
        return result - col2num(start_col) + 1 if use_col else result - int(start_row) + 1
    return ERR_NA

# Excel Reference: https://support.office.com/en-us/article/MOD-function-9b6cd169-b6ee-406a-a97b-edf2a9dc24f3
def mod(spreadsheet, nb, q):
    if not isinstance(nb, int):
        raise TypeError("%s is not an integer" % str(nb))
    elif not isinstance(q, int):
        raise TypeError("%s is not an integer" % str(q))
    else:
        return nb % q

# Excel reference: https://support.office.com/en-us/article/COUNT-function-a59cd7fc-b623-4d93-87a4-d23bf411294c
def count(spreadsheet, cell_address):
    counter = 0

    def process(col_nr, row_nr, value):
        nonlocal counter
        if is_nr(value):
            counter += 1
        return True

    # Ensure to use the exact range
    rng = get_range(spreadsheet, cell_address)
    iterate_cells(spreadsheet, rng, process)
    # result = to_values(spreadsheet, rng, True, is_nr);
    return counter

def iferror(spreadsheet, value, value_if_error):
    # list of errors that are used in excel
    return value_if_error if value in ERROR_VALUES else value
"""
Counta function: counts the non empty cells
Ref: https://exceljet.net/excel-functions/excel-counta-function
"""
def counta(spreadsheet, cell_address):
    counter = 0

    def process(col_nr, row_nr, value):
        nonlocal counter
        if value is not None:
            counter += 1
        return True

    # Ensure to use the exact range
    rng = get_range(spreadsheet, cell_address)
    iterate_cells(spreadsheet, rng, process)
    return counter

# Excel reference: https://support.office.com/en-us/article/COUNTIF-function-e0de10c6-f885-4e71-abb4-1f464816df34
def countif(spreadsheet, cell_address, criteria):
    # WARNING:
    # - wildcards not supported
    # - support of strings with >, <, <=, =>, <> not provided
    rng = get_range(spreadsheet, cell_address)

    def is_valid_cell(value):
        return is_valid(value, criteria)

    return len(to_values(spreadsheet, rng, True, is_valid_cell))

# Ref: https://support.office.com/en-us/article/COUNTIFS-function-dda3dc6e-f74e-4aee-88bc-aa8c2a866842
def countifs(*args):
    arg_list = list(args)
    l = len(arg_list)

    if l % 2 != 0:
        raise Exception('excellib.countifs() must have a pair number of arguments, here %d' % l)

    if l >= 2:
        indexes = find_corresponding_index(args[0], args[1])  # find indexes that match first layer of countif

        remaining_ranges = [elem for i, elem in enumerate(arg_list[2:]) if i % 2 == 0]  # get only ranges
        remaining_criteria = [elem for i, elem in enumerate(arg_list[2:]) if i % 2 == 1]  # get only criteria

        filtered_remaining_ranges = []

        for range in remaining_ranges:  # filter items in remaining_ranges that match valid indexes from first countif layer
            filtered_remaining_range = []

            for index, item in enumerate(range):
                if index in indexes:
                    filtered_remaining_range.append(item)

            filtered_remaining_ranges.append(filtered_remaining_range)

        new_tuple = ()
        for index, range in enumerate(
                filtered_remaining_ranges):  # rebuild the tuple that will be the argument of next layer
            new_tuple += (range, remaining_criteria[index])

        return min(countifs(*new_tuple), len(indexes))  # only consider the minimum number across all layer responses

    else:
        return float('inf')

# Ref: https://support.office.com/en-us/article/ROUND-function-c018c5d8-40fb-4053-90b1-b3e7f61a213c
def xround(spreadsheet, number, num_digits=0):
    if not is_number(number) and number in ERROR_VALUES:
        return number
    elif not is_number(number) and isinstance(number, str):
        return ERR_VALUE
    elif not is_number(number):
        raise TypeError("%s is not a number" % str(number))

    if not is_number(num_digits):
        raise TypeError("%s is not a number" % str(num_digits))

    # if num_digits >= 0:  # round to the right side of the point
    # Refs: https://docs.python.org/2/library/functions.html#round
    # https://gist.github.com/ejamesc/cedc886c5f36e2d075c5
    if isinstance(number, (int, float)):
        result = float(Decimal(repr(number)).quantize(Decimal(repr(pow(10, -num_digits))), rounding=ROUND_HALF_UP))
    return result if num_digits > 0 else int(result)

def roundup(spreadsheet, number, num_digits=0):
    if not is_nr(number) or num_digits != 0:
        raise Exception("Incorrect input: nr: [%s], num_digits: [%s]" % (number, num_digits))
    return math.ceil(number)

def rounddown(spreadsheet, number, num_digits=0):
    if not is_nr(number) or num_digits != 0:
        raise Exception("Incorrect input: nr: [%s], num_digits: [%s]" % (number, num_digits))
    return math.trunc(number)

# Excel reference: https://support.office.com/en-us/article/MID-MIDB-functions-d5f9e25c-d7d6-472e-b568-4ecb12433028
def mid(text, start_num, num_chars):
    text = str(text)
    if type(start_num) != int:
        raise TypeError("%s is not an integer" % str(start_num))
    if type(num_chars) != int:
        raise TypeError("%s is not an integer" % str(num_chars))

    if start_num < 1:
        raise ValueError("%s is < 1" % str(start_num))
    if num_chars < 0:
        raise ValueError("%s is < 0" % str(num_chars))

    return text[start_num:num_chars]

# Ref: https://support.office.com/en-us/article/DATE-function-e36c0c8c-4104-49da-ab83-82328b832349
def date(year, month, day):
    if type(year) != int:
        raise TypeError("%s is not an integer" % str(year))

    if type(month) != int:
        raise TypeError("%s is not an integer" % str(month))

    if type(day) != int:
        raise TypeError("%s is not an integer" % str(day))

    if year < 0 or year > 9999:
        raise ValueError("Year must be between 1 and 9999, instead %s" % str(year))

    if year < 1900:
        year = 1900 + year

    year, month, day = normalize_year(year, month, day)  # taking into account negative month and day values
    date_0 = datetime(1900, 1, 1)
    date = datetime(year, month, day)
    result = (datetime(year, month, day) - date_0).days + 2
    if result <= 0:
        raise ArithmeticError("Date result is negative")
    else:
        return result

# Excel reference: https://support.office.com/en-us/article/YEARFRAC-function-3844141e-c76d-4143-82b6-208454ddc6a8
def yearfrac(start_date, end_date, basis=0):
    def actual_nb_days_isda(start, end):  # needed to separate days_in_leap_year from days_not_leap_year
        y1, m1, d1 = start
        y2, m2, d2 = end

        days_in_leap_year = 0
        days_not_in_leap_year = 0
        year_range = list(range(y1, y2 + 1))

        for y in year_range:
            if y == y1 and y == y2:
                nb_days = date(y2, m2, d2) - date(y1, m1, d1)
            elif y == y1:
                nb_days = date(y1 + 1, 1, 1) - date(y1, m1, d1)
            elif y == y2:
                nb_days = date(y2, m2, d2) - date(y2, 1, 1)
            else:
                nb_days = 366 if is_leap_year(y) else 365

            if is_leap_year(y):
                days_in_leap_year += nb_days
            else:
                days_not_in_leap_year += nb_days

        return days_not_in_leap_year, days_in_leap_year

    # http://svn.finmath.net/finmath%20lib/trunk/src/main/java/net/finmath/time/daycount/DayCountConvention_ACT_ACT_YEARFRAC.java
    def actual_nb_days_afb_alter(start, end):
        y1, m1, d1 = start
        y2, m2, d2 = end
        delta = date(*end) - date(*start)

        if delta <= 365:
            if is_leap_year(y1) and is_leap_year(y2):
                denom = 366
            elif is_leap_year(y1) and date(y1, m1, d1) <= date(y1, 2, 29):
                denom = 366
            elif is_leap_year(y2) and date(y2, m2, d2) >= date(y2, 2, 29):
                denom = 366
            else:
                denom = 365
        else:
            year_range = list(range(y1, y2 + 1))
            nb = 0

            for y in year_range:
                nb += 366 if is_leap_year(y) else 365

            denom = nb / len(year_range)

        return delta / denom

    if not is_number(start_date):
        raise TypeError("start_date %s must be a number" % str(start_date))
    if not is_number(end_date):
        raise TypeError("end_date %s must be number" % str(end_date))
    if start_date < 0:
        raise ValueError("start_date %s must be positive" % str(start_date))
    if end_date < 0:
        raise ValueError("end_date %s must be positive" % str(end_date))

    if start_date > end_date:  # switch dates if start_date > end_date
        temp = end_date
        end_date = start_date
        start_date = temp

    y1, m1, d1 = date_from_int(start_date)
    y2, m2, d2 = date_from_int(end_date)

    if basis == 0:  # US 30/360
        d2 = 30 if d2 == 31 and (d1 == 31 or d1 == 30) else min(d2, 31)
        d1 = 30 if d1 == 31 else d1

        count = 360 * (y2 - y1) + 30 * (m2 - m1) + (d2 - d1)
        result = count / 360

    elif basis == 1:  # Actual/actual
        result = actual_nb_days_afb_alter((y1, m1, d1), (y2, m2, d2))

    elif basis == 2:  # Actual/360
        result = (end_date - start_date) / 360

    elif basis == 3:  # Actual/365
        result = (end_date - start_date) / 365

    elif basis == 4:  # Eurobond 30/360
        d2 = 30 if d2 == 31 else d2
        d1 = 30 if d1 == 31 else d1

        count = 360 * (y2 - y1) + 30 * (m2 - m1) + (d2 - d1)
        result = count / 360

    else:
        raise ValueError("%d must be 0, 1, 2, 3 or 4" % basis)

    return result


if __name__ == '__main__':
    pass
