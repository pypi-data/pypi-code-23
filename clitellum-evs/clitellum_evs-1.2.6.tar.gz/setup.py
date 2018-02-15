from setuptools import setup

setup(
    name='clitellum_evs',
    version='1.2.6',
    packages=['clitellum_evs', 'clitellum_evs.rejection'],
    package_dir={'clitellum_evs': 'src'},
    url='https://gitlab.com/clitellum/clitellum_evs/wikis/home',
    license='APACHE',
    author='Sergio.Bermudez',
    author_email='sbermudezlozano@gmail.com',
    description='Event Sourcing Library',
    keywords="clitellum event sourcing eventsourcing",
    extras_require={
    },
    install_requires=['pymongo']
)
