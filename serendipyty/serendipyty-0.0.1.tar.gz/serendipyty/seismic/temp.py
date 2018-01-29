extension_config = {'pysit.solvers.constant_density_acoustic.time.scalar._constant_density_acoustic_time_scalar_cpp' :
                          { 'sources' : [os.path.join('/w04d2/bfilippo/serendipyty-project/serendipyty/serendipyty/seismic', 'pysit','solvers','constant_density_acoustic','time','scalar','solvers_wrap.cxx')],
                            'extra_compile_args' :  ["-O3","-fopenmp","-ffast-math"],
                            'include_dirs' : [np.get_include(), os.path.join('/w04d2/bfilippo/serendipyty-project/serendipyty/serendipyty/seismic', 'pysit','solvers','fd_tools')],
                            'libraries' :  ['gomp'],
                            'library_dirs' : ['/usr/lib64']
                          },
}
