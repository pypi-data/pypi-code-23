from distutils.core import setup


setup(
    name='Taiwanese-Speech-And-Text-Corpus',
    packages=['程式', '程式/全漢全羅', '檢查'],
    package_data={
        '程式': ['全漢全羅/語料/語句文本.txt.gz', ],
    },
    version='0.3.2',
    author='高明達',
    author_email='mtko@iis.sinica.edu.tw',
    url='http://www.iis.sinica.edu.tw/pages/mtko/index_zh.html',
    keywords=[
        'Corpus', '語料庫',
        'Taiwan', 'Taiwanese',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    install_requires=[
        'tai5-uan5-gian5-gi2-kang1-ku7==0.6.32',
        'django',
        'praatIO',
    ],
)
