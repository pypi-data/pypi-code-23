import argparse
import functools
import json
import logging
import os
from typing import Any, Callable, Dict, Sequence

from xkcdpass import xkcd_password as xp


from lib import Converter


# ============================== =- Logging -= ============================== #
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# create console handler and formatter
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(levelname)s] %(message)s')

# add formatter to console handler
console.setFormatter(formatter)
log.addHandler(console)


# ============================= =- argparse -= ============================== #
def parseme():
    def file_exists(parser, filepath: str) -> str:
        if not os.path.isfile(filepath):
            parser.error('Not a file %s' % filepath)
        return filepath

    parser = argparse.ArgumentParser()
    parser.add_argument(
        'input',
        metavar='DATA',
        type=lambda f: file_exists(parser, f),
        help='an Ilias course export in .zip or .xls format')
    parser.add_argument(
        'output',
        metavar='OUTFILE',
        help='destination of converter output (JSON)')
    parser.add_argument(
        '-a', '--anonymous',
        action='store_true',
        help='replace personal information and create a reversing table')
    parser.add_argument(
        '-t', '--personal-secret-table',
        help='where to store personal information (CSV)',
    )
    parser.add_argument(
        '-m', '--meta',
        action='store_true',
        help='add meta information (lecturer, course title)'
    )

    args = parser.parse_args()

    if args.anonymous != (args.personal_secret_table is not None):
        parser.error('Need an output for anonymous mode')

    return args


# ========================== =- General Purpose -= ========================== #
def compose(*functions: Sequence[Callable]) -> Callable:
    """ Standard function composition. Takes a Sequence of functions [f, g, h, ...]
    and returns the composite function i(x) = f(g(h(x))). There are no checks
    that validate if domain and image of these functions are compatible."""
    return functools.reduce(lambda f,
                            g: lambda x: f(g(x)),
                            functions,
                            lambda x: x)


# ========================== =- Post processors -= ========================== #
def anonymise(structured_data: Dict[str, Any]) -> Dict[str, Any]:
    DELIMITER = '-'
    wordfile = xp.locate_wordfile()
    words = xp.generate_wordlist(wordfile=wordfile,
                                 min_length=7,
                                 max_length=7)

    def get_identifier():
        return xp.generate_xkcdpassword(words, numwords=2, delimiter=DELIMITER)

    students = structured_data.pop('students')
    reverser = {get_identifier(): s for s in students.values()}
    students_anon = {r: {
        'fullname': ' '.join(w[0].capitalize() + w[1:]
                             for w in r.split(DELIMITER)),
        'identifier': r,
        'submissions': student['submissions']
    } for r, student in zip(reverser, students.values())}

    with open(args.personal_secret_table, 'w') as out:
        print('key, previous identifier, fullname', file=out)
        print('\n'.join(anon + '\t' + '\t'.join(v
                                                for v in data.values()
                                                if type(v) is str)
                        for anon, data in reverser.items()), file=out)

    structured_data.update({'students': students_anon})
    return structured_data


def add_meta_information(structured_data: Dict[str, Any]) -> Dict[str, Any]:
    if args.meta:
        structured_data['author'] = input('[Q] author: ')
        structured_data['exam'] = input('[Q] course title: ')
    return structured_data


def assert_correct_format(structured_data: Dict[str, Any]) -> Dict[str, Any]:
    def assert_submission(submission):
        assert 'code' in submission, 'A submission needs code'
        assert 'type' in submission, 'A submission has to be of some type'
        assert 'tests' in submission, 'A tests dict has to be present.'

    def assert_student(student):
        log.debug('asserting %s (%d)' % (student['fullname'],
                                         len(student['submissions'])))
        assert 'fullname' in student, 'Student needs a name %s' % student
        assert 'identifier' in student, 'Student needs a unique identifier'

    def base_assert():
        assert 'students' in structured_data, 'No students found'
        assert 'tasks' in structured_data, 'No tasks found'

    try:
        base_assert()
        students = structured_data['students'].values()
        number_of_submissions = len(structured_data['tasks'])
        for student in students:

            try:
                assert_student(student)
                assert number_of_submissions == len(student['submissions']), \
                    '%s does not have enough submissoins' % student['fullname']
                for submission in student['submissions']:

                    try:
                        assert_submission(submission)
                    except AssertionError as err:
                        log.warn(err)

            except AssertionError as err:
                log.warn(err)

    except AssertionError as err:
        log.warn(err)

    return structured_data


post_processors = [
    anonymise,
    # add_meta_information,
    # assert_correct_format
]


# ============================== =- Hektor -= =============================== #
def _preprocessing(filepath: str) -> str:
    return filepath


def _processing(filepath: str) -> Dict[str, Any]:
    try:
        return next(converter().convert(filepath)
                    for converter in Converter.implementations()
                    if converter.accept(filepath))
    except StopIteration as err:
        log.error('No suitable converter found. Accepting only %s' %
                  ', '.join(f
                            for c in Converter.implementations()
                            for f in c.accepted_files))


def _postprocessing(structured_data: Dict[str, Any]) -> Dict[str, Any]:
    return compose(*post_processors)(structured_data)


def main():
    global args
    args = parseme()

    processing = compose(_postprocessing, _processing, _preprocessing)
    data = processing(args.input)
    destination = args.output.split('.json')[0] + '.json'
    with open(destination, 'w') as output:
        json.dump(data, output, indent=2, sort_keys=True)
    log.info('Wrote exam data to %s', destination)


if __name__ == '__main__':
    main()
