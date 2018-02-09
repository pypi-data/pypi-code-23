from setuptools import find_packages, setup, Command
import pypandoc

try:
    long_description = pypandoc.convert('README.md', 'rst')
    long_description = long_description.replace("\r","") # Do not forget this line
except OSError:
    print("Pandoc not found. Long_description conversion failure.")
    import io
    # pandoc is not installed, fallback to using raw contents
    with io.open('README.md', encoding="utf-8") as f:
        long_description = f.read()

setup(name='pytorch-semseg',
      version='0.1.1',
      description='Semantic Segmentation Architectures implemented in PyTorch',
      classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
      ],
      keywords='semantic-segmentation, fully-convolutional-networks, deep-learning, pytorch',
      url='https://github.com/meetshah1995/pytorch-semseg',
      author='Meet Pragnesh Shah',
      long_description=long_description,
      author_email='meetshah1995@gmail.com',
      license='MIT',
      packages=['ptsemseg'],
      install_requires=['matplotlib', 'numpy', 'scipy', 'torch', 'torchvision', 'tqdm', 'visdom', 'pydensecrf'],
      zip_safe=False,)