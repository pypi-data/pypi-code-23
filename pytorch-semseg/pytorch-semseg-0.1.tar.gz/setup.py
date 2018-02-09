from setuptools import find_packages, setup, Command

setup(name='pytorch-semseg',
      version='0.1',
      description='Semantic Segmentation Architectures implemented in PyTorch',
      classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
      ],
      keywords='semantic-segmentation, fully-convolutional-networks, deep-learning, pytorch',
      url='http://github.com/meetshah1995/pytorch-semseg',
      download_url='https://github.com/meetshah1995/pytorch-semseg/archive/0.1.tar.gz',
      author='Meet Pragnesh Shah',
      author_email='meetshah1995@gmail.com',
      license='MIT',
      packages=['ptsemseg'],
      install_requires=['matplotlib', 'numpy', 'scipy', 'torch', 'torchvision', 'tqdm', 'visdom', 'pydensecrf'],
      zip_safe=False,)