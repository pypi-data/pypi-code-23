from setuptools import setup, find_packages
import os

#long_description = open('README.md').read()

def main():
    print(os.getcwd())
    setup(
        name='lyricscorpora',
        version='0.2.0',
        description='Lyrics API',
        long_description='Lyrics API',
        packages=find_packages(),
        include_package_data=True,
        package_data = {
                "": [
                    "*.txt",
                    "*.md",
                    "*.rst",
                    "*.py"
                ]
            },
        install_requires=['billboard.py', 'requests', 'bs4'],
        url='https://github.com/edwardseley/lyrics-corpora',
        author='Edward Seley',
        author_email='edwardseley@gmail.com',
        license='No license',
        py_modules=['lyricscorpora'],
        scripts=['lyricscorpora.py'],
        classifiers=[
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 3',
            'License :: OSI Approved :: BSD License',
            'Development Status :: 4 - Beta',
            'Topic :: Multimedia :: Sound/Audio',
            'Natural Language :: English',
        ],
        keywords='lyrics LyricWikia music billboard songs scrape',
        entry_points={
            'console_scripts': [
                'lyricscorpora=lyricscorpora:main',
            ],
        },
        zip_safe=False
    )


if __name__ == "__main__":
    main()