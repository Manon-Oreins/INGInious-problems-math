#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

doc_requires = [
    "sphinx==4.5.0",
    "sphinx_rtd_theme==1.0.0",
    "sphinx-tabs==3.3.1",
    "ipython==8.2.0",
    "sphinx-autodoc-typehints>=1.12.0"
]


setup(
    name="inginious-problems-math",
    version="0.1dev0",
    description="Plugin to add math formulas problem type",
    packages=find_packages(),
    install_requires=["inginious>=0.5.dev0", "sympy", "antlr4-python3-runtime"],
    tests_require=[],
    extras_require={"doc": doc_requires},
    scripts=[],
    include_package_data=True,
    author="The INGInious authors",
    author_email="inginious@info.ucl.ac.be",
    license="AGPL 3",
    url="https://github.com/UCL-INGI/INGInious-problems-math"
)
