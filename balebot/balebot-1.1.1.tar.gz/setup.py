import setuptools

setuptools.setup(name='balebot',
                 version='1.1.1',
                 description='python framework for Bale messenger Bot API ',
                 author='elenoon',
                 author_email='balebot@elenoon.ir',
                 license='GNU',
                 install_requires=[
                     'aiohttp',
                     'asyncio',
                     'graypy',
                 ],
                 packages=setuptools.find_packages())
