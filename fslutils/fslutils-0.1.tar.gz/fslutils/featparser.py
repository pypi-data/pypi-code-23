""" Parser for FEAT designs
"""

from re import compile as rcomp, VERBOSE

import numpy as np

_DEF_RE = rcomp(
    r"""set \ (?P<top_name>[A-Za-z0-9_]+)
    \((?P<field>[A-Za-z0-9_.]+)\)
    \ (?P<content>.*)""",
    VERBOSE)

_MAT_RE = rcomp(
    r"""/(?P<field>[A-Za-z0-9_]+)
    \s+(?P<content>.*)""",
    VERBOSE)


def _to_bool(val):
    return bool(int(val))


_TOP_TYPES = {
    'fmri': dict,
    'feat_files': list,
    'initial_highres_files': list,
    'highres_files': list,
}


_CONVERTERS = {
    'version': str,
    'inmelodic': _to_bool,
    'level': int,
    'npts': int,
    'ndelete': int,
    'analysis': int,
    'st': int,
    'smooth': float,
    'tr': float,
    'ncon_orig': int,
    'ncon_real': int,
    'nftests_orig': int,
    'nftests_real': int,
    'ncopeinputs': int,
    'paradigm_hp': float,
    'totalVoxels': int,
    'regstandard_nonlinear_warpres': int,
    'multiple': int,
    'z_thresh': float,
    'prob_thresh': float,
    'mixed_yn': int,  # othewise will be forced to bool below
}

_CONVERTER_REGEXPS = (
    (rcomp(r'_yn(\d+)?$'), _to_bool),
    (rcomp(r'^groupmem\.\d+'), int),
    (rcomp(r'^con_real\d+\.\d+'), float),
    (rcomp(r'^con_orig\d+\.\d+'), float),
    (rcomp(r'^evg\d+\.\d+'), float),
    (rcomp(r'^shape\d+'), int),
    (rcomp(r'^convolve\d+'), int),
    (rcomp(r'^convolve_phase\d+'), float),
)


def _infer_converter(field_name):
    if field_name in _CONVERTERS:
        return _CONVERTERS[field_name]
    for regexp, converter in _CONVERTER_REGEXPS:
        match = regexp.search(field_name)
        if match is not None:
            return converter
    return str


def _process_fsf_line(line, out_dict):
    match = _DEF_RE.match(line)
    if match is None:
        return
    top_name, field_name, contents = match.groups()
    if (contents[0], contents[-1]) == ('"', '"'):
        contents = contents[1:-1]
    if top_name not in out_dict:
        out_dict[top_name] = _TOP_TYPES[top_name]()
    try:
        field_name = int(field_name) - 1
    except ValueError:
        contents = _infer_converter(field_name)(contents)
        out_dict[top_name][field_name] = contents
        return
    else:
        # List element
        assert len(out_dict[top_name]) == field_name
        out_dict[top_name].append(contents)


def fsf_to_dict(fsf):
    """ Parse FSF design file in string `fsf` to dictionary

    Parameters
    ----------
    fsf : str
        String containing contents of FSF design file.

    Returns
    -------
    fsf_dict : dict
        Dict containing contents of FSF file.
    """
    fsf_dict = {}
    for line in fsf.splitlines():
        _process_fsf_line(line, fsf_dict)
    return fsf_dict


def _process_mat_line(line):
    field_name, contents = _MAT_RE.match(line).groups()
    converter = float if '.' in contents else int
    contents = [converter(v) for v in contents.split()]
    return field_name, contents if len(contents) > 1 else contents[0]


def mat_to_dict(mat):
    """ Parse FSF design matrix file in string `mat`, return as dict

    Parameters
    ----------
    mat : str
        String containing contents of .mat design matrix file.

    Returns
    -------
    mat_dict : dict
        Dict containing contents of mat file.
    """
    mat_dict = {}
    state = 'getfields'
    mat_lines = []
    for line in mat.splitlines():
        line = line.strip()
        if line == '':
            continue
        if state == 'matrix':
            assert not line.startswith('/')
            mat_lines.append([float(v) for v in line.split()])
            continue
        assert state == 'getfields'
        assert line.startswith('/')
        if line == '/Matrix':
            state = 'matrix'
            continue
        field_name, contents = _process_mat_line(line)
        mat_dict[field_name] = contents
    mat_dict['Matrix'] = np.array(mat_lines)
    return mat_dict
