# -*- coding: UTF-8 -*-
"""
The setuptools base setup module. Necessary for the PyPI upload.
"""

# Always prefer setuptools over distutils
from setuptools import setup
# load version
from geological_toolbox.constants import project_version
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
status = "Development Status :: "
if project_version[3].startswith("a"):
    status += "3 - Alpha"
elif project_version[3].startswith("b"):
    status += "4 - Beta"
elif project_version[3].startswith("rc") or project_version[3].startswith(""):
    status += "5 - Production/Stable"
# elif project_version[1] == "0" and project_version[3].startswith("rc"):
#     status += "6 - Mature"
else:
    status += "1 - Planning"

# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()
long_description_content_type = "text/markdown"

setup(
    # $ pip install GeologicalToolbox
    #
    # PyPI: https://pypi.org/project/GeologicalToolbox/

    name="GeologicalToolbox",
    version=".".join(project_version),
    description="A python module for processing and storing geological data.",
    long_description=long_description,  # Optional
    long_description_content_type=long_description_content_type,
    url="https://github.com/stdonn/GeologicalToolbox",  # Optional
    author="Stephan Donndorf",  # Optional
    author_email="stephan@donndorf.info",  # Optional
    license="MIT",

    # Classifiers help users find your project by categorizing it.
    #
    # For a list of valid classifiers, see
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers

    classifiers=[
        status,
        # Indicate who your project is intended for
        "Intended Audience :: Developers",
        "Intended Audience :: Other Audience",
        "Intended Audience :: Science/Research",

        # Pick your license as you wish
        "License :: OSI Approved :: MIT License",

        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",

        # other classifiers
        "Natural Language :: English",
        "Topic :: Database :: Front-Ends",
        "Topic :: Documentation :: Sphinx",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],

    keywords="Geology Modelling SQLAlchemy",  # Optional

    # You can just specify package directories manually here if your project is
    # simple. Or you can use find_packages().
    #
    # Alternatively, if you just want to distribute a single Python file, use
    # the `py_modules` argument instead as follows, which will expect a file
    # called `my_module.py` to exist:
    #
    #   py_modules=["my_module"],
    #
    packages=["geological_toolbox"],  # Required
    package_data={"geological_toolbox": ["alembic.ini", "alembic/env.py", "alembic/versions/*.py"]},

    # This field lists other packages that your project depends on to run.
    # Any package you put here will be installed by pip when your project is
    # installed, so they must be valid existing projects.
    #
    # For an analysis of "install_requires" vs pip"s requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[
        "SQLAlchemy>=1.2",
        "alembic>=1.2"
    ],  # Optional

    # List additional groups of dependencies here (e.g. development
    # dependencies). Users will be able to install these using the "extras"
    # syntax, for example:
    #
    #   $ pip install sampleproject[dev]
    #
    # Similar to `install_requires` above, these must be valid existing
    # projects.
    extras_require={  # Optional
        ":python_version < '3.5'": [
            "typing"
        ],
        "dev": ["Sphinx", "sphinxjp.themes.basicstrap"]
        # "test": ["coverage"],
    },

    python_requires=">=3.5"
)
