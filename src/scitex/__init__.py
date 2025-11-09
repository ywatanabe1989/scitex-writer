#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SciTeX namespace package.

This is a namespace package that allows multiple scitex packages
to be installed independently while sharing the same namespace.
"""

__path__ = __import__('pkgutil').extend_path(__path__, __name__)
