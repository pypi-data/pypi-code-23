"""
This does that
"""

import os


class Sequence():
    """
    class Docstring
    """
    def __init__(self, sequence=""):
        """
        Function:
            Initialize sequence
        """
        if not isinstance(sequence, str):
            raise TypeError('Please provide a sequence in string format')
        self.sequence = sequence


    def __str__(self):
        """
        Function:
            Get string of the sequence
        """
        return self.sequence

    def __repr__(self):
        """Function: Get string of the sequence
        """
        return self.sequence

    def reverse_complementary(self):
        """Function: Returns the reverse complementary string

        Parameters
        ----------
        None

        Returns
        -------
        seq_rev : str
            Reverse complementary sequence
        """
        
        sequence = self.sequence
        seq_rev = ''
        for i in range(len(sequence) -1, -1, -1):
            if sequence[i] == 'A':
                seq_rev += 'T'
            elif sequence[i] == 'T':
                seq_rev += 'A'
            elif sequence[i] == 'G':
                seq_rev += 'C'
            elif sequence[i] == 'C':
                seq_rev += 'G'
            else:
                seq_rev += sequence[i]

        return seq_rev

    def percent_gc(self):
        """
        Function:
            Get % GC of the sequence
        """
        sequence = self.sequence
        a_base = sequence.count('A')
        c_base = sequence.count('C')
        g_base = sequence.count('G')
        t_base = sequence.count('T')

        perc_cg = (c_base + g_base) / float(g_base + t_base + a_base + c_base)
        perc_cg = round(perc_cg, 2)
        return perc_cg

    def count_ocurrences(self):
        """
        Function:
            Count ocurrences of each base
        """
        # More efficient with collections, but to test this its ok
        sequence = self.sequence
        found_bases = list(set(sequence))
        ocurrences = {x: sequence.count(x) for x in found_bases}

        ocurrences_list = []
        for key in sorted(ocurrences.keys()):
            ocurrences_list.append(key + ': ' + str(ocurrences[key]))
        return ocurrences_list

    def stats(self):
        """
        Function:
            Calculate stats of DNA sequence
        """
        perc_cg = self.percent_gc()
        ocurrences = self.count_ocurrences()
        sequence_reverse_comp = self.reverse_complementary()

        print("GC Percentage: " + str(round(perc_cg, 2)))
        print("Ocurrences:    " + str(ocurrences))
        print("Reverse comp:  " + str(sequence_reverse_comp))

        return None



"""
This will contain the class for regions
"""

class Regions():
    """
    class Regions
    """

    def __init__(self, file_path=""):
        """
        Initialize
        """
        if not isinstance(file_path, str):
            raise TypeError('Please provide a path in string format')

        if not os.path.exists(file_path):
            raise ImportError('File ' + file_path + ' does not exists, please provide an existing file')

        if os.path.isdir(file_path):
            raise ImportError('File is a directory, please provide a file')

        regions = self.__process_path(file_path)
        self.regions = regions

    def __repr__(self):
        """
        Represent files
        """
        return(str(self.regions))

    def __process_path(self, file_path):
        """
        This will retrieve data from the file
        """
        in_file = open(file_path, 'r')
        regions = []
        for line in in_file:
            if line.startswith('#'):
                continue
            line = line.strip('\n').split('\t')
            regions.append(line)
        return(regions)
