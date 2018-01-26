from setuptools import setup,find_packages
setup(
        name='SinaWeibo',
        version='0.3',
        description='SinaWeibo',
        author='xjouyi@163.com',
        author_email='xjouyi@163.com',
        url='https://github.com/XJouYi/SinaWeibo',
        packages=find_packages(),
        install_requires=['requests', 'rsa','beautifulsoup4'],
)