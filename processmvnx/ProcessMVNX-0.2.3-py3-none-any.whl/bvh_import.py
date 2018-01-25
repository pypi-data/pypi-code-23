import ProcessMVNX as mvnx
from . import bvh_import as bvh
import numpy as np
import re


class BVHHandler(object):
    def __init__(self, fn):
        self.joints, self.pelvis = bvh.read_bvh_motion(fn)
        self.dict = {i: j for i, j in enumerate(bvh.get_joints(fn))}
        self.fn = fn

    def write_bvh(self, mov, of='out.bvh'):
        with open(self.fn, 'r') as f:
            bvh = f.readlines()
        with open(of, 'w') as out:
            for line in bvh:
                if line != 'MOTION\n':
                    out.write(line)
                else:
                    break
            mvnx.write_motion(out, mov, append_zeros=False)


class Segment:
    """
    Represents Bodypart as Element of doubly linked list.
    """
    def __init__(self, name):
        self.name = name
        self.parent = None
        self.children = []
        self.offset = None
        self.channels = None
        self.end_site = None
        self.pos = None

    def __repr__(self):
        msg = 'Segment "{}" with children:\n'.format(self.name)
        for c in self.children:
            msg += c.name + ' '
        return msg

    def add_parent(self, parent):
        self.parent = parent

    def set_offset(self, offset):
        self.offset = offset
        abs_pos = offset.copy()
        parent = self.parent
        while parent is not None:
            if self.name == 'Chest2':
                pass
            abs_pos += parent.offset
            parent = parent.parent
        self.pos = abs_pos

    def add_child(self, child):
        self.children.append(child)


def get_joints(fp):
    with open(fp, 'r') as f:
        bvh = f.readlines()
    scanner = make_scanner()
    jointnames = []
    i = 0
    while bvh[i] != 'MOTION\n':
        tokens, _ = scanner.scan(bvh[i])
        match, keyword = tokens[0]
        if keyword == 'JOINT':
            name = tokens[1][1]
            jointnames.append(name)
        i += 1
    return jointnames


def parse_bvh(bvh):
    """
    Takes bvh-file as list of strings, and returns the segments
    with skeleton hierarchy. (Until now only one hierarchy.)
    """
    scanner = make_scanner()
    prev = None
    i, seg_count, bracket_count = 0, 0, 0
    after_endsite = False
    while bvh[i] != 'MOTION\n':
        tokens, _ = scanner.scan(bvh[i])
        match, keyword = tokens[0]
        if keyword == 'ROOT':
            name = tokens[1][1]
            seg = Segment(name)
            segments = [seg]
            seg_count += 1
        elif keyword == 'JOINT':
            name = tokens[1][1]
            seg = Segment(name)
            prev = segments[seg_count-1]
            if after_endsite:
                for j in range(bracket_count-1):
                    prev = prev.parent
                after_endsite = False
            seg.add_parent(prev)
            prev.add_child(seg)
            segments.append(seg)
            seg_count += 1
        elif tokens[0][1] == 'OFFSET':
            offset = []
            for t in tokens:
                if t[0] == 'DIGIT':
                    offset.append(float(t[1]))
            if not after_endsite:
                seg.set_offset(np.array(offset))
            else:
                seg.end_site = np.array(offset)
        elif tokens[0][1] == 'End':
            bracket_count = 0
            after_endsite = True
        elif tokens[0][0] == 'CLOSE_BRACE':
            bracket_count += 1
        i += 1
    return segments


def make_scanner():
    def identifier(scanner, token): return 'IDENT', token

    def digit(scanner, token): return 'DIGIT', token

    def open_brace(scanner, token): return 'OPEN_BRACE', token

    def close_brace(scanner, token): return 'CLOSE_BRACE', token
    scanner = re.Scanner([
        ('[a-zA-Z_]\w*', identifier),
        ('-*[0-9]+(\.[0-9]+)?', digit),
        ('}', close_brace),
        ('{', open_brace),
        (':', None),
        ('\s+', None),  # remove whitespace et al
    ])
    return scanner


def read_bvh_motion(fp):
    bvh = read_file(fp)
    for i in range(1000):
        if bvh[i] == 'MOTION\n':
            break
    motion_start = i + 3
    motion = []
    for i in range(motion_start, len(bvh)):
        data = np.array([float(b) for b in bvh[i][:-1].split(' ')])
        motion.append(data)
    joints = np.array(motion)[:, 6:]
    pelvis = np.array(motion)[:, :6]
    return joints, pelvis


def read_file(fp):
    with open(fp, 'r') as f:
        fstr = f.readlines()
    return fstr
