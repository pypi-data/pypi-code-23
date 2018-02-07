import argparse
import base64
import json
import re
import sys
import zipfile

from lxml import etree

file_regex = re.compile(
    r'(\d+)__(\d+)__(?P<data>results|qti|tst)_(?P<id>\d+).xml')
task_id_regex = re.compile(r'il_\d+_qst_(?P<task_id>\d+)')

tasks_path = ('./assessment/section')

users = './tst_active/row'
solutions = './tst_solutions/row[@question_fi="%s"]'

lecturer_xpath = ('./MetaData/Lifecycle/Contribute'
                  '[@Role="Author"]/Entity/text()')


def eat_qti(tree, only_of_type=('assSourceCode',), **kwargs):
    tasks = tree.xpath(tasks_path)[0]

    titles = tasks.xpath('./item/@title')
    types = tasks.xpath(
        './item/itemmetadata/qtimetadata/qtimetadatafield/'
        'fieldlabel[text()="QUESTIONTYPE"]/../fieldentry/text()')
    ids = [re.search(task_id_regex, ident).group('task_id')
           for ident in tasks.xpath('./item/@ident')]
    texts = ['\n'.join(flow.xpath('./material/mattext/text()'))
             for flow in tasks.xpath('./item/presentation/flow')]

    return {id: {'title': title, 'text': text, 'type': type}
            for id, type, title, text in zip(ids, types, titles, texts)
            if not only_of_type or type in only_of_type}


def eat_users(results_tree):
    return {row.attrib['active_id']: dict(row.attrib)
            for row in results_tree.xpath(users)}


def convert_code(text):
    return base64.b64decode(text).decode('utf-8').split('\n')


def eat_solutions(results_tree, task_id):
    return {row.attrib['active_fi']: convert_code(row.attrib['value1'])
            for row in results_tree.xpath(solutions % task_id)}


def eat_results(tree, qti=(), **kwargs):
    questions = qti
    users = eat_users(tree)
    for user in users.values():
        user['submissions'] = {}
    for question in questions:
        solutions = eat_solutions(tree, question)
        for user_id, solution in solutions.items():
            users[user_id]['submissions'][question] = solution
    return users


def eat_tst(tree):
    title = tree.xpath('./MetaData/General/Title/text()')
    lecturer = tree.xpath(lecturer_xpath)
    return {'exam': title[0], 'author': lecturer[0]}


def eval_file(archive, match, cache):
    funcname = 'eat_' + match.group('data')
    with archive.open(match.string) as datafile:
        tree = etree.parse(datafile)
        return globals()[funcname](tree, **cache)


def eat_archive(archive):
    files = {match.group('data'): match
             for match in (re.search(file_regex, name)
                           for name in archive.NameToInfo)
             if match}

    order = ('tst', 'qti', 'results')
    cache = {}

    for key in order:
        cache[key] = eval_file(archive, files[key], cache)

    return cache


def add_meta(base, data):
    base.update(data['tst'])


def add_tasks(base, data):
    base['tasks'] = data['qti']


ignore_user_fields = ("user_fi",
                      "anonymous_id",
                      "test_fi",
                      "lastindex",
                      "tries",
                      "submitted",
                      "submittimestamp",
                      "tstamp",
                      "user_criteria",)


def add_users(base, data):
    for userdata in data['results'].values():
        for field in ignore_user_fields:
            userdata.pop(field)
    base['students'] = data['results']


def give_me_structure(data):
    base = {}

    add_meta(base, data)
    add_tasks(base, data)
    add_users(base, data)

    return base


def eat_zipfile(input_file, output):
    with zipfile.ZipFile(input_file) as archive:
        data = dict(eat_archive(archive))

    structured_data = give_me_structure(data)

    json.dump(structured_data, output, indent=2, sort_keys=True)


def parseme():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'input',
        metavar='FILE',
        help='A ZIP file that contains a qit course')
    parser.add_argument(
        '-o',
        '--output',
        default=sys.stdout,
        type=argparse.FileType('w'),
        metavar='FILE',
        help='Where you want to put the output')
    return parser.parse_args()


def main():
    args = parseme()
    eat_zipfile(args.input, args.output)


if __name__ == '__main__':
    main()
