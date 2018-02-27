import mpi_map
import numpy as np
import numpy.random as npr
import logging

def mul(A, b):
    import numpy as np
    return np.dot(A,b.T).T

if __name__ == '__main__':
    A = npr.randn(10000,3000)
    b = npr.randn(10000,3000)
    # A = npr.randn(100000,3000)
    # b = npr.randn(10,3000)

    mpi_pool = mpi_map.MPI_Pool_v2()
    mpi_pool.start(3, log_level=logging.INFO)
    try:
        mpi_pool.mod_import( set([(None, 'numpy', 'np')]) )

        # Allocate A in distributed memory
        print("Populating distributed memory")
        mpi_pool.alloc_dmem(A=A)

        # Perform multiplication
        print("Map-dot")
        obj_scatter = mpi_pool.split_data( [b], ['b'] )
        dmem_key_in_list = ['A']
        dmem_arg_in_list = ['A']
        Ab_list = mpi_pool.map(mul, obj_scatter=obj_scatter,
                               dmem_key_in_list=dmem_key_in_list,
                               dmem_arg_in_list=dmem_arg_in_list)
        Ab = np.vstack(Ab_list)
        assert np.all(np.equal(Ab, mul(A, b)))

        # Pop out the matrix A
        print("Pop matrix")
        vals = mpi_pool.pop_dmem('A')
        assert all([ np.all(np.equal(A, A1)) for (A1,) in vals ])

        print("Success")
    finally:
        mpi_pool.stop()