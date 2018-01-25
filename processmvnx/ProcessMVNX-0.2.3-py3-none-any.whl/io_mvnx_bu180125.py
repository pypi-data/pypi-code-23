import numpy as np
import xml.etree.ElementTree as ET
# import sklearn.decomposition as dec
import matplotlib.pyplot as plt
import pickle
import sys
import os
import re


def to_float(s):
    return np.array([float(x) for x in s.split(' ')])


def load_data(fp, silent=False):
    '''
    Reads file and returns dictionary X with data.
    '''
    if silent:
        out = open(os.devnull, 'w')
    else:
        out = sys.stdout

    fp_pkl = fp[:-5] + '.pkl'
    fn = fp.split('/')[-1].split('.')[0]
    print('Loading: {} ...'.format(fn), file=out)
    if os.path.isfile(fp_pkl):
        with open(fp_pkl, 'rb') as f:
            try:
                X = pickle.load(f, encoding='latin1')
            except TypeError:
                X = pickle.load(f)
        print("Loaded from pickled file.", file=out)
    else:
        X = {}
        tree = ET.parse(fp)
        root = tree.getroot()
        prefix = '{http://www.xsens.com/mvn/mvnx}'
        joints = root[2].findall(prefix + 'joints')[0]
        J = [s.attrib for s in joints.getchildren()]
        X['jointIndices'] = {j['label']: range(3*i, 3*(i+1))
                             for (i, j) in enumerate(J)}
        tags = [e.tag for e in root.getchildren()[2][-1][100].getchildren()]
        for s in tags:
            O = tree.findall('.//' + s)
            x = np.array([to_float(o.text) for o in O])
            s = s.split('}', 1)[1]
            X[s] = x
        times = [i.get('ms') for i in root[2][-1]]
        X['times'] = times
        X['jointAngle'] = remove_discontinuities(X['jointAngle'])
        with open(fp_pkl, 'wb') as f:
            pickle.dump(X, f)
    return X


def remove_discontinuities(arr):
    jump_x, jump_joint = np.where(abs(np.diff(arr, axis=0)) > 180)
    gaps = zip(jump_x[:-1:2], jump_x[1::2], jump_joint[1::2])
    for i, j, w in gaps:
        # print(i, j, w)
        # plt.plot(arr[i-50:j+50, w])
        arr[i+1:j+1, w] += 360.
        # plt.plot(arr[i-50:j+50, w])
        # plt.show()
    return arr


class Segment:
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


def bvh_hierarchy(bvh):
    i = 0
    while bvh[i] != 'MOTION\n':
        i += 1
    return bvh[:i].copy()


def parse_bvh(bvh):
    """
    Takes bvh-file as list of strings, and returns the segments
    with skeleton hierarchy
    """
    scanner = make_scanner()
    segments = []
    prev = None
    i = 0
    seg_count = 0
    bracket_count = 0
    after_endsite = False
    while bvh[i] != 'MOTION\n':
        tokens, _ = scanner.scan(bvh[i])
        if tokens[0][1] in ['ROOT', 'JOINT']:
            name = tokens[1][1]
            seg = Segment(name)
            if tokens[0][1] == 'JOINT':
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


def load_bvh_segments(fp):
    bvh = read_file(fp)
    return parse_bvh(bvh)


def load_bvh_hierarchy(fp):
    bvh = read_file(fp)
    return bvh_hierarchy(bvh)


def read_file(fp):
    with open(fp, 'r') as f:
        fstr = f.readlines()
    return fstr


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
    motion = np.array(motion)
    return motion


def print_skeleton(segments):
    for s in segments:
        print(s.name)
        print('Offset:', s.offset)
        print('Pos:', s.pos)
        if s.end_site is not None:
            print('Endsite:', s.end_site)
        if s.parent is not None:
            print('\tparent:', s.parent.name)
        for c in s.children:
            print('\tchild:', c.name)


def plot3D(t_pos):
    fig = plt.figure()
    from mpl_toolkits.mplot3d import Axes3D
    Axes3D()  # just to satisfy pep8
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(t_pos[:, 0], t_pos[:, 1], t_pos[:, 2])
    return ax


def append2chain(prev, seg_list, t_pos, i, segments):
    name = seg_list[i]['label']
    seg = Segment(name)
    seg.pos = t_pos[i]
    segments.append(seg)
    seg.add_parent(prev)
    if prev is not None:
        prev.add_child(seg)
        seg.offset = seg.pos - seg.parent.pos
    else:
        seg.offset = seg.pos
    prev = seg
    return prev


def read_mvnx(fp):
    tree = ET.parse(fp)
    root = tree.getroot()
    return tree, root


def transform2bvh_coord(x):
    return 100 * x[:, [1, 2, 0]]


