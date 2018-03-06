import math
import mmh3
from bitarray import bitarray


class BaseHashFunction:
    def __init__(self, num_of_filter_bits, num_of_hash_func):
        self.num_of_filter_bits = num_of_filter_bits
        self.num_of_hash_func = num_of_hash_func

    def get_indexes(self, element):
        raise NotImplementedError('get_indexes method not implemented!')


class MurmurHashFunction(BaseHashFunction):
    def __init__(self, num_of_filter_bits, num_of_hash_func):
        super().__init__(num_of_filter_bits, num_of_hash_func)

    def get_indexes(self, element):
        hash_list = []
        hash1 = mmh3.hash(element, 0)
        hash2 = mmh3.hash(element, hash1)
        for i in range(self.num_of_hash_func):
            hash_list.append(abs((hash1 + i * hash2) % self.num_of_filter_bits))

        return hash_list


class BloomFilter:
    def __init__(self, items_in_filter, error_rate, num_of_filter_bits=0, num_of_hash_func=0):
        """
        :param items_in_filter: expected number of items that will be added to filter
        :param error_rate: expected False Positive probability
        :param num_of_filter_bits: Number of bits in filter. If 0 calc_num_of_filter_bits method is used to calculate number of bits in filter
        :param num_of_hash_func: Number of hash functions to use. If 0 calc_num_of_hash_func method is used to calculate number of hash functions to use
        """

        self.__items_in_filter = items_in_filter
        self.__error_rate = error_rate

        self.__num_of_filter_bits = num_of_filter_bits if num_of_filter_bits else BloomFilter.calc_num_of_filter_bits(self.__items_in_filter, self.__error_rate)
        self.__num_of_hash_func = num_of_hash_func if num_of_hash_func else BloomFilter.calc_num_of_hash_func(self.__num_of_filter_bits, self.__items_in_filter)

        self.__filter = bitarray(self.__num_of_filter_bits)
        self.__filter.setall(0)

        self.__elements_count = 0

        self.__hash_function = MurmurHashFunction(self.__num_of_filter_bits, self.__num_of_hash_func)

    @property
    def num_of_filter_bits(self):
        """
        :return: Number of bits in filter
        """

        return self.__num_of_filter_bits

    @property
    def num_of_hash_functions(self):
        """
        :return: Number of hash functions
        """

        return self.__num_of_hash_func

    def get_filter(self):
        """
        :return: byte array of Bloom filter
        """
        return self.__filter

    def set_hash_function(self, func):
        """
        Changes default hash function
        :param func: hash function class subclass of BaseHashFunction
        """

        if not isinstance(func, BaseHashFunction):
            raise ValueError('Hash function must be subclass of BaseHashFunction!')

        self.__hash_function = func

    def false_positive_probability(self):
        """
        Calculates the current false positive probability based on the number of elements added so far
        :return: Current false positive probability
        """

        return math.pow((1.0 - math.exp(-(self.__num_of_hash_func * self.__elements_count) / self.__num_of_filter_bits)), self.__num_of_hash_func)

    def add(self, element):
        """
        Addes element to Bloom filter
        :param element: string to add to filter
        :return: if element already not inserted - insert and return list of indexes, else - None
        """

        indexes = self.__hash_function.get_indexes(element)
        if not self.__filter_contains(*indexes):
            self.__elements_count += 1
            self.__filter_add(*indexes)

            return indexes

    def __filter_add(self, *args):
        """
        Add hashed indexes to Bloom filter
        :param args: indexes to mark as True
        """

        for i in args:
            self.__filter[i] = True

    def __filter_contains(self, *args):
        """
        Checks whether all indexes args in filter are True
        :param args: indexes of filter to check
        :return: True if all indexes True, else - False
        """

        exist = True
        for i in args:
            exist = exist & self.__filter[i]
            if not exist:
                return exist

        return exist

    def __contains__(self, element):
        """
        Checks if elements is in filter
        :param element: string to check for existence
        :return: True if element exists, else - False
        """

        indexes = self.__hash_function.get_indexes(element)
        return self.__filter_contains(*indexes)

    def __len__(self):
        """
        :return: Unique number of elements added to filter
        """

        return self.__elements_count

    def __repr__(self):
        return ('Calculated probability of False Positive : %.4f\n'
                'Expected False Positive probability : %.4f\n'
                'Number of bits in filter : %s\n'
                'Number of hash functions : %s\n'
                'Number of elements added to filter : %s\n'
                'Bloom filter : %s'
                ) % (
            self.false_positive_probability(),
            self.__error_rate,
            self.__num_of_filter_bits,
            self.__num_of_hash_func,
            self.__elements_count,
            self.__filter,
        )

    @staticmethod
    def calc_num_of_hash_func(number_of_filter_bits, number_of_items_in_filter):
        """
        Calculates number of hash functions to use
        :param number_of_filter_bits: number of bits in filter
        :param number_of_items_in_filter: expected number of items
        :return: number of hash functions to use
        """

        return round(math.log(2.0) * number_of_filter_bits / number_of_items_in_filter)

    @staticmethod
    def calc_num_of_filter_bits(number_of_items_in_filter, error_rate):
        """
        Calculates number of bits in the filter
        :param number_of_items_in_filter: expected number of items
        :param error_rate: Probability of false positives
        :return: number of bits in the filter
        """

        return math.ceil((number_of_items_in_filter*math.log(error_rate)) / math.log(1.0 / math.pow(2.0, math.log(2.0))))

if __name__ == '__main__':
    class CustomHash(BaseHashFunction):
        def __init__(self, num_of_filter_bits, num_of_hash_func):
            super().__init__(num_of_filter_bits, num_of_hash_func)

        def get_indexes(self, element):
            hash_list = []
            hash1 = mmh3.hash(element, 0)
            hash2 = mmh3.hash(element, hash1)
            for i in range(self.num_of_hash_func):
                hash_list.append(abs((hash1 + i * hash2 * 2) % self.num_of_filter_bits))

            return hash_list

    bf = BloomFilter(100, 0.01)
    print(bf)

    bf.set_hash_function(CustomHash(bf.num_of_filter_bits, bf.num_of_hash_functions))

    print(bf.add('tomas'))
    print(bf.add('jonas'))
    print(bf.add('petras'))

    print(bf)

    print('tomas' in bf)
    print('bomas' in bf)