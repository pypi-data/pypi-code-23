"""
Sorter for big files
Copyright (C) 2017 - Pietro Mascolo

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Author: Pietro Mascolo
Email: iz4vve@gmail.com
"""
import collections
import heapq
import tempfile

TEMP_FILE_SIZE = 10000


def yield_lines(tmp):
    """
    Support function to yield lines from temporary file
    """
    for line in sorted(tmp.read().split(b"\n")):
        yield str(line)


def chunk_file(path, temp_file_size=TEMP_FILE_SIZE, line_filter=None, header=False):
    """
    Function to read (big) files in chunks
    Yields iterators over chunks

    :param path: path to file to read
    :param temp_file_size: number of lines per chunk
    :param line_filter: function to filter or operate on lines
    :param header: whether the first line contains a header (it will be skipped)
    """
    curr = collections.deque()
    for n, line in enumerate(open(path)):
        if not n and header:
            continue
        if n and not n % temp_file_size:
            yield curr
            curr = collections.deque()
        if line_filter:
            curr.append(line_filter(line))
        else:
            curr.append(line)


def write_merged(merged, output_file):
    """
    Writes sorted iterable to a file
    """
    with open(output_file, "w") as out:
        for sample in merged:
            out.write(str(sample))


def sorter(iterable):
    """
    Sorts an iterable using temporary files for chunks.
    Sorting is performed using heapq module to join multiple
    already sorted chunks

    :param iterable: iterable to sort
    :return: sorted iterable
    """
    iterators = collections.deque()
    for chunk in iterable:
        f = tempfile.TemporaryFile()
        f.write(bytes("\n".join(chunk), "utf-8"))
        f.seek(0)
        iterators.append(yield_lines(f))

    merged = heapq.merge(*iterators)

    return merged

#
# ###############################################################################
# if __name__ == '__main__':
#     import operator
#     # EXAMPLE USAGE
#
#     def element_filter(line):
#         return ",".join(
#             operator.itemgetter(*(2, 8, 3))(line.strip().split(","))
#         )
#     SORTED_LINES = sorter(
#         chunk_file(
#             "C:\\Users\\vmascol52\\Desktop\\deliveries.csv",
#             line_filter=element_filter
#         )
#     )
