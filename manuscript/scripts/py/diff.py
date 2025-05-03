#!./.env/bin/python
# -*- coding: utf-8 -*-
# Time-stamp: "2024-01-13 16:01:47 (ywatanabe)"

import os
import sys

sys.path.append("./scripts/py/")
from utils import load_tex, save_tex, show_diff


def diff_tex_files(lpath_1, lpath_2, spath):
    text_1 = load_tex(lpath_1)
    text_2 = load_tex(lpath_2)
    diff = show_diff(text_1, text_2, for_tex=True)
    
    if spath != "":        
        save_tex(diff, spath)
        print(f"Saved to: {spath}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--lpath_1", default="./.manuscript.tex")
    parser.add_argument("--lpath_2", default="./old/compile_v001.tex")
    parser.add_argument("--spath", default="./diff.tex")
    args = parser.parse_args()

    if (args.lpath_1 != "") & (args.lpath_2 != ""):
        diff_tex_files(args.lpath_1, args.lpath_2, args.spath)

## EOF
