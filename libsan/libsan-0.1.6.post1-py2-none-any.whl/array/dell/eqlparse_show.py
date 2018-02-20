# Copyright (C) 2016 Red Hat, Inc.
# This file is part of libsan.
#
# libsan is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# libsan is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with libsan.  If not, see <http://www.gnu.org/licenses/>.

#Initial version was developed by jdmorts, and it is available at:
#http://pydoc.net/Python/ail/0.2.8/ail.platforms.equallogic.parse_show/

__author__ = 'jdmorts'
#Modified by: Bruno Goncalves <bgoncalv@redhat.com>

from collections import namedtuple
from collections import deque
import re

def _print(string):
    module_name = __name__
    string = re.sub("DEBUG:", "DEBUG:("+ module_name + ") ", string)
    string = re.sub("FAIL:", "FAIL:("+ module_name + ") ", string)
    string = re.sub("FATAL:", "FATAL:("+ module_name + ") ", string)
    string = re.sub("WARN:", "WARN:("+ module_name + ") ", string)
    print string
    if "FATAL:" in string:
        raise RuntimeError(string)
    return

def remove_col_wrap(column_spec, column_names, rows):
    """Given a set of rows and column widths, concatentate the fields of each
    column until the number of fields equals the number of columns. If two rows
    each contain five fields in five columns, this function returns one row of
    five fields in five columns. Any leading/trailing spaces are removed.

    This::

       a    b         c  d e
     ['----|---------|--|-|----------',
      ' ---|  -------|--|-| -----------']

    becomes::

     {'a': '-------',
      'b': '-------',
      'c': '----------------',
      'd': '----',
      'e': '--',
      'f': '---------------------'}

    :param column_spec: row widths stored as int
    :type column_spec: list of int
    :param column_names: used as keys to build record dict
    :type column_names: list of str
    :param rows: rows of a column-wrapped record
    """
    record = {}
    offset = 0
    #print "DEBUG remove"
    #0print rows

    for col_width, col_name in zip(column_spec, column_names):
        column = ''
        # Strip line ends and left justify so len(row) == sum(column_spec)
        for row in (r.rstrip('\n\r').ljust(sum(column_spec)) for r in rows):
            # Concatenate lines in the current column
            col_slice = slice(offset, offset + col_width)
            column += row[col_slice].strip()
        # Add column to record and set offset for next column
        record[col_name] = column
        offset += col_width + 1

    return record


def parse_show(output, class_name=None, repr_method=None):
    """Parse Dell EqualLogic 'show' command output. While the formatting is
    consistent, it's tricksy on account of an ill-conceived column wrap. The
    following is sample output illustrating this curious 'feature'::

        EQGroup01> volume select MBX01-DB01 access show
        ID  Initiator                     Ipaddress       AuthMethod UserName   Apply-To
        --- ----------------------------- --------------- ---------- ---------- --------
        1   iqn.1998-01.com.vmware:xxxxxv *.*.*.*         none                  volume
              m01-4c08cb5e
        2   iqn.1998-01.com.vmware:xxxxxv *.*.*.*         none                  volume
              m02-7b27a2a8
        . . .

    Because the use of hyphens to denote column width is consistent, we can
    precisely specify the number of characters in each column using the
    number of hyphens observed. Also, notice the two-space indent where the
    'Initiator' column wraps; this must be stripped before concatenation.

    :param output: output from an EqualLogic CLI 'show' command
    :type output: list of str
    :param class_name: type given to the namedtuples to create for each record
    :type class_name: str
    :param repr_method: function given to __repr__ for all namedtuples returned
    :type repr_method: function
    """
    col_spec = []  # Column slices
    col_names = []  # Column headers
    Klass = None  # Container class
    previous_line = ''  # Used to catch column headers once we see hypens
    saw_prompt = False
    records = {}

    try:
        #lines = deque(output)
        lines = output.split("\n")
        #print "DEBUG: output : %s" % output

    except TypeError:
        raise TypeError('Unexpected output type {:s}'.format(type(output)))

    line_id = 0
    sub_item = None
    detailed_info = False
    while True:
        try:
            #cur_line = lines.popleft().rstrip('\n')
            cur_line = lines[line_id].rstrip('\n')
            line_id += 1
            #print "DEBUG parse: try %s - %s" % (cur_line, previous_line)
            if not cur_line:
                continue

        except IndexError:
            break
        #print "DEBUG cur line: %s" % cur_line
        # Identify EQ prompts; ignore remaining output if we see two of them
        if cur_line.split(' ', 1)[0].endswith('>'):
            if saw_prompt:
                break
            else:
                saw_prompt = True
        elif cur_line.startswith('_'):
            #The setting from lines starting with _ will be stored with diferent key
            #for example volume select <volume> access show
            entry = cur_line.replace("_","")
            entry = entry.replace(" ","_")
            entry = entry.lower()
            #print "parse_show - entry: %s" % entry
            sub_item = entry
            col_spec = []
            col_names = []
            detailed_info = False
        elif cur_line.startswith('-'):
            #print "DEBUG parse: %s - %s" % (cur_line, previous_line)
            col_spec = [len(c) for c in cur_line.split()]
            col_names = [col.lower()
                         for col in previous_line.replace('-', '_').split()]
            #print "DEBUG: parse show start '-':"
            #print col_names
            #print col_spec
            #Klass = namedtuple(class_name, col_names)
            #if repr_method:
            #    Klass.__repr__ = repr_method
        # Once we know the column widths,
        elif col_spec:
            rows = [cur_line]
            # Gather continuing lines resulting from column wrap
            while True:
                try:
                    # If next line is a continuation of current line,
                    if lines[line_id].startswith(' '):
                        #rows.append(lines.popleft())
                        rows.append(lines[line_id])
                        line_id += 1
                    else:
                        break

                except IndexError:
                    break
            # Combine like columns in rows of the same record
            record = remove_col_wrap(col_spec, col_names, rows)
            # Store record in container object and use first column as dict key
            #obj = Klass(**record)
            key = record[col_names[0]]
            if sub_item:
                if sub_item not in records:
                    records[sub_item] = {}
                records[sub_item][key] = record
            else:
                records[key] = record
            
        # For example Volume Information of specific LUN
        elif re.match("(.*): (\S+)", cur_line):
            m = re.match("(.*): (\S+)", cur_line)
            if not sub_item:
                _print("FAIL: parse_show() - Does not know to which sub item this info belongs")
                previous_line = cur_line
                continue
            key = m.group(1)
            key = key.replace(" ", "_")
            key = key.lower()
            value = m.group(2)
            #col_spec = [len(c) for c in cur_line.split()]
            #col_names = [key, value]
            next_line = lines[line_id].rstrip('\n')
            #: means new entry
            #starting with _ mean end of registry
            if not re.search(": ", next_line) and not re.match("_", next_line):
                value += next_line
            if sub_item not in records:
                records[sub_item] = {}
            records[sub_item][key] = value
            #_print("DEBUG: Found key %s with value %s" % (key, value))
            #print records[sub_item]
            
        # Update previous_line to current line
        previous_line = cur_line

    return records
