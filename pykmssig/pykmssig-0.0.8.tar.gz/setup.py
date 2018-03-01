from distutils.core import setup

setup(name="pykmssig",
      version="0.0.8",
      author="Andrew Krug",
      author_email="akrug@mozilla.com",
      packages=["pykmssig"],
      license="MPL",
      description="pykmssig is a utility for signing and verifying files on AWS using the Key Management Service",
      url='https://github.com/mozilla-iam/pykmssig',
      download_url="",
      install_requires=[
        'boto3',
        'cryptography',
        'python-decouple',
        'aws-encryption-sdk',
        'pyblake2'
      ]
  )
