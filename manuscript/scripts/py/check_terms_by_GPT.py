# ./.env/bin/python
# -*- coding: utf-8 -*-
# Time-stamp: "2024-01-14 10:27:58 (ywatanabe)"


import os
import sys

sys.path.append("./scripts/py/")
from utils import ChatGPT, load_tex, back_up, save_tex
from pprint import pprint
import re


def check_terms_by_GPT(lpath):
    # Parameters
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if OPENAI_API_KEY is None:
        raise ValueError(
            "The OpenAI API key must be set as an environment variable to use ChatGPT. Please visit https://openai.com/blog/openai-api for more information. To set the key, run the command: echo 'export OPENAI_API_KEY=\"<YOUR_OPENAI_API_KEY>\"' >> ~/.bashrc. Replace <YOUR_OPENAI_API_KEY> with your actual API key, which might look similar to 'sk**AN'."
        )

    # Instantiates GPT
    gpt = ChatGPT(OPENAI_API_KEY, model="gpt-4-1106-preview")
    text = load_tex(lpath)

    # Remove LaTeX commands from the text
    text = re.sub(r"\\(?!cite|ref)[a-zA-Z]+(\[[^\]]+\])?(\{[^\}]+\})?", "", text)
    # text = re.sub(r"\\[a-zA-Z]+(\[[^\]]+\])?(\{[^\}]+\})?", "", text)  # [REVISED]
    # except for \cite tag, please
    # also except for \ref tag, please    

    revise_instruction = """
    You are a sophisticated proofreader for scientific manuscripts.

    I would like you to review a manuscript to ensure the consistency of abbreviations and technical terms.

    In the abstract, abbreviations should be defined at their first occurrence using parentheses, such as sharp-wave ripples (SWRs), and consistently used in their abbreviated form throughout the abstract.
     
    In the main text, which comprises the introduction, methods, results, and discussions, abbreviations should be defined or redefined at their first occurrence, even if they have already been defined in the abstract. For instance, if a term is defined in the introduction, there is no need to redefine it in subsequent sections of the main text, such as in the methods.
     
    Consistency in terms is crucial throughout the manuscript, from the abstract and introduction to the methods and discussions.
     
    Lastly, terms in each legend of a figure or table should be independently (re-)defined, similar to rule applied to the abstract.

    Please review the usage of terms and indicate any errors using bullet points, specifying the section, line number, and the phrases. For example:

    - Methods 2.1 (Title) Line 39-40
      "sharp-wave ripples" -> "SWR"
      Reason: Already defined

    - Discussion 3.1 (Title) Line 20
      "time resolution" -> "temporal resolution"
      Reason: Inconsistency

    Also, ignore LaTeX commands and focus on the text.

    Never include any comments as they are indistinguishable from your cheking.

    Just show me mistakes.

    If no issues are found, simply reply with "Term usage was checked and no mistakes were found."
    
    Here is my manuscript for your review:
    """

    # Main
    # print(f"Checking abbreviations and term usage in {lpath}...")

    checked = gpt(revise_instruction + text)
    print(checked)

    # # Copy the original tex under the ./orig dir in its directory
    # back_up(lpath)

    # # Saves
    # spath = lpath.replace(".tex", "_revised.tex")
    # save_tex(revised_text, lpath)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--lpath", "-l")
    args = parser.parse_args()

    check_terms_by_GPT(args.lpath)

    # python ./scripts/_revise_by_GPT.py -l ./src/abstract.tex
