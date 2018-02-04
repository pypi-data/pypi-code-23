from distutils.core import setup
setup(
    name = "video2tfrecord",
    version = "0.1",
    description = "Easily convert RGB video data (e.g. .avi) to the TensorFlow tfrecord file format for training e.g. a NN in TensorFlow.",
    author = "Fabio Ferreira",
    author_email = "fabioferreira@mailbox.org",
    url = "https://ferreirafabio.github.io/",
    download_url = "https://github.com/ferreirafabio/video2tfrecords",
    keywords = ["tensorflow", "neural networks", "tfrecord", "video"],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Multimedia :: Video :: Conversion"
        ],
    long_description = "Easily convert RGB video data (e.g. tested with .avi and .mp4) to the TensorFlow tfrecords file format for training e.g. a NN in TensorFlow. Due to common hardware/GPU RAM limitations in Deep Learning, this implementation allows to limit the number of frames per video to be stored in the tfrecords. The code automatically chooses the frame step size s.t. there is an equal separation distribution of the individual video frames."
)
