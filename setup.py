# -*- coding:utf-8 -*-
from setuptools import setup
from setuptools import find_packages


version = '0.4'
description = "JSON based migrations for Plone"

requirements = [
    'setuptools',
    'collective.transmogrifier',
    'plone.app.transmogrifier',
    'zope.app.container',
]

try:
    import json
except ImportError:
    requirements.append('simplejson')


setup(
    name='collective.jsonmigrator',
    version=version,
    description=description,
    long_description="%s\n%s" % (
        open("README.rst").read(),
        open("CHANGES.rst").read(),
    ),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='plone transmogrifier ',
    author='Rok Garbas',
    author_email='rok@garbas.si',
    url='https://github.com/collective/collective.jsonmigrator',
    license='BSD',
    packages=find_packages(),
    namespace_packages=['collective'],
    include_package_data=True,
    zip_safe=False,
    install_requires=requirements,
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """
)
