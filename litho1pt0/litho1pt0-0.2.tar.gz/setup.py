from setuptools import setup, find_packages

# interface for Renka's algorithm 772 fortran code
# ext = Extension(name  = '_stripy',
#                 sources       = ['_stripy.pyf','_stripy.f90'])

if __name__ == "__main__":
    setup(name = 'litho1pt0',
          author            = "LM",
          author_email      = "louis.moresi@unimelb.edu.au",
          url               = "https://github.com/University-of-Melbourne-Geodynamics/litho1pt0",
          download_url      = "",
          version           = "0.2",
          description       = "Python interface to Litho 1.0 dataset - needs stripy",
          packages          = ['litho1pt0'],
          package_dir       = {'litho1pt0': 'litho1pt0'},
          package_data      = {'litho1pt0': ['data/*.npz'] },
          install_requires=['stripy'],



          )


