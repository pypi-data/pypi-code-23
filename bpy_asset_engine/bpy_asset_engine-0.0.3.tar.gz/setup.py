from setuptools import setup, find_packages

setup(name='bpy_asset_engine',
      version='0.0.3',
      description='Blender Asset Engine Library',
      url='https://gitlab.com/lvxejay/asset_engine',
      author='Jared Webber',
      author_email='info@onelvxe.com',
      license='GNU GPLv3',
      packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
      keywords='blender bpy asset engine pipeline',
      python_requires='~=3.5',
      package_data={
            # If any package contains *.txt or *.rst files, include them:
            # '': ['*.txt', '*.rst'],
            #  And include any *.msg files found in the 'hello' package, too:
            # 'hello': ['*.msg'],
            'path_lib': ['*.txt']
      },
      #install_requires=['setuptools', 'wheel', 'requests', 'numpy'],
      zip_safe=False)