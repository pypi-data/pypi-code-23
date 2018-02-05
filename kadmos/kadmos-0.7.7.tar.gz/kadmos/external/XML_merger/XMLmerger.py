import sys
import argparse
from xml.etree import ElementTree as et

import os


class hashabledict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.items())))


class XMLCombiner(object):
    def __init__(self, roots):
        assert len(roots) > 0, 'No XML trees!'
        # save all the roots, in order, to be processed later
        self.roots = [root for root in roots]

    def combine(self):
        for r in self.roots[1:]:
            # combine each element with the first one, and update that
            self.combine_element(self.roots[0], r)
        # return the string representation
        return et.ElementTree(self.roots[0])

    def combine_element(self, one, other):
        """
        This function recursively updates either the text or the children
        of an element if another element is found in `one`, or adds it
        from `other` if not found.
        """
        # Create a mapping from tag name to element, as that's what we are filtering with
        mapping = {(el.tag, hashabledict(el.attrib)): el for el in one}
        for el in other:
            if len(el) == 0:
                # Not nested
                try:
                    # Update the text
                    mapping[(el.tag, hashabledict(el.attrib))].text = el.text
                except KeyError:
                    # An element with this name is not in the mapping
                    mapping[(el.tag, hashabledict(el.attrib))] = el
                    # Add it
                    one.append(el)
            else:
                try:
                    # Recursively process the element, and update it in the same way
                    self.combine_element(mapping[(el.tag, hashabledict(el.attrib))], el)
                except KeyError:
                    # Not in the mapping
                    mapping[(el.tag, hashabledict(el.attrib))] = el
                    # Just add it
                    one.append(el)

def merge_xmls(filenames, output_file_name, destination_folder=None):
    assert isinstance(filenames, list), 'First argument must be a list of filenames.'
    assert len(filenames) > 0, 'List of files to be merged must contain at least one element.'
    if destination_folder is not None:
        assert isinstance(destination_folder, basestring), "Destination folder should be a string."
    assert isinstance(output_file_name, basestring), "Output file name should be a string."
    if not output_file_name.endswith('.xml'):
        output_file_name += '.xml'

    for file in filenames:
        assert file.endswith('.xml'), 'Files should be XML files with extension xml.'
    roots = [et.parse(f).getroot() for f in filenames]
    r = XMLCombiner(roots).combine()
    print '-' * 20

    if destination_folder is not None:
        target_file = os.path.join(destination_folder, output_file_name)
    else:
        target_file = output_file_name

    # write resulting file to path
    with open(target_file, "a+") as f:
        f.seek(0)
        f.truncate()
        r.write(f, xml_declaration=True, encoding='utf-8')
    return r

# this is the exact same class as above, except that only uid attribute is checked when comparing node attribs

class XMLCombiner_UID(object):
    def __init__(self, filenames):
        assert len(filenames) > 0, 'No filenames!'
        # save all the roots, in order, to be processed later
        self.roots = [et.parse(f).getroot() for f in filenames]

    def combine(self):
        for r in self.roots[1:]:
            # combine each element with the first one, and update that
            self.combine_element(self.roots[0], r)
        # return the string representation
        return et.ElementTree(self.roots[0])

    def combine_element(self, one, other):
        """
        This function recursively updates either the text or the children
        of an element if another element is found in `one`, or adds it
        from `other` if not found.
        """

        # Create a mapping from tag name to element, as that's what we are fltering with
        mapping = {(el.tag, hashabledict(dict((k, el.attrib[k]) for k in el.attrib if k=="uID"))): el for el in one}
        # mapping = {(el.tag, hashabledict({"uID":el.get("uID")})): el for el in one if "uID" in el.attrib}
        for el in other:
            if len(el) == 0:
                # Not nested
                try:
                    # Update the text
                    mapping[(el.tag, hashabledict(dict((k, el.attrib[k]) for k in el.attrib if k=="uID")))].text = el.text
                except KeyError:
                    # An element with this name is not in the mapping
                    mapping[(el.tag, hashabledict(dict((k, el.attrib[k]) for k in el.attrib if k=="uID")))] = el
                    # Add it
                    one.append(el)
            else:
                try:
                    # Recursively process the element, and update it in the same way
                    self.combine_element(mapping[(el.tag, hashabledict(dict((k, el.attrib[k]) for k in el.attrib if k=="uID")))], el)
                except KeyError:
                    # Not in the mapping
                    mapping[(el.tag, hashabledict(dict((k, el.attrib[k]) for k in el.attrib if k=="uID")))] = el
                    # Just add it
                    one.append(el)


def main(*args, **kwargs):
    """
    If path is indicated, merger writes the resulting tree to that path. Otherwise, will return element tree.

    :param args:
    :param kwargs:
    :return:
    """


    PATH_TO_FILE = 'Merger-output-loc.xml'

    if 'path' in kwargs:
        path_to_file = kwargs['path']
        assert isinstance(path_to_file, basestring), "Path must be string."
    else:
        path_to_file = None

    sys.stdout.write('\nXML MERGER\n')
    for file in args:
        if file.endswith('.xml'):
            sys.stdout.write('file: ' + file + '\n')
    roots = [et.parse(f).getroot() for f in args]
    r = XMLCombiner(roots).combine()
    print '-' * 20

    if path_to_file is not None:
        # write resulting file to path
        with open(path_to_file, "a+") as f:
            f.seek(0)
            f.truncate()
            r.write(f, xml_declaration=True, encoding='utf-8')
        return

    return r


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('files', nargs='*')
    parser.add_argument('--path')
    args = parser.parse_args()

    if args.path is not None:
        main(*args.files, path=args.path)
    else:
        main(*args.files)
