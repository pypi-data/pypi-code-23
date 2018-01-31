
def _get_version(version_info):
    dic = {'alpha': 'a',
           'beta': 'b',
           'candidate': 'rc',
           'final': ''}
    vi = version_info
    specifier = '' if vi[3] == 'final' else dic[vi[3]] + str(vi[4])
    version = '%s.%s.%s%s' % (vi[0], vi[1], vi[2], specifier)
    return version


# meta data

__name__ = 'jupyter_widget_d3_slider'
name_url = __name__.replace('_', '-')

version_info = (0, 1, 9, 'final', 0)
__version__ = _get_version(version_info)

__description__ = 'd3 based slider Jupyter Widget - for demo'
__long_description__ = 'See repo README'
__author__ = 'oscar6echo'
__author_email__ = 'olivier.borderies@gmail.com'
__url__ = 'https://gitlab.com/{}/{}'.format(__author__,
                                            name_url)
__download_url__ = 'https://gitlab.com/{}/{}/repository/archive.tar.gz?ref={}'.format(__author__,
                                                                                      name_url,
                                                                                      __version__)
__keywords__ = ['jupyter-widget', 'd3', 'slider']
__license__ = 'MIT'
__classifiers__ = ['Development Status :: 4 - Beta',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python :: 3.5',
                   'Programming Language :: Python :: 3.6'
                   ]
__include_package_data__ = True
__data_files__ = [
    ('share/jupyter/nbextensions/jupyter-widget-d3-slider', [
        'jupyter_widget_d3_slider/static/extension.js',
        'jupyter_widget_d3_slider/static/index.js',
        'jupyter_widget_d3_slider/static/index.js.map',
    ]),
    # auto enable active for notebook>=5.3
    ('etc/jupyter/nbconfig/notebook.d', [
        'enable_d3_slider.json'
    ])
]
__zip_safe__ = False
