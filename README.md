![PyPI](https://img.shields.io/pypi/v/GeologicalToolbox.svg)
![Build Status](https://travis-ci.org/stdonn/GeologicalToolbox.svg?branch=master)
![PyPI - Status](https://img.shields.io/pypi/status/GeologicalToolbox.svg)
![Python Version](https://img.shields.io/pypi/pyversions/GeologicalToolbox.svg)
![License](https://img.shields.io/pypi/l/GeologicalToolbox.svg)
![PyPI - Format](https://img.shields.io/pypi/format/GeologicalToolbox.svg)


# Geological Toolbox

## General Description

This toolbox provides basic functionality for the storage and processing of geological data in a database. The toolbox can process point, line (and so also polygons as closed lines) and well data.

## Installation

You can install the GeologicalToolbox via pip from the [Python Package Index (PyPI)](https://pypi.org/):

```
pip install GeologicalToolbox
```

For further information on installing packages with pip and PyPI see [Installing Packages](https://packaging.python.org/tutorials/installing-packages/).

## System Requirements

This toolbox was tested with Python version 2.7 and 3.6.

This toolbox requires [SQLAlchemy](https://www.sqlalchemy.org/) and [typing](https://pypi.org/project/typing/). The documentation uses [Sphinx](https://pypi.org/project/Sphinx/) and the [basicstrap template package](https://pypi.org/project/sphinxjp.themes.basicstrap/). More information to configure the documentation theme can be found on the [theme homepage](https://pythonhosted.org/sphinxjp.themes.basicstrap/index.html).


You can install all of the requirements via pip:

```
pip install -r requirements.txt
```