# Copyright 2015-2017 The MathWorks, Inc.

from setuptools import setup
#from distutils.core import setup
#from distutils.command.clean import clean
#from distutils.command.install import install

#class InstallRuntime(install):
#    # Calls the default run command, then deletes the build area 
#    # (equivalent to "setup clean --all").
#    def run(self):
#        install.run(self)
#        c = clean(self.distribution)
#        c.all = True
#        c.finalize_options()
#        c.run()

if __name__ == '__main__':

    setup(
        name="rpi_feature_selection_toolbox",
        version="2.0.4",
        description='',
        author='Keyi Liu, Zijun Cui, Qiang Ji',
        author_email="liuk7@rpi.edu",
        url='https://www.ecse.rpi.edu/~cvrl/',
        platforms=['Linux', 'Windows', 'MacOS'],
        packages=[
            'rpi_feature_selection_toolbox'
        ],
        package_data={'rpi_feature_selection_toolbox': ['*.ctf']},
        # Executes the custom code above in order to delete the build area.
        #cmdclass={'install': InstallRuntime}
    )


