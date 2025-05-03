#!./.env/bin/python
# -*- coding: utf-8 -*-
# Time-stamp: "2024-01-13 16:02:05 (ywatanabe)"


import os
import sys

sys.path.append("./scripts/py/")
from utils import ChatGPT, back_up, load_tex, save_tex, show_diff


def insert_citations(lpath_tex, lpath_bib):
    # Parameters
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # Instantiates GPT
    gpt = ChatGPT(OPENAI_API_KEY, model="gpt-4-1106-preview")

    # Load text files
    tex_contents = load_tex(lpath_tex)
    bib_contents = load_tex(lpath_bib)

    # Instruction
    prompt = f"""
    Please insert citations at appropriate places in the TeX file below, using the bibliography file provided.

    Note that:
    - Do not alter the original text, including LaTeX commands and indentation, except to manage citations.
    - Exclude any comments from your output, as the original TeX file will be overwritten with your output.
    - The original TeX manuscript for citation insertion is as follows:\n{tex_contents}
    - The bibliography file to be referred to is as follows:\n{bib_contents}
    - Do not include any tags other than \cite{}, this is because other tags will be compiled from external tex files.
    """

    # Main
    print(f"Inserting citations to {lpath_tex} based on {lpath_bib}...")
    inserted_text = gpt(prompt)

    # Copy the original tex under the ./orig dir in its directory
    back_up(lpath_tex)

    # Saves
    spath = lpath_tex
    save_tex(inserted_text, spath) # fxime: \indent disappears
    print(f"Citations were inserted to: {spath}")

    # Show diff between the original and inserted_text
    show_diff(tex_contents, inserted_text)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--lpath_tex", "-lt", default="./src/introduction.tex")
    parser.add_argument("--lpath_bib", "-lb", default="./bibliography.bib")
    args = parser.parse_args()

    insert_citations(args.lpath_tex, args.lpath_bib)

    # python ./scripts/insert_citations.py -lt ./src/introduction.tex -lb ./bibliography.bib
    # cat ./src/introduction_cited.tex
