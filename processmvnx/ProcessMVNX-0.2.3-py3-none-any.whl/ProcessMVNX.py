import os
import numpy as np
import xml.etree.ElementTree as ET
import itertools
import pandas as pd
import transforms3d
import pickle
from ProcessMVNX import bvh_import
from . import bvh_import


def parse_mvnx(fn):
    mvnx = MVNX(fn)
    return mvnx.parse_mvnx()


class MVNX(object):
    def __init__(self, fn):
        self.tree, self.root = read_mvnx(fn)

    def parse_mvnx(self):
        D, tree, root = {}, self.tree, self.root
        prefix = '{http://www.xsens.com/mvn/mvnx}'
        joints = root[2].findall(prefix + 'joints')[0]
        joint_labels = [s.attrib['label'] for s in joints.getchildren()]
        D['jointIndices'] = {j: range(3*i, 3*(i+1))
                            for (i, j) in enumerate(joint_labels)}
        tags = [e.tag for e in root.getchildren()[2][-1][100].getchildren()]
        for s in tags:
            all_data = tree.findall('.//' + s)
            # TODO: this should be avoided. possibly best to read directly into
            # DataFrame
            x = np.array([to_float(o.text) for o in all_data])
            s = s.split('}', 1)[1]
            D[s] = x
        times = [i.get('ms') for i in root[2][-1]]
        D['times'] = times
        D['jointAngle'] = remove_discontinuities(D['jointAngle'])
        return D


def convert_to_axis_angle(x_euler, axes='syzx'):
    x_euler = x_euler.copy()
    x_euler *= np.pi/180
    assert np.abs(x_euler).max() < np.pi
    T, dim = x_euler.shape
    new_dim = dim * 4//3
    x_transform = np.nan * np.empty((T, new_dim))
    i = 0
    for x_row in x_euler:
        a = x_row[0::3]
        b = x_row[1::3]
        c = x_row[2::3]
        tmp = np.empty((new_dim,))
        j = 0
        for ai, aj, ak in zip(a, b, c):
            unit_vector, theta = transforms3d.euler.euler2axangle(ai, aj, ak,
                                                                  axes=axes)
            assert np.allclose(np.linalg.norm(unit_vector), 1)
            tmp[j:j+4] = np.array([theta, *unit_vector])
            j += 4
        x_transform[i] = np.array(tmp)
        i += 1
    return x_transform


def convert_to_euler(x_axisangle, axes='syzx'):
    T, dim = x_axisangle.shape
    new_dim = dim * 3//4
    x_transform = np.nan * np.empty((T, new_dim))
    i = 0
    for x_row in x_axisangle:
        a = x_row[0::4]
        b = x_row[1::4]
        c = x_row[2::4]
        d = x_row[3::4]
        tmp = np.empty((new_dim,))
        j = 0
        for theta, aj, ak, al in zip(a, b, c, d):
            vec = [aj, ak, al]
            theta = transforms3d.euler.axangle2euler(vec, theta,
                                                     axes=axes)
            tmp[j:j+3] = theta
            j += 3
        x_transform[i] = np.array(tmp)
        i += 1
    return x_transform * 180/np.pi


def read_mvnx(fn):
    tree = ET.parse(fn)
    root = tree.getroot()
    return tree, root


def to_float(s):
    # TODO: slow, speed up!
    return np.array([float(x) for x in s.split(' ')])


def remove_discontinuities(arr, unit='deg'):
    circle = 360. if unit == 'deg' else 2*np.pi
    is_discontinuous = abs(np.diff(arr, axis=0)) > circle/2 - 0.1
    jump_loc, jump_deg = np.where(is_discontinuous)
    for deg in set(jump_deg):
        jump_deg_loc = jump_loc[jump_deg == deg]
        start = jump_deg_loc[::2]
        end = jump_deg_loc[1::2]
        even = arr[start[0], deg] > 0
        for s, e in zip(start, end):
            if even:
                arr[s+1:e+1, deg] += 2 * circle
            else:
                arr[s+1:e+1, deg] -= 2 * circle
    # gaps = zip(jump_loc[:-1:2], jump_loc[1::2], jump_deg[1::2])
    # for i, j, w in gaps:
    #     arr[i+1:j+1, w] += circle
    return arr


def load_accelerations(fp='data/indoor.mvnx'):
    rf_name = 'right_foot_acceleration.pkl'
    lf_name = 'left_foot_acceleration.pkl'

    if not os.path.isfile(rf_name):
        # Load data
        mvnx = MVNX(fp)
        data = mvnx.parse_mvnx()
        # prepare multiindex
        sensors = mvnx.root[2][2].getchildren()
        sensor_names = [s.attrib['label'] for s in sensors]
        dat = data['sensorAcceleration']
        idx = list(itertools.product(sensor_names, ['x', 'y', 'z']))
        midx = pd.MultiIndex.from_tuples(idx, names=['sensor', 'coord'])
        # convert to DataFrame
        df = pd.DataFrame(data=dat.T, index=midx)
        left_foot_acc = df.loc['LeftFoot']
        right_foot_acc = df.loc['RightFoot']
        # save as pickle to save time (in class FootAcceleration)
        pd.to_pickle(left_foot_acc, lf_name)
        pd.to_pickle(right_foot_acc, rf_name)
    else:
        print('loading from pkl (reminder: switch to json).')
        left_foot_acc = pd.read_pickle(lf_name)
        right_foot_acc = pd.read_pickle(rf_name)
    return right_foot_acc, left_foot_acc


def mvnx2skeleton(fp):
    """
    Read mvnx and return skeleton as linked segments.
    """
    fp_skeleton = fp[:-5] + '.skeleton'
    if not os.path.isfile(fp_skeleton):
        tree, root = read_mvnx(fp)
        seg_list = [s.attrib for s in root[2][1].getchildren()]
        t_pos = to_float(root.getchildren()[2][-1][0][-1].text).reshape(23, 3)
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


def transform2bvh_coord(x):
    return 100 * x[:, [1, 2, 0]]


def append2chain(prev, seg_list, t_pos, i, segments):
    name = seg_list[i]['label']
    seg = bvh_import.Segment(name)
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


def xyz_to_yzx(x):
    bvh_inds = []
    for i in range(22):
        bvh_inds.append(3 * i + 1)
        bvh_inds.append(3 * i + 2)
        bvh_inds.append(3 * i + 0)
    if len(x.shape) == 1:
        return x[bvh_inds]
    elif len(x.shape) == 2:
        return x[:, bvh_inds]
    else:
        raise IndexError

def write_motion(f, X, append_zeros=True):
    f.write('MOTION\nFrames: {}\n'.format(X.shape[0]))
    f.write('Frame Time: 0.016667\n')
    for x in X:
        if append_zeros:
            x = xyz_to_yzx(x)
            x = np.concatenate([np.zeros((6,)), x])
        f.write(np.array2string(x, max_line_width=10000,
                                formatter={'float_kind':
                                           lambda x: "%.6f" % x},
                                suppress_small=True)[1:-1] + '\n')
