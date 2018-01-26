from setuptools import setup,find_packages
setup(
        name='sinaweibo',
        version='0.3.7',
        description='SinaWeibo',
        author='xjouyi@163.com',
        author_email='xjouyi@163.com',
        url='https://github.com/XJouYi/SinaWeibo',
        packages=['SinaWeibo','SinaWeibo.common'],
        include_package_data=True,
        install_requires=['requests', 'rsa','beautifulsoup4'],
)