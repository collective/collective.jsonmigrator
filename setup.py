from setuptools import setup
from setuptools import find_packages

version = '0.2'

setup(
    name='collective.jsonmigrator',
    version=version,
    description="Migrations from legacy Plone sites (2.0, 2.1, 2.5) to Plone 4.0",
    long_description=open("README.rst").read(),
    # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
    keywords='plone transmogrifier ',
    author='Rok Garbas',
    author_email='rok@garbas.si',
    url='https://github.com/collective/',
    license='BSD',
    packages=find_packages(),
    namespace_packages=['collective'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'simplejson',
        'collective.transmogrifier',
        'plone.app.transmogrifier',
        'zope.app.container',
        ],
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
    )
