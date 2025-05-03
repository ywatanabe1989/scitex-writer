#./.env/bin/python
# -*- coding: utf-8 -*-
# Time-stamp: "2024-01-14 11:22:25 (ywatanabe)"


import os
import sys

sys.path.append("./scripts/py/")
from utils import ChatGPT, load_tex, back_up, save_tex


def revise_by_GPT(lpath):
    # Parameters
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if OPENAI_API_KEY is None:
        raise ValueError(
            "The OpenAI API key must be set as an environment variable to use ChatGPT. Please visit https://openai.com/blog/openai-api for more information. To set the key, run the command: echo 'export OPENAI_API_KEY=\"<YOUR_OPENAI_API_KEY>\"' >> ~/.bashrc. Replace <YOUR_OPENAI_API_KEY> with your actual API key, which might look similar to 'sk**AN'."
        )

    # Instantiates GPT
    gpt = ChatGPT(OPENAI_API_KEY)
    text = load_tex(lpath)
    revise_instruction = """
    You are an esteemed professor in the scientific field, based in the United States.
    The subsequent passages originate from a student whose first language is not English.
    Please proofread them with following the rules below.
    
    - Correct the English without including messages or comments.
    - Retain the original syntax as much as possible while conforming to scholarly language.
    - Do not modify linguistically correct sections.
    - Minimize revisions to avoid endless paraphrasing.
    - Exclude comments beyond the revised text.
    - Preserve LaTeX commands as needed.
    - Avoid unnecessary adjectives not suitable for scientific writing, such as "somewhat", "in-depth", and "various".
    - For figures and tables, please use tags like Figure~\ref{fig:01}A or Table~\ref{tab:01}.
    
    - Highlight parts that may require the author's manual review due to ambiguity using CHECKME tags as follows: [CHECKME>] This is an ambiguous sentence. [<CHECKME ENDS].
    - If [FIXME ->][<- FIXME] tags are present, please revise only the enclosed area; otherwise, please revise the entire text.
    - When using --- (emdash), please add spaces on either side.
    - Terminology should be consistent throughout the manuscript.

    - Titles should follow the capitalization rules for titles like this: Local Field Potentials, Multiunit Activity, and Neural Trajectories in the Hippocampus during a Modified Sternberg Task. Please note that prepositions are written in lower letters. When a singular form without a preposition such as (a, an, the) is appropriate, it is preferred.

    - Titles of figures and tables should be the nown form

    - The legend of figures and tables should use noun forms as much as possible.
    
    Now, the original manuscript to be revised is as follows:
    """

    # Main
    print(f"Revising {lpath} ...")
    revised_text = gpt(revise_instruction + text)

    # Copy the original tex under the ./orig dir in its directory
    back_up(lpath)

    # Saves
    spath = lpath # .replace(".tex", "_revised.tex")
    save_tex(revised_text, lpath)
    print(f"Revised: {lpath}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--lpath", "-l")
    args = parser.parse_args()

    revise_by_GPT(args.lpath)

    # python ./scripts/_revise_by_GPT.py -l ./src/abstract.tex
