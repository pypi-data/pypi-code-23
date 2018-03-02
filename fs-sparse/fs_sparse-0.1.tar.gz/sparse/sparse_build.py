#
# This is the main build file
# after this script is run, it will generate a source file _sparse.c
# which will be compiled into regular C extension
#
import cffi

ffibuilder = cffi.FFI()

C_SRC = """
#include "Python.h"
#include <sys/types.h>
#include <unistd.h>
off_t lseek(int fd, off_t offset, int whence);
"""

#
# there are two things we need to call
#
# - ffibuilder.set_source()
# - ffibuilder.cdef()
#

ffibuilder.set_source("sparse._sparse",
        r"""

        // this is to pass to real C compiler
        // it should contain implementations of things declared in cdef()
        // since we don't have to implement anything, we just pass header info.
        #ifndef _GNU_SOURCE
        #define _GNU_SOURCE
        #endif

        #ifndef _LARGEFILE64_SOURCE
        #define _LARGEFILE64_SOURCE
        #endif

        #include <Python.h>
        #include <sys/types.h>
        #include <sys/stat.h>
        #include <fcntl.h>
        #include <unistd.h>
       """,
       libraries=['c']    # link with C library
)

ffibuilder.cdef("""
        // ask cffi to find out these defs
        #define O_RDONLY ...
        #define SEEK_HOLE ...
        #define SEEK_DATA ...

        // inform cffi that mode_t and off_t are of SOME integer type
        typedef int... off_t;
        typedef int... mode_t;

        // function declarations
        int open(const char * pathname, mode_t mode);
        off_t lseek(int fd, off_t offset, int whence);
        int close(int fd);

        """)


if __name__ == '__main__':
    ffibuilder.compile(verbose=True)
