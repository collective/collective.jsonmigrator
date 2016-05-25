# -*- coding:utf-8 -*-
from setuptools import setup
from setuptools import find_packages
from sys import version_info


version = '0.5.dev0'
description = "JSON based migrations for Plone"

requirements = [
    'setuptools',
    'collective.transmogrifier',
    'zope.app.container',
]

if version_info[0] == 2 and version_info[1] < 6:
    # If this happens you are probably using Python 2.4
    # According to the documentation of simplejson, since version 2.1.0,
    # Python 2.4 is no longer supported but may still work
    # This line will probably pull in simplejson 2.3.3
    requirements.append('simplejson < 2.4')
    # To my knowledge 1.3 work fine
    requirements.append('plone.app.transmogrifier < 1.4')
else:
    requirements.append('plone.app.transmogrifier')


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
