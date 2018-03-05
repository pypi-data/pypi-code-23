from Bio import bgzf
        

class IndexedTable(object):
    """
    Interface for a block-gzipped tsv or csv file stored on disk that allows rapid random access to rows of
    that file. Very similar to tabix except more flexible in that it is not restricted to indexing
    by genomic coordinates.
    """

    def __init__(self, bgzipped_filename, index_filename='', sep='\t', index_field='SYMBOL', force_reindex=False):
        """
        Returns a new IndexedTsv object that indexes the data in :param:`bgzipped_filename`. It will attempt
        to load a pre-generated index from `index_filename` (default is :param:`bgzipped_filename + .idx`.
        If that fails, it will create a new index and save it to :param:`index_filename`.

        Assumes that the first row of the file is a header row with field names. The values in :param:`index_field`
        will be indexed such that an entire row can be rapidly retrieved given the value in :param:`index_field`.

        :param bgzipped_filename: the filename of the compressed (with block gzip) tsv file to index.
        :param index_filename: the filename of the index. Defaults to :param:`bgzipped_filename + .idx`
        :param sep: the separator between fields. Defaults to `tab`
        :param index_field: which field to use for indexing
        :param force_reindex: forces the index to be rebuilt from scratch.
        :return: an IndexedTsv object.
        """
        self.bgzipped_filename = bgzipped_filename
        self.index_field = index_field
        self.sep = sep

        if not index_filename:
            index_filename = self.bgzipped_filename + '.idx'

        try:
            self._load_index(index_filename)
        except (OSError, IOError, ValueError, EOFError):
            force_reindex = True

        if force_reindex:
            try:
                self._create_index(index_filename=index_filename)
            except ValueError:
                dbg_print(
                    '{} does not appear to be a valid bgzipped file. Converting now...'.format(self.bgzipped_filename))
                convert_gzipped_to_bgzipped(self.bgzipped_filename)
                self._create_index(index_filename=index_filename)

    def _load_index(self, index_filename):
        """
        Load the index from :param:`index_filename`

        :param index_filename:
        :return:
        """
        self._offset_index = {}

        with open(index_filename, 'rt') as index_file:
            self.fields = index_file.readline().rstrip().split(self.sep)
            for line in index_file:
                split_line = line.rstrip().split('\t')
                self._offset_index[split_line[0]] = int(split_line[1])

    def _create_index(self, index_filename):
        """
        Create a new index and save it to :param:`index_filename`
        :param index_filename:
        :return:
        """
        start_time = datetime.datetime.now()
        dbg_print('Indexing {} ...'.format(self.bgzipped_filename))
        self._offset_index = {}
        line_num = 0
        with bgzf.BgzfReader(self.bgzipped_filename, 'rt') as in_file:
            # process header line
            line = in_file.readline()
            self.fields = line.rstrip().split(self.sep)
            self.index_col = self.fields.index(self.index_field)  # find the column containing the index field

            start_pos = in_file.tell()  # record position at beginning of line
            # get the first data line
            line = in_file.readline().rstrip()

            while line is not '':

                if line_num % 1000000 == 0:
                    dbg_print('\tIndexing line {} ...'.format(line_num + 1))
                try:
                    key = line.split(self.sep)[self.index_col]
                except IndexError:
                    dbg_print('Malformed line {} : {}'.format(line_num, line))
                self._offset_index[key] = start_pos
                line_num += 1
                start_pos = in_file.tell()  # record position at beginning of line
                line = in_file.readline().rstrip()

            dbg_print('\tRead {} lines.'.format(line_num))

        dbg_print('Saving index to {} ...'.format(index_filename))
        with open(index_filename, 'wt') as index_file:
            index_file.write(self.sep.join(self.fields) + '\n')
            for key in self._offset_index:
                index_file.write('{}\t{}\n'.format(key, self._offset_index[key]))
        dbg_print('Done in {}'.format(datetime.datetime.now() - start_time))

    def _parserow(self, row_text):
        """
        Parse :param:`row_text` and return it as a dictionary.
        :param row_text:
        :return:
        """
        return dict(list(zip(self.fields, row_text.split(self.sep))))

    def __getitem__(self, item):
        """
        Retrieves a single row using Python bracket notation.
        :param item:
        :return:
        """
        if item in self._offset_index:
            with bgzf.BgzfReader(self.bgzipped_filename, 'rt') as in_file:
                in_file.seek(self._offset_index[item])
                return self._parserow(in_file.readline().rstrip())

    def __contains__(self, key):
        """
        Performs the membership test for :param:`key`.
        :param key:
        :return:
        """
        return key in self._offset_index