import numpy as np
import scipy.sparse

def save_sparse_matrix(hdf5_file, group_name, matrix):
    """Saves a scipy sparse matrix to a hdf5 file's group.

    Parameters
    ----------
    hdf5_file : h5py.File
        File used for saving
    group_name : str
        Name of the group in the hdf5 file where we save the matrix 
    matrix : scipy.sparse.spmatrix
        Matrix to be saved
    """
    if isinstance(matrix, (scipy.sparse.dok_matrix, scipy.sparse.lil_matrix)):
        raise TypeError("Saving for DOK and LIL matrices not implemented")

    grp = hdf5_file.create_group(group_name)
    if isinstance(matrix, scipy.sparse.bsr_matrix):
        _save_bsr_matrix(grp, matrix)
    elif isinstance(matrix, scipy.sparse.coo_matrix):
        _save_coo_matrix(grp, matrix)
    elif isinstance(matrix, scipy.sparse.csc_matrix):
        _save_csc_matrix(grp, matrix)
    elif isinstance(matrix, scipy.sparse.csr_matrix):
        _save_csr_matrix(grp, matrix)
    elif isinstance(matrix, scipy.sparse.dia_matrix):
        _save_dia_matrix(grp, matrix)
    else:
        raise RuntimeError("Matrix type not understood. This should not\
                           happen!")

def load_sparse_matrix(grp):
    """
    Loads a matrix from hdf5-group and constructs the corresponding
    scipy.sparse.spmatrix

    Parameters
    ---------
    grp : hdf5-group
        group where the matrix was saved with `save_sparse_matrix`

    Returns
    -------
    the corresponding sparse matrix
    """
    try:
        sparse_matrix_type = grp['sparse_matrix_type'].value
    except:
        raise RuntimeError("Given hdf5-group doesn't seem to contain a sparse\
                           matrix")
    if sparse_matrix_type == 'bsr':
        mat = _load_bsr_matrix(grp)
    elif sparse_matrix_type == 'coo':
        mat = _load_coo_matrix(grp)
    elif sparse_matrix_type == 'csc':
        mat = _load_csc_matrix(grp)
    elif sparse_matrix_type == 'csr':
        mat = _load_csr_matrix(grp)
    elif sparse_matrix_type == 'dia':
        mat = _load_dia_matrix(grp)
    else:
        raise RuntimeError("Matrix type not understood. Should not happen!")

    return mat


def _save_bsr_matrix(grp, matrix):
    """Saves a scipy.sparse.bsr_matrix to a hdf5 group"""
    assert isinstance(matrix, scipy.sparse.bsr_matrix)

    grp["dtype"] = matrix.dtype
    grp["shape"] = matrix.shape
    grp["ndim"] = matrix.ndim
    grp["nnz"] = matrix.nnz
    grp["data"] = matrix.data
    grp["indices"] = matrix.indices
    grp["indptr"] = matrix.indptr
    grp["blocksize"] = matrix.blocksize
    grp["has_sorted_indices"] = matrix.has_sorted_indices
    grp["sparse_matrix_type"] = "bsr"

def _load_bsr_matrix(grp):
    """Loads a scipy.sparse.bsr_matrix from a hdf5 group
    saved by _save_bsr_matrix"""
    assert grp['sparse_matrix_type'].value == 'bsr'
    return scipy.sparse.bsr_matrix((grp['data'], grp['indices'],
                                    grp['indptr']), shape=grp['shape'],
                                    blocksize = grp['blocksize'], 
                                    dtype=grp['dtype'].dtype)

def _save_coo_matrix(grp, matrix):
    assert isinstance(matrix, scipy.sparse.coo_matrix)

    grp["dtype"] = matrix.dtype
    grp["shape"] = matrix.shape
    grp["ndim"] = matrix.ndim
    grp['nnz'] = matrix.nnz
    grp['data'] = matrix.data
    grp['row'] = matrix.row
    grp['col'] = matrix.col
    grp['sparse_matrix_type'] = 'coo' 

def _load_coo_matrix(grp):
    assert grp['sparse_matrix_type'].value == 'coo'
    return scipy.sparse.coo_matrix((grp['data'], (grp['row'], grp['col'])),
                                   shape=grp['shape'],
                                   dtype=grp['dtype'].dtype)

def _save_csc_matrix(grp, matrix):
    assert isinstance(matrix, scipy.sparse.csc_matrix)

    grp["dtype"] = matrix.dtype
    grp["shape"] = matrix.shape
    grp["ndim"] = matrix.ndim
    grp["nnz"] = matrix.nnz
    grp["data"] = matrix.data
    grp["indices"] = matrix.indices
    grp["indptr"] = matrix.indptr
    grp["has_sorted_indices"] = matrix.has_sorted_indices
    grp["sparse_matrix_type"] = "csc"

def _load_csc_matrix(grp):
    assert grp['sparse_matrix_type'].value == 'csc'

    return scipy.sparse.csc_matrix((grp['data'], grp['indices'],
                                    grp['indptr']), shape=grp['shape'],
                                   dtype=grp['dtype'].dtype)

def _save_csr_matrix(grp, matrix):
    assert isinstance(matrix, scipy.sparse.csr_matrix)

    grp["dtype"] = matrix.dtype
    grp["shape"] = matrix.shape
    grp["ndim"] = matrix.ndim
    grp["nnz"] = matrix.nnz
    grp["data"] = matrix.data
    grp["indices"] = matrix.indices
    grp["indptr"] = matrix.indptr
    grp["has_sorted_indices"] = matrix.has_sorted_indices
    grp["sparse_matrix_type"] = "csr"

def _load_csr_matrix(grp):
    assert grp['sparse_matrix_type'].value == 'csr'

    return scipy.sparse.csr_matrix((grp['data'], grp['indices'],
                                    grp['indptr']), shape=grp['shape'],
                                   dtype=grp['dtype'].dtype)

def _save_dia_matrix(grp, matrix):
    assert isinstance(matrix, scipy.sparse.dia_matrix)

    grp["dtype"] = matrix.dtype
    grp["shape"] = matrix.shape
    grp["ndim"] = matrix.ndim
    grp["nnz"] = matrix.nnz
    grp["data"] = matrix.data
    grp["offsets"] = matrix.offsets
    grp["sparse_matrix_type"] = 'dia'

def _load_dia_matrix(grp):
    assert grp['sparse_matrix_type'].value == 'dia'

    return scipy.sparse.dia_matrix((grp['data'], grp['offsets']), 
                                   shape=grp['shape'],
                                   dtype=grp['dtype'].dtype)

_real_types = (np.int8, np.int16, np.int32, np.int64,
               np.float16, np.float32, np.float64, int, float)


def is_numpy_array_of_reals(x):
    return x.dtype in _real_types if isinstance(x, np.ndarray) else False
