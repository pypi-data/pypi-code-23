from distutils.core import setup

classifiers = [
    'Programming Language :: Python :: 3',
]

# requirements = []

paramters = {
    'name': 'random_string_generate',
    'packages': ['random_code'],
    'version': '0.01',
    'author': 'minchiuan.gao',
    'author_email': 'minchiuan.gao@gmail.com',
    'url': 'https://github.com/fortymiles',
    'description': 'generate random code',
    # 'install_requires': requirements
}


setup(**paramters)