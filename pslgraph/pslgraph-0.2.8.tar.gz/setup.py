import setuptools

setuptools.setup(
    name = 'pslgraph',

    version = '0.2.8',

    description = 'Graph and PSL based TA1 primitive for D3M',
    long_description = 'Graph and PSL based TA1 primitive for D3M',
    keywords='d3m_primitive',

    maintainer_email = 'eaugusti@ucsc.edu',
    maintainer = 'Eriq Augustine',

    # The project's main homepage.
    url = 'https://gitlab.datadrivendiscovery.org/dhartnett/psl',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        'Programming Language :: Python :: 3.6',
    ],

    packages = setuptools.find_packages(exclude = ['contrib', 'docs', 'tests']),
    include_package_data = True,
    package_data = {
        'pslgraph.psl-cli': [
            'psl-cli-CANARY-2.1.1.jar',
            'link_prediction.data',
            'link_prediction.psl'
        ]
    },

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires = [
        'networkx', 'pandas>=0.20.1', 'sklearn', 'psutil'
    ],

    python_requires = '>=3.6',

    entry_points = {
        'd3m.primitives': [
            'pslgraph.GraphMatchingParser = pslgraph.graph_matching:GraphMatchingParser',
            'pslgraph.CollaborativeFilteringParser = pslgraph.collaborative_filtering:CollaborativeFilteringParser',
            'pslgraph.GraphTransformer = pslgraph.graph_transform:GraphTransformer',
            'pslgraph.LinkPrediction = pslgraph.link_prediction:LinkPrediction',
            'pslgraph.GraphMatchingLinkPrediction = pslgraph.graph_matching_link_prediction:GraphMatchingLinkPrediction',
            'pslgraph.CollaborativeFilteringLinkPrediction = pslgraph.collaborative_filtering_link_prediction:CollaborativeFilteringLinkPrediction'
        ]
    }
)
