from setuptools import setup

setup(
    name='imagetyperzapi2',
    packages=['imagetyperzapi2'],  # this must be the same as the name above
    version='0.3',
    description='ImagetyperzAPI Python2 - is a super easy to use bypass captcha API wrapper for imagetyperz.com captcha service',
    author='Imagetyperz Dev',
    author_email='imagetyperz@gmail.com',
    url='https://github.com/imagetyperz-api/imagetyperz-api-python2',  # use the URL to the github repo
    download_url='https://github.com/imagetyperz-api/imagetyperz-api-python2/archive/0.1.tar.gz',
    # create git tag and push to get archive
    keywords=["captcha", "bypasscaptcha", "decaptcher", "decaptcha", "2captcha", "deathbycaptcha", "anticaptcha",
              "bypass recaptcha v2", "bypass no captcha recaptcha", "bypass invisible recaptcha",
              "captcha services for recaptcha v2", "recaptcha v2 captcha solver", "google recaptcha solver",
              "recaptcha solver python", "recaptcha bypass script"],
    classifiers=[],
    install_requires=['requests'],  # Optional
    license='MIT',
    python_requires='==2.7.*'
)
