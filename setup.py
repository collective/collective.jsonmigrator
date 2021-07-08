# -*- coding: utf-8 -*-
"""Installer for the collective.jsonmigrator package."""

from setuptools import find_packages
from setuptools import setup


long_description = '\n\n'.join([
    open('README.rst').read(),
    open('CONTRIBUTORS.rst').read(),
    open('CHANGES.rst').read(),
])


setup(
    name='collective.jsonmigrator',
    version='1.0.2.dev0',
    description="Tool for you to migrate from old Plone sites",
    long_description=long_description,
    # Get more from https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: Addon",
        "Framework :: Plone :: 4.3",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Operating System :: OS Independent",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='plone transmogrifier',
    author='Rok Garbas',
    author_email='rok@garbas.si',
    url='https://github.com/collective/collective.jsonmigrator',
    project_urls={
        'PyPI': 'https://pypi.python.org/pypi/collective.jsonmigrator',
        'Source': 'https://github.com/collective/collective.jsonmigrator',
        'Tracker': 'https://github.com/collective/collective.jsonmigrator/issues',
        # 'Documentation': 'https://collective.jsonmigrator.readthedocs.io/en/latest/',
    },
    license='BSD',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['collective'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    python_requires="==2.7",
    install_requires=[
        'collective.transmogrifier',
        'plone.app.transmogrifier',
        'setuptools',
        'zope.app.container',
    ],
    extras_require={
        'test': [
            'plone.api',
            'plone.app.testing',
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    [console_scripts]
    update_locale = collective.jsonmigrator.locales.update:update_locale
    """,
)
