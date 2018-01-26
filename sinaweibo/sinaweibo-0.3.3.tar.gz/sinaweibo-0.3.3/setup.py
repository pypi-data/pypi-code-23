from setuptools import setup,find_packages
setup(
        name='sinaweibo',
        version='0.3.3',
        description='SinaWeibo',
        author='xjouyi@163.com',
        author_email='xjouyi@163.com',
        url='https://github.com/XJouYi/SinaWeibo',
        packages=find_packages(),
        include_package_data=True,
        install_requires=['requests', 'rsa','beautifulsoup4'],
)