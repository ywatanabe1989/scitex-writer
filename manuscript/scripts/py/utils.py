#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Time-stamp: "2024-01-16 16:35:03 (ywatanabe)"

import difflib
import io
import os
import shutil
import sys

import openai
from openai import OpenAI

# import wasabi
import re

class ChatGPT(object):
    """
    # version 1.00?
    Example:
        gpt = ChatGPT()
        gpt("Hi")
    """

    def __init__(
        self,
        system_setting="",
        chatgpt_api_key=None,
        model="gpt-4",
    ):
        self.system_setting = system_setting
        self.model = model
        self.counter = 0
        openai.api_key = chatgpt_api_key
        self.client = OpenAI()

        self.chat_history = []
        self.chat_history.append(
            {
                "role": "system",
                "content": system_setting,
            }
        )

    @staticmethod
    def remove_old_history(chat_history, n_limit=1):
        if len(chat_history) > n_limit:
            chat_history = [chat_history[0]] + chat_history[
                len(chat_history) - n_limit :
            ]
        return chat_history

    def __call__(self, text):
        original_stdout = sys.stdout
        sys.stdout = io.StringIO()

        self.counter += 1

        if text is None:
            text = ""
        try:
            self.chat_history.append({"role": "user", "content": text})
            self.chat_history = self.remove_old_history(self.chat_history)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.chat_history,
                stream=False,
            )
            out_text = response.choices[0].message.content

            self.chat_history.append({"role": "assistant", "content": out_text})
            sys.stdout = original_stdout

            return out_text

        except Exception as e:
            print(e)
            sys.stdout = original_stdout
            return e


def load_tex(lpath):
    with open(lpath, "r") as file:
        return file.read()


def back_up(path):
    sdir, fname = os.path.split(path)
    old_dir = os.path.join(sdir, ".old")
    os.makedirs(old_dir, exist_ok=True)
    spath = os.path.join(sdir, ".old", fname)
    shutil.copy(path, spath)
    print(f"Backed up: {path} -> {spath}")


def save_tex(text, spath):
    with open(spath, "w", encoding="utf-8") as file:
        # text = replace_highlighting_marks(text)
        file.write(text)


# def replace_highlighting_marks(text):
#     return text


def show_diff(a: str, b: str, *, for_tex: bool = False) -> str:
    output = []
    matcher = difflib.SequenceMatcher(None, a, b)

    if for_tex:
        start_green = "\GREENSTARTS "
        end_green = "\GREENENDS "
        
        start_red = "\REDSTARTS "
        end_red = "\REDENDS "
    else: # for bash
        start_green = '\x1b[38;5;16;48;5;2m'
        start_red = '\x1b[38;5;16;48;5;1m'
        end_green = '\x1b[0m'
        end_red = '\x1b[0m'

    for opcode, a0, a1, b0, b1 in matcher.get_opcodes():
        if opcode == 'equal':
            output.append(a[a0:a1])
        elif opcode == 'insert':
            output.append(f'{start_green}{b[b0:b1]}{end_green}')
        elif opcode == 'delete':
            output.append(f'{start_red}{a[a0:a1]}{end_red}')
        elif opcode == 'replace':
            output.append(f'{start_green}{b[b0:b1]}{end_green}')
            output.append(f'{start_red}{a[a0:a1]}{end_red}')
    return ''.join(output)


# # new lines disappears
# def show_diff_tex(text1, text2):
#     words1 = text1.split()
#     words2 = text2.split()
#     matcher = difflib.SequenceMatcher(None, words1, words2)
#     diff = []

#     for opcode, a0, a1, b0, b1 in matcher.get_opcodes():
#         if opcode == "equal":
#             diff.extend(words1[a0:a1])
#         elif opcode == "insert":
#             diff.extend(["\\greenhighlight{{{}}}".format(" ".join(words2[b0:b1]))])
#         elif opcode == "delete":
#             diff.extend(["\\redhighlight{{{}}}".format(" ".join(words1[a0:a1]))])
#         elif opcode == "replace":
#             diff.extend([
#                 "\\redhighlight{{{}}}".format(" ".join(words1[a0:a1])),
#                 "\\greenhighlight{{{}}}".format(" ".join(words2[b0:b1]))
#             ])
#     return " ".join(diff)
