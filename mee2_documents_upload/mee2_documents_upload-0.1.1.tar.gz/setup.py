from setuptools import setup

setup(
    name='mee2_documents_upload',
    version='0.1.1',
    author="Marcel Fernandez / Sebastian Kutsch",
    scripts=['document_upload.py'],
    install_requires=[
          'mysqlclient',
          'pickle',
          'pathlib']
)
