from setuptools import setup,find_packages
setup(
        name='sinaweibo',
        version='0.3.5',
        description='SinaWeibo',
        author='xjouyi@163.com',
        author_email='xjouyi@163.com',
        url='https://github.com/XJouYi/SinaWeibo',
        packages=find_packages(exclude=['__pycache__','.idea']),
        include_package_data=True,
        install_requires=['requests', 'rsa','beautifulsoup4'],
)