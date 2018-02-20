from distutils.core import setup

setup(
  name = 'pDtlabCsCovea',
  packages = ['pDtlabCsCovea'], # this must be the same as the name above
  version = '2.1',
  description = 'Package Datalab Covea',
  author='covea datalab team',
  author_email='dtlab-team@getnada.com',
)

proxies = {
  "http": "http://px-internet.maafprod.e-corail.com:80",
  "https": "https://px-internet.maafprod.e-corail.com:80",
}

