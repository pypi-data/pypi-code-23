#!/usr/bin/env python

from functools import partial
import argparse
import csv
import os
import subprocess
import sys

from .pdf import Pdf
from .util import chunks, stacked_chunks


type_to_icon_map = {
    'chore': 'icons/chore.png',
    'bug': 'icons/bug.png',
    'feature': 'icons/feature.png',
    'spike': 'icons/spike.png',
    'release': 'icons/release.png'
}


class PivotalTask(object):

    def __init__(self, description, story, *a, **k):
        super(PivotalTask, self).__init__(*a, **k)

        self.description = description
        self.story = story

    def draw(self, pdf, x, y, width, height, show_number=False):
        pdf.set_line_width(0.3)
        pdf.rect(x, y, width, height)

        pdf.set_xy(x + 2, y + 2)
        pdf.set_font('Helvetica', '', 18)
        pdf.set_text_color(0, 0, 0)
        with pdf.clipping_rect(x, y, width, height - 10):
            pdf.multi_cell(width - 4, 8, self.description, align='L')

        pdf.set_font_size(10)
        pdf.set_text_color(150, 150, 150)
        pdf.text(x + 4, y + height - 4, '#' + self.story.id)


class PivotalTaskPair(object):

    def __init__(self, pair, *a, **k):
        super(PivotalTaskPair, self).__init__(*a, **k)

        self.first = pair[0]
        self.second = pair[1] if len(pair) > 1 else None

    def draw(self, pdf, x, y, width, height, show_number=False):
        self.first.draw(pdf, x, y, width, height / 2)

        if self.second:
            self.second.draw(pdf, x, y + height / 2, width, height / 2)


class PivotalStory(object):

    def __init__(self, number, id,
                 title, description,
                 estimate, labels, type,
                 tasks,
                 *a, **k):
        super(PivotalStory, self).__init__(*a, **k)

        self.number = number
        self.id = id
        self.title = title
        self.description = description
        self.estimate = estimate
        self.labels = labels
        is_spike = 'spike' in labels.split(', ')
        self.type = 'spike' if is_spike else type
        self.tasks = [PivotalTask(t, self) for t in tasks]

    def draw(self, pdf, x, y, width, height, show_number=False):
        pdf.set_font('Helvetica')
        pdf.set_text_color(0, 0, 0)
        pdf.set_line_width(0.3)
        pdf.rect(x, y, width, height)

        icon = type_to_icon_map.get(self.type, None)
        if icon is not None:
            root_dir = os.path.dirname(os.path.abspath(__file__))
            icon_path = os.path.join(root_dir, icon)
            pdf.image(icon_path, x + width - 12, y + height - 12, 8, 8)

        pdf.set_xy(x + 2, y + 2)
        pdf.set_font_size(12)
        pdf.multi_cell(width - 4, 12, '#' + self.id, align='L', border='B')

        pdf.set_xy(x + 2, y + 2)
        pdf.multi_cell(width - 8, 12, self.estimate, align='R')

        pdf.multi_cell(width, 4)

        pdf.set_x(x + 2)
        pdf.set_font('Helvetica', 'B', 18)
        pdf.multi_cell(width - 4, 8, self.title, align='L')

        pdf.multi_cell(width, 4)

        pdf.set_x(x + 2)
        pdf.set_font('Helvetica', '', 12)
        with pdf.clipping_rect(x + 2, y, width - 4, height - 14):
            pdf.multi_cell(width - 4, 6, self.description)

        pdf.set_font_size(10)
        pdf.text(x + 4, y + height - 4, self.labels)

        if show_number:
            pdf.set_font_size(8)
            pdf.set_text_color(150, 150, 150)
            pdf.text(x + width - 4, y + height - 2, str(self.number))


def get_data_from_column_index(data, column_names, column_title):
    return "" if column_title not in column_names \
        else data[column_names.index(column_title)]


def make_pivotal_story(column_names, number_data):
    number, data = number_data
    task_indices = [i for i, name in enumerate(column_names) if name == 'Task']
    tasks = [data[i] for i in task_indices if i < len(data)]
    return PivotalStory(
        number=number,
        id=get_data_from_column_index(data, column_names, 'Id'),
        title=get_data_from_column_index(data, column_names, 'Title'),
        description=get_data_from_column_index(data, column_names, 'Description'),
        estimate=get_data_from_column_index(data, column_names, 'Estimate'),
        labels=get_data_from_column_index(data, column_names, 'Labels'),
        type=get_data_from_column_index(data, column_names, 'Type'),
        tasks=tasks,
    )


def validate_columns(column_names):
    requried_columns = set(('Id', 'Title', 'Description', 'Estimate', 'Labels', 'Type'))
    column_names = set(column_names)
    if not requried_columns.issubset(column_names):
        raise RuntimeError(
            "Missing columns: %s" % requried_columns.difference(column_names)
        )


def iterstories(stories, include_tasks=False):
    for s in stories:
        yield s
        if include_tasks:
            for t in chunks(s.tasks, 2):
                yield PivotalTaskPair(t)


def open_file(filename):
    if sys.platform.startswith('darwin'):
        subprocess.call(('open', filename))
    elif os.name == 'nt':
        os.startfile(filename)
    elif os.name == 'posix':
        subprocess.call(('xdg-open', filename))


def main():
    arg_parser = argparse.ArgumentParser(
        description='Create a pdf document from a exported csv of Pivotal Tracker',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    arg_parser.add_argument(
        'csv',
        help='the file path to the csv file')
    arg_parser.add_argument(
        '-m', '--margin', type=int, default=5,
        help='margin of the page in mm')
    arg_parser.add_argument(
        '-o', '--output',
        help='file path to the generated pdf')
    arg_parser.add_argument(
        '-n', '--show-number', action='store_true',
        help='shows the story number on the bottom left')
    arg_parser.add_argument(
        '-t', '--show-tasks', action='store_true',
        help='shows the tasks for each story')
    arg_parser.add_argument(
        '-c', '--collate', action='store_true',
        help='collate stories for easier sorting after cutting all pages')
    arg_parser.add_argument(
        '-s', '--strict', action='store_true',
        help='fails if the csv file does not contain all required columns')

    args = arg_parser.parse_args()

    output_file = args.output if args.output is not None \
        else os.path.splitext(args.csv)[0] + '.pdf'
    page_margin = args.margin
    story_width = (297 - (page_margin * 2)) / 2
    story_height = (210 - (page_margin * 2)) / 2
    stories = []

    with open(args.csv, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        data = list(reader)
        if args.strict:
            validate_columns(data[0])
        stories = map(partial(make_pivotal_story, data[0]),
                      enumerate(data[1:], 1))

    pdf = Pdf()
    pdf.set_auto_page_break(False)

    positions = [
        (page_margin, page_margin),
        (page_margin + story_width, page_margin),
        (page_margin, page_margin + story_height),
        (page_margin + story_width, page_margin + story_height)]

    stories = list(iterstories(stories, include_tasks=args.show_tasks))
    chunk_function = stacked_chunks if args.collate else chunks
    for story_chunk in chunk_function(stories, 4):
        pdf.add_page('Landscape')
        for story, position in zip(story_chunk, positions):
            story.draw(
                pdf,
                position[0], position[1],
                story_width, story_height,
                args.show_number,
            )

    pdf.output(output_file)

    open_file(output_file)

    return output_file


if __name__ == "__main__":
    main()
