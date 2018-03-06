from typing import Dict, Set

import click

from collections import defaultdict

from pytsv.pytsv import TsvReader


@click.command()
@click.option(
    '--input-file',
    required=True,
    type=str,
    help="input filename",
)
@click.option(
    '--parent-column',
    required=True,
    type=int,
    help="parent column",
    show_default=True,
)
@click.option(
    '--child-column',
    required=True,
    type=int,
    help="child column",
    show_default=True,
)
@click.option(
    '--roots',
    required=False,
    type=str,
    default=None,
    help="roots to output, separated by commas",
    show_default=True,
)
def main(
    input_file,
    parent_column,
    child_column,
    roots,
):
    # type: (str, int, int) -> None
    """
    Draw tree by two columns in a tsv file
    You can also see only parts of the tree
    """
    children_dict = defaultdict(set)  # type: Dict[Set]
    parents_dict = defaultdict(set)
    with TsvReader(filename=input_file) as input_file_handle:
        for fields in input_file_handle:
            p_parent = fields[parent_column]
            p_child = fields[child_column]
            children_dict[p_parent].add(p_child)
            parents_dict[p_child].add(p_parent)
    # find the roots (parents that have no parents)
    if roots:
        list_of_roots = roots.split(',')
    else:
        list_of_roots = []
        for p_parent in children_dict.keys():
            if len(parents_dict[p_parent]) == 0:
                list_of_roots.append(p_parent)

    list_to_append = []
    first = True
    for root in list_of_roots:
        list_to_append.append((root, 0, first, ""))
        first = False

    stack = []
    stack.extend(list_to_append)
    # lets draw the tree
    while len(stack) > 0:
        name, depth, last, print_list = stack.pop()
        if last:
            special_string = u"└──"
        else:
            special_string = u"├──"
        print("{}{}".format(print_list + special_string, name))
        first = True
        list_to_append = []
        for p_child in children_dict[name]:
            if last:
                special_string = "   "
            else:
                special_string = u"│  "
            list_to_append.append((p_child, depth+1, first, print_list+special_string))
            first = False
        stack.extend(list(reversed(list_to_append)))


if __name__ == '__main__':
    main()
