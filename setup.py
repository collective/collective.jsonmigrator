from pathlib import Path
from setuptools import find_packages
from setuptools import setup


long_description = f"""
{Path("README.md").read_text()}\n
{Path("CONTRIBUTORS.md").read_text()}\n
{Path("CHANGES.md").read_text()}\n
"""


setup(
    name="collective.jsonmigrator",
    version="3.0.1",
    description="Tool for you to migrate from old Plone sites",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # Get more from https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Plone :: 5.2",
        "Framework :: Plone :: 6.0",
        "Framework :: Plone :: Addon",
        "Framework :: Plone",
        "Framework :: Zope :: 4",
        "Framework :: Zope :: 5",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="plone transmogrifier plonecms migration",
    author="Rok Garbas",
    author_email="rok@garbas.si",
    url="https://github.com/collective/collective.jsonmigrator",
    project_urls={
        "PyPI": "https://pypi.python.org/pypi/collective.jsonmigrator",
        "Source": "https://github.com/collective/collective.jsonmigrator",
        "Tracker": "https://github.com/collective/collective.jsonmigrator/issues",
    },
    license="GPL version 2",
    packages=find_packages("src", exclude=["ez_setup"]),
    namespace_packages=["collective"],
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.7",
    install_requires=[
        "collective.transmogrifier",
        "plone.app.transmogrifier",
        "Products.CMFPlone",
        "setuptools",
        "zope.interface",
    ],
    extras_require={
        "test": [
            "zope.testrunner",
            "plone.app.testing",
            "plone.uuid",
            "zope.component",
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
