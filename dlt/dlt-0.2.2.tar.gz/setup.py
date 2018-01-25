from setuptools import setup

setup(
    name='dlt',
    version='0.2.2',
    packages=['dlt'],
    url='https://github.com/hiroyuki827/deep_learning_tools',
    license='MIT',
    author='David Walz',
    maintainer='Hioyuki Fuchiue',
    maintainer_email='hiroyuki.fuchiue.827@gmail.com',
    description='The  package to visualize the result for the learners of the deep learning ',
    install_requires=["tensorflow", "keras", "Numpy", "scikit-learn", "matplotlib"],
    classifiers=[
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        "Programming Language :: Python",
        'License :: OSI Approved :: MIT License',
    ],
)
