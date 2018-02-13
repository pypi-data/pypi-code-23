from setuptools import setup
setup(
  name = 'imagetyperzapi3',
  packages = ['imagetyperzapi3'], # this must be the same as the name above
  version = '0.2',
  description = 'ImagetyperzAPI Python3 - is a super easy to use bypass captcha API wrapper for imagetyperz.com captcha service',
  author = 'Imagetyperz Dev',
  author_email = 'imagetyperz@gmail.com',
  url = 'https://github.com/imagetyperz-api/imagetyperz-api-python3', # use the URL to the github repo
  download_url = 'https://github.com/imagetyperz-api/imagetyperz-api-python3/archive/0.1.tar.gz', # create git tag and push to get archive
  keywords = ['captcha', 'bypasscaptcha', 'decaptcher', 'decaptcha', '2captcha', 'deathbycaptcha', 'anticaptcha'], # arbitrary keywords
  classifiers = [],
  install_requires=['requests'], # Optional
  license='MIT',
  python_requires='==3.*'
)