def mvnx2skeleton(fp):
    """
    Read mvnx and return skeleton as linked segments.
    """
    fp_skeleton = fp[:-5] + '.skeleton'
    if not os.path.isfile(fp_skeleton):
        tree, root = read_mvnx(fp)
        seg_list = [s.attrib for s in root[2][1].getchildren()]
        # joints_list = [j.attrib for j in root[2][3].getchildren()]
        t_pos = to_float(root.getchildren()[2][-1][0][-1].text).reshape(23, 3)
        # t_pos = 100 * t_pos[:, [1, 2, 0]]
        t_pos = transform2bvh_coord(t_pos)
        t_pos -= t_pos[0]

        segments = []
        prev = None
        for i in range(7):
            prev = append2chain(prev, seg_list, t_pos, i, segments)
        segments[-1].end_site = np.zeros((3,))
        prev = segments[4]
        for i in range(7, 11):
            prev = append2chain(prev, seg_list, t_pos, i, segments)
        segments[-1].end_site = np.zeros((3,))
        prev = segments[4]
        for i in range(11, 15):
            prev = append2chain(prev, seg_list, t_pos, i, segments)
        prev = segments[0]
        segments[-1].end_site = np.zeros((3,))
        for i in range(15, 19):
            prev = append2chain(prev, seg_list, t_pos, i, segments)
        segments[-1].end_site = np.zeros((3,))
        prev = segments[0]
        for i in range(19, 23):
            prev = append2chain(prev, seg_list, t_pos, i, segments)
        segments[-1].end_site = np.zeros((3,))
        with open(fp_skeleton, 'wb') as f:
            pickle.dump(segments, f)
    else:
        with open(fp_skeleton, 'rb') as f:
            segments = pickle.load(f)
    return segments


def write_bvh_from_mvnx(out_name, segments, X_joints):
    rot_str = ' Yrotation Xrotation Zrotation'
    ch_root = 'CHANNELS 6 Xposition Yposition Zposition' + rot_str
    ch_joint = 'CHANNELS 3' + rot_str
    with open(out_name, 'w') as f:
        f.write('HIERARCHY\n')
        for i, s in enumerate(segments):
            if s.parent is None:
                f.write('ROOT ' + s.name + '\n{\n')
                level = ' '
                f.write(level + 'OFFSET ' +
                        '{:.6} {:.6} {:.6}\n'.format(*s.offset))
                f.write(level + ch_root + '\n')
            else:
                f.write(level)
                f.write('JOINT ' + s.name + '\n' + level + '{\n')
                level += ' '
                f.write(level + 'OFFSET ' +
                        '{:.6} {:.6} {:.6}\n'.format(*s.offset))
                f.write(level + ch_joint + '\n')
            if s.end_site is not None:
                f.write(level + 'End Site\n')
                f.write(level + '{\n')
                f.write(level + ' OFFSET ' +
                        '{:.6} {:.6} {:.6}\n'.format(*s.end_site))
                f.write(level + '}\n')
                if i <= len(segments) - 2:
                    joint_root = segments[i+1].parent
                else:
                    level = level[:-1]
                    f.write(level + '}\n')
                    joint_root = segments[0]
                parent = s.parent
                level = level[:-1]
                f.write(level + '}\n')
                while parent != joint_root:
                    level = level[:-1]
                    f.write(level + '}\n')
                    parent = parent.parent
        write_motion(f, X_joints)


def load_olaf_hierarchy():
    data_dir = '/home/benjamin/Data/NaturalMovements/indoor/170324_olaf'
    out_dir = os.path.abspath('../out')
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)
    fn = '170324_olaftest-002.bvh'
    fp = os.path.join(data_dir, fn)
    hierarchy = load_bvh_hierarchy(fp)
    return hierarchy


def write_bvh(out_name, X, hierarchy=None):
    """
    X must have shape: (T, 72)
    """
    if hierarchy is None:
        hierarchy = load_olaf_hierarchy()
    with open(out_name, 'w') as f:
        f.writelines(hierarchy)
        write_motion(f, X)


def write_motion(f, X):
    f.write('MOTION\nFrames: {}\n'.format(X.shape[0]))
    f.write('Frame Time: 0.016667\n')
    for x in X:
        f.write(np.array2string(x, max_line_width=10000,
                                formatter={'float_kind':
                                           lambda x: "%.6f" % x},
                                suppress_small=True)[1:-1] + '\n')


def append_pelvis(x):
    return np.concatenate([np.zeros((x.shape[0], 6)), x], axis=1)


if __name__ == '__main__':
    ddir = '/home/benjamin/Data/indoor/170404_bjoern/'
    fn = 'Session_03-000.mvnx'
    fp = ddir + fn
    X = load_data(fp)

    # # read bvh
    # fp = ddir + 'office_2_bench.bvh'
    # with open(fp, 'r') as f:
    #     bvh = f.readlines()

    fp = ddir + 'Session_03-000.bvh'
    motion = read_bvh_motion(fp)

    x = motion[:85215, 3:]
    x = np.reshape(x, (1235, 69, 69))
