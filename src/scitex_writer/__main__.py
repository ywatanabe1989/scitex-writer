#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-19 05:00:00
# File: src/scitex_writer/__main__.py

"""Allow running as: python -m scitex_writer"""

import sys

from ._cli import main

if __name__ == "__main__":
    sys.exit(main())

# EOF
