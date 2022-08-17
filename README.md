<h1 align="center">collective.jsonmigrator</h1>

<div align="center">

[![PyPI](https://img.shields.io/pypi/v/collective.jsonmigrator)](https://pypi.org/project/collective.jsonmigrator/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/collective.jsonmigrator)](https://pypi.org/project/collective.jsonmigrator/)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/collective.jsonmigrator)](https://pypi.org/project/collective.jsonmigrator/)
[![PyPI - License](https://img.shields.io/pypi/l/collective.jsonmigrator)](https://pypi.org/project/collective.jsonmigrator/)
[![PyPI - Status](https://img.shields.io/pypi/status/collective.jsonmigrator)](https://pypi.org/project/collective.jsonmigrator/)


[![PyPI - Plone Versions](https://img.shields.io/pypi/frameworkversions/plone/collective.jsonmigrator)](https://pypi.org/project/collective.jsonmigrator/)

[![Code analysis checks](https://github.com/collective/collective.jsonmigrator/actions/workflows/code-analysis.yml/badge.svg)](https://github.com/collective/collective.jsonmigrator/actions/workflows/code-analysis.yml)
[![Tests](https://github.com/collective/collective.jsonmigrator/actions/workflows/tests.yml/badge.svg)](https://github.com/collective/collective.jsonmigrator/actions/workflows/tests.yml)
![Code Style](https://img.shields.io/badge/Code%20Style-Black-000000)

[![GitHub contributors](https://img.shields.io/github/contributors/collective/collective.jsonmigrator)](https://github.com/collective/collective.jsonmigrator)
[![GitHub Repo stars](https://img.shields.io/github/stars/collective/collective.jsonmigrator?style=social)](https://github.com/collective/collective.jsonmigrator)

</div>

## Introduction

JSON based migrations for Plone

`collective.jsonmigrator` is a ready tool for you to migrate from old Plone sites (2.0, 2.1, 2.5) to new Plone 4.0 (or higher). Its based extensivly [collective.transmogrifier](https://pypi.org/project/collective.transmogrifier/) and custom blueprints avaliable.

Real beauty of it lays in ability to easily customize it and extend to support all your custom content types that you are using.

Note that collective.jsonmigrator was previously named [collective.blueprint.jsonmigrator](https://github.com/collective/collective.jsonmigrator/commit/747af7d0be1bf16f12822ef4841f40f5bb23a6b6).

## Developing this package

Create the virtual enviroment and install all dependencies:

```shell
make build
```

Start Plone in foreground:

```shell
make start
```


### Running tests

```shell
make tests
```


### Formatting the codebase

```shell
make format
```

### Linting the codebase

```shell
make lint
```

## License

The project is licensed under the GPLv2.
